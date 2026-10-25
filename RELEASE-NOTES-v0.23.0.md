# oxidize-pdf 0.23.0

Release candidate from develop 03dde8b91b2c24257a2f460e41c500a16ff38ed5.
Core remains pinned to the published Rust 5.5.0. No new core or .NET release.

- Expose incremental text-note and highlight editors with typed identities,
  geometry, RGB colors, opacity and owned results. The core rejects mutations
  under DocMDP P=1/P=2 and allows annotations under P=3. Reading and empty
  mutation batches preserve the existing document. This delivers the Python
  adoption tracked by [core #712](https://github.com/bzsanti/oxidizePdf/issues/712); publication and installed-package checks are
  required before that issue closes.
- Add geometric annotation and incremental TaggedPdf editing, with explicit
  permission checks and atomic mutation batches.
- Expose RAG configuration, element graphs, custom token counters and document
  export; bounded bookmark reading and revision-aware semantic comparison.
- Return real pages from iteration, preserve incremental parser event payloads,
  and connect parser/recovery, batch, lazy and streaming options to core behavior.
- Add image pixel construction/inspection, marked content and Unicode ActualText,
  coordinate transforms, page geometry, clipping paths, dash patterns, blend modes
  and color conversions.
- Preserve structured signature errors and adopt fallible AES IV generation from
  core 5.5.0. Reconcile public typing with the runtime API.

## Compatibility and limits

Python 3.10+; wheels target Linux x64/ARM64, macOS x64/ARM64 and Windows x64.
Existing free-text and Ink APIs remain available. Incremental edits preserve
history and are not irreversible redaction. Synthetic DocMDP policy fixtures
verify permissions, not signature authenticity.

The core 5.5.0 batch executor rejects explicit nonzero memory caps; zero means
no global cap. Timeouts are reported after work completes and may leave output.
Rotate/Compress do not provide the requested transformations in this core;
see [core #797](https://github.com/bzsanti/oxidizePdf/issues/797) and do not infer functional support from successful jobs.
Unsupported recovery/streaming settings remain documented as such. Parser
recovery is not a fidelity guarantee or a global memory bound.

Real OCR, the draft OCR-layer binding, irreversible redaction and full functional
parity remain outside this release's claims (#244, #262, #263, #278). The draft
OCR PR #279 is excluded. No claim that core 5.5.0 includes fixes from 5.5.1/5.5.2.

## Validation

The integrated Python #293 head passed all 26 PR checks, followed by successful
CI and parity workflows on develop. A fresh installed wheel from that exact
source passed all 75 note/highlight tests, including the 17 DocMDP cases and
independent qpdf/Poppler checks, without skips. The earlier discriminating
policy mutation produced 12 expected failures while all five P3 controls passed.
Release-candidate metadata and hosted validation are recorded separately; this
file alone does not assert publication to PyPI.
