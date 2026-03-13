"""Tests for PDF operations: split, merge, rotate, extract pages."""

import pytest


@pytest.fixture
def two_page_pdf(tmp_dir):
    """Generate a 2-page PDF for operation tests."""
    from oxidize_pdf import Document, Font, Page

    path = tmp_dir / "two_page.pdf"
    doc = Document()

    page1 = Page.a4()
    page1.set_font(Font.HELVETICA, 12.0)
    page1.text_at(100.0, 700.0, "Page one content")
    doc.add_page(page1)

    page2 = Page.a4()
    page2.set_font(Font.COURIER, 12.0)
    page2.text_at(100.0, 700.0, "Page two content")
    doc.add_page(page2)

    doc.save(str(path))
    return path


@pytest.fixture
def three_page_pdf(tmp_dir):
    """Generate a 3-page PDF for operation tests."""
    from oxidize_pdf import Document, Font, Page

    path = tmp_dir / "three_page.pdf"
    doc = Document()

    for i in range(1, 4):
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, f"Page {i}")
        doc.add_page(page)

    doc.save(str(path))
    return path


@pytest.fixture
def single_page_pdf_a(tmp_dir):
    """First single-page PDF for merge tests."""
    from oxidize_pdf import Document, Font, Page

    path = tmp_dir / "doc_a.pdf"
    doc = Document()
    page = Page.a4()
    page.set_font(Font.HELVETICA, 12.0)
    page.text_at(100.0, 700.0, "Document A")
    doc.add_page(page)
    doc.save(str(path))
    return path


@pytest.fixture
def single_page_pdf_b(tmp_dir):
    """Second single-page PDF for merge tests."""
    from oxidize_pdf import Document, Font, Page

    path = tmp_dir / "doc_b.pdf"
    doc = Document()
    page = Page.a4()
    page.set_font(Font.HELVETICA, 12.0)
    page.text_at(100.0, 700.0, "Document B")
    doc.add_page(page)
    doc.save(str(path))
    return path


# ── Split ──────────────────────────────────────────────────────────────────────


class TestSplitPdf:
    """Test PDF splitting operations."""

    def test_split_into_single_pages(self, two_page_pdf, tmp_dir):
        from oxidize_pdf import split_pdf

        output_dir = tmp_dir / "split_output"
        output_dir.mkdir()

        result = split_pdf(str(two_page_pdf), str(output_dir))
        assert isinstance(result, list)
        assert len(result) == 2

    def test_split_output_files_are_valid_pdfs(self, two_page_pdf, tmp_dir):
        from oxidize_pdf import PdfReader, split_pdf

        output_dir = tmp_dir / "split_valid"
        output_dir.mkdir()

        result = split_pdf(str(two_page_pdf), str(output_dir))
        for path in result:
            reader = PdfReader.open(path)
            assert reader.page_count == 1

    def test_split_three_pages(self, three_page_pdf, tmp_dir):
        from oxidize_pdf import split_pdf

        output_dir = tmp_dir / "split_three"
        output_dir.mkdir()

        result = split_pdf(str(three_page_pdf), str(output_dir))
        assert len(result) == 3

    def test_split_nonexistent_file(self, tmp_dir):
        from oxidize_pdf import PdfError, split_pdf

        output_dir = tmp_dir / "split_missing"
        output_dir.mkdir()

        with pytest.raises(PdfError):
            split_pdf("/nonexistent/fake.pdf", str(output_dir))


# ── Merge ──────────────────────────────────────────────────────────────────────


class TestMergePdfs:
    """Test PDF merging operations."""

    def test_merge_two_pdfs(self, single_page_pdf_a, single_page_pdf_b, tmp_dir):
        from oxidize_pdf import merge_pdfs

        output = tmp_dir / "merged.pdf"
        merge_pdfs(
            [str(single_page_pdf_a), str(single_page_pdf_b)],
            str(output),
        )
        assert output.exists()

    def test_merge_result_has_correct_page_count(
        self, single_page_pdf_a, single_page_pdf_b, tmp_dir
    ):
        from oxidize_pdf import PdfReader, merge_pdfs

        output = tmp_dir / "merged_count.pdf"
        merge_pdfs(
            [str(single_page_pdf_a), str(single_page_pdf_b)],
            str(output),
        )
        reader = PdfReader.open(str(output))
        assert reader.page_count == 2

    def test_merge_three_pdfs(
        self, single_page_pdf_a, single_page_pdf_b, two_page_pdf, tmp_dir
    ):
        from oxidize_pdf import PdfReader, merge_pdfs

        output = tmp_dir / "merged_three.pdf"
        merge_pdfs(
            [str(single_page_pdf_a), str(single_page_pdf_b), str(two_page_pdf)],
            str(output),
        )
        reader = PdfReader.open(str(output))
        assert reader.page_count == 4

    def test_merge_nonexistent_input(self, tmp_dir):
        from oxidize_pdf import PdfError, merge_pdfs

        output = tmp_dir / "merged_fail.pdf"
        with pytest.raises(PdfError):
            merge_pdfs(["/nonexistent/a.pdf"], str(output))

    def test_merge_empty_list_raises(self, tmp_dir):
        from oxidize_pdf import PdfError, merge_pdfs

        output = tmp_dir / "merged_empty.pdf"
        with pytest.raises((PdfError, ValueError)):
            merge_pdfs([], str(output))


# ── Rotate ─────────────────────────────────────────────────────────────────────


class TestRotatePdf:
    """Test PDF rotation operations."""

    def test_rotate_90(self, two_page_pdf, tmp_dir):
        from oxidize_pdf import rotate_pdf

        output = tmp_dir / "rotated_90.pdf"
        rotate_pdf(str(two_page_pdf), str(output), 90)
        assert output.exists()

    def test_rotate_changes_dimensions(self, two_page_pdf, tmp_dir):
        from oxidize_pdf import PdfReader, rotate_pdf

        output = tmp_dir / "rotated_dims.pdf"
        rotate_pdf(str(two_page_pdf), str(output), 90)

        reader = PdfReader.open(str(output))
        page = reader.get_page(0)
        # A4 is 595x842; after 90° rotation, effective dims swap
        assert abs(page.width - 842.0) < 1.0
        assert abs(page.height - 595.0) < 1.0

    def test_rotate_180(self, two_page_pdf, tmp_dir):
        from oxidize_pdf import PdfReader, rotate_pdf

        output = tmp_dir / "rotated_180.pdf"
        rotate_pdf(str(two_page_pdf), str(output), 180)

        reader = PdfReader.open(str(output))
        page = reader.get_page(0)
        # 180° rotation doesn't change dimensions
        assert abs(page.width - 595.0) < 1.0
        assert abs(page.height - 842.0) < 1.0

    def test_rotate_270(self, two_page_pdf, tmp_dir):
        from oxidize_pdf import rotate_pdf

        output = tmp_dir / "rotated_270.pdf"
        rotate_pdf(str(two_page_pdf), str(output), 270)
        assert output.exists()

    def test_rotate_invalid_angle(self, two_page_pdf, tmp_dir):
        from oxidize_pdf import PdfError, rotate_pdf

        output = tmp_dir / "rotated_bad.pdf"
        with pytest.raises((PdfError, ValueError)):
            rotate_pdf(str(two_page_pdf), str(output), 45)

    def test_rotate_preserves_page_count(self, three_page_pdf, tmp_dir):
        from oxidize_pdf import PdfReader, rotate_pdf

        output = tmp_dir / "rotated_count.pdf"
        rotate_pdf(str(three_page_pdf), str(output), 90)

        reader = PdfReader.open(str(output))
        assert reader.page_count == 3


# ── Extract Pages ──────────────────────────────────────────────────────────────


class TestExtractPages:
    """Test extracting specific pages from a PDF."""

    def test_extract_single_page(self, three_page_pdf, tmp_dir):
        from oxidize_pdf import PdfReader, extract_pages

        output = tmp_dir / "extracted_single.pdf"
        extract_pages(str(three_page_pdf), str(output), [0])

        reader = PdfReader.open(str(output))
        assert reader.page_count == 1

    def test_extract_multiple_pages(self, three_page_pdf, tmp_dir):
        from oxidize_pdf import PdfReader, extract_pages

        output = tmp_dir / "extracted_multi.pdf"
        extract_pages(str(three_page_pdf), str(output), [0, 2])

        reader = PdfReader.open(str(output))
        assert reader.page_count == 2

    def test_extract_all_pages(self, three_page_pdf, tmp_dir):
        from oxidize_pdf import PdfReader, extract_pages

        output = tmp_dir / "extracted_all.pdf"
        extract_pages(str(three_page_pdf), str(output), [0, 1, 2])

        reader = PdfReader.open(str(output))
        assert reader.page_count == 3

    def test_extract_invalid_page(self, two_page_pdf, tmp_dir):
        from oxidize_pdf import PdfError, extract_pages

        output = tmp_dir / "extracted_bad.pdf"
        with pytest.raises(PdfError):
            extract_pages(str(two_page_pdf), str(output), [99])

    def test_extract_empty_list_raises(self, two_page_pdf, tmp_dir):
        from oxidize_pdf import PdfError, extract_pages

        output = tmp_dir / "extracted_empty.pdf"
        with pytest.raises((PdfError, ValueError)):
            extract_pages(str(two_page_pdf), str(output), [])
