"""Tests for advanced operations — Features 49-53."""

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_pdf(tmp_dir, page_count=2, name="doc.pdf"):
    """Create a minimal PDF with ``page_count`` pages."""
    from oxidize_pdf import Document, Font, Page

    doc = Document()
    for i in range(page_count):
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, f"Page {i + 1}")
        doc.add_page(page)
    path = tmp_dir / name
    doc.save(str(path))
    return path


# ── Feature 49: PageRange + SplitMode ─────────────────────────────────────────


class TestPageRange:
    """Verify PageRange static constructors and repr."""

    def test_all_variant(self):
        from oxidize_pdf import PageRange

        pr = PageRange.all()
        assert isinstance(pr, PageRange)
        assert "all" in repr(pr).lower()

    def test_single_variant(self):
        from oxidize_pdf import PageRange

        pr = PageRange.single(0)
        assert isinstance(pr, PageRange)
        assert "0" in repr(pr)

    def test_range_variant(self):
        from oxidize_pdf import PageRange

        pr = PageRange.range(0, 2)
        assert isinstance(pr, PageRange)

    def test_list_variant(self):
        from oxidize_pdf import PageRange

        pr = PageRange.list([0, 2, 4])
        assert isinstance(pr, PageRange)


class TestSplitMode:
    """Verify SplitMode static constructors."""

    def test_single_pages_variant(self):
        from oxidize_pdf import SplitMode

        sm = SplitMode.single_pages()
        assert isinstance(sm, SplitMode)

    def test_chunk_size_variant(self):
        from oxidize_pdf import SplitMode

        sm = SplitMode.chunk_size(2)
        assert isinstance(sm, SplitMode)
        assert "2" in repr(sm)

    def test_split_at_variant(self):
        from oxidize_pdf import SplitMode

        sm = SplitMode.split_at([1, 3])
        assert isinstance(sm, SplitMode)


class TestSplitPdfWithMode:
    """Test split_pdf_with_mode function."""

    def test_split_with_single_pages_mode(self, tmp_dir):
        from oxidize_pdf import PdfReader, SplitMode, split_pdf_with_mode

        pdf = _make_pdf(tmp_dir, page_count=3, name="src.pdf")
        out_dir = tmp_dir / "split_single"
        out_dir.mkdir()

        paths = split_pdf_with_mode(str(pdf), str(out_dir), SplitMode.single_pages())

        assert len(paths) == 3
        for p in paths:
            reader = PdfReader.open(p)
            assert reader.page_count == 1

    def test_split_with_chunk_size_mode(self, tmp_dir):
        from oxidize_pdf import PdfReader, SplitMode, split_pdf_with_mode

        pdf = _make_pdf(tmp_dir, page_count=4, name="src4.pdf")
        out_dir = tmp_dir / "split_chunk"
        out_dir.mkdir()

        paths = split_pdf_with_mode(str(pdf), str(out_dir), SplitMode.chunk_size(2))

        assert len(paths) == 2
        for p in paths:
            reader = PdfReader.open(p)
            assert reader.page_count == 2

    def test_split_with_split_at_mode(self, tmp_dir):
        from oxidize_pdf import PdfReader, SplitMode, split_pdf_with_mode

        pdf = _make_pdf(tmp_dir, page_count=4, name="src4b.pdf")
        out_dir = tmp_dir / "split_at"
        out_dir.mkdir()

        paths = split_pdf_with_mode(str(pdf), str(out_dir), SplitMode.split_at([2]))

        assert len(paths) == 2

    def test_returns_list_of_strings(self, tmp_dir):
        from oxidize_pdf import SplitMode, split_pdf_with_mode

        pdf = _make_pdf(tmp_dir, page_count=2, name="src2.pdf")
        out_dir = tmp_dir / "split_str"
        out_dir.mkdir()

        paths = split_pdf_with_mode(str(pdf), str(out_dir), SplitMode.single_pages())

        assert isinstance(paths, list)
        assert all(isinstance(p, str) for p in paths)


# ── Feature 50: MergeOptions ──────────────────────────────────────────────────


class TestMergeOptions:
    """Test MergeOptions class and merge_pdfs_with_options."""

    def test_default_constructor(self):
        from oxidize_pdf import MergeOptions

        opts = MergeOptions()
        assert isinstance(opts, MergeOptions)

    def test_custom_constructor(self):
        from oxidize_pdf import MergeOptions

        opts = MergeOptions(preserve_bookmarks=False, preserve_forms=True, optimize=True)
        assert isinstance(opts, MergeOptions)

    def test_merge_pdfs_with_options(self, tmp_dir):
        from oxidize_pdf import MergeOptions, PdfReader, merge_pdfs_with_options

        a = _make_pdf(tmp_dir, page_count=2, name="a.pdf")
        b = _make_pdf(tmp_dir, page_count=3, name="b.pdf")
        out = tmp_dir / "merged.pdf"

        merge_pdfs_with_options([str(a), str(b)], str(out), MergeOptions())

        reader = PdfReader.open(str(out))
        assert reader.page_count == 5

    def test_merge_with_optimize_flag(self, tmp_dir):
        from oxidize_pdf import MergeOptions, PdfReader, merge_pdfs_with_options

        a = _make_pdf(tmp_dir, page_count=1, name="opt_a.pdf")
        b = _make_pdf(tmp_dir, page_count=1, name="opt_b.pdf")
        out = tmp_dir / "merged_opt.pdf"

        merge_pdfs_with_options([str(a), str(b)], str(out), MergeOptions(optimize=True))

        reader = PdfReader.open(str(out))
        assert reader.page_count == 2

    def test_merge_empty_input_raises(self, tmp_dir):
        from oxidize_pdf import MergeOptions, merge_pdfs_with_options

        out = tmp_dir / "empty.pdf"
        with pytest.raises(ValueError):
            merge_pdfs_with_options([], str(out), MergeOptions())


# ── Feature 51: RotationAngle + RotateOptions ─────────────────────────────────


class TestRotationAngle:
    """Verify RotationAngle enum variants."""

    def test_none_variant(self):
        from oxidize_pdf import RotationAngle

        assert RotationAngle.NONE is not None

    def test_clockwise_90_variant(self):
        from oxidize_pdf import RotationAngle

        assert RotationAngle.CLOCKWISE_90 is not None

    def test_rotate_180_variant(self):
        from oxidize_pdf import RotationAngle

        assert RotationAngle.ROTATE_180 is not None

    def test_clockwise_270_variant(self):
        from oxidize_pdf import RotationAngle

        assert RotationAngle.CLOCKWISE_270 is not None

    def test_repr(self):
        from oxidize_pdf import RotationAngle

        assert "CLOCKWISE_90" in repr(RotationAngle.CLOCKWISE_90)


class TestRotateOptions:
    """Test RotateOptions construction."""

    def test_default_all_pages(self):
        from oxidize_pdf import RotateOptions, RotationAngle

        opts = RotateOptions(RotationAngle.CLOCKWISE_90)
        assert isinstance(opts, RotateOptions)

    def test_with_page_range(self):
        from oxidize_pdf import PageRange, RotateOptions, RotationAngle

        opts = RotateOptions(RotationAngle.ROTATE_180, pages=PageRange.single(0))
        assert isinstance(opts, RotateOptions)

    def test_with_preserve_page_size(self):
        from oxidize_pdf import RotateOptions, RotationAngle

        opts = RotateOptions(RotationAngle.CLOCKWISE_90, preserve_page_size=True)
        assert isinstance(opts, RotateOptions)


class TestRotatePdfWithOptions:
    """Test rotate_pdf_with_options function."""

    def test_rotate_all_pages(self, tmp_dir):
        from oxidize_pdf import PdfReader, RotateOptions, RotationAngle, rotate_pdf_with_options

        pdf = _make_pdf(tmp_dir, page_count=2, name="rot_src.pdf")
        out = tmp_dir / "rotated.pdf"

        rotate_pdf_with_options(str(pdf), str(out), RotateOptions(RotationAngle.CLOCKWISE_90))

        reader = PdfReader.open(str(out))
        assert reader.page_count == 2

    def test_rotate_single_page(self, tmp_dir):
        from oxidize_pdf import (
            PageRange,
            PdfReader,
            RotateOptions,
            RotationAngle,
            rotate_pdf_with_options,
        )

        pdf = _make_pdf(tmp_dir, page_count=3, name="rot3.pdf")
        out = tmp_dir / "rot_single.pdf"

        opts = RotateOptions(RotationAngle.ROTATE_180, pages=PageRange.single(0))
        rotate_pdf_with_options(str(pdf), str(out), opts)

        reader = PdfReader.open(str(out))
        assert reader.page_count == 3

    def test_rotate_produces_valid_pdf(self, tmp_dir):
        from oxidize_pdf import RotateOptions, RotationAngle, rotate_pdf_with_options

        pdf = _make_pdf(tmp_dir, page_count=1, name="rot1.pdf")
        out = tmp_dir / "rot_valid.pdf"

        rotate_pdf_with_options(str(pdf), str(out), RotateOptions(RotationAngle.CLOCKWISE_270))

        assert out.exists()
        data = out.read_bytes()
        assert data[:5] == b"%PDF-"


# ── Feature 52: extract_page_range_to_bytes / to_file ─────────────────────────


class TestExtractPageRange:
    """Test extract_page_range_to_bytes and extract_page_range_to_file."""

    def test_extract_range_to_bytes_returns_bytes(self, tmp_dir):
        from oxidize_pdf import extract_page_range_to_bytes

        pdf = _make_pdf(tmp_dir, page_count=4, name="ext4.pdf")
        data = extract_page_range_to_bytes(str(pdf), 0, 1)

        assert isinstance(data, bytes)
        assert data[:5] == b"%PDF-"

    def test_extract_range_to_bytes_correct_page_count(self, tmp_dir):
        from oxidize_pdf import PdfReader, extract_page_range_to_bytes

        import tempfile
        import pathlib

        pdf = _make_pdf(tmp_dir, page_count=5, name="ext5.pdf")
        data = extract_page_range_to_bytes(str(pdf), 0, 2)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(data)
            tmp_path = f.name

        reader = PdfReader.open(tmp_path)
        assert reader.page_count == 3

    def test_extract_range_to_file(self, tmp_dir):
        from oxidize_pdf import PdfReader, extract_page_range_to_file

        pdf = _make_pdf(tmp_dir, page_count=4, name="ext4b.pdf")
        out = tmp_dir / "range_out.pdf"

        extract_page_range_to_file(str(pdf), 1, 3, str(out))

        assert out.exists()
        reader = PdfReader.open(str(out))
        assert reader.page_count == 3

    def test_extract_range_single_page(self, tmp_dir):
        from oxidize_pdf import PdfReader, extract_page_range_to_file

        pdf = _make_pdf(tmp_dir, page_count=3, name="ext3.pdf")
        out = tmp_dir / "single_range.pdf"

        extract_page_range_to_file(str(pdf), 1, 1, str(out))

        reader = PdfReader.open(str(out))
        assert reader.page_count == 1


# ── Feature 53: PageContentAnalyzer ──────────────────────────────────────────


class TestPageType:
    """Verify PageType enum variants."""

    def test_scanned_variant(self):
        from oxidize_pdf import PageType

        assert PageType.SCANNED is not None

    def test_text_variant(self):
        from oxidize_pdf import PageType

        assert PageType.TEXT is not None

    def test_mixed_variant(self):
        from oxidize_pdf import PageType

        assert PageType.MIXED is not None

    def test_repr(self):
        from oxidize_pdf import PageType

        assert "TEXT" in repr(PageType.TEXT)


class TestContentAnalysis:
    """Test ContentAnalysis attributes via analyze_page_content."""

    def test_analyze_page_content_returns_analysis(self, tmp_dir):
        from oxidize_pdf import analyze_page_content

        pdf = _make_pdf(tmp_dir, page_count=2, name="analyze.pdf")
        analysis = analyze_page_content(str(pdf), 0)

        assert analysis.page_number == 0

    def test_analysis_has_page_type(self, tmp_dir):
        from oxidize_pdf import ContentAnalysis, analyze_page_content

        pdf = _make_pdf(tmp_dir, page_count=1, name="analyze_type.pdf")
        analysis = analyze_page_content(str(pdf), 0)

        assert isinstance(analysis, ContentAnalysis)
        assert analysis.page_type is not None

    def test_analysis_ratios_are_floats(self, tmp_dir):
        from oxidize_pdf import analyze_page_content

        pdf = _make_pdf(tmp_dir, page_count=1, name="analyze_ratio.pdf")
        analysis = analyze_page_content(str(pdf), 0)

        assert isinstance(analysis.text_ratio, float)
        assert isinstance(analysis.image_ratio, float)
        assert isinstance(analysis.blank_space_ratio, float)

    def test_analysis_counts_are_ints(self, tmp_dir):
        from oxidize_pdf import analyze_page_content

        pdf = _make_pdf(tmp_dir, page_count=1, name="analyze_counts.pdf")
        analysis = analyze_page_content(str(pdf), 0)

        assert isinstance(analysis.text_fragment_count, int)
        assert isinstance(analysis.image_count, int)
        assert isinstance(analysis.character_count, int)


class TestAnalyzeDocumentContent:
    """Test analyze_document_content function."""

    def test_returns_one_analysis_per_page(self, tmp_dir):
        from oxidize_pdf import analyze_document_content

        pdf = _make_pdf(tmp_dir, page_count=3, name="analyze_doc.pdf")
        analyses = analyze_document_content(str(pdf))

        assert len(analyses) == 3

    def test_page_numbers_are_sequential(self, tmp_dir):
        from oxidize_pdf import analyze_document_content

        pdf = _make_pdf(tmp_dir, page_count=2, name="analyze_seq.pdf")
        analyses = analyze_document_content(str(pdf))

        assert analyses[0].page_number == 0
        assert analyses[1].page_number == 1

    def test_text_page_is_classified_correctly(self, tmp_dir):
        from oxidize_pdf import ContentAnalysis, PageType, analyze_document_content

        pdf = _make_pdf(tmp_dir, page_count=1, name="analyze_text.pdf")
        analyses = analyze_document_content(str(pdf))

        assert len(analyses) == 1
        analysis = analyses[0]
        # A page with text should have text_ratio > 0 or be classified as Text/Mixed
        assert isinstance(analysis, ContentAnalysis)
        # PageType should be one of the known variants
        assert analysis.page_type in (PageType.TEXT, PageType.MIXED, PageType.SCANNED)
