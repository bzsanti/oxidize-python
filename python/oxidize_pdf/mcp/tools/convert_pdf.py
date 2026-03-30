"""MCP tool: convert_pdf — convert PDF to markdown, chunks, or RAG format."""

import json
from typing import Literal

from oxidize_pdf.mcp.server import mcp


@mcp.tool()
def convert_pdf(
    path: str,
    format: Literal["markdown", "chunks", "rag"],
    password: str | None = None,
    max_tokens: int = 256,
    overlap: int = 50,
) -> str:
    """Convert a PDF to a different text representation.

    Supported formats:
    - "markdown": Convert to a structured markdown document.
    - "chunks": Split into token-limited chunks for LLM consumption.
    - "rag": Split into semantic chunks optimized for RAG pipelines.
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

        if format == "markdown":
            content = reader.to_markdown()
            return json.dumps({"content": content, "format": "markdown"})

        if format == "chunks":
            doc_chunks = reader.chunk(max_tokens, overlap)
            chunks = [
                {
                    "id": c.id,
                    "content": c.content,
                    "tokens": c.tokens,
                    "chunk_index": c.chunk_index,
                    "page_numbers": c.page_numbers,
                }
                for c in doc_chunks
            ]
            return json.dumps({"chunks": chunks, "format": "chunks"})

        if format == "rag":
            rag_chunks = reader.rag_chunks()
            chunks = [
                {
                    "text": c.text,
                    "chunk_index": c.chunk_index,
                    "page_numbers": c.page_numbers,
                    "token_estimate": c.token_estimate,
                    "heading_context": c.heading_context,
                }
                for c in rag_chunks
            ]
            return json.dumps({"chunks": chunks, "format": "rag"})

        return json.dumps({
            "error": f"Unknown format: {format}. Use 'markdown', 'chunks', or 'rag'.",
            "code": "INVALID_FORMAT",
        })

    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})
