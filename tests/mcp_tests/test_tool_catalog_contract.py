"""Mutate real discovery payloads to prove CI rejects the reported regressions."""

from copy import deepcopy

import pytest

from .clients.tool_catalog_contract import assert_tool_catalog


@pytest.mark.asyncio
@pytest.mark.parametrize("mutation, diagnostic", [
    ("empty", "Unexpected tool catalog"),
    ("missing_tool", "Unexpected tool catalog"),
    ("duplicate", "Duplicate tools"),
    ("missing_description", "tool description required"),
    ("blank_description", "tool description required"),
    ("missing_parameters", "missing input parameters"),
    ("missing_parameter_description", "missing parameter description"),
    ("blank_parameter_description", "missing parameter description"),
])
async def test_catalog_contract_rejects_metadata_regressions(mcp_client, mutation, diagnostic):
    tools = [tool.model_dump(by_alias=True) for tool in await mcp_client.list_tools()]
    assert_tool_catalog(tools)
    broken = deepcopy(tools)
    if mutation == "empty":
        broken.clear()
    elif mutation == "missing_tool":
        broken.pop()
    elif mutation == "duplicate":
        broken.append(deepcopy(broken[0]))
    elif mutation == "missing_description":
        del broken[0]["description"]
    elif mutation == "blank_description":
        broken[0]["description"] = " " * 120
    elif mutation == "missing_parameters":
        broken[0]["inputSchema"]["properties"] = {}
    else:
        parameter = next(iter(broken[0]["inputSchema"]["properties"].values()))
        if mutation == "missing_parameter_description":
            del parameter["description"]
        else:
            parameter["description"] = " " * 12
    with pytest.raises(AssertionError, match=diagnostic):
        assert_tool_catalog(broken)
