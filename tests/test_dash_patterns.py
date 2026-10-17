"""Dash parameters and their actual effect on a PDF stroke."""
import math
import shutil
import subprocess

import pytest
from oxidize_pdf import Color, Document, LineDashPattern, Page


def test_factories_and_owned_parameters():
    source = [3.0, 7.0]
    pattern = LineDashPattern(source, 2.5)
    source.clear()
    snapshot = pattern.array
    snapshot.append(99)
    assert pattern.array == [3.0, 7.0]
    assert pattern.phase == 2.5
    for name, value in [('array', []), ('phase', 0)]:
        with pytest.raises(AttributeError):
            setattr(pattern, name, value)
    assert pattern.to_pdf_string() == '[3.00 7.00] 2.50'
    solid = LineDashPattern.solid()
    assert (solid.array, solid.phase, solid.to_pdf_string()) == ([], 0, '[] 0')
    dashed = LineDashPattern.dashed(6, 2)
    dotted = LineDashPattern.dotted(1, 4)
    assert (dashed.array, dashed.phase, dashed.to_pdf_string()) == ([6, 2], 0, '[6.00 2.00] 0.00')
    assert (dotted.array, dotted.phase, dotted.to_pdf_string()) == ([1, 4], 0, '[1.00 4.00] 0.00')


def test_numeric_serialization_preserves_core_contract():
    pattern = LineDashPattern([float('nan'), float('inf'), -float('inf'), -2.5], float('inf'))
    assert math.isnan(pattern.array[0])
    assert pattern.array[1:] == [float('inf'), -float('inf'), -2.5]
    assert math.isinf(pattern.phase)
    assert pattern.to_pdf_string() == '[0.00 0.00 0.00 -2.50] 0.00'
    assert LineDashPattern([], 9).phase == 9
    assert LineDashPattern([], 9).to_pdf_string() == '[] 0'
    assert LineDashPattern([1.234, 5.678], -1.234).to_pdf_string() == '[1.23 5.68] -1.23'


def test_invalid_arguments_do_not_mutate_existing_pattern():
    pattern = LineDashPattern.dashed(3, 7)
    with pytest.raises(TypeError):
        LineDashPattern([1, object()], 0)
    with pytest.raises(TypeError):
        LineDashPattern.dashed('bad', 2)
    with pytest.raises(TypeError):
        LineDashPattern.dotted(1, None)
    assert pattern.to_pdf_string() == '[3.00 7.00] 0.00'


@pytest.mark.parametrize('factory, phase, expected', [
    ('solid', 0, [True, True, True, True]),
    ('dashed', 0, [True, False, True, False]),
    ('dotted', 0, [True, False, True, False]),
    ('custom', 5, [False, True, False, True]),
])
def test_pattern_reaches_rendered_page(tmp_path, factory, phase, expected):
    if shutil.which('pdftoppm') is None:
        pytest.skip('independent Poppler renderer unavailable')
    if factory == 'custom':
        pattern = LineDashPattern([10, 10], phase)
    elif factory == 'solid':
        pattern = LineDashPattern.solid()
    else:
        pattern = getattr(LineDashPattern, factory)(10, 10)
    page = Page(100, 100)
    page.set_dash_pattern(pattern)
    pattern.array.clear()  # Inspection cannot alter the installed pattern
    page.set_stroke_color(Color.blue())
    page.set_line_width(4)
    page.move_to(10, 50)
    page.line_to(90, 50)
    page.stroke()
    doc = Document()
    doc.add_page(page)
    pdf = tmp_path / 'stroke.pdf'
    pdf.write_bytes(doc.save_to_bytes())
    subprocess.run(['pdftoppm', '-r', '72', '-singlefile', str(pdf), str(tmp_path / 'stroke')], check=True, capture_output=True, timeout=30)
    magic, width, height, maximum, pixels = (tmp_path / 'stroke.ppm').read_bytes().split(None, 4)
    assert (magic, width, height, maximum) == (b'P6', b'100', b'100', b'255')
    for x, painted in zip([17, 27, 37, 47], expected):
        start = (50 * 100 + x) * 3
        assert pixels[start:start + 3] == (b'\x00\x00\xff' if painted else b'\xff\xff\xff')
