"""Tests for PdfReader.get_page_content_streams — READ-012.

Each assertion checks actual operator bytes emitted by the writer into a
page's Contents stream. Streams returned by the bridge are already
decoded (filters applied); callers receive the raw PostScript-like
operator sequence, not the compressed on-disk form.
"""

import pytest


# ── Fixture builders ──────────────────────────────────────────────────────────


def _build_text_page() -> bytes:
    """A4 page with a single line of Helvetica text.

    The writer emits ``BT`` / ``Tf`` / ``Td`` / ``Tj`` / ``ET`` operators
    into the content stream for the ``text_at`` call.
    """
    from oxidize_pdf import Document, Font, Page

    doc = Document()
    page = Page.a4()
    page.set_font(Font.HELVETICA, 12.0)
    page.text_at(72.0, 720.0, "READ-012 stream content")
    doc.add_page(page)
    return doc.save_to_bytes()


def _build_rectangle_page() -> bytes:
    """A4 page with one filled rectangle.

    Drawing a rectangle emits the ``re`` path-construction operator
    followed by a fill operator (``f`` or ``f*``).
    """
    from oxidize_pdf import Document, Page

    doc = Document()
    page = Page.a4()
    page.draw_rect(50.0, 500.0, 120.0, 60.0)
    page.fill()
    doc.add_page(page)
    return doc.save_to_bytes()


def _build_multi_page() -> bytes:
    """Document with two pages, each with distinct text, so the bridge
    can be checked to return per-page streams independently."""
    from oxidize_pdf import Document, Font, Page

    doc = Document()
    for marker in ("FIRST-PAGE-MARKER", "SECOND-PAGE-MARKER"):
        page = Page.a4()
        page.set_font(Font.HELVETICA, 10.0)
        page.text_at(72.0, 700.0, marker)
        doc.add_page(page)
    return doc.save_to_bytes()


def _assemble_raw_pdf(objects: list[bytes]) -> bytes:
    """Minimal PDF assembler used by raw-bytes fixtures below."""
    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    body = bytearray(header)
    offsets: list[int] = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body.extend(f"{i} 0 obj\n".encode())
        body.extend(obj)
        body.extend(b"\nendobj\n")

    xref_offset = len(body)
    body.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    body.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        body.extend(f"{off:010d} 00000 n \n".encode())
    body.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode())
    body.extend(f"startxref\n{xref_offset}\n%%EOF\n".encode())
    return bytes(body)


def _build_no_contents_page() -> bytes:
    """PDF whose single page omits the ``/Contents`` entry entirely."""
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>",
    ]
    return _assemble_raw_pdf(objects)


def _build_split_contents_page() -> bytes:
    """PDF whose page stores ``/Contents`` as an array of two separate
    streams. Most writers inline everything into one stream; splitting
    exercises the array branch of the resolver."""
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents [4 0 R 5 0 R] >>"
        ),
        b"<< /Length 2 >>\nstream\nq\nendstream",
        b"<< /Length 2 >>\nstream\nQ\nendstream",
    ]
    return _assemble_raw_pdf(objects)


# ── Return shape ──────────────────────────────────────────────────────────────


class TestReturnShape:
    def test_returns_list(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_text_page())
        streams = reader.get_page_content_streams(0)
        assert isinstance(streams, list)

    def test_text_page_returns_at_least_one_stream(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_text_page())
        streams = reader.get_page_content_streams(0)
        assert len(streams) >= 1

    def test_entries_are_bytes(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_text_page())
        streams = reader.get_page_content_streams(0)
        assert all(isinstance(s, bytes) for s in streams)


# ── Semantic content of text pages ────────────────────────────────────────────


class TestTextStream:
    def test_stream_contains_begin_text_operator(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_text_page())
        joined = b"\n".join(reader.get_page_content_streams(0))
        assert b"BT" in joined

    def test_stream_contains_end_text_operator(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_text_page())
        joined = b"\n".join(reader.get_page_content_streams(0))
        assert b"ET" in joined

    def test_stream_contains_tf_font_selector(self):
        """``Tf`` is the font-selection operator; the writer must emit it
        once ``set_font`` has been called."""
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_text_page())
        joined = b"\n".join(reader.get_page_content_streams(0))
        assert b"Tf" in joined

    def test_stream_is_already_decoded(self):
        """A FlateDecode-compressed stream starts with 0x78 0x9C (zlib
        header). The bridge must return decoded bytes — readable ASCII
        operators — so that marker must NOT appear at byte 0."""
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_text_page())
        streams = reader.get_page_content_streams(0)
        for s in streams:
            if len(s) >= 2:
                assert s[:2] != b"\x78\x9c"


# ── Semantic content of graphics pages ────────────────────────────────────────


class TestGraphicsStream:
    def test_rectangle_page_contains_re_operator(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_rectangle_page())
        joined = b"\n".join(reader.get_page_content_streams(0))
        assert b" re" in joined or joined.startswith(b"re")

    def test_rectangle_page_contains_fill_operator(self):
        """``f`` (or ``f*``) paints the current path using the non-zero
        / even-odd winding rule respectively. Either is acceptable."""
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_rectangle_page())
        joined = b"\n".join(reader.get_page_content_streams(0))
        assert b"\nf\n" in joined or b" f\n" in joined or b"\nf*\n" in joined


# ── Multi-page independence ───────────────────────────────────────────────────


class TestMultiPageIsolation:
    def test_first_page_only_has_first_marker(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_multi_page())
        joined = b"\n".join(reader.get_page_content_streams(0))
        assert b"FIRST-PAGE-MARKER" in joined
        assert b"SECOND-PAGE-MARKER" not in joined

    def test_second_page_only_has_second_marker(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_multi_page())
        joined = b"\n".join(reader.get_page_content_streams(1))
        assert b"SECOND-PAGE-MARKER" in joined
        assert b"FIRST-PAGE-MARKER" not in joined


# ── Empty and split contents ──────────────────────────────────────────────────


class TestEdgeCases:
    def test_page_without_contents_returns_empty_list(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_no_contents_page())
        streams = reader.get_page_content_streams(0)
        assert streams == []

    def test_split_contents_returns_both_streams(self):
        """Contents stored as ``[4 0 R 5 0 R]`` must surface as two
        separate bytes entries in the returned list, in order."""
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_split_contents_page())
        streams = reader.get_page_content_streams(0)
        assert len(streams) == 2
        assert b"q" in streams[0]
        assert b"Q" in streams[1]

    def test_out_of_bounds_raises(self):
        from oxidize_pdf import PdfError, PdfReader

        reader = PdfReader.from_bytes(_build_text_page())
        with pytest.raises((IndexError, PdfError)):
            reader.get_page_content_streams(9999)
