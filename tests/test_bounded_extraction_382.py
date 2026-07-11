"""F1 (#382): bounded extraction — ExtractionOptions.max_extracted_bytes and
ExtractedText.truncated.

Upstream oxidize-pdf 4.0.0 caps decoded-text accumulation during a page run so
an adversarially inflated content stream cannot materialise an unbounded String.
The bridge must (a) let callers set the cap and (b) surface whether extraction
was truncated. Complements the MCP DoS hardening shipped in v0.14.0 (#115).
"""

import pytest
import oxidize_pdf as op


def _create_multiline_pdf(lines: int = 20) -> bytes:
    """A single page with many recognisable, ordered lines top-to-bottom."""
    doc = op.Document()
    page = op.Page.a4()
    page.set_font(op.Font.HELVETICA, 12.0)
    for i in range(lines):
        page.text_at(50.0, 750.0 - i * 20.0, f"Line number {i:02d} with some filler text")
    doc.add_page(page)
    return doc.save_to_bytes()


@pytest.fixture
def multiline_bytes() -> bytes:
    return _create_multiline_pdf()


class TestMaxExtractedBytesOption:
    def test_default_is_none(self):
        opts = op.ExtractionOptions()
        assert opts.max_extracted_bytes is None

    def test_custom_value(self):
        opts = op.ExtractionOptions(max_extracted_bytes=64)
        assert opts.max_extracted_bytes == 64

    def test_surfaces_in_repr(self):
        r = repr(op.ExtractionOptions(max_extracted_bytes=64))
        assert "max_extracted_bytes" in r


class TestExtractedTextTruncation:
    def test_unbounded_extracts_full_text_not_truncated(self, multiline_bytes):
        reader = op.PdfReader.from_bytes(multiline_bytes)
        result = reader.extract_page_text(0, op.ExtractionOptions())
        assert result.truncated is False
        assert "Line number 19" in result.text

    def test_bounded_truncates_and_flags(self, multiline_bytes):
        reader = op.PdfReader.from_bytes(multiline_bytes)
        full = reader.extract_page_text(0, op.ExtractionOptions())
        bounded = reader.extract_page_text(0, op.ExtractionOptions(max_extracted_bytes=40))
        assert full.truncated is False
        assert bounded.truncated is True
        assert len(bounded.text) < len(full.text)
        assert "Line number 19" in full.text
        assert "Line number 19" not in bounded.text

    def test_large_cap_is_byte_identical_to_unbounded(self, multiline_bytes):
        reader = op.PdfReader.from_bytes(multiline_bytes)
        full = reader.extract_page_text(0, op.ExtractionOptions())
        large = reader.extract_page_text(0, op.ExtractionOptions(max_extracted_bytes=100_000))
        assert large.truncated is False
        assert large.text == full.text

    def test_result_exposes_fragments(self, multiline_bytes):
        reader = op.PdfReader.from_bytes(multiline_bytes)
        opts = op.ExtractionOptions(preserve_layout=True)
        result = reader.extract_page_text(0, opts)
        # preserve_layout=True yields positional fragments
        assert isinstance(result.fragments, list)
        assert len(result.fragments) > 0
