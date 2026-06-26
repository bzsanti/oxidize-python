"""Issue #358 — CID-keyed positioned glyph runs exposed in the Python bridge.

Upstream 3.0.0 added a write path for pre-shaped glyph runs: a CID-keyed
(CID == GID under Identity-H) Type0/CIDFontType2 font drawn by glyph id via a
``TJ`` array, with a ``ToUnicode`` CMap so the result stays extractable. This
mirrors the upstream end-to-end test (issue_358_glyph_run_extraction_test.rs)
through the Python surface:

  - ``CidMapping(cid_to_gid=..., cid_to_unicode=..., cid_to_unicode_str=...,
    max_cid=...)`` — kwargs build the underlying HashMaps; ``max_cid`` is
    auto-derived from the keys when omitted.
  - ``Document.add_cid_keyed_font(name, data, mapping)``
  - ``Page.set_custom_font(name, size)`` selects the active CID-keyed font.
  - ``CidShowElement.new(cid, adjust)`` / ``.with_x_offset(off)`` and its
    ``cid`` / ``adjust`` / ``x_offset`` accessors.
  - ``Page.show_cid_array(elements, x, y)`` writes the positioned run.

CIDs are chosen distinct from their GIDs so the test proves the CID is what the
content stream and ``ToUnicode`` carry (not the GID). The binding's contract is
the structural emission + extraction round-trip; the CID->outline fidelity is
the shaper's responsibility, so any valid in-range GID exercises the path.
"""

from pathlib import Path

import oxidize_pdf as ox

FONT_PATH = str(Path(__file__).parent / "fixtures" / "Roboto-Regular.ttf")

# Valid in-range glyph ids in Roboto-Regular (1294 glyphs). The exact outline
# is irrelevant to the extraction contract; what matters is that subsetting
# finds a real glyph for each GID.
GID_LIG = 36
GID_X = 45
# CIDs deliberately != GIDs: the writer must emit these codes, mapped to GIDs
# via cid_to_gid and to text via the ToUnicode CMap.
CID_LIG = 100
CID_X = 200


def _font_bytes() -> bytes:
    return Path(FONT_PATH).read_bytes()


def _shaped_mapping() -> "ox.CidMapping":
    """CID_LIG renders GID_LIG and decomposes to the two characters 'fi';
    CID_X renders GID_X and maps to the single character 'x'."""
    return ox.CidMapping(
        cid_to_gid={CID_LIG: GID_LIG, CID_X: GID_X},
        cid_to_unicode={CID_X: ord("x")},
        cid_to_unicode_str={CID_LIG: "fi"},
    )


# ── CidMapping ──────────────────────────────────────────────────────────────


def test_cid_mapping_kwargs_populate_fields():
    m = ox.CidMapping(
        cid_to_gid={CID_LIG: GID_LIG, CID_X: GID_X},
        cid_to_unicode={CID_X: ord("x")},
        cid_to_unicode_str={CID_LIG: "fi"},
    )
    assert m.cid_to_gid == {CID_LIG: GID_LIG, CID_X: GID_X}
    assert m.cid_to_unicode == {CID_X: ord("x")}
    assert m.cid_to_unicode_str == {CID_LIG: "fi"}


def test_cid_mapping_max_cid_autoderived_from_all_keys():
    """When max_cid is omitted it is the largest CID across every map."""
    m = ox.CidMapping(
        cid_to_gid={CID_LIG: GID_LIG},
        cid_to_unicode={CID_X: ord("x")},
        cid_to_unicode_str={CID_LIG: "fi"},
    )
    assert m.max_cid == CID_X  # 200, the largest key anywhere


def test_cid_mapping_explicit_max_cid_is_honored():
    m = ox.CidMapping(cid_to_gid={CID_LIG: GID_LIG}, max_cid=500)
    assert m.max_cid == 500


def test_cid_mapping_empty_is_constructible():
    m = ox.CidMapping()
    assert m.cid_to_gid == {}
    assert m.max_cid == 0


# ── CidShowElement ──────────────────────────────────────────────────────────


def test_cid_show_element_basic_fields():
    el = ox.CidShowElement(CID_LIG, -20.0)
    assert el.cid == CID_LIG
    assert el.adjust == -20.0
    assert el.x_offset == 0.0


def test_cid_show_element_with_x_offset():
    el = ox.CidShowElement(CID_X, 0.0).with_x_offset(15.0)
    assert el.cid == CID_X
    assert el.adjust == 0.0
    assert el.x_offset == 15.0


# ── add_cid_keyed_font ──────────────────────────────────────────────────────


def test_add_cid_keyed_font_rejects_non_truetype_bytes():
    doc = ox.Document()
    import pytest

    with pytest.raises(Exception):
        doc.add_cid_keyed_font("Bad", b"not a font", ox.CidMapping(cid_to_gid={1: 1}))


# ── End-to-end glyph run ────────────────────────────────────────────────────


def _render_glyph_run(compress: bool = True) -> bytes:
    doc = ox.Document()
    doc.add_cid_keyed_font("ShapedRun", _font_bytes(), _shaped_mapping())

    page = ox.Page.a4()
    page.set_custom_font("ShapedRun", 24.0)
    page.show_cid_array(
        [
            ox.CidShowElement(CID_LIG, 0.0),
            ox.CidShowElement(CID_X, -20.0),  # small kern; must not split the word
        ],
        100.0,
        500.0,
    )
    doc.add_page(page)

    if compress:
        return doc.save_to_bytes()
    return doc.save_to_bytes_with_config(ox.WriterConfig(compress_streams=False))


def test_glyph_run_emits_type0_cidfonttype2_identity_h():
    pdf = _render_glyph_run(compress=False)
    # Structural contract, verified on the real (uncompressed) bytes.
    assert b"/Subtype /Type0" in pdf, "Type0 wrapper font expected"
    assert b"/Encoding /Identity-H" in pdf, "Identity-H encoding expected"
    assert b"/Subtype /CIDFontType2" in pdf, "CIDFontType2 descendant expected"
    assert b"/ToUnicode" in pdf, "a ToUnicode CMap must be emitted for extraction"


def test_glyph_run_content_stream_uses_tj_with_cid_codes():
    """The drawn run is a TJ array carrying the CID hex codes (not the GIDs)."""
    pdf = _render_glyph_run(compress=False)
    reader = ox.PdfReader.from_bytes(pdf)
    content = b"\n".join(reader.get_page_content_streams(0))
    assert b"TJ" in content, "show_cid_array must emit a TJ show-array operator"
    # CID_LIG=100=0x0064, CID_X=200=0x00C8 written as 4-hex glyph codes.
    assert b"0064" in content, "CID_LIG (0x0064) must appear in the TJ run"
    assert b"00C8" in content, "CID_X (0x00C8) must appear in the TJ run"


def test_glyph_run_extracts_component_characters_via_tounicode():
    """The whole MVP chain: the ligature CID decomposes to 'fi' and the run
    extracts as 'fix' through the ToUnicode CMap."""
    pdf = _render_glyph_run(compress=True)
    reader = ox.PdfReader.from_bytes(pdf)
    text = reader.extract_text_from_page(0)
    assert "fix" in text, f"run must extract as 'fix' via ToUnicode; got: {text!r}"
