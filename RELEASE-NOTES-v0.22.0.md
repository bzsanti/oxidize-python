# oxidize-pdf 0.22.0

- Update the exact Rust core dependency to the published 5.4.2.
- Expose existing-document preservation policies, plans, reports and mutations.
- Add typed external-CMS signature preparation/finalization and its options.
- Expose reading-order, column-reordering and carriage-return extraction policies.
- Add incremental FreeText and Ink editing with typed mutations and results.
- Enforce per-capability API contracts in CI and strengthen the GIL concurrency guard.

Python 3.10+; Linux x64/ARM64, macOS x64/ARM64 and Windows x64.
The optional MCP extra retains its installed-wheel discovery regression tests.
Implementation PRs #243, #245, #246, #248, #249 and #250 passed their CI matrices;
#250 passed all 26 checks. Full functional parity remains tracked in #244.

Upgrade: `python -m pip install --upgrade "oxidize-pdf[mcp]"`.
