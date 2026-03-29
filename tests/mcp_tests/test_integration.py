"""Integration tests: all tools, resources, and prompts are registered."""

import json

import pytest


class TestAllToolsRegistered:
    """F-054: all 12 tools are registered."""

    pytestmark = pytest.mark.asyncio

    async def test_all_12_tools_registered(self, mcp_client):
        tools = await mcp_client.list_tools()
        names = {t.name for t in tools}
        expected = {
            "read_pdf", "extract_text", "convert_pdf", "analyze_pdf",
            "extract_entities", "manipulate_pdf", "annotate_pdf",
            "manage_forms", "secure_pdf", "create_pdf", "add_pdf_content",
            "save_pdf",
        }
        assert expected.issubset(names)


class TestAllResourcesRegistered:
    """F-055: all resources are registered."""

    pytestmark = pytest.mark.asyncio

    async def test_all_static_resources_registered(self, mcp_client):
        resources = await mcp_client.list_resources()
        uris = {str(r.uri) for r in resources}
        assert "oxidize://fonts" in uris
        assert "oxidize://page-sizes" in uris
        assert "oxidize://capabilities" in uris
        assert "oxidize://version" in uris
        assert "oxidize://workspace" in uris

    async def test_session_resource_template_registered(self, mcp_client):
        templates = await mcp_client.list_resource_templates()
        template_uris = {str(t.uriTemplate) for t in templates}
        assert any("session" in u for u in template_uris)


class TestAllPromptsRegistered:
    """F-056: all 5 prompts are registered."""

    pytestmark = pytest.mark.asyncio

    async def test_all_5_prompts_registered(self, mcp_client):
        prompts = await mcp_client.list_prompts()
        names = {p.name for p in prompts}
        expected = {
            "create-invoice", "extract-for-rag", "review-pdf",
            "compare-documents", "fill-form",
        }
        assert expected.issubset(names)


class TestFullInvoiceWorkflow:
    """F-060: full invoice creation workflow."""

    pytestmark = pytest.mark.asyncio

    async def test_create_add_save_workflow(self, mcp_client, mcp_workspace):
        create = await mcp_client.call_tool(
            "create_pdf", {"title": "Invoice #001", "author": "Acme Corp"}
        )
        sid = json.loads(create.content[0].text)["session_id"]

        await mcp_client.call_tool(
            "add_pdf_content",
            {
                "session_id": sid,
                "content_type": "text",
                "content": "Invoice #001",
                "x": 100.0,
                "y": 750.0,
                "font_size": 24.0,
            },
        )
        await mcp_client.call_tool(
            "add_pdf_content",
            {
                "session_id": sid,
                "content_type": "text",
                "content": "Widget x2 - $20.00",
                "x": 100.0,
                "y": 700.0,
            },
        )

        out = mcp_workspace / "invoice.pdf"
        save = await mcp_client.call_tool(
            "save_pdf", {"session_id": sid, "output_path": str(out)}
        )
        resp = json.loads(save.content[0].text)
        assert resp.get("status") == "ok"
        assert out.exists()
        assert out.read_bytes()[:5] == b"%PDF-"


class TestReadThenConvertWorkflow:
    """F-061: read then convert to markdown."""

    pytestmark = pytest.mark.asyncio

    async def test_read_then_convert(self, mcp_client, sample_pdf_with_text):
        read = await mcp_client.call_tool(
            "read_pdf", {"path": str(sample_pdf_with_text)}
        )
        meta = json.loads(read.content[0].text)
        assert meta["page_count"] >= 1

        convert = await mcp_client.call_tool(
            "convert_pdf",
            {"path": str(sample_pdf_with_text), "format": "markdown"},
        )
        out = json.loads(convert.content[0].text)
        assert isinstance(out["content"], str)


class TestSplitThenMergeWorkflow:
    """F-062: split then merge."""

    pytestmark = pytest.mark.asyncio

    async def test_split_then_merge(self, mcp_client, two_page_pdf, mcp_workspace):
        split_dir = mcp_workspace / "split"
        split_dir.mkdir()
        split = await mcp_client.call_tool(
            "manipulate_pdf",
            {
                "operation": "split",
                "input_path": str(two_page_pdf),
                "output_path": str(split_dir),
            },
        )
        assert json.loads(split.content[0].text)["status"] == "ok"

        pages = list(split_dir.glob("*.pdf"))
        assert len(pages) >= 1

        merged_out = mcp_workspace / "merged_back.pdf"
        merge = await mcp_client.call_tool(
            "manipulate_pdf",
            {
                "operation": "merge",
                "input_paths": [str(p) for p in sorted(pages)],
                "output_path": str(merged_out),
            },
        )
        assert json.loads(merge.content[0].text)["status"] == "ok"
        assert merged_out.exists()


class TestSecurityEdgeCases:
    """F-064/F-065: security enforcement on tools."""

    pytestmark = pytest.mark.asyncio

    async def test_convert_rejects_unsafe_path(self, mcp_client):
        result = await mcp_client.call_tool(
            "convert_pdf", {"path": "/etc/hosts", "format": "markdown"}
        )
        out = json.loads(result.content[0].text)
        assert out.get("code") == "SECURITY_ERROR"

    async def test_manipulate_rejects_output_outside_workspace(
        self, mcp_client, sample_pdf
    ):
        result = await mcp_client.call_tool(
            "manipulate_pdf",
            {
                "operation": "rotate",
                "input_path": str(sample_pdf),
                "output_path": "/etc/evil.pdf",
                "degrees": 90,
            },
        )
        resp = json.loads(result.content[0].text)
        assert resp.get("code") == "SECURITY_ERROR"


class TestToolDescriptions:
    """F-066: all tools have descriptions."""

    pytestmark = pytest.mark.asyncio

    async def test_all_tools_have_descriptions(self, mcp_client):
        tools = await mcp_client.list_tools()
        for tool in tools:
            assert tool.description, f"Tool {tool.name!r} has no description"
            assert len(tool.description) > 10, (
                f"Tool {tool.name!r} description too short"
            )


class TestResourceDescriptions:
    """F-067: all resources have descriptions."""

    pytestmark = pytest.mark.asyncio

    async def test_all_resources_have_descriptions(self, mcp_client):
        resources = await mcp_client.list_resources()
        for r in resources:
            assert r.description, f"Resource {r.uri!r} has no description"


class TestPromptDescriptions:
    """F-068: all prompts have descriptions."""

    pytestmark = pytest.mark.asyncio

    async def test_all_prompts_have_descriptions(self, mcp_client):
        prompts = await mcp_client.list_prompts()
        for p in prompts:
            assert p.description, f"Prompt {p.name!r} has no description"
