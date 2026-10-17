"""Color conversion contracts against literal component and pixel values."""
import math
import shutil
import subprocess

import pytest
from oxidize_pdf import Color, Document, Page


@pytest.mark.parametrize('color,space,predicates', [
    (Color.rgb(.2, .4, .8), 'DeviceRGB', (True, False, False)),
    (Color.cmyk(.2, .4, .6, .5), 'DeviceCMYK', (False, True, False)),
    (Color.gray(.25), 'DeviceGray', (False, False, True)),
])
def test_space_predicates_and_copy_identity(color, space, predicates):
    assert color.color_space_name() == space
    assert (color.is_rgb(), color.is_cmyk(), color.is_gray()) == predicates
    rgb, cmyk = color.to_rgb(), color.to_cmyk()
    assert rgb is not color and cmyk is not color
    assert rgb.is_rgb() and cmyk.is_cmyk()
    assert color.color_space_name() == space
    assert color.color_space == space.removeprefix('Device')


@pytest.mark.parametrize('color,rgb,cmyk', [
    (Color.rgb(.2, .4, .8), (.2, .4, .8), (.75, .5, 0, .2)),
    (Color.cmyk(.2, .4, .6, .5), (.4, .3, .2), (.2, .4, .6, .5)),
    (Color.gray(.25), (.25, .25, .25), (0, 0, 0, .75)),
    (Color.rgb(0, 0, 0), (0, 0, 0), (0, 0, 0, 1)),
    (Color.rgb(1, 1, 1), (1, 1, 1), (0, 0, 0, 0)),
    (Color.cmyk(.2, .4, .6, 1), (0, 0, 0), (.2, .4, .6, 1)),
])
def test_component_conversions(color, rgb, cmyk):
    assert color.cmyk_components() == pytest.approx(cmyk)
    converted = color.to_rgb()
    assert (converted.r, converted.g, converted.b) == pytest.approx(rgb)
    converted = color.to_cmyk()
    assert (converted.c, converted.m, converted.y, converted.k) == pytest.approx(cmyk)
    assert color.to_cmyk().to_rgb().r == pytest.approx(rgb[0])


def test_existing_properties_and_numeric_limits():
    rgb = Color.rgb(.2, .4, .8)
    # Existing channel getters do not convert RGB to CMYK; preserve this API.
    assert (rgb.c, rgb.m, rgb.y, rgb.k) == (0, 0, 0, 0)
    assert rgb.cmyk_components() == pytest.approx((.75, .5, 0, .2))
    clamped = Color.cmyk(-1, 2, float('inf'), -float('inf')).to_rgb()
    assert (clamped.r, clamped.g, clamped.b) == (1, 0, 0)
    gray = Color.gray(float('nan'))
    assert gray.is_gray()
    assert math.isnan(gray.to_rgb().r)
    assert math.isnan(gray.to_cmyk().k)
    assert math.isnan(gray.cmyk_components()[3])


def test_converted_rgb_reaches_page(tmp_path):
    if shutil.which('pdftoppm') is None:
        pytest.skip('independent Poppler renderer unavailable')
    page = Page(100, 100)
    page.set_fill_color(Color.cmyk(.2, .4, .6, .5).to_rgb())
    page.draw_rect(0, 0, 100, 100)
    page.fill()
    doc = Document()
    doc.add_page(page)
    pdf = tmp_path / 'color.pdf'
    pdf.write_bytes(doc.save_to_bytes())
    subprocess.run(['pdftoppm', '-r', '72', '-singlefile', str(pdf), str(tmp_path / 'color')], check=True, capture_output=True, timeout=30)
    magic, width, height, maximum, pixels = (tmp_path / 'color.ppm').read_bytes().split(None, 4)
    assert (magic, width, height, maximum) == (b'P6', b'100', b'100', b'255')
    start = (50 * 100 + 50) * 3
    assert tuple(pixels[start:start + 3]) == pytest.approx((102, 77, 51), abs=1)
