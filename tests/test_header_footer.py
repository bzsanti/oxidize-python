"""Tests for Headers/Footers — Feature 3 (Tier 1)."""

import pytest


class TestHeaderFooterConstruction:
    """Test HeaderFooter and HeaderFooterOptions construction."""

    def test_header_creation(self):
        from oxidize_pdf import HeaderFooter

        hf = HeaderFooter.new_header("Page {page}")
        assert isinstance(hf, HeaderFooter)

    def test_footer_creation(self):
        from oxidize_pdf import HeaderFooter

        hf = HeaderFooter.new_footer("Page {page} of {total}")
        assert isinstance(hf, HeaderFooter)

    def test_header_with_font(self):
        from oxidize_pdf import Font, HeaderFooter

        hf = HeaderFooter.new_header("Title")
        hf = hf.with_font(Font.HELVETICA_BOLD, 14.0)
        assert isinstance(hf, HeaderFooter)

    def test_header_with_alignment(self):
        from oxidize_pdf import HeaderFooter, TextAlign

        hf = HeaderFooter.new_header("Centered Title")
        hf = hf.with_alignment(TextAlign.CENTER)
        assert isinstance(hf, HeaderFooter)

    def test_header_with_margin(self):
        from oxidize_pdf import HeaderFooter

        hf = HeaderFooter.new_header("Margin Test")
        hf = hf.with_margin(20.0)
        assert isinstance(hf, HeaderFooter)

    def test_header_footer_options_defaults(self):
        from oxidize_pdf import HeaderFooterOptions

        opts = HeaderFooterOptions()
        assert isinstance(opts, HeaderFooterOptions)


class TestHeaderFooterOnPage:
    """Test adding headers/footers to pages and rendering."""

    def test_page_with_header_renders(self):
        from oxidize_pdf import Document, Font, HeaderFooter, Page

        hf = HeaderFooter.new_header("Document Title").with_font(Font.HELVETICA_BOLD, 12.0)

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Body text")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()

        assert data[:5] == b"%PDF-"

    def test_page_with_footer_renders(self):
        from oxidize_pdf import Document, HeaderFooter, Page

        hf = HeaderFooter.new_footer("Page {page}")

        page = Page.a4()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()

        assert data[:5] == b"%PDF-"

    def test_header_builder_chain(self):
        from oxidize_pdf import Font, HeaderFooter, TextAlign

        hf = (
            HeaderFooter.new_header("Title")
            .with_font(Font.TIMES_BOLD, 16.0)
            .with_alignment(TextAlign.CENTER)
            .with_margin(30.0)
        )
        assert isinstance(hf, HeaderFooter)
