# oxidize-pdf 0.21.1 — MCP regression protection and CI reliability

- Verify actual stdio discovery for all 12 tools, their descriptions and input
  parameter documentation. Cover direct-file, module and installed-command
  startup, including legacy protocol discovery and clean installed wheels.
- Add eight mutation cases proving that CI rejects empty/incomplete/duplicate
  tool catalogs and absent or blank descriptions.
- Stabilize the GIL concurrency tests with up to three measurements while keeping
  the strict 0.7 speedup threshold. Retained-GIL work and sustained slowdowns
  remain rejected.
- Document Windows upgrade/startup commands for the empty-catalog issue #198.
  The runtime startup fix was already released in 0.20.0; this patch strengthens
  its regression coverage and user guidance.

No public API, runtime dependency or Rust core changes. The core remains 5.4.1;
Python 3.10+ and the optional MCP extra remain supported.

Upgrade with `python -m pip install --upgrade "oxidize-pdf[mcp]"` and start with
`python -m oxidize_pdf.mcp.server`.

Changes: #235, #237. Local validation of the included changes: 2567 tests passed
and one optional separate legacy-client test skipped. Both implementation PRs
passed all 26 checks, including Python 3.10–3.14 on Linux/macOS/Windows and four
minimum/latest clean-wheel jobs. The release workflow repeats validation on the
tag before publication.
