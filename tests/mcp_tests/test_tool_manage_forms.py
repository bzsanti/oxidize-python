"""Tests for the manage_forms MCP tool."""

import json

import pytest


class TestManageFormsCreate:
    """F-032: manage_forms create operation."""

    pytestmark = pytest.mark.asyncio

    async def test_create_text_field(self, mcp_client, mcp_workspace):
        out = mcp_workspace / "form.pdf"
        result = await mcp_client.call_tool(
            "manage_forms",
            {
                "operation": "create",
                "output_path": str(out),
                "fields": [
                    {
                        "type": "text",
                        "name": "first_name",
                        "x": 100.0,
                        "y": 700.0,
                        "width": 200.0,
                        "height": 30.0,
                    }
                ],
            },
        )
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"
        assert out.exists()
        assert resp.get("fields_created") == 1


class TestManageFormsFill:
    """F-033: manage_forms fill operation."""

    pytestmark = pytest.mark.asyncio

    async def test_fill_form(self, mcp_client, form_pdf, mcp_workspace):
        out = mcp_workspace / "filled.pdf"
        result = await mcp_client.call_tool(
            "manage_forms",
            {
                "operation": "fill",
                "input_path": str(form_pdf),
                "output_path": str(out),
                "values": {"first_name": "Alice"},
            },
        )
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"


class TestManageFormsRead:
    """F-034: manage_forms read operation."""

    pytestmark = pytest.mark.asyncio

    async def test_read_form(self, mcp_client, form_pdf):
        result = await mcp_client.call_tool(
            "manage_forms",
            {"operation": "read", "input_path": str(form_pdf)},
        )
        resp = json.loads(result.content[0].text)
        assert "fields" in resp


class TestManageFormsValidate:
    """F-034: manage_forms validate operation."""

    pytestmark = pytest.mark.asyncio

    async def test_validate_form(self, mcp_client, form_pdf):
        result = await mcp_client.call_tool(
            "manage_forms",
            {
                "operation": "validate",
                "input_path": str(form_pdf),
                "values": {"first_name": "Bob"},
            },
        )
        resp = json.loads(result.content[0].text)
        assert "valid" in resp
