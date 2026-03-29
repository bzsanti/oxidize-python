"""Tests for the save_pdf MCP tool."""

import json

import pytest


class TestSavePdf:
    """F-041: save_pdf — finalize session to file."""

    pytestmark = pytest.mark.asyncio

    async def test_save_pdf_creates_file(self, mcp_client, mcp_workspace):
        create = await mcp_client.call_tool("create_pdf", {"title": "Saved Doc"})
        sid = json.loads(create.content[0].text)["session_id"]

        await mcp_client.call_tool(
            "add_pdf_content",
            {
                "session_id": sid,
                "content_type": "text",
                "content": "Page 1",
                "x": 100.0,
                "y": 700.0,
            },
        )

        out = mcp_workspace / "saved.pdf"
        result = await mcp_client.call_tool(
            "save_pdf",
            {"session_id": sid, "output_path": str(out)},
        )
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"
        assert out.exists()
        assert out.read_bytes()[:5] == b"%PDF-"

    async def test_save_pdf_tool_is_listed(self, mcp_client):
        tools = await mcp_client.list_tools()
        names = [t.name for t in tools]
        assert "save_pdf" in names


class TestSavePdfCleanup:
    """F-042: save_pdf — cleanup session after save."""

    pytestmark = pytest.mark.asyncio

    async def test_save_cleans_up_session(self, mcp_client, mcp_workspace):
        create = await mcp_client.call_tool("create_pdf", {"title": "Temp"})
        sid = json.loads(create.content[0].text)["session_id"]

        out = mcp_workspace / "cleaned.pdf"
        await mcp_client.call_tool(
            "save_pdf", {"session_id": sid, "output_path": str(out)}
        )

        resource = await mcp_client.read_resource(f"oxidize://session/{sid}")
        data = json.loads(resource[0].text) if resource else None
        assert data is None or data.get("status") == "completed"

    async def test_save_pdf_with_encryption(self, mcp_client, mcp_workspace):
        """F-059: encrypt on save."""
        from oxidize_pdf import PdfReader

        create = await mcp_client.call_tool("create_pdf", {"title": "Secure"})
        sid = json.loads(create.content[0].text)["session_id"]
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
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"
        reader = PdfReader.open(str(out))
        assert reader.is_encrypted

    async def test_save_missing_session_returns_error(self, mcp_client, mcp_workspace):
        result = await mcp_client.call_tool(
            "save_pdf",
            {"session_id": "ghost", "output_path": str(mcp_workspace / "x.pdf")},
        )
        resp = json.loads(result.content[0].text)
        assert "error" in resp
