"""MCP tool: annotate_pdf — add annotations (text, highlight) to an existing PDF."""

import json
import tempfile
from pathlib import Path

from oxidize_pdf.mcp.server import mcp

_VALID_TYPES = frozenset({"text", "highlight"})


@mcp.tool()
def annotate_pdf(
    input_path: str,
    output_path: str,
    annotation_type: str,
    page: int,
    x: float,
    y: float,
    contents: str | None = None,
    width: float = 100.0,
    height: float = 20.0,
) -> str:
    """Add an annotation to an existing PDF.

    Supported annotation types:
    - text: A sticky note annotation at (x, y) with optional contents.
    - highlight: A highlight rectangle at (x, y) with given width and height.
    """
    from oxidize_pdf.mcp.tools.base import setup_output_path, setup_pdf_path

    resolved_input, err = setup_pdf_path(input_path)
    if err:
        return err

    resolved_output, err = setup_output_path(output_path)
    if err:
        return err

    if annotation_type not in _VALID_TYPES:
        return json.dumps({
            "error": f"Unknown annotation type: '{annotation_type}'. "
            f"Valid types: {', '.join(sorted(_VALID_TYPES))}.",
            "code": "INVALID_TYPE",
        })

    try:
        from oxidize_pdf import (
            Document,
            HighlightAnnotation,
            OverlayOptions,
            Page,
            PdfReader,
            Point,
            Rectangle,
            TextAnnotation,
            overlay_pdf,
        )

        reader = PdfReader.open(str(resolved_input))
        if page < 0 or page >= reader.page_count:
            return json.dumps({
                "error": f"Page {page} out of range (0-{reader.page_count - 1}).",
                "code": "INVALID_PAGE",
            })

        parsed = reader.get_page(page)
        page_obj = Page(parsed.width, parsed.height)

        if annotation_type == "text":
            ta = TextAnnotation(Point(x, y))
            if contents:
                ta.with_contents(contents)
            page_obj.add_annotation(ta.to_annotation())

        elif annotation_type == "highlight":
            rect = Rectangle.from_xywh(x, y, width, height)
            ha = HighlightAnnotation(rect)
            page_obj.add_annotation(ha.to_annotation())

        overlay_doc = Document()
        overlay_doc.add_page(page_obj)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            overlay_doc.save(tmp.name)
            overlay_tmp = Path(tmp.name)

        try:
            overlay_pdf(
                str(resolved_input),
                str(overlay_tmp),
                str(resolved_output),
                OverlayOptions(),
            )
        finally:
            overlay_tmp.unlink(missing_ok=True)

        return json.dumps({"status": "ok", "annotation_type": annotation_type})

    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})
