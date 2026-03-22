"""Tests for ParseOptions — Feature 42 (Tier 1.5)."""

import pytest


class TestParseOptionsPresets:
    def test_strict(self):
        from oxidize_pdf import ParseOptions

        opts = ParseOptions.strict()
        assert isinstance(opts, ParseOptions)
        assert opts.strict_mode is True
        assert opts.lenient_streams is False

    def test_tolerant(self):
        from oxidize_pdf import ParseOptions

        opts = ParseOptions.tolerant()
        assert isinstance(opts, ParseOptions)
        assert opts.strict_mode is False
        assert opts.lenient_streams is True

    def test_lenient(self):
        from oxidize_pdf import ParseOptions

        opts = ParseOptions.lenient()
        assert isinstance(opts, ParseOptions)
        assert opts.strict_mode is False

    def test_skip_errors(self):
        from oxidize_pdf import ParseOptions

        opts = ParseOptions.skip_errors()
        assert isinstance(opts, ParseOptions)
        assert opts.ignore_corrupt_streams is True


class TestParseOptionsCustom:
    def test_custom_construction(self):
        from oxidize_pdf import ParseOptions

        opts = ParseOptions(
            strict_mode=False,
            lenient_streams=True,
            recover_from_stream_errors=True,
        )
        assert opts.strict_mode is False
        assert opts.lenient_streams is True
        assert opts.recover_from_stream_errors is True

    def test_default_values(self):
        from oxidize_pdf import ParseOptions

        opts = ParseOptions()
        assert opts.strict_mode is True
        assert opts.lenient_streams is False
        assert opts.collect_warnings is False
        assert opts.lenient_encoding is True


class TestReaderWithOptions:
    def test_reader_open_with_strict(self, tmp_path):
        from oxidize_pdf import Document, Font, Page, ParseOptions, PdfReader

        # Create a valid PDF
        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Test")
        doc.add_page(page)
        path = str(tmp_path / "test.pdf")
        doc.save(path)

        reader = PdfReader.open(path, options=ParseOptions.strict())
        assert reader.page_count > 0

    def test_reader_open_with_tolerant(self, tmp_path):
        from oxidize_pdf import Document, Font, Page, ParseOptions, PdfReader

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Tolerant test")
        doc.add_page(page)
        path = str(tmp_path / "test.pdf")
        doc.save(path)

        reader = PdfReader.open(path, options=ParseOptions.tolerant())
        assert reader.page_count > 0

    def test_reader_open_without_options(self, tmp_path):
        from oxidize_pdf import Document, Font, Page, PdfReader

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "No options")
        doc.add_page(page)
        path = str(tmp_path / "test.pdf")
        doc.save(path)

        reader = PdfReader.open(path)
        assert reader.page_count > 0

    def test_reader_from_bytes_with_options(self):
        from oxidize_pdf import Document, Font, Page, ParseOptions, PdfReader

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Bytes test")
        doc.add_page(page)
        data = doc.save_to_bytes()

        reader = PdfReader.from_bytes(data, options=ParseOptions.strict())
        assert reader.page_count > 0

    def test_strict_rejects_malformed(self):
        from oxidize_pdf import ParseOptions, PdfParseError, PdfReader

        with pytest.raises((PdfParseError, Exception)):
            PdfReader.from_bytes(b"not-a-pdf", options=ParseOptions.strict())
