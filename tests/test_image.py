"""Tests for Image embedding — Feature 1 (Tier 1)."""

import pytest

from helpers import _minimal_jpeg, _minimal_png


class TestImageConstruction:
    """Test Image factory methods."""

    def test_image_from_jpeg_data(self):
        from oxidize_pdf import Image

        img = Image.from_jpeg_data(_minimal_jpeg())
        assert isinstance(img, Image)

    def test_image_from_png_data(self):
        from oxidize_pdf import Image

        img = Image.from_png_data(_minimal_png())
        assert isinstance(img, Image)

    def test_image_from_file(self, tmp_dir):
        from oxidize_pdf import Image

        jpeg_path = tmp_dir / "test.jpg"
        jpeg_path.write_bytes(_minimal_jpeg())
        img = Image.from_file(str(jpeg_path))
        assert isinstance(img, Image)

    def test_image_accessors(self):
        from oxidize_pdf import Image

        img = Image.from_png_data(_minimal_png())
        assert img.width == 1
        assert img.height == 1
        assert isinstance(img.has_transparency, bool)

    def test_image_from_invalid_data_raises(self):
        from oxidize_pdf import Image, PdfError

        with pytest.raises(PdfError):
            Image.from_jpeg_data(b"not a jpeg")


class TestImageOnPage:
    """Test adding and drawing images on pages."""

    def test_page_add_and_draw_image(self):
        from oxidize_pdf import Document, Image, Page

        img = Image.from_png_data(_minimal_png())
        page = Page.a4()
        page.add_image("logo", img)
        page.draw_image("logo", 100.0, 100.0, 200.0, 150.0)

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()

        assert isinstance(data, bytes)
        assert data[:5] == b"%PDF-"
        assert len(data) > 0

    def test_draw_image_unknown_name_raises(self):
        from oxidize_pdf import Page, PdfError

        page = Page.a4()
        with pytest.raises(PdfError):
            page.draw_image("missing", 0.0, 0.0, 100.0, 100.0)

    def test_image_repr(self):
        from oxidize_pdf import Image

        img = Image.from_png_data(_minimal_png())
        r = repr(img)
        assert "Image" in r
