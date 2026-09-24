# Release v0.19.0

Updates the bundled `oxidize-pdf` core from `=4.6.0` to `=5.1.3` and exposes
new text extraction metadata and controls.

## Added

- `TextFragment.render_mode` identifies all eight PDF text rendering modes,
  including invisible OCR text. `TextRenderingMode` compares by value, and
  fragment equality now distinguishes rendering modes.
- `ExtractionOptions(include_link_annotations=True)` appends URI annotation
  targets in annotation order, without following them. Extracted URIs count
  toward the UTF-8 byte budget.
- `ExtractionOptions(include_unreliable_figure_text=True)` retains fallback
  Figure text from fonts with Differences encodings but no ToUnicode mapping.
  Both new options are keyword-only and disabled by default.
- Type stubs for advanced extraction options, results, fragments, spacing
  decisions and rendering modes, with a strict consumer check in CI.

```python
from oxidize_pdf import ExtractionOptions, PdfReader, TextRenderingMode

reader = PdfReader.open("document.pdf")
result = reader.extract_page_text(0, ExtractionOptions(
    preserve_layout=True,
    include_link_annotations=True,
    max_extracted_bytes=1_000_000,
))
for fragment in result.fragments:
    if fragment.render_mode == TextRenderingMode.INVISIBLE:
        print("Invisible text:", fragment.text)
```

## Compatibility changes

- `MergeOptions.preserve_bookmarks` now defaults to `False`, matching the core
  reconstruction engine. Explicit `preserve_bookmarks=True` or
  `preserve_forms=True` raises `PdfError` when merging, rather than accepting an
  unsupported preservation request. Disabling these flags does not preserve
  those structures. Existing merge/split/extract APIs remain reconstructive;
  policy-driven preservation APIs are not yet exposed in Python.
- Core 5.1.3 filters unreliable Figure text by default. The new opt-in restores
  fallback extraction for forensic workflows; it does not make that text reliable.
- Existing APIs inherit improvements in font metrics, encodings, reading order,
  word boundaries, signature trust validation and lenient xref recovery.
- Wheels remain `cp310-abi3` for Python 3.10+. The declared MSRV remains Rust 1.88.

## Validation

- 2513 Python tests passed locally, including MCP and regression tests for mode
  equality, preservation rejection and exact Unicode extraction budgets.
- Clippy with warnings denied, compilation without the experimental SPI,
  package typing, the strict consumer example and the feature-parity check passed.

See [the upstream integration review](docs/UPSTREAM-5.1.3.md) for remaining
bindings and fixes merged upstream after the published 5.1.3 release.
