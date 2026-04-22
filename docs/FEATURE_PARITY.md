# Feature Parity — oxidize-python

Bridge version: 0.4.3
Core dependency: =2.5.5
Last updated: 2026-04-22

Reference: [API Surface definition](lifecycle/API_SURFACE.md)

Status values:
- `yes` — fully implemented and tested
- `partial` — implemented but with known gaps (see Notes)
- `no` — not yet implemented
- `n/a` — not applicable to this runtime

---

## DOC — Document creation

| Feature ID | Feature Name | Python |
|---|---|---|
| DOC-001 | Create empty document | yes |
| DOC-002 | Set document metadata | yes |
| DOC-003 | Add pages | yes |
| DOC-004 | Save to file | yes |
| DOC-005 | Save to bytes | yes |
| DOC-006 | Encrypt (RC4-128) | yes |
| DOC-007 | Permissions | yes |

## PAGE — Page creation

| Feature ID | Feature Name | Python |
|---|---|---|
| PAGE-001 | Arbitrary dimensions | yes |
| PAGE-002 | Standard presets | yes |
| PAGE-003 | Margins | yes |

## TXT — Text operations

| Feature ID | Feature Name | Python |
|---|---|---|
| TXT-001 | Standard fonts | yes |
| TXT-002 | Custom/embedded fonts | yes |
| TXT-003 | Text color | yes |
| TXT-004 | Character spacing | yes |
| TXT-005 | Word spacing | yes |
| TXT-006 | Line leading | yes |
| TXT-007 | Text at position | yes |
| TXT-008 | Text alignment | yes |

## GFX — Graphics operations

| Feature ID | Feature Name | Python |
|---|---|---|
| GFX-001 | Color spaces | yes |
| GFX-002 | Fill color | yes |
| GFX-003 | Stroke color | yes |
| GFX-004 | Line width | yes |
| GFX-005 | Fill opacity | yes |
| GFX-006 | Stroke opacity | yes |
| GFX-007 | Rectangle | yes |
| GFX-008 | Circle | yes |
| GFX-009 | Arbitrary paths | yes |
| GFX-010 | Fill | yes |
| GFX-011 | Stroke | yes |
| GFX-012 | Fill-and-stroke | yes |
| GFX-013 | Image embedding | yes |

## PARSE — PDF parsing

| Feature ID | Feature Name | Python |
|---|---|---|
| PARSE-001 | Open from file path | yes |
| PARSE-002 | Open from bytes | yes |
| PARSE-003 | Is-encrypted | yes |
| PARSE-004 | Unlock with password | yes |
| PARSE-005 | Page count | yes |
| PARSE-006 | PDF version | yes |
| PARSE-007 | Parsed page dimensions | yes |
| PARSE-008 | Extract text single page | yes |
| PARSE-009 | Extract text all pages | yes |
| PARSE-010 | Text chunking | yes |

## OPS — Document operations

| Feature ID | Feature Name | Python |
|---|---|---|
| OPS-001 | Split to files | yes |
| OPS-002 | Merge from files | yes |
| OPS-003 | Rotate all pages | yes |
| OPS-004 | Extract pages | yes |
| OPS-005 | Overlay/watermark | yes |
| OPS-006 | Page reordering | yes |

## ERR — Error model

| Feature ID | Feature Name | Python |
|---|---|---|
| ERR-001 | Base PdfError | yes |
| ERR-002 | PdfParseError | yes |
| ERR-003 | PdfIoError | yes |
| ERR-004 | PdfEncryptionError | yes |
| ERR-005 | PdfPermissionError | yes |

---

## Scope of this document

This table covers the **core PDF generation, parsing, and operations surface** that the ecosystem-wide parity framework tracks across bridges (Python, .NET, WASM). The Python bridge also exposes a larger feature set not represented in this core surface — tables, charts, dashboards, annotations (deep), forms (deep), AI/ML pipeline (`DocumentChunker`, `MarkdownExporter`, `RagChunk`), signatures, PDF/A validation, XMP metadata, templates, MCP server. Those live in the internal TDD plan (`.private/tdd-plan-full.md`) and in the `_oxidize_pdf.pyi` type stub.

## Known gaps

- **OCR**: the Rust core exposes a Tesseract-backed OCR provider (`oxidize-pdf-core/src/text/ocr/`), but it is **not wrapped in the Python bridge** yet. This is the main user-facing gap for scanned-PDF pipelines.
- **OPS-001**: `split_pdf` uses a hardcoded `page_{n}.pdf` naming pattern. The core may support custom patterns — check if this should be exposed.
