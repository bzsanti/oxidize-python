# Rust core 5.5.3 compatibility

Historical checkpoint: current adoption is documented in [5.5.4 notes](UPSTREAM-5.5.4.md).

Tracking: #296. Development pins the registry dependency `oxidize-pdf = "=5.5.3"`.
This is a source dependency update, not a new Python/NuGet package publication.
Existing package versions and public binding surface remain unchanged.

The previous pin was 5.5.0. Core 5.5.1 and 5.5.2 include stricter redaction and
form-permission checks, page-label/font/URI/annotation corrections and changes
to batch operation behavior. Core 5.5.3 adds page-tree consistency, OCR geometry
and Unicode corrections, and generation allocation/metric improvements.
See the upstream [5.5.1](https://github.com/bzsanti/oxidizePdf/blob/v5.5.1/docs/releases/5.5.1.md),
[5.5.2](https://github.com/bzsanti/oxidizePdf/blob/v5.5.2/docs/releases/5.5.2.md)
and [5.5.3](https://github.com/bzsanti/oxidizePdf/blob/v5.5.3/docs/releases/5.5.3.md)
compatibility notes. Core benchmark percentages are not binding benchmarks.

The dependency pin does not expose missing OCR APIs or complete the remaining
parity issues. Existing unsupported operations remain explicit. Historical
upstream blocker references must be re-evaluated against 5.5.3 before working
on their corresponding binding issues; they are not closure evidence by themselves.

## Validation

Registry 5.5.3 is published and not yanked. Both the exact pin and registry
checksum are verified: `ac23cc2913977d436332f433faa48686cbd9b096c7f45f36de8d8278d8715b5a`.
Only the core package changes in dependency resolution. No local path override
remains. Local build and regression checks passed; multiplatform CI is tracked by the adoption PR.

## Existing Python batch APIs

`BatchJob.rotate` now rotates the selected pages and composes their existing
angles instead of reporting a successful file copy. Rotation reconstructs the
PDF: it does not preserve signatures, annotations, forms, original page boxes
or all document-level structures. `BatchJob.compress` now produces a failed
job result without creating or replacing output; check the batch summary and
per-job error. It no longer reports an unchanged copy as successful compression.
The regression contracts execute both public APIs, verify selected page angles
and preserve the source and existing compression destination.

Local Python 3.12 validation: 3,117 tests passed and two skipped, including MCP;
11 focused batch/parity cases passed independently. The registry-backed extension
built successfully; Clippy with warnings denied, parity and typing checks passed.
Global rustfmt reports pre-existing formatting in unchanged Rust source; this
adoption does not reformat it. No Python Rust implementation file changes.

[Review and validation evidence](evidence/core-5.5.3/review.md).
