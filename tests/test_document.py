"""Tests for Document and Page generation API."""

import os

import pytest


class TestDocument:
    """Test the Document class."""

    def test_create_empty_document(self):
        from oxidize_pdf import Document

        doc = Document()
        assert doc.page_count == 0

    def test_set_metadata(self):
        from oxidize_pdf import Document

        doc = Document()
        doc.set_title("Test Title")
        doc.set_author("Test Author")
        doc.set_subject("Test Subject")
        doc.set_keywords("test, pdf, python")
        doc.set_creator("oxidize-python tests")
        # No assertion on values — just verify no exception

    def test_add_page(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.add_page(Page.a4())
        assert doc.page_count == 1

    def test_add_multiple_pages(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.add_page(Page.a4())
        doc.add_page(Page.letter())
        doc.add_page(Page(400.0, 600.0))
        assert doc.page_count == 3

    def test_save_to_file(self, output_pdf):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.add_page(Page.a4())
        doc.save(str(output_pdf))

        assert output_pdf.exists()
        assert output_pdf.stat().st_size > 0

    def test_save_to_bytes(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.add_page(Page.a4())
        data = doc.save_to_bytes()

        assert isinstance(data, bytes)
        assert len(data) > 0
        assert data[:5] == b"%PDF-"

    def test_save_empty_document(self, output_pdf):
        """Saving a document with no pages should still work."""
        from oxidize_pdf import Document

        doc = Document()
        doc.save(str(output_pdf))
        assert output_pdf.exists()

    def test_repr(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        assert "Document" in repr(doc)
        doc.add_page(Page.a4())
        r = repr(doc)
        assert "1" in r  # page count

    def test_page_reuse(self):
        """Adding the same Page object multiple times should work (clone)."""
        from oxidize_pdf import Document, Page

        doc = Document()
        page = Page.a4()
        doc.add_page(page)
        doc.add_page(page)
        assert doc.page_count == 2


class TestPage:
    """Test the Page class."""

    def test_a4_dimensions(self):
        from oxidize_pdf import Page

        page = Page.a4()
        assert page.width == 595.0
        assert page.height == 842.0

    def test_letter_dimensions(self):
        from oxidize_pdf import Page

        page = Page.letter()
        assert page.width == 612.0
        assert page.height == 792.0

    def test_legal_dimensions(self):
        from oxidize_pdf import Page

        page = Page.legal()
        assert page.width == 612.0
        assert page.height == 1008.0

    def test_custom_dimensions(self):
        from oxidize_pdf import Page

        page = Page(400.0, 600.0)
        assert page.width == 400.0
        assert page.height == 600.0

    def test_landscape_variants(self):
        from oxidize_pdf import Page

        a4l = Page.a4_landscape()
        assert a4l.width == 842.0
        assert a4l.height == 595.0

        letterl = Page.letter_landscape()
        assert letterl.width == 792.0
        assert letterl.height == 612.0

    def test_margins_default(self):
        from oxidize_pdf import Page

        page = Page.a4()
        m = page.margins
        assert m.top == 72.0
        assert m.right == 72.0
        assert m.bottom == 72.0
        assert m.left == 72.0

    def test_set_margins(self):
        from oxidize_pdf import Margins, Page

        page = Page.a4()
        page.set_margins(Margins(top=50.0, right=40.0, bottom=50.0, left=40.0))
        m = page.margins
        assert m.top == 50.0
        assert m.right == 40.0

    def test_repr(self):
        from oxidize_pdf import Page

        page = Page.a4()
        r = repr(page)
        assert "Page" in r
        assert "595" in r
        assert "842" in r
