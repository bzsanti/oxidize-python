"""Page-aware chunks must decode source character codes before exposing text."""
import pytest
from oxidize_pdf import PdfReader


def _pdf(content, *, composite=True, differences=False):
    cmap = b"""/CIDInit /ProcSet findresource begin 12 dict begin begincmap
/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def
/CMapName /Fixture def /CMapType 2 def
1 begincodespacerange <0000> <FFFF> endcodespacerange
3 beginbfchar <0001> <03A9> <0002> <0032> <0003> <00660069> endbfchar
endcmap CMapName currentdict /CMap defineresource pop end end"""
    def stream(data):
        return b"<< /Length " + str(len(data)).encode() + b" >>\nstream\n" + data + b"\nendstream"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 7 0 R >>",
        b"<< /Type /Font /Subtype /Type0 /BaseFont /Fixture /Encoding /Identity-H /DescendantFonts [5 0 R] /ToUnicode 6 0 R >>" if composite else (b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding << /Type /Encoding /BaseEncoding /WinAnsiEncoding /Differences [65 /B] >> >>" if differences else b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"),
        b"<< /Type /Font /Subtype /CIDFontType2 /BaseFont /Fixture /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> /DW 600 >>",
        stream(cmap), stream(content),
    ]
    result = bytearray(b"%PDF-1.7\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(result)
    result.extend(b"xref\n0 8\n0000000000 65535 f \n")
    for offset in offsets[1:]:
        result.extend(f"{offset:010d} 00000 n \n".encode())
    result.extend(f"trailer\n<< /Size 8 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(result)


def test_chunks_decode_tounicode_sequences_with_page_geometry():
    reader = PdfReader.from_bytes(_pdf(b"2 0 0 2 0 0 cm BT /F1 10 Tf 50 200 Td <000100020003> Tj ET"))
    chunks = reader.extract_text_chunks(0)
    assert "".join(chunk.text for chunk in chunks) == "Ω2fi"
    assert chunks[0].x == pytest.approx(100)
    assert chunks[0].y == pytest.approx(400)
    assert chunks[0].font_size == pytest.approx(20)
    assert chunks[0].font_name is not None


def test_chunks_preserve_simple_font_text_and_empty_pages():
    reader = PdfReader.from_bytes(_pdf(b"BT /F1 12 Tf 50 200 Td (Hello) Tj ET", composite=False))
    assert "".join(c.text for c in reader.extract_text_chunks(0)) == "Hello"
    assert PdfReader.from_bytes(_pdf(b"")).extract_text_chunks(0) == []


def test_chunks_reject_page_out_of_range():
    reader = PdfReader.from_bytes(_pdf(b""))
    with pytest.raises(ValueError):
        reader.extract_text_chunks(1)


def test_chunks_keep_content_order_and_coordinate_association():
    content = b"BT /F1 10 Tf 1 0 0 1 80 100 Tm (Bottom) Tj 1 0 0 1 30 300 Tm (Top) Tj ET"
    chunks = PdfReader.from_bytes(_pdf(content, composite=False)).extract_text_chunks(0)
    assert [chunk.text for chunk in chunks] == ["Bottom", "Top"]
    assert [(chunk.x, chunk.y) for chunk in chunks] == [(80, 100), (30, 300)]


def test_chunks_preserve_artifact_text():
    content = b"/Artifact BMC BT /F1 10 Tf 50 200 Td (Disclaimer) Tj ET EMC"
    chunks = PdfReader.from_bytes(_pdf(content, composite=False)).extract_text_chunks(0)
    assert "".join(chunk.text for chunk in chunks) == "Disclaimer"


def test_chunks_preserve_figure_text_with_custom_encoding():
    content = b"/Figure BMC BT /F1 10 Tf 50 200 Td (A) Tj ET EMC"
    chunks = PdfReader.from_bytes(_pdf(content, composite=False, differences=True)).extract_text_chunks(0)
    assert "".join(chunk.text for chunk in chunks) == "B"
