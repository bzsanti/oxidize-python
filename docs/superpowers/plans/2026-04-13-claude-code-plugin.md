# oxidize-pdf Claude Code Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a Claude Code plugin that exposes oxidize-pdf's PDF manipulation capabilities through 6 skills, 1 agent, and an MCP server, distributed via a self-hosted marketplace.

**Architecture:** Monorepo `oxidize-pdf-integrations` with `claude-code/` subdirectory containing the plugin. Bootstrap script (`bin/launch-mcp`) handles dependency detection and MCP server launch. Marketplace at repo root enables direct GitHub installation.

**Tech Stack:** Bash (bootstrap script), Markdown (skills/agent), JSON (manifests/config), Python/FastMCP (MCP server from oxidize-pdf PyPI package)

**Spec:** `docs/superpowers/specs/2026-04-13-claude-code-plugin-design.md`

**Remote:** `git@github.com-bzsanti:bzsanti/oxidize-pdf-integrations.git`

---

## File Map

| File | Responsibility |
|------|---------------|
| `claude-code/.claude-plugin/plugin.json` | Plugin manifest (name, version, metadata) |
| `claude-code/.mcp.json` | MCP server configuration pointing to launch script |
| `claude-code/hooks/hooks.json` | SessionStart hook for dependency check |
| `claude-code/bin/launch-mcp` | Bash bootstrap: detect/install oxidize-pdf, launch MCP |
| `claude-code/skills/read-pdf/SKILL.md` | Skill: read PDF metadata and info |
| `claude-code/skills/extract-text/SKILL.md` | Skill: extract text and convert formats |
| `claude-code/skills/create-pdf/SKILL.md` | Skill: create PDFs from scratch |
| `claude-code/skills/analyze-pdf/SKILL.md` | Skill: validate, corruption, compliance, compare |
| `claude-code/skills/secure-pdf/SKILL.md` | Skill: encrypt, permissions, signatures |
| `claude-code/skills/manipulate-pdf/SKILL.md` | Skill: split, merge, rotate, annotate, forms |
| `claude-code/agents/pdf-specialist.md` | Agent: orchestrates all 12 MCP tools |
| `.claude-plugin/marketplace.json` | Self-hosted marketplace catalog |
| `LICENSE` | MIT license |
| `README.md` | Installation and usage docs |
| `CHANGELOG.md` | Version history |

---

### Task 1: Initialize repo and plugin scaffold

**Files:**
- Create: `.claude-plugin/marketplace.json`
- Create: `claude-code/.claude-plugin/plugin.json`
- Create: `LICENSE`
- Create: `README.md`
- Create: `CHANGELOG.md`

- [ ] **Step 1: Create the repo directory and initialize git**

```bash
mkdir -p /home/santi/repos/BelowZero/oxidizePdf/oxidize-pdf-integrations
cd /home/santi/repos/BelowZero/oxidizePdf/oxidize-pdf-integrations
git init
git remote add origin git@github.com-bzsanti:bzsanti/oxidize-pdf-integrations.git
```

- [ ] **Step 2: Create plugin manifest**

Create `claude-code/.claude-plugin/plugin.json`:

```json
{
  "name": "oxidize-pdf",
  "version": "1.0.0",
  "description": "PDF reading, creation, analysis, manipulation, and security powered by oxidize-pdf",
  "author": {
    "name": "BelowZero",
    "url": "https://github.com/bzsanti"
  },
  "homepage": "https://github.com/bzsanti/oxidize-pdf-integrations",
  "repository": "https://github.com/bzsanti/oxidize-pdf-integrations",
  "license": "MIT",
  "keywords": ["pdf", "document", "analysis", "creation", "manipulation", "security", "forms", "annotations"]
}
```

- [ ] **Step 3: Create marketplace manifest**

Create `.claude-plugin/marketplace.json`:

```json
{
  "name": "oxidize-pdf",
  "owner": {
    "name": "BelowZero"
  },
  "metadata": {
    "description": "PDF manipulation tools powered by oxidize-pdf (Rust core + Python bridge)"
  },
  "plugins": [
    {
      "name": "oxidize-pdf",
      "source": "./claude-code",
      "description": "PDF reading, creation, analysis, manipulation, and security for Claude Code",
      "version": "1.0.0",
      "keywords": ["pdf", "document", "analysis", "creation", "manipulation"],
      "category": "tools"
    }
  ]
}
```

- [ ] **Step 4: Create LICENSE (MIT)**

Create `LICENSE`:

```
MIT License

Copyright (c) 2026 BelowZero

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 5: Create README.md**

Create `README.md`:

```markdown
# oxidize-pdf Integrations

Platform integrations for [oxidize-pdf](https://pypi.org/project/oxidize-pdf/), a high-performance PDF library powered by Rust.

## Claude Code Plugin

A plugin that gives Claude full PDF manipulation capabilities: read, create, analyze, manipulate, secure, and transform PDF documents.

### Install

Add the marketplace and install:

```shell
/plugin marketplace add bzsanti/oxidize-pdf-integrations
/plugin install oxidize-pdf@oxidize-pdf
```

### What's included

- **6 skills**: `/oxidize-pdf:read-pdf`, `/oxidize-pdf:extract-text`, `/oxidize-pdf:create-pdf`, `/oxidize-pdf:analyze-pdf`, `/oxidize-pdf:secure-pdf`, `/oxidize-pdf:manipulate-pdf`
- **1 agent**: `oxidize-pdf:pdf-specialist` — orchestrates all PDF tools for complex workflows
- **MCP server**: 12 tools, 6 resources for complete PDF manipulation

### Requirements

- Python 3.10+
- `oxidize-pdf` is auto-installed if not found in your environment

## Other Integrations

Future integrations (VS Code, JetBrains, Cursor) will live in separate subdirectories.

## License

MIT
```

- [ ] **Step 6: Create CHANGELOG.md**

Create `CHANGELOG.md`:

```markdown
# Changelog

## [1.0.0] - 2026-04-13

### Added
- Claude Code plugin with 6 skills, 1 agent, and MCP server integration
- Self-hosted marketplace for direct GitHub installation
- Bootstrap script with smart dependency detection
```

- [ ] **Step 7: Commit scaffold**

```bash
git add -A
git commit -m "feat: initialize oxidize-pdf-integrations monorepo with plugin scaffold"
```

---

### Task 2: Bootstrap script (`bin/launch-mcp`)

**Files:**
- Create: `claude-code/bin/launch-mcp`

- [ ] **Step 1: Write the failing test — verify script exists and is executable**

```bash
test -x claude-code/bin/launch-mcp && echo "PASS" || echo "FAIL: script not found or not executable"
```

Expected: FAIL

- [ ] **Step 2: Create the bootstrap script**

Create `claude-code/bin/launch-mcp`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Bootstrap script for oxidize-pdf MCP server.
# Modes:
#   check  — verify oxidize-pdf is available, install if needed (SessionStart hook)
#   serve  — launch the MCP server with the correct Python environment

PLUGIN_DATA="${OXIDIZE_PLUGIN_DATA:-${CLAUDE_PLUGIN_DATA:-}}"
VENV_DIR="${PLUGIN_DATA}/venv"

find_python() {
    if command -v python3 &>/dev/null; then
        echo "python3"
    elif command -v python &>/dev/null; then
        echo "python"
    else
        echo ""
    fi
}

has_oxidize() {
    local py="$1"
    "$py" -c "import oxidize_pdf" &>/dev/null 2>&1
}

ensure_venv() {
    local py="$1"
    if [ ! -d "$VENV_DIR" ]; then
        echo "[oxidize-pdf] Installing into plugin environment..."
        "$py" -m venv "$VENV_DIR"
    fi
    "$VENV_DIR/bin/pip" install --quiet --upgrade oxidize-pdf
}

PYTHON=$(find_python)
if [ -z "$PYTHON" ]; then
    echo "[oxidize-pdf] ERROR: Python 3.10+ is required but not found in PATH."
    exit 1
fi

MODE="${1:-serve}"

if [ "$MODE" = "check" ]; then
    if has_oxidize "$PYTHON"; then
        echo "[oxidize-pdf] Found in current environment."
        exit 0
    fi
    if [ -n "$PLUGIN_DATA" ]; then
        if [ -d "$VENV_DIR" ] && has_oxidize "$VENV_DIR/bin/python"; then
            echo "[oxidize-pdf] Found in plugin environment."
            exit 0
        fi
        ensure_venv "$PYTHON"
        echo "[oxidize-pdf] Installed in plugin environment."
        exit 0
    fi
    echo "[oxidize-pdf] Not found. Install with: pip install oxidize-pdf"
    exit 1
fi

if [ "$MODE" = "serve" ]; then
    if has_oxidize "$PYTHON"; then
        exec "$PYTHON" -c "from oxidize_pdf.mcp.server import run; run()"
    fi
    if [ -n "$PLUGIN_DATA" ] && [ -d "$VENV_DIR" ] && has_oxidize "$VENV_DIR/bin/python"; then
        exec "$VENV_DIR/bin/python" -c "from oxidize_pdf.mcp.server import run; run()"
    fi
    echo "[oxidize-pdf] ERROR: oxidize-pdf not found. Run '/oxidize-pdf:read-pdf' to trigger setup or install manually: pip install oxidize-pdf"
    exit 1
fi

echo "[oxidize-pdf] Unknown mode: $MODE. Use 'check' or 'serve'."
exit 1
```

- [ ] **Step 3: Make the script executable**

```bash
chmod +x claude-code/bin/launch-mcp
```

- [ ] **Step 4: Run the test again**

```bash
test -x claude-code/bin/launch-mcp && echo "PASS" || echo "FAIL"
```

Expected: PASS

- [ ] **Step 5: Test syntax validation**

```bash
bash -n claude-code/bin/launch-mcp && echo "PASS: no syntax errors" || echo "FAIL"
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add claude-code/bin/launch-mcp
git commit -m "feat: add bootstrap script for MCP server dependency management"
```

---

### Task 3: MCP and hooks configuration

**Files:**
- Create: `claude-code/.mcp.json`
- Create: `claude-code/hooks/hooks.json`

- [ ] **Step 1: Create MCP server config**

Create `claude-code/.mcp.json`:

```json
{
  "mcpServers": {
    "oxidize-pdf": {
      "command": "${CLAUDE_PLUGIN_ROOT}/bin/launch-mcp",
      "args": ["serve"],
      "env": {
        "OXIDIZE_PLUGIN_DATA": "${CLAUDE_PLUGIN_DATA}"
      }
    }
  }
}
```

- [ ] **Step 2: Create hooks config**

Create `claude-code/hooks/hooks.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/bin/launch-mcp check"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Validate JSON syntax**

```bash
python3 -m json.tool claude-code/.mcp.json > /dev/null && echo "PASS: .mcp.json valid"
python3 -m json.tool claude-code/hooks/hooks.json > /dev/null && echo "PASS: hooks.json valid"
```

Expected: Both PASS

- [ ] **Step 4: Commit**

```bash
git add claude-code/.mcp.json claude-code/hooks/hooks.json
git commit -m "feat: add MCP server and SessionStart hook configuration"
```

---

### Task 4: Skill — read-pdf

**Files:**
- Create: `claude-code/skills/read-pdf/SKILL.md`

- [ ] **Step 1: Create the skill**

Create `claude-code/skills/read-pdf/SKILL.md`:

```markdown
---
name: read-pdf
description: >
  Read PDF metadata, page count, and document information. Use when the user wants
  to open, inspect, or get info about a PDF file — page count, title, author,
  encryption status, or per-page dimensions.
---

# Read PDF

Read metadata and structural information from a PDF file using the `read_pdf` MCP tool.

## Tool: `read_pdf`

**Parameters:**
- `path` (required): Path to the PDF file
- `password` (optional): Password to unlock encrypted PDFs
- `include_page_details` (optional, default false): Include per-page width, height, and rotation

**Returns:** JSON with `page_count`, `is_encrypted`, `version`, `title`, `author`, `subject`, `keywords`. When `include_page_details=true`, includes a `pages` array with `index`, `width`, `height`, `rotation` per page.

## Usage patterns

**Basic metadata:**
Call `read_pdf` with the file path. Report the page count, title, author, and encryption status.

**Encrypted PDFs:**
If the response includes `"locked": true`, ask the user for a password and retry with the `password` parameter.

**Page dimensions:**
When the user asks about page sizes or layout, use `include_page_details=true` to get width/height per page. Dimensions are in PDF points (72 points = 1 inch).

## Examples

- "What's in report.pdf?" → `read_pdf(path="report.pdf")`
- "How many pages?" → `read_pdf(path="doc.pdf")` then report `page_count`
- "Is this encrypted?" → `read_pdf(path="secret.pdf")` then check `is_encrypted`
- "What are the page dimensions?" → `read_pdf(path="doc.pdf", include_page_details=true)`
```

- [ ] **Step 2: Verify file exists and has frontmatter**

```bash
head -5 claude-code/skills/read-pdf/SKILL.md | grep -q "^name: read-pdf" && echo "PASS" || echo "FAIL"
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add claude-code/skills/read-pdf/SKILL.md
git commit -m "feat: add read-pdf skill"
```

---

### Task 5: Skill — extract-text

**Files:**
- Create: `claude-code/skills/extract-text/SKILL.md`

- [ ] **Step 1: Create the skill**

Create `claude-code/skills/extract-text/SKILL.md`:

```markdown
---
name: extract-text
description: >
  Extract text content from PDF documents and convert PDFs to markdown, chunks,
  or RAG format. Use when the user wants text from a PDF, needs to search within
  a PDF, or wants to convert PDF to another text representation.
---

# Extract Text

Extract text content from PDFs and convert to different formats using `extract_text` and `convert_pdf` MCP tools.

## Tool: `extract_text`

**Parameters:**
- `path` (required): Path to the PDF file
- `page` (optional): Specific page index (0-based) to extract from
- `password` (optional): Password for encrypted PDFs

**Returns:** JSON with `text` (extracted content), `page_count`, and optionally `page` index.

## Tool: `convert_pdf`

**Parameters:**
- `path` (required): Path to the PDF file
- `format` (required): One of `"markdown"`, `"chunks"`, `"rag"`
- `password` (optional): Password for encrypted PDFs
- `max_tokens` (optional, default 256): Token limit per chunk (for `chunks` format)
- `overlap` (optional, default 50): Token overlap between chunks (for `chunks` format)

**Returns:**
- `markdown`: `{"content": "...", "format": "markdown"}`
- `chunks`: `{"chunks": [{"id", "content", "tokens", "chunk_index", "page_numbers"}], "format": "chunks"}`
- `rag`: `{"chunks": [{"text", "chunk_index", "page_numbers", "token_estimate", "heading_context"}], "format": "rag"}`

## Usage patterns

**Full text extraction:**
Call `extract_text` with just the path. The entire document text is returned.

**Single page:**
Use the `page` parameter (0-based index). Good when the user says "page 3" — pass `page=2`.

**Markdown conversion:**
Use `convert_pdf` with `format="markdown"` for structured output with headings and formatting.

**RAG ingestion:**
Use `convert_pdf` with `format="rag"` for semantic chunks with heading context, optimized for embedding.

**LLM-sized chunks:**
Use `convert_pdf` with `format="chunks"` and adjust `max_tokens` for your context window.

## Examples

- "Extract text from report.pdf" → `extract_text(path="report.pdf")`
- "Get text from page 5" → `extract_text(path="doc.pdf", page=4)`
- "Convert to markdown" → `convert_pdf(path="doc.pdf", format="markdown")`
- "Prepare for RAG" → `convert_pdf(path="doc.pdf", format="rag")`
- "Split into 512-token chunks" → `convert_pdf(path="doc.pdf", format="chunks", max_tokens=512)`
```

- [ ] **Step 2: Verify file exists and has frontmatter**

```bash
head -5 claude-code/skills/extract-text/SKILL.md | grep -q "^name: extract-text" && echo "PASS" || echo "FAIL"
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add claude-code/skills/extract-text/SKILL.md
git commit -m "feat: add extract-text skill"
```

---

### Task 6: Skill — create-pdf

**Files:**
- Create: `claude-code/skills/create-pdf/SKILL.md`

- [ ] **Step 1: Create the skill**

Create `claude-code/skills/create-pdf/SKILL.md`:

```markdown
---
name: create-pdf
description: >
  Create new PDF documents from scratch with text and styling. Use when the user
  wants to generate a new PDF, create a report, build an invoice, or compose
  any document from scratch.
---

# Create PDF

Create new PDF documents using a stateful three-step workflow: `create_pdf` → `add_pdf_content` (repeat) → `save_pdf`.

## Step 1: Start session with `create_pdf`

**Parameters:**
- `title` (required): Document title
- `author` (optional): Document author
- `page_size` (optional, default "a4"): Page size — use `oxidize://page-sizes` resource for available options

**Returns:** `{"session_id": "...", "status": "created", "page_size": "a4"}`

Save the `session_id` — it is required for all subsequent calls.

## Step 2: Add content with `add_pdf_content`

**Parameters:**
- `session_id` (required): From step 1
- `content_type` (required): `"text"` or `"new_page"`
- `content` (for text): The text string to add
- `x`, `y` (for text): Position in PDF points (origin is bottom-left, 72 points = 1 inch)
- `font` (optional): Font name — use `oxidize://fonts` resource for available options
- `font_size` (optional, default 12.0): Font size in points

Call this tool multiple times to build up the document content. Use `content_type="new_page"` to add additional pages.

## Step 3: Save with `save_pdf`

**Parameters:**
- `session_id` (required): From step 1
- `output_path` (required): Where to save the PDF file
- `user_password` (optional): Set user password for encryption
- `owner_password` (optional): Set owner password for encryption

**Returns:** `{"status": "ok", "path": "...", "page_count": N}`

## Coordinate system

- Origin (0, 0) is at the **bottom-left** of the page
- X increases to the right, Y increases upward
- A4 dimensions: 595.28 x 841.89 points
- Letter dimensions: 612.0 x 792.0 points
- Title at top of A4: y ~ 800, body text starts at y ~ 750, decreasing ~15 per line

## Usage patterns

**Simple document:**
1. `create_pdf(title="My Report")`
2. `add_pdf_content(session_id=ID, content_type="text", content="Title", x=50, y=800, font_size=24)`
3. `add_pdf_content(session_id=ID, content_type="text", content="Body text...", x=50, y=750, font_size=12)`
4. `save_pdf(session_id=ID, output_path="report.pdf")`

**Multi-page document:**
After filling a page, call `add_pdf_content(session_id=ID, content_type="new_page")` then continue adding text to the new page starting at the top (y ~ 800 for A4).

**Encrypted document:**
Pass both `user_password` and `owner_password` to `save_pdf`.

## Examples

- "Create a one-page report" → create_pdf + add_pdf_content (text) + save_pdf
- "Make an invoice for Acme Corp" → create_pdf(title="Invoice - Acme Corp") + multiple add_pdf_content + save_pdf
- "Create an encrypted PDF" → full workflow + save_pdf with passwords
```

- [ ] **Step 2: Verify file exists and has frontmatter**

```bash
head -5 claude-code/skills/create-pdf/SKILL.md | grep -q "^name: create-pdf" && echo "PASS" || echo "FAIL"
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add claude-code/skills/create-pdf/SKILL.md
git commit -m "feat: add create-pdf skill"
```

---

### Task 7: Skill — analyze-pdf

**Files:**
- Create: `claude-code/skills/analyze-pdf/SKILL.md`

- [ ] **Step 1: Create the skill**

Create `claude-code/skills/analyze-pdf/SKILL.md`:

```markdown
---
name: analyze-pdf
description: >
  Analyze PDF structure, validate integrity, detect corruption, check PDF/A
  compliance, compare two documents, and extract structured entities (text chunks
  with position and font info). Use when the user wants to validate, audit,
  compare, or deeply inspect PDF documents.
---

# Analyze PDF

Analyze and inspect PDF documents using `analyze_pdf` and `extract_entities` MCP tools.

## Tool: `analyze_pdf`

**Parameters:**
- `path` (required): Path to the PDF file
- `check` (optional, default "validate"): Analysis mode — one of:
  - `"validate"` — Check structural validity, report error/warning counts
  - `"corruption"` — Detect corruption, report severity and type
  - `"compliance"` — Check PDF/A compliance against a specific level
  - `"compare"` — Compare two PDFs for structural and content equivalence
- `compare_path` (required for compare): Path to the second PDF
- `compliance_level` (optional, default "a1b"): PDF/A level — `a1a`, `a1b`, `a2a`, `a2b`, `a2u`, `a3a`, `a3b`, `a3u`

**Returns by mode:**
- validate: `{"valid", "error_count", "warning_count"}`
- corruption: `{"corrupted", "corruption_type", "severity", "found_pages", "file_size", "errors"}`
- compliance: `{"level", "is_valid", "error_count", "warning_count", "compliance_percentage"}`
- compare: `{"structurally_equivalent", "content_equivalent", "similarity_score", "difference_count"}`

## Tool: `extract_entities`

**Parameters:**
- `path` (required): Path to the PDF file

**Returns:** `{"entities": [{"text", "page", "x", "y", "font_size", "font_name"}], "entity_count", "page_count"}`

Extracts every text chunk with its position, font, and page index. Use for detailed layout analysis or when you need to understand document structure beyond plain text.

## Usage patterns

**Quick validation:**
Call `analyze_pdf` with default `check="validate"`. Report whether the PDF is valid and any error/warning counts.

**Corruption check:**
Use `check="corruption"`. Severity 0 = no corruption. Higher values indicate more severe issues.

**PDF/A compliance:**
Use `check="compliance"`. The `compliance_percentage` shows how close the document is to meeting the standard.

**Document comparison:**
Use `check="compare"` with both `path` and `compare_path`. Report similarity score and differences.

**Layout analysis:**
Use `extract_entities` to get text positions. Useful for understanding document layout, finding headers, or locating specific content regions.

**Comprehensive audit:**
Chain multiple calls: validate → corruption → compliance → extract_entities for a full document report.

## Examples

- "Is this PDF valid?" → `analyze_pdf(path="doc.pdf")`
- "Check for corruption" → `analyze_pdf(path="doc.pdf", check="corruption")`
- "Is this PDF/A-2b compliant?" → `analyze_pdf(path="doc.pdf", check="compliance", compliance_level="a2b")`
- "Compare these two PDFs" → `analyze_pdf(path="v1.pdf", check="compare", compare_path="v2.pdf")`
- "Show me the document layout" → `extract_entities(path="doc.pdf")`
```

- [ ] **Step 2: Verify file exists and has frontmatter**

```bash
head -5 claude-code/skills/analyze-pdf/SKILL.md | grep -q "^name: analyze-pdf" && echo "PASS" || echo "FAIL"
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add claude-code/skills/analyze-pdf/SKILL.md
git commit -m "feat: add analyze-pdf skill"
```

---

### Task 8: Skill — secure-pdf

**Files:**
- Create: `claude-code/skills/secure-pdf/SKILL.md`

- [ ] **Step 1: Create the skill**

Create `claude-code/skills/secure-pdf/SKILL.md`:

```markdown
---
name: secure-pdf
description: >
  Encrypt PDFs with passwords, check encryption status and permissions, and verify
  digital signatures. Use when the user wants to password-protect a PDF, check if
  a PDF is encrypted, inspect permissions, or verify signatures.
---

# Secure PDF

Secure PDF operations using the `secure_pdf` MCP tool.

## Tool: `secure_pdf`

**Parameters:**
- `operation` (required): One of `"encrypt"`, `"permissions"`, `"verify_signatures"`
- `input_path` (required for all operations): Path to the source PDF
- `output_path` (required for encrypt): Path to save the encrypted PDF
- `user_password` (required for encrypt): Password users need to open the PDF
- `owner_password` (required for encrypt): Password for full access (editing, printing)
- `password` (optional for permissions): Password to unlock and check a locked PDF

## Operations

### encrypt

Encrypts a PDF with user and owner passwords. Both passwords are required.

**Important limitation:** Encryption reconstructs the document preserving text content and layout, but may lose non-text elements (images, embedded fonts, vector graphics). Warn the user about this before encrypting documents with images.

**Returns:** `{"status": "ok", "operation": "encrypt", "page_count": N, "note": "..."}`

### permissions

Checks if a PDF is encrypted and reports its status. Pass a `password` to unlock and inspect a locked PDF.

**Returns:** `{"path", "is_encrypted", "unlocked", "permissions": {"encrypted": bool}}`

### verify_signatures

Verifies digital signatures in a PDF. Reports each signature's validity and signer.

**Returns:** `{"path", "signatures": [{"valid", "signer"}], "signature_count": N}`

## Usage patterns

**Encrypt a PDF:**
1. First `read_pdf` to confirm the document content
2. Warn user about non-text element limitation
3. Call `secure_pdf(operation="encrypt", input_path=..., output_path=..., user_password=..., owner_password=...)`

**Check encryption status:**
Call `secure_pdf(operation="permissions", input_path=...)`.

**Verify signatures:**
Call `secure_pdf(operation="verify_signatures", input_path=...)`. Report how many signatures were found and whether each is valid.

## Examples

- "Encrypt report.pdf with password 'secret'" → `secure_pdf(operation="encrypt", input_path="report.pdf", output_path="report_encrypted.pdf", user_password="secret", owner_password="secret")`
- "Is this PDF encrypted?" → `secure_pdf(operation="permissions", input_path="doc.pdf")`
- "Check digital signatures" → `secure_pdf(operation="verify_signatures", input_path="signed.pdf")`
```

- [ ] **Step 2: Verify file exists and has frontmatter**

```bash
head -5 claude-code/skills/secure-pdf/SKILL.md | grep -q "^name: secure-pdf" && echo "PASS" || echo "FAIL"
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add claude-code/skills/secure-pdf/SKILL.md
git commit -m "feat: add secure-pdf skill"
```

---

### Task 9: Skill — manipulate-pdf

**Files:**
- Create: `claude-code/skills/manipulate-pdf/SKILL.md`

- [ ] **Step 1: Create the skill**

Create `claude-code/skills/manipulate-pdf/SKILL.md`:

```markdown
---
name: manipulate-pdf
description: >
  Split, merge, rotate, reorder, extract pages, overlay PDFs, add annotations,
  and manage form fields. Use when the user wants to combine PDFs, split pages,
  rotate, add sticky notes or highlights, create forms, or fill form fields.
---

# Manipulate PDF

Manipulate PDF documents using `manipulate_pdf`, `annotate_pdf`, and `manage_forms` MCP tools.

## Tool: `manipulate_pdf`

**Parameters:**
- `operation` (required): One of `"split"`, `"merge"`, `"rotate"`, `"extract_pages"`, `"reverse"`, `"overlay"`
- `input_path` (for single-file ops): Source PDF path
- `input_paths` (for merge): List of PDF paths to merge
- `output_path` (required): Destination path (directory for split, file for others)
- `degrees` (for rotate): Rotation angle (90, 180, 270)
- `page_indices` (for extract_pages): List of 0-based page indices to extract
- `overlay_path` (for overlay): Path to the overlay PDF

### Operations

- **split**: Splits PDF into individual page files in `output_path` directory
- **merge**: Combines multiple PDFs from `input_paths` into one file
- **rotate**: Rotates all pages by `degrees`
- **extract_pages**: Extracts specific pages by `page_indices`
- **reverse**: Reverses page order
- **overlay**: Overlays `overlay_path` on top of `input_path`

## Tool: `annotate_pdf`

**Parameters:**
- `input_path` (required): Source PDF
- `output_path` (required): Destination PDF
- `annotation_type` (required): `"text"` (sticky note) or `"highlight"`
- `page` (required): 0-based page index
- `x`, `y` (required): Position in PDF points (origin bottom-left)
- `contents` (optional, for text): Note contents
- `width`, `height` (optional, for highlight): Rectangle dimensions (default 100x20)

## Tool: `manage_forms`

**Parameters:**
- `operation` (required): `"create"`, `"fill"`, `"read"`, `"validate"`
- `output_path` (for create, fill): Destination path
- `input_path` (for fill, read, validate): Source PDF with form
- `fields` (for create): List of field definitions `[{"name", "type", "x", "y", "width", "height", "page"}]`
- `values` (for fill, validate): Dict of `{"field_name": "value"}` pairs

### Form operations

- **create**: Create a new PDF with form fields
- **fill**: Fill form fields and save (overlays on original)
- **read**: Read form structure by extracting text entities
- **validate**: Validate field values against required rules

## Usage patterns

**Merge PDFs:**
`manipulate_pdf(operation="merge", input_paths=["a.pdf", "b.pdf", "c.pdf"], output_path="merged.pdf")`

**Split into pages:**
`manipulate_pdf(operation="split", input_path="doc.pdf", output_path="./pages/")`

**Extract specific pages:**
`manipulate_pdf(operation="extract_pages", input_path="doc.pdf", output_path="excerpt.pdf", page_indices=[0, 2, 5])`

**Add a sticky note:**
`annotate_pdf(input_path="doc.pdf", output_path="annotated.pdf", annotation_type="text", page=0, x=100, y=700, contents="Review this section")`

**Fill a form:**
1. `manage_forms(operation="read", input_path="form.pdf")` — discover fields
2. Map user values to field names
3. `manage_forms(operation="fill", input_path="form.pdf", output_path="filled.pdf", values={"name": "John", "date": "2026-04-13"})`

## Examples

- "Merge these 3 PDFs" → `manipulate_pdf(operation="merge", ...)`
- "Rotate page 2 by 90 degrees" → `manipulate_pdf(operation="rotate", input_path=..., output_path=..., degrees=90)`
- "Extract pages 1, 3, 5" → `manipulate_pdf(operation="extract_pages", page_indices=[0, 2, 4], ...)`
- "Add a note on page 1" → `annotate_pdf(annotation_type="text", page=0, ...)`
- "Fill this tax form" → read first, then fill with values
```

- [ ] **Step 2: Verify file exists and has frontmatter**

```bash
head -5 claude-code/skills/manipulate-pdf/SKILL.md | grep -q "^name: manipulate-pdf" && echo "PASS" || echo "FAIL"
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add claude-code/skills/manipulate-pdf/SKILL.md
git commit -m "feat: add manipulate-pdf skill"
```

---

### Task 10: Agent — pdf-specialist

**Files:**
- Create: `claude-code/agents/pdf-specialist.md`

- [ ] **Step 1: Create the agent definition**

Create `claude-code/agents/pdf-specialist.md`:

```markdown
---
name: pdf-specialist
description: >
  Expert PDF document specialist that orchestrates oxidize-pdf tools for complex
  multi-step PDF workflows. Use when the task involves reading, creating, analyzing,
  manipulating, securing, or transforming PDF documents — especially when multiple
  tools need to be combined.
model: sonnet
maxTurns: 30
---

You are a PDF document specialist powered by oxidize-pdf. You have access to 12 MCP tools for comprehensive PDF manipulation.

## Available MCP tools

| Tool | Purpose |
|------|---------|
| `read_pdf` | Read metadata: page count, title, author, encryption, version |
| `extract_text` | Extract text from all pages or a specific page |
| `convert_pdf` | Convert to markdown, token chunks, or RAG-optimized chunks |
| `analyze_pdf` | Validate structure, detect corruption, check PDF/A compliance, compare two PDFs |
| `extract_entities` | Extract text chunks with position and font info per page |
| `manipulate_pdf` | Split, merge, rotate, extract pages, reverse, overlay |
| `annotate_pdf` | Add text annotations (sticky notes) or highlights |
| `manage_forms` | Create, fill, read, and validate PDF form fields |
| `secure_pdf` | Encrypt with passwords, check permissions, verify signatures |
| `create_pdf` | Start a stateful PDF creation session |
| `add_pdf_content` | Add text or new pages to a creation session |
| `save_pdf` | Save a creation session to file |

## Available resources

| Resource | Content |
|----------|---------|
| `oxidize://fonts` | List of built-in PDF fonts |
| `oxidize://page-sizes` | Standard page dimensions (A4, Letter, etc.) |
| `oxidize://capabilities` | Full server capability list |
| `oxidize://version` | oxidize-pdf and MCP server version info |
| `oxidize://workspace` | PDF files in the current workspace directory |
| `oxidize://session/{id}` | State of a PDF creation session |

## Workflow strategies

### Inspect before acting
Always call `read_pdf` first to understand the document before performing operations. Report what you find to the user.

### Stateful PDF creation
1. `create_pdf` — start session, get `session_id`
2. `add_pdf_content` — repeat for each piece of content (text, new pages)
3. `save_pdf` — finalize and write to disk

Coordinate system: origin at bottom-left, 72 points = 1 inch. A4 = 595.28 x 841.89 pt.

### Analysis pipeline
For comprehensive document audits:
1. `read_pdf` — metadata overview
2. `extract_text` — content extraction
3. `analyze_pdf` with `check="validate"` — structural integrity
4. `analyze_pdf` with `check="corruption"` — corruption detection
5. `analyze_pdf` with `check="compliance"` — PDF/A compliance
6. `extract_entities` — detailed layout analysis

### Secure pipeline
1. `read_pdf` — check current state
2. `secure_pdf` with `operation="verify_signatures"` — check existing signatures
3. `secure_pdf` with `operation="encrypt"` — apply encryption

### Batch processing
Process multiple files by iterating tools across a list of paths. Use `read_pdf` on each file first, then apply the requested operation.

## Constraints

- File paths must be accessible from the working directory
- PDF creation sessions expire after 1 hour of inactivity
- The `encrypt` operation reconstructs documents and may lose non-text elements (images, vector graphics) — always warn the user
- Always confirm before overwriting existing files
- Page indices are 0-based (page 1 = index 0)

## Behavior

- Be concise in reporting results — summarize key findings, don't dump raw JSON
- When multiple tools are needed, explain your plan before executing
- If a tool returns an error, explain what went wrong and suggest alternatives
- For complex workflows, process step by step and report progress
```

- [ ] **Step 2: Verify file exists and has correct frontmatter**

```bash
head -8 claude-code/agents/pdf-specialist.md | grep -q "^name: pdf-specialist" && echo "PASS" || echo "FAIL"
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add claude-code/agents/pdf-specialist.md
git commit -m "feat: add pdf-specialist agent"
```

---

### Task 11: Local testing with --plugin-dir

**Files:** None (testing only)

- [ ] **Step 1: Verify plugin structure is complete**

```bash
cd /home/santi/repos/BelowZero/oxidizePdf/oxidize-pdf-integrations
echo "=== Plugin structure ==="
find claude-code -type f | sort
echo ""
echo "=== Marketplace ==="
cat .claude-plugin/marketplace.json | python3 -m json.tool > /dev/null && echo "marketplace.json: valid JSON"
echo ""
echo "=== Plugin manifest ==="
cat claude-code/.claude-plugin/plugin.json | python3 -m json.tool > /dev/null && echo "plugin.json: valid JSON"
echo ""
echo "=== MCP config ==="
cat claude-code/.mcp.json | python3 -m json.tool > /dev/null && echo ".mcp.json: valid JSON"
echo ""
echo "=== Hooks ==="
cat claude-code/hooks/hooks.json | python3 -m json.tool > /dev/null && echo "hooks.json: valid JSON"
echo ""
echo "=== Script executable ==="
test -x claude-code/bin/launch-mcp && echo "launch-mcp: executable"
echo ""
echo "=== Skills ==="
for skill in claude-code/skills/*/SKILL.md; do
    name=$(grep "^name:" "$skill" | head -1 | sed 's/name: //')
    echo "  $name: $(wc -l < "$skill") lines"
done
echo ""
echo "=== Agent ==="
grep "^name:" claude-code/agents/pdf-specialist.md | head -1
```

Expected: All files present, all JSON valid, script executable, 6 skills listed, agent present.

- [ ] **Step 2: Run plugin validation**

```bash
claude plugin validate ./claude-code 2>&1 || echo "(validation command may not exist in CLI — manual testing needed)"
```

- [ ] **Step 3: Test with --plugin-dir**

```bash
claude --plugin-dir ./claude-code
```

Inside the session, verify:
1. `/help` shows skills under `oxidize-pdf:` namespace
2. `/agents` shows `oxidize-pdf:pdf-specialist`
3. Run `/oxidize-pdf:read-pdf` on a sample PDF
4. Run `claude --debug --plugin-dir ./claude-code` to verify MCP server starts

- [ ] **Step 4: Commit any fixes from testing**

```bash
git add -A
git commit -m "fix: adjustments from local plugin testing"
```

---

### Task 12: Push to GitHub and verify marketplace install

**Files:** None (deployment)

- [ ] **Step 1: Push to remote**

```bash
cd /home/santi/repos/BelowZero/oxidizePdf/oxidize-pdf-integrations
git push -u origin main
```

- [ ] **Step 2: Verify marketplace can be added**

Inside a Claude Code session:

```shell
/plugin marketplace add bzsanti/oxidize-pdf-integrations
```

Expected: Marketplace added successfully.

- [ ] **Step 3: Verify plugin can be installed**

```shell
/plugin install oxidize-pdf@oxidize-pdf
```

Expected: Plugin installed successfully.

- [ ] **Step 4: Verify installed plugin works**

```shell
/oxidize-pdf:read-pdf some-test.pdf
```

Expected: PDF metadata returned.

- [ ] **Step 5: Tag release**

```bash
git tag v1.0.0
git push origin v1.0.0
```

- [ ] **Step 6: Commit**

No additional commit needed — this task is deployment verification only.
