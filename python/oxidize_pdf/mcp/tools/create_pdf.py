"""MCP tool: create_pdf — start a stateful PDF creation session."""

import json

from oxidize_pdf.mcp.server import mcp


@mcp.tool()
def create_pdf(
    title: str,
    author: str | None = None,
    page_size: str = "a4",
) -> str:
    """Create a new PDF creation session.

    Returns a session_id that can be used with add_pdf_content and save_pdf.
    The first page is created automatically.
    """
    from oxidize_pdf.mcp.tools.base import PAGE_SIZES, get_session_store

    store = get_session_store()

    size_info = PAGE_SIZES.get(page_size.lower(), PAGE_SIZES["a4"])
    dims = (size_info["width"], size_info["height"])

    try:
        session_id = store.create({
            "title": title,
            "author": author,
            "page_size": page_size,
            "page_dimensions": dims,
            "status": "active",
            "pages": [[]],
        })
    except Exception as e:
        return json.dumps({"error": str(e), "code": "SESSION_ERROR"})

    return json.dumps({
        "session_id": session_id,
        "status": "created",
        "page_size": page_size,
    })
