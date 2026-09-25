# MCP v2: implementation and TDD evidence

Date: 2026-09-25. Candidate: oxidize-pdf 0.20.0, core 5.1.3.
Implementation branch: `feat/mcp-v2` in both repositories. Integrations changes
were prepared in `/tmp/oxidize-mcp-v2-integrations`; the original sibling's
local deletion of `claude-code/.mcp.json` was preserved.

## RED → GREEN record

| Contract | Observed RED | GREEN |
| --- | --- | --- |
| SDK/framework major | SDK 1 and FastMCP 3 failed the new version assertions | SDK 2.2.0 and FastMCP 4.0.9 |
| Advertised resource template | `{id}` differed from discovery's `{session_id}` | Exact advertised/registered catalog agreement |
| Module startup | Real stdio module invocation did not list all tools | Canonical registered server runs for module and console entry point |
| Wire metadata | Handshake reported framework 4.0.9 instead of server 1.0.0 | Explicit application version, JSON-RPC stdout test |
| Missing extracted font | Encryption returned PDF_ERROR (`NoneType.upper`) | Helvetica fallback; encrypted PDF reopened and text checked |
| Launcher readiness | Base-only interpreter was accepted | Server import and SDK/framework version checks |
| Launcher dependency installation | Upgrade command omitted `[mcp]` | MCP extra with supported package range; interval and skip behavior preserved |
| Existing FastMCP 3 upgrade | Real upgrade removed FastMCP module files despite successful pip exit | Managed-environment slim reinstall and post-install readiness check |
| Launcher error channel | Missing server wrote non-JSON text to protocol stdout | Startup errors use stderr |
| Registry runtime | Manifest had no extra-bearing `--from` source | Pinned extra-bearing source, publication workflow updates it |

The initial SDK/contracts run had 3 expected failures and 2 characterizations
passing. The initial launcher run had 2 expected failures; the registry test
then reproduced a separate failure. No test assertion was weakened to conceal
a migration regression. Probe working directory was explicitly set to its
workspace because existing relative-path semantics use the process directory.

## Local results

- Baseline: 274 MCP tests passed on SDK 1.26.0 / FastMCP 3.1.1.
- Migrated MCP suite including real legacy client: 282 passed before the final
  font and wire-version regressions; those additional cases passed separately.
- Final full suite: **2520 passed, 2 skipped**, Python 3.12/Linux. Skips were
  the image module's missing Pillow and the optional legacy-interpreter env var.
  Pillow was then installed and its two image tests run separately. Legacy
  stdio was already exercised in the MCP suite and again from a clean isolated
  SDK 1.26.0 environment by the installation script.
- Existing pytest warning: `enumerate` in `test_core_5_1_bindings.py` is
  deprecated as a parameter iterable in newer pytest. Not a migration failure.
- Whole-package mypy, now including all 21 MCP files: passed (24 source files).
- Strict consumers `tests/typing/extraction.py` and `mcp_contract.py`: passed.
- Native API stubs added for the APIs already consumed by MCP; optional native
  font names and metadata page count retain their actual nullable types.
- Wheel and sdist 0.20.0 built. Wheel extras/versions inspected; sdist includes
  Cargo.lock, the protocol probe, installation script and constraints.
- Clean wheel base installation: creates and reads a PDF, with no MCP packages.
- Clean wheel extra installation with minimum direct dependencies: `pip check`,
  module/console workflows with SDK v2 and separate SDK v1 all passed.
- Clean wheel extra installation with latest allowed dependencies: same checks,
  plus real plugin bootstrap and registry uvx workflow, passed.
- Resolver checks succeeded for Python 3.10, 3.11, 3.13 and 3.14; Python 3.12
  was installed and exercised. Resolver success does not prove runtime support.
- Integrations: 5 launcher/manifest tests, Bash syntax and official registry
  JSON Schema validation passed. Real launcher fresh installation and its
  stdio workflow passed; the registry uvx command also passed using the local
  candidate wheel as an additional package source.
- A published 0.19.0 / FastMCP 3.1.1 environment reproduced the pip file-overlap
  failure on upgrade. The corrected launcher repaired that actual environment
  (FastMCP 4.0.10 / SDK 2.2.0) and passed the full stdio probe.
- `cargo check --locked --offline --no-default-features`: passed.
- Parity check: passed, 7 groups / 386 exports. `git diff --check`: passed.

## CI and remaining release gates

CI has been configured for Python 3.10–3.14 on Linux/macOS/Windows, plus clean
wheel minimum/latest dependency jobs on Linux 3.10 and 3.14. Its actual results
must be checked on the PR before merge; configuration alone is not a passed CI.
The companion adapter jobs install the version in the registry manifest, so
its 0.20.0 release PR must remain draft until that version exists on PyPI.
The companion manual packaging workflow can build the candidate bridge ref
before publication.

Claude Code 2.1.278 is present, but `claude --mcp-config ... mcp list` did not
exercise the temporary server configuration; no host-level success is claimed.
Real official SDK clients and the plugin launcher were tested. ChatGPT Desktop,
ChatGPT web and Secure MCP Tunnel have not been exercised in this environment.
The documented web deployment is outside the stdio migration's scope.

No release tag, PyPI publication or MCP registry publication has been performed.
No global Rust formatting cleanup or changes to the pre-existing local uv.lock,
kripteia.toml or handoff files were made.

## Reproduction and raw local evidence

Use `docs/MCP-V2-MIGRATION.md` for commands. Logs are retained under
`/tmp/oxidize-mcp-v2-*`: `baseline.log`, `red.log`, `green.log`, `stdio.log`,
`font-red.log`, `typing-green.log`, `wire-red.log`, `wire-green.log`,
`launcher-red.log`, `registry-red.log`, `launcher-clean.log`,
`launcher-stdio.log`, `registry-stdio.log`, `packaging.log`,
`packaging-latest.log`, `final-tests.log`, `mypy.log`, `build.log`, `sdist.log`,
`cargo.log`, `upgrade.log` (initial failure), `repro-import.log`,
`launcher-repair-red.log`, `launcher-stderr-red.log`, `repair-green.log`, and
the per-Python resolution reports. These are local artifacts,
not dependencies of CI.
