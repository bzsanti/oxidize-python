# Rust core 5.5.0 compatibility

The source pins the published registry crate `oxidize-pdf = "=5.5.0"`.
This is not a new Python package release and does not change an already
published wheel.

- Package commit: `55284b4821869141b291f772a7c909bd670e348e`.
- Registry checksum: `b10d71fadd841b51fc1f7549d946831afc56ec1fa5de7fcaf3c100a134bed9a8`.
- Dependency changes: core 5.4.2 → 5.5.0; adds pure-Rust `roxmltree 0.21.1`.

## AES security (#253)

AES IVs now use the fallible operating-system entropy source. AES-128 and AES-256
serialization propagates `PdfEncryptionError` when secure IV generation fails;
no successful byte result or valid completed PDF is produced. A failed file save
may leave an incomplete file; this change does not promise atomic filesystem
replacement.

The tests exercise the actual extension: native round trips on each platform,
independent qpdf decryption/wrong-password checks, and a Linux child process that
denies `getrandom` after warming the thread-local RNG. The fault test covers both
algorithms and byte/file saves. Linux Python 3.12 CI requires qpdf and libseccomp
before running these tests. Other platforms retain native round-trip coverage;
OS entropy fault injection is Linux-specific.

## Necessary compatibility changes

- `BatchOptions.memory_limit_per_worker` defaults to **0**, meaning no cap.
  Core rejects requested nonzero caps instead of pretending to enforce them.
  Job timeout is checked after completion: it reports a failure but does not
  interrupt work or roll back outputs.
- `IncrementalParser` requires valid PDF syntax and preserves binary stream
  bytes. Object, xref and trailer events contain parsed values rather than the
  old placeholders. Existing event keys and public types remain available.
- Reading a locked `PdfReader` raises `PdfEncryptionError` before promoting its
  state. A subsequent `unlock()` still works, including after a wrong password.

## Scope and evidence

The adoption does not close full parity #244. Redaction retains the residual-data
blocker [core #792](https://github.com/bzsanti/oxidizePdf/issues/792), and
LayoutManager retains [core #793](https://github.com/bzsanti/oxidizePdf/issues/793).
TaggedPdf/OCR/streaming option bindings remain separately tracked.

Local delivery validation and review are recorded under `evidence/issue-253/`.
CI and integration status belong to the delivery PR, not the core version number.
