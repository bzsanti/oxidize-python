"""Tests for OPS-002: split_pdf_with_options + SplitOptions + SplitMode.ranges."""

import pytest


def _make_pdf(tmp_dir, page_count=4, name="doc.pdf"):
    """Create a PDF with N pages each labelled 'Page i'."""
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


# ── SplitMode.ranges constructor ──────────────────────────────────────────────


class TestSplitModeRanges:
    def test_ranges_constructor_empty(self):
        from oxidize_pdf import SplitMode

        sm = SplitMode.ranges([])
        assert isinstance(sm, SplitMode)

    def test_ranges_constructor_single_range(self):
        from oxidize_pdf import PageRange, SplitMode

        sm = SplitMode.ranges([PageRange.range(0, 1)])
        assert isinstance(sm, SplitMode)
        assert "ranges" in repr(sm).lower()

    def test_ranges_constructor_multiple_ranges(self):
        from oxidize_pdf import PageRange, SplitMode

        sm = SplitMode.ranges(
            [
                PageRange.single(0),
                PageRange.range(1, 2),
                PageRange.list([3]),
            ]
        )
        assert isinstance(sm, SplitMode)


# ── SplitOptions construction ────────────────────────────────────────────────


class TestSplitOptionsConstruction:
    def test_default_construction_requires_mode(self):
        from oxidize_pdf import SplitMode, SplitOptions

        opts = SplitOptions(SplitMode.single_pages())
        assert isinstance(opts, SplitOptions)

    def test_full_construction(self):
        from oxidize_pdf import SplitMode, SplitOptions

        opts = SplitOptions(
            SplitMode.chunk_size(2),
            output_pattern="part_{}.pdf",
            preserve_metadata=False,
            optimize=True,
        )
        assert isinstance(opts, SplitOptions)
        repr_str = repr(opts)
        assert "part_" in repr_str

    def test_repr_includes_pattern(self):
        from oxidize_pdf import SplitMode, SplitOptions

        opts = SplitOptions(SplitMode.single_pages(), output_pattern="custom_{}.pdf")
        assert "custom_" in repr(opts)


# ── split_pdf_with_options behaviour ─────────────────────────────────────────


class TestSplitPdfWithOptions:
    def test_single_pages_produces_one_file_per_page(self, tmp_path):
        from oxidize_pdf import (
            PdfReader,
            SplitMode,
            SplitOptions,
            split_pdf_with_options,
        )

        pdf = _make_pdf(tmp_path, page_count=3)
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        opts = SplitOptions(
            SplitMode.single_pages(),
            output_pattern=str(out_dir / "page_{}.pdf"),
        )

        paths = split_pdf_with_options(str(pdf), opts)

        assert len(paths) == 3
        for path in paths:
            reader = PdfReader.open(path)
            assert reader.page_count == 1

    def test_chunk_size_groups_pages(self, tmp_path):
        from oxidize_pdf import (
            PdfReader,
            SplitMode,
            SplitOptions,
            split_pdf_with_options,
        )

        pdf = _make_pdf(tmp_path, page_count=5)
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        opts = SplitOptions(
            SplitMode.chunk_size(2),
            output_pattern=str(out_dir / "chunk_{}.pdf"),
        )

        paths = split_pdf_with_options(str(pdf), opts)

        assert len(paths) == 3  # ceil(5/2)
        page_counts = []
        for path in paths:
            reader = PdfReader.open(path)
            page_counts.append(reader.page_count)
        # Two chunks of 2, last chunk of 1
        assert page_counts == [2, 2, 1]

    def test_ranges_mode_produces_one_file_per_range(self, tmp_path):
        from oxidize_pdf import (
            PageRange,
            PdfReader,
            SplitMode,
            SplitOptions,
            split_pdf_with_options,
        )

        pdf = _make_pdf(tmp_path, page_count=6)
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        opts = SplitOptions(
            SplitMode.ranges(
                [PageRange.range(0, 1), PageRange.single(3), PageRange.range(4, 5)]
            ),
            output_pattern=str(out_dir / "rng_{}.pdf"),
        )

        paths = split_pdf_with_options(str(pdf), opts)

        assert len(paths) == 3
        r0 = PdfReader.open(paths[0])
        assert r0.page_count == 2
        r1 = PdfReader.open(paths[1])
        assert r1.page_count == 1
        r2 = PdfReader.open(paths[2])
        assert r2.page_count == 2

    def test_ranges_mode_preserves_text_content(self, tmp_path):
        from oxidize_pdf import (
            PageRange,
            PdfReader,
            SplitMode,
            SplitOptions,
            split_pdf_with_options,
        )

        pdf = _make_pdf(tmp_path, page_count=5)
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        opts = SplitOptions(
            SplitMode.ranges([PageRange.single(2)]),
            output_pattern=str(out_dir / "single_{}.pdf"),
        )

        paths = split_pdf_with_options(str(pdf), opts)

        assert len(paths) == 1
        reader = PdfReader.open(paths[0])
        text = reader.extract_text_from_page(0)
        assert "Page 3" in text

    def test_output_pattern_is_honoured(self, tmp_path):
        import os

        from oxidize_pdf import SplitMode, SplitOptions, split_pdf_with_options

        pdf = _make_pdf(tmp_path, page_count=2)
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        opts = SplitOptions(
            SplitMode.single_pages(),
            output_pattern=str(out_dir / "myfile_{}.pdf"),
        )

        paths = split_pdf_with_options(str(pdf), opts)

        for path in paths:
            assert "myfile_" in os.path.basename(path)
            assert path.endswith(".pdf")

    def test_split_at_mode(self, tmp_path):
        from oxidize_pdf import (
            PdfReader,
            SplitMode,
            SplitOptions,
            split_pdf_with_options,
        )

        pdf = _make_pdf(tmp_path, page_count=5)
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        opts = SplitOptions(
            SplitMode.split_at([2]),
            output_pattern=str(out_dir / "part_{}.pdf"),
        )

        paths = split_pdf_with_options(str(pdf), opts)

        # split_at([2]) creates: pages 0-1, then 2-4
        assert len(paths) == 2
        r = PdfReader.open(paths[0])
        assert r.page_count == 2
        r = PdfReader.open(paths[1])
        assert r.page_count == 3
