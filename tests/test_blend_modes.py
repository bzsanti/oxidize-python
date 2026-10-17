"""Blend mode mappings and independent PDF rendering."""
import re
import shutil
import subprocess

import pytest
from oxidize_pdf import BlendMode, Color, Document, Page

NAMES = [
    ('NORMAL', 'Normal'), ('MULTIPLY', 'Multiply'), ('SCREEN', 'Screen'),
    ('OVERLAY', 'Overlay'), ('SOFT_LIGHT', 'SoftLight'), ('HARD_LIGHT', 'HardLight'),
    ('COLOR_DODGE', 'ColorDodge'), ('COLOR_BURN', 'ColorBurn'),
    ('DARKEN', 'Darken'), ('LIGHTEN', 'Lighten'), ('DIFFERENCE', 'Difference'),
    ('EXCLUSION', 'Exclusion'), ('HUE', 'Hue'), ('SATURATION', 'Saturation'),
    ('COLOR', 'Color'), ('LUMINOSITY', 'Luminosity'),
]


@pytest.mark.parametrize('name,pdf_name', NAMES)
def test_all_mode_names_and_immutable_values(name, pdf_name):
    mode = getattr(BlendMode, name)
    assert mode.pdf_name() == pdf_name
    assert repr(mode) == 'BlendMode.' + name
    with pytest.raises(AttributeError):
        mode.pdf_name = lambda: 'Normal'


def make_pdf(mode):
    page = Page(100, 100)
    page.set_fill_color(Color.rgb(0.5, 0.5, 0.5))
    page.draw_rect(0, 0, 100, 100)
    page.fill()
    page.set_blend_mode(mode)
    page.set_fill_color(Color.red())
    page.draw_rect(20, 20, 60, 60)
    page.fill()
    doc = Document()
    doc.add_page(page)
    return doc.save_to_bytes()


@pytest.mark.parametrize('name,pdf_name', NAMES[10:])
def test_new_modes_reach_extgstate(name, pdf_name):
    data = make_pdf(getattr(BlendMode, name))
    assert re.search(rb'/BM\s*/' + pdf_name.encode() + rb'(?=[\s/>])', data)
    assert b'/ExtGState' in data


@pytest.mark.parametrize('name,expected', [
    ('DIFFERENCE', (128, 128, 128)), ('EXCLUSION', (128, 128, 128)),
    ('HUE', (128, 128, 128)), ('SATURATION', (128, 128, 128)),
    ('COLOR', (255, 73, 73)), ('LUMINOSITY', (77, 77, 77)),
])
def test_new_modes_render(tmp_path, name, expected):
    if shutil.which('pdftoppm') is None:
        pytest.skip('independent Poppler renderer unavailable')
    # Gray backdrop + red source: Difference/Exclusion = 0.5 per channel;
    # Hue/Saturation retain gray; red luminosity is 0.3. Color preserves
    # backdrop luminosity 0.5, clipping red to (1, 2/7, 2/7).
    pdf = tmp_path / 'blend.pdf'
    pdf.write_bytes(make_pdf(getattr(BlendMode, name)))
    subprocess.run(['pdftoppm', '-r', '72', '-singlefile', str(pdf), str(tmp_path / 'blend')], check=True, capture_output=True, timeout=30)
    magic, width, height, maximum, pixels = (tmp_path / 'blend.ppm').read_bytes().split(None, 4)
    assert (magic, width, height, maximum) == (b'P6', b'100', b'100', b'255')
    def pixel(x, y):
        start = (y * 100 + x) * 3
        return tuple(pixels[start:start + 3])
    assert pixel(50, 50) == pytest.approx(expected, abs=2)
    assert pixel(5, 5) == pytest.approx((128, 128, 128), abs=1)


def test_invalid_mode_rejected():
    with pytest.raises(TypeError):
        Page.a4().set_blend_mode('Difference')
