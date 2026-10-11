# External CMS signing parity — Rust 5.4.2

## Resumen ejecutivo

Exposes typed signature targets, every preparation option, certification/field-lock
policies, all PDF value variants for additional dictionary entries, appearance and
watermark settings, layout results and immutable prepared-signature snapshots.
The caller retains its private key and produces CMS externally. Finalization
checks container shape/size; it does not claim cryptographic authentication.
This is another #244 increment, not complete Rust parity. Platform CI pending.

## Contratos y evidencia

| Contract | Evidence | Status |
| --- | --- | --- |
| Exact byte coverage and prior-revision preservation | Real detached CMS created with cryptography; embedded CMS independently verified by OpenSSL on Linux against final PDF ranges | Demonstrated |
| Digest bytes must exclude the reserved signature gap | Returning the complete PDF instead causes the coverage assertion to fail; restored 2595 tests pass, 1 existing skip | Demonstrated |
| Preparation is immutable and supports retries | Failed malformed-CMS call leaves preparation unchanged; repeated completion returns identical bytes | Demonstrated |
| All targets/options reach Rust | Existing/new target, invalid page/widget, reserved entry rejection; decoded reason/location/contact/time, handler/profile, size, all certification levels and both selective locks asserted | Demonstrated |
| Appearance includes text/watermark and rejects invalid input | Layout fields, image object, geometry, watermark dimensions tested | Demonstrated |
| Public type contracts retained | Explicit stubs/reexports, strict consumer test, per-member parity manifest and static/runtime gates | Demonstrated locally; CI pending |

14 new signing cases pass. Full suite: 2595 passed / 1 existing legacy-MCP skip.
Clippy with warnings denied and strict signing-consumer typing pass. Cryptography
is a development dependency only; the shipped native implementation remains Rust.
Linux CI requires OpenSSL for independent verification; other platforms exercise
real CMS generation, exact embedding, ranges and all option/error cases.

## Hallazgos

No confirmed unresolved finding in this increment. The field-value assertions
were corrected to decode PDF hexadecimal strings rather than assume literal
string serialization. They still assert the original independent expected values.

## Calidad de Tests (Kripteia)

Real Python and Rust analyses retained in `docs/evidence/parity-signing/`.
Python: score 96, 2484 tests / 115 files; new signing tests score 100.
Rust reports no native tests in PyO3 source; behavior is exercised through the
installed Python extension. Manual review verifies independent signer/verification,
actual final PDF bytes, error retries and each options-to-core mapping. Scores do
not establish full parity or cryptographic correctness by themselves.

## Análisis de Seguridad (Kripteia Security)

Rust scan reports no issues. Python reports the preexisting synthetic PDF string
`SECRET = "Secret content RT-117"`, not a credential. OpenSSL test invocation uses
an argument array, never shell interpolation, and temporary local files.
New product code has no unsafe blocks; immutable Python byte slices and owned
options are used during GIL detachment. Prepared state is cloned for finalization,
so failure/retry cannot mutate a shared signing session. Reserved dictionary keys,
permissions and CMS structural checks remain enforced by core.

## Métricas

- Reviewed: signing module/registration, exports/stubs, development dependency,
  signing tests, consumer typing, parity manifest/gates and CI wiring.
- Unresolved findings: none within this increment.
- Product edits by the read-only review: 0.
- Pending: platform CI and remaining #244 capabilities.
