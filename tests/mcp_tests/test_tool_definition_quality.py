"""Tool Definition Quality contract for every MCP tool.

These tests assert the concrete schema surface that Glama's Tool Definition
Quality Score (TDQS) evaluates and that MCP agents consume at selection time:

- Parameter Semantics: every input parameter carries a non-tautological
  description in the generated JSON schema.
- Behavioral Transparency: every tool declares MCP annotations
  (readOnlyHint, openWorldHint, title) so a client knows the side effects
  without executing the tool.
- Purpose / Usage / Completeness: the tool description is substantive and
  (for tools with siblings) cross-references the alternative tool.
- Typed enums: free-form mode parameters are exposed as JSON-schema enums
  (Literal), not opaque strings.

This validates real generated content (descriptions, annotations, enums),
not merely that the server starts — it is a behavior contract, not a smoke
test. It reads the same wire-level Tool objects a client receives.
"""

import pytest

pytestmark = pytest.mark.asyncio

# Every tool the server exposes.
ALL_TOOLS = {
    "read_pdf",
    "extract_text",
    "extract_entities",
    "convert_pdf",
    "analyze_pdf",
    "manipulate_pdf",
    "annotate_pdf",
    "manage_forms",
    "secure_pdf",
    "create_pdf",
    "add_pdf_content",
    "save_pdf",
}

# Tools that neither write files nor mutate server state.
READ_ONLY_TOOLS = {
    "read_pdf",
    "extract_text",
    "extract_entities",
    "convert_pdf",
    "analyze_pdf",
}

WRITE_TOOLS = ALL_TOOLS - READ_ONLY_TOOLS

# Free-form mode parameters that must be typed as Literal enums (layer 4).
ENUM_PARAMS = {
    "manipulate_pdf": "operation",
    "analyze_pdf": "check",
    "secure_pdf": "operation",
    "manage_forms": "operation",
    "add_pdf_content": "content_type",
    "create_pdf": "page_size",
    "annotate_pdf": "annotation_type",
    "convert_pdf": "format",
}

# Tools whose purpose overlaps a sibling: the description must name the
# alternative so an agent can disambiguate (Purpose Clarity 5/5).
SIBLING_CROSS_REFERENCES = {
    "extract_text": ("convert_pdf", "extract_entities"),
    "convert_pdf": ("extract_text",),
    "extract_entities": ("extract_text",),
    "read_pdf": ("analyze_pdf",),
    "analyze_pdf": ("read_pdf",),
}


async def _tools_by_name(mcp_client):
    tools = await mcp_client.list_tools()
    return {t.name: t for t in tools}


async def test_all_expected_tools_present(mcp_client):
    tools = await _tools_by_name(mcp_client)
    assert set(tools) == ALL_TOOLS


@pytest.mark.parametrize("name", sorted(ALL_TOOLS))
async def test_description_is_substantive(mcp_client, name):
    tools = await _tools_by_name(mcp_client)
    desc = (tools[name].description or "").strip()
    # Purpose + Usage + Behavior cannot fit in a single short sentence.
    assert len(desc) >= 120, f"{name}: description too thin ({len(desc)} chars)"


@pytest.mark.parametrize("name", sorted(ALL_TOOLS))
async def test_every_parameter_has_a_description(mcp_client, name):
    tools = await _tools_by_name(mcp_client)
    props = (tools[name].inputSchema or {}).get("properties", {})
    assert props, f"{name}: no parameters in schema"
    for pname, pschema in props.items():
        desc = (pschema.get("description") or "").strip()
        assert desc, f"{name}.{pname}: missing parameter description"
        assert desc.lower() != pname.lower().replace("_", " "), (
            f"{name}.{pname}: description merely restates the name"
        )
        assert len(desc) >= 12, f"{name}.{pname}: description too short"


@pytest.mark.parametrize("name", sorted(ALL_TOOLS))
async def test_tool_declares_annotations(mcp_client, name):
    tools = await _tools_by_name(mcp_client)
    ann = tools[name].annotations
    assert ann is not None, f"{name}: no annotations declared"
    assert ann.title, f"{name}: annotation title missing"
    assert isinstance(ann.readOnlyHint, bool), f"{name}: readOnlyHint not set"
    # All tools operate on the local filesystem/session, never the open world.
    assert ann.openWorldHint is False, f"{name}: openWorldHint should be False"


@pytest.mark.parametrize("name", sorted(READ_ONLY_TOOLS))
async def test_read_only_tools_marked_read_only(mcp_client, name):
    tools = await _tools_by_name(mcp_client)
    assert tools[name].annotations.readOnlyHint is True


@pytest.mark.parametrize("name", sorted(WRITE_TOOLS))
async def test_write_tools_not_marked_read_only(mcp_client, name):
    tools = await _tools_by_name(mcp_client)
    assert tools[name].annotations.readOnlyHint is False


@pytest.mark.parametrize("name,param", sorted(ENUM_PARAMS.items()))
async def test_mode_parameters_are_typed_enums(mcp_client, name, param):
    tools = await _tools_by_name(mcp_client)
    props = (tools[name].inputSchema or {}).get("properties", {})
    assert param in props, f"{name}.{param}: parameter missing"
    assert props[param].get("enum"), f"{name}.{param}: should be a Literal/enum"


@pytest.mark.parametrize("name,siblings", sorted(SIBLING_CROSS_REFERENCES.items()))
async def test_overlapping_tools_cross_reference_siblings(mcp_client, name, siblings):
    tools = await _tools_by_name(mcp_client)
    desc = (tools[name].description or "").lower()
    assert any(sib in desc for sib in siblings), (
        f"{name}: description should name an alternative tool ({siblings})"
    )
