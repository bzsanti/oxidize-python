"""Regression for issue #78 — text measurement must use an embedded custom
font's real metrics, not a fallback.

Bug in oxidize-pdf 0.7.0 (Python bridge), two compounding causes:

1. The module-level ``measure_text`` / ``measure_char`` call the free upstream
   functions with no ``FontMetricsStore``, so ``Font.custom(name)`` can never
   resolve a document's embedded font and falls back to default (Helvetica-
   shaped) widths. There was no Document-bound measurement API.

2. The bridge's ``Document.add_font(name, path)`` delegated to the upstream
   path-variant which (unlike ``add_font_from_bytes``) does NOT register text
   metrics, so even a Document-bound measurement would see an empty store.

The fix adds ``Document.measure_text`` / ``Document.measure_char`` that scope
measurement to the document's font metrics store, and routes ``add_font(path)``
through the byte-loading path so embedded glyph widths are registered.

The default custom-font fallback in upstream uses Helvetica-shaped widths, so
"differs from the builtin Helvetica width" is the discriminator between real
embedded metrics and the fallback.
"""

from pathlib import Path

import oxidize_pdf as ox

FONT_PATH = str(Path(__file__).parent / "fixtures" / "Roboto-Regular.ttf")
# A proportional string with mixed-width glyphs; Roboto's advance widths differ
# from the Helvetica-shaped fallback here.
SAMPLE = "Wiwiwilll"


def _font_bytes() -> bytes:
    return Path(FONT_PATH).read_bytes()


def test_add_font_path_registers_same_metrics_as_add_font_from_bytes():
    """``add_font(path)`` must register the embedded font's metrics, exactly
    like ``add_font_from_bytes`` does for the same bytes."""
    doc_path = ox.Document()
    doc_path.add_font("Roboto", FONT_PATH)

    doc_bytes = ox.Document()
    doc_bytes.add_font_from_bytes("Roboto", _font_bytes())

    font = ox.Font.custom("Roboto")
    for s in ["A", "i", "W", SAMPLE]:
        w_path = doc_path.measure_text(s, font, 12.0)
        w_bytes = doc_bytes.measure_text(s, font, 12.0)
        assert w_path == w_bytes, f"path vs bytes mismatch for {s!r}: {w_path} != {w_bytes}"


def test_document_measure_text_uses_embedded_metrics_not_fallback():
    """Document-bound measurement of a custom font must differ from the
    Helvetica-shaped fallback returned by the free function."""
    doc = ox.Document()
    doc.add_font("Roboto", FONT_PATH)
    font = ox.Font.custom("Roboto")

    w_embedded = doc.measure_text(SAMPLE, font, 12.0)
    w_fallback = ox.measure_text(SAMPLE, font, 12.0)  # free fn -> fallback
    assert w_embedded > 0.0
    assert w_embedded != w_fallback


def test_document_measure_char_uses_embedded_metrics():
    """Per-character measurement must reflect the embedded font's proportions:
    a wide glyph ('W') must measure wider than a narrow one ('i')."""
    doc = ox.Document()
    doc.add_font("Roboto", FONT_PATH)
    font = ox.Font.custom("Roboto")

    w_wide = doc.measure_char("W", font, 12.0)
    w_narrow = doc.measure_char("i", font, 12.0)
    assert w_wide > w_narrow


def test_document_measure_text_scales_with_size():
    doc = ox.Document()
    doc.add_font("Roboto", FONT_PATH)
    font = ox.Font.custom("Roboto")

    w12 = doc.measure_text(SAMPLE, font, 12.0)
    w24 = doc.measure_text(SAMPLE, font, 24.0)
    assert abs(w24 - 2.0 * w12) < 1e-6


def test_document_measure_text_builtin_font_matches_free_function():
    """For builtin fonts (no custom store needed) the Document-bound method
    must agree with the free function."""
    doc = ox.Document()
    w_doc = doc.measure_text("Hello World", ox.Font.HELVETICA, 12.0)
    w_free = ox.measure_text("Hello World", ox.Font.HELVETICA, 12.0)
    assert w_doc == w_free
