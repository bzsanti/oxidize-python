"""GFX-019 — ICC + named calibrated/Lab colour drawing (oxidize-pdf 2.11.0).

Mirrors the upstream end-to-end contract (``gfx_019_icc_graphics_color_test.rs``)
on the Python side: every assertion reads the *decoded content stream bytes*
written by the writer, never a return code or byte count.

The colour-setting methods emit, into the page content stream:

* fill  → ``/<name> cs`` followed by ``<components> sc``
* stroke → ``/<name> CS`` followed by ``<components> SC``

with components rendered to four decimals (e.g. ``0.2500 0.5000 0.7500 sc``),
referencing a colour space registered on the page via ``add_color_space`` and
emitted at ``/Resources/ColorSpace/<name>``.
"""

import pytest

from oxidize_pdf import (
    CalibratedColor,
    CalRgbColorSpace,
    Document,
    LabColor,
    LabColorSpace,
    Page,
    PageColorSpace,
    PdfError,
    PdfReader,
)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _content(doc: Document) -> bytes:
    """Serialize ``doc`` and return its first page's decoded content stream(s).

    ``get_page_content_streams`` returns the writer's operator sequence with
    all filters already applied, so the bytes are the raw PostScript-like
    operators — exactly what we assert on.
    """
    reader = PdfReader.from_bytes(doc.save_to_bytes())
    return b"".join(reader.get_page_content_streams(0))


def _pos(content: bytes, needle: bytes) -> int:
    idx = content.find(needle)
    assert idx != -1, f"{needle!r} not found in content stream:\n{content!r}"
    return idx


# ── ICC fill / stroke ────────────────────────────────────────────────────────


def test_icc_fill_emits_named_space_then_components_in_order():
    doc = Document()
    page = Page.a4()
    page.add_color_space("ICCRGB1", PageColorSpace.icc_based(3, "DeviceRGB"))
    page.set_fill_color_icc("ICCRGB1", [0.25, 0.5, 0.75])
    doc.add_page(page)

    content = _content(doc)
    cs_pos = _pos(content, b"/ICCRGB1 cs")
    comp_pos = _pos(content, b"0.2500 0.5000 0.7500 sc")
    assert cs_pos < comp_pos, (
        f"`/ICCRGB1 cs` must precede its components:\n{content!r}"
    )


def test_icc_stroke_emits_named_space_then_components_in_order():
    doc = Document()
    page = Page.a4()
    page.add_color_space("ICCGRAY1", PageColorSpace.icc_based(1, "DeviceGray"))
    page.set_stroke_color_icc("ICCGRAY1", [0.42])
    doc.add_page(page)

    content = _content(doc)
    cs_pos = _pos(content, b"/ICCGRAY1 CS")
    comp_pos = _pos(content, b"0.4200 SC")
    assert cs_pos < comp_pos, f"stroke CS must precede components:\n{content!r}"


def test_icc_cmyk_four_components():
    doc = Document()
    page = Page.a4()
    page.add_color_space("ICCCMYK1", PageColorSpace.icc_based(4, "DeviceCMYK"))
    page.set_fill_color_icc("ICCCMYK1", [0.1, 0.2, 0.3, 0.4])
    doc.add_page(page)

    content = _content(doc)
    assert b"/ICCCMYK1 cs" in content
    assert b"0.1000 0.2000 0.3000 0.4000 sc" in content, content


def test_icc_resource_registered_as_iccbased():
    """The ``/Resources/ColorSpace/<name>`` entry survives in the saved PDF as
    an ``ICCBased`` family array."""
    doc = Document()
    page = Page.a4()
    page.add_color_space("ICCRGB1", PageColorSpace.icc_based(3, "DeviceRGB"))
    page.set_fill_color_icc("ICCRGB1", [0.25, 0.5, 0.75])
    doc.add_page(page)

    raw = doc.save_to_bytes()
    assert b"/ICCRGB1" in raw, "ICC resource name must be registered"
    assert b"/ICCBased" in raw, "ICC space must serialise as /ICCBased family"


def test_icc_fill_empty_components_raises():
    """Empty component list would emit a bare ``sc`` with no operands — invalid
    per ISO 32000-1 §8.6.8. The bridge must reject it explicitly."""
    page = Page.a4()
    page.add_color_space("ICCRGB1", PageColorSpace.icc_based(3, "DeviceRGB"))
    with pytest.raises(ValueError):
        page.set_fill_color_icc("ICCRGB1", [])


def test_icc_stroke_empty_components_raises():
    page = Page.a4()
    page.add_color_space("ICCGRAY1", PageColorSpace.icc_based(1, "DeviceGray"))
    with pytest.raises(ValueError):
        page.set_stroke_color_icc("ICCGRAY1", [])


# ── Named calibrated / Lab spaces ────────────────────────────────────────────


def test_two_named_calibrated_spaces_coexist_on_one_page():
    """Two CalRGB spaces under different names paint in draw order — proving
    the old one-calibrated-space-per-page limitation is removed."""
    doc = Document()
    page = Page.a4()
    page.add_color_space("CalA", PageColorSpace.cal_rgb(CalRgbColorSpace.d65()))
    page.add_color_space("CalB", PageColorSpace.cal_rgb(CalRgbColorSpace.srgb()))

    page.set_fill_color_calibrated_named(
        "CalA", CalibratedColor.cal_rgb([0.1, 0.2, 0.3], CalRgbColorSpace())
    )
    page.set_fill_color_calibrated_named(
        "CalB", CalibratedColor.cal_rgb([0.4, 0.5, 0.6], CalRgbColorSpace())
    )
    doc.add_page(page)

    content = _content(doc)
    a_pos = _pos(content, b"/CalA cs")
    b_pos = _pos(content, b"/CalB cs")
    assert a_pos < b_pos, f"both named spaces must paint in order:\n{content!r}"
    assert b"0.1000 0.2000 0.3000 sc" in content, content
    assert b"0.4000 0.5000 0.6000 sc" in content, content


def test_calibrated_stroke_named():
    doc = Document()
    page = Page.a4()
    page.add_color_space("CalS", PageColorSpace.cal_rgb(CalRgbColorSpace()))
    page.set_stroke_color_calibrated_named(
        "CalS", CalibratedColor.cal_rgb([0.7, 0.8, 0.9], CalRgbColorSpace())
    )
    doc.add_page(page)

    content = _content(doc)
    cs_pos = _pos(content, b"/CalS CS")
    comp_pos = _pos(content, b"0.7000 0.8000 0.9000 SC")
    assert cs_pos < comp_pos, content


def test_lab_fill_named():
    doc = Document()
    page = Page.a4()
    page.add_color_space("LabA", PageColorSpace.lab(LabColorSpace.d50()))
    page.set_fill_color_lab_named(
        "LabA", LabColor(50.0, 10.0, -20.0, LabColorSpace.d50())
    )
    doc.add_page(page)

    content = _content(doc)
    cs_pos = _pos(content, b"/LabA cs")
    # LabColor.values() normalises components to [0,1] for the content stream:
    # L/100, (a-rmin)/(rmax-rmin), (b-rmin)/(rmax-rmin). With the default
    # range [-100,100], L=50,a=10,b=-20 → 0.5000 0.5500 0.4000.
    comp_pos = _pos(content, b"0.5000 0.5500 0.4000 sc")
    assert cs_pos < comp_pos, (
        f"`/LabA cs` must precede its components:\n{content!r}"
    )


def test_lab_stroke_named():
    doc = Document()
    page = Page.a4()
    page.add_color_space("LabS", PageColorSpace.lab(LabColorSpace.d50()))
    page.set_stroke_color_lab_named(
        "LabS", LabColor(75.0, -5.0, 15.0, LabColorSpace.d50())
    )
    doc.add_page(page)

    content = _content(doc)
    cs_pos = _pos(content, b"/LabS CS")
    # Normalised: L=75 → 0.7500, a=-5 → (−5+100)/200=0.4750,
    # b=15 → (15+100)/200=0.5750.
    comp_pos = _pos(content, b"0.7500 0.4750 0.5750 SC")
    assert cs_pos < comp_pos, (
        f"`/LabS CS` must precede its components:\n{content!r}"
    )


# ── PageColorSpace construction ──────────────────────────────────────────────


def test_device_alias_registers_named_device_space():
    doc = Document()
    page = Page.a4()
    page.add_color_space("CS1", PageColorSpace.device("DeviceRGB"))
    doc.add_page(page)

    raw = doc.save_to_bytes()
    assert b"/CS1" in raw
    assert b"/DeviceRGB" in raw


def test_parameterised_escape_hatch_builds_family_array():
    """The generic ``parameterised(family, params)`` accepts a raw Python dict
    for cases the typed constructors don't cover (``#[non_exhaustive]``)."""
    doc = Document()
    page = Page.a4()
    page.add_color_space(
        "CSlab",
        PageColorSpace.parameterised(
            "Lab",
            {"WhitePoint": [0.9505, 1.0, 1.089], "Range": [-128.0, 127.0, -128.0, 127.0]},
        ),
    )
    doc.add_page(page)

    raw = doc.save_to_bytes()
    assert b"/CSlab" in raw
    assert b"/Lab" in raw


def test_parameterised_accepts_int_float_str_and_list():
    """The escape hatch maps int → Integer, float → Real, str → Name, and
    lists recursively, so a mixed parameter dict round-trips into the PDF."""
    doc = Document()
    page = Page.a4()
    page.add_color_space(
        "CSicc",
        PageColorSpace.parameterised("ICCBased", {"N": 3, "Alternate": "DeviceRGB"}),
    )
    doc.add_page(page)

    raw = doc.save_to_bytes()
    assert b"/CSicc" in raw
    assert b"/ICCBased" in raw
    assert b"/Alternate" in raw
    assert b"/DeviceRGB" in raw


def test_parameterised_rejects_unknown_family():
    with pytest.raises(ValueError):
        PageColorSpace.parameterised("NotAFamily", {})


def test_parameterised_rejects_bool_value():
    """Python ``bool`` is a subclass of ``int``; a bool in a PDF parameter
    dict is always a caller mistake and must be rejected, not silently
    coerced to 1/0."""
    with pytest.raises(ValueError):
        PageColorSpace.parameterised("ICCBased", {"N": True})


def test_icc_based_rejects_invalid_channel_count():
    """ICC /N must be 1, 3, or 4 (ISO 32000-1 §8.6.5.5)."""
    for bad_n in (0, 2, 5, 7):
        with pytest.raises(ValueError):
            PageColorSpace.icc_based(bad_n, "DeviceRGB")


def test_icc_based_accepts_valid_channel_counts():
    for n, alt in ((1, "DeviceGray"), (3, "DeviceRGB"), (4, "DeviceCMYK")):
        # Constructing must not raise for legal channel counts.
        assert PageColorSpace.icc_based(n, alt) is not None


def test_add_color_space_rejects_invalid_resource_name():
    """Resource names containing PDF delimiters are invalid per ISO 32000-1
    §7.3.5 and must be rejected fail-safe."""
    page = Page.a4()
    with pytest.raises(PdfError):
        page.add_color_space("bad/name", PageColorSpace.device("DeviceRGB"))


# ── Legacy methods unchanged ─────────────────────────────────────────────────


def test_legacy_calibrated_method_still_emits_default_name():
    """The unchanged ``set_fill_color_calibrated`` must keep emitting the
    default ``CalRGB1`` slot after the upstream delegation refactor."""
    doc = Document()
    page = Page.a4()
    page.set_fill_color_calibrated(
        CalibratedColor.cal_rgb([0.1, 0.2, 0.3], CalRgbColorSpace())
    )
    doc.add_page(page)

    content = _content(doc)
    assert b"/CalRGB1 cs" in content, content
    assert b"0.1000 0.2000 0.3000 sc" in content, content
