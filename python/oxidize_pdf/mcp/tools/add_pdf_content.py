"""MCP tool: add_pdf_content — add content to a PDF creation session."""

import json
from typing import Annotated, Literal, Optional

from mcp.types import ToolAnnotations
from pydantic import Field

from oxidize_pdf.mcp.server import mcp

# #115 Capa A: nominal in-memory cost charged per appended page, so that
# new_page spam is bounded by the per-session content cap even though an empty
# page carries no text bytes.
_PAGE_COST_BYTES = 256


@mcp.tool(
    annotations=ToolAnnotations(
        title="Add content to a PDF session",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    )
)
def add_pdf_content(
    session_id: Annotated[
        str,
        Field(description="Session id returned by create_pdf. Must be active."),
    ],
    content_type: Annotated[
        Literal["text", "new_page"],
        Field(
            description="'text' draws a text string at (x, y) on the current "
            "page; 'new_page' appends a blank page and makes it current."
        ),
    ],
    content: Optional[str] = Field(
        default=None,
        description="Text to draw. Required when content_type='text'.",
    ),
    x: Optional[float] = Field(
        default=None,
        description="Horizontal position in PDF points from the left edge. "
        "Required when content_type='text'.",
    ),
    y: Optional[float] = Field(
        default=None,
        description="Vertical position in PDF points from the bottom edge "
        "(origin is bottom-left). Required when content_type='text'.",
    ),
    font: Optional[str] = Field(
        default=None,
        description="Font name (e.g. 'Helvetica', 'Courier', 'Times-Roman'). "
        "Defaults to Helvetica when omitted.",
    ),
    font_size: Annotated[
        float,
        Field(description="Font size in points for text content."),
    ] = 12.0,
) -> str:
    """Append text or a new page to an open create_pdf session (step 2 of 3).

    Mutates the in-memory session; nothing is written to disk until save_pdf.
    Returns JSON {status, session_id, page_count} on success, or {error, code}
    if the session is missing/inactive or required text fields are absent.
    Coordinates use PDF points with the origin at the bottom-left of the page.

    Call repeatedly to build up pages, then call save_pdf. This only works on a
    session from create_pdf — to add notes/highlights to an existing PDF file
    use annotate_pdf instead.
    """
    from oxidize_pdf.mcp.tools.base import enforce_session_byte_limit, get_session_store

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
    current_bytes = session.get("content_bytes", 0)

    if content_type == "text":
        if content is None or x is None or y is None:
            return json.dumps({
                "error": "content, x, and y are required for text content.",
                "code": "MISSING_PARAM",
            })
        # #115 Capa A: bound per-session memory before appending.
        projected = current_bytes + len(content.encode("utf-8"))
        if limit_err := enforce_session_byte_limit(projected):
            return limit_err
        pages[-1].append({
            "type": "text",
            "content": content,
            "x": x,
            "y": y,
            "font": font,
            "font_size": font_size,
        })
        session["content_bytes"] = projected
        return json.dumps({
            "status": "ok",
            "session_id": session_id,
            "page_count": len(pages),
        })

    # content_type == "new_page" (the Literal type guarantees no other value)
    projected = current_bytes + _PAGE_COST_BYTES
    if limit_err := enforce_session_byte_limit(projected):
        return limit_err
    pages.append([])
    session["content_bytes"] = projected
    return json.dumps({
        "status": "ok",
        "session_id": session_id,
        "page_count": len(pages),
    })
