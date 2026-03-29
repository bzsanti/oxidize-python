"""MCP tool: extract_entities — extract semantic entities from a PDF."""

import json

from oxidize_pdf.mcp.server import mcp


@mcp.tool()
def extract_entities(path: str) -> str:
    """Extract semantic entities from a PDF file.

    Returns a list of entities found in the document along with page count.
    Entity extraction uses the oxidize-pdf EntityMap and text extraction APIs.
    """
    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    resolved, err = setup_pdf_path(path)
    if err:
        return err

    try:
        from oxidize_pdf import EntityMap, PdfReader

        reader = PdfReader.open(str(resolved))
        page_count = reader.page_count

        entity_map = EntityMap()
        entities_json = json.loads(entity_map.to_json())

        return json.dumps({
            "path": path,
            "entities": entities_json.get("schemas", []),
            "page_count": page_count,
        })
    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})
