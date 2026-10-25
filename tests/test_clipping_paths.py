"""Clipping path contracts through native commands and an independent renderer."""
import shutil
import subprocess

import pytest

from oxidize_pdf import ClippingPath as Path, Color, Document, Page, WindingRule as Rule


def test_free_path_chaining_commands_and_pdf_operators():
    path = Path()
    assert path.is_empty and path.commands == []
    assert path.move_to(1, 2) is path
    assert path.line_to(3, 4).curve_to(5, 6, 7, 8, 9, 10).close_path() is path
    assert [(c.kind, c.coordinates) for c in path.commands] == [
        ('move_to', [1, 2]), ('line_to', [3, 4]),
        ('curve_to', [5, 6, 7, 8, 9, 10]), ('close_path', []),
    ]
    assert path.to_pdf_operations() == '1.000 2.000 m\n3.000 4.000 l\n5.000 6.000 7.000 8.000 9.000 10.000 c\nh\nW\nn\n'


def test_snapshot_and_winding_builder_independence():
    path = Path.rect(1, 2, 30, 40)
    snapshot = path.commands
    even = path.with_winding_rule(Rule.EvenOdd)
    assert even is not path
    assert even.to_pdf_operations().endswith('W*\nn\n')
    assert path.to_pdf_operations().endswith('W\nn\n')
    snapshot[0].coordinates.clear()
    path.commands.clear()
    assert path.commands[0].coordinates == [1, 2, 30, 40]
    with pytest.raises(AttributeError):
        snapshot[0].kind = 'close_path'
    path.clear()
    assert path.is_empty and path.commands == []
    assert snapshot[0].coordinates == [1, 2, 30, 40]
    assert not even.is_empty
    even.clear()
    assert even.to_pdf_operations() == 'W*\nn\n'  # clear preserves winding
    assert even.with_winding_rule(Rule.NonZero).to_pdf_operations() == 'W\nn\n'


def test_polygon_order_empty_and_invalid_input_atomicity():
    path = Path()
    assert path.add_polygon([]) is path and path.is_empty
    assert path.add_polygon([(1, 2), (9, 3), (4, 8)]) is path
    assert [(c.kind, c.coordinates) for c in path.commands] == [
        ('move_to', [1, 2]), ('line_to', [9, 3]), ('line_to', [4, 8]), ('close_path', []),
    ]
    before = path.to_pdf_operations()
    with pytest.raises((TypeError, ValueError)):
        path.add_polygon([(1, 2), (3, 4, 5)])
    with pytest.raises(TypeError):
        path.with_winding_rule('even_odd')
    assert path.to_pdf_operations() == before


def test_add_rect_and_rounded_rect_radius_cap():
    path = Path()
    assert path.add_rect(1, 2, 3, 4) is path
    assert [(c.kind, c.coordinates) for c in path.commands] == [('rectangle', [1, 2, 3, 4])]
    path.clear()
    assert path.add_rounded_rect(1, 2, 20, 10, 100) is path
    assert path.commands[0].coordinates == [6, 2]  # radius capped at 5
    assert [c.kind for c in path.commands] == ['move_to', 'line_to', 'curve_to', 'line_to', 'curve_to', 'line_to', 'curve_to', 'line_to', 'curve_to', 'close_path']
    assert [c.coordinates[-2:] for c in path.commands if c.kind == 'curve_to'] == [[21, 7], [16, 12], [1, 7], [6, 2]]


@pytest.mark.parametrize('shape, radii', [('circle', (5,)), ('ellipse', (5, 3))])
def test_curved_shapes_and_existing_factories(shape, radii):
    path = Path()
    assert getattr(path, 'add_' + shape)(10, 20, *radii) is path
    commands = path.commands
    assert [c.kind for c in commands] == ['move_to', 'curve_to', 'curve_to', 'curve_to', 'curve_to', 'close_path']
    ry = 5 if shape == 'circle' else 3
    assert commands[0].coordinates == [10, 20 + ry]
    assert [c.coordinates[-2:] for c in commands[1:5]] == [[15, 20], [10, 20 - ry], [5, 20], [10, 20 + ry]]
    assert commands[1].coordinates[0] == pytest.approx(12.761423749153966)
    assert getattr(Path, shape)(10, 20, *radii).to_pdf_operations() == path.to_pdf_operations()


@pytest.mark.parametrize('rule, center', [(Rule.NonZero, b'\x00\x00\xff'), (Rule.EvenOdd, b'\xff\xff\xff')])
def test_real_clipping_winding_and_page_snapshot(tmp_path, rule, center):
    if shutil.which('pdftoppm') is None:
        pytest.skip('independent Poppler renderer unavailable')
    path = Path().add_rect(10, 10, 80, 80).add_rect(30, 30, 40, 40).with_winding_rule(rule)
    page = Page(100, 100)
    page.set_clipping_path(path)
    path.clear()  # Page must retain the installed path
    page.set_fill_color(Color.blue())
    page.draw_rect(0, 0, 100, 100)
    page.fill()
    doc = Document()
    doc.add_page(page)
    source = tmp_path / 'clip.pdf'
    source.write_bytes(doc.save_to_bytes())
    subprocess.run(['pdftoppm', '-r', '72', '-singlefile', str(source), str(tmp_path / 'raster')], check=True, capture_output=True, timeout=30)
    magic, width, height, maximum, pixels = (tmp_path / 'raster.ppm').read_bytes().split(None, 4)
    assert (magic, width, height, maximum) == (b'P6', b'100', b'100', b'255')
    assert pixels[(20 * 100 + 20) * 3: (20 * 100 + 20) * 3 + 3] == b'\x00\x00\xff'
    assert pixels[(50 * 100 + 50) * 3: (50 * 100 + 50) * 3 + 3] == center
    assert pixels[(5 * 100 + 5) * 3: (5 * 100 + 5) * 3 + 3] == b'\xff\xff\xff'
