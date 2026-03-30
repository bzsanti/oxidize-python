"""MCP tool: extract_text — extract text content from PDF pages."""

import json

from oxidize_pdf.mcp.server import mcp


@mcp.tool()
def extract_text(
    path: str,
    page: int | None = None,
    password: str | None = None,
) -> str:
    """Extract text from a PDF file. Returns all text by default, or text from a specific page if page index is provided.

    For encrypted PDFs, provide a password to unlock before extraction.
    """
    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    resolved, err = setup_pdf_path(path)
    if err:
        return err

    try:
        # Deferred import: avoids circular import chain via server.py -> tools -> this module
        from oxidize_pdf import PdfReader

        reader = PdfReader.open(str(resolved))

        if reader.is_encrypted:
            if password:
                reader.unlock(password)
            else:
                return json.dumps({
                    "error": "PDF is encrypted. Provide a password.",
                    "code": "ENCRYPTED",
                })

        page_count = reader.page_count

        if page is not None:
            if page < 0 or page >= page_count:
                return json.dumps({
                    "error": f"Page index {page} out of range (0-{page_count - 1})",
                    "code": "INVALID_PAGE",
                })
            text = reader.extract_text_from_page(page)
            return json.dumps({"text": text, "page": page, "page_count": page_count})

        text_parts = reader.extract_text()
        full_text = "\n".join(text_parts) if isinstance(text_parts, list) else str(text_parts)
        return json.dumps({"text": full_text, "page_count": page_count})

    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})
