"""Tests for the manipulate_pdf MCP tool."""

import json

import pytest


class TestManipulateSplit:
    """F-025: manipulate_pdf split operation."""

    pytestmark = pytest.mark.asyncio

    async def test_split_returns_ok(self, mcp_client, sample_pdf, mcp_workspace):
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
        out = json.loads(result.content[0].text)
        assert out.get("status") == "ok"
        assert out.get("operation") == "split"


class TestManipulateMerge:
    """F-026: manipulate_pdf merge operation."""

    pytestmark = pytest.mark.asyncio

    async def test_merge_returns_ok(
        self, mcp_client, sample_pdf, sample_pdf_copy, mcp_workspace
    ):
        out_file = mcp_workspace / "merged.pdf"
        result = await mcp_client.call_tool(
            "manipulate_pdf",
            {
                "operation": "merge",
                "input_paths": [str(sample_pdf), str(sample_pdf_copy)],
                "output_path": str(out_file),
            },
        )
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"
        assert out_file.exists()

    async def test_merge_missing_input_paths_returns_error(
        self, mcp_client, mcp_workspace
    ):
        out_file = mcp_workspace / "merged.pdf"
        result = await mcp_client.call_tool(
            "manipulate_pdf",
            {
                "operation": "merge",
                "output_path": str(out_file),
            },
        )
        resp = json.loads(result.content[0].text)
        assert "error" in resp


class TestManipulateRotate:
    """F-027: manipulate_pdf rotate operation."""

    pytestmark = pytest.mark.asyncio

    async def test_rotate_returns_ok(self, mcp_client, sample_pdf, mcp_workspace):
        out_file = mcp_workspace / "rotated.pdf"
        result = await mcp_client.call_tool(
            "manipulate_pdf",
            {
                "operation": "rotate",
                "input_path": str(sample_pdf),
                "output_path": str(out_file),
                "degrees": 90,
            },
        )
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"


class TestManipulateExtractPages:
    """F-027: manipulate_pdf extract_pages operation."""

    pytestmark = pytest.mark.asyncio

    async def test_extract_pages_returns_ok(
        self, mcp_client, two_page_pdf, mcp_workspace
    ):
        out_file = mcp_workspace / "extracted.pdf"
        result = await mcp_client.call_tool(
            "manipulate_pdf",
            {
                "operation": "extract_pages",
                "input_path": str(two_page_pdf),
                "output_path": str(out_file),
                "page_indices": [0],
            },
        )
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"


class TestManipulateInvalidOperation:
    """F-027: manipulate_pdf invalid operation."""

    pytestmark = pytest.mark.asyncio

    async def test_invalid_operation_returns_error(
        self, mcp_client, sample_pdf, mcp_workspace
    ):
        result = await mcp_client.call_tool(
            "manipulate_pdf",
            {
                "operation": "vaporize",
                "input_path": str(sample_pdf),
                "output_path": str(mcp_workspace / "x.pdf"),
            },
        )
        resp = json.loads(result.content[0].text)
        assert "error" in resp


class TestManipulateReverse:
    """F-028: manipulate_pdf reverse operation."""

    pytestmark = pytest.mark.asyncio

    async def test_reverse_returns_ok(
        self, mcp_client, two_page_pdf, mcp_workspace
    ):
        out_file = mcp_workspace / "reversed.pdf"
        result = await mcp_client.call_tool(
            "manipulate_pdf",
            {
                "operation": "reverse",
                "input_path": str(two_page_pdf),
                "output_path": str(out_file),
            },
        )
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"


class TestManipulateOverlay:
    """F-028: manipulate_pdf overlay operation."""

    pytestmark = pytest.mark.asyncio

    async def test_overlay_returns_ok(
        self, mcp_client, sample_pdf, sample_pdf_copy, mcp_workspace
    ):
        out_file = mcp_workspace / "overlaid.pdf"
        result = await mcp_client.call_tool(
            "manipulate_pdf",
            {
                "operation": "overlay",
                "input_path": str(sample_pdf),
                "overlay_path": str(sample_pdf_copy),
                "output_path": str(out_file),
            },
        )
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"

    async def test_overlay_missing_overlay_path_returns_error(
        self, mcp_client, sample_pdf, mcp_workspace
    ):
        out_file = mcp_workspace / "overlaid.pdf"
        result = await mcp_client.call_tool(
            "manipulate_pdf",
            {
                "operation": "overlay",
                "input_path": str(sample_pdf),
                "output_path": str(out_file),
            },
        )
        resp = json.loads(result.content[0].text)
        assert "error" in resp
