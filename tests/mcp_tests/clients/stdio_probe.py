"""Real SDK v1/v2 interoperability probe; runs outside the server environment."""

import asyncio
import json
import os
import sys
from importlib.metadata import version

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def wire(model):
    return model.model_dump(by_alias=True)


async def exercise(client):
    tools = wire(await client.list_tools())["tools"]
    assert {t["name"] for t in tools} == {
        "read_pdf", "extract_text", "convert_pdf", "analyze_pdf",
        "extract_entities", "manipulate_pdf", "annotate_pdf", "manage_forms",
        "secure_pdf", "create_pdf", "add_pdf_content", "save_pdf",
    }
    read = next(t for t in tools if t["name"] == "read_pdf")
    assert read["annotations"]["readOnlyHint"] is True
    assert read["inputSchema"]["required"] == ["path"]
    assert len(wire(await client.list_resources())["resources"]) == 5
    assert wire(await client.list_resource_templates())["resourceTemplates"][0]["uriTemplate"] == "oxidize://session/{session_id}"
    assert len(wire(await client.list_prompts())["prompts"]) == 5
    prompt = wire(await client.get_prompt("review-pdf", {"path": "probe.pdf"}))
    assert "probe.pdf" in prompt["messages"][0]["content"]["text"]

    async def call(name, args):
        result = wire(await client.call_tool(name, args))
        assert not result.get("isError"), result
        return json.loads(result["content"][0]["text"])

    first = await call("create_pdf", {"title": "First"})
    second = await call("create_pdf", {"title": "Second"})
    assert first["session_id"] != second["session_id"]
    sid = first["session_id"]
    await call("add_pdf_content", {
        "session_id": sid, "content_type": "text", "content": "MCP migration proof",
        "x": 50, "y": 700,
    })
    saved = await call("save_pdf", {"session_id": sid, "output_path": "probe.pdf"})
    assert saved.get("status") == "ok", saved
    metadata = await call("read_pdf", {"path": "probe.pdf"})
    assert metadata["title"] == "First"
    assert metadata["page_count"] == 1
    extracted = await call("extract_text", {"path": "probe.pdf"})
    assert "MCP migration proof" in extracted["text"]
    resource = wire(await client.read_resource("oxidize://session/" + second["session_id"]))
    assert json.loads(resource["contents"][0]["text"])["title"] == "Second"
    assert (await call("save_pdf", {"session_id": sid, "output_path": "again.pdf"}))["code"] == "SESSION_NOT_FOUND"
    for path in ["missing.pdf", "../outside.pdf"]:
        assert (await call("read_pdf", {"path": path}))["code"] == "SECURITY_ERROR"
    # Validation failures are tool errors, not the application's JSON error body.
    invalid = wire(await client.call_tool("read_pdf", {}))
    assert invalid["isError"] is True
    # Unknown tool is a JSON-RPC error or tool error according to the protocol era.
    try:
        unknown = wire(await client.call_tool("nonexistent_tool", {}))
    except Exception as exc:
        error = getattr(exc, "error", None)
        assert error is not None and error.code == -32602, repr(exc)
    else:
        assert unknown["isError"] is True


async def main():
    server_python, launch, workspace = sys.argv[1:]
    command = server_python
    args = ["-m", "oxidize_pdf.mcp.server"]
    if launch == "entrypoint":
        from pathlib import Path
        command = str(Path(server_python).with_name("oxidize-mcp.exe" if os.name == "nt" else "oxidize-mcp"))
        args = []
    elif launch == "launcher":
        command, args = "bash", [os.environ["OXIDIZE_TEST_LAUNCHER"], "serve"]
    elif launch == "registry":
        with open(os.environ["OXIDIZE_TEST_MANIFEST"]) as manifest:
            package = json.load(manifest)["packages"][0]
        command = package["runtimeHint"]
        args = []
        for arg in package["runtimeArguments"] + package["packageArguments"]:
            if arg["type"] == "named":
                args.append(arg["name"])
            args.append(arg["value"])
    params = StdioServerParameters(command=command, args=args, cwd=workspace, env={**os.environ, "OXIDIZE_WORKSPACE": workspace})
    if version("mcp").split(".")[0] == "1":
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as client:
                initialized = await client.initialize()
                assert initialized.protocolVersion == "2025-11-25"
                await exercise(client)
        protocol = "2025-11-25"
    else:
        from mcp import Client
        async with Client(params, read_timeout_seconds=15) as client:
            assert client.protocol_version == "2026-07-28"
            await exercise(client)
            protocol = client.protocol_version
    print(json.dumps({"sdk": version("mcp"), "protocol": protocol, "workflow": "passed"}))


if __name__ == "__main__":
    asyncio.run(asyncio.wait_for(main(), timeout=45))
