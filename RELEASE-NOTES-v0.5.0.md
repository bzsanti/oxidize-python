# Release v0.5.0

## Summary

Minor release that completes the parity-spec backlog on the Python side and ships the upstream `oxidize-pdf` 2.6.0 security hardening.

Twelve of fourteen Tier 1–4 parity tasks are now closed in `oxidize-python`. The remaining two — Tesseract OCR bridge (Tier 8) and the Haystack converter (Tier 2, lives in `oxidize-pdf-integrations`) — are tracked separately.

## Security

- **CWE-20 NaN/inf bypass in colour content-stream emission** (upstream `oxidize-pdf` #220). Direct construction of `Color::Rgb(f64::NAN, ...)` (and the `Gray`/`Cmyk` variants) bypassed the clamping in `Color::rgb`/`gray`/`cmyk` constructors. Without sanitisation at the emission boundary, the `{:.3}` formatter wrote literal `NaN`/`inf`/`-inf` tokens to content streams; ISO 32000-1 §7.3.3 rejects those, so conformant viewers refused the entire content stream (availability DoS via crafted input). Fixed in upstream 2.6.0 by routing every colour emitter through a sanitising helper that substitutes `0.0` for non-finite components. ~50 emitter sites across 17 files in upstream were patched. Inherited by this bridge through the dependency bump.

## Added

### OPS-002 — `SplitOptions` + `split_pdf_with_options`

```python
from oxidize_pdf import PageRange, SplitMode, SplitOptions, split_pdf_with_options

opts = SplitOptions(
    SplitMode.ranges([PageRange.range(0, 4), PageRange.single(7)]),
    output_pattern="/tmp/chapter_{}.pdf",
    preserve_metadata=True,
    optimize=False,
)
paths = split_pdf_with_options("/path/to/book.pdf", opts)
```

- `SplitMode.ranges(list[PageRange])` — exposes the upstream `SplitMode::Ranges` variant that previously had no Python constructor.
- `SplitOptions(mode, output_pattern="page_{}.pdf", preserve_metadata=True, optimize=False)` — full shape mirroring `oxidize_pdf::operations::SplitOptions`.
- `split_pdf_with_options(input_path, options) -> list[str]` — returns the paths of the emitted files.

### OPS-004 — `MergeInput` + `merge_pdfs_with_inputs`

```python
from oxidize_pdf import MergeInput, PageRange, merge_pdfs_with_inputs

merge_pdfs_with_inputs(
    [
        MergeInput("/path/to/intro.pdf"),                         # all pages
        MergeInput("/path/to/body.pdf", pages=PageRange.range(0, 49)),
        MergeInput.with_pages("/path/to/appendix.pdf", PageRange.list([2, 5])),
    ],
    "/path/to/output.pdf",
)
```

- `MergeInput(path, pages: PageRange | None = None)` — pyclass that pairs a file path with an optional per-input page range.
- `MergeInput.with_pages(path, pages)` — chainable static convenience constructor.
- `merge_pdfs_with_inputs(inputs, output_path, options=None)` — accepts a list of `MergeInput` objects and an optional `MergeOptions`.

## Architectural decision recorded

`MergeOptions.page_ranges` is intentionally **not** exposed from this bridge. Upstream declares the field but the merger (`oxidize-pdf-core/src/operations/merge.rs:135`) reads `MergeInput.pages`, never `options.page_ranges` — the latter is referenced only in upstream's own unit tests. Surfacing it from Python would have created a no-op API surface. The per-input model (`MergeInput.pages`) is the one the merger actually consumes.

## Changed

- **Upstream pin**: `oxidize-pdf = "=2.5.5"` → `"=2.6.0"`.
- **Bridge version**: `0.4.3` → `0.5.0` (minor bump driven by additive public API: `SplitOptions`, `MergeInput`, `split_pdf_with_options`, `merge_pdfs_with_inputs`, `SplitMode.ranges`).
- **MCP `server.json`**: bumped to `0.5.0` to match the PyPI package.
- **`docs/PARITY_SPEC.md`**: rows OPS-002 and OPS-004 flipped to ✅ on the Python column; ecosystem rows OPS-011 and OPS-012 flipped from ❌/❌ to ✅/❌ with the action moved to the .NET column. Cross-repo sync against `oxidize-pdf-dotnet/docs/PARITY_SPEC.md` is a follow-up maintenance ritual; this release does not modify that copy.
- **`docs/FEATURE_PARITY.md`**: bridge version + core dependency checkpoint refreshed.

## Bug Fixes

- Inherits the wire-format consistency fix from upstream 2.6.0: every colour-operator emission now uses `.3`-precision uniformly. PDF/A consumers that relied on the previous implicit RGB normalisation in `forms/choice_widget.rs` should verify their output intent — non-RGB colours now emit `g` (Gray) or `k` (CMYK) operators instead of being lossily converted to `rg`.

## Breaking Changes

None at the Python API surface. The behavioural changes from upstream 2.6.0 (native colour-space emission in form widgets, `.3`-precision uniformity) are wire-format refinements that affect generated PDFs, not the bridge's call signatures.

## Compatibility verified before release

- `errors.rs::to_py_err` has a wildcard arm; the new upstream `PdfError::TableOverflow` variant does not break the dispatch.
- `TableStyle` is built via constructors; the new `header_font` / `header_bold` fields default to `None`.
- `Color::{Rgb,Gray,Cmyk}` matches in `types.rs` and `graphics_extraction.rs` remain exhaustive.
- `default-features = false` isolates the bridge from upstream's default-feature change.

## Validation

- `cargo build --release`: clean, no warnings.
- `pytest tests/ --ignore=tests/mcp_tests`: **1944 passed** (1920 baseline + 24 new content-verifying tests across `tests/test_split_with_options.py` and `tests/test_merge_with_inputs.py`).
- `mypy python/oxidize_pdf/`: clean.
