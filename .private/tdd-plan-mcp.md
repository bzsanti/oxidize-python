# TDD Plan: oxidize-pdf MCP Server Module

## Contexto

Añadir un submodulo `oxidize_pdf.mcp` al proyecto oxidize-python que expone las capacidades PDF via Model Context Protocol usando FastMCP. El modulo vive en `python/oxidize_pdf/mcp/` con tests en `tests/mcp_tests/`.

**Stack detectado**: Python 3.10+, PyO3/Maturin, pytest, pytest-asyncio
**Convenciones**: imports locales en cada test, fixtures en conftest.py, clases de test agrupadas por feature, asyncio_mode="auto"
**Afecta hot path**: No — es una capa de adaptacion sobre la API existente

## Decisiones Previas Necesarias

Ninguna — arquitectura definida en el prompt.

## REGLA: No smoke tests

**NUNCA** escribir smoke tests. Todos los tests deben validar comportamiento real.
Patrones prohibidos: `assert callable()`, `assert hasattr()`, `import X; assert X is not None`, `test_*_importable`, `test_*_is_listed` (como test individual).
Hook global en `~/.claude/hooks/reject-smoke-tests.sh` bloquea estos patrones.

---

## Tier 1: Infrastructure [COMPLETADO]

> Features F-001 a F-003 eliminadas (eran smoke tests).
> Features F-004 a F-012 implementadas. 37 tests pasando.

### Feature F-004: Config module — environment-based settings [M] [DONE]
Dependencies: F-001

**RED**: Write test `tests/mcp/test_config.py`
```python
import os

def test_config_has_defaults():
    from oxidize_pdf.mcp.config import McpConfig
    cfg = McpConfig()
    assert cfg.workspace_dir is not None
    assert cfg.max_session_age_seconds > 0
    assert cfg.max_file_size_bytes > 0

def test_config_workspace_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("OXIDIZE_WORKSPACE", str(tmp_path))
    from importlib import reload
    import oxidize_pdf.mcp.config as mod
    reload(mod)
    cfg = mod.McpConfig()
    assert cfg.workspace_dir == tmp_path

def test_config_max_file_size_from_env(monkeypatch):
    monkeypatch.setenv("OXIDIZE_MAX_FILE_SIZE_MB", "50")
    from importlib import reload
    import oxidize_pdf.mcp.config as mod
    reload(mod)
    cfg = mod.McpConfig()
    assert cfg.max_file_size_bytes == 50 * 1024 * 1024

def test_config_defaults_are_sane():
    from oxidize_pdf.mcp.config import McpConfig
    cfg = McpConfig()
    assert cfg.max_session_age_seconds == 3600
    assert cfg.max_file_size_bytes == 100 * 1024 * 1024
```

**GREEN**: Create `python/oxidize_pdf/mcp/config.py` with `McpConfig` dataclass reading from environment via `os.environ.get`. Defaults: workspace=`/tmp/oxidize_workspace`, max_session_age=3600, max_file_size=100MB.

**REFACTOR**: None.

---

### Feature F-005: Security module — path validation [M] [DONE]
Dependencies: F-004

**RED**: Write test `tests/mcp/test_security.py`
```python
import pathlib
import pytest

def test_validate_safe_path_within_workspace(tmp_path):
    from oxidize_pdf.mcp.security import validate_path
    safe = tmp_path / "file.pdf"
    safe.touch()
    result = validate_path(str(safe), workspace=tmp_path)
    assert result == safe.resolve()

def test_validate_path_rejects_traversal(tmp_path):
    from oxidize_pdf.mcp.security import validate_path, SecurityError
    with pytest.raises(SecurityError, match="traversal"):
        validate_path(str(tmp_path / ".." / "etc" / "passwd"), workspace=tmp_path)

def test_validate_path_rejects_absolute_outside_workspace(tmp_path):
    from oxidize_pdf.mcp.security import validate_path, SecurityError
    with pytest.raises(SecurityError):
        validate_path("/etc/passwd", workspace=tmp_path)

def test_validate_path_rejects_nonexistent_when_must_exist(tmp_path):
    from oxidize_pdf.mcp.security import validate_path, SecurityError
    with pytest.raises(SecurityError, match="not found"):
        validate_path(str(tmp_path / "missing.pdf"), workspace=tmp_path, must_exist=True)

def test_validate_path_allows_nonexistent_output(tmp_path):
    from oxidize_pdf.mcp.security import validate_path
    out = tmp_path / "output.pdf"
    result = validate_path(str(out), workspace=tmp_path, must_exist=False)
    assert result == out.resolve()

def test_validate_path_rejects_non_pdf_extension(tmp_path):
    from oxidize_pdf.mcp.security import validate_path, SecurityError
    f = tmp_path / "evil.exe"
    f.touch()
    with pytest.raises(SecurityError, match="extension"):
        validate_path(str(f), workspace=tmp_path, allowed_extensions={".pdf"})
```

**GREEN**: Create `python/oxidize_pdf/mcp/security.py` with `SecurityError(ValueError)` and `validate_path(path, workspace, must_exist=True, allowed_extensions=None)`. Resolve both paths and check `is_relative_to`. Detect traversal via `..` in raw string before resolving.

**REFACTOR**: Extract `_check_extension` helper.

---

### Feature F-006: Security module — file size enforcement [S] [DONE]
Dependencies: F-005

**RED**: Add to `tests/mcp/test_security.py`
```python
def test_check_file_size_passes_within_limit(tmp_path):
    from oxidize_pdf.mcp.security import check_file_size, SecurityError
    f = tmp_path / "small.pdf"
    f.write_bytes(b"x" * 1024)
    check_file_size(f, max_bytes=1024 * 1024)

def test_check_file_size_rejects_oversized(tmp_path):
    from oxidize_pdf.mcp.security import check_file_size, SecurityError
    f = tmp_path / "big.pdf"
    f.write_bytes(b"x" * 200)
    with pytest.raises(SecurityError, match="too large"):
        check_file_size(f, max_bytes=100)
```

**GREEN**: Add `check_file_size(path, max_bytes)` to `security.py`.

**REFACTOR**: None.

---

### Feature F-007: Sessions module — create and retrieve [M] [DONE]
Dependencies: F-004

**RED**: Write test `tests/mcp/test_sessions.py`
```python
import pytest

def test_create_session_returns_id():
    from oxidize_pdf.mcp.sessions import SessionStore
    store = SessionStore()
    session_id = store.create({"title": "Test"})
    assert isinstance(session_id, str)
    assert len(session_id) == 36  # UUID

def test_get_session_returns_data():
    from oxidize_pdf.mcp.sessions import SessionStore
    store = SessionStore()
    sid = store.create({"title": "Test"})
    data = store.get(sid)
    assert data["title"] == "Test"

def test_get_missing_session_returns_none():
    from oxidize_pdf.mcp.sessions import SessionStore
    store = SessionStore()
    assert store.get("nonexistent-id") is None

def test_update_session():
    from oxidize_pdf.mcp.sessions import SessionStore
    store = SessionStore()
    sid = store.create({"pages": []})
    store.update(sid, {"pages": ["p1"]})
    assert store.get(sid)["pages"] == ["p1"]

def test_delete_session():
    from oxidize_pdf.mcp.sessions import SessionStore
    store = SessionStore()
    sid = store.create({})
    store.delete(sid)
    assert store.get(sid) is None
```

**GREEN**: Create `python/oxidize_pdf/mcp/sessions.py` with `SessionStore` backed by an in-memory `dict`. `create` uses `uuid4()`. `update` does a shallow merge with dict update.

**REFACTOR**: None.

---

### Feature F-008: Sessions module — expiry and list [M] [DONE]
Dependencies: F-007

**RED**: Add to `tests/mcp/test_sessions.py`
```python
import time

def test_session_expires_after_max_age():
    from oxidize_pdf.mcp.sessions import SessionStore
    store = SessionStore(max_age_seconds=0.01)
    sid = store.create({})
    time.sleep(0.05)
    store.purge_expired()
    assert store.get(sid) is None

def test_list_sessions_returns_all_active():
    from oxidize_pdf.mcp.sessions import SessionStore
    store = SessionStore()
    sid1 = store.create({"title": "A"})
    sid2 = store.create({"title": "B"})
    ids = store.list_ids()
    assert sid1 in ids
    assert sid2 in ids

def test_session_count():
    from oxidize_pdf.mcp.sessions import SessionStore
    store = SessionStore()
    store.create({})
    store.create({})
    assert store.count() == 2
```

**GREEN**: Add `max_age_seconds` param, store creation timestamp alongside data, implement `purge_expired()`, `list_ids()`, `count()`.

**REFACTOR**: None.

---

### Feature F-009: Models — input/output Pydantic models [M] [DONE]
Dependencies: F-002

**RED**: Write test `tests/mcp/test_models.py`
```python
def test_read_pdf_input_validates():
    from oxidize_pdf.mcp.models import ReadPdfInput
    inp = ReadPdfInput(path="/tmp/test.pdf")
    assert inp.path == "/tmp/test.pdf"
    assert inp.password is None

def test_read_pdf_input_with_password():
    from oxidize_pdf.mcp.models import ReadPdfInput
    inp = ReadPdfInput(path="/tmp/test.pdf", password="secret")
    assert inp.password == "secret"

def test_read_pdf_output_structure():
    from oxidize_pdf.mcp.models import ReadPdfOutput
    out = ReadPdfOutput(
        path="/tmp/test.pdf",
        page_count=3,
        is_encrypted=False,
        version="1.7",
        title=None,
        author=None,
    )
    assert out.page_count == 3
    assert out.is_encrypted is False

def test_error_output_structure():
    from oxidize_pdf.mcp.models import ErrorOutput
    err = ErrorOutput(error="file not found", code="IO_ERROR")
    assert err.error == "file not found"
    assert err.code == "IO_ERROR"

def test_session_output_structure():
    from oxidize_pdf.mcp.models import SessionOutput
    out = SessionOutput(session_id="abc-123", status="created")
    assert out.session_id == "abc-123"
```

**GREEN**: Create `python/oxidize_pdf/mcp/models.py` with Pydantic `BaseModel` subclasses: `ReadPdfInput`, `ReadPdfOutput`, `ErrorOutput`, `SessionOutput`. All fields typed, optional fields default to `None`.

**REFACTOR**: None.

---

### Feature F-010: Models — extract, convert, analyze input models [M] [DONE]
Dependencies: F-009

**RED**: Add to `tests/mcp/test_models.py`
```python
def test_extract_text_input():
    from oxidize_pdf.mcp.models import ExtractTextInput
    inp = ExtractTextInput(path="/tmp/t.pdf", page=0)
    assert inp.page == 0
    inp_all = ExtractTextInput(path="/tmp/t.pdf")
    assert inp_all.page is None

def test_convert_pdf_input():
    from oxidize_pdf.mcp.models import ConvertPdfInput
    inp = ConvertPdfInput(path="/tmp/t.pdf", format="markdown")
    assert inp.format == "markdown"

def test_analyze_pdf_input():
    from oxidize_pdf.mcp.models import AnalyzePdfInput
    inp = AnalyzePdfInput(path="/tmp/t.pdf", check="validate")
    assert inp.check == "validate"

def test_manipulate_pdf_input():
    from oxidize_pdf.mcp.models import ManipulatePdfInput
    inp = ManipulatePdfInput(
        operation="split",
        input_path="/tmp/t.pdf",
        output_path="/tmp/out",
    )
    assert inp.operation == "split"
```

**GREEN**: Add `ExtractTextInput`, `ConvertPdfInput`, `AnalyzePdfInput`, `ManipulatePdfInput` to `models.py`. Use `Literal` for constrained string fields where appropriate.

**REFACTOR**: None.

---

### Feature F-011: Models — create/add-content/save session models [M] [DONE]
Dependencies: F-009

**RED**: Add to `tests/mcp/test_models.py`
```python
def test_create_pdf_input():
    from oxidize_pdf.mcp.models import CreatePdfInput
    inp = CreatePdfInput(title="My Doc")
    assert inp.title == "My Doc"
    assert inp.author is None
    assert inp.page_size == "a4"

def test_add_content_input():
    from oxidize_pdf.mcp.models import AddContentInput
    inp = AddContentInput(
        session_id="abc",
        content_type="text",
        content="Hello World",
        x=100.0,
        y=700.0,
    )
    assert inp.content_type == "text"

def test_save_pdf_input():
    from oxidize_pdf.mcp.models import SavePdfInput
    inp = SavePdfInput(session_id="abc", output_path="/tmp/out.pdf")
    assert inp.session_id == "abc"
```

**GREEN**: Add `CreatePdfInput`, `AddContentInput`, `SavePdfInput` to `models.py`.

**REFACTOR**: None.

---

### Feature F-012: conftest — MCP fixtures [M] [DONE]
Dependencies: F-001, F-007, F-003

**RED**: Write test `tests/mcp/test_fixtures.py`
```python
import pytest

async def test_mcp_client_fixture(mcp_client):
    tools = await mcp_client.list_tools()
    assert isinstance(tools, list)

async def test_mcp_workspace_fixture(mcp_workspace):
    assert mcp_workspace.exists()
    assert mcp_workspace.is_dir()

async def test_sample_pdf_fixture(sample_pdf):
    assert sample_pdf.exists()
    assert sample_pdf.suffix == ".pdf"
    data = sample_pdf.read_bytes()
    assert data[:5] == b"%PDF-"
```

**GREEN**: Create `tests/mcp/conftest.py` with:
- `mcp_workspace` fixture: `tmp_path` subdir
- `sample_pdf` fixture: creates a minimal PDF using `Document`/`Page`/`save`
- `mcp_client` async fixture: `async with Client(mcp) as client: yield client`

**REFACTOR**: None.

---

## Tier 2: Stateless Tools — Read & Extract

### Feature F-013: tool `read_pdf` — basic metadata [M]
Dependencies: F-012, F-005, F-009

**RED**: Write test `tests/mcp/test_tool_read_pdf.py`
```python
import pytest

async def test_read_pdf_returns_metadata(mcp_client, sample_pdf):
    result = await mcp_client.call_tool(
        "read_pdf", {"path": str(sample_pdf)}
    )
    data = result[0].text if hasattr(result[0], "text") else result
    import json
    out = json.loads(data) if isinstance(data, str) else data
    assert out["page_count"] >= 1
    assert "is_encrypted" in out
    assert "version" in out

async def test_read_pdf_missing_file_returns_error(mcp_client, mcp_workspace):
    result = await mcp_client.call_tool(
        "read_pdf", {"path": str(mcp_workspace / "nonexistent.pdf")}
    )
    import json
    out = json.loads(result[0].text)
    assert "error" in out
```

**GREEN**: Implement `read_pdf` tool in `python/oxidize_pdf/mcp/tools/read_pdf.py`. Register on `server.mcp`. Use `PdfReader.open(path)`, return dict with `path`, `page_count`, `is_encrypted`, `version`, `title`, `author`. Catch all exceptions, return `ErrorOutput` dict. Import and register from `server.py`.

**REFACTOR**: None.

---

### Feature F-014: tool `read_pdf` — encrypted PDF with password [M]
Dependencies: F-013

**RED**: Add to `tests/mcp/test_tool_read_pdf.py`
```python
async def test_read_pdf_encrypted_without_password(mcp_client, encrypted_pdf):
    result = await mcp_client.call_tool(
        "read_pdf", {"path": str(encrypted_pdf)}
    )
    import json
    out = json.loads(result[0].text)
    assert out.get("is_encrypted") is True

async def test_read_pdf_encrypted_with_correct_password(mcp_client, encrypted_pdf):
    result = await mcp_client.call_tool(
        "read_pdf", {"path": str(encrypted_pdf), "password": "userpass"}
    )
    import json
    out = json.loads(result[0].text)
    assert out.get("page_count", 0) >= 1
    assert "error" not in out
```

**GREEN**: Add `encrypted_pdf` fixture to `tests/mcp/conftest.py` creating a PDF encrypted with `doc.encrypt("userpass", "ownerpass")`. In `read_pdf` tool: if `password` provided, call `reader.unlock(password)` before reading metadata.

**REFACTOR**: None.

---

### Feature F-015: tool `read_pdf` — path security enforcement [S]
Dependencies: F-013, F-005

**RED**: Add to `tests/mcp/test_tool_read_pdf.py`
```python
async def test_read_pdf_rejects_path_outside_workspace(mcp_client):
    result = await mcp_client.call_tool(
        "read_pdf", {"path": "/etc/passwd"}
    )
    import json
    out = json.loads(result[0].text)
    assert "error" in out
    assert out.get("code") == "SECURITY_ERROR"
```

**GREEN**: Wrap `validate_path` call at top of `read_pdf` tool. Catch `SecurityError`, return `{"error": ..., "code": "SECURITY_ERROR"}`.

**REFACTOR**: Extract `_safe_open_reader(path, workspace, password)` helper in `tools/read_pdf.py`.

---

### Feature F-016: tool `extract_text` — all pages [M]
Dependencies: F-012, F-005

**RED**: Write test `tests/mcp/test_tool_extract_text.py`
```python
async def test_extract_text_all_pages(mcp_client, sample_pdf_with_text):
    result = await mcp_client.call_tool(
        "extract_text", {"path": str(sample_pdf_with_text)}
    )
    import json
    out = json.loads(result[0].text)
    assert "text" in out
    assert "Hello" in out["text"]

```

**GREEN**: Create `tools/extract_text.py`. Add `sample_pdf_with_text` fixture to conftest (PDF with `page.text_at(100, 700, "Hello")`). Implement `extract_text` using `PdfReader.open(path).extract_text()`. Return `{"text": ..., "page_count": ...}`.

**REFACTOR**: None.

---

### Feature F-017: tool `extract_text` — single page [S]
Dependencies: F-016

**RED**: Add to `tests/mcp/test_tool_extract_text.py`
```python
async def test_extract_text_single_page(mcp_client, sample_pdf_with_text):
    result = await mcp_client.call_tool(
        "extract_text", {"path": str(sample_pdf_with_text), "page": 0}
    )
    import json
    out = json.loads(result[0].text)
    assert "text" in out
    assert out.get("page") == 0

async def test_extract_text_invalid_page_returns_error(mcp_client, sample_pdf_with_text):
    result = await mcp_client.call_tool(
        "extract_text", {"path": str(sample_pdf_with_text), "page": 999}
    )
    import json
    out = json.loads(result[0].text)
    assert "error" in out
```

**GREEN**: Add `page: int | None = None` param to `extract_text`. If page provided, use `reader.extract_text_from_page(page)`. Catch `IndexError`/`PdfError`, return error dict.

**REFACTOR**: None.

---

### Feature F-018: tool `extract_text` — security enforcement [S]
Dependencies: F-016, F-005

**RED**: Add to `tests/mcp/test_tool_extract_text.py`
```python
async def test_extract_text_rejects_unsafe_path(mcp_client):
    result = await mcp_client.call_tool(
        "extract_text", {"path": "/etc/shadow"}
    )
    import json
    out = json.loads(result[0].text)
    assert "error" in out
    assert out.get("code") == "SECURITY_ERROR"
```

**GREEN**: Add `validate_path` call at top of `extract_text` tool.

**REFACTOR**: None.

---

### Feature F-019: tool `convert_pdf` — to markdown [M]
Dependencies: F-012, F-005

**RED**: Write test `tests/mcp/test_tool_convert_pdf.py`
```python
async def test_convert_to_markdown(mcp_client, sample_pdf_with_text):
    result = await mcp_client.call_tool(
        "convert_pdf", {"path": str(sample_pdf_with_text), "format": "markdown"}
    )
    import json
    out = json.loads(result[0].text)
    assert "content" in out
    assert out.get("format") == "markdown"
    assert isinstance(out["content"], str)

```

**GREEN**: Create `tools/convert_pdf.py`. Implement `convert_pdf` with `format: str` param. For `"markdown"`: use `MarkdownExporter.default().export(reader.extract_text())`. Return `{"content": ..., "format": "markdown"}`.

**REFACTOR**: None.

---

### Feature F-020: tool `convert_pdf` — to chunks [M]
Dependencies: F-019

**RED**: Add to `tests/mcp/test_tool_convert_pdf.py`
```python
async def test_convert_to_chunks(mcp_client, sample_pdf_with_text):
    result = await mcp_client.call_tool(
        "convert_pdf",
        {"path": str(sample_pdf_with_text), "format": "chunks", "max_tokens": 100},
    )
    import json
    out = json.loads(result[0].text)
    assert "chunks" in out
    assert isinstance(out["chunks"], list)

async def test_convert_to_rag(mcp_client, sample_pdf_with_text):
    result = await mcp_client.call_tool(
        "convert_pdf",
        {"path": str(sample_pdf_with_text), "format": "rag"},
    )
    import json
    out = json.loads(result[0].text)
    assert "chunks" in out

async def test_convert_invalid_format_returns_error(mcp_client, sample_pdf_with_text):
    result = await mcp_client.call_tool(
        "convert_pdf", {"path": str(sample_pdf_with_text), "format": "invalid"}
    )
    import json
    out = json.loads(result[0].text)
    assert "error" in out
```

**GREEN**: Add `format=="chunks"` branch using `DocumentChunker(max_tokens, overlap).chunk_text(text)`. Add `format=="rag"` branch using `reader.rag_chunks()`. Return `{"chunks": [c.text for c in chunks], "format": ...}`.

**REFACTOR**: Extract `_dispatch_format(reader, fmt, params)` dict dispatch.

---

## Tier 3: Stateless Tools — Analyze, Entities, Manipulate

### Feature F-021: tool `analyze_pdf` — validate [M]
Dependencies: F-012, F-005

**RED**: Write test `tests/mcp/test_tool_analyze_pdf.py`
```python
async def test_analyze_validate(mcp_client, sample_pdf):
    result = await mcp_client.call_tool(
        "analyze_pdf", {"path": str(sample_pdf), "check": "validate"}
    )
    import json
    out = json.loads(result[0].text)
    assert "valid" in out
    assert isinstance(out["valid"], bool)

```

**GREEN**: Create `tools/analyze_pdf.py`. For `check=="validate"`: use `validate_pdf(path)`. Return `{"valid": True/False, "check": "validate"}`.

**REFACTOR**: None.

---

### Feature F-022: tool `analyze_pdf` — detect corruption [M]
Dependencies: F-021

**RED**: Add to `tests/mcp/test_tool_analyze_pdf.py`
```python
async def test_analyze_detect_corruption(mcp_client, sample_pdf):
    result = await mcp_client.call_tool(
        "analyze_pdf", {"path": str(sample_pdf), "check": "corruption"}
    )
    import json
    out = json.loads(result[0].text)
    assert "corrupted" in out
    assert out["corrupted"] is False

async def test_analyze_pdf_compliance(mcp_client, sample_pdf):
    result = await mcp_client.call_tool(
        "analyze_pdf", {"path": str(sample_pdf), "check": "compliance"}
    )
    import json
    out = json.loads(result[0].text)
    assert "check" in out
    assert out["check"] == "compliance"
```

**GREEN**: Add `check=="corruption"` using `detect_pdf_corruption(path)`. Add `check=="compliance"` using `ComplianceSystem`. Return structured dicts.

**REFACTOR**: None.

---

### Feature F-023: tool `analyze_pdf` — compare two PDFs [M]
Dependencies: F-021

**RED**: Add to `tests/mcp/test_tool_analyze_pdf.py`
```python
async def test_analyze_compare_pdfs(mcp_client, sample_pdf, sample_pdf_copy):
    result = await mcp_client.call_tool(
        "analyze_pdf",
        {
            "path": str(sample_pdf),
            "check": "compare",
            "compare_path": str(sample_pdf_copy),
        },
    )
    import json
    out = json.loads(result[0].text)
    assert "identical" in out or "differences" in out

async def test_analyze_compare_missing_compare_path_returns_error(
    mcp_client, sample_pdf
):
    result = await mcp_client.call_tool(
        "analyze_pdf", {"path": str(sample_pdf), "check": "compare"}
    )
    import json
    out = json.loads(result[0].text)
    assert "error" in out
```

**GREEN**: Add `compare_path: str | None = None` param. For `check=="compare"`: require `compare_path`, use `compare_pdfs(path, compare_path)`. Return `{"identical": ..., "differences": [...]}`. Add `sample_pdf_copy` fixture to conftest.

**REFACTOR**: None.

---

### Feature F-024: tool `extract_entities` [M]
Dependencies: F-012, F-005

**RED**: Write test `tests/mcp/test_tool_extract_entities.py`
```python
async def test_extract_entities_returns_list(mcp_client, sample_pdf_with_text):
    result = await mcp_client.call_tool(
        "extract_entities", {"path": str(sample_pdf_with_text)}
    )
    import json
    out = json.loads(result[0].text)
    assert "entities" in out
    assert isinstance(out["entities"], list)

async def test_extract_entities_rejects_unsafe_path(mcp_client):
    result = await mcp_client.call_tool(
        "extract_entities", {"path": "/etc/passwd"}
    )
    import json
    out = json.loads(result[0].text)
    assert out.get("code") == "SECURITY_ERROR"
```

**GREEN**: Create `tools/extract_entities.py`. Use `PdfReader.open(path)`, extract text, use `EntityMap` / `GraphicsExtractor` if applicable. Return `{"entities": [...], "page_count": N}`. For now, return empty list if no entities — real impl uses `SemanticEntity`.

**REFACTOR**: None.

---

### Feature F-025: tool `manipulate_pdf` — split [M]
Dependencies: F-012, F-005

**RED**: Write test `tests/mcp/test_tool_manipulate_pdf.py`
```python
import pathlib

async def test_manipulate_split(mcp_client, sample_pdf, mcp_workspace):
    out_dir = mcp_workspace / "split_out"
    out_dir.mkdir()
    result = await mcp_client.call_tool(
        "manipulate_pdf",
        {
            "operation": "split",
            "input_path": str(sample_pdf),
            "output_path": str(out_dir),
        },
    )
    import json
    out = json.loads(result[0].text)
    assert out.get("status") == "ok"
    assert out.get("operation") == "split"

```

**GREEN**: Create `tools/manipulate_pdf.py`. For `operation=="split"`: call `split_pdf(input_path, output_path)`. Return `{"status": "ok", "operation": "split"}`. Validate both paths.

**REFACTOR**: None.

---

### Feature F-026: tool `manipulate_pdf` — merge [M]
Dependencies: F-025

**RED**: Add to `tests/mcp/test_tool_manipulate_pdf.py`
```python
async def test_manipulate_merge(mcp_client, sample_pdf, sample_pdf_copy, mcp_workspace):
    out = mcp_workspace / "merged.pdf"
    result = await mcp_client.call_tool(
        "manipulate_pdf",
        {
            "operation": "merge",
            "input_paths": [str(sample_pdf), str(sample_pdf_copy)],
            "output_path": str(out),
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"
    assert out.exists()
```

**GREEN**: Add `input_paths: list[str] | None = None` to tool params. For `operation=="merge"`: call `merge_pdfs(input_paths, output_path)`.

**REFACTOR**: None.

---

### Feature F-027: tool `manipulate_pdf` — rotate, extract, reorder [M]
Dependencies: F-025

**RED**: Add to `tests/mcp/test_tool_manipulate_pdf.py`
```python
async def test_manipulate_rotate(mcp_client, sample_pdf, mcp_workspace):
    out = mcp_workspace / "rotated.pdf"
    result = await mcp_client.call_tool(
        "manipulate_pdf",
        {
            "operation": "rotate",
            "input_path": str(sample_pdf),
            "output_path": str(out),
            "degrees": 90,
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"

async def test_manipulate_extract_pages(mcp_client, two_page_pdf, mcp_workspace):
    out = mcp_workspace / "extracted.pdf"
    result = await mcp_client.call_tool(
        "manipulate_pdf",
        {
            "operation": "extract_pages",
            "input_path": str(two_page_pdf),
            "output_path": str(out),
            "page_indices": [0],
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"

async def test_manipulate_invalid_operation(mcp_client, sample_pdf, mcp_workspace):
    result = await mcp_client.call_tool(
        "manipulate_pdf",
        {
            "operation": "vaporize",
            "input_path": str(sample_pdf),
            "output_path": str(mcp_workspace / "x.pdf"),
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert "error" in resp
```

**GREEN**: Add `degrees`, `page_indices` optional params. Dispatch to `rotate_pdf`, `extract_pages`. Add `two_page_pdf` fixture to conftest. For unknown operation: return error dict.

**REFACTOR**: Extract `_dispatch_operation(op, params)` dict.

---

### Feature F-028: tool `manipulate_pdf` — overlay and reverse [S]
Dependencies: F-027

**RED**: Add to `tests/mcp/test_tool_manipulate_pdf.py`
```python
async def test_manipulate_reverse(mcp_client, two_page_pdf, mcp_workspace):
    out = mcp_workspace / "reversed.pdf"
    result = await mcp_client.call_tool(
        "manipulate_pdf",
        {
            "operation": "reverse",
            "input_path": str(two_page_pdf),
            "output_path": str(out),
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"
```

**GREEN**: Add `operation=="reverse"` using `reverse_pdf_pages`. Add `operation=="overlay"` using `overlay_pdf` with `overlay_path` param.

**REFACTOR**: None.

---

## Tier 4: Stateless Tools — Annotate, Forms, Secure

### Feature F-029: tool `annotate_pdf` — add text annotation [M]
Dependencies: F-012, F-005

**RED**: Write test `tests/mcp/test_tool_annotate_pdf.py`
```python
async def test_annotate_add_text(mcp_client, sample_pdf, mcp_workspace):
    out = mcp_workspace / "annotated.pdf"
    result = await mcp_client.call_tool(
        "annotate_pdf",
        {
            "input_path": str(sample_pdf),
            "output_path": str(out),
            "annotation_type": "text",
            "page": 0,
            "x": 100.0,
            "y": 700.0,
            "contents": "Review this section",
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"
    assert out.exists()
    data = out.read_bytes()
    assert data[:5] == b"%PDF-"

```

**GREEN**: Create `tools/annotate_pdf.py`. Use `PdfReader.open(input_path)`, get page, add `Annotation(AnnotationType.Text, Rectangle(...)).with_contents(contents)`, save. Return `{"status": "ok"}`.

**REFACTOR**: None.

---

### Feature F-030: tool `annotate_pdf` — highlight annotation [S]
Dependencies: F-029

**RED**: Add to `tests/mcp/test_tool_annotate_pdf.py`
```python
async def test_annotate_highlight(mcp_client, sample_pdf, mcp_workspace):
    out = mcp_workspace / "highlighted.pdf"
    result = await mcp_client.call_tool(
        "annotate_pdf",
        {
            "input_path": str(sample_pdf),
            "output_path": str(out),
            "annotation_type": "highlight",
            "page": 0,
            "x": 100.0,
            "y": 700.0,
            "width": 200.0,
            "height": 20.0,
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"
```

**GREEN**: Add `annotation_type=="highlight"` branch using `AnnotationType.Highlight`. Add `width`, `height` optional params to build `Rectangle`.

**REFACTOR**: Extract `_build_rect(x, y, width, height)` helper.

---

### Feature F-031: tool `annotate_pdf` — security enforcement [S]
Dependencies: F-029, F-005

**RED**: Add to `tests/mcp/test_tool_annotate_pdf.py`
```python
async def test_annotate_rejects_unsafe_input(mcp_client, mcp_workspace):
    result = await mcp_client.call_tool(
        "annotate_pdf",
        {
            "input_path": "/etc/passwd",
            "output_path": str(mcp_workspace / "out.pdf"),
            "annotation_type": "text",
            "page": 0,
            "x": 0.0,
            "y": 0.0,
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert resp.get("code") == "SECURITY_ERROR"
```

**GREEN**: Add `validate_path` for both `input_path` and `output_path` at top of `annotate_pdf` tool.

**REFACTOR**: None.

---

### Feature F-032: tool `manage_forms` — create form field [M]
Dependencies: F-012, F-005

**RED**: Write test `tests/mcp/test_tool_manage_forms.py`
```python
async def test_manage_forms_create_text_field(mcp_client, mcp_workspace):
    out = mcp_workspace / "form.pdf"
    result = await mcp_client.call_tool(
        "manage_forms",
        {
            "operation": "create",
            "output_path": str(out),
            "fields": [
                {"type": "text", "name": "first_name", "x": 100.0, "y": 700.0, "width": 200.0, "height": 30.0}
            ],
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"
    assert out.exists()

```

**GREEN**: Create `tools/manage_forms.py`. For `operation=="create"`: build `Document`, `enable_forms()`, add `TextField` for each field descriptor, save. Return `{"status": "ok", "fields_created": N}`.

**REFACTOR**: None.

---

### Feature F-033: tool `manage_forms` — fill form [M]
Dependencies: F-032

**RED**: Add to `tests/mcp/test_tool_manage_forms.py`
```python
async def test_manage_forms_fill(mcp_client, form_pdf, mcp_workspace):
    out = mcp_workspace / "filled.pdf"
    result = await mcp_client.call_tool(
        "manage_forms",
        {
            "operation": "fill",
            "input_path": str(form_pdf),
            "output_path": str(out),
            "values": {"first_name": "Alice"},
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"
```

**GREEN**: Add `form_pdf` fixture to conftest (PDF with a text field). Add `operation=="fill"` branch using `FormManager` or direct field manipulation. Add `values: dict | None` param.

**REFACTOR**: None.

---

### Feature F-034: tool `manage_forms` — read and validate [M]
Dependencies: F-032

**RED**: Add to `tests/mcp/test_tool_manage_forms.py`
```python
async def test_manage_forms_read(mcp_client, form_pdf):
    result = await mcp_client.call_tool(
        "manage_forms",
        {"operation": "read", "input_path": str(form_pdf)},
    )
    import json
    resp = json.loads(result[0].text)
    assert "fields" in resp

async def test_manage_forms_validate(mcp_client, form_pdf):
    result = await mcp_client.call_tool(
        "manage_forms",
        {
            "operation": "validate",
            "input_path": str(form_pdf),
            "values": {"first_name": "Bob"},
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert "valid" in resp
```

**GREEN**: Add `operation=="read"` returning field names/types from `FormManager`. Add `operation=="validate"` using `FormValidationSystem`. Return structured dicts.

**REFACTOR**: None.

---

### Feature F-035: tool `secure_pdf` — encrypt [M]
Dependencies: F-012, F-005

**RED**: Write test `tests/mcp/test_tool_secure_pdf.py`
```python
async def test_secure_pdf_encrypt(mcp_client, sample_pdf, mcp_workspace):
    out = mcp_workspace / "secure.pdf"
    result = await mcp_client.call_tool(
        "secure_pdf",
        {
            "operation": "encrypt",
            "input_path": str(sample_pdf),
            "output_path": str(out),
            "user_password": "user123",
            "owner_password": "owner123",
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"
    assert out.exists()
    reader = __import__("oxidize_pdf").PdfReader.open(str(out))
    assert reader.is_encrypted

```

**GREEN**: Create `tools/secure_pdf.py`. For `operation=="encrypt"`: read input bytes via `PdfReader`, build `Document` and call `doc.encrypt(user_password, owner_password)`, save to output. Or copy-encrypt pattern: read source PDF, re-save with encryption. Return `{"status": "ok"}`.

**REFACTOR**: None.

---

### Feature F-036: tool `secure_pdf` — verify signatures and check permissions [M]
Dependencies: F-035

**RED**: Add to `tests/mcp/test_tool_secure_pdf.py`
```python
async def test_secure_pdf_check_permissions(mcp_client, encrypted_pdf):
    result = await mcp_client.call_tool(
        "secure_pdf",
        {
            "operation": "permissions",
            "input_path": str(encrypted_pdf),
            "password": "userpass",
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert "permissions" in resp

async def test_secure_pdf_verify_signatures(mcp_client, sample_pdf):
    result = await mcp_client.call_tool(
        "secure_pdf",
        {"operation": "verify_signatures", "input_path": str(sample_pdf)},
    )
    import json
    resp = json.loads(result[0].text)
    assert "signatures" in resp
```

**GREEN**: Add `operation=="permissions"` using `reader.unlock(password)` then inspect permissions. Add `operation=="verify_signatures"` using `verify_pdf_signatures(path)`. Return structured dicts.

**REFACTOR**: Extract `_dispatch_secure_operation` dict.

---

## Tier 5: Stateful Tools — Session-Based PDF Creation

### Feature F-037: tool `create_pdf` — start session [M]
Dependencies: F-007, F-012, F-009

**RED**: Write test `tests/mcp/test_tool_create_pdf.py`
```python
async def test_create_pdf_returns_session_id(mcp_client):
    result = await mcp_client.call_tool(
        "create_pdf", {"title": "My Document"}
    )
    import json
    resp = json.loads(result[0].text)
    assert "session_id" in resp
    assert isinstance(resp["session_id"], str)
    assert resp.get("status") == "created"

async def test_create_pdf_with_metadata(mcp_client):
    result = await mcp_client.call_tool(
        "create_pdf",
        {"title": "Report", "author": "Alice", "page_size": "letter"},
    )
    import json
    resp = json.loads(result[0].text)
    assert "session_id" in resp

async def test_create_pdf_tool_is_listed(mcp_client):
    tools = await mcp_client.list_tools()
    names = [t.name for t in tools]
    assert "create_pdf" in names
```

**GREEN**: Create `tools/create_pdf.py`. Use `ctx.state` via `Context` for session management. Create entry in `sessions` dict with `{"title": ..., "author": ..., "page_size": ..., "pages": [], "created_at": ...}`. Return `{"session_id": ..., "status": "created"}`.

**REFACTOR**: None.

---

### Feature F-038: tool `create_pdf` — session persists across calls [M]
Dependencies: F-037

**RED**: Add to `tests/mcp/test_tool_create_pdf.py`
```python
async def test_create_pdf_session_is_retrievable(mcp_client):
    create_result = await mcp_client.call_tool(
        "create_pdf", {"title": "Persistent Doc"}
    )
    import json
    create_resp = json.loads(create_result[0].text)
    sid = create_resp["session_id"]

    # Verify session is listed in resource
    resource = await mcp_client.read_resource(f"oxidize://session/{sid}")
    assert resource is not None
```

**GREEN**: Implement `oxidize://session/{id}` resource (stub — full resource in Tier 6). Reads from `ctx.state["sessions"]`.

**REFACTOR**: None.

---

### Feature F-039: tool `add_pdf_content` — add text block [M]
Dependencies: F-037, F-012

**RED**: Write test `tests/mcp/test_tool_add_content.py`
```python
async def test_add_text_content(mcp_client):
    create = await mcp_client.call_tool("create_pdf", {"title": "Doc"})
    import json
    sid = json.loads(create[0].text)["session_id"]

    result = await mcp_client.call_tool(
        "add_pdf_content",
        {
            "session_id": sid,
            "content_type": "text",
            "content": "Hello World",
            "x": 100.0,
            "y": 700.0,
        },
    )
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"
    assert resp.get("session_id") == sid

async def test_add_content_tool_is_listed(mcp_client):
    tools = await mcp_client.list_tools()
    names = [t.name for t in tools]
    assert "add_pdf_content" in names
```

**GREEN**: Create `tools/add_pdf_content.py`. Retrieve session from `ctx.state["sessions"][session_id]`. Append content descriptor `{"type": "text", "content": ..., "x": ..., "y": ...}` to `session["pages"][current_page]`. Return `{"status": "ok", "session_id": ...}`.

**REFACTOR**: None.

---

### Feature F-040: tool `add_pdf_content` — new page [S]
Dependencies: F-039

**RED**: Add to `tests/mcp/test_tool_add_content.py`
```python
async def test_add_new_page(mcp_client):
    create = await mcp_client.call_tool("create_pdf", {"title": "Doc"})
    import json
    sid = json.loads(create[0].text)["session_id"]

    result = await mcp_client.call_tool(
        "add_pdf_content",
        {"session_id": sid, "content_type": "new_page"},
    )
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"
    assert resp.get("page_count", 0) >= 1

async def test_add_content_missing_session_returns_error(mcp_client):
    result = await mcp_client.call_tool(
        "add_pdf_content",
        {"session_id": "nonexistent", "content_type": "new_page"},
    )
    import json
    resp = json.loads(result[0].text)
    assert "error" in resp
```

**GREEN**: For `content_type=="new_page"`: append empty page descriptor to `session["pages"]`, increment page counter. For missing session: return `{"error": "session not found", "code": "SESSION_NOT_FOUND"}`.

**REFACTOR**: None.

---

### Feature F-041: tool `save_pdf` — finalize session to file [L]
Dependencies: F-039, F-012, F-005

**RED**: Write test `tests/mcp/test_tool_save_pdf.py`
```python
async def test_save_pdf_creates_file(mcp_client, mcp_workspace):
    import json
    create = await mcp_client.call_tool("create_pdf", {"title": "Saved Doc"})
    sid = json.loads(create[0].text)["session_id"]

    await mcp_client.call_tool(
        "add_pdf_content",
        {"session_id": sid, "content_type": "text", "content": "Page 1", "x": 100.0, "y": 700.0},
    )

    out = mcp_workspace / "saved.pdf"
    result = await mcp_client.call_tool(
        "save_pdf",
        {"session_id": sid, "output_path": str(out)},
    )
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"
    assert out.exists()
    assert out.read_bytes()[:5] == b"%PDF-"

async def test_save_pdf_tool_is_listed(mcp_client):
    tools = await mcp_client.list_tools()
    names = [t.name for t in tools]
    assert "save_pdf" in names
```

**GREEN**: Create `tools/save_pdf.py`. Retrieve session, reconstruct `Document`/`Page` from stored descriptors, call `doc.save(output_path)`. Return `{"status": "ok", "path": ..., "page_count": N}`.

**REFACTOR**: Extract `_build_document_from_session(session)` into `sessions.py` or a builder helper.

---

### Feature F-042: tool `save_pdf` — cleanup session after save [S]
Dependencies: F-041

**RED**: Add to `tests/mcp/test_tool_save_pdf.py`
```python
async def test_save_pdf_cleans_up_session(mcp_client, mcp_workspace):
    import json
    create = await mcp_client.call_tool("create_pdf", {"title": "Temp"})
    sid = json.loads(create[0].text)["session_id"]
    out = mcp_workspace / "cleaned.pdf"
    await mcp_client.call_tool("save_pdf", {"session_id": sid, "output_path": str(out)})
    resource = await mcp_client.read_resource(f"oxidize://session/{sid}")
    import json as j
    data = j.loads(resource.contents[0].text) if hasattr(resource, "contents") else None
    assert data is None or data.get("status") == "completed"

async def test_save_pdf_missing_session_returns_error(mcp_client, mcp_workspace):
    import json
    result = await mcp_client.call_tool(
        "save_pdf",
        {"session_id": "ghost", "output_path": str(mcp_workspace / "x.pdf")},
    )
    resp = json.loads(result[0].text)
    assert "error" in resp
```

**GREEN**: After successful save, mark session as `"status": "completed"` or delete from state. Handle missing session with error return.

**REFACTOR**: None.

---

## Tier 6: Resources

### Feature F-043: resource `oxidize://fonts` [S]
Dependencies: F-001

**RED**: Write test `tests/mcp/test_resources.py`
```python
async def test_resource_fonts_listed(mcp_client):
    resources = await mcp_client.list_resources()
    uris = [str(r.uri) for r in resources]
    assert "oxidize://fonts" in uris

async def test_resource_fonts_content(mcp_client):
    resource = await mcp_client.read_resource("oxidize://fonts")
    content = resource.contents[0].text
    import json
    data = json.loads(content)
    assert isinstance(data, list)
    assert len(data) > 0
    assert any("Helvetica" in f for f in data)
```

**GREEN**: Create `python/oxidize_pdf/mcp/resources.py`. Register `@mcp.resource("oxidize://fonts")` returning JSON list of `Font` enum values: `["Helvetica", "Times-Roman", "Courier", ...]`.

**REFACTOR**: None.

---

### Feature F-044: resource `oxidize://page-sizes` [S]
Dependencies: F-043

**RED**: Add to `tests/mcp/test_resources.py`
```python
async def test_resource_page_sizes_listed(mcp_client):
    resources = await mcp_client.list_resources()
    uris = [str(r.uri) for r in resources]
    assert "oxidize://page-sizes" in uris

async def test_resource_page_sizes_content(mcp_client):
    resource = await mcp_client.read_resource("oxidize://page-sizes")
    import json
    data = json.loads(resource.contents[0].text)
    assert "a4" in data
    assert "letter" in data
    assert isinstance(data["a4"]["width"], (int, float))
```

**GREEN**: Add `@mcp.resource("oxidize://page-sizes")` returning dict `{"a4": {"width": 595, "height": 842}, "letter": {"width": 612, "height": 792}, "legal": {...}}`.

**REFACTOR**: None.

---

### Feature F-045: resource `oxidize://capabilities` [S]
Dependencies: F-043

**RED**: Add to `tests/mcp/test_resources.py`
```python
async def test_resource_capabilities_content(mcp_client):
    resource = await mcp_client.read_resource("oxidize://capabilities")
    import json
    data = json.loads(resource.contents[0].text)
    assert "tools" in data
    assert "read_pdf" in data["tools"]
    assert "version" in data
```

**GREEN**: Add `@mcp.resource("oxidize://capabilities")` returning dict with `tools` list (all 12 tool names), `version`, `features`.

**REFACTOR**: None.

---

### Feature F-046: resource `oxidize://version` [S]
Dependencies: F-043

**RED**: Add to `tests/mcp/test_resources.py`
```python
async def test_resource_version_content(mcp_client):
    resource = await mcp_client.read_resource("oxidize://version")
    import json
    data = json.loads(resource.contents[0].text)
    assert "oxidize_pdf" in data
    assert "mcp_server" in data
    assert isinstance(data["oxidize_pdf"], str)
```

**GREEN**: Add `@mcp.resource("oxidize://version")` returning `{"oxidize_pdf": __version__, "mcp_server": "1.0.0", "fastmcp": fastmcp.__version__}`.

**REFACTOR**: None.

---

### Feature F-047: resource `oxidize://workspace` [M]
Dependencies: F-043, F-004

**RED**: Add to `tests/mcp/test_resources.py`
```python
async def test_resource_workspace_content(mcp_client, sample_pdf):
    resource = await mcp_client.read_resource("oxidize://workspace")
    import json
    data = json.loads(resource.contents[0].text)
    assert "files" in data
    assert "workspace_dir" in data
    assert isinstance(data["files"], list)
```

**GREEN**: Add `@mcp.resource("oxidize://workspace")`. List PDF files in `McpConfig().workspace_dir`. Return `{"workspace_dir": str(dir), "files": [{"name": ..., "size": ...}]}`. If dir doesn't exist or is empty, return empty list.

**REFACTOR**: None.

---

### Feature F-048: resource `oxidize://session/{id}` [M]
Dependencies: F-037, F-043

**RED**: Add to `tests/mcp/test_resources.py`
```python
async def test_resource_session_valid(mcp_client):
    import json
    create = await mcp_client.call_tool("create_pdf", {"title": "Res Test"})
    sid = json.loads(create[0].text)["session_id"]
    resource = await mcp_client.read_resource(f"oxidize://session/{sid}")
    data = json.loads(resource.contents[0].text)
    assert data["session_id"] == sid
    assert data["title"] == "Res Test"

async def test_resource_session_missing_returns_error(mcp_client):
    resource = await mcp_client.read_resource("oxidize://session/nonexistent")
    import json
    data = json.loads(resource.contents[0].text)
    assert "error" in data
```

**GREEN**: Register `@mcp.resource("oxidize://session/{id}")` as parameterized resource. Read from `ctx.state["sessions"].get(id)`. Return session data or `{"error": "session not found"}`.

**REFACTOR**: None.

---

## Tier 7: Prompts

### Feature F-049: prompt `create-invoice` [M]
Dependencies: F-001

**RED**: Write test `tests/mcp/test_prompts.py`
```python
async def test_prompt_create_invoice_listed(mcp_client):
    prompts = await mcp_client.list_prompts()
    names = [p.name for p in prompts]
    assert "create-invoice" in names

async def test_prompt_create_invoice_content(mcp_client):
    result = await mcp_client.get_prompt(
        "create-invoice",
        {"company": "Acme Corp", "items": "Widget x2 $10, Gadget x1 $25"},
    )
    assert result is not None
    text = result.messages[0].content.text
    assert "Acme Corp" in text
    assert "invoice" in text.lower()
```

**GREEN**: Create `python/oxidize_pdf/mcp/prompts.py`. Register `@mcp.prompt` `create-invoice(company: str, items: str)` returning multi-step instructions for using `create_pdf`, `add_pdf_content`, `save_pdf` to build an invoice. Import and call from `server.py`.

**REFACTOR**: None.

---

### Feature F-050: prompt `extract-for-rag` [M]
Dependencies: F-049

**RED**: Add to `tests/mcp/test_prompts.py`
```python
async def test_prompt_extract_for_rag_listed(mcp_client):
    prompts = await mcp_client.list_prompts()
    names = [p.name for p in prompts]
    assert "extract-for-rag" in names

async def test_prompt_extract_for_rag_content(mcp_client):
    result = await mcp_client.get_prompt(
        "extract-for-rag",
        {"path": "/tmp/doc.pdf", "chunk_size": "500"},
    )
    text = result.messages[0].content.text
    assert "convert_pdf" in text or "extract" in text.lower()
    assert "chunks" in text.lower() or "rag" in text.lower()
```

**GREEN**: Register `@mcp.prompt` `extract-for-rag(path: str, chunk_size: str = "256")` returning instructions to call `convert_pdf` with `format="rag"` and guidance on using chunks for vector store ingestion.

**REFACTOR**: None.

---

### Feature F-051: prompt `review-pdf` [M]
Dependencies: F-049

**RED**: Add to `tests/mcp/test_prompts.py`
```python
async def test_prompt_review_pdf_listed(mcp_client):
    prompts = await mcp_client.list_prompts()
    names = [p.name for p in prompts]
    assert "review-pdf" in names

async def test_prompt_review_pdf_content(mcp_client):
    result = await mcp_client.get_prompt(
        "review-pdf", {"path": "/tmp/report.pdf"}
    )
    text = result.messages[0].content.text
    assert "read_pdf" in text or "analyze" in text.lower()
```

**GREEN**: Register `@mcp.prompt` `review-pdf(path: str)` returning a workflow: 1) `read_pdf` for metadata, 2) `extract_text` for content, 3) `analyze_pdf` for validation. Includes guidance on summarizing findings.

**REFACTOR**: None.

---

### Feature F-052: prompt `compare-documents` [M]
Dependencies: F-049

**RED**: Add to `tests/mcp/test_prompts.py`
```python
async def test_prompt_compare_documents_listed(mcp_client):
    prompts = await mcp_client.list_prompts()
    names = [p.name for p in prompts]
    assert "compare-documents" in names

async def test_prompt_compare_documents_content(mcp_client):
    result = await mcp_client.get_prompt(
        "compare-documents",
        {"path1": "/tmp/a.pdf", "path2": "/tmp/b.pdf"},
    )
    text = result.messages[0].content.text
    assert "analyze_pdf" in text or "compare" in text.lower()
```

**GREEN**: Register `@mcp.prompt` `compare-documents(path1: str, path2: str)` returning instructions to call `analyze_pdf` with `check="compare"` and interpret the diff.

**REFACTOR**: None.

---

### Feature F-053: prompt `fill-form` [M]
Dependencies: F-049

**RED**: Add to `tests/mcp/test_prompts.py`
```python
async def test_prompt_fill_form_listed(mcp_client):
    prompts = await mcp_client.list_prompts()
    names = [p.name for p in prompts]
    assert "fill-form" in names

async def test_prompt_fill_form_content(mcp_client):
    result = await mcp_client.get_prompt(
        "fill-form",
        {"form_path": "/tmp/form.pdf", "context": "Name: Bob, Age: 30"},
    )
    text = result.messages[0].content.text
    assert "manage_forms" in text or "fill" in text.lower()
```

**GREEN**: Register `@mcp.prompt` `fill-form(form_path: str, context: str)` with instructions to 1) `manage_forms` with `operation="read"` to discover fields, 2) map context values to field names, 3) `manage_forms` with `operation="fill"`.

**REFACTOR**: None.

---

## Tier 8: Integration and Edge Cases

### Feature F-054: server registers all 12 tools [S]
Dependencies: F-013 through F-042

**RED**: Add to `tests/mcp/test_import.py`
```python
async def test_all_12_tools_registered(mcp_client):
    tools = await mcp_client.list_tools()
    names = {t.name for t in tools}
    expected = {
        "read_pdf", "extract_text", "convert_pdf", "analyze_pdf",
        "extract_entities", "manipulate_pdf", "annotate_pdf",
        "manage_forms", "secure_pdf", "create_pdf", "add_pdf_content",
        "save_pdf",
    }
    assert expected.issubset(names)
```

**GREEN**: Ensure all tool modules are imported in `server.py`. Add any missing registrations.

**REFACTOR**: None.

---

### Feature F-055: server registers all 6 resources [S]
Dependencies: F-043 through F-048

**RED**: Add to `tests/mcp/test_import.py`
```python
async def test_all_resources_registered(mcp_client):
    resources = await mcp_client.list_resources()
    uris = {str(r.uri) for r in resources}
    # Static resources
    assert "oxidize://fonts" in uris
    assert "oxidize://page-sizes" in uris
    assert "oxidize://capabilities" in uris
    assert "oxidize://version" in uris
    assert "oxidize://workspace" in uris
    # Parameterized resource template
    templates = await mcp_client.list_resource_templates()
    template_uris = {str(t.uri_template) for t in templates}
    assert "oxidize://session/{id}" in template_uris
```

**GREEN**: Verify `resources.py` is imported in `server.py` and all 5 static + 1 template are registered.

**REFACTOR**: None.

---

### Feature F-056: server registers all 5 prompts [S]
Dependencies: F-049 through F-053

**RED**: Add to `tests/mcp/test_import.py`
```python
async def test_all_5_prompts_registered(mcp_client):
    prompts = await mcp_client.list_prompts()
    names = {p.name for p in prompts}
    expected = {
        "create-invoice", "extract-for-rag", "review-pdf",
        "compare-documents", "fill-form",
    }
    assert expected.issubset(names)
```

**GREEN**: Verify `prompts.py` is imported in `server.py` and all 5 prompts are registered.

**REFACTOR**: None.

---

### Feature F-057: tool `read_pdf` — large file rejection [S]
Dependencies: F-015, F-006

**RED**: Add to `tests/mcp/test_tool_read_pdf.py`
```python
async def test_read_pdf_rejects_oversized_file(mcp_client, mcp_workspace, monkeypatch):
    import oxidize_pdf.mcp.config as cfg_mod
    from importlib import reload
    monkeypatch.setenv("OXIDIZE_MAX_FILE_SIZE_MB", "0")
    reload(cfg_mod)
    tiny = mcp_workspace / "tiny.pdf"
    from oxidize_pdf import Document, Page
    doc = Document()
    doc.add_page(Page.a4())
    doc.save(str(tiny))
    result = await mcp_client.call_tool("read_pdf", {"path": str(tiny)})
    import json
    out = json.loads(result[0].text)
    assert "error" in out
    monkeypatch.delenv("OXIDIZE_MAX_FILE_SIZE_MB", raising=False)
    reload(cfg_mod)
```

**GREEN**: Add `check_file_size(path, cfg.max_file_size_bytes)` call in `read_pdf` tool after path validation. Catch `SecurityError`, return error dict with `code="FILE_TOO_LARGE"`.

**REFACTOR**: None.

---

### Feature F-058: `add_pdf_content` — add font and size to text [S]
Dependencies: F-039

**RED**: Add to `tests/mcp/test_tool_add_content.py`
```python
async def test_add_text_with_font_and_size(mcp_client, mcp_workspace):
    import json
    create = await mcp_client.call_tool("create_pdf", {"title": "Styled"})
    sid = json.loads(create[0].text)["session_id"]

    result = await mcp_client.call_tool(
        "add_pdf_content",
        {
            "session_id": sid,
            "content_type": "text",
            "content": "Styled Text",
            "x": 100.0,
            "y": 700.0,
            "font": "Helvetica",
            "font_size": 16.0,
        },
    )
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"

    out = mcp_workspace / "styled.pdf"
    await mcp_client.call_tool(
        "save_pdf", {"session_id": sid, "output_path": str(out)}
    )
    assert out.exists()
```

**GREEN**: Add `font: str | None`, `font_size: float | None` to `add_pdf_content` params. Store in content descriptor. In `_build_document_from_session`, call `page.set_font(Font[font], font_size)` if specified.

**REFACTOR**: None.

---

### Feature F-059: `save_pdf` — encrypt on save [S]
Dependencies: F-041

**RED**: Add to `tests/mcp/test_tool_save_pdf.py`
```python
async def test_save_pdf_with_encryption(mcp_client, mcp_workspace):
    import json
    create = await mcp_client.call_tool("create_pdf", {"title": "Secure"})
    sid = json.loads(create[0].text)["session_id"]
    out = mcp_workspace / "enc.pdf"
    result = await mcp_client.call_tool(
        "save_pdf",
        {
            "session_id": sid,
            "output_path": str(out),
            "user_password": "u123",
            "owner_password": "o123",
        },
    )
    resp = json.loads(result[0].text)
    assert resp.get("status") == "ok"
    from oxidize_pdf import PdfReader
    reader = PdfReader.open(str(out))
    assert reader.is_encrypted
```

**GREEN**: Add `user_password`, `owner_password` optional params to `save_pdf`. If provided, call `doc.encrypt(user_password, owner_password)` before saving.

**REFACTOR**: None.

---

### Feature F-060: integration — full invoice creation workflow [L]
Dependencies: F-037, F-039, F-041, F-043

**RED**: Write test `tests/mcp/test_integration.py`
```python
async def test_full_invoice_creation_workflow(mcp_client, mcp_workspace):
    import json

    # Step 1: create session
    create = await mcp_client.call_tool(
        "create_pdf", {"title": "Invoice #001", "author": "Acme Corp"}
    )
    sid = json.loads(create[0].text)["session_id"]

    # Step 2: add header
    await mcp_client.call_tool(
        "add_pdf_content",
        {"session_id": sid, "content_type": "text",
         "content": "Invoice #001", "x": 100.0, "y": 750.0, "font_size": 24.0},
    )

    # Step 3: add line item
    await mcp_client.call_tool(
        "add_pdf_content",
        {"session_id": sid, "content_type": "text",
         "content": "Widget x2 - $20.00", "x": 100.0, "y": 700.0},
    )

    # Step 4: save
    out = mcp_workspace / "invoice.pdf"
    save = await mcp_client.call_tool(
        "save_pdf", {"session_id": sid, "output_path": str(out)}
    )
    resp = json.loads(save[0].text)
    assert resp.get("status") == "ok"
    assert out.exists()
    data = out.read_bytes()
    assert data[:5] == b"%PDF-"
```

**GREEN**: No new code — this validates the full pipeline works end to end.

**REFACTOR**: None.

---

### Feature F-061: integration — read then convert to markdown [M]
Dependencies: F-013, F-019

**RED**: Add to `tests/mcp/test_integration.py`
```python
async def test_read_then_convert_workflow(mcp_client, sample_pdf_with_text):
    import json

    read = await mcp_client.call_tool("read_pdf", {"path": str(sample_pdf_with_text)})
    meta = json.loads(read[0].text)
    assert meta["page_count"] >= 1

    convert = await mcp_client.call_tool(
        "convert_pdf", {"path": str(sample_pdf_with_text), "format": "markdown"}
    )
    out = json.loads(convert[0].text)
    assert isinstance(out["content"], str)
```

**GREEN**: No new code — integration validation.

**REFACTOR**: None.

---

### Feature F-062: integration — split then merge [M]
Dependencies: F-025, F-026

**RED**: Add to `tests/mcp/test_integration.py`
```python
async def test_split_then_merge_workflow(mcp_client, two_page_pdf, mcp_workspace):
    import json

    split_dir = mcp_workspace / "split"
    split_dir.mkdir()
    split = await mcp_client.call_tool(
        "manipulate_pdf",
        {"operation": "split", "input_path": str(two_page_pdf), "output_path": str(split_dir)},
    )
    assert json.loads(split[0].text)["status"] == "ok"

    pages = list(split_dir.glob("*.pdf"))
    assert len(pages) >= 1

    merged_out = mcp_workspace / "merged_back.pdf"
    merge = await mcp_client.call_tool(
        "manipulate_pdf",
        {
            "operation": "merge",
            "input_paths": [str(p) for p in sorted(pages)],
            "output_path": str(merged_out),
        },
    )
    assert json.loads(merge[0].text)["status"] == "ok"
    assert merged_out.exists()
```

**GREEN**: No new code — integration validation.

**REFACTOR**: None.

---

### Feature F-063: ELIMINADA (smoke test — `assert callable`)

---

### Feature F-064: tool `convert_pdf` — security enforcement [S]
Dependencies: F-019, F-005

**RED**: Add to `tests/mcp/test_tool_convert_pdf.py`
```python
async def test_convert_rejects_unsafe_path(mcp_client):
    result = await mcp_client.call_tool(
        "convert_pdf", {"path": "/etc/hosts", "format": "markdown"}
    )
    import json
    out = json.loads(result[0].text)
    assert out.get("code") == "SECURITY_ERROR"
```

**GREEN**: Add `validate_path` call at top of `convert_pdf` tool.

**REFACTOR**: None.

---

### Feature F-065: tool `manipulate_pdf` — security on output path [S]
Dependencies: F-025, F-005

**RED**: Add to `tests/mcp/test_tool_manipulate_pdf.py`
```python
async def test_manipulate_rejects_output_outside_workspace(mcp_client, sample_pdf):
    result = await mcp_client.call_tool(
        "manipulate_pdf",
        {
            "operation": "rotate",
            "input_path": str(sample_pdf),
            "output_path": "/etc/evil.pdf",
            "degrees": 90,
        },
    )
    import json
    resp = json.loads(result[0].text)
    assert resp.get("code") == "SECURITY_ERROR"
```

**GREEN**: Add `validate_path(output_path, workspace, must_exist=False, allowed_extensions={".pdf"})` in `manipulate_pdf` tool.

**REFACTOR**: None.

---

## Tier 9: Final Quality

### Feature F-066: all tool docstrings and descriptions [S]
Dependencies: F-054

**RED**: Add to `tests/mcp/test_import.py`
```python
async def test_all_tools_have_descriptions(mcp_client):
    tools = await mcp_client.list_tools()
    for tool in tools:
        assert tool.description, f"Tool {tool.name!r} has no description"
        assert len(tool.description) > 10, f"Tool {tool.name!r} description too short"
```

**GREEN**: Ensure all `@mcp.tool` decorated functions have docstrings longer than 10 characters. Update any missing.

**REFACTOR**: None.

---

### Feature F-067: all resources have descriptions [S]
Dependencies: F-055

**RED**: Add to `tests/mcp/test_import.py`
```python
async def test_all_resources_have_descriptions(mcp_client):
    resources = await mcp_client.list_resources()
    for r in resources:
        assert r.description, f"Resource {r.uri!r} has no description"
```

**GREEN**: Ensure all `@mcp.resource` functions have docstrings.

**REFACTOR**: None.

---

### Feature F-068: all prompts have descriptions [S]
Dependencies: F-056

**RED**: Add to `tests/mcp/test_import.py`
```python
async def test_all_prompts_have_descriptions(mcp_client):
    prompts = await mcp_client.list_prompts()
    for p in prompts:
        assert p.description, f"Prompt {p.name!r} has no description"
```

**GREEN**: Ensure all `@mcp.prompt` functions have docstrings.

**REFACTOR**: None.

---

### Feature F-069: ELIMINADA (smoke test — `assert hasattr`, `assert is not None`)

---

## Estimacion Total (actualizado 2026-03-29)

- Tier 1 (Infrastructure): COMPLETADO — 37 tests
- Tier 2 (Read & Extract): COMPLETADO — 7 features (F-013 a F-020)
- Tier 3 (Analyze, Entities, Manipulate): COMPLETADO — 8 features (F-021 a F-028)
- Tier 4 (Annotate, Forms, Secure): COMPLETADO — 8 features (F-029 a F-036)
- Tier 5 (Stateful): COMPLETADO — 6 features (F-037 a F-042)
- Tier 6 (Resources): COMPLETADO — 6 features (F-043 a F-048)
- Tier 7 (Prompts): COMPLETADO — 5 features (F-049 a F-053)
- Tier 8 (Integration): COMPLETADO — 8 features (F-054 a F-062, F-064, F-065)
- Tier 9 (Quality): COMPLETADO — 3 features (F-066 a F-068)

**Eliminadas**: F-001, F-002, F-003 (smoke), F-063 (smoke), F-069 (smoke)
**Total tests MCP**: 166 pasando
**Total tests proyecto**: 1960 pasando

## Criterios de Exito

- [x] Todos los tests pasan con `pytest tests/mcp_tests/ -v`
- [x] `asyncio_mode = "auto"` configurado en pyproject.toml
- [x] 12 tools, 6 resources, 5 prompts registrados
- [x] Todos los tools validan paths via `security.py`
- [x] Sessions de creacion funcionan end-to-end (create → add → save)
- [x] Sin regresion en tests existentes (`pytest tests/` completo verde)
- [x] Modulo importable como `from oxidize_pdf.mcp.server import mcp`
- [x] `fastmcp>=2.0` en optional-dependencies `[mcp]` de pyproject.toml

## Archivos a Crear

```
python/oxidize_pdf/mcp/__init__.py
python/oxidize_pdf/mcp/server.py
python/oxidize_pdf/mcp/config.py
python/oxidize_pdf/mcp/security.py
python/oxidize_pdf/mcp/sessions.py
python/oxidize_pdf/mcp/models.py
python/oxidize_pdf/mcp/resources.py
python/oxidize_pdf/mcp/prompts.py
python/oxidize_pdf/mcp/tools/__init__.py
python/oxidize_pdf/mcp/tools/read_pdf.py
python/oxidize_pdf/mcp/tools/extract_text.py
python/oxidize_pdf/mcp/tools/convert_pdf.py
python/oxidize_pdf/mcp/tools/analyze_pdf.py
python/oxidize_pdf/mcp/tools/extract_entities.py
python/oxidize_pdf/mcp/tools/manipulate_pdf.py
python/oxidize_pdf/mcp/tools/annotate_pdf.py
python/oxidize_pdf/mcp/tools/manage_forms.py
python/oxidize_pdf/mcp/tools/secure_pdf.py
python/oxidize_pdf/mcp/tools/create_pdf.py
python/oxidize_pdf/mcp/tools/add_pdf_content.py
python/oxidize_pdf/mcp/tools/save_pdf.py
tests/mcp_tests/__init__.py          [EXISTE]
tests/mcp_tests/conftest.py          [EXISTE]
tests/mcp_tests/test_config.py       [EXISTE]
tests/mcp_tests/test_security.py     [EXISTE]
tests/mcp_tests/test_sessions.py     [EXISTE]
tests/mcp_tests/test_models.py       [EXISTE]
tests/mcp_tests/test_server_registration.py  (reemplaza test_import.py — F-054/F-055/F-056/F-066/F-067/F-068)
tests/mcp_tests/test_resources.py
tests/mcp_tests/test_prompts.py
tests/mcp_tests/test_tool_read_pdf.py
tests/mcp_tests/test_tool_extract_text.py
tests/mcp_tests/test_tool_convert_pdf.py
tests/mcp_tests/test_tool_analyze_pdf.py
tests/mcp_tests/test_tool_extract_entities.py
tests/mcp_tests/test_tool_manipulate_pdf.py
tests/mcp_tests/test_tool_annotate_pdf.py
tests/mcp_tests/test_tool_manage_forms.py
tests/mcp_tests/test_tool_secure_pdf.py
tests/mcp_tests/test_tool_create_pdf.py
tests/mcp_tests/test_tool_add_content.py
tests/mcp_tests/test_tool_save_pdf.py
tests/mcp_tests/test_integration.py
```

## Archivos a Modificar

```
pyproject.toml  — add [mcp] optional-deps, pytest asyncio_mode="auto"
```
