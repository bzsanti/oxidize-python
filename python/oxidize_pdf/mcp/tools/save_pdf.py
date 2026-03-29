"""MCP tool: save_pdf — finalize a PDF creation session and save to file."""

import json

from oxidize_pdf.mcp.server import mcp


@mcp.tool()
def save_pdf(
    session_id: str,
    output_path: str,
    user_password: str | None = None,
    owner_password: str | None = None,
) -> str:
    """Save an active PDF creation session to a file.

    Builds a Document from the session's accumulated content and writes it to output_path.
    The session is marked as completed after saving.
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

        session["status"] = "completed"
        store.update(session_id, session)

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

    dims = session.get("page_dimensions", (595.28, 841.89))
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
