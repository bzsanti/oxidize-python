"""Public discovery contracts, serialized with protocol field aliases."""

import json

import pytest

pytestmark = pytest.mark.asyncio


async def test_capabilities_match_discovery(mcp_client):
    content = await mcp_client.read_resource("oxidize://capabilities")
    advertised = json.loads(content[0].text)
    tools = await mcp_client.list_tools()
    resources = await mcp_client.list_resources()
    templates = await mcp_client.list_resource_templates()
    assert set(advertised["tools"]) == {tool.name for tool in tools}
    assert set(advertised["resources"]) == {
        *(str(resource.uri) for resource in resources),
        *(template.model_dump(by_alias=True)["uriTemplate"] for template in templates),
    }
    assert len(resources) == 5
    assert len(templates) == 1


async def test_prompt_arguments_are_preserved(mcp_client):
    prompts = await mcp_client.list_prompts()
    assert {
        prompt.name: {arg.name: bool(arg.required) for arg in prompt.arguments or []}
        for prompt in prompts
    } == {
        "create-invoice": {"company": True, "items": True},
        "extract-for-rag": {"path": True, "chunk_size": False},
        "review-pdf": {"path": True},
        "compare-documents": {"path1": True, "path2": True},
        "fill-form": {"form_path": True, "context": True},
    }


async def test_read_pdf_wire_schema_and_defaults(mcp_client):
    tools = {tool.name: tool.model_dump(by_alias=True) for tool in await mcp_client.list_tools()}
    tool = tools["read_pdf"]
    schema = tool["inputSchema"]
    assert schema["required"] == ["path"]
    assert schema["properties"]["include_page_details"]["default"] is False
    assert schema["properties"]["password"]["default"] is None
    assert tool["annotations"]["readOnlyHint"] is True
    assert tool["annotations"]["openWorldHint"] is False
