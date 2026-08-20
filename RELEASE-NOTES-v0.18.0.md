# Release v0.18.0

## Summary

Updates the bundled `oxidize-pdf` core from `=4.3.0` to `=4.6.0` and exposes
the new parser-side font-resolution, Type 3 glyph, and bounded in-memory image
extraction APIs in Python.

## Added — resolved font resources

`PdfReader.resolve_font(page_index, resource_name)` returns a
`ResolvedFontResource` with renderer-oriented information for simple, Type 0,
CID, Symbol, and Type 3 fonts:

- base font, subtype, encoding, writing mode, and encoding differences;
- decoded embedded Type 1, TrueType, CFF, CID-CFF, or OpenType font bytes;
- source code, CID, GID, Unicode text, and advance width for decoded glyphs;
- consistent decoding through `ResolvedFontResource.decode_glyphs()`.

```python
from oxidize_pdf import PdfReader

reader = PdfReader.open("document.pdf")
font = reader.resolve_font(0, "F1")
glyphs = font.decode_glyphs(b"Hello")

for glyph in glyphs:
    print(glyph.source_code, glyph.cid, glyph.gid, glyph.unicode, glyph.advance)
```

## Added — Type 3 glyph programs

Resolved Type 3 fonts expose their `FontMatrix`, `FontBBox`, character-code to
CharProc mapping, declared and procedure widths, optional glyph bounding box,
and parsed `ContentOperation` sequence. Downstream renderers can therefore draw
opaque pdfTeX-style Type 3 glyphs without inventing Unicode mappings.

```python
font = reader.resolve_font(0, "F1")
if font.type3 is not None:
    glyph = font.type3.glyph(0x10)
    if glyph is not None:
        for operation in glyph.operations:
            print(operation.op_type)
```

## Added — bounded in-memory image extraction

`extract_images_in_memory()` returns typed `ExtractedImageData` objects without
creating directories or files. `ImageExtractionLimits` can bound image count,
encoded bytes per image, total encoded bytes, and decoded pixels per image.
Extraction can cover the entire document or one zero-based page.

```python
from oxidize_pdf import ImageExtractionLimits, extract_images_in_memory

limits = ImageExtractionLimits(
    max_images=100,
    max_encoded_bytes_per_image=20_000_000,
    max_total_encoded_bytes=100_000_000,
    max_decoded_pixels_per_image=40_000_000,
)
images = extract_images_in_memory("document.pdf", limits)

for image in images:
    print(image.page_number, image.width, image.height, image.format, len(image.data))
```

## Changed — core bumped to 4.6.0

Existing Python APIs inherit the core releases from 4.4.0 through 4.6.0,
including improvements to text positioning and flat-path spacing, structure
element `ActualText`, page operations, stream decoding, font resolution, and
image extraction. Incremental form-fill tests now accept the core's valid hex
string serialization for field values.

## Compatibility

- No existing Python APIs are removed or changed incompatibly.
- Wheels remain `cp310-abi3` and support Python 3.10+.
- MSRV remains Rust 1.88.
- `oxidize-pdf` is pinned to `=4.6.0` for reproducible native builds.
- Resource-limit violations in in-memory image extraction raise `ValueError`;
  parser and operation failures continue through the existing PDF exception
  hierarchy.

## Verification

- Behavioral tests cover Type 3 CharProc resolution, glyph decoding, in-memory
  JPEG extraction, and encoded-byte limit enforcement.
- The integration PR passed the Linux, macOS, and Windows matrix for Python
  3.10 through 3.13, the feature-parity check, and the release-wheel build.
- Local validation includes the Rust workspace tests, Clippy with warnings
  denied, and the Python suite.
