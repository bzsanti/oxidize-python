"""FastMCP server definition for oxidize-pdf."""

import json

from fastmcp import FastMCP

MCP_SERVER_VERSION = "1.0.0"

mcp = FastMCP(name="oxidize-pdf")

# Tool and prompt modules must be imported after mcp is defined, because their
# decorators (@mcp.tool(), @mcp.prompt()) reference the mcp instance at import time.
import oxidize_pdf.mcp.tools  # noqa: E402, F401
import oxidize_pdf.mcp.prompts  # noqa: E402, F401


@mcp.resource("oxidize://fonts")
def get_fonts() -> str:
    """List available built-in PDF fonts."""
    from oxidize_pdf import Font

    font_names = [name for name in dir(Font) if not name.startswith("_") and name.isupper()]
    return json.dumps([name.replace("_", "-").title() for name in font_names])


@mcp.resource("oxidize://page-sizes")
def get_page_sizes() -> str:
    """List available page sizes with dimensions in points."""
    from oxidize_pdf.mcp.tools.base import PAGE_SIZES

    return json.dumps(PAGE_SIZES)


@mcp.resource("oxidize://capabilities")
def get_capabilities() -> str:
    """List server capabilities: available tools, version, features."""
    return json.dumps({
        "tools": [
            "read_pdf", "extract_text", "convert_pdf", "analyze_pdf",
            "extract_entities", "manipulate_pdf", "annotate_pdf",
            "manage_forms", "secure_pdf", "create_pdf",
            "add_pdf_content", "save_pdf",
        ],
        "resources": [
            "oxidize://fonts", "oxidize://page-sizes",
            "oxidize://capabilities", "oxidize://version",
            "oxidize://workspace", "oxidize://session/{id}",
        ],
        "version": MCP_SERVER_VERSION,
        "features": ["stateless-tools", "stateful-sessions", "pdf-analysis", "pdf-creation"],
    })


@mcp.resource("oxidize://version")
def get_version() -> str:
    """Return version information for oxidize-pdf and the MCP server."""
    import oxidize_pdf

    version = getattr(oxidize_pdf, "__version__", "unknown")
    return json.dumps({
        "oxidize_pdf": version,
        "mcp_server": MCP_SERVER_VERSION,
    })


@mcp.resource("oxidize://workspace")
def get_workspace() -> str:
    """List PDF files in the configured workspace directory."""
    from oxidize_pdf.mcp.tools.base import get_config

    cfg = get_config()
    workspace = cfg.workspace_dir
    files = []
    if workspace.exists():
        for f in sorted(workspace.iterdir()):
            if f.suffix.lower() == ".pdf" and f.is_file():
                files.append({"name": f.name, "size": f.stat().st_size})

    return json.dumps({
        "workspace_dir": str(workspace),
        "files": files,
    })


@mcp.resource("oxidize://session/{session_id}")
def get_session(session_id: str) -> str:
    """Read session data by ID."""
    from oxidize_pdf.mcp.tools.base import get_session_store

    store = get_session_store()
    session = store.get(session_id)
    if session is None:
        return json.dumps(None)
    return json.dumps({
        "session_id": session_id,
        "title": session.get("title"),
        "status": session.get("status"),
        "page_count": len(session.get("pages", [])),
    })


def run() -> None:
    """Entry point for the oxidize-mcp command."""
    mcp.run()


if __name__ == "__main__":
    run()
