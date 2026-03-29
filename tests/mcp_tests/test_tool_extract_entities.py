"""Tests for the extract_entities MCP tool."""

import json

import pytest


class TestExtractEntities:
    """F-024: extract_entities tool."""

    pytestmark = pytest.mark.asyncio

    async def test_extract_entities_returns_structure(
        self, mcp_client, sample_pdf_with_text
    ):
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert "entities" in out
        assert isinstance(out["entities"], list)

    async def test_extract_entities_returns_page_count(
        self, mcp_client, sample_pdf_with_text
    ):
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert "page_count" in out
        assert isinstance(out["page_count"], int)
        assert out["page_count"] >= 1

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
