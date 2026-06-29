"""Use the oxidize-pdf MCP server from the OpenAI Agents SDK.

The oxidize-pdf package installs an ``oxidize-mcp`` command that speaks the
Model Context Protocol over stdio. The OpenAI Agents SDK can spawn it directly
via ``MCPServerStdio`` and expose all 12 PDF tools to an agent.

Run it:

    pip install oxidize-pdf openai-agents
    export OPENAI_API_KEY=sk-...            # only needed for the agent turn
    python examples/openai_agents_quickstart.py

Without ``OPENAI_API_KEY`` the script still connects to the MCP server and lists
the available tools, so you can verify the integration end to end offline.

Docs: https://openai.github.io/openai-agents-python/mcp/
"""

import asyncio
import os
import tempfile
from pathlib import Path


def _make_sample_pdf(workspace: Path) -> Path:
    """Create a small PDF inside the workspace so the example is self-contained."""
    from oxidize_pdf import Document, Font, Page

    doc = Document()
    doc.set_title("Quarterly Report")
    doc.set_author("oxidize-pdf")
    page = Page.a4()
    page.set_font(Font.HELVETICA, 14.0)
    page.text_at(72.0, 760.0, "Quarterly Report")
    page.set_font(Font.HELVETICA, 11.0)
    page.text_at(72.0, 720.0, "Revenue grew 18% quarter over quarter.")
    doc.add_page(page)

    path = workspace / "report.pdf"
    doc.save(str(path))
    return path


async def main() -> None:
    from agents.mcp import MCPServerStdio

    # The MCP server is sandboxed to OXIDIZE_WORKSPACE; only files under it are
    # reachable by the tools. Point it at the directory holding your PDFs.
    workspace = Path(tempfile.mkdtemp(prefix="oxidize-agents-"))
    _make_sample_pdf(workspace)

    async with MCPServerStdio(
        params={
            "command": "oxidize-mcp",
            "env": {**os.environ, "OXIDIZE_WORKSPACE": str(workspace)},
        },
        cache_tools_list=True,
        client_session_timeout_seconds=30,
    ) as server:
        tools = await server.list_tools()
        print(f"Connected to oxidize-mcp — {len(tools)} tools available:")
        for tool in sorted(tools, key=lambda t: t.name):
            print(f"  - {tool.name}")

        if not os.environ.get("OPENAI_API_KEY"):
            print("\nSet OPENAI_API_KEY to run the agent turn below.")
            return

        from agents import Agent, Runner

        agent = Agent(
            name="PDF assistant",
            instructions=(
                "You inspect and manipulate PDF files using the oxidize-pdf "
                "tools. Refer to files by their name within the workspace."
            ),
            mcp_servers=[server],
        )
        result = await Runner.run(
            agent,
            "How many pages does report.pdf have, and what is its title?",
        )
        print("\nAgent:", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
