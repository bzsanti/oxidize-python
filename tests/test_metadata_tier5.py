"""Tests for Tier 5 — Extended Metadata (Features 19-20)."""

import pytest


class TestProducerMetadata:
    def test_set_producer(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.set_producer("oxidize-python 1.0")
        doc.add_page(Page.a4())
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_set_producer_empty(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.set_producer("")
        doc.add_page(Page.a4())
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


class TestDocumentDates:
    def test_set_creation_date(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.set_creation_date("2024-01-15T10:00:00Z")
        doc.add_page(Page.a4())
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_set_modification_date(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.set_modification_date("2025-06-20T15:30:00Z")
        doc.add_page(Page.a4())
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_set_both_dates(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.set_creation_date("2024-01-01T00:00:00Z")
        doc.set_modification_date("2024-12-31T23:59:59Z")
        doc.add_page(Page.a4())
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_invalid_date_raises(self):
        from oxidize_pdf import Document

        doc = Document()
        with pytest.raises(ValueError):
            doc.set_creation_date("not-a-date")

    def test_invalid_modification_date_raises(self):
        from oxidize_pdf import Document

        doc = Document()
        with pytest.raises(ValueError):
            doc.set_modification_date("2024-13-45")

    def test_date_with_timezone_offset(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.set_creation_date("2024-06-15T10:00:00+02:00")
        doc.add_page(Page.a4())
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
