"""Tests for the extract_entities MCP tool."""

import json

import pytest


class TestExtractEntities:
    """F-024: extract_entities tool."""

    pytestmark = pytest.mark.asyncio

    async def test_extract_entities_returns_real_content(
        self, mcp_client, sample_pdf_with_text
    ):
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert "entities" in out
        assert isinstance(out["entities"], list)
        assert len(out["entities"]) > 0, "Should extract real entities from PDF with text"

        entity = out["entities"][0]
        assert "text" in entity
        assert "page" in entity
        assert "x" in entity
        assert "y" in entity
        assert "font_size" in entity
        assert isinstance(entity["text"], str)
        assert len(entity["text"]) > 0

    async def test_extract_entities_page_count_matches(
        self, mcp_client, sample_pdf_with_text
    ):
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert out["page_count"] == 2
        assert out["entity_count"] == len(out["entities"])

    async def test_extract_entities_contains_known_text(
        self, mcp_client, sample_pdf_with_text
    ):
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        all_text = " ".join(e["text"] for e in out["entities"])
        assert "Chapter 1" in all_text
        assert "Chapter 2" in all_text

    async def test_extract_entities_returns_path(
        self, mcp_client, sample_pdf_with_text
    ):
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert out["path"] == str(sample_pdf_with_text)

    async def test_extract_entities_rejects_unsafe_path(self, mcp_client):
        result = await mcp_client.call_tool(
            "extract_entities", {"path": "/etc/passwd"}
        )
        out = json.loads(result.content[0].text)
        assert out.get("code") == "SECURITY_ERROR"
