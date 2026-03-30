"""MCP tool: add_pdf_content — add content to a PDF creation session."""

import json

from oxidize_pdf.mcp.server import mcp


@mcp.tool()
def add_pdf_content(
    session_id: str,
    content_type: str,
    content: str | None = None,
    x: float | None = None,
    y: float | None = None,
    font: str | None = None,
    font_size: float = 12.0,
) -> str:
    """Add content to an active PDF creation session.

    Content types:
    - text: Add text at position (x, y). Requires content, x, y.
    - new_page: Add a new blank page to the session.
    """
    from oxidize_pdf.mcp.tools.base import get_session_store

    store = get_session_store()
    session = store.get(session_id)

    if session is None:
        return json.dumps({
            "error": "Session not found.",
            "code": "SESSION_NOT_FOUND",
        })

    if session.get("status") != "active":
        return json.dumps({
            "error": "Session is not active.",
            "code": "SESSION_INACTIVE",
        })

    pages = session["pages"]

    if content_type == "text":
        if content is None or x is None or y is None:
            return json.dumps({
                "error": "content, x, and y are required for text content.",
                "code": "MISSING_PARAM",
            })
        pages[-1].append({
            "type": "text",
            "content": content,
            "x": x,
            "y": y,
            "font": font,
            "font_size": font_size,
        })
        return json.dumps({
            "status": "ok",
            "session_id": session_id,
            "page_count": len(pages),
        })

    elif content_type == "new_page":
        pages.append([])
        return json.dumps({
            "status": "ok",
            "session_id": session_id,
            "page_count": len(pages),
        })

    else:
        return json.dumps({
            "error": f"Unknown content type: '{content_type}'.",
            "code": "INVALID_TYPE",
        })
