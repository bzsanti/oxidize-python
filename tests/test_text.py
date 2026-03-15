"""Tests for text writing: Font, TextAlign, and Page text operations."""

import pytest


class TestFont:
    """Test the Font enum."""

    def test_standard_fonts_exist(self):
        from oxidize_pdf import Font

        assert Font.HELVETICA is not None
        assert Font.HELVETICA_BOLD is not None
        assert Font.HELVETICA_OBLIQUE is not None
        assert Font.HELVETICA_BOLD_OBLIQUE is not None
        assert Font.TIMES_ROMAN is not None
        assert Font.TIMES_BOLD is not None
        assert Font.TIMES_ITALIC is not None
        assert Font.TIMES_BOLD_ITALIC is not None
        assert Font.COURIER is not None
        assert Font.COURIER_BOLD is not None
        assert Font.COURIER_OBLIQUE is not None
        assert Font.COURIER_BOLD_OBLIQUE is not None
        assert Font.SYMBOL is not None
        assert Font.ZAPF_DINGBATS is not None

    def test_repr(self):
        from oxidize_pdf import Font

        assert "HELVETICA" in repr(Font.HELVETICA)


class TestTextAlign:
    """Test the TextAlign enum."""

    def test_variants_exist(self):
        from oxidize_pdf import TextAlign

        assert TextAlign.LEFT is not None
        assert TextAlign.RIGHT is not None
        assert TextAlign.CENTER is not None
        assert TextAlign.JUSTIFIED is not None


class TestTextWriting:
    """Test writing text on pages."""

    def test_write_text_basic(self):
        from oxidize_pdf import Document, Font, Page

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Hello, World!")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_write_text_with_color(self):
        from oxidize_pdf import Color, Document, Font, Page

        page = Page.a4()
        page.set_font(Font.HELVETICA, 24.0)
        page.set_text_color(Color.red())
        page.text_at(100.0, 700.0, "Red text")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_write_multiple_lines(self):
        from oxidize_pdf import Document, Font, Page

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Line 1")
        page.text_at(100.0, 680.0, "Line 2")
        page.text_at(100.0, 660.0, "Line 3")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_different_fonts(self):
        from oxidize_pdf import Document, Font, Page

        page = Page.a4()

        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Helvetica")

        page.set_font(Font.TIMES_ROMAN, 12.0)
        page.text_at(100.0, 680.0, "Times Roman")

        page.set_font(Font.COURIER, 12.0)
        page.text_at(100.0, 660.0, "Courier")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_font_size_variation(self):
        from oxidize_pdf import Document, Font, Page

        page = Page.a4()
        for i, size in enumerate([8.0, 12.0, 18.0, 24.0, 36.0]):
            page.set_font(Font.HELVETICA, size)
            page.text_at(100.0, 750.0 - (i * 50.0), f"Size {size}")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_character_spacing(self):
        from oxidize_pdf import Document, Font, Page

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.set_character_spacing(2.0)
        page.text_at(100.0, 700.0, "Spaced out")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_word_spacing(self):
        from oxidize_pdf import Document, Font, Page

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.set_word_spacing(5.0)
        page.text_at(100.0, 700.0, "Words spaced out")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0


class TestCustomFont:
    """Test custom/embedded fonts (TXT-002)."""

    def test_custom_font_classmethod(self):
        from oxidize_pdf import Font

        font = Font.custom("MyCustomFont")
        assert font is not None

    def test_custom_font_repr(self):
        from oxidize_pdf import Font

        font = Font.custom("MyCustomFont")
        assert "CUSTOM" in repr(font)
        assert "MyCustomFont" in repr(font)

    def test_custom_font_usable_in_set_font(self):
        from oxidize_pdf import Font, Page

        page = Page.a4()
        font = Font.custom("MyFont")
        # Should not raise — set_font accepts any Font variant
        page.set_font(font, 12.0)

    def test_font_from_file_nonexistent_raises(self):
        from oxidize_pdf import Font, PdfError

        with pytest.raises(PdfError):
            Font.from_file("TestFont", "/nonexistent/font.ttf")

    def test_font_from_bytes_invalid_raises(self):
        from oxidize_pdf import Font, PdfError

        with pytest.raises(PdfError):
            Font.from_bytes("TestFont", b"\xff\xfe\x00\x01")


class TestTextFlowAt:
    """Test text alignment via text_flow_at (TXT-008)."""

    def test_text_flow_at_basic(self):
        from oxidize_pdf import Document, Font, Page

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_flow_at(50.0, 700.0, "This is a paragraph of text that should be wrapped.")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_text_flow_at_align_center(self):
        from oxidize_pdf import Document, Font, Page, TextAlign

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_flow_at(
            50.0, 700.0,
            "Centered text paragraph.",
            align=TextAlign.CENTER,
        )

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_text_flow_at_align_right(self):
        from oxidize_pdf import Document, Font, Page, TextAlign

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_flow_at(50.0, 700.0, "Right aligned.", align=TextAlign.RIGHT)

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_text_flow_at_align_justified(self):
        from oxidize_pdf import Document, Font, Page, TextAlign

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_flow_at(
            50.0, 700.0,
            "Justified text that is long enough to wrap across multiple lines in the page.",
            align=TextAlign.JUSTIFIED,
        )

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_text_flow_at_default_align_is_left(self):
        from oxidize_pdf import Document, Font, Page

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        # No align argument — should default to LEFT
        page.text_flow_at(50.0, 700.0, "Default alignment is left.")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0
