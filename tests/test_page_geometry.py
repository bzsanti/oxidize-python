"""Known page geometry, independent of the core's layout reservation engine."""
import re

import pytest

from oxidize_pdf import CoordinateSystem, Document, Margins, Page


def test_asymmetric_content_bounds_and_live_margins():
    page = Page(200, 300)
    page.set_margins(Margins(top=11, right=23, bottom=37, left=41))
    assert (page.content_width, page.content_height) == (136, 252)
    assert page.content_area == (41, 37, 177, 289)
    snapshot = page.content_area
    page.set_margins(Margins(top=10, right=20, bottom=30, left=40))
    assert page.content_area == (40, 30, 180, 290)
    assert (page.content_width, page.content_height) == (140, 260)
    assert snapshot == (41, 37, 177, 289)
    assert (page.width, page.height) == (200, 300)


@pytest.mark.parametrize('rotation, expected', [(0, (200, 300)), (90, (300, 200)), (180, (200, 300)), (270, (300, 200))])
def test_rotation_dimensions_match_serialized_page(rotation, expected):
    page = Page(200, 300)
    page.set_margins(Margins(top=11, right=23, bottom=37, left=41))
    page.set_rotation(rotation)
    assert (page.effective_width, page.effective_height) == expected
    assert (page.width, page.height) == (200, 300)
    assert page.content_area == (41, 37, 177, 289)
    assert (page.content_width, page.content_height) == (136, 252)
    doc = Document()
    doc.add_page(page)
    data = doc.save_to_bytes()
    box = re.search(rb'/MediaBox\s*\[([^]]+)\]', data)
    assert box is not None
    assert tuple(float(v) for v in box[1].split()) == (0, 0, 200, 300)
    rotate = re.search(rb'/Rotate\s+(\d+)', data)
    assert (int(rotate[1]) if rotate else 0) == rotation


def test_oversized_margins_remain_unclamped_and_coordinates_are_unrotated():
    page = Page(100, 80)
    page.set_margins(Margins(top=60, right=70, bottom=50, left=40))
    page.set_coordinate_system(CoordinateSystem.SCREEN_SPACE)
    page.set_rotation(90)
    assert (page.content_width, page.content_height) == (-10, -30)
    assert page.content_area == (40, 50, 30, 20)
    assert (page.effective_width, page.effective_height) == (80, 100)


def test_geometry_is_read_only_and_rejected_rotation_keeps_dimensions():
    page = Page(200, 300)
    page.set_rotation(90)
    for name in ('content_width', 'content_height', 'content_area', 'effective_width', 'effective_height'):
        with pytest.raises(AttributeError):
            setattr(page, name, 0)
    with pytest.raises(ValueError):
        page.set_rotation(45)
    assert (page.effective_width, page.effective_height) == (300, 200)
