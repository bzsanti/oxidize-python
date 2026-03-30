"""Tests for the create_pdf MCP tool."""

import json

import pytest


class TestCreatePdf:
    """F-037: create_pdf tool — session creation."""

    pytestmark = pytest.mark.asyncio

    async def test_create_pdf_returns_session_id(self, mcp_client):
        result = await mcp_client.call_tool(
            "create_pdf", {"title": "My Document"}
        )
        resp = json.loads(result.content[0].text)
        assert "session_id" in resp
        assert isinstance(resp["session_id"], str)
        assert resp.get("status") == "created"

    async def test_create_pdf_with_metadata(self, mcp_client):
        result = await mcp_client.call_tool(
            "create_pdf",
            {"title": "Report", "author": "Alice", "page_size": "letter"},
        )
        resp = json.loads(result.content[0].text)
        assert "session_id" in resp

    async def test_create_pdf_tool_is_listed(self, mcp_client):
        tools = await mcp_client.list_tools()
        names = [t.name for t in tools]
        assert "create_pdf" in names


class TestCreatePdfSessionPersists:
    """F-038: create_pdf session persists across calls."""

    pytestmark = pytest.mark.asyncio

    async def test_session_is_retrievable_via_resource(self, mcp_client):
        create_result = await mcp_client.call_tool(
            "create_pdf", {"title": "Persistent Doc"}
        )
        create_resp = json.loads(create_result.content[0].text)
        sid = create_resp["session_id"]

        resource = await mcp_client.read_resource(f"oxidize://session/{sid}")
        assert resource is not None
