"""Tests for the add_pdf_content MCP tool."""

import json

import pytest


class TestAddTextContent:
    """F-039: add_pdf_content — add text block."""

    pytestmark = pytest.mark.asyncio

    async def test_add_text_content(self, mcp_client):
        create = await mcp_client.call_tool("create_pdf", {"title": "Doc"})
        sid = json.loads(create.content[0].text)["session_id"]

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
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"
        assert resp.get("session_id") == sid

    async def test_add_content_tool_is_listed(self, mcp_client):
        tools = await mcp_client.list_tools()
        names = [t.name for t in tools]
        assert "add_pdf_content" in names


class TestAddNewPage:
    """F-040: add_pdf_content — new page."""

    pytestmark = pytest.mark.asyncio

    async def test_add_new_page(self, mcp_client):
        create = await mcp_client.call_tool("create_pdf", {"title": "Doc"})
        sid = json.loads(create.content[0].text)["session_id"]

        result = await mcp_client.call_tool(
            "add_pdf_content",
            {"session_id": sid, "content_type": "new_page"},
        )
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"
        assert resp.get("page_count", 0) >= 1

    async def test_add_text_with_font_and_size(self, mcp_client, mcp_workspace):
        """F-058: add_pdf_content with font param."""
        create = await mcp_client.call_tool("create_pdf", {"title": "Styled"})
        sid = json.loads(create.content[0].text)["session_id"]

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
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"

        out = mcp_workspace / "styled.pdf"
        await mcp_client.call_tool(
            "save_pdf", {"session_id": sid, "output_path": str(out)}
        )
        assert out.exists()

    async def test_missing_session_returns_error(self, mcp_client):
        result = await mcp_client.call_tool(
            "add_pdf_content",
            {"session_id": "nonexistent", "content_type": "new_page"},
        )
        resp = json.loads(result.content[0].text)
        assert "error" in resp
