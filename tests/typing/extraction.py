"""Consumer contract: run mypy --strict --disallow-any-expr on this file."""

from oxidize_pdf import (
    ExtractedText,
    ExtractionOptions,
    PdfReader,
    SpaceDecision,
    TextFragment,
    TextRenderingMode,
)


def extract(reader: PdfReader) -> tuple[list[str], list[list[TextFragment]], ExtractedText]:
    options = ExtractionOptions(
        preserve_layout=True,
        max_extracted_bytes=1000,
        include_link_annotations=True,
        include_unreliable_figure_text=False,
    )
    links: bool = options.include_link_annotations
    figures: bool = options.include_unreliable_figure_text
    limit: int | None = options.max_extracted_bytes
    assert links and not figures and limit == 1000
    page: ExtractedText = reader.extract_page_text(0, options)
    fragments: list[TextFragment] = reader.extract_fragments_from_page(0, options)
    for fragment in fragments:
        mode: TextRenderingMode = fragment.render_mode
        hidden: bool = mode == TextRenderingMode.INVISIBLE
        text: str = fragment.text
        decisions: list[SpaceDecision] = fragment.space_decisions
        if hidden:
            assert text or not decisions
    truncated: bool = page.truncated
    if not truncated:
        assert page.fragments == fragments
    return reader.extract_text_with_options(options), reader.extract_fragments_with_options(options), page
