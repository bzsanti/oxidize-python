"""Regression for issue #58 — `page.text_flow_at(...)` must honour the
document-wide WIN_ANSI font encoding, the same way `text_at` does.

Bug in oxidize-pdf 2.8.0: `text_flow_at` emitted the input string as raw
UTF-8 into the PDF Contents stream, ignoring
`Document.set_default_font_encoding(FontEncoding.WIN_ANSI)`. This made
every multi-byte glyph (€, em-dash, smart quotes, accented letters)
render as 2-3 wrong characters under Helvetica/WinAnsi. Upstream fix
landed in oxidize-pdf #240 (released as 2.8.2).

The tests inspect the actual operator bytes in the Contents stream to
distinguish:
  * single-byte WIN_ANSI 0x80 for €  (correct)
  * three-byte UTF-8 0xE2 0x82 0xAC for €  (the bug)
"""

import pytest


# WinAnsiEncoding code points for the glyphs used in the reproducer.
WIN_ANSI_EURO = 0x80
WIN_ANSI_EM_DASH = 0x97

# Inside a PDF literal string ``(...)``, bytes ≥ 0x80 are typically
# emitted as octal escapes ``\NNN`` (4 ASCII bytes) for safety. A
# conformant writer may also emit the raw byte. Either representation
# proves the encoding was applied.
WIN_ANSI_EURO_OCTAL = b"\\200"
WIN_ANSI_EM_DASH_OCTAL = b"\\227"

# UTF-8 byte sequences that must NOT appear in the Contents stream if
# the encoding is applied correctly.
UTF8_EURO = b"\xe2\x82\xac"
UTF8_EM_DASH = b"\xe2\x80\x94"


def _stream_encodes(stream: bytes, raw: int, octal_escape: bytes) -> bool:
    """The byte may be present either as the raw byte or as a PDF octal
    escape inside a literal string. Both are valid WIN_ANSI encodings.
    """
    return bytes([raw]) in stream or octal_escape in stream


def _build_text_flow_with_winansi() -> bytes:
    """Reproducer from issue #58: a sentence with € and em-dash, written
    via ``text_flow_at`` after the document opts into WIN_ANSI.
    """
    from oxidize_pdf import Color, Document, Font, FontEncoding, Margins, Page

    doc = Document()
    doc.set_default_font_encoding(FontEncoding.WIN_ANSI)

    page = Page.a4()
    page.set_margins(Margins.uniform(50.0))
    page.set_text_color(Color.rgb(0.0, 0.0, 0.0))
    page.set_font(Font.HELVETICA, 10.0)
    page.text_flow_at(50.0, 700.0, "Price is €100 — including VAT.")

    doc.add_page(page)
    return doc.save_to_bytes()


def _page_content_stream(pdf_bytes: bytes, page_index: int = 0) -> bytes:
    from oxidize_pdf import PdfReader

    reader = PdfReader.from_bytes(pdf_bytes)
    return b"\n".join(reader.get_page_content_streams(page_index))


# ── Assertions ────────────────────────────────────────────────────────────────


def test_text_flow_emits_win_ansi_byte_for_euro():
    """Under WIN_ANSI, € is single byte 0x80. Inside a PDF literal
    string the writer may emit it as the raw byte ``\\x80`` or as the
    PDF octal escape ``\\200``. Either form proves the encoding step
    ran on the input.
    """
    stream = _page_content_stream(_build_text_flow_with_winansi())
    assert _stream_encodes(stream, WIN_ANSI_EURO, WIN_ANSI_EURO_OCTAL), (
        "Expected the WIN_ANSI representation of € (byte 0x80 or octal "
        "escape \\200) inside the Contents stream. text_flow_at appears "
        "to be emitting raw UTF-8 (issue #58)."
    )


def test_text_flow_emits_win_ansi_byte_for_em_dash():
    """Under WIN_ANSI, em-dash (—) is single byte 0x97 (raw or octal
    escape ``\\227`` inside a literal string).
    """
    stream = _page_content_stream(_build_text_flow_with_winansi())
    assert _stream_encodes(stream, WIN_ANSI_EM_DASH, WIN_ANSI_EM_DASH_OCTAL), (
        "Expected the WIN_ANSI representation of — (byte 0x97 or octal "
        "escape \\227) inside the Contents stream. text_flow_at appears "
        "to be emitting raw UTF-8 (issue #58)."
    )


def test_text_flow_does_not_emit_raw_utf8_euro():
    """The three-byte UTF-8 sequence for € (0xE2 0x82 0xAC) must NOT be
    present in the Contents stream. If it is, ``text_flow_at`` is
    bypassing the WIN_ANSI mapping.
    """
    stream = _page_content_stream(_build_text_flow_with_winansi())
    assert UTF8_EURO not in stream, (
        "UTF-8 byte sequence for € leaked into the Contents stream. "
        "text_flow_at is ignoring set_default_font_encoding(WIN_ANSI) (issue #58)."
    )


def test_text_flow_does_not_emit_raw_utf8_em_dash():
    """The three-byte UTF-8 sequence for em-dash (0xE2 0x80 0x94) must
    NOT be present in the Contents stream.
    """
    stream = _page_content_stream(_build_text_flow_with_winansi())
    assert UTF8_EM_DASH not in stream, (
        "UTF-8 byte sequence for em-dash leaked into the Contents stream. "
        "text_flow_at is ignoring set_default_font_encoding(WIN_ANSI) (issue #58)."
    )


def test_text_flow_matches_text_at_encoding():
    """Cross-check: the same sentence rendered via ``text_at`` (which was
    not affected by the bug) and via ``text_flow_at`` must produce the
    same encoded byte sequences for € and —. If text_flow_at lags
    text_at on encoding, the bug is present.
    """
    from oxidize_pdf import Color, Document, Font, FontEncoding, Margins, Page

    sample = "Price is €100 — VAT."

    # Reference: text_at — known-good encoding path.
    doc_ref = Document()
    doc_ref.set_default_font_encoding(FontEncoding.WIN_ANSI)
    page_ref = Page.a4()
    page_ref.set_text_color(Color.rgb(0.0, 0.0, 0.0))
    page_ref.set_font(Font.HELVETICA, 10.0)
    page_ref.text_at(50.0, 700.0, sample)
    doc_ref.add_page(page_ref)
    stream_ref = _page_content_stream(doc_ref.save_to_bytes())

    # Subject: text_flow_at — under test.
    doc_flow = Document()
    doc_flow.set_default_font_encoding(FontEncoding.WIN_ANSI)
    page_flow = Page.a4()
    page_flow.set_margins(Margins.uniform(50.0))
    page_flow.set_text_color(Color.rgb(0.0, 0.0, 0.0))
    page_flow.set_font(Font.HELVETICA, 10.0)
    page_flow.text_flow_at(50.0, 700.0, sample)
    doc_flow.add_page(page_flow)
    stream_flow = _page_content_stream(doc_flow.save_to_bytes())

    # Both must encode € via WIN_ANSI (raw 0x80 or octal escape \200).
    ref_encoded = _stream_encodes(stream_ref, WIN_ANSI_EURO, WIN_ANSI_EURO_OCTAL)
    flow_encoded = _stream_encodes(stream_flow, WIN_ANSI_EURO, WIN_ANSI_EURO_OCTAL)
    assert ref_encoded and flow_encoded, (
        "Both text_at and text_flow_at must apply WIN_ANSI to €. "
        f"text_at encoded={ref_encoded}, text_flow_at encoded={flow_encoded} "
        "(issue #58)."
    )

    assert (UTF8_EURO in stream_ref) == (UTF8_EURO in stream_flow), (
        "text_at and text_flow_at disagree on raw UTF-8 leakage of € (issue #58)."
    )
