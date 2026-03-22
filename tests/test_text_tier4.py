"""Tests for Tier 4 — Advanced Text (Features 16-18)."""

import pytest


class TestHorizontalScaling:
    def test_set_horizontal_scaling(self):
        from oxidize_pdf import Document, Font, Page

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.set_horizontal_scaling(150.0)
        page.text_at(72.0, 700.0, "Stretched text")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_horizontal_scaling_100_is_normal(self):
        from oxidize_pdf import Document, Font, Page

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.set_horizontal_scaling(100.0)
        page.text_at(72.0, 700.0, "Normal text")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


class TestTextRise:
    def test_set_text_rise(self):
        from oxidize_pdf import Document, Font, Page

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.set_text_rise(5.0)
        page.text_at(72.0, 700.0, "Superscript")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_text_rise_negative(self):
        from oxidize_pdf import Document, Font, Page

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.set_text_rise(-3.0)
        page.text_at(72.0, 700.0, "Subscript")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


class TestTextRenderingMode:
    def test_rendering_mode_variants(self):
        from oxidize_pdf import TextRenderingMode

        assert TextRenderingMode.FILL is not None
        assert TextRenderingMode.STROKE is not None
        assert TextRenderingMode.FILL_STROKE is not None
        assert TextRenderingMode.INVISIBLE is not None
        assert TextRenderingMode.FILL_CLIP is not None
        assert TextRenderingMode.STROKE_CLIP is not None
        assert TextRenderingMode.FILL_STROKE_CLIP is not None
        assert TextRenderingMode.CLIP is not None

    def test_set_rendering_mode_stroke(self):
        from oxidize_pdf import Document, Font, Page, TextRenderingMode

        page = Page.a4()
        page.set_font(Font.HELVETICA, 36.0)
        page.set_rendering_mode(TextRenderingMode.STROKE)
        page.text_at(72.0, 700.0, "Outlined")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_set_rendering_mode_fill_stroke(self):
        from oxidize_pdf import Document, Font, Page, TextRenderingMode

        page = Page.a4()
        page.set_font(Font.HELVETICA, 36.0)
        page.set_rendering_mode(TextRenderingMode.FILL_STROKE)
        page.text_at(72.0, 700.0, "Bold outline")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
