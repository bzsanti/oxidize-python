"""Strict consumer of native APIs and protocol types used by MCP."""
from mcp_types import ToolAnnotations
from oxidize_pdf import (
    Document, DocumentMetadata, PdfReader, PdfALevel, PdfAValidator,
    TextAnnotation, HighlightAnnotation, Point, Rectangle, Page,
)


def inspect_pdf(reader: PdfReader) -> tuple[DocumentMetadata, list[str]]:
    chunks = reader.extract_text_chunks(0)
    for chunk in chunks:
        name: str | None = chunk.font_name
        if name is not None:
            name.upper()
    return reader.metadata(), [chunk.text for chunk in reader.rag_chunks()]


def build() -> Document:
    doc = Document()
    page = Page.a4()
    page.add_annotation(TextAnnotation(Point(10, 10)).with_contents("Note").to_annotation())
    page.add_annotation(HighlightAnnotation(Rectangle.from_xywh(10, 10, 20, 20)).to_annotation())
    doc.add_page(page)
    annotations = ToolAnnotations(read_only_hint=True, open_world_hint=False)
    assert annotations.read_only_hint is True
    return doc


def validate(data: bytes) -> bool:
    validator = PdfAValidator(PdfALevel.A1B).collect_all_errors(True)
    return validator.validate_bytes(data).is_valid
