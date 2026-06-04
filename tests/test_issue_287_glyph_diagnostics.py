"""Glyph-coverage diagnostics for embedded custom fonts (upstream #287).

When a custom font is embedded, characters with no glyph render as ``.notdef``
(an empty box). These diagnostics let callers detect coverage gaps *before*
rendering, e.g. to substitute a character or pick a different font.

Surfaces the upstream 2.12.0 API into Python:
  - ``Document.embedded_font(name) -> EmbeddedFont | None``
  - ``Document.font_missing_glyphs(name, text) -> list[str]``
  - ``EmbeddedFont.has_glyph(ch) -> bool``
  - ``EmbeddedFont.missing_glyphs(text) -> list[str]``
  - ``EmbeddedFont.name``

Roboto-Regular covers Latin (incl. ASCII) but not CJK ideographs, so a CJK
character is a reliable "missing" probe.
"""

from pathlib import Path

import oxidize_pdf as ox

FONT_PATH = str(Path(__file__).parent / "fixtures" / "Roboto-Regular.ttf")
CJK = "中"  # 中 — CJK ideograph, absent from Roboto-Regular


def _doc_with_roboto() -> "ox.Document":
    doc = ox.Document()
    doc.add_font("Roboto", FONT_PATH)
    return doc


def test_embedded_font_returns_handle_for_registered_font():
    doc = _doc_with_roboto()
    font = doc.embedded_font("Roboto")
    assert font is not None
    assert font.name == "Roboto"


def test_embedded_font_returns_none_for_unregistered_font():
    doc = _doc_with_roboto()
    assert doc.embedded_font("DoesNotExist") is None


def test_embedded_font_has_glyph_true_for_covered_char():
    font = _doc_with_roboto().embedded_font("Roboto")
    assert font.has_glyph("A") is True
    assert font.has_glyph("z") is True


def test_embedded_font_has_glyph_false_for_uncovered_char():
    font = _doc_with_roboto().embedded_font("Roboto")
    assert font.has_glyph(CJK) is False


def test_embedded_font_missing_glyphs_lists_uncovered_chars():
    font = _doc_with_roboto().embedded_font("Roboto")
    missing = font.missing_glyphs("AB" + CJK + "z")
    assert missing == [CJK]


def test_embedded_font_missing_glyphs_empty_when_all_covered():
    font = _doc_with_roboto().embedded_font("Roboto")
    assert font.missing_glyphs("Hello World") == []


def test_embedded_font_missing_glyphs_dedups():
    font = _doc_with_roboto().embedded_font("Roboto")
    missing = font.missing_glyphs(CJK + CJK + CJK)
    assert missing == [CJK]


def test_document_font_missing_glyphs_convenience():
    doc = _doc_with_roboto()
    assert doc.font_missing_glyphs("Roboto", "AB" + CJK) == [CJK]
    assert doc.font_missing_glyphs("Roboto", "ABC") == []


def test_document_font_missing_glyphs_unregistered_returns_empty():
    """Upstream contract: unknown font -> empty (nothing can be determined)."""
    doc = _doc_with_roboto()
    assert doc.font_missing_glyphs("DoesNotExist", "anything") == []


def test_has_glyph_rejects_multichar_string():
    font = _doc_with_roboto().embedded_font("Roboto")
    with __import__("pytest").raises(ValueError):
        font.has_glyph("AB")
