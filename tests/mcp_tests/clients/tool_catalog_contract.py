"""Independent consumer contract for tools/list; no server or SDK imports."""

EXPECTED_TOOLS = {
    "read_pdf", "extract_text", "convert_pdf", "analyze_pdf",
    "extract_entities", "manipulate_pdf", "annotate_pdf", "manage_forms",
    "secure_pdf", "create_pdf", "add_pdf_content", "save_pdf",
}


def assert_tool_catalog(tools):
    """Reject empty/incomplete catalogs and metadata lost during serialization."""
    names = [tool["name"] for tool in tools]
    assert set(names) == EXPECTED_TOOLS, f"Unexpected tool catalog: {names}"
    assert len(names) == len(set(names)), f"Duplicate tools: {names}"
    for tool in tools:
        name = tool["name"]
        description = (tool.get("description") or "").strip()
        assert len(description) >= 120, f"{name}: missing/substantive tool description required"
        properties = tool.get("inputSchema", {}).get("properties", {})
        assert properties, f"{name}: missing input parameters"
        for parameter, schema in properties.items():
            description = (schema.get("description") or "").strip()
            assert len(description) >= 12, f"{name}.{parameter}: missing parameter description"
            assert description.lower() != parameter.lower().replace("_", " "), (
                f"{name}.{parameter}: description only repeats parameter name"
            )
