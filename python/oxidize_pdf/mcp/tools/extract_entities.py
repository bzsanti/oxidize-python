"""MCP tool: extract_entities — extract text entities from a PDF by page."""

import json
from typing import Annotated

from mcp.types import ToolAnnotations
from pydantic import Field

from oxidize_pdf.mcp.server import mcp


@mcp.tool(
    annotations=ToolAnnotations(
        title="Extract positioned text runs",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=False,
    )
)
def extract_entities(
    path: Annotated[
        str,
        Field(description="Path to the PDF file, relative to the configured workspace."),
    ],
) -> str:
    """Extract every text run of a PDF together with its layout geometry.

    Returns JSON {path, entities, entity_count, page_count} where each entity is
    {text, page (0-based), x, y, font_size, font_name}. Coordinates are in PDF
    points with the origin at the bottom-left of the page. Read-only.

    Use this for layout-aware tasks (table reconstruction, positional lookup,
    locating a label on the page). If you only need the reading text without
    coordinates, use extract_text; for Markdown or RAG chunks use convert_pdf.
    """
    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    resolved, err = setup_pdf_path(path)
    if err:
        return err

    try:
        from oxidize_pdf import PdfReader

        reader = PdfReader.open(str(resolved))
        page_count = reader.page_count

        entities: list[dict] = []
        for page_idx in range(page_count):
            chunks = reader.extract_text_chunks(page_idx)
            for chunk in chunks:
                entities.append({
                    "text": chunk.text,
                    "page": page_idx,
                    "x": chunk.x,
                    "y": chunk.y,
                    "font_size": chunk.font_size,
                    "font_name": chunk.font_name,
                })

        return json.dumps({
            "path": path,
            "entities": entities,
            "entity_count": len(entities),
            "page_count": page_count,
        })
    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})
