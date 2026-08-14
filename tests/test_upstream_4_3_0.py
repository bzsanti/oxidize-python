"""Regression coverage for behavior adopted from oxidize-pdf 4.3.0."""

import pytest

import oxidize_pdf as op


def _pdf_with_content_stream(content: bytes) -> bytes:
    """Build a minimal one-page PDF with Helvetica exposed as /F1."""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n"
        + content
        + b"\nendstream",
    ]

    result = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, body in enumerate(objects, start=1):
        offsets.append(len(result))
        result.extend(f"{number} 0 obj\n".encode())
        result.extend(body)
        result.extend(b"\nendobj\n")

    xref_offset = len(result)
    result.extend(b"xref\n0 6\n0000000000 65535 f \n")
    for offset in offsets[1:]:
        result.extend(f"{offset:010d} 00000 n \n".encode())
    result.extend(
        f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode()
    )
    return bytes(result)


TWO_COLUMNS_RIGHT_FIRST = b"""BT
/F1 10 Tf
1 0 0 1 350 700 Tm
[(Right top)] TJ
1 0 0 1 350 680 Tm
[(Right bottom)] TJ
1 0 0 1 50 700 Tm
[(Left top)] TJ
1 0 0 1 50 680 Tm
[(Left bottom)] TJ
ET"""


def test_reading_order_is_opt_in_and_reorders_columns():
    reader = op.PdfReader.from_bytes(_pdf_with_content_stream(TWO_COLUMNS_RIGHT_FIRST))

    assert reader.extract_text_from_page(0) == (
        "Right top\nRight bottom\nLeft top\nLeft bottom"
    )
    assert reader.extract_text_from_page_with_reading_order(0) == (
        "Left top\nLeft bottom\nRight top\nRight bottom"
    )


def test_document_reading_order_returns_one_string_per_page():
    reader = op.PdfReader.from_bytes(_pdf_with_content_stream(TWO_COLUMNS_RIGHT_FIRST))

    assert reader.extract_text_with_reading_order() == [
        "Left top\nLeft bottom\nRight top\nRight bottom"
    ]


def test_text_streamer_honors_td_tstar_and_tm_positioning():
    content = b"""BT
/F1 12 Tf
14 TL
100 700 Td
(Alpha) Tj
T*
(Bravo) Tj
0 -20 TD
(Charlie) Tj
1 0 0 1 200 500 Tm
(Delta) Tj
ET"""
    reader = op.PdfReader.from_bytes(_pdf_with_content_stream(content))

    chunks = reader.extract_text_chunks(0)
    by_text = {chunk.text: chunk.y for chunk in chunks}

    assert list(by_text) == ["Alpha", "Bravo", "Charlie", "Delta"]
    assert by_text == pytest.approx(
        {"Alpha": 700.0, "Bravo": 686.0, "Charlie": 666.0, "Delta": 500.0}
    )
