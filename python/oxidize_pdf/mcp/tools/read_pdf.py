"""MCP tool: read_pdf — read PDF metadata and structure."""

import json
from typing import Annotated

from mcp.types import ToolAnnotations
from pydantic import Field

from oxidize_pdf.mcp.server import mcp


@mcp.tool(
    annotations=ToolAnnotations(
        title="Read PDF metadata",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=False,
    )
)
def read_pdf(
    path: Annotated[
        str,
        Field(description="Path to the PDF file, relative to the configured workspace."),
    ],
    password: Annotated[
        str | None,
        Field(
            description="User password to unlock an encrypted PDF. Omit for "
            "unencrypted files; if omitted on an encrypted file the tool reports "
            "it as locked instead of failing."
        ),
    ] = None,
    include_page_details: Annotated[
        bool,
        Field(
            description="When true, also return per-page width, height (in PDF "
            "points) and rotation. Off by default to keep the response small."
        ),
    ] = False,
) -> str:
    """Read a single PDF's document-level metadata without parsing its content.

    Returns a JSON object with: page_count, is_encrypted, version, title,
    author, subject, keywords, and (when include_page_details=true) a `pages`
    array of {index, width, height, rotation}. Read-only: never modifies the
    file.

    Use this to inspect what a PDF is before deciding how to process it. For
    structural validation, corruption/PDF-A checks, or comparing two files use
    analyze_pdf instead; for the actual text use extract_text. Encrypted files
    without a password return {is_encrypted, locked, message} rather than
    metadata.
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
