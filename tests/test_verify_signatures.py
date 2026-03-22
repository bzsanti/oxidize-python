"""Tests for Feature 28 fix: verify_pdf_signatures standalone function."""
import pytest


def _minimal_pdf_bytes():
    """Create a minimal valid PDF byte string for testing."""
    from oxidize_pdf import Document, Page

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)
    return bytes(doc.save_to_bytes())


def test_verify_signatures_empty_pdf_returns_empty_list():
    from oxidize_pdf import verify_pdf_signatures

    pdf_bytes = _minimal_pdf_bytes()
    results = verify_pdf_signatures(pdf_bytes)
    assert isinstance(results, list)
    assert results == []


def test_verify_signatures_non_pdf_raises_error():
    from oxidize_pdf import PdfParseError, verify_pdf_signatures

    with pytest.raises(Exception):
        verify_pdf_signatures(b"not a pdf at all")


def test_verify_signatures_return_type():
    from oxidize_pdf import verify_pdf_signatures

    pdf_bytes = _minimal_pdf_bytes()
    results = verify_pdf_signatures(pdf_bytes)
    assert isinstance(results, list)
    for item in results:
        assert isinstance(item, dict)
        assert "name" in item
        assert "valid" in item


def test_verify_signatures_empty_bytes_raises_error():
    from oxidize_pdf import verify_pdf_signatures

    with pytest.raises(Exception):
        verify_pdf_signatures(b"")
