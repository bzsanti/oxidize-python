"""Tests for Tier 2 operations — Features 6-10."""

import pytest


@pytest.fixture
def two_page_pdf(tmp_dir):
    """Create a 2-page PDF for testing."""
    from oxidize_pdf import Document, Font, Page

    doc = Document()
    for i in range(2):
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, f"Page {i + 1}")
        doc.add_page(page)
    path = tmp_dir / "two_page.pdf"
    doc.save(str(path))
    return path


@pytest.fixture
def three_page_pdf(tmp_dir):
    """Create a 3-page PDF for testing."""
    from oxidize_pdf import Document, Font, Page

    doc = Document()
    for i in range(3):
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, f"Page {i + 1}")
        doc.add_page(page)
    path = tmp_dir / "three_page.pdf"
    doc.save(str(path))
    return path


# ── Feature 6: Page Reorder/Swap/Move/Reverse ─────────────────────────────


class TestReorderPdfPages:
    """Test page reordering operations."""

    def test_reorder_pdf_pages(self, three_page_pdf, tmp_dir):
        from oxidize_pdf import PdfReader, reorder_pdf_pages

        output = tmp_dir / "reordered.pdf"
        reorder_pdf_pages(str(three_page_pdf), str(output), [2, 0, 1])
        reader = PdfReader.open(str(output))
        assert reader.page_count == 3

    def test_swap_pdf_pages(self, three_page_pdf, tmp_dir):
        from oxidize_pdf import PdfReader, swap_pdf_pages

        output = tmp_dir / "swapped.pdf"
        swap_pdf_pages(str(three_page_pdf), str(output), 0, 2)
        reader = PdfReader.open(str(output))
        assert reader.page_count == 3

    def test_move_pdf_page(self, three_page_pdf, tmp_dir):
        from oxidize_pdf import PdfReader, move_pdf_page

        output = tmp_dir / "moved.pdf"
        move_pdf_page(str(three_page_pdf), str(output), 0, 2)
        reader = PdfReader.open(str(output))
        assert reader.page_count == 3

    def test_reverse_pdf_pages(self, three_page_pdf, tmp_dir):
        from oxidize_pdf import PdfReader, reverse_pdf_pages

        output = tmp_dir / "reversed.pdf"
        reverse_pdf_pages(str(three_page_pdf), str(output))
        reader = PdfReader.open(str(output))
        assert reader.page_count == 3

    def test_reorder_invalid_index_raises(self, two_page_pdf, tmp_dir):
        from oxidize_pdf import PdfError, reorder_pdf_pages

        output = tmp_dir / "bad.pdf"
        with pytest.raises(PdfError):
            reorder_pdf_pages(str(two_page_pdf), str(output), [0, 1, 99])


# ── Feature 7: Overlay PDF ────────────────────────────────────────────────


class TestOverlayPdf:
    """Test PDF overlay operations."""

    def test_overlay_position_variants(self):
        from oxidize_pdf import OverlayPosition

        assert OverlayPosition.CENTER is not None
        assert OverlayPosition.TOP_LEFT is not None
        assert OverlayPosition.TOP_RIGHT is not None
        assert OverlayPosition.BOTTOM_LEFT is not None
        assert OverlayPosition.BOTTOM_RIGHT is not None

    def test_overlay_options_defaults(self):
        from oxidize_pdf import OverlayOptions

        opts = OverlayOptions()
        assert isinstance(opts, OverlayOptions)

    def test_overlay_options_custom(self):
        from oxidize_pdf import OverlayOptions, OverlayPosition

        opts = OverlayOptions(
            position=OverlayPosition.CENTER,
            opacity=0.5,
            scale=0.8,
        )
        assert isinstance(opts, OverlayOptions)

    def test_overlay_pdf(self, two_page_pdf, tmp_dir):
        from oxidize_pdf import OverlayOptions, PdfReader, overlay_pdf

        output = tmp_dir / "overlaid.pdf"
        overlay_pdf(str(two_page_pdf), str(two_page_pdf), str(output), OverlayOptions())
        reader = PdfReader.open(str(output))
        assert reader.page_count >= 1


# ── Feature 8: Extract Images ─────────────────────────────────────────────


class TestExtractImages:
    """Test image extraction from PDFs."""

    def test_extract_images_options(self, tmp_dir):
        from oxidize_pdf import ExtractImagesOptions

        opts = ExtractImagesOptions(str(tmp_dir))
        assert isinstance(opts, ExtractImagesOptions)

    def test_extract_images_from_pdf_no_images(self, two_page_pdf, tmp_dir):
        from oxidize_pdf import ExtractImagesOptions, extract_images_from_pdf

        opts = ExtractImagesOptions(str(tmp_dir))
        result = extract_images_from_pdf(str(two_page_pdf), opts)
        assert isinstance(result, list)
        # The PDF has no embedded images, so result should be empty
        assert len(result) == 0


# ── Feature 9: Page Rotation (creation-side) ──────────────────────────────


class TestPageRotation:
    """Test page rotation getters/setters."""

    def test_page_rotation_default(self):
        from oxidize_pdf import Page

        page = Page.a4()
        assert page.rotation == 0

    def test_page_set_rotation(self):
        from oxidize_pdf import Page

        page = Page.a4()
        page.set_rotation(90)
        assert page.rotation == 90

    def test_page_rotation_in_saved_pdf(self):
        from oxidize_pdf import Document, Page

        page = Page.a4()
        page.set_rotation(90)

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()

        assert data[:5] == b"%PDF-"
        assert len(data) > 0


# ── Feature 10: Save-to-bytes variants ────────────────────────────────────


class TestBytesOperations:
    """Test _bytes variants for operations."""

    def test_merge_pdfs_to_bytes(self, two_page_pdf, three_page_pdf):
        from oxidize_pdf import merge_pdfs_to_bytes

        result = merge_pdfs_to_bytes([str(two_page_pdf), str(three_page_pdf)])
        assert isinstance(result, bytes)
        assert result[:5] == b"%PDF-"

    def test_rotate_pdf_to_bytes(self, two_page_pdf):
        from oxidize_pdf import rotate_pdf_to_bytes

        result = rotate_pdf_to_bytes(str(two_page_pdf), 90)
        assert isinstance(result, bytes)
        assert result[:5] == b"%PDF-"

    def test_extract_pages_to_bytes(self, three_page_pdf):
        from oxidize_pdf import extract_pages_to_bytes

        result = extract_pages_to_bytes(str(three_page_pdf), [0, 2])
        assert isinstance(result, bytes)
        assert result[:5] == b"%PDF-"

    def test_split_pdf_to_bytes(self, two_page_pdf):
        from oxidize_pdf import split_pdf_to_bytes

        result = split_pdf_to_bytes(str(two_page_pdf))
        assert isinstance(result, list)
        assert len(result) == 2
        for chunk in result:
            assert isinstance(chunk, bytes)
            assert chunk[:5] == b"%PDF-"
