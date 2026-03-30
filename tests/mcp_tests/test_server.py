"""Tests for server initialization and tool registration."""

import pytest


class TestToolRegistration:
    pytestmark = pytest.mark.asyncio

    async def test_all_implemented_tools_registered(self):
        """The mcp server must have all 3 implemented tools registered."""
        from oxidize_pdf.mcp.server import mcp

        tools = await mcp.list_tools()
        tool_names = {t.name for t in tools}
        expected = {"read_pdf", "extract_text", "convert_pdf"}
        assert expected.issubset(tool_names), (
            f"Missing tools: {expected - tool_names}"
        )

    async def test_all_tools_have_descriptions(self):
        """Every registered tool must have a non-empty description."""
        from oxidize_pdf.mcp.server import mcp

        tools = await mcp.list_tools()
        for tool in tools:
            desc = tool.description or ""
            assert len(desc) > 10, f"Tool {tool.name!r} has no or too-short description"
