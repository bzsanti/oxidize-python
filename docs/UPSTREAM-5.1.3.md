# Upstream integration review — 2026-09-24

## Updated in this change

The native dependency is pinned from `=4.6.0` to `=5.1.3`, including its registry
checksum in `Cargo.lock`. The bridge package version is 0.19.0. Rust 1.88 and Python 3.10+ remain the declared minimums.

The published crate identifies source commit
`beb3fb9d74a55d2270472664d76524aeff7b43f0`. Its actual public API was inspected,
in addition to the upstream changelog. In particular, the changelog's claim
that v5 removed legacy operations does **not** match this artifact:
`operations::{merge_pdfs, split_pdf, MergeOptions, SplitOptions}` still exist.
Existing Python operations therefore retain their previous reconstruction
behavior. Updating the dependency alone does not make them lossless.

Compatibility adjustment: `MergeOptions.preserve_bookmarks` now defaults to
false, matching the core's reconstruction engine. Explicit `preserve_bookmarks=True`
or `preserve_forms=True` raises `PdfError` when merging: core 5.1.3 rejects
unsupported preservation instead of silently accepting these flags. Code relying
on their former acceptance must choose reconstruction without the flags, or wait
for the preservation API below; clearing a flag does not preserve that structure.

New Python integrations:

- `TextFragment.render_mode` returns the existing `TextRenderingMode` type,
  including `INVISIBLE` for retained OCR text. Modes compare by value; fragment
  equality also includes rendering mode so visible and invisible text differ.
- `ExtractionOptions(include_link_annotations=True)` appends URI annotation
  targets without following them, preserving annotation order and byte limits.
- `ExtractionOptions(include_unreliable_figure_text=True)` opts into fallback
  text from Figure scopes with Differences encodings and no ToUnicode mapping.
  The new core filters this text by default; this can change extraction output.
- Both new options are keyword-only and default to false. They work through
  `extract_text_with_options`, `extract_fragments_with_options`,
  `extract_fragments_from_page`, and `extract_page_text`.
- Type stubs cover these options, extraction results, fragments and rendering
  modes. CI checks a consumer example with strict typing and disallows `Any`.

```python
from oxidize_pdf import ExtractionOptions, PdfReader

reader = PdfReader.open("document.pdf")
result = reader.extract_page_text(0, ExtractionOptions(
    preserve_layout=True,
    include_link_annotations=True,
    max_extracted_bytes=1_000_000,
))
for fragment in result.fragments:
    print(fragment.text, fragment.render_mode)
print(result.text, result.truncated)
```

Existing entry points also inherit fixes for Standard-14 metrics, Type 3 width
scaling, indirect encodings, reading order, word boundaries, and lenient xref
recovery. Signature trust validation now uses `rustls-webpki`; the lockfile adds
`ring` and its platform dependencies. Wheel CI must cover this native build
dependency on all supported platforms.

## New integrations still required

These capabilities exist in the published core but are not exposed by this
change. Priority reflects preservation and user-visible utility, not effort.

| Priority | Core API | Python integration and acceptance criteria |
|---|---|---|
| P1 | `operations::existing_document` | Expose explicit preserve-base/reconstruct policies, planning and `SemanticPreservationReport` for merge, split and extraction. Test outlines, forms, annotations, metadata, signed/encrypted inputs and rejected secondary structures. Preserve-base is not an arbitrary semantic union. Keep existing reconstruction entry points compatible. |
| P1 | `plan_pdf_page_mutations`, `mutate_pdf_pages_lossless` | Typed reorder/insert/duplicate/remove batches, dry-run and atomic execution; verify original byte prefix and DocMDP rejection. Existing Python reorder/swap/move/reverse do not expose these guarantees. |
| P1 | `prepare_incremental_signature`, `PreparedSignature`, `SignatureAppearance` | Provider-neutral prepare/finalize lifecycle accepting caller-generated CMS, existing/new fields and bounded visible appearances. Test successive signatures, byte ranges, DocMDP/FieldMDP and text-fit errors. Current bindings detect/verify signatures, not this signing workflow. |
| P2 | `IncrementalHighlightEditor`, `IncrementalFreeTextEditor`, `IncrementalInkEditor`, `IncrementalGeometricEditor` | Enumerate and atomically add/update/remove annotations on existing PDFs; creation-time annotation bindings are not equivalent. Verify prefix preservation and rejected edits. |
| P2 | `IncrementalOcrLayerEditor` | Positioned invisible Unicode layers, dry-run, duplicate detection and metadata; verify extraction, byte preservation and rejection of certified/encrypted documents. No OCR engine is needed to accept caller-supplied text. |
| P2 | `PdfDocument::outline_with_options` | Bounded bookmark reading with resolved page destinations, styles and open state. Existing outline APIs create outlines. |
| P2 | `compare_pdfs_semantically` | Typed differences and revision attribution with configurable budgets. Existing comparison bindings do not expose this revision-aware API. |
| P2 | `SemanticRedactor::redact_irreversible` | Explicit security-grade redaction, budgets and report fields (`mode`, `residual_risks`, `is_irreversible`). Do not equate visual masking with removal; test forensic reparse and unsupported-content rejection. |
| P3 | `IncrementalTaggedPdfEditor`, tagged-PDF validation | Bounded structure/MCID/ParentTree editing and PDF/UA findings with policy-aware dry-run and preservation tests. |

For each new Python API, assess a matching MCP tool only after the binding,
error mapping and behavioral tests are in place. MCP options do not currently
expose the new extraction flags.

## Upstream changes beyond the published release

GitHub `develop` was checked on 2026-09-24 at `e1792e8`. These merged fixes are
after the published crate's source commit, so are **not** included in this pin:

- [#611](https://github.com/bzsanti/oxidizePdf/pull/611): escaped line breaks in PDF literal strings.
- [#612](https://github.com/bzsanti/oxidizePdf/pull/612): synthesized spaces before punctuation across text operators.
- [#614](https://github.com/bzsanti/oxidizePdf/pull/614): concatenation of multiple page Contents streams.

Adopt the next published release and add bridge-level regression fixtures for
these cases; no additional Python API is expected for these parser fixes.

## Local validation

- Editable native wheel built and installed with `maturin develop --locked --offline`.
- Full Python suite including MCP after QR fixes: **2513 passed**, on Linux / Python 3.12.
  This includes 21 new extraction cases and two preservation-rejection cases.
  Tests cover equality of all eight modes and exact UTF-8 byte budgets with
  Unicode URIs, separators and preceding text.
  MCP's first integration workflow stalled in the restricted sandbox; the full
  suite completed outside it.
- `cargo clippy --locked --offline --all-targets -- -D warnings` passed.
- `cargo check --locked --offline --no-default-features` passed.
- `cargo test --locked --offline` passed (the bridge has zero Rust unit tests;
  behavioral coverage is in Python).
- `mypy python/oxidize_pdf/`, `scripts/check_parity.py` and `git diff --check` passed.
- The consumer in `tests/typing/extraction.py` passes mypy with `--strict
  --disallow-any-expr`, including the Python 3.10 target. An invalid string value
  for `include_link_annotations` is rejected as expected.
- The two extraction calls flagged by rustfmt were corrected. The repository-wide
  formatting check still reports unrelated pre-existing formatting differences.
- Cross-platform wheel builds and the remaining Python versions require CI.

## Sources

- [Published crate](https://crates.io/crates/oxidize-pdf/5.1.3)
- [Pinned upstream source](https://github.com/bzsanti/oxidizePdf/tree/beb3fb9d74a55d2270472664d76524aeff7b43f0/oxidize-pdf-core/src)
- [Migration guide at the published commit](https://github.com/bzsanti/oxidizePdf/blob/beb3fb9d74a55d2270472664d76524aeff7b43f0/docs/migration/v5-existing-pdf-operations.md)
