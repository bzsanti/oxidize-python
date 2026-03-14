# oxidize-pdf Core API Surface

This file defines the canonical feature identifiers used in bridge `FEATURE_PARITY.md` files.
It is maintained manually and updated whenever a feature is added to or removed from oxidize-pdf.

Last updated: 2026-03-14 (core v2.3.0)

---

## Feature Groups

### DOC — Document creation

| Feature ID | Description | Core since |
|---|---|---|
| DOC-001 | Create empty document (`Document::new`) | 2.0.0 |
| DOC-002 | Set document metadata (title, author, subject, keywords, creator) | 2.0.0 |
| DOC-003 | Add pages to document | 2.0.0 |
| DOC-004 | Save document to file path | 2.0.0 |
| DOC-005 | Save document to byte buffer | 2.0.0 |
| DOC-006 | Encrypt document (RC4-128, user + owner passwords) | 2.0.0 |
| DOC-007 | Document permissions (print, copy, modify, etc.) | 2.0.0 |

### PAGE — Page creation and layout

| Feature ID | Description | Core since |
|---|---|---|
| PAGE-001 | Create page with arbitrary dimensions | 2.0.0 |
| PAGE-002 | Standard page presets (A4, A4 landscape, Letter, Letter landscape, Legal) | 2.0.0 |
| PAGE-003 | Page margins | 2.0.0 |

### TXT — Text operations

| Feature ID | Description | Core since |
|---|---|---|
| TXT-001 | Set font (standard 14 PDF fonts) | 2.0.0 |
| TXT-002 | Custom/embedded fonts | 2.0.0 |
| TXT-003 | Set text color | 2.0.0 |
| TXT-004 | Character spacing | 2.0.0 |
| TXT-005 | Word spacing | 2.0.0 |
| TXT-006 | Line leading | 2.0.0 |
| TXT-007 | Text at position (`text_at`) | 2.0.0 |
| TXT-008 | Text alignment (Left, Right, Center, Justified) | 2.0.0 |

### GFX — Graphics operations

| Feature ID | Description | Core since |
|---|---|---|
| GFX-001 | Color spaces (RGB, Grayscale, CMYK, Hex) | 2.0.0 |
| GFX-002 | Fill color | 2.0.0 |
| GFX-003 | Stroke color | 2.0.0 |
| GFX-004 | Line width | 2.0.0 |
| GFX-005 | Fill opacity | 2.0.0 |
| GFX-006 | Stroke opacity | 2.0.0 |
| GFX-007 | Rectangle path | 2.0.0 |
| GFX-008 | Circle path | 2.0.0 |
| GFX-009 | Arbitrary paths (move_to, line_to, curve_to, close_path) | 2.0.0 |
| GFX-010 | Fill path | 2.0.0 |
| GFX-011 | Stroke path | 2.0.0 |
| GFX-012 | Fill-and-stroke path | 2.0.0 |
| GFX-013 | Image embedding (JPEG, PNG) | (TBD) |

### PARSE — PDF parsing / reading

| Feature ID | Description | Core since |
|---|---|---|
| PARSE-001 | Open PDF from file path | 2.0.0 |
| PARSE-002 | Open PDF from byte buffer | 2.0.0 |
| PARSE-003 | Is-encrypted check | 2.0.0 |
| PARSE-004 | Unlock encrypted PDF (user/owner password) | 2.0.0 |
| PARSE-005 | Page count | 2.0.0 |
| PARSE-006 | PDF version string | 2.0.0 |
| PARSE-007 | Get parsed page (dimensions, rotation) | 2.0.0 |
| PARSE-008 | Extract text from single page | 2.0.0 |
| PARSE-009 | Extract text from all pages | 2.0.0 |
| PARSE-010 | Text chunking / positional text extraction | 2.1.0 |

### OPS — Document operations

| Feature ID | Description | Core since |
|---|---|---|
| OPS-001 | Split PDF into single-page files | 2.0.0 |
| OPS-002 | Merge multiple PDFs into one | 2.0.0 |
| OPS-003 | Rotate all pages | 2.0.0 |
| OPS-004 | Extract specific pages to new PDF | 2.0.0 |
| OPS-005 | Overlay / watermark | (TBD) |
| OPS-006 | Page reordering | (TBD) |

### ERR — Error model

| Feature ID | Description | Core since |
|---|---|---|
| ERR-001 | Base PDF error | 2.0.0 |
| ERR-002 | Parse error (distinct from IO) | 2.0.0 |
| ERR-003 | IO error | 2.0.0 |
| ERR-004 | Encryption error | 2.0.0 |
| ERR-005 | Permission error | 2.0.0 |

---

## TBD features

Features marked `(TBD)` do not yet exist in the core. They are listed here to ensure
bridge parity tracking includes them when they land.
