"""Behavioral coverage for the renderer and in-memory APIs added in core 4.6."""

import pytest

from oxidize_pdf import (
    ImageExtractionLimits,
    PdfReader,
    extract_images_in_memory,
)
from helpers import _minimal_jpeg


def _stream(dictionary: str, data: bytes) -> bytes:
    entries = f"{dictionary} /Length {len(data)}".strip()
    return f"<< {entries} >>\nstream\n".encode() + data + b"\nendstream"


def _pdf(objects: list[bytes]) -> bytes:
    body = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(body))
        body.extend(f"{number} 0 obj\n".encode())
        body.extend(obj)
        body.extend(b"\nendobj\n")
    xref = len(body)
    body.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    body.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        body.extend(f"{offset:010d} 00000 n \n".encode())
    body.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode())
    body.extend(f"startxref\n{xref}\n%%EOF\n".encode())
    return bytes(body)


def _type3_pdf() -> bytes:
    glyph = b"500 0 0 0 8 1 d1 0 0 8 1 re f"
    return _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R /MediaBox [0 0 100 100] >>",
        _stream("", b"BT /F1 12 Tf <10> Tj ET"),
        b"<< /Type /Font /Subtype /Type3 /Name /Fixture /FontBBox [0 0 8 1] /FontMatrix [0.001 0 0 0.001 0 0] /FirstChar 16 /LastChar 16 /Widths 7 0 R /Encoding << /Differences [16 /a16] >> /CharProcs 6 0 R >>",
        b"<< /a16 8 0 R >>",
        b"[500]",
        _stream("", glyph),
    ])


def _image_pdf(image: bytes) -> bytes:
    image_dict = "/Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /DCTDecode"
    return _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 10 10] /Resources << /XObject << /Im0 5 0 R >> >> /Contents 4 0 R >>",
        _stream("", b"q /Im0 Do Q"),
        _stream(image_dict, image),
    ])


def test_resolve_type3_font_and_glyph_program():
    resolved = PdfReader.from_bytes(_type3_pdf()).resolve_font(0, "F1")
    assert resolved.resource_name == "F1"
    assert resolved.subtype == "Type3"
    assert resolved.differences == {16: "a16"}
    assert resolved.type3 is not None
    glyph = resolved.type3.glyph(16)
    assert glyph is not None
    assert (glyph.name, glyph.width, glyph.procedure_width) == ("a16", 500.0, (500.0, 0.0))
    assert glyph.bbox == (0.0, 0.0, 8.0, 1.0)
    assert glyph.operations


def test_decode_type3_glyphs():
    glyphs = PdfReader.from_bytes(_type3_pdf()).resolve_font(0, "/F1").decode_glyphs(b"\x10")
    assert len(glyphs) == 1
    assert glyphs[0].source_code == b"\x10"
    assert glyphs[0].advance == 500.0


def test_extract_images_in_memory_and_enforce_limits(tmp_path):
    jpeg = _minimal_jpeg()
    path = tmp_path / "image.pdf"
    path.write_bytes(_image_pdf(jpeg))

    images = extract_images_in_memory(str(path))
    assert len(images) == 1
    assert (images[0].page_number, images[0].image_index) == (0, 0)
    assert (images[0].width, images[0].height, images[0].format) == (1, 1, "jpeg")
    assert images[0].data == jpeg

    with pytest.raises(ValueError, match="encoded bytes per image"):
        extract_images_in_memory(
            str(path),
            ImageExtractionLimits(max_encoded_bytes_per_image=len(jpeg) - 1),
        )
