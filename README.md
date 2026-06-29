<!-- mcp-name: io.github.bzsanti/oxidize-pdf-mcp -->
# oxidize-pdf

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

## Why oxidize-pdf?

| | oxidize-pdf | Pure-Python libs | C/Java wrappers |
|---|---|---|---|
| **Performance** | Native (compiled Rust) | Interpreted | Native but heavy |
| **Dependencies** | Zero | Varies | Poppler, Java, Ghostscript |
| **Memory safety** | Rust ownership model | GC-dependent | Manual / GC |
| **Type stubs** | Full (mypy/pyright) | Partial | Rare |
| **AI-ready (MCP)** | Built-in | No | No |

---

## MCP Server

Give your AI agent full PDF capabilities in one line:

```bash
oxidize-mcp
```

The built-in [Model Context Protocol](https://modelcontextprotocol.io/) server exposes **12 tools**, **6 resources**, and **5 prompts** — compatible with Claude, GPT, and any MCP client.

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
> on PDFs in the configured workspace directory. Remote/hosted use (e.g. the
> OpenAI Responses API hosted MCP tool) needs an HTTP transport and is not yet
> exposed.

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
