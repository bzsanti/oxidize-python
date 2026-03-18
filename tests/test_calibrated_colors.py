"""Tests for Feature 54: Calibrated Colors on Graphics."""


def test_cal_gray_new():
    from oxidize_pdf import CalGrayColorSpace

    cs = CalGrayColorSpace()
    assert cs.gamma == 1.0
    assert cs.white_point[0] == pytest.approx(0.9505, rel=1e-3)


def test_cal_gray_d50():
    from oxidize_pdf import CalGrayColorSpace

    cs = CalGrayColorSpace.d50()
    assert cs.gamma == 1.0


def test_cal_gray_d65():
    from oxidize_pdf import CalGrayColorSpace

    cs = CalGrayColorSpace.d65()
    assert cs.white_point[0] == pytest.approx(0.9504, rel=1e-3)


def test_cal_gray_builders():
    from oxidize_pdf import CalGrayColorSpace

    cs = CalGrayColorSpace().with_gamma(2.2).with_white_point([0.95, 1.0, 1.09]).with_black_point([0.01, 0.01, 0.01])
    assert cs.gamma == pytest.approx(2.2)
    assert cs.white_point[0] == pytest.approx(0.95)


def test_cal_rgb_new():
    from oxidize_pdf import CalRgbColorSpace

    cs = CalRgbColorSpace()
    g = cs.gamma
    assert g == (1.0, 1.0, 1.0)


def test_cal_rgb_statics():
    from oxidize_pdf import CalRgbColorSpace

    srgb = CalRgbColorSpace.srgb()
    assert srgb.gamma == (2.2, 2.2, 2.2)

    adobe = CalRgbColorSpace.adobe_rgb()
    assert adobe.gamma == (2.2, 2.2, 2.2)

    d65 = CalRgbColorSpace.d65()
    assert d65 is not None


def test_cal_rgb_builders():
    from oxidize_pdf import CalRgbColorSpace

    cs = CalRgbColorSpace().with_gamma([2.0, 2.2, 1.8]).with_white_point([0.95, 1.0, 1.09])
    g = cs.gamma
    assert g[0] == pytest.approx(2.0)
    assert g[1] == pytest.approx(2.2)
    assert g[2] == pytest.approx(1.8)


def test_calibrated_color_cal_gray():
    from oxidize_pdf import CalGrayColorSpace, CalibratedColor

    cs = CalGrayColorSpace.d50()
    color = CalibratedColor.cal_gray(0.5, cs)
    vals = color.values()
    assert len(vals) == 1
    assert vals[0] == pytest.approx(0.5)


def test_calibrated_color_cal_rgb():
    from oxidize_pdf import CalRgbColorSpace, CalibratedColor

    cs = CalRgbColorSpace.srgb()
    color = CalibratedColor.cal_rgb([0.1, 0.5, 0.9], cs)
    vals = color.values()
    assert len(vals) == 3
    assert vals[0] == pytest.approx(0.1)
    assert vals[1] == pytest.approx(0.5)
    assert vals[2] == pytest.approx(0.9)


def test_lab_color_new():
    from oxidize_pdf import LabColor, LabColorSpace

    cs = LabColorSpace.d50()
    color = LabColor(50.0, 25.0, -25.0, cs)
    assert color.l == pytest.approx(50.0)
    assert color.a == pytest.approx(25.0)
    assert color.b == pytest.approx(-25.0)


def test_lab_color_statics():
    from oxidize_pdf import LabColor

    white = LabColor.white()
    assert white.l == pytest.approx(100.0)
    assert white.a == pytest.approx(0.0)

    black = LabColor.black()
    assert black.l == pytest.approx(0.0)

    gray = LabColor.gray()
    assert gray.l == pytest.approx(50.0)


def test_lab_color_values():
    from oxidize_pdf import LabColor

    white = LabColor.white()
    vals = white.values()
    assert len(vals) == 3


def test_lab_color_delta_e():
    from oxidize_pdf import LabColor

    white = LabColor.white()
    black = LabColor.black()
    de = white.delta_e(black)
    assert de > 0.0


def test_calibrated_colors_on_page():
    from oxidize_pdf import (
        CalGrayColorSpace,
        CalRgbColorSpace,
        CalibratedColor,
        Document,
        LabColor,
        LabColorSpace,
        Page,
    )

    doc = Document()
    page = Page(612.0, 792.0)

    cs_gray = CalGrayColorSpace.d50()
    color_gray = CalibratedColor.cal_gray(0.5, cs_gray)
    page.set_fill_color_calibrated(color_gray)

    cs_rgb = CalRgbColorSpace.srgb()
    color_rgb = CalibratedColor.cal_rgb([0.2, 0.4, 0.8], cs_rgb)
    page.set_stroke_color_calibrated(color_rgb)

    cs_lab = LabColorSpace.d50()
    lab_color = LabColor(50.0, 0.0, 0.0, cs_lab)
    page.set_fill_color_lab(lab_color)
    page.set_stroke_color_lab(lab_color)

    doc.add_page(page)
    pdf_bytes = doc.save_to_bytes()
    assert len(pdf_bytes) > 0


import pytest
