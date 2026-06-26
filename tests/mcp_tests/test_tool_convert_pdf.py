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
