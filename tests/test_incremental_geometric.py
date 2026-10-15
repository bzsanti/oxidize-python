"""#276: geometric edits on independent PDFs, immutable batches and policy."""
from pathlib import Path
import re

import pytest
import oxidize_pdf as p
from test_existing_document import fixture_pdf

G = p.GeometricGeometry
M = p.GeometricMutation
E = p.IncrementalGeometricEditor
LE = p.GeometricLineEnding


def style():
    return p.GeometricStyle(p.GeometricColor.rgb([0.25, 0.5, 1.0]), 2.0,
                            p.GeometricColor.cmyk([0.0, 0.25, 0.5, 1.0]), [3., 2.], 0.5)


def shapes():
    return [G.line((10., 20.), (60., 70.), LE.OpenArrow, LE.ClosedArrow),
            G.square([10., 20., 60., 70.]), G.circle([10., 20., 60., 70.]),
            G.polygon([(10., 20.), (60., 20.), (30., 70.)]),
            G.polyline([(10., 20.), (60., 20.), (30., 70.)], LE.Circle, LE.Slash)]


def geometry_values(g):
    return (g.kind, g.rect, g.vertices, g.start, g.end, g.start_ending, g.end_ending)


@pytest.mark.parametrize('index,subtype', list(enumerate(['Line', 'Square', 'Circle', 'Polygon', 'PolyLine'])))
def test_geometric_shapes_styles_and_readback(tmp_path, index, subtype):
    _, base = fixture_pdf(tmp_path / 'base.pdf')
    editor = E(base)
    geometry = shapes()[index]
    result = editor.apply([M.add(1, geometry, style())])
    assert result.pdf_bytes.startswith(base)
    assert result.pdf_bytes.count(b'%%EOF') == base.count(b'%%EOF') + 1
    assert p.PdfReader.from_bytes(result.pdf_bytes).page_count == 2
    annotation, = result.annotations
    reread, = E(result.pdf_bytes).annotations()
    assert reread.id == annotation.id and reread.page_index == 1
    assert annotation.id.object_number > 0 and annotation.id.generation_number == 0
    assert geometry_values(reread.geometry) == geometry_values(geometry)
    actual = reread.style
    assert actual.stroke_color.space == p.GeometricColorSpace.Rgb
    assert actual.stroke_color.components == [0.25, 0.5, 1.0]
    assert actual.fill_color.space == p.GeometricColorSpace.Cmyk
    assert actual.fill_color.components == [0.0, 0.25, 0.5, 1.0]
    assert (actual.width, actual.dash_pattern, actual.opacity) == (2.0, [3., 2.], 0.5)
    # Inspect emitted PDF tokens as well as the geometric reader result.
    reader = p.PdfReader.from_bytes(result.pdf_bytes)
    assert f'/Subtype /{subtype}'.encode() in result.pdf_bytes[len(base):]
    assert b'/AP' in result.pdf_bytes[len(base):] and b'/Annots' in result.pdf_bytes[len(base):]
    assert reader.page_count == 2
    assert editor.annotations() == [] and editor.apply([]).pdf_bytes == base


@pytest.mark.parametrize('ending', [LE.None_, LE.Square, LE.Circle, LE.Diamond, LE.OpenArrow,
                                    LE.ClosedArrow, LE.Butt, LE.ROpenArrow, LE.RClosedArrow, LE.Slash])
def test_geometric_line_endings_and_gray(tmp_path, ending):
    _, base = fixture_pdf(tmp_path / 'line.pdf')
    geom = G.line((20., 30.), (60., 80.), ending, ending)
    result = E(base).apply([M.add(0, geom, p.GeometricStyle(p.GeometricColor.gray(0.25), 1.))])
    annotation, = E(result.pdf_bytes).annotations()
    assert annotation.geometry.start_ending == ending == annotation.geometry.end_ending
    assert annotation.style.stroke_color == p.GeometricColor.gray(0.25)
    assert annotation.style.fill_color is None
    assert annotation.style.dash_pattern is None and annotation.style.opacity is None


def test_geometric_update_remove_identity_and_ownership(tmp_path):
    _, base = fixture_pdf(tmp_path / 'update.pdf')
    points = [(10., 20.), (60., 70.)]
    geometry = G.polyline(points)
    points[0] = (999., 999.)
    first = E(base).apply([M.add(0, geometry, style())])
    annotation, = first.annotations
    assert annotation.geometry.vertices == [(10., 20.), (60., 70.)]
    identity = annotation.id
    with pytest.raises(p.PdfParseError, match='subtype'):
        E(first.pdf_bytes).apply([M.update(identity, G.circle([30., 40., 70., 80.]), style())])
    update = M.update(identity, G.polyline([(30., 40.), (70., 80.)]), style())
    second = E(first.pdf_bytes).apply([update])
    assert second.pdf_bytes.startswith(first.pdf_bytes)
    current, = second.annotations
    assert current.id == identity and current.page_index == 0
    assert current.geometry.kind == p.GeometricKind.PolyLine
    assert current.geometry.vertices == [(30., 40.), (70., 80.)]
    # Returned collections are snapshots, not mutable references into the editor/results.
    current.geometry.vertices[0] = (-999., -999.)
    second.annotations.clear()
    assert second.annotations[0].geometry.vertices == [(30., 40.), (70., 80.)]
    removed = E(second.pdf_bytes).apply([M.remove(identity)])
    assert removed.pdf_bytes.startswith(second.pdf_bytes)
    assert removed.annotations == E(removed.pdf_bytes).annotations() == []
    assert first.annotations[0].geometry.kind == p.GeometricKind.PolyLine


@pytest.mark.parametrize('make', [
    lambda: p.GeometricColor.gray(-0.1),
    lambda: p.GeometricColor.rgb([0., 0., float('nan')]),
    lambda: p.GeometricColor.cmyk([0., 0., 0., 2.]),
    lambda: p.GeometricStyle(p.GeometricColor.gray(0.), 0.),
    lambda: p.GeometricStyle(p.GeometricColor.gray(0.), float('inf')),
    lambda: p.GeometricStyle(p.GeometricColor.gray(0.), 1., opacity=1.1),
    lambda: p.GeometricStyle(p.GeometricColor.gray(0.), 1., dash_pattern=[]),
    lambda: p.GeometricStyle(p.GeometricColor.gray(0.), 1., dash_pattern=[0., 0.]),
    lambda: p.GeometricStyle(p.GeometricColor.gray(0.), 1., dash_pattern=[-1., 2.]),
    lambda: p.GeometricStyle(p.GeometricColor.gray(0.), 1., dash_pattern=[1.] * 257),
])
def test_geometric_style_validation(make):
    with pytest.raises(p.PdfParseError):
        make()


@pytest.mark.parametrize('geometry', [G.square([10., 20., 5., 30.]), G.circle([0., 0., 0., 1.]),
                                     G.polygon([(0., 0.), (1., 1.)]), G.polyline([]),
                                     G.line((float('nan'), 1.), (2., 3.))])
def test_geometric_invalid_batch_atomic_retry(tmp_path, geometry):
    _, base = fixture_pdf(tmp_path / 'atomic.pdf')
    editor = E(base)
    good = M.add(0, shapes()[0], style())
    with pytest.raises(p.PdfParseError):
        editor.apply([good, M.add(1, geometry, style())])
    assert editor.annotations() == [] and editor.apply([]).pdf_bytes == base
    assert len(editor.apply([good]).annotations) == 1


@pytest.mark.parametrize('bad', [M.remove(p.GeometricId(9999, 7)), M.add(99, shapes()[0], style())])
def test_geometric_missing_target_atomic(tmp_path, bad):
    _, base = fixture_pdf(tmp_path / 'missing.pdf')
    editor = E(base)
    with pytest.raises(p.PdfParseError):
        editor.apply([M.add(0, shapes()[0], style()), bad])
    assert editor.apply([]).pdf_bytes == base


@pytest.mark.parametrize('permission,allowed', [(1, False), (2, False), (3, True)])
def test_geometric_docmdp_policy(permission, allowed):
    # Modified fixtures exercise permission interpretation, not signature authenticity.
    source = (Path(__file__).parent / 'fixtures/signatures/docmdp_p2_rsa.pdf').read_bytes()
    assert b'/P 2' in source
    source = source.replace(b'/P 2', f'/P {permission}'.encode(), 1)
    editor = E(source)
    assert editor.apply([]).pdf_bytes == source
    mutation = M.add(0, shapes()[0], style())
    if allowed:
        assert editor.apply([mutation]).pdf_bytes.startswith(source)
    else:
        with pytest.raises(p.PdfPermissionError, match='DocMDP'):
            editor.apply([mutation])


@pytest.mark.parametrize('data', [b'', b'not a PDF', b'%PDF-1.7\n'])
def test_geometric_invalid_pdf(data):
    editor = E(data)
    with pytest.raises(p.PdfError):
        editor.annotations()
    with pytest.raises(p.PdfError):
        editor.apply([])


def test_geometric_existing_generation_and_unrelated_keys():
    # Hand-authored annotation with a nonzero generation, not created by this editor.
    objects = [(1, 0, b'<< /Type /Catalog /Pages 2 0 R >>'),
               (2, 0, b'<< /Type /Pages /Count 1 /Kids [3 0 R] >>'),
               (3, 0, b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 300] /Annots [4 7 R] >>'),
               (4, 7, b'<< /Type /Annot /Subtype /Square /Rect [10 20 60 70] /C [0] /BS << /W 1 >> /Custom (KEEP-ME) >>')]
    data = b'%PDF-1.7\n'
    offsets = []
    for number, generation, content in objects:
        offsets.append(len(data))
        data += f'{number} {generation} obj\n'.encode() + content + b'\nendobj\n'
    xref = len(data)
    data += b'xref\n0 5\n0000000000 65535 f \n'
    for offset, (_, generation, _) in zip(offsets, objects):
        data += f'{offset:010d} {generation:05d} n \n'.encode()
    data += f'trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
    editor = E(data)
    annotation, = editor.annotations()
    assert annotation.id == p.GeometricId(4, 7)
    with pytest.raises(p.PdfParseError):
        editor.apply([M.remove(p.GeometricId(4, 0))])
    result = editor.apply([M.update(annotation.id, G.square([20., 30., 70., 80.]), style())])
    assert result.pdf_bytes.startswith(data)
    assert b'4 7 obj' in result.pdf_bytes[len(data):]
    custom = re.search(rb'/Custom\s+(?:<([0-9A-Fa-f]+)>|\(([^)]*)\))', result.pdf_bytes[len(data):])
    assert custom is not None
    value = bytes.fromhex(custom[1].decode()) if custom[1] is not None else custom[2]
    assert value == b'KEEP-ME'
    reread, = E(result.pdf_bytes).annotations()
    assert reread.id == annotation.id and reread.geometry.rect == [20., 30., 70., 80.]
    with pytest.raises(p.PdfParseError):
        editor.apply([M.remove(annotation.id), M.remove(annotation.id)])
    assert editor.annotations()[0].geometry.rect == [10., 20., 60., 70.]


@pytest.mark.parametrize('make', [lambda: p.GeometricId(-1, 0), lambda: p.GeometricId(1, 65536),
                                 lambda: M.add(-1, shapes()[0], style())])
def test_geometric_unsigned_boundaries(make):
    with pytest.raises(OverflowError):
        make()
