"""MCP tool: save_pdf — finalize a PDF creation session and save to file."""

import json
from typing import Annotated, Optional

from mcp.types import ToolAnnotations
from pydantic import Field

from oxidize_pdf.mcp.server import mcp


@mcp.tool(
    annotations=ToolAnnotations(
        title="Save and close a PDF session",
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=False,
    )
)
def save_pdf(
    session_id: Annotated[
        str,
        Field(description="Session id returned by create_pdf to finalize."),
    ],
    output_path: Annotated[
        str,
        Field(
            description="Destination .pdf path inside the workspace. An existing "
            "file at this path is overwritten."
        ),
    ],
    user_password: Optional[str] = Field(
        default=None,
        description="If set together with owner_password, the saved PDF is "
        "encrypted; this is the password required to open it.",
    ),
    owner_password: Optional[str] = Field(
        default=None,
        description="Owner/permissions password. Encryption is applied only "
        "when both user_password and owner_password are provided.",
    ),
) -> str:
    """Render an open create_pdf session to a PDF file (step 3 of 3, terminal).

    Builds a Document from the session's accumulated pages, writes it to
    output_path (overwriting any existing file), then deletes the session — so
    the session_id is no longer usable afterwards. Returns JSON {status, path,
    page_count}, or {error, code} if the session is missing.

    Only finalizes sessions created via create_pdf/add_pdf_content. To encrypt an
    already-saved PDF use secure_pdf; to add annotations use annotate_pdf.
    """
    from oxidize_pdf.mcp.tools.base import get_session_store, setup_output_path

    store = get_session_store()
    session = store.get(session_id)

    if session is None:
        return json.dumps({
            "error": "Session not found.",
            "code": "SESSION_NOT_FOUND",
        })

    resolved, err = setup_output_path(output_path)
    if err:
        return err

    try:
        doc = _build_document(session)
        if user_password and owner_password:
            doc.encrypt(user_password, owner_password)
        doc.save(str(resolved))

        store.delete(session_id)

        return json.dumps({
            "status": "ok",
            "path": output_path,
            "page_count": doc.page_count,
        })
    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})


def _build_document(session: dict) -> "Document":
    """Reconstruct a Document from session page descriptors."""
    from oxidize_pdf import Document, Font, Page

    doc = Document()
    title = session.get("title")
    author = session.get("author")
    if title:
        doc.set_title(title)
    if author:
        doc.set_author(author)

    from oxidize_pdf.mcp.tools.base import PAGE_SIZES

    default_dims = PAGE_SIZES["a4"]
    dims = session.get("page_dimensions", (default_dims["width"], default_dims["height"]))
    pages = session.get("pages", [[]])

    for page_contents in pages:
        page = Page(dims[0], dims[1])
        page.set_font(Font.HELVETICA, 12.0)

        for item in page_contents:
            if item["type"] == "text":
                font_name = item.get("font")
                font_size = item.get("font_size", 12.0)
                font_obj = Font.HELVETICA
                if font_name:
                    font_obj = getattr(Font, font_name.upper(), Font.HELVETICA)
                page.set_font(font_obj, font_size)
                page.text_at(item["x"], item["y"], item["content"])

        doc.add_page(page)

    return doc
