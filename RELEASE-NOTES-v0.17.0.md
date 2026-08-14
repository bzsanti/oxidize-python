# Release v0.17.0

## Summary

Updates the bundled `oxidize-pdf` core from `=4.2.0` to `=4.3.0` and exposes
its opt-in visual reading-order extraction in Python. The release also inherits
the core's correctness fixes for text positioning and decoding, page-operation
content preservation, encryption, and signature handling.

## Added — visual reading-order extraction

Two new `PdfReader` methods reorder separated flat-text blocks according to
their visual position instead of preserving the PDF content-stream order:

```python
from oxidize_pdf import PdfReader

reader = PdfReader.open("two-columns.pdf")

# One page (zero-based index)
page_text = reader.extract_text_from_page_with_reading_order(0)

# One string per page
document_text = reader.extract_text_with_reading_order()
```

This is useful for PDFs that draw the right column before the left column, or
draw lower sections before upper sections. The feature is explicit and opt-in:
the existing `extract_text_from_page()` and `extract_text()` methods retain
their previous stream-order behavior.

The ordering applies to the flat-text path. Layout-preserving extraction and
the existing column-reconstruction options remain separate APIs.

## Changed — core bumped to 4.3.0

Correctness fixes from core 4.3.0 reach existing Python APIs without caller
changes:

- Text extraction now tracks the graphics-state stack and more completely
  handles `Td`, `TD`, `T*`, `Tm`, `TJ`, and the quote text-showing operators.
  This prevents lines from collapsing onto a shared position and improves
  spacing and reading order in real-world content streams.
- PDF text strings distinguish textual decoding from binary security fields,
  improving metadata, signature, and encrypted-document handling without
  corrupting raw password or permission bytes.
- Page extraction, splitting, reordering, rotation, overlay, and merge paths
  preserve content and nested XObject streams more reliably, including image
  soft masks and transparency resources.
- Incremental form filling, signature detection, and PDF writing receive the
  corresponding 4.3.0 robustness fixes.

## Compatibility

- No breaking Python API changes. Both reading-order methods are additions.
- Wheels remain `cp310-abi3` and support Python 3.10+.
- MSRV remains Rust 1.88.
- `oxidize-pdf` is pinned to `=4.3.0` for reproducible native builds.

## Verification

- New cross-language regression coverage verifies that reading-order mode
  changes a deliberately right-column-first PDF to left-column-first output
  while the legacy API remains byte-for-byte stream ordered.
- New regression coverage verifies `TD`, `T*`, and `Tm` positioning through
  the public Python `extract_text_chunks()` path.
- GitHub Actions matrix: Linux, macOS, and Windows across Python 3.10–3.13.
- Release-wheel build, Clippy with warnings denied, and mypy all pass.
