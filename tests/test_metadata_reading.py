"""Tests for Metadata Reading from PdfReader — Feature 43 (Tier 1.5)."""

import pytest


class TestReaderMetadata:
    def test_metadata_returns_object(self):
        from oxidize_pdf import Document, DocumentMetadata, Font, Page, PdfReader

        doc = Document()
        doc.set_title("Test Title")
        doc.set_author("Test Author")
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Content")
        doc.add_page(page)
        data = doc.save_to_bytes()

        reader = PdfReader.from_bytes(data)
        meta = reader.metadata()
        assert isinstance(meta, DocumentMetadata)
        assert meta.title == "Test Title"
        assert meta.author == "Test Author"

    def test_metadata_subject_keywords(self):
        from oxidize_pdf import Document, Font, Page, PdfReader

        doc = Document()
        doc.set_subject("Test Subject")
        doc.set_keywords("test, pdf, metadata")
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Content")
        doc.add_page(page)
        data = doc.save_to_bytes()

        reader = PdfReader.from_bytes(data)
        meta = reader.metadata()
        assert meta.subject == "Test Subject"
        assert meta.keywords == "test, pdf, metadata"

    def test_metadata_producer_creator(self):
        from oxidize_pdf import Document, Font, Page, PdfReader

        doc = Document()
        doc.set_creator("My App")
        doc.set_producer("My Producer")
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Content")
        doc.add_page(page)
        data = doc.save_to_bytes()

        reader = PdfReader.from_bytes(data)
        meta = reader.metadata()
        assert meta.creator == "My App"
        assert meta.producer == "My Producer"

    def test_metadata_empty_document(self):
        from oxidize_pdf import Document, Font, Page, PdfReader

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Blank metadata")
        doc.add_page(page)
        data = doc.save_to_bytes()

        reader = PdfReader.from_bytes(data)
        meta = reader.metadata()
        # Title/author not set explicitly
        assert meta.title is None

    def test_metadata_version_and_page_count(self):
        from oxidize_pdf import Document, Font, Page, PdfReader

        doc = Document()
        for i in range(3):
            page = Page.a4()
            page.set_font(Font.HELVETICA, 12.0)
            page.text_at(72.0, 700.0, f"Page {i}")
            doc.add_page(page)
        data = doc.save_to_bytes()

        reader = PdfReader.from_bytes(data)
        meta = reader.metadata()
        assert isinstance(meta.version, str)
        assert meta.page_count == 3
