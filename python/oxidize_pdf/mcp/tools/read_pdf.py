"""MCP tool: read_pdf — read PDF metadata and structure."""

import json

from oxidize_pdf.mcp.server import mcp


@mcp.tool()
def read_pdf(
    path: str,
    password: str | None = None,
    include_page_details: bool = False,
) -> str:
    """Read a PDF file and return its metadata: page count, encryption status, version, title, author, subject, and keywords.

    Optionally include per-page details (dimensions, rotation) with include_page_details=True.
    For encrypted PDFs, provide a password to unlock and read full metadata.
    """
    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    resolved, err = setup_pdf_path(path)
    if err:
        return err

    try:
        # Deferred import: PdfReader is imported here (not at module level) to avoid
        # a circular import chain: server.py -> tools/__init__.py -> this module -> server.py
        from oxidize_pdf import PdfReader

        reader = PdfReader.open(str(resolved))

        is_encrypted = reader.is_encrypted

        if is_encrypted and password:
            reader.unlock(password)
        elif is_encrypted:
            return json.dumps({
                "path": path,
                "is_encrypted": True,
                "locked": True,
                "message": "PDF is encrypted. Provide a password to read metadata.",
            })

        meta = reader.metadata()

        result = {
            "path": path,
            "page_count": meta.page_count,
            "is_encrypted": is_encrypted,
            "version": meta.version,
            "title": meta.title,
            "author": meta.author,
            "subject": meta.subject,
            "keywords": meta.keywords,
        }

        if include_page_details:
            pages = []
            for i in range(meta.page_count):
                page = reader.get_page(i)
                pages.append({
                    "index": i,
                    "width": page.width,
                    "height": page.height,
                    "rotation": page.rotation,
                })
            result["pages"] = pages

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})
