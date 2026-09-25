# MCP SDK v2 migration (oxidize-pdf 0.20)

The optional MCP server now uses FastMCP 4 and Python SDK MCP 2. The Rust
core remains 5.1.3 and the library still supports Python >=3.10.

## Install and connect

```sh
pip install 'oxidize-pdf[mcp]>=0.20,<0.21'
oxidize-mcp
# Alternatively, uvx installs an isolated tool environment:
uvx --from 'oxidize-pdf[mcp]>=0.20,<0.21' oxidize-mcp
```

`pip install oxidize-pdf` includes server source and the console entry point,
but does not install MCP dependencies. Use the extra to run the server. Base
PDF creation and reading need none of FastMCP, MCP or mcp-types.

| Client | Connection |
| --- | --- |
| Claude Code | The updated integrations plugin installs `[mcp]`; alternatively configure the uvx command above. |
| Claude Desktop | Configure a local stdio server: command `uvx`, arguments `--from`, `oxidize-pdf[mcp]>=0.20,<0.21`, `oxidize-mcp`. |
| ChatGPT Desktop using a Codex host | Configure a local STDIO server with the same command in Settings → MCP servers. |
| ChatGPT web | Requires a reachable connection: public HTTPS, or Secure MCP Tunnel for developer-mode testing. No hosted endpoint or public ChatGPT plugin is supplied here. |

The OpenAI client distinction is documented in [MCP configuration](https://learn.chatgpt.com/docs/extend/mcp)
and [connecting a plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt),
consulted on 2026-09-25. Workspace policy can affect availability. The tunnel
is a separate deployment component; this release has not tested that setup.

Set `OXIDIZE_WORKSPACE` to the directory containing PDFs. Use absolute file
paths in tool calls; relative paths currently resolve against the server's
working directory. The protocol exposes local files in that workspace, not
files automatically uploaded to a chat.

## Upgrading an existing FastMCP 3 environment

Prefer a fresh virtual environment, as used by the clean installation tests.
FastMCP 4 delegates its Python modules to `fastmcp-slim`. With pip, installing
slim before removing FastMCP 3 can delete shared module files, even though
`pip check` reports no dependency conflict. This was reproduced with the
published 0.19.0 package and FastMCP 3.1.1.

For an existing environment, remove FastMCP 3 before installing the new extra:

```sh
python -m pip uninstall fastmcp
python -m pip install --upgrade 'oxidize-pdf[mcp]>=0.20,<0.21'
```

If an attempted upgrade already left a broken import, force-reinstall
`fastmcp-slim` at exactly the version reported by `python -m pip show fastmcp`.
The companion Claude Code launcher checks the import after installation and
performs this repair automatically inside its managed environment. It reports
success and records its upgrade timestamp only after that check passes.

## Dependency and protocol compatibility

Declared minimums: FastMCP 4.0.9, SDK MCP 2.2.0, mcp-types 2.2.0, Pydantic
2.12.5. Upper bounds exclude the next major of each. Exact direct minimums
used by tests are in `tests/constraints/mcp-min.txt`. The pre-existing local
`uv.lock` is not a distributed lockfile and was not changed.

The `fastmcp` package remains the server framework. The official SDK's
`MCPServer` rename does not rename `fastmcp.FastMCP`. Protocol Python types now
come from `mcp_types` and use snake_case; JSON-RPC retains protocol aliases
such as `inputSchema` and `readOnlyHint`.

Real stdio clients test SDK 2.2.0 using protocol 2026-07-28 and an isolated
SDK 1.26.0 using protocol 2025-11-25. SDK v1 is only installed in the client
compatibility environment, never alongside v2 in the server environment.
The server's application version remains 1.0.0 and is now explicitly announced
in the handshake, consistent with `oxidize://version`; the Python package
version is 0.20.0. Neither number is the protocol revision or SDK version.

All 12 tools and 5 prompts remain. Five static resources and the
`oxidize://session/{session_id}` template are preserved; the capabilities
resource now advertises the exact registered template. PDF creation sessions
are application state and remain valid across requests in the same server
process. They do not persist across process restarts.

The module entry point now runs the canonical registered server. Previously,
`python -m oxidize_pdf.mcp.server` could start a separate instance without tools.
Completing native type stubs allowed mypy to check MCP code. This also exposed
an encryption failure on extracted text with no font name; it now uses Helvetica,
with a test that reopens the encrypted PDF and checks the preserved text.

## Reproduce validation

```sh
maturin develop --locked --extras dev,mcp
pytest tests/ -q
mypy python/oxidize_pdf/
mypy --strict --disallow-any-expr tests/typing/extraction.py tests/typing/mcp_contract.py
maturin build --locked --out /tmp/oxidize-mcp-wheels
python scripts/check_mcp_install.py /tmp/oxidize-mcp-wheels/<wheel>.whl
python scripts/check_mcp_install.py /tmp/oxidize-mcp-wheels/<wheel>.whl --constraints tests/constraints/mcp-min.txt
```

The installation script creates temporary base, server and legacy-client
environments and executes real workflows from outside the checkout. Add
`--integrations-dir /path/to/oxidize-pdf-integrations` to test its launcher and
registry command against the candidate wheel before publication. This requires
Bash and uvx and substitutes the wheel directory as a package source; it does
not publish anything. Network access is required for third-party dependencies.

CI covers Python 3.10–3.14 on Linux/macOS/Windows. Separate Linux jobs exercise
clean wheels at minimum and latest allowed dependencies on Python 3.10 and
3.14, including the legacy client. See `MCP-V2-VALIDATION.md` for actual results
and any pending checks; configured jobs are not evidence of successful runs.

Upgrade the integrations plugin together with the Python release. The registry
manifest pins the package version in its `--from` argument as well as its
version fields; the publication workflow updates all three. Publish the Python
wheel first, then merge the integrations release and publish the registry.
Published 0.19.0 artifacts and tags are not modified.
