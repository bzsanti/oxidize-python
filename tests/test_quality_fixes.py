"""Tests for quality review fixes — 11 cycles."""

import pytest


# ── Cycle 1: Font repr (no Box::leak) ────────────────────────────────────


class TestFontRepr:
    def test_standard_font_reprs(self):
        from oxidize_pdf import Font

        cases = [
            (Font.HELVETICA, "Font.HELVETICA"),
            (Font.HELVETICA_BOLD, "Font.HELVETICA_BOLD"),
            (Font.COURIER, "Font.COURIER"),
            (Font.SYMBOL, "Font.SYMBOL"),
            (Font.ZAPF_DINGBATS, "Font.ZAPF_DINGBATS"),
            (Font.TIMES_ROMAN, "Font.TIMES_ROMAN"),
        ]
        for font, expected in cases:
            assert repr(font) == expected


# ── Cycle 2: page_index removed from form methods ────────────────────────


class TestFormMethodSignatures:
    def test_add_text_field_rejects_three_positional_args(self):
        from oxidize_pdf import Document, Point, Rectangle, TextField

        doc = Document()
        doc.enable_forms()
        tf = TextField("f")
        rect = Rectangle(Point(0.0, 0.0), Point(100.0, 20.0))
        with pytest.raises(TypeError):
            doc.add_text_field(0, tf, rect)

    def test_add_text_field_two_args(self):
        from oxidize_pdf import Document, Font, Page, Point, Rectangle, TextField

        doc = Document()
        doc.enable_forms()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Label")
        doc.add_page(page)
        tf = TextField("f")
        rect = Rectangle(Point(100.0, 690.0), Point(300.0, 715.0))
        doc.add_text_field(tf, rect)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_add_checkbox_two_args(self):
        from oxidize_pdf import CheckBox, Document, Point, Rectangle

        doc = Document()
        doc.enable_forms()
        doc.add_page(__import__("oxidize_pdf").Page.a4())
        doc.add_checkbox(CheckBox("c"), Rectangle(Point(0.0, 0.0), Point(20.0, 20.0)))

    def test_add_combo_box_two_args(self):
        from oxidize_pdf import ComboBox, Document, Point, Rectangle

        doc = Document()
        doc.enable_forms()
        doc.add_page(__import__("oxidize_pdf").Page.a4())
        doc.add_combo_box(
            ComboBox("c").add_option("a", "A"),
            Rectangle(Point(0.0, 0.0), Point(100.0, 20.0)),
        )

    def test_add_list_box_two_args(self):
        from oxidize_pdf import Document, ListBox, Point, Rectangle

        doc = Document()
        doc.enable_forms()
        doc.add_page(__import__("oxidize_pdf").Page.a4())
        doc.add_list_box(
            ListBox("l").add_option("a", "A"),
            Rectangle(Point(0.0, 0.0), Point(100.0, 50.0)),
        )

    def test_add_radio_button_two_args(self):
        from oxidize_pdf import Document, Point, RadioButton, Rectangle

        doc = Document()
        doc.enable_forms()
        doc.add_page(__import__("oxidize_pdf").Page.a4())
        doc.add_radio_button(
            RadioButton("r").add_option("a", "A"),
            Rectangle(Point(0.0, 0.0), Point(20.0, 20.0)),
        )


# ── Cycle 3: detect_signatures raises after promotion ────────────────────


class TestDetectSignatures:
    def _make_pdf_bytes(self):
        from oxidize_pdf import Document, Font, Page

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "test")
        doc.add_page(page)
        return doc.save_to_bytes()

    def test_returns_list_on_unsigned_pdf(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(self._make_pdf_bytes())
        result = reader.detect_signatures()
        assert isinstance(result, list)
        assert len(result) == 0


# ── Cycle 6: set_open_action_uri with is_map ─────────────────────────────


class TestSetOpenActionUriIsMap:
    def test_default_is_map_false(self):
        from oxidize_pdf import Document, Font, Page, UriAction

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Content")
        doc.add_page(page)
        doc.set_open_action_uri(UriAction("https://example.com"))
        assert doc.save_to_bytes()[:5] == b"%PDF-"

    def test_explicit_is_map_true(self):
        from oxidize_pdf import Document, Font, Page, UriAction

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Content")
        doc.add_page(page)
        doc.set_open_action_uri(UriAction("https://example.com"), is_map=True)
        assert doc.save_to_bytes()[:5] == b"%PDF-"


# ── Cycle 7: WriterConfig with kwargs ─────────────────────────────────────


class TestWriterConfigKwargs:
    def test_keyword_constructor(self):
        from oxidize_pdf import WriterConfig

        cfg = WriterConfig(compress_streams=True, use_xref_streams=False)
        assert cfg.compress_streams is True
        assert cfg.use_xref_streams is False

    def test_all_keyword_args(self):
        from oxidize_pdf import WriterConfig

        cfg = WriterConfig(
            compress_streams=False,
            use_xref_streams=True,
            use_object_streams=False,
        )
        assert cfg.compress_streams is False
        assert cfg.use_xref_streams is True
        assert cfg.use_object_streams is False

    def test_default_constructor_still_works(self):
        from oxidize_pdf import WriterConfig

        cfg = WriterConfig()
        assert isinstance(cfg, WriterConfig)


# ── Cycle 8: ParsedPage and TextChunk exports ────────────────────────────


class TestMissingExports:
    def test_parsed_page_importable(self):
        from oxidize_pdf import ParsedPage

        assert ParsedPage is not None

    def test_text_chunk_importable(self):
        from oxidize_pdf import TextChunk

        assert TextChunk is not None

    def test_in_all(self):
        import oxidize_pdf

        assert "ParsedPage" in oxidize_pdf.__all__
        assert "TextChunk" in oxidize_pdf.__all__


# ── Cycle 9: Certificate validation ──────────────────────────────────────


class TestRecipientValidation:
    def test_empty_cert_raises(self):
        from oxidize_pdf import Recipient

        with pytest.raises(ValueError):
            Recipient.from_certificate(b"")

    def test_too_short_cert_raises(self):
        from oxidize_pdf import Recipient

        with pytest.raises(ValueError):
            Recipient.from_certificate(bytes([0x30]))

    def test_non_der_cert_raises(self):
        from oxidize_pdf import Recipient

        with pytest.raises(ValueError):
            Recipient.from_certificate(b"not a certificate at all but long enough to pass length")

    def test_valid_der_header_accepted(self):
        from oxidize_pdf import Recipient

        fake_cert = bytes([0x30, 0x82]) + b"\x00" * 64
        r = Recipient.from_certificate(fake_cert)
        assert repr(r).startswith("Recipient(")


# ── Cycle 10: set_rotation validation ─────────────────────────────────────


class TestPageRotationValidation:
    def test_valid_rotations(self):
        from oxidize_pdf import Page

        for deg in [0, 90, 180, 270]:
            page = Page.a4()
            page.set_rotation(deg)
            assert page.rotation == deg

    def test_invalid_rotations(self):
        from oxidize_pdf import Page

        for deg in [45, -90, 360, 1, 91]:
            page = Page.a4()
            with pytest.raises(ValueError):
                page.set_rotation(deg)


# ── Cycle 11: Opacity validation ──────────────────────────────────────────


class TestOpacityValidation:
    def test_valid_fill_opacity(self):
        from oxidize_pdf import Page

        page = Page.a4()
        page.set_fill_opacity(0.0)
        page.set_fill_opacity(0.5)
        page.set_fill_opacity(1.0)

    def test_fill_opacity_below_range(self):
        from oxidize_pdf import Page

        with pytest.raises(ValueError):
            Page.a4().set_fill_opacity(-0.1)

    def test_fill_opacity_above_range(self):
        from oxidize_pdf import Page

        with pytest.raises(ValueError):
            Page.a4().set_fill_opacity(1.001)

    def test_valid_stroke_opacity(self):
        from oxidize_pdf import Page

        page = Page.a4()
        page.set_stroke_opacity(0.0)
        page.set_stroke_opacity(1.0)

    def test_stroke_opacity_out_of_range(self):
        from oxidize_pdf import Page

        with pytest.raises(ValueError):
            Page.a4().set_stroke_opacity(2.0)
