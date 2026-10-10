# MCP catalog CI contract — #236

Review date: 2026-10-10. Base: develop c97d511. Scope: test consumer contract,
stdio probe/wire tests, mutation tests and clean-wheel installation script.
No runtime or dependency change; unrelated local documentation WIP excluded.

## Contracts and evidence

- A discovery response must contain all 12 expected tool names exactly once.
  Every tool must have a substantive description (120 characters after trimming),
  nonempty input parameters, and a description for each parameter (12 characters,
  not just its name). These thresholds preserve the existing definition-quality
  contract and now check the actual serialized response.
- SDK stdio probes validate the response before exercising create/save/read/extract.
  They run through module, installed command and direct-file launch in the existing
  CI test matrix: Python 3.10–3.14 on Linux, macOS and Windows. No additional workflow
  trigger is needed: `.github/workflows/test.yml` already executes `pytest tests/`.
- Raw 2024-11-05 and 2025-11-25 discovery uses the same independent consumer oracle.
  It imports no server implementation or capabilities to derive expectations.
- Clean-wheel minimum/latest dependency jobs now exercise all three startup modes.
  The separate SDK v1 client validates metadata through the existing console route.
  Direct launch resolves server.py with the server interpreter, avoiding accidental
  selection of a different installation when client and server interpreters differ.
- Eight mutations of genuine discovery payloads cover empty/incomplete/duplicate
  catalogs, missing/blank tool descriptions, missing parameters and missing/blank
  parameter descriptions. Whitespace-only strings do not satisfy minimum lengths.

## Validation

- Focused wire/SDK/mutation suite: **15 passed, 1 skipped**, 16.79 seconds.
- Full local suite: **2567 passed, 1 skipped**, 45.87 seconds, Python 3.12/Linux.
- The skip is the existing optional isolated SDK v1 interpreter; distribution CI
  supplies that environment. No Windows/macOS or clean-wheel local result is claimed.
- Disabling the validator with a temporary pytest plugin causes **all eight mutation
  tests to fail** with `DID NOT RAISE`, rather than setup/import errors.
- `git diff --check` passed. Cross-platform and clean-wheel results are tracked by
  PR CI before integration. Raw local logs: `/tmp/oxidize-mcp-metadata-ci/`.

Reproduce with `.venv/bin/python -m pytest tests/mcp_tests/test_stdio.py
 tests/mcp_tests/test_tool_catalog_contract.py -q`, or the complete `tests/` suite.
Wheel validation uses `python scripts/check_mcp_install.py WHEEL`, with optional
`--constraints tests/constraints/mcp-min.txt` for the minimum dependencies.

## Findings

No unresolved findings in the changed scope. The gap between in-memory metadata
assertions and actual discovery responses is covered. These checks verify what
clients receive, not whether a particular client UI chooses to display descriptions.
No changes to production source were needed during review.

## Test quality (Kripteia)

Required script executed on `tests/mcp_tests`: **96**, 230 test functions, 26 files.
Changed wire tests score 100; mutation test score 90 due to low assert/setup ratio.
Manual review confirms two assertions enforce the intact payload and rejection of
its mutation; the eight failing cases with the validator disabled establish that
this is not a vacuous test. Other warnings are pre-existing surrounding tests.
The installation script scan reports 0 tests: its behavior is covered by the
actual distribution jobs, not by that score.

## Security (Kripteia Security)

Both test-directory and installation-script scans reported **No security issues
found**. Both completed despite a warning that the local telemetry database is
read-only. Manual inspection checked fixed subprocess argument arrays, bounded
launch/communication timeouts, temporary workspaces, cleanup and absence of shell
interpolation. No product trust boundary or public API was changed.

## Review accounting

Six affected/supporting files reviewed (five changed Python files plus the CI
workflow). Confirmed unresolved findings: 0. Product files modified: 0.
Remaining delivery step at review time: cross-platform/clean-wheel CI, integration
into develop and closure of #236. Existing #198 remains closed.
