"""Tests for Image embedding — Feature 1 (Tier 1)."""

import struct

import pytest


def _minimal_jpeg() -> bytes:
    """Create a minimal valid JPEG (1x1 red pixel)."""
    return bytes([
        0xFF, 0xD8, 0xFF, 0xE0,  # SOI + APP0 marker
        0x00, 0x10,               # length = 16
        0x4A, 0x46, 0x49, 0x46, 0x00,  # "JFIF\0"
        0x01, 0x01,               # version 1.1
        0x00,                     # aspect ratio units: none
        0x00, 0x01, 0x00, 0x01,  # density 1x1
        0x00, 0x00,               # no thumbnail
        0xFF, 0xDB,               # DQT marker
        0x00, 0x43, 0x00,         # length=67, table 0
    ] + [0x01] * 64 + [           # 64-byte quantization table
        0xFF, 0xC0,               # SOF0 marker
        0x00, 0x0B,               # length=11
        0x08,                     # 8-bit precision
        0x00, 0x01, 0x00, 0x01,  # height=1, width=1
        0x01,                     # 1 component
        0x01, 0x11, 0x00,         # comp 1: id=1, sampling=1x1, quant table 0
        0xFF, 0xC4,               # DHT marker
        0x00, 0x1F, 0x00,         # length=31, DC table 0
    ] + [0x00] * 16 + [           # 16-byte symbol counts (all zero)
        0xFF, 0xC4,               # DHT marker
        0x00, 0x1F, 0x10,         # length=31, AC table 0
    ] + [0x00] * 16 + [           # 16-byte symbol counts (all zero)
        0xFF, 0xDA,               # SOS marker
        0x00, 0x08,               # length=8
        0x01,                     # 1 component
        0x01, 0x00,               # comp 1: DC table 0, AC table 0
        0x00, 0x3F, 0x00,         # spectral selection 0-63, ah=0 al=0
        0x7F, 0x50,               # minimal scan data
        0xFF, 0xD9,               # EOI
    ])


def _minimal_png() -> bytes:
    """Create a minimal valid PNG (1x1 red pixel)."""
    import zlib

    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        raw = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(raw) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + raw + crc

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    ihdr = _chunk(b"IHDR", ihdr_data)
    raw_row = b"\x00\xFF\x00\x00"  # filter=None + R=255, G=0, B=0
    idat = _chunk(b"IDAT", zlib.compress(raw_row))
    iend = _chunk(b"IEND", b"")
    return signature + ihdr + idat + iend


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
