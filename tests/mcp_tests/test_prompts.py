"""Tests for MCP prompts."""

import re

import pytest

REGISTERED_TOOLS = {
    "read_pdf", "extract_text", "convert_pdf", "analyze_pdf",
    "extract_entities", "manipulate_pdf", "annotate_pdf",
    "manage_forms", "secure_pdf", "create_pdf", "add_pdf_content",
    "save_pdf",
}


def _extract_tool_refs(text: str) -> set[str]:
    """Extract backtick-quoted tool names from prompt text."""
    return {m for m in re.findall(r"`(\w+)`", text) if m in REGISTERED_TOOLS}


class TestCreateInvoicePrompt:
    """F-049: create-invoice prompt."""

    pytestmark = pytest.mark.asyncio

    async def test_prompt_listed(self, mcp_client):
        prompts = await mcp_client.list_prompts()
        names = [p.name for p in prompts]
        assert "create-invoice" in names

    async def test_prompt_content(self, mcp_client):
        result = await mcp_client.get_prompt(
            "create-invoice",
            {"company": "Acme Corp", "items": "Widget x2 $10, Gadget x1 $25"},
        )
        text = result.messages[0].content.text
        assert "Acme Corp" in text
        assert "invoice" in text.lower()

    async def test_prompt_references_valid_tools(self, mcp_client):
        result = await mcp_client.get_prompt(
            "create-invoice",
            {"company": "Test", "items": "Item x1 $5"},
        )
        refs = _extract_tool_refs(result.messages[0].content.text)
        assert refs, "Prompt should reference at least one registered tool"
        assert refs.issubset(REGISTERED_TOOLS)


class TestExtractForRagPrompt:
    """F-050: extract-for-rag prompt."""

    pytestmark = pytest.mark.asyncio

    async def test_prompt_listed(self, mcp_client):
        prompts = await mcp_client.list_prompts()
        names = [p.name for p in prompts]
        assert "extract-for-rag" in names

    async def test_prompt_content(self, mcp_client):
        result = await mcp_client.get_prompt(
            "extract-for-rag",
            {"path": "/tmp/doc.pdf", "chunk_size": "500"},
        )
        text = result.messages[0].content.text
        assert "extract" in text.lower() or "convert_pdf" in text
        assert "chunks" in text.lower() or "rag" in text.lower()


class TestReviewPdfPrompt:
    """F-051: review-pdf prompt."""

    pytestmark = pytest.mark.asyncio

    async def test_prompt_listed(self, mcp_client):
        prompts = await mcp_client.list_prompts()
        names = [p.name for p in prompts]
        assert "review-pdf" in names

    async def test_prompt_content(self, mcp_client):
        result = await mcp_client.get_prompt(
            "review-pdf", {"path": "/tmp/report.pdf"}
        )
        text = result.messages[0].content.text
        assert "read_pdf" in text or "analyze" in text.lower()


class TestCompareDocumentsPrompt:
    """F-052: compare-documents prompt."""

    pytestmark = pytest.mark.asyncio

    async def test_prompt_listed(self, mcp_client):
        prompts = await mcp_client.list_prompts()
        names = [p.name for p in prompts]
        assert "compare-documents" in names

    async def test_prompt_content(self, mcp_client):
        result = await mcp_client.get_prompt(
            "compare-documents",
            {"path1": "/tmp/a.pdf", "path2": "/tmp/b.pdf"},
        )
        text = result.messages[0].content.text
        assert "analyze_pdf" in text or "compare" in text.lower()


class TestFillFormPrompt:
    """F-053: fill-form prompt."""

    pytestmark = pytest.mark.asyncio

    async def test_prompt_listed(self, mcp_client):
        prompts = await mcp_client.list_prompts()
        names = [p.name for p in prompts]
        assert "fill-form" in names

    async def test_prompt_content(self, mcp_client):
        result = await mcp_client.get_prompt(
            "fill-form",
            {"form_path": "/tmp/form.pdf", "context": "Name: Bob, Age: 30"},
        )
        text = result.messages[0].content.text
        assert "manage_forms" in text or "fill" in text.lower()
