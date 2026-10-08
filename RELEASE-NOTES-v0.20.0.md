# oxidize-pdf 0.20.0 — MCP SDK v2

- Migrate the optional MCP extra to FastMCP 4 and MCP SDK 2. Python >=3.10 and
  core Rust 5.1.3 are retained; the base library has no MCP dependencies.
- Preserve the 12 tools, resources, prompts and PDF creation sessions, with
  real stdio coverage for modern and legacy clients.
- Fix module startup, advertised session template and server version metadata.
- Include MCP in mypy and extend native stubs used by its tools. Handle missing
  extracted font names when reconstructing an encrypted PDF.
- Add clean wheel installation checks and Python 3.14 to CI.

Install with `pip install 'oxidize-pdf[mcp]>=0.20,<0.21'`. See the
[migration guide](docs/MCP-V2-MIGRATION.md) for client setup and compatibility.
The companion integrations change fixes installation of MCP extras from the
Claude Code launcher and registry command. Hosted ChatGPT distribution is a
separate deployment task.
