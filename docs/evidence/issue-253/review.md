# Review: #253 secure AES core adoption

## Resumen ejecutivo

Delivery branch based on develop `177987cacfc16dc03f0f39dfa53aca507096573b`.
Published core 5.5.0 pinned with its registry checksum. Scope: dependency adoption,
AES behavioral guards, and compatibility adaptations required by this version.
No TaggedPdf draft, Color PR #289, redaction binding or LayoutManager is included.

## Contratos y evidencia

- AES-128 and AES-256 round trips run on all platform jobs. qpdf independently
  decrypts the sentinel and rejects a wrong password. File/byte serialization
  with denied OS entropy raises PdfEncryptionError and produces no valid PDF.
  Linux libseccomp runs in a child only; fresh IV entropy is denied after warming
  the thread RNG. File-save failure may leave an incomplete file, not an atomic
  replacement guarantee. `aes-542-red.log` has four expected failures using the
  prior real 5.4.2 wheel; `final-focused.log` passes on the isolated 5.5.0 wheel.
  The CI Linux 3.12 gate asserts availability of both qpdf and libseccomp, so the
  required independent/fault tests cannot silently skip in that job.
- `src/parser.rs:352` refuses to promote a locked reader. All callers propagate
  PyResult. `tests/test_security.py:231` verifies a failed read followed by unlock
  and exact secret recovery; AES round trips additionally retry after a wrong
  password. This preserves state instead of swallowing a parsing error.
- Batch default memory=0 matches the core. Explicit caps are rejected rather
  than ignored. Timeout is observed after job completion; the test checks both
  a failed report and the still-present output. Callback/ownership/cancellation
  tests remain in the regression suite.
- Parser tests independently serialize a complete PDF and assert binary bytes,
  parsed objects, offsets targeting their object headers, trailer Root/Size and
  completion across 1/7/64/4096-byte chunks. Event bridge conversion is unchanged.
- Public stubs, core pin and required behavioral entry points are enforced by
  the parity gate; removing options/results/tests/core pin is still detected.

## Hallazgos

1. Default nonzero batch memory cap rejected every batch after the core upgrade.
   Corrected default/stub to zero; explicit unsupported requests still fail.
2. Locked reader promotion lost unlock capability and exposed a parse error.
   Corrected before transition and verified recovery on the same instance.
3. Old parser fixtures expected lossy placeholders and accepted malformed input.
   Replaced those expectations with independent valid-input binary/object tests.
4. The parity negative-control fixture omitted the newly audited AES test file.
   Corrected the fixture copy list; all eight original control cases pass.

No unresolved finding in this delivery. Upstream #792/#793 remain explicitly
outside #253 and block their own capabilities. No general parser/redactor
security certification is inferred from this review.

## Calidad de Tests (Kripteia)

Both analyses executed with the quality-review script. AES: score 93, 3 functions;
batch: 95, 8 functions; parser payloads: 100, 6 functions. The skip decorator is
reported as ignore for the Linux fault test, but all 8 parametrized AES cases ran
locally and Linux CI requires the prerequisites. Reader/tier8/helper scans detect
no test functions; their score 100 is not evidence of native coverage.

## Análisis de Seguridad (Kripteia Security)

All six scoped scans report no security findings. Manual review checked Result
propagation, reader transition ownership, absence of new Rust unsafe blocks,
child-only seccomp filtering and absence of successful output on failure.
Test strings/passwords are public fixture sentinels. The ctypes function
signatures use a pointer-sized seccomp context and explicit integer arguments.

## Métricas y validación

- 17 tracked-file diffs plus new AES test/helper, compatibility document and
  evidence reviewed. Product changes are the pin, batch defaults and reader guard.
- Isolated wheel: initial library run 2668 passed, 8 fixture failures; after the
  fixture-only correction, all eight controls plus AES/parity passed (18 tests).
  No product change followed the full library run.
- MCP: 295 passed, 1 skipped, outside sandbox for IPC support.
- Clippy, no-default-features build, parity, typing inventory, package mypy and
  strict parser/batch consumer mypy pass; logs in this directory.
- Local review complete. Multiplatform CI and integration remain required and
  must be checked against the PR head before closing #253. No release performed.
