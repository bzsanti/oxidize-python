"""Deterministic PDFs assembled without using the library under test."""
from pathlib import Path
import zlib


def stream(data, extra=b""):
    return b"<< /Length %d %s >>\nstream\n" % (len(data), extra) + data + b"\nendstream"


def pdf(content, *, cmap=False, annotation=False, damaged=False):
    font = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    if cmap:
        font = (b"<< /Type /Font /Subtype /TrueType /BaseFont /ABCDEF+Arial /FirstChar 32 /LastChar 126 /Widths ["
                + b"500 " * 95 + b"] /Encoding /WinAnsiEncoding /ToUnicode 6 0 R >>")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R "
        + (b"/Annots [6 0 R]" if annotation else b"") + b" >>",
        stream(content), font,
    ]
    if cmap:
        objects.append(stream(b"begincmap 1 begincodespacerange <0000> <FFFF> endcodespacerange 1 beginbfchar <20> <0020> endbfchar endcmap"))
    if annotation:
        objects.append(b"<< /Type /Annot /Subtype /Widget /Rect [72 600 172 620] /AP << /N 7 0 R >> >>")
        payload = zlib.compress(b"BT /F1 10 Tf 0 0 Td (Note) Tj ET")
        objects.append(stream(payload[:-4] if damaged else payload,
            b"/Filter /FlateDecode /Type /XObject /Subtype /Form /BBox [0 0 100 20] /Resources << /Font << /F1 5 0 R >> >>"))
    result = b"%PDF-1.4\n"
    offsets = []
    for i, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result += b"%d 0 obj\n" % i + obj + b"\nendobj\n"
    xref = len(result)
    result += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    result += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    return result + b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)


if __name__ == "__main__":
    fixtures = {
        "visual": pdf(b"BT /F1 10 Tf 420 700 Td (12-34-56) Tj ET BT /F1 10 Tf 350 700 Td (Account No.) Tj ET BT /F1 10 Tf 72 695 Td (Payments to be made to:) Tj ET"),
        "fallback": pdf(b"BT /F1 10 Tf 72 700 Td (Hello world) Tj ET", cmap=True),
        "tj": pdf(b"BT /F1 10 Tf 72 700 Td [(Alpha) -179 (Beta)] TJ ET"),
        "annotation": pdf(b"BT /F1 10 Tf 72 700 Td (Body) Tj ET", annotation=True),
        "annotation-damaged": pdf(b"BT /F1 10 Tf 72 700 Td (Body) Tj ET", annotation=True, damaged=True),
    }
    for name, data in fixtures.items():
        Path(__file__).with_name(name + ".pdf").write_bytes(data)
