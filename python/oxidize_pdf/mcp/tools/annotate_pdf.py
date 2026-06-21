"""MCP tool: annotate_pdf — add annotations (text, highlight) to an existing PDF."""

import json
import tempfile
from pathlib import Path
from typing import Annotated, Literal, Optional

from mcp.types import ToolAnnotations
from pydantic import Field

from oxidize_pdf.mcp.server import mcp


@mcp.tool(
    annotations=ToolAnnotations(
        title="Annotate a PDF",
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=False,
    )
)
def annotate_pdf(
    input_path: Annotated[
        str,
        Field(description="Source PDF to annotate, relative to the workspace."),
    ],
    output_path: Annotated[
        str,
        Field(description="Destination .pdf path; overwritten if it already exists."),
    ],
    annotation_type: Annotated[
        Literal["text", "highlight"],
        Field(
            description="'text' adds a sticky-note marker at (x, y); 'highlight' "
            "draws a highlight rectangle of width×height anchored at (x, y)."
        ),
    ],
    page: Annotated[
        int,
        Field(description="0-based index of the page to annotate."),
    ],
    x: Annotated[
        float,
        Field(description="Horizontal anchor in PDF points from the left edge."),
    ],
    y: Annotated[
        float,
        Field(
            description="Vertical anchor in PDF points from the bottom edge "
            "(origin is bottom-left)."
        ),
    ],
    contents: Annotated[
        Optional[str],
        Field(description="Note text for a 'text' annotation. Ignored for 'highlight'."),
    ] = None,
    width: Annotated[
        float,
        Field(description="Highlight width in points. Used only for 'highlight'."),
    ] = 100.0,
    height: Annotated[
        float,
        Field(description="Highlight height in points. Used only for 'highlight'."),
    ] = 20.0,
) -> str:
    """Stamp a sticky note or highlight onto a page of an existing PDF.

    Writes the annotated copy to output_path (overwriting any existing file) and
    returns JSON {status, annotation_type}; out-of-range pages or coordinates
    outside the page bounds return {error, code}. Coordinates are in PDF points
    with the origin at the bottom-left.

    Use this to mark up a document. To reorder/rotate/overlay whole pages use
    manipulate_pdf; to author a new PDF use create_pdf.
    """
    from oxidize_pdf.mcp.tools.base import setup_output_path, setup_pdf_path

    resolved_input, err = setup_pdf_path(input_path)
    if err:
        return err

    resolved_output, err = setup_output_path(output_path)
    if err:
        return err

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

        if x < 0 or x > parsed.width or y < 0 or y > parsed.height:
            return json.dumps({
                "error": f"Coordinates ({x}, {y}) outside page bounds "
                f"(0-{parsed.width}, 0-{parsed.height}).",
                "code": "INVALID_COORDINATES",
            })

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
