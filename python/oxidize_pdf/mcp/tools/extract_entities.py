"""MCP tool: extract_entities — extract text entities from a PDF by page."""

import json

from oxidize_pdf.mcp.server import mcp


@mcp.tool()
def extract_entities(path: str) -> str:
    """Extract text entities from a PDF file, organized by page.

    Returns text chunks with position and font information for each page.
    Each entity includes: text, x, y, font_size, font_name, and page index.
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
