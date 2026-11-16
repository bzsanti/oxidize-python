"""Strict indirect stream lengths through the public Python reader."""


def fixture(value=None, reference="5 0 R", payload=b"BT ET\n"):
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << >> /Contents 4 0 R >>",
        b"<< /Length " + reference.encode() + b" >>\nstream\n" + payload + b"endstream",
        str(len(payload)).encode() if value is None else value.encode(),
    ]
    pdf = bytearray(b"%PDF-1.7\n")
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode() + body + b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(b"xref\n0 6\n0000000000 65535 f \n")
    for offset in offsets:
        pdf.extend(f"{offset:010} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(pdf)


def test_strict_indirect_length_public_reader():
    from oxidize_pdf import ParseOptions, PdfError, PdfReader

    for payload in (b"BT ET\n", b"% endstream\n% endobj\nBT ET\n", b""):
        reader = PdfReader.from_bytes(fixture(payload=payload), ParseOptions.strict())
        assert reader.page_count == 1
        assert [bytes(stream) for stream in reader.get_page_content_streams(0)] == [payload]
    cases = [("-1", "5 0 R"), ("/Bad", "5 0 R"), ("5 0 R", "5 0 R"),
             ("6", "5 1 R"), ("9223372036854775807", "5 0 R"),
             ("2", "5 0 R"), ("8", "5 0 R"), ("6", "99 0 R")]
    for value, reference in cases:
        reader = PdfReader.from_bytes(fixture(value, reference), ParseOptions.strict())
        for _ in range(2):
            try:
                reader.get_page_content_streams(0)
            except PdfError:
                pass
            else:
                raise AssertionError((value, reference, "invalid stream accepted"))
        assert reader.page_count == 1

