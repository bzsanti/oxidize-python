"""MCP tool: create_pdf — start a stateful PDF creation session."""

import json
from typing import Annotated, Literal, Optional

from mcp.types import ToolAnnotations
from pydantic import Field

from oxidize_pdf.mcp.server import mcp


@mcp.tool(
    annotations=ToolAnnotations(
        title="Start a PDF creation session",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    )
)
def create_pdf(
    title: Annotated[
        str,
        Field(description="Document title; stored in the PDF metadata on save."),
    ],
    author: Optional[str] = Field(
        default=None,
        description="Document author; stored in the PDF metadata on save.",
    ),
    page_size: Annotated[
        Literal[
            "a4", "a4_landscape", "letter", "letter_landscape",
            "legal", "legal_landscape",
        ],
        Field(description="Page size for every page in this document."),
    ] = "a4",
) -> str:
    """Open an in-memory PDF building session; the first step of authoring a PDF.

    Returns JSON {session_id, status, page_size}. No file is written here — this
    only allocates a session (with one blank starting page) held in server
    memory and subject to a TTL. Not idempotent: each call creates a new session.

    Workflow: create_pdf → add_pdf_content (text / new pages, repeatable) →
    save_pdf (writes the file and closes the session). To annotate or fill an
    existing PDF instead of authoring one, use annotate_pdf or manage_forms.
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
