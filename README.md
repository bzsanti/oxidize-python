# oxidize-pdf

Python bindings for [oxidize-pdf](https://crates.io/crates/oxidize-pdf), a pure Rust PDF generation and manipulation library.

Generate, parse, split, merge, and manipulate PDF files from Python with native performance — no C dependencies, no Java, no subprocess calls.

## Installation

```bash
pip install oxidize-pdf
```

**Supported platforms:** Linux (x86_64, aarch64), macOS (x86_64, Apple Silicon), Windows (x86_64)
**Requires:** Python 3.10+

## Quick start

### Create a PDF

```python
from oxidize_pdf import Document, Page, Font, Color

doc = Document()
doc.set_title("My Document")
doc.set_author("Jane Doe")

page = Page.a4()
page.set_font(Font.HELVETICA, 24.0)
page.set_text_color(Color.black())
page.text_at(72.0, 750.0, "Hello from oxidize-pdf!")

page.set_font(Font.TIMES_ROMAN, 12.0)
page.text_at(72.0, 700.0, "Generated with Python + Rust.")

doc.add_page(page)
doc.save("output.pdf")
```

### Parse an existing PDF

```python
from oxidize_pdf import PdfReader

reader = PdfReader.open("document.pdf")
print(f"Pages: {reader.page_count}, Version: {reader.version}")

# Extract text from all pages
for i, text in enumerate(reader.extract_text()):
    print(f"--- Page {i + 1} ---")
    print(text)

# Inspect page dimensions
page = reader.get_page(0)
print(f"Size: {page.width} x {page.height} points")
```

## Operations

### Split a PDF into individual pages

```python
from oxidize_pdf import split_pdf

files = split_pdf("input.pdf", "output_dir/")
# Returns: ["output_dir/page_1.pdf", "output_dir/page_2.pdf", ...]
```

### Merge multiple PDFs

```python
from oxidize_pdf import merge_pdfs

merge_pdfs(["part1.pdf", "part2.pdf", "part3.pdf"], "merged.pdf")
```

### Rotate all pages

```python
from oxidize_pdf import rotate_pdf

rotate_pdf("input.pdf", "rotated.pdf", 90)  # 0, 90, 180, or 270 degrees
```

### Extract specific pages

```python
from oxidize_pdf import extract_pages

extract_pages("input.pdf", "subset.pdf", [0, 2, 4])  # 0-based indices
```

## Graphics

```python
from oxidize_pdf import Document, Page, Color

doc = Document()
page = Page.a4()

# Draw a filled rectangle
page.set_fill_color(Color.hex("#3498db"))
page.draw_rect(72.0, 700.0, 200.0, 100.0)
page.fill()

# Draw a circle with stroke
page.set_stroke_color(Color.red())
page.set_line_width(2.0)
page.draw_circle(300.0, 500.0, 50.0)
page.stroke()

# Draw a custom path
page.set_fill_color(Color.rgb(0.2, 0.8, 0.2))
page.move_to(100.0, 400.0)
page.line_to(200.0, 400.0)
page.line_to(150.0, 450.0)
page.close_path()
page.fill_and_stroke()

doc.add_page(page)
doc.save("graphics.pdf")
```

## Types

### Color

```python
from oxidize_pdf import Color

color = Color.rgb(1.0, 0.0, 0.0)       # Red (values 0.0–1.0)
color = Color.gray(0.5)                  # 50% gray
color = Color.cmyk(0.0, 1.0, 1.0, 0.0)  # CMYK red
color = Color.hex("#ff6600")             # From hex string
color = Color.black()                    # Convenience presets
```

### Point, Rectangle, Margins

```python
from oxidize_pdf import Point, Rectangle, Margins

point = Point(72.0, 720.0)
origin = Point.origin()

rect = Rectangle(Point(0.0, 0.0), Point(612.0, 792.0))
rect = Rectangle.from_xywh(72.0, 72.0, 468.0, 648.0)
print(f"{rect.width} x {rect.height}, center: {rect.center}")

margins = Margins(top=72.0, right=72.0, bottom=72.0, left=72.0)
margins = Margins.uniform(72.0)  # Same value for all sides
```

### Fonts

All 14 standard PDF fonts are available:

```python
from oxidize_pdf import Font

Font.HELVETICA             # Font.HELVETICA_BOLD
Font.TIMES_ROMAN           # Font.TIMES_BOLD
Font.COURIER               # Font.COURIER_BOLD
Font.SYMBOL                # Font.ZAPF_DINGBATS
# ... and italic/oblique variants
```

## Error handling

All exceptions inherit from `PdfError`:

```python
from oxidize_pdf import PdfReader, PdfError, PdfIoError, PdfParseError

try:
    reader = PdfReader.open("missing.pdf")
except PdfIoError as e:
    print(f"I/O error: {e}")
except PdfParseError as e:
    print(f"Parse error: {e}")
except PdfError as e:
    print(f"PDF error: {e}")
```

Exception hierarchy:
- `PdfError` — base class
  - `PdfIoError` — file I/O errors
  - `PdfParseError` — malformed PDF structure
  - `PdfEncryptionError` — encryption/decryption failures
  - `PdfPermissionError` — operation denied by document permissions

## Type checking

oxidize-pdf ships with type stubs and a `py.typed` marker. Full autocomplete and type checking work out of the box with mypy, pyright, and IDEs.

## Known limitations

- **Encryption write support**: `Document.encrypt()` configures encryption parameters but the underlying Rust library does not yet serialize the encryption dictionary to the PDF output. The `PdfReader.is_encrypted` / `unlock()` API for reading encrypted PDFs works correctly.
- **CPython only**: PyPy and GraalPy are not supported.

## License

MIT — see [LICENSE](LICENSE) for details.
