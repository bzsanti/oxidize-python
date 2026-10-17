"""Known geometric results exercise the real native coordinate bindings."""
import math

import pytest

from oxidize_pdf import CoordinateSystem as C, Page, Point, TransformMatrix as M


def test_components_and_immutable_snapshot():
    matrix = M(2, 3, 5, 7, 11, 13)
    assert (matrix.a, matrix.b, matrix.c, matrix.d, matrix.e, matrix.f) == (2, 3, 5, 7, 11, 13)
    assert matrix.transform_point(Point(17, 19)) == Point(140, 197)
    with pytest.raises(AttributeError):
        matrix.a = 9
    assert M.IDENTITY.transform_point(Point(-4, 8)) == Point(-4, 8)
    assert matrix.to_pdf_ctm() == '2.000000 3.000000 5.000000 7.000000 11.000000 13.000000 cm'


def test_composition_order_and_factories():
    translate = M.translate(10, -5)
    scale = M.scale(2, 3)
    point = Point(4, 6)
    assert translate.multiply(scale).transform_point(point) == Point(18, 13)
    assert scale.multiply(translate).transform_point(point) == Point(28, 3)
    assert translate.transform_point(point) == Point(14, 1)
    assert scale.transform_point(point) == Point(8, 18)
    rotated = M.rotate(math.pi / 2).transform_point(Point(3, 4))
    assert (rotated.x, rotated.y) == pytest.approx((-4, 3))
    assert M.flip_y(800).transform_point(Point(20, 30)) == Point(20, 770)
    assert M.scale(0, -2).transform_point(Point(3, 4)) == Point(0, -8)


def test_coordinate_conversions_and_custom_semantics():
    point = Point(17, 19)
    assert C.PDF_STANDARD.to_pdf_standard(point, 800) == point
    assert C.PDF_STANDARD.y_to_pdf_standard(19, 800) == 19
    assert C.PDF_STANDARD.grows_upward()
    assert C.SCREEN_SPACE.to_pdf_standard(point, 800) == Point(17, 781)
    assert C.SCREEN_SPACE.y_to_pdf_standard(19, 800) == 781
    assert not C.SCREEN_SPACE.grows_upward()
    assert C.SCREEN_SPACE.to_pdf_standard_matrix(800).transform_point(point) == Point(17, 781)
    matrix = M(2, 3, 5, 7, 11, 13)
    custom = C.custom(matrix)
    assert custom.to_pdf_standard(point, 800) == Point(140, 197)
    assert custom.to_pdf_standard_matrix(900).transform_point(point) == Point(140, 197)
    assert custom.y_to_pdf_standard(19, 800) == 146  # x=0, not the point's x=17
    assert custom.grows_upward()
    assert not C.custom(M.scale(1, 0)).grows_upward()
    assert not C.custom(M.flip_y(800)).grows_upward()
    assert repr(custom) == 'CoordinateSystem.CUSTOM'


def test_page_coordinate_system_snapshot():
    page = Page(200, 100)
    before = page.coordinate_system
    page.set_coordinate_system(C.custom(M.translate(7, 9)))
    custom = page.coordinate_system
    page.set_coordinate_system(C.SCREEN_SPACE)
    point = Point(1, 2)
    assert before.to_pdf_standard(point, 100) == point
    assert custom.to_pdf_standard(point, 100) == Point(8, 11)
    assert page.coordinate_system.to_pdf_standard(point, 100) == Point(1, 98)


def test_float_semantics_and_type_errors():
    # Core permits arbitrary f64, including degenerate/nonfinite transforms.
    assert math.isnan(M.scale(float('nan'), 1).transform_point(Point(1, 2)).x)
    assert math.isinf(M.translate(float('inf'), 0).e)
    with pytest.raises(TypeError):
        C.custom((1, 0, 0, 1, 0, 0))
    with pytest.raises(TypeError):
        M.IDENTITY.transform_point((1, 2))
