"""F-009 to F-011: Pydantic models for tool inputs and outputs."""

import pytest


class TestCommonModels:
    def test_error_output(self):
        from oxidize_pdf.mcp.models import ErrorOutput

        err = ErrorOutput(error="file not found", code="IO_ERROR")
        assert err.error == "file not found"
        assert err.code == "IO_ERROR"

    def test_session_output(self):
        from oxidize_pdf.mcp.models import SessionOutput

        out = SessionOutput(session_id="abc-123", status="created")
        assert out.session_id == "abc-123"


class TestReadPdfModels:
    def test_read_pdf_input_defaults(self):
        from oxidize_pdf.mcp.models import ReadPdfInput

        inp = ReadPdfInput(path="/tmp/test.pdf")
        assert inp.path == "/tmp/test.pdf"
        assert inp.password is None
        assert inp.include_page_details is False

    def test_read_pdf_input_with_password(self):
        from oxidize_pdf.mcp.models import ReadPdfInput

        inp = ReadPdfInput(path="/tmp/test.pdf", password="secret")
        assert inp.password == "secret"

    def test_read_pdf_output(self):
        from oxidize_pdf.mcp.models import ReadPdfOutput

        out = ReadPdfOutput(
            path="/tmp/test.pdf",
            page_count=3,
            is_encrypted=False,
            version="1.7",
        )
        assert out.page_count == 3
        assert out.is_encrypted is False
        assert out.title is None


class TestExtractConvertModels:
    def test_extract_text_input(self):
        from oxidize_pdf.mcp.models import ExtractTextInput

        inp = ExtractTextInput(path="/tmp/t.pdf", page=0)
        assert inp.page == 0
        inp_all = ExtractTextInput(path="/tmp/t.pdf")
        assert inp_all.page is None

    def test_convert_pdf_input(self):
        from oxidize_pdf.mcp.models import ConvertPdfInput

        inp = ConvertPdfInput(path="/tmp/t.pdf", format="markdown")
        assert inp.format == "markdown"


class TestModelValidation:
    def test_convert_pdf_input_rejects_invalid_format(self):
        from pydantic import ValidationError

        from oxidize_pdf.mcp.models import ConvertPdfInput

        with pytest.raises(ValidationError):
            ConvertPdfInput(path="/tmp/t.pdf", format="xml")

    def test_convert_pdf_input_accepts_all_valid_formats(self):
        from oxidize_pdf.mcp.models import ConvertPdfInput

        for fmt in ("markdown", "chunks", "rag"):
            inp = ConvertPdfInput(path="/tmp/t.pdf", format=fmt)
            assert inp.format == fmt

    def test_read_pdf_input_rejects_missing_path(self):
        from pydantic import ValidationError

        from oxidize_pdf.mcp.models import ReadPdfInput

        with pytest.raises(ValidationError):
            ReadPdfInput()

    def test_extract_text_input_rejects_missing_path(self):
        from pydantic import ValidationError

        from oxidize_pdf.mcp.models import ExtractTextInput

        with pytest.raises(ValidationError):
            ExtractTextInput()
