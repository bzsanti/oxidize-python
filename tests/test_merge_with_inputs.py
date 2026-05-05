"""Tests for OPS-004: MergeInput pyclass + merge_pdfs_with_inputs.

`MergeInput` carries an optional per-file `PageRange`; the merger consumes that
to select pages from each input. `MergeOptions.page_ranges` is intentionally
NOT exposed because the upstream merger ignores it (uses `MergeInput.pages`).
"""

import pytest


def _make_labelled_pdf(tmp_dir, label, page_count=3):
    """Create a PDF with N pages labelled '<label> page i'."""
    from oxidize_pdf import Document, Font, Page

    doc = Document()
    for i in range(page_count):
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, f"{label} page {i + 1}")
        doc.add_page(page)
    path = tmp_dir / f"{label}.pdf"
    doc.save(str(path))
    return path


# ── MergeInput construction ──────────────────────────────────────────────────


class TestMergeInputConstruction:
    def test_default_constructor_path_only(self, tmp_path):
        from oxidize_pdf import MergeInput

        pdf = _make_labelled_pdf(tmp_path, "alpha", page_count=2)
        mi = MergeInput(str(pdf))
        assert isinstance(mi, MergeInput)

    def test_constructor_with_page_range_kwarg(self, tmp_path):
        from oxidize_pdf import MergeInput, PageRange

        pdf = _make_labelled_pdf(tmp_path, "beta", page_count=4)
        mi = MergeInput(str(pdf), pages=PageRange.range(0, 1))
        assert isinstance(mi, MergeInput)

    def test_with_pages_static_constructor(self, tmp_path):
        from oxidize_pdf import MergeInput, PageRange

        pdf = _make_labelled_pdf(tmp_path, "gamma", page_count=3)
        mi = MergeInput.with_pages(str(pdf), PageRange.single(1))
        assert isinstance(mi, MergeInput)

    def test_repr_includes_path_basename(self, tmp_path):
        from oxidize_pdf import MergeInput

        pdf = _make_labelled_pdf(tmp_path, "delta", page_count=1)
        mi = MergeInput(str(pdf))
        repr_str = repr(mi)
        assert "delta" in repr_str

    def test_repr_indicates_page_range_when_set(self, tmp_path):
        from oxidize_pdf import MergeInput, PageRange

        pdf = _make_labelled_pdf(tmp_path, "epsilon", page_count=4)
        mi = MergeInput(str(pdf), pages=PageRange.range(0, 1))
        repr_str = repr(mi)
        assert "range" in repr_str.lower() or "pages" in repr_str.lower()


# ── merge_pdfs_with_inputs behaviour ─────────────────────────────────────────


class TestMergePdfsWithInputs:
    def test_empty_inputs_raises(self, tmp_path):
        from oxidize_pdf import merge_pdfs_with_inputs

        with pytest.raises(ValueError):
            merge_pdfs_with_inputs([], str(tmp_path / "out.pdf"))

    def test_two_full_inputs_concatenate_all_pages(self, tmp_path):
        from oxidize_pdf import (
            MergeInput,
            PdfReader,
            merge_pdfs_with_inputs,
        )

        a = _make_labelled_pdf(tmp_path, "alpha", page_count=2)
        b = _make_labelled_pdf(tmp_path, "beta", page_count=3)
        out = tmp_path / "merged.pdf"

        merge_pdfs_with_inputs(
            [MergeInput(str(a)), MergeInput(str(b))], str(out)
        )

        reader = PdfReader.open(str(out))
        assert reader.page_count == 5

    def test_per_input_page_range_selects_subset(self, tmp_path):
        from oxidize_pdf import (
            MergeInput,
            PageRange,
            PdfReader,
            merge_pdfs_with_inputs,
        )

        a = _make_labelled_pdf(tmp_path, "alpha", page_count=4)
        b = _make_labelled_pdf(tmp_path, "beta", page_count=4)
        out = tmp_path / "merged.pdf"

        merge_pdfs_with_inputs(
            [
                MergeInput(str(a), pages=PageRange.range(0, 1)),
                MergeInput(str(b), pages=PageRange.single(2)),
            ],
            str(out),
        )

        reader = PdfReader.open(str(out))
        assert reader.page_count == 3

        # Verify content: alpha pages 1-2, then beta page 3
        assert "alpha page 1" in reader.extract_text_from_page(0)
        assert "alpha page 2" in reader.extract_text_from_page(1)
        assert "beta page 3" in reader.extract_text_from_page(2)

    def test_with_pages_static_constructor_works_with_merger(self, tmp_path):
        from oxidize_pdf import (
            MergeInput,
            PageRange,
            PdfReader,
            merge_pdfs_with_inputs,
        )

        a = _make_labelled_pdf(tmp_path, "alpha", page_count=3)
        out = tmp_path / "merged.pdf"

        merge_pdfs_with_inputs(
            [MergeInput.with_pages(str(a), PageRange.list([0, 2]))],
            str(out),
        )

        reader = PdfReader.open(str(out))
        assert reader.page_count == 2

    def test_options_none_uses_defaults(self, tmp_path):
        from oxidize_pdf import (
            MergeInput,
            PdfReader,
            merge_pdfs_with_inputs,
        )

        a = _make_labelled_pdf(tmp_path, "alpha", page_count=1)
        b = _make_labelled_pdf(tmp_path, "beta", page_count=1)
        out = tmp_path / "merged.pdf"

        merge_pdfs_with_inputs(
            [MergeInput(str(a)), MergeInput(str(b))],
            str(out),
            options=None,
        )

        reader = PdfReader.open(str(out))
        assert reader.page_count == 2

    def test_options_passed_explicitly(self, tmp_path):
        from oxidize_pdf import (
            MergeInput,
            MergeOptions,
            PdfReader,
            merge_pdfs_with_inputs,
        )

        a = _make_labelled_pdf(tmp_path, "alpha", page_count=2)
        b = _make_labelled_pdf(tmp_path, "beta", page_count=2)
        out = tmp_path / "merged.pdf"

        opts = MergeOptions(preserve_bookmarks=False, preserve_forms=False, optimize=False)
        merge_pdfs_with_inputs(
            [MergeInput(str(a)), MergeInput(str(b))],
            str(out),
            options=opts,
        )

        reader = PdfReader.open(str(out))
        assert reader.page_count == 4

    def test_three_inputs_with_mixed_ranges(self, tmp_path):
        from oxidize_pdf import (
            MergeInput,
            PageRange,
            PdfReader,
            merge_pdfs_with_inputs,
        )

        a = _make_labelled_pdf(tmp_path, "alpha", page_count=3)
        b = _make_labelled_pdf(tmp_path, "beta", page_count=3)
        c = _make_labelled_pdf(tmp_path, "gamma", page_count=3)
        out = tmp_path / "merged.pdf"

        merge_pdfs_with_inputs(
            [
                MergeInput(str(a), pages=PageRange.single(0)),
                MergeInput(str(b)),  # all 3
                MergeInput(str(c), pages=PageRange.range(1, 2)),
            ],
            str(out),
        )

        reader = PdfReader.open(str(out))
        assert reader.page_count == 6  # 1 + 3 + 2

        # Order: alpha p1, beta p1-3, gamma p2-3
        assert "alpha page 1" in reader.extract_text_from_page(0)
        assert "beta page 1" in reader.extract_text_from_page(1)
        assert "beta page 2" in reader.extract_text_from_page(2)
        assert "beta page 3" in reader.extract_text_from_page(3)
        assert "gamma page 2" in reader.extract_text_from_page(4)
        assert "gamma page 3" in reader.extract_text_from_page(5)
