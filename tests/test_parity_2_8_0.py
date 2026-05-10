"""Parity coverage for upstream oxidize-pdf 2.8.0 additions.

Surface added in this module:

- ``Document.new_page_a4()``, ``Document.new_page_letter()``,
  ``Document.new_page(width, height)`` — factory methods that bind
  the returned page to the Document's per-instance ``FontMetricsStore``
  (upstream 2.8.0, issue #230).
- ``TextField.with_default_appearance(font, size, color)`` and
  ``ComboBox.with_default_appearance(font, size, color)`` — typed
  ``/DA`` builder mirroring the upstream Rust API. Required so that
  ``Document::fill_field`` (when later wired through the bridge) can
  dispatch to the Type0/CID custom-font path for non-WinAnsi values
  (CJK, Arabic, Latin-extended). See upstream issue #212.

Tests verify observable behaviour: page dimensions, full-cycle
font/text round-trip, and the AcroForm /DA wire format inside the
saved PDF bytes — no smoke or shape-only assertions.
"""

import pathlib

import pytest

from oxidize_pdf import (
    Color,
    ComboBox,
    Document,
    Font,
    PdfReader,
    Point,
    Rectangle,
    TextField,
)


FIXTURE_FONT = pathlib.Path(__file__).parent / "fixtures" / "Roboto-Regular.ttf"


# ── Helpers ────────────────────────────────────────────────────────────────


def _load_roboto_bytes() -> bytes:
    if not FIXTURE_FONT.exists():
        pytest.skip(f"missing font fixture: {FIXTURE_FONT}")
    return FIXTURE_FONT.read_bytes()


# ── Document.new_page_* — A4 / letter / arbitrary ─────────────────────────


# Upstream uses rounded PDF user-space units, matching ``Page::a4``
# (595.0 × 842.0 pt) and ``Page::letter`` (612.0 × 792.0 pt).
A4_WIDTH_PT = 595.0
A4_HEIGHT_PT = 842.0
LETTER_WIDTH_PT = 612.0
LETTER_HEIGHT_PT = 792.0


def test_new_page_a4_returns_a4_dimensions():
    doc = Document()
    page = doc.new_page_a4()
    assert page.width == pytest.approx(A4_WIDTH_PT, abs=0.001)
    assert page.height == pytest.approx(A4_HEIGHT_PT, abs=0.001)


def test_new_page_letter_returns_letter_dimensions():
    doc = Document()
    page = doc.new_page_letter()
    assert page.width == pytest.approx(LETTER_WIDTH_PT, abs=0.001)
    assert page.height == pytest.approx(LETTER_HEIGHT_PT, abs=0.001)


def test_new_page_arbitrary_dimensions_are_passed_through():
    doc = Document()
    page = doc.new_page(123.5, 678.25)
    assert page.width == pytest.approx(123.5, abs=0.001)
    assert page.height == pytest.approx(678.25, abs=0.001)


def test_new_page_a4_with_custom_font_round_trip(output_pdf):
    """End-to-end: register a custom font, build an A4 page via the new
    factory, render text with the custom font, save, re-read, and verify
    the text comes back unchanged. The factory must not reject pages
    bound to the Document's per-instance metrics store."""
    doc = Document()
    doc.add_font_from_bytes("Roboto", _load_roboto_bytes())

    page = doc.new_page_a4()
    page.set_font(Font.custom("Roboto"), 12.0)
    page.text_at(72.0, 720.0, "Hola mundo Roboto")

    doc.add_page(page)
    doc.save(str(output_pdf))

    reader = PdfReader.open(str(output_pdf))
    assert reader.page_count == 1
    extracted = reader.extract_text_from_page(0)
    assert extracted, (
        "PdfReader.extract_text_from_page returned empty — "
        "if this fails, suspect the text extractor's custom-font path, "
        "not the new_page_a4 factory itself"
    )
    assert "Hola mundo Roboto" in extracted


def test_new_page_letter_round_trip(output_pdf):
    doc = Document()
    page = doc.new_page_letter()
    page.set_font(Font.HELVETICA, 12.0)
    page.text_at(72.0, 720.0, "Letter factory smoke")

    doc.add_page(page)
    doc.save(str(output_pdf))

    reader = PdfReader.open(str(output_pdf))
    assert reader.page_count == 1
    extracted = reader.extract_text_from_page(0)
    assert "Letter factory smoke" in extracted


def test_new_page_with_custom_dimensions_round_trip(output_pdf):
    doc = Document()
    page = doc.new_page(400.0, 600.0)
    page.set_font(Font.HELVETICA, 14.0)
    page.text_at(50.0, 550.0, "Custom size page")

    doc.add_page(page)
    doc.save(str(output_pdf))

    reader = PdfReader.open(str(output_pdf))
    assert reader.page_count == 1
    extracted = reader.extract_text_from_page(0)
    assert "Custom size page" in extracted


# ── TextField.with_default_appearance ──────────────────────────────────────


def test_textfield_default_appearance_reaches_acroform_da(output_pdf):
    """The typed /DA built via ``with_default_appearance`` must land
    in the saved PDF's AcroForm field dictionary. Upstream
    ``DefaultAppearance::to_da_string`` emits the form
    ``/<font_resource> <size> Tf <r> <g> <b> rg`` for an RGB colour:
    size via Rust's ``{}`` Display (so 13.5f64 → "13.5") and the
    colour triple via ``{:.3}`` (three decimals). We don't lock the
    writer-assigned font resource name."""
    doc = Document()
    field = TextField("name").with_default_appearance(
        Font.HELVETICA, 13.5, Color.rgb(0.25, 0.5, 0.75)
    )
    page = doc.new_page_a4()
    doc.add_page(page)
    doc.add_text_field(
        field,
        Rectangle(Point(72.0, 600.0), Point(300.0, 624.0)),
    )
    doc.save(str(output_pdf))

    raw = pathlib.Path(str(output_pdf)).read_bytes()
    assert b"13.5 Tf" in raw, "expected /DA to carry size 13.5 via Tf"
    assert b"0.250 0.500 0.750 rg" in raw, (
        "expected /DA to carry the RGB fill colour via three-decimal rg"
    )


# ── ComboBox.with_default_appearance ───────────────────────────────────────


def test_combobox_default_appearance_reaches_acroform_da(output_pdf):
    """Same contract as the TextField counterpart for Choice fields.
    Closes the gap from upstream issue #212 at the Python surface:
    without a typed /DA, ``Document::fill_field`` falls through to
    the Helvetica + WinAnsi path and rejects non-WinAnsi values."""
    doc = Document()
    field = (
        ComboBox("country")
        .add_option("es", "España")
        .add_option("fr", "France")
        .with_default_appearance(Font.HELVETICA, 10.0, Color.rgb(0.1, 0.2, 0.3))
    )
    page = doc.new_page_a4()
    doc.add_page(page)
    doc.add_combo_box(
        field,
        Rectangle(Point(72.0, 540.0), Point(300.0, 564.0)),
    )
    doc.save(str(output_pdf))

    raw = pathlib.Path(str(output_pdf)).read_bytes()
    assert b"10 Tf" in raw, "expected /DA to carry size 10 via Tf"
    assert b"0.100 0.200 0.300 rg" in raw, (
        "expected /DA to carry the RGB fill colour via three-decimal rg"
    )
