"""Tests for the oxidize_pdf error system."""

import pytest


class TestPdfErrorBase:
    """Test the base PdfError exception."""

    def test_pdf_error_exists(self):
        from oxidize_pdf import PdfError

        assert PdfError is not None

    def test_pdf_error_is_exception(self):
        from oxidize_pdf import PdfError

        assert issubclass(PdfError, Exception)

    def test_pdf_error_can_be_raised(self):
        from oxidize_pdf import PdfError

        with pytest.raises(PdfError):
            raise PdfError("test error")

    def test_pdf_error_message(self):
        from oxidize_pdf import PdfError

        try:
            raise PdfError("something went wrong")
        except PdfError as e:
            assert "something went wrong" in str(e)

    def test_pdf_error_caught_by_exception(self):
        """PdfError should be catchable as a generic Exception."""
        from oxidize_pdf import PdfError

        with pytest.raises(Exception):
            raise PdfError("generic catch")


class TestErrorSubclasses:
    """Test specialized error subclasses."""

    def test_parse_error_exists(self):
        from oxidize_pdf import PdfParseError

        assert issubclass(PdfParseError, Exception)

    def test_parse_error_is_subclass_of_pdf_error(self):
        from oxidize_pdf import PdfError, PdfParseError

        assert issubclass(PdfParseError, PdfError)

    def test_io_error_is_subclass_of_pdf_error(self):
        from oxidize_pdf import PdfError, PdfIoError

        assert issubclass(PdfIoError, PdfError)

    def test_encryption_error_is_subclass_of_pdf_error(self):
        from oxidize_pdf import PdfEncryptionError, PdfError

        assert issubclass(PdfEncryptionError, PdfError)

    def test_permission_error_is_subclass_of_pdf_error(self):
        from oxidize_pdf import PdfError, PdfPermissionError

        assert issubclass(PdfPermissionError, PdfError)

    def test_subclass_caught_by_parent(self):
        """All subclasses should be catchable as PdfError."""
        from oxidize_pdf import PdfError, PdfIoError, PdfParseError

        with pytest.raises(PdfError):
            raise PdfParseError("parse failed")

        with pytest.raises(PdfError):
            raise PdfIoError("io failed")

    def test_subclass_not_caught_by_sibling(self):
        """Sibling errors should not catch each other."""
        from oxidize_pdf import PdfEncryptionError, PdfParseError

        with pytest.raises(PdfParseError):
            raise PdfParseError("parse")

        with pytest.raises(PdfEncryptionError):
            raise PdfEncryptionError("encrypt")

        # ParseError should NOT catch EncryptionError
        with pytest.raises(PdfEncryptionError):
            try:
                raise PdfEncryptionError("encrypt")
            except PdfParseError:
                pytest.fail("PdfParseError should not catch PdfEncryptionError")
