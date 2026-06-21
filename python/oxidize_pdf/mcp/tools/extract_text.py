"""MCP tool: extract_text — extract text content from PDF pages."""

import json
from typing import Annotated, Optional

from mcp.types import ToolAnnotations
from pydantic import Field

from oxidize_pdf.mcp.server import mcp


@mcp.tool(
    annotations=ToolAnnotations(
        title="Extract plain text",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=False,
    )
)
def extract_text(
    path: Annotated[
        str,
        Field(description="Path to the PDF file, relative to the configured workspace."),
    ],
    page: Optional[int] = Field(
        default=None,
        description="0-based page index to extract. Omit to extract every "
        "page joined by newlines. Out-of-range indices return an error.",
    ),
    password: Optional[str] = Field(
        default=None,
        description="User password to unlock an encrypted PDF before extraction.",
    ),
) -> str:
    """Extract the raw, unformatted text of a PDF as a single string.

    Returns JSON {text, page_count} (plus `page` when a specific page was
    requested). Read-only.

    Use this when you want the plain reading text. If you need Markdown
    structure or chunking for LLM/RAG pipelines use convert_pdf; if you need
    each text run with its on-page coordinates and font use extract_entities.
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
