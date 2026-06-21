"""Tests for the annotate_pdf MCP tool."""

import json

import pytest


class TestAnnotateText:
    """F-029: annotate_pdf with text annotation."""

    pytestmark = pytest.mark.asyncio

    async def test_annotate_add_text(self, mcp_client, sample_pdf, mcp_workspace):
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
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"
        assert out.exists()
        data = out.read_bytes()
        assert data[:5] == b"%PDF-"


class TestAnnotateHighlight:
    """F-030: annotate_pdf with highlight annotation."""

    pytestmark = pytest.mark.asyncio

    async def test_annotate_highlight(self, mcp_client, sample_pdf, mcp_workspace):
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
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"


class TestAnnotateSecurity:
    """F-031: annotate_pdf security enforcement."""

    pytestmark = pytest.mark.asyncio

    async def test_annotate_rejects_unsafe_input(self, mcp_client, mcp_workspace):
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
        resp = json.loads(result.content[0].text)
        assert resp.get("code") == "SECURITY_ERROR"

    async def test_annotate_invalid_type_returns_error(
        self, mcp_client, sample_pdf, mcp_workspace
    ):
        # annotation_type is a Literal: an unknown value is rejected by schema
        # validation before the tool runs (ToolError), not as a JSON error body.
        from fastmcp.exceptions import ToolError

        with pytest.raises(ToolError, match="should be 'text' or 'highlight'"):
            await mcp_client.call_tool(
                "annotate_pdf",
                {
                    "input_path": str(sample_pdf),
                    "output_path": str(mcp_workspace / "out.pdf"),
                    "annotation_type": "sparkle",
                    "page": 0,
                    "x": 0.0,
                    "y": 0.0,
                },
            )
