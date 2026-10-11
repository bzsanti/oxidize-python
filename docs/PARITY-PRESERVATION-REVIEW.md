# Existing-document parity increment — review

## Resumen ejecutivo

Scope: new typed preservation policies, input selections, complete semantic and
object planning reports, plan/execute merge/extract/split, and five atomic page
mutations; core pinned to 5.4.2. Changes are additive and retain legacy APIs.
No claim of overall Rust parity: #244 remains open. Platform CI remains pending.

## Contratos y evidencia

| Contract / source | Evidence | Status |
| --- | --- | --- |
| Core existing_document policy must be explicit; preserve-base retains exact input prefix | Hand-authored PDF, typed report, selected-page checks; changing preserve-base to reconstruct caused four intended failures | Demonstrated |
| Reconstruct metadata choice is visible in reports | Both values checked against DocumentInfo disposition | Demonstrated |
| Planning and execution expose all report fields | Object replacements/additions/unreachable IDs and input structures/options compared; property and parameter contract gate | Demonstrated |
| Page mutations use sequential zero-based indexes | Move, rotate, duplicate, delete, import batch; independent expected rotated dimensions/order | Demonstrated |
| Invalid inputs must not overwrite/publish output | Out-of-bounds selection, source alias, invalid rotation with preexisting destination | Demonstrated |
| Core page-label remapping limitation remains explicit | Base labels rejected; secondary labels require opt-in first-input policy | Demonstrated |
| Audited APIs retain options/results/behavior entry points | Runtime introspection plus static contract gate; four gate mutations rejected | Demonstrated |
| Cross-platform behavior | Existing test matrix automatically collects new tests; strict typing added to workflow | CI pending |

Tests execute the compiled wheel. Final behavioral regression: 2577 passed,
1 existing legacy-MCP skip; four additional gate negative controls passed after
that regression. Focused 10 tests passed after restoring the preservation mutation.
Clippy passes with warnings denied. Package and strict consumer typing pass against
updated stubs. Logs: `docs/evidence/parity-preservation/`.

## Hallazgos

1. Public consumer typing initially omitted the `__init__.pyi` reexports. Corrected
   explicit reexports, added PageRange's missing declaration and strict consumer
   test wired into CI. No unresolved finding in this increment.

## Calidad de Tests (Kripteia)

Executed Rust and Python analyses. Rust has no native tests in this PyO3 module
(report: 0 tests); behavior is exercised through Python. Python report covers the
complete test directory: score 96, 2477 tests in 114 files. New preservation and contract tests score 100; scores
are supporting evidence, not acceptance. Full output is retained alongside logs.
Manual review covers independent PDF construction, actual mutation failure causes,
error publication and mapping, detached GIL execution, and complete core fields.

## Análisis de Seguridad (Kripteia Security)

Rust scan: no issues. Python scan flags `test_security.py`'s literal
`SECRET = "Secret content RT-117"`; inspected as preexisting synthetic PDF content,
not a credential. New bridge code introduces no unsafe blocks or native ownership
protocol. Paths and policies go directly to core atomic publication, permission
and alias checks; bridge does not catch and downgrade failed core operations.

## Métricas

- Scope: source module/registration/error conversion, public imports and stubs,
  contract script/manifest, behavioral/gate/typing tests and CI wiring.
- Findings: one corrected public typing omission.
- Product edits made by the read-only review: 0; correction followed separately.
- Pending: platform CI, remaining Rust capabilities tracked by #244.
