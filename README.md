<!-- mcp-name: io.github.bzsanti/oxidize-pdf-mcp -->

# oxidize-pdf

> Rust core pinned to **5.4.2**. See [compatibility and validation](docs/UPSTREAM-5.4.2.md).

<!-- mcp-name: io.github.bzsanti/oxidize-pdf-mcp -->

[![PyPI version](https://img.shields.io/pypi/v/oxidize-pdf)](https://pypi.org/project/oxidize-pdf/)
[![CI](https://github.com/bzsanti/oxidize-python/actions/workflows/ci.yml/badge.svg)](https://github.com/bzsanti/oxidize-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/pypi/pyversions/oxidize-pdf)](https://pypi.org/project/oxidize-pdf/)
[![Typed](https://img.shields.io/badge/typing-typed-green)](https://github.com/bzsanti/oxidize-python)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple)](https://modelcontextprotocol.io/)

[![oxidize-python MCP server](https://glama.ai/mcp/servers/bzsanti/oxidize-python/badges/card.svg)](https://glama.ai/mcp/servers/bzsanti/oxidize-python)

**Rust-powered PDF library for Python.** Generate, parse, split, merge, and manipulate PDFs with native performance. Ships with a built-in [MCP server](#mcp-server) so AI agents can work with PDFs out of the box.

No C dependencies. No Java. No subprocess calls.

## Installation

```bash
pip install oxidize-pdf            # Core library
pip install "oxidize-pdf[mcp]"     # + MCP server for AI agents
```

**Platforms:** Linux (x86_64, aarch64) | macOS (x86_64, Apple Silicon) | Windows (x86_64)
**Requires:** Python 3.10+

Version 0.22.0 pins Rust core **5.4.2**, using the MIT-licensed `oxidize-webpki`
RustCrypto provider for certificate verification. See the
[dependency policy](docs/NO-NATIVE-CRYPTO.md) for supported builds and limits.
New APIs include explicit text recovery, non-breaking-space normalization,
build identification controls and incremental signature slots. See the
[API guide and validation](docs/UPSTREAM-5.4.1.md).

The current develop branch contains post-release parity work. See the
[current capability inventory](docs/FEATURE_PARITY.md) and
[Python/.NET comparison](docs/PARITY_SPEC.md) for the audited subset, missing
bindings and inherited core limitations. Neither the core version nor the type
stubs establish full functional parity; no global coverage percentage is claimed.

## Why oxidize-pdf?

| | oxidize-pdf | Pure-Python libs | C/Java wrappers |
|---|---|---|---|
| **Performance** | Native (compiled Rust) | Interpreted | Native but heavy |
| **Dependencies** | Zero | Varies | Poppler, Java, Ghostscript |
| **Memory safety** | Rust ownership model | GC-dependent | Manual / GC |
| **Type stubs** | Public API inventory + strict mypy checks on develop | Varies | Varies |
| **AI-ready (MCP)** | Built-in | No | No |

---

## MCP Server

Expose the supported PDF tools to your AI agent:

```bash
oxidize-mcp
```

The built-in [Model Context Protocol](https://modelcontextprotocol.io/) server exposes **12 tools**, **5 static resources plus a session resource template**, and **5 prompts** over stdio. Install `oxidize-pdf[mcp]` to include its dependencies; the base library keeps MCP optional.

Version 0.20 uses FastMCP 4 and MCP Python SDK 2, with support for both modern and legacy stdio clients. See the [migration guide](docs/MCP-V2-MIGRATION.md) for versions and installation routes.

If `tools/list` returns an empty array with an older installation (issue [#198](https://github.com/bzsanti/oxidize-python/issues/198)), upgrade to 0.20.0 or newer. These versions fix tool registration when starting `server.py` directly. On Windows, use the same Python environment for installation and startup:

```powershell
python -m pip install --upgrade "oxidize-pdf[mcp]"
python -m oxidize_pdf.mcp.server
```

For a custom JSON-RPC client, send `initialize`, wait for its response, then send `notifications/initialized` before `tools/list`. Read newline-delimited JSON-RPC from stdout and keep stderr separate; the startup banner is written to stderr.

### Claude Desktop integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "oxidize-pdf": {
      "command": "oxidize-mcp",
      "env": {
        "OXIDIZE_WORKSPACE": "/path/to/your/pdfs"
      }
    }
  }
}
```

### GitHub Copilot (VS Code) integration

Copilot's agent mode speaks MCP. Add `.vscode/mcp.json` to your workspace:

```json
{
  "servers": {
    "oxidize-pdf": {
      "command": "oxidize-mcp",
      "env": {
        "OXIDIZE_WORKSPACE": "/path/to/your/pdfs"
      }
    }
  }
}
```

Open the Chat view, switch to **Agent** mode, and the 12 PDF tools appear in
the tool picker. (The same block also works under the `mcp.servers` key in your
user `settings.json` if you prefer a global install.)

### OpenAI Agents SDK integration

The [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/mcp/)
spawns the server over stdio and exposes its tools to an agent:

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

async with MCPServerStdio(
    params={"command": "oxidize-mcp", "env": {"OXIDIZE_WORKSPACE": "/path/to/your/pdfs"}},
    cache_tools_list=True,
) as server:
    agent = Agent(
        name="PDF assistant",
        instructions="Use the oxidize-pdf tools to inspect and manipulate PDFs.",
        mcp_servers=[server],
    )
    result = await Runner.run(agent, "How many pages does report.pdf have?")
    print(result.final_output)
```

A runnable version is in [`examples/openai_agents_quickstart.py`](examples/openai_agents_quickstart.py).

> Both integrations run the server **locally over stdio**, so its tools operate
> on PDFs in the configured workspace directory. This package does not expose
> a hosted HTTP endpoint. ChatGPT web needs a remote connection; developer-mode
> testing can also use [Secure MCP Tunnel](https://developers.openai.com/plugins/deploy/connect-chatgpt)
> with a local stdio server. No ChatGPT plugin is published by this migration.

### Available tools

| Tool | What it does |
|------|-------------|
| `read_pdf` | Read metadata — page count, version, encryption status, title, author |
| `extract_text` | Extract text from all pages or a specific page |
| `convert_pdf` | Convert to markdown, chunks, or RAG-optimized format |
| `create_pdf` | Create a new PDF with optional metadata |
| `save_pdf` | Save a session to disk, with optional encryption |
| `add_content` | Add pages, text, and graphics to a session |
| `annotate_pdf` | Add text annotations and highlights |
| `manipulate_pdf` | Split, merge, rotate, extract pages, reverse, overlay |
| `manage_forms` | Create, fill, read, and validate form fields |
| `secure_pdf` | Encrypt, check permissions, verify signatures |
| `extract_entities` | Extract structured entities from pages |
| `analyze_pdf` | Validate structure, detect corruption, check PDF/A compliance |

The server also exposes **resources** (session data, capabilities, version info) and **prompts** (guided workflows for summarization, data extraction, form filling, and more).

### Configuration

```bash
OXIDIZE_WORKSPACE=/path/to/pdfs oxidize-mcp
```

The server is configured entirely through environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `OXIDIZE_WORKSPACE` | `~/Documents/oxidize-mcp` | Sandbox root; all paths must resolve inside it. |
| `OXIDIZE_ALLOWED_PATHS` | _(none)_ | Comma-separated extra directories allowed outside the workspace. |
| `OXIDIZE_MAX_FILE_SIZE_MB` | `100` | Reject input PDFs larger than this on disk. |
| `OXIDIZE_MAX_PAGES` | `10000` | Reject documents with more pages than this before any extraction work. |
| `OXIDIZE_MAX_OUTPUT_BYTES` | `10485760` | Cap the serialized size of a tool's JSON response (10 MB). |
| `OXIDIZE_MAX_SESSIONS` | `10` | Maximum concurrent stateful PDF-creation sessions. |
| `OXIDIZE_MAX_SESSION_BYTES` | `10485760` | Cap the content a single session may accumulate (10 MB). |
| `OXIDIZE_SESSION_TIMEOUT` | `3600` | Session expiry, in seconds. |

Resource caps (`OXIDIZE_MAX_*`) protect the server from a large or malicious
PDF: oversized documents are rejected up front and tool responses are bounded
rather than serialized unbounded. Exceeding a cap returns an error with code
`RESOURCE_LIMIT`.

Or start programmatically:

```python
from oxidize_pdf.mcp.server import run
run()
```

---

## Python API

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

for i, text in enumerate(reader.extract_text()):
    print(f"--- Page {i + 1} ---")
    print(text)
```

### Inspect tagged PDF structure

```python
from pathlib import Path
from oxidize_pdf import TaggedPdfLimits, TaggedPdfValidationOptions, validate_tagged_pdf

report = validate_tagged_pdf(
    Path("input.pdf").read_bytes(),
    TaggedPdfValidationOptions(TaggedPdfLimits(max_depth=64)),
)
for finding in report.findings:
    print(finding.severity, finding.code, finding.path, finding.message)
```

The report includes structure elements, artifacts, role/class maps, the parent
number tree and content MCIDs. Original dictionary values remain typed
`PdfValue` objects, including unknown attributes and reference generations.
Results are immutable snapshots; returned lists and dictionaries are owned copies.

`valid` means the core validator found no error-level findings. It is **not a
PDF/UA certificate**: an untagged PDF can have `tagged=False`, `valid=True` and a
`MissingStructureTree` warning. Malformed input raises `PdfParseError`, locked
input raises `PdfEncryptionError`, and exceeded validation budgets raise `PdfError`.

`TaggedPdfLimits` bounds visited objects, traversal depth, entries and decoded
content bytes (defaults: 100,000; 256; 1,000,000; 256 MiB). These are core validator
budgets, not a process memory or time limit: input copying and initial PDF parsing
occur before traversal. No PDF bytes are modified.

### Operations

```python
from oxidize_pdf import split_pdf, merge_pdfs, rotate_pdf, extract_pages

split_pdf("input.pdf", "output_dir/")                       # Split into individual pages
merge_pdfs(["part1.pdf", "part2.pdf"], "merged.pdf")         # Merge multiple PDFs
rotate_pdf("input.pdf", "rotated.pdf", 90)                   # Rotate all pages
extract_pages("input.pdf", "subset.pdf", [0, 2, 4])          # Extract specific pages
```

### Graphics

```python
from oxidize_pdf import Document, Page, Color

doc = Document()
page = Page.a4()

page.set_fill_color(Color.hex("#3498db"))
page.draw_rect(72.0, 700.0, 200.0, 100.0)
page.fill()

page.set_stroke_color(Color.red())
page.set_line_width(2.0)
page.draw_circle(300.0, 500.0, 50.0)
page.stroke()

doc.add_page(page)
doc.save("graphics.pdf")
```

### Types

```python
from oxidize_pdf import Color, Point, Rectangle, Margins, Font

# Colors
Color.rgb(1.0, 0.0, 0.0)          # RGB
Color.hex("#ff6600")               # Hex
Color.cmyk(0.0, 1.0, 1.0, 0.0)   # CMYK

# Geometry
Point(72.0, 720.0)
Rectangle.from_xywh(72.0, 72.0, 468.0, 648.0)
Margins.uniform(72.0)

# Fonts — all 14 standard PDF fonts
Font.HELVETICA    # Font.HELVETICA_BOLD
Font.TIMES_ROMAN  # Font.TIMES_BOLD
Font.COURIER      # Font.COURIER_BOLD
```

### Error handling

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

Exception hierarchy: `PdfError` > `PdfIoError`, `PdfParseError`, `PdfEncryptionError`, `PdfPermissionError`

## MCP Server

oxidize-pdf includes an [MCP](https://modelcontextprotocol.io/) server that exposes PDF capabilities to AI assistants like Claude. Install with the `mcp` extra:

```bash
pip install oxidize-pdf[mcp]
```

### Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "oxidize-pdf": {
      "command": "uvx",
      "args": ["--from", "oxidize-pdf[mcp]", "oxidize-mcp"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add oxidize-pdf -- uvx --from "oxidize-pdf[mcp]" oxidize-mcp
```

### Available tools

| Tool | Description |
|---|---|
| `read_pdf` | Open a PDF and get metadata (pages, version, encryption) |
| `extract_text` | Extract text content from PDF pages |
| `convert_pdf` | Convert between PDF versions |
| `analyze_pdf` | Analyze structure, fonts, images, and compliance |
| `extract_entities` | Extract images and digital signatures |
| `manipulate_pdf` | Split, merge, rotate, extract, and reorder pages |
| `annotate_pdf` | Add text annotations, highlights, and stamps |
| `manage_forms` | Create, fill, and read PDF form fields |
| `secure_pdf` | Encrypt, decrypt, and set document permissions |
| `create_pdf` | Create a new PDF document with pages |
| `add_pdf_content` | Add text, shapes, and images to pages |
| `save_pdf` | Save the document to file or bytes |

### Resources

- `oxidize://fonts` — Available built-in PDF fonts
- `oxidize://page-sizes` — Standard page sizes with dimensions
- `oxidize://capabilities` — Server capabilities and tool listing
- `oxidize://version` — Version information
- `oxidize://workspace` — PDF files in the workspace directory
- `oxidize://session/{id}` — Session data by ID

## Known limitations

- **Encryption write support**: `Document.encrypt()` configures encryption parameters but the underlying Rust library does not yet serialize the encryption dictionary to the PDF output. Reading encrypted PDFs works correctly.
- **Image extraction returns raw embedded streams**: `extract_images_from_pdf` extracts each embedded image as-is (e.g. a `DCTDecode` JPEG is written byte-for-byte). Image *preprocessing* — auto rotation-correction, contrast enhancement, denoise, upscaling, force-grayscale — is not available, because the build excludes the upstream `external-images` feature (and its `image`-crate dependency). This keeps extraction faithful and lossless; it does not silently return empty or stub results.
- **CPython only**: PyPy and GraalPy are not supported.

## License

MIT — see [LICENSE](LICENSE) for details.

### Semantic comparison with revision history

```python
from oxidize_pdf import (
    compare_pdfs_semantically, SemanticComparisonLimits, SemanticComparisonOptions,
)

options = SemanticComparisonOptions(SemanticComparisonLimits(
    max_objects=100_000, max_depth=256,
    max_decoded_stream_bytes=256 * 1024 * 1024,
    max_canonical_bytes=256 * 1024 * 1024,
    max_extracted_text_bytes=64 * 1024 * 1024,
    max_unreachable_objects=10_000, max_revisions=1024,
))
result = compare_pdfs_semantically(original_bytes, revised_bytes, options)
for difference in result.differences:
    print(difference.path, difference.class_, difference.description)
for revision in result.right_revisions:
    print(revision.index, revision.xref_offset, revision.semantic_fingerprint.hex())
    for change in revision.object_changes:
        print(change.object_number, change.generation, change.kind)
```

The immutable result exposes both revision histories, unreachable object
identities and pairs of semantically equivalent objects. Collection properties
return independent snapshots. Revision fingerprints are 32-byte hashes, and
revisions are ordered oldest first. `class_` is the Python spelling of Rust's
`class` field. Difference classes are Visual, Textual, Structural, Metadata,
Security and SerializationOnly. `semantically_equal` may be true when the only
difference is SerializationOnly; it includes supported historical semantics,
so restoring the latest state does not erase an intervening semantic change.

Limits apply independently to each document. Decoded/canonical budgets count
work across repeated traversals, not just unique input bytes. Initial input
copies, parsing and some extraction allocations precede these checks; the
options are not process-wide memory/time limits. Malformed input, exceeded
budgets and unsupported decoding raise PDF errors; encrypted input raises
`PdfPermissionError` and must be decrypted before comparison.

This API compares the core's supported object/text domains, not rendered pixels,
and does not certify signatures or irreversible redaction. Core 5.4.2 includes
physical ObjStm/XRef containers among objects unreachable from Root/Info. A
qpdf conversion to object streams can therefore report Structural differences
at `/UnreachableObjects` and `/Revisions` despite equal text and page content.
The binding preserves that conservative result; it does not promise equivalence
across every PDF layout. The existing `compare_pdfs` API remains available.

### Images from pixel buffers

```python
from oxidize_pdf import Image, ImageColorSpace

rgb = Image.from_raw_data(b'\xff\x00\x00', 1, 1, ImageColorSpace.DeviceRGB)
gray = Image.from_gray_data(b'\x80', 1, 1)
rgba = Image.from_rgba_data(b'\xff\x00\x00\x80', 1, 1)
assert rgba.alpha_data == b'\x80'
assert rgba.soft_mask.data == b'\x80'
```

`from_raw_data(data, width, height, color_space, bits_per_component=8)` accepts
DeviceGray, DeviceRGB and DeviceCMYK. Components are packed in pixel order, most
significant bits first, with each scanline padded to a whole byte. Supported
component depths are 1, 2, 4, 8 and 16; 16-bit components use big-endian byte
order. RGBA and grayscale convenience constructors use 8-bit components.

All three constructors require positive dimensions and an exact buffer length.
Invalid sizes/depths raise `ValueError`; values outside unsigned argument ranges
raise `OverflowError`. The RGBA/gray constructors reject products exceeding
`u32::MAX` before calling the published core's dimension arithmetic. Validation
happens before copying the pixel buffer.

`data`, `format`, `bits_per_component`, `alpha_data` and `soft_mask` expose owned
snapshots. `ImageFormat` distinguishes Jpeg, Png, Tiff and Raw. Data is the core's
image payload: JPEG remains encoded, while PNG/TIFF constructors expose decoded
pixel data. RGBA separates RGB data from alpha; its soft mask can be inspected
independently. These APIs use the existing core without `external-images` or
new dependencies. Explicit mask creation/application and writer-object export
remain outside this increment.

### Marked content on new pages

`Page.begin_marked_content(tag)` and
`Page.begin_marked_content_with_actual_text(tag, actual_text)` return a page-local
MCID. Pair every begin with `Page.end_marked_content()`; `next_mcid()` and
`marked_content_depth()` inspect the state. Tags are nonempty literal names
(UTF-8 bytes are PDF-name escaped, so pass `"Span"`, not `"/Span"`). Empty tags
raise `ValueError` without changing state; ending an empty stack raises `PdfError`.

```python
page = Page.a4()
page.set_font(Font.HELVETICA, 12)
mcid = page.begin_marked_content_with_actual_text("Span", "café 😀")
page.text_at(40, 700, "visible glyphs")
page.end_marked_content()
```

ActualText is a Unicode logical replacement; copying/extraction depends on the
viewer honoring it. For tagged structure, attach the returned ID using
`StructureElement.add_mcid(page_index, mcid)` and install the tree with
`Document.set_struct_tree(tree)`. These operations alone do not certify PDF/UA.
The core writes these markers in the text context; they are intended for text
operations, not as a general scope around separately buffered graphics.

### Coordinate transformations

`TransformMatrix(a, b, c, d, e, f)` exposes immutable affine components,
`IDENTITY`, `translate`, `scale`, `rotate` (radians), `flip_y`, `multiply`,
`transform_point(Point)` and `to_pdf_ctm()`. Composition `a.multiply(b)` applies
`b` first, then `a`. Values retain the core's floating-point semantics, including
singular and nonfinite matrices; validate them before using the CTM in a PDF.

```python
from oxidize_pdf import CoordinateSystem, Point, TransformMatrix

matrix = TransformMatrix.translate(10, 20).multiply(TransformMatrix.scale(2, 3))
point = matrix.transform_point(Point(4, 5))  # Point(18, 35)
custom = CoordinateSystem.custom(matrix)
pdf_point = custom.to_pdf_standard(Point(4, 5), 800)  # Point(18, 35)
```

`CoordinateSystem` supports point, Y-only and matrix conversions to PDF
coordinates, plus `grows_upward()`. For custom systems, Y-only conversion uses
x=0, orientation tests `d > 0`, and page height is ignored. `Page.coordinate_system`
returns a snapshot of the stored system. In core 5.4.2, setting this property
through `set_coordinate_system` does not automatically transform page content;
convert positions explicitly. `LayoutManager` remains outside this binding increment.


`RenderContext(coordinate_system, page_width, page_height)` stores mutable
`coordinate_system`, `page_width`, `page_height` and `current_transform` fields.
Its `to_pdf_standard(Point)` and `y_to_pdf(y)` methods use the current system and
height. The matrix is initialized from the constructor's system and height;
later field assignments do not recalculate it, and conversions do not read it.
This preserves core 5.4.2 behavior. Getters return independent value snapshots.
Use `context.current_transform.transform_point(point)` when you explicitly want
to apply the stored matrix. Numeric fields retain the core's f64 semantics.


`Page.content_width` and `Page.content_height` subtract the page margins.
`Page.content_area` returns `(left, bottom, right, top)` bounds in unrotated PDF
coordinates, rather than a position and size. These read-only properties reflect
current margins and can be negative or inverted when margins exceed page size.
`Page.effective_width` and `Page.effective_height` reflect rotation: 90°/270° swap
width and height. They use the full page dimensions, without subtracting margins.
Setting a coordinate system does not change these geometry properties.

### Custom clipping paths

```python
from oxidize_pdf import ClippingPath, WindingRule

clip = (ClippingPath().add_rect(10, 10, 80, 80)
        .add_polygon([(30, 30), (70, 30), (50, 70)])
        .with_winding_rule(WindingRule.EvenOdd))
page.set_clipping_path(clip)
```

`move_to`, `line_to`, `curve_to`, `close_path` and `add_rect`, `add_circle`,
`add_ellipse`, `add_rounded_rect`, `add_polygon` mutate and return the same path.
`with_winding_rule` returns an independent copy; the default is `NonZero`.
`clear()` removes commands while preserving the rule. `is_empty` reports whether
commands exist. `Page.set_clipping_path` retains a copy.

`commands` returns owned `ClippingPathCommand` snapshots with read-only `kind`
and copied `coordinates`: move/line use `[x, y]`, cubic curves use two control
points and an endpoint `[x1, y1, x2, y2, x3, y3]`, rectangles use
`[x, y, width, height]`, and close has no coordinates. Coordinates are PDF user
space values; callers supply valid finite geometry. `to_pdf_operations()` emits
the core's clipping operators, including `W`/`W*` and `n`.
The existing `rect`, `circle`, and `ellipse` factories remain available.
This API does not expose path intersection, text clipping, or a clipping stack.
