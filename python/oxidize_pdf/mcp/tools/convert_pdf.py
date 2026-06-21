"""MCP tool: convert_pdf — convert PDF to markdown, chunks, or RAG format."""

import json
from typing import Annotated, Literal

from mcp.types import ToolAnnotations
from pydantic import Field

from oxidize_pdf.mcp.server import mcp


@mcp.tool(
    annotations=ToolAnnotations(
        title="Convert PDF to text representation",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=False,
    )
)
def convert_pdf(
    path: Annotated[
        str,
        Field(description="Path to the PDF file, relative to the configured workspace."),
    ],
    format: Annotated[
        Literal["markdown", "chunks", "rag"],
        Field(
            description="Output representation: 'markdown' = one structured "
            "Markdown document; 'chunks' = fixed-size token windows; 'rag' = "
            "heading-aware semantic chunks for retrieval pipelines."
        ),
    ],
    password: Annotated[
        str | None,
        Field(description="User password to unlock an encrypted PDF before conversion."),
    ] = None,
    max_tokens: Annotated[
        int,
        Field(
            description="Target maximum tokens per chunk. Applies to "
            "format='chunks' and 'rag' only; ignored for 'markdown'."
        ),
    ] = 256,
    overlap: Annotated[
        int,
        Field(
            description="Token overlap carried between consecutive chunks. "
            "Applies to format='chunks' only; ignored for 'markdown' and 'rag'."
        ),
    ] = 50,
) -> str:
    """Convert a whole PDF into a text representation for downstream LLM use.

    Returns JSON: {content, format} for 'markdown', or {chunks, format} for
    'chunks'/'rag' (each chunk carries its index and page_numbers; rag chunks
    add token_estimate and heading_context). Read-only.

    Use this when you need structure or chunking. If you just want the raw
    reading text use extract_text; for per-run coordinates use extract_entities.
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

        # format == "rag" (the Literal type guarantees no other value reaches here)
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

    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})
