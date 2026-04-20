# oxidize-pdf Claude Code Plugin — Design Spec

**Date**: 2026-04-13
**Status**: Draft
**Repo**: `git@github.com-bzsanti:bzsanti/oxidize-pdf-integrations.git`

## Goal

Create a Claude Code plugin that exposes oxidize-pdf's full PDF manipulation capabilities through skills, an agent, and an MCP server. Distribute via a self-hosted marketplace (immediate) and the official Anthropic marketplace (via submission form).

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Repo structure | Monorepo `oxidize-pdf-integrations` | Future-proof for VS Code, JetBrains, etc. |
| Plugin location | `claude-code/` subdirectory | Marketplace uses `git-subdir` or relative path |
| Functionality level | Skills + Agent + MCP server | Agent is the key differentiator |
| Dependency management | Smart detection with fallback venv | Respects existing envs, zero-config for new users |
| Naming | `oxidize-pdf` | Matches PyPI package and MCP server name |
| Skills scope | All tiers (6 skills + 1 agent) in v1.0.0 | Skills are markdown-only, low incremental effort |
| Extras | No output styles or hooks beyond SessionStart | Ship clean v1.0.0, iterate from user feedback |

## Repository Structure

```
oxidize-pdf-integrations/
├── claude-code/                        # Claude Code plugin
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── skills/
│   │   ├── read-pdf/SKILL.md
│   │   ├── create-pdf/SKILL.md
│   │   ├── extract-text/SKILL.md
│   │   ├── analyze-pdf/SKILL.md
│   │   ├── secure-pdf/SKILL.md
│   │   └── manipulate-pdf/SKILL.md
│   ├── agents/
│   │   └── pdf-specialist.md
│   ├── .mcp.json
│   ├── hooks/
│   │   └── hooks.json
│   └── bin/
│       └── launch-mcp
├── .claude-plugin/
│   └── marketplace.json                # Self-hosted marketplace
├── LICENSE
├── README.md
└── CHANGELOG.md
```

## Component Specifications

### 1. Plugin Manifest (`claude-code/.claude-plugin/plugin.json`)

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

### 2. Marketplace (`/.claude-plugin/marketplace.json`)

```json
{
  "name": "oxidize-pdf",
  "owner": {
    "name": "BelowZero",
    "email": "bzsanti@users.noreply.github.com"
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

**Distribution channels**:
- Self-hosted: `/plugin marketplace add bzsanti/oxidize-pdf-integrations`
- Install: `/plugin install oxidize-pdf@oxidize-pdf`
- Official: submit via `platform.claude.com/plugins/submit` pointing to this repo

### 3. MCP Server Configuration (`claude-code/.mcp.json`)

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

This delegates to the bootstrap script which finds the correct Python environment.

### 4. Bootstrap Script (`claude-code/bin/launch-mcp`)

Bash script (~40 lines) with two modes:

**`launch-mcp check`** (called by SessionStart hook):
1. Try `python -c "import oxidize_pdf"` using current environment
2. If found: print status message, exit 0
3. If not found: check if `${OXIDIZE_PLUGIN_DATA}/venv` exists
4. If venv exists: print status message, exit 0
5. If no venv: create `${OXIDIZE_PLUGIN_DATA}/venv`, run `pip install oxidize-pdf`, exit 0
6. On any install failure: print error with manual instructions, exit 1

**`launch-mcp serve`** (called by `.mcp.json`):
1. Try `python -c "import oxidize_pdf"` using current environment
2. If found: exec `python -m oxidize_pdf.mcp`
3. If not found: activate `${OXIDIZE_PLUGIN_DATA}/venv`, exec `python -m oxidize_pdf.mcp`
4. If neither works: print error, exit 1

**Key behaviors**:
- Respects active venv or conda environment first
- Falls back to plugin-managed venv in `${CLAUDE_PLUGIN_DATA}/venv`
- Uses `python3` with fallback to `python`
- The venv persists across plugin updates (Anthropic's `${CLAUDE_PLUGIN_DATA}` contract)

### 5. Hooks (`claude-code/hooks/hooks.json`)

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

Runs at session start to verify oxidize-pdf is available, installing if needed.

### 6. Skills

Each skill is a markdown file with frontmatter. Skills guide Claude on how to use the MCP tools effectively.

#### 6.1 `read-pdf/SKILL.md`

**Description**: Read PDF metadata, page count, and basic document information.
**MCP tools used**: `read_pdf`
**When to invoke**: User wants to open, inspect, or get info about a PDF file.
**Content**:
- How to call `read_pdf` with a file path
- Available metadata fields (title, author, subject, page_count, encrypted, etc.)
- How to read specific page ranges
- Examples: "What's in this PDF?", "How many pages does report.pdf have?"

#### 6.2 `extract-text/SKILL.md`

**Description**: Extract text content from PDF documents with formatting options.
**MCP tools used**: `extract_text`, `convert_pdf`
**When to invoke**: User wants text content from a PDF, needs to search within a PDF, or wants to convert PDF to text/markdown/RAG chunks.
**Content**:
- `extract_text` for direct text extraction (with optional page range)
- `convert_pdf` for format conversions (text, markdown, rag)
- RAG chunking with configurable chunk_size
- Examples: "Extract the text from chapter 3", "Convert this PDF to markdown"

#### 6.3 `create-pdf/SKILL.md`

**Description**: Create new PDF documents from scratch with text, images, and styling.
**MCP tools used**: `create_pdf`, `add_pdf_content`, `save_pdf`
**When to invoke**: User wants to generate a new PDF, create a report, or build a document.
**Content**:
- Stateful workflow: `create_pdf` → `add_pdf_content` (repeat) → `save_pdf`
- Session management: create_pdf returns a session_id used by subsequent calls
- Available content types: text, heading, image, table
- Page size options (reference `oxidize://page-sizes` resource)
- Font options (reference `oxidize://fonts` resource)
- Examples: "Create a one-page summary PDF", "Make an invoice for Acme Corp"

#### 6.4 `analyze-pdf/SKILL.md`

**Description**: Analyze PDF structure, validate integrity, check compliance, and compare documents.
**MCP tools used**: `analyze_pdf`, `extract_entities`
**When to invoke**: User wants to validate a PDF, check for corruption, verify PDF/A compliance, compare two PDFs, or extract structured entities.
**Content**:
- Analysis modes: `validate`, `corruption`, `compliance`, `compare`
- Entity extraction: tables, images, links, annotations, bookmarks, signatures
- Comparison workflow (requires two file paths)
- Examples: "Is this PDF corrupted?", "Compare v1.pdf and v2.pdf", "Extract all tables"

#### 6.5 `secure-pdf/SKILL.md`

**Description**: Encrypt PDFs, manage permissions, and verify digital signatures.
**MCP tools used**: `secure_pdf`
**When to invoke**: User wants to password-protect a PDF, restrict permissions, or check signatures.
**Content**:
- Operations: `encrypt`, `permissions`, `verify_signatures`
- Encryption: user_password, owner_password, algorithm options
- Permissions: print, copy, modify, annotate, fill_forms
- Signature verification workflow
- Examples: "Encrypt this PDF with password 'secret'", "Can this PDF be printed?"

#### 6.6 `manipulate-pdf/SKILL.md`

**Description**: Split, merge, rotate, reorder, extract pages, and overlay PDFs.
**MCP tools used**: `manipulate_pdf`, `annotate_pdf`, `manage_forms`
**When to invoke**: User wants to combine PDFs, split pages, rotate, add annotations, or work with form fields.
**Content**:
- Page operations: `split`, `merge`, `rotate`, `extract_pages`, `reverse`, `overlay`
- Annotation types and placement
- Form operations: `create`, `fill`, `read`, `validate`
- Examples: "Merge these 3 PDFs", "Rotate page 2 by 90 degrees", "Fill this tax form"

### 7. Agent (`claude-code/agents/pdf-specialist.md`)

```yaml
---
name: pdf-specialist
description: >
  Expert PDF document specialist that orchestrates oxidize-pdf tools for complex
  multi-step PDF workflows. Use when the task involves reading, creating, analyzing,
  manipulating, securing, or transforming PDF documents.
model: sonnet
maxTurns: 30
---
```

**System prompt content**:

1. **Identity**: You are a PDF document specialist powered by oxidize-pdf. You have access to 12 MCP tools for comprehensive PDF manipulation.

2. **Available tools** (with one-line descriptions of each):
   - `read_pdf` — Read metadata and basic info
   - `extract_text` — Extract text with formatting
   - `convert_pdf` — Convert to text/markdown/RAG
   - `analyze_pdf` — Validate, check corruption, compliance, compare
   - `extract_entities` — Extract tables, images, links, annotations
   - `manipulate_pdf` — Split, merge, rotate, extract pages, overlay
   - `annotate_pdf` — Add annotations (highlight, note, link, etc.)
   - `manage_forms` — Create, fill, read, validate form fields
   - `secure_pdf` — Encrypt, permissions, verify signatures
   - `create_pdf` — Start a new PDF creation session
   - `add_pdf_content` — Add content to a creation session
   - `save_pdf` — Save a creation session to file

3. **Available resources**:
   - `oxidize://fonts` — List of built-in fonts
   - `oxidize://page-sizes` — Standard page dimensions
   - `oxidize://capabilities` — Full server capability list
   - `oxidize://version` — Version info
   - `oxidize://workspace` — PDF files in workspace
   - `oxidize://session/{id}` — Session state

4. **Workflow strategies**:
   - **Inspect before acting**: Always read_pdf first to understand the document
   - **Stateful creation**: create_pdf → add_pdf_content (N times) → save_pdf
   - **Analysis pipeline**: read_pdf → extract_text → analyze_pdf → extract_entities
   - **Secure pipeline**: read_pdf → verify_signatures → encrypt/set permissions
   - **Batch processing**: Process multiple files by iterating tools

5. **Constraints**:
   - File paths must be accessible from the server's working directory
   - Creation sessions expire after 1 hour
   - Always confirm destructive operations (overwriting existing files)

## Testing Strategy

### Manual testing with `--plugin-dir`

```bash
claude --plugin-dir ./claude-code
```

Verification checklist:
- [ ] All 6 skills appear in `/help` under `oxidize-pdf:` namespace
- [ ] Agent appears in `/agents` as `oxidize-pdf:pdf-specialist`
- [ ] MCP server starts (check with `claude --debug`)
- [ ] SessionStart hook runs and reports oxidize-pdf status
- [ ] Each skill invocation correctly triggers MCP tool calls
- [ ] Agent can orchestrate multi-step workflows
- [ ] Fallback venv installation works on clean system

### Functional tests per skill

| Skill | Test |
|-------|------|
| read-pdf | Read metadata from a sample PDF |
| extract-text | Extract text, verify content matches |
| create-pdf | Create PDF, verify it opens and has content |
| analyze-pdf | Validate a known-good and known-bad PDF |
| secure-pdf | Encrypt, then verify encryption is detected |
| manipulate-pdf | Merge two PDFs, verify page count |
| pdf-specialist | "Review this PDF and create a summary report" (multi-tool) |

## Distribution Plan

### Phase 1: Self-hosted marketplace (week 1)

1. Create repo `bzsanti/oxidize-pdf-integrations`
2. Implement all components
3. Test locally with `--plugin-dir`
4. Push to GitHub
5. Verify: `/plugin marketplace add bzsanti/oxidize-pdf-integrations`
6. Verify: `/plugin install oxidize-pdf@oxidize-pdf`

### Phase 2: Official Anthropic marketplace (week 2+)

1. Submit via `platform.claude.com/plugins/submit`
2. Provide repo URL, description, and category
3. Wait for Anthropic review
4. Once approved: `/plugin install oxidize-pdf@claude-plugins-official`

### Phase 3: Cross-platform (future)

The `oxidize-pdf-integrations` monorepo can host additional integrations:
- `vscode/` — VS Code extension (using oxidize-pdf's MCP server via VS Code MCP support)
- `jetbrains/` — JetBrains plugin
- `cursor/` — Cursor integration

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| oxidize-pdf (PyPI) | >=0.2.1 | Core PDF library |
| Python | >=3.10 | Runtime for MCP server |
| bash | any | Bootstrap script |

## File Count Summary

| Component | Files |
|-----------|-------|
| Plugin manifest | 1 |
| Marketplace manifest | 1 |
| Skills (SKILL.md) | 6 |
| Agent | 1 |
| MCP config | 1 |
| Hooks config | 1 |
| Bootstrap script | 1 |
| README | 1 |
| LICENSE | 1 |
| CHANGELOG | 1 |
| **Total** | **15** |
