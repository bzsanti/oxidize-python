"""Tests for the convert_pdf MCP tool."""

import json

import pytest


class TestConvertToMarkdown:
    """F-019: convert_pdf converts PDF content to markdown."""

    pytestmark = pytest.mark.asyncio

    async def test_returns_markdown_content(self, mcp_client, sample_pdf_with_text):
        result = await mcp_client.call_tool(
            "convert_pdf", {"path": str(sample_pdf_with_text), "format": "markdown"}
        )
        out = json.loads(result.content[0].text)
        assert "content" in out
        assert out["format"] == "markdown"
        assert isinstance(out["content"], str)
        assert len(out["content"]) > 0

    async def test_markdown_contains_pdf_text(self, mcp_client, sample_pdf_with_text):
        result = await mcp_client.call_tool(
            "convert_pdf", {"path": str(sample_pdf_with_text), "format": "markdown"}
        )
        out = json.loads(result.content[0].text)
        assert "Chapter 1" in out["content"] or "Introduction" in out["content"]


class TestConvertToChunks:
    """F-020: convert_pdf converts PDF to chunks for RAG/LLM pipelines."""

    pytestmark = pytest.mark.asyncio

    async def test_returns_chunks_list(self, mcp_client, sample_pdf_with_text):
        result = await mcp_client.call_tool(
            "convert_pdf",
            {"path": str(sample_pdf_with_text), "format": "chunks", "max_tokens": 100},
        )
        out = json.loads(result.content[0].text)
        assert "chunks" in out
        assert isinstance(out["chunks"], list)
        assert out["format"] == "chunks"

    async def test_chunks_have_content(self, mcp_client, sample_pdf_with_text):
        result = await mcp_client.call_tool(
            "convert_pdf",
            {"path": str(sample_pdf_with_text), "format": "chunks"},
        )
        out = json.loads(result.content[0].text)
        assert len(out["chunks"]) > 0
        chunk = out["chunks"][0]
        assert "content" in chunk
        assert len(chunk["content"]) > 0

    async def test_rag_format_returns_chunks(self, mcp_client, sample_pdf_with_text):
        result = await mcp_client.call_tool(
            "convert_pdf",
            {"path": str(sample_pdf_with_text), "format": "rag"},
        )
        out = json.loads(result.content[0].text)
        assert "chunks" in out
        assert out["format"] == "rag"
        assert len(out["chunks"]) > 0
        chunk = out["chunks"][0]
        assert "text" in chunk

    async def test_rag_ignores_max_tokens(self, mcp_client, sample_pdf_with_text):
        """The ``rag`` format uses heading-aware semantic chunking with a fixed
        internal budget: ``max_tokens`` does not apply (it drives only the
        fixed-window ``chunks`` format). Pin that contract so the parameter
        description stays truthful — two very different ``max_tokens`` values
        must produce byte-identical rag output."""

        async def rag_with(max_tokens: int) -> list:
            result = await mcp_client.call_tool(
                "convert_pdf",
                {
                    "path": str(sample_pdf_with_text),
                    "format": "rag",
                    "max_tokens": max_tokens,
                },
            )
            return json.loads(result.content[0].text)["chunks"]

        small = await rag_with(16)
        large = await rag_with(4096)
        assert small == large, "rag output must be independent of max_tokens"


class TestConvertPdfFormatValidation:
    """C-6/R-8: convert_pdf validates format parameter."""

    pytestmark = pytest.mark.asyncio

    async def test_invalid_format_raises_validation_error(
        self, mcp_client, sample_pdf_with_text
    ):
        from fastmcp.exceptions import ToolError

        with pytest.raises(ToolError, match="should be 'markdown', 'chunks' or 'rag'"):
            await mcp_client.call_tool(
                "convert_pdf",
                {"path": str(sample_pdf_with_text), "format": "xml"},
            )

    async def test_empty_format_raises_validation_error(
        self, mcp_client, sample_pdf_with_text
    ):
        from fastmcp.exceptions import ToolError

        with pytest.raises(ToolError, match="should be 'markdown', 'chunks' or 'rag'"):
            await mcp_client.call_tool(
                "convert_pdf",
                {"path": str(sample_pdf_with_text), "format": ""},
            )


class TestConvertPdfSecurity:
    """F-020: convert_pdf enforces path security."""

    pytestmark = pytest.mark.asyncio

    async def test_rejects_unsafe_path(self, mcp_client):
        result = await mcp_client.call_tool(
            "convert_pdf", {"path": "/etc/hosts", "format": "markdown"}
        )
        out = json.loads(result.content[0].text)
        assert out.get("code") == "SECURITY_ERROR"

    async def test_encrypted_without_password_returns_error(
        self, mcp_client, encrypted_pdf
    ):
        result = await mcp_client.call_tool(
            "convert_pdf", {"path": str(encrypted_pdf), "format": "markdown"}
        )
        out = json.loads(result.content[0].text)
        assert "error" in out


class _FakeConvertReader:
    is_encrypted = False

    def __init__(self, page_count):
        self._page_count = page_count

    @property
    def page_count(self):
        return self._page_count

    def to_markdown(self):
        raise AssertionError("to_markdown must not run once the page cap is exceeded")

    def chunk(self, max_tokens, overlap):
        raise AssertionError("chunk must not run once the page cap is exceeded")

    def rag_chunks(self):
        raise AssertionError("rag_chunks must not run once the page cap is exceeded")


def _fake_pdfreader(page_count):
    class _FakePdfReader:
        @staticmethod
        def open(path):
            return _FakeConvertReader(page_count)

    return _FakePdfReader


class TestConvertPdfPageCountCap:
    """#115 Capa B: convert_pdf rejects documents over the page-count cap."""

    pytestmark = pytest.mark.asyncio

    async def test_rejects_real_pdf_over_cap(
        self, mcp_client, sample_pdf_with_text, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_PAGES", "0")
        result = await mcp_client.call_tool(
            "convert_pdf", {"path": str(sample_pdf_with_text), "format": "markdown"}
        )
        out = json.loads(result.content[0].text)
        assert out["code"] == "RESOURCE_LIMIT"
        assert "page" in out["error"].lower()

    async def test_conversion_never_called_when_over_cap(
        self, mcp_client, sample_pdf, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_PAGES", "5")
        monkeypatch.setattr("oxidize_pdf.PdfReader", _fake_pdfreader(999))
        result = await mcp_client.call_tool(
            "convert_pdf", {"path": str(sample_pdf), "format": "markdown"}
        )
        out = json.loads(result.content[0].text)
        assert out["code"] == "RESOURCE_LIMIT"


class TestConvertPdfOutputCap:
    """#115 Capa B: convert_pdf bounds the serialized response size."""

    pytestmark = pytest.mark.asyncio

    async def test_rejects_when_output_exceeds_cap(
        self, mcp_client, sample_pdf_with_text, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_OUTPUT_BYTES", "10")
        result = await mcp_client.call_tool(
            "convert_pdf", {"path": str(sample_pdf_with_text), "format": "markdown"}
        )
        out = json.loads(result.content[0].text)
        assert out["code"] == "RESOURCE_LIMIT"

    async def test_passes_when_output_within_cap(
        self, mcp_client, sample_pdf_with_text, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_OUTPUT_BYTES", str(10 * 1024 * 1024))
        result = await mcp_client.call_tool(
            "convert_pdf", {"path": str(sample_pdf_with_text), "format": "markdown"}
        )
        out = json.loads(result.content[0].text)
        assert "content" in out
        assert "error" not in out
