"""Rendering context state and consumers follow the published core contract."""
import pytest

from oxidize_pdf import CoordinateSystem as C, Point, RenderContext, TransformMatrix as M


@pytest.mark.parametrize('system, expected', [(C.PDF_STANDARD, Point(17, 19)), (C.SCREEN_SPACE, Point(17, 781)), (C.custom(M(2, 3, 5, 7, 11, 13)), Point(140, 197))])
def test_initial_context_and_conversions(system, expected):
    context = RenderContext(system, 600, 800)
    assert (context.page_width, context.page_height) == (600, 800)
    assert context.to_pdf_standard(Point(17, 19)) == expected
    assert context.current_transform.transform_point(Point(17, 19)) == expected
    assert context.coordinate_system.to_pdf_standard(Point(17, 19), 800) == expected


def test_mutations_use_live_system_and_height_without_refreshing_matrix():
    context = RenderContext(C.SCREEN_SPACE, 600, 800)
    snapshot = context.current_transform
    old_system = context.coordinate_system
    context.page_height = 900
    context.page_width = 700
    assert (context.page_width, context.page_height) == (700, 900)
    assert context.to_pdf_standard(Point(17, 19)) == Point(17, 881)
    assert context.y_to_pdf(19) == 881
    assert context.current_transform.transform_point(Point(17, 19)) == Point(17, 781)
    context.coordinate_system = C.PDF_STANDARD
    assert context.to_pdf_standard(Point(17, 19)) == Point(17, 19)
    assert context.y_to_pdf(19) == 19
    assert old_system.to_pdf_standard(Point(17, 19), 800) == Point(17, 781)
    context.current_transform = M.translate(7, 9)
    assert context.current_transform.transform_point(Point(1, 2)) == Point(8, 11)
    assert snapshot.transform_point(Point(1, 2)) == Point(1, 798)
    assert context.to_pdf_standard(Point(1, 2)) == Point(1, 2)


def test_custom_context_y_uses_zero_x_and_ignores_cached_transform():
    context = RenderContext(C.PDF_STANDARD, 100, 200)
    context.coordinate_system = C.custom(M(2, 3, 5, 7, 11, 13))
    context.current_transform = M.scale(0, 0)
    context.page_height = -200
    assert context.to_pdf_standard(Point(17, 19)) == Point(140, 197)
    assert context.y_to_pdf(19) == 146
    assert context.current_transform.transform_point(Point(17, 19)) == Point(0, 0)


def test_invalid_assignments_preserve_context():
    context = RenderContext(C.SCREEN_SPACE, 600, 800)
    for name, value in [('coordinate_system', 'screen'), ('page_width', None), ('page_height', 'bad'), ('current_transform', (1, 0, 0, 1, 0, 0))]:
        with pytest.raises(TypeError):
            setattr(context, name, value)
    assert (context.page_width, context.page_height) == (600, 800)
    assert context.to_pdf_standard(Point(17, 19)) == Point(17, 781)
    assert context.current_transform.transform_point(Point(17, 19)) == Point(17, 781)
    with pytest.raises(TypeError):
        RenderContext('screen', 600, 800)
