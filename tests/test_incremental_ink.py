"""Incremental ink contracts retain original color space, points and policy."""
from pathlib import Path
import pytest
import oxidize_pdf as op
from test_existing_document import fixture_pdf

POINTS = [(10., 20.), (80., 60.)]


@pytest.mark.parametrize('color,space,components', [
    (op.InkColor.gray(0.25), op.InkColorSpace.Gray, [0.25]),
    (op.InkColor.rgb([1.,0.5,0.]), op.InkColorSpace.Rgb, [1.,0.5,0.]),
    (op.InkColor.cmyk([0.,0.25,0.5,1.]), op.InkColorSpace.Cmyk, [0.,0.25,0.5,1.]),
])
@pytest.mark.parametrize('opacity', [None, 0.25])
def test_ink_style_geometry_and_original_color_space(tmp_path, color, space, components, opacity):
    _, base = fixture_pdf(tmp_path / 'ink.pdf')
    editor = op.IncrementalInkEditor(base)
    assert editor.annotations() == []
    assert editor.apply([]).pdf_bytes == base
    stroke = op.InkStroke(POINTS)
    result = editor.apply([op.InkMutation.add(1, [stroke], color, 2., opacity)])
    assert result.pdf_bytes.startswith(base)
    assert result.pdf_bytes.count(b'%%EOF') == base.count(b'%%EOF') + 1
    assert op.PdfReader.from_bytes(result.pdf_bytes).page_count == 2
    annotation, = result.annotations
    assert annotation.id.object_number > 0 and annotation.id.generation_number == 0
    assert annotation.page_index == 1
    assert annotation.rect == [9.,19.,81.,61.]
    assert [s.points for s in annotation.strokes] == [POINTS]
    assert annotation.color.space == space and annotation.color.components == components
    assert annotation.color == color
    assert annotation.width == 2. and annotation.opacity == opacity
    reread, = op.IncrementalInkEditor(result.pdf_bytes).annotations()
    assert reread.id == annotation.id and reread.color == color
    assert editor.annotations() == []


def test_ink_update_and_remove_keep_identity_and_single_point_strokes(tmp_path):
    _, base = fixture_pdf(tmp_path / 'update.pdf')
    first = op.IncrementalInkEditor(base).apply([op.InkMutation.add(0, [op.InkStroke(POINTS)], op.InkColor.gray(0.), 2.)])
    identity = first.annotations[0].id
    points = [(30.,40.)]
    stroke = op.InkStroke(points)
    points.append((100.,100.))  # Constructor takes an owned snapshot.
    update = op.InkMutation.update(identity, [stroke], op.InkColor.cmyk([0.,0.,0.,1.]), 4., 0.5)
    second = op.IncrementalInkEditor(first.pdf_bytes).apply([update])
    assert second.pdf_bytes.startswith(first.pdf_bytes)
    current, = second.annotations
    assert current.id == identity and current.strokes[0].points == [(30.,40.)]
    assert current.width == 4. and current.opacity == 0.5
    assert current.color.space == op.InkColorSpace.Cmyk
    removed = op.IncrementalInkEditor(second.pdf_bytes).apply([op.InkMutation.remove(identity)])
    assert removed.pdf_bytes.startswith(second.pdf_bytes)
    assert removed.annotations == []
    assert op.IncrementalInkEditor(removed.pdf_bytes).annotations() == []


@pytest.mark.parametrize('make', [
    lambda: op.InkStroke([]),
    lambda: op.InkStroke([(float('nan'),0.)]),
    lambda: op.InkColor.gray(-0.1),
    lambda: op.InkColor.rgb([1.,2.,0.]),
    lambda: op.InkColor.cmyk([0.,0.,float('inf'),0.]),
    lambda: op.InkMutation.add(0, [op.InkStroke(POINTS)], op.InkColor.gray(0.), 0.),
    lambda: op.InkMutation.add(0, [op.InkStroke(POINTS)], op.InkColor.gray(0.), 1., 2.),
])
def test_ink_validation_rejects_invalid_values(make):
    with pytest.raises(op.PdfParseError):
        make()


def test_ink_invalid_batch_is_atomic_and_retryable(tmp_path):
    _, base = fixture_pdf(tmp_path / 'atomic.pdf')
    editor = op.IncrementalInkEditor(base)
    good = op.InkMutation.add(0, [op.InkStroke(POINTS)], op.InkColor.gray(0.), 1.)
    with pytest.raises(op.PdfParseError):
        editor.apply([good, op.InkMutation.remove(op.InkId(9999,7))])
    assert editor.annotations() == [] and editor.apply([]).pdf_bytes == base
    assert len(editor.apply([good]).annotations) == 1


@pytest.mark.parametrize('permission,allowed', [(1,False),(2,False),(3,True)])
def test_ink_preserves_core_certification_policy(permission, allowed):
    # P variants exercise policy interpretation, not authenticity of the modified signature.
    source = (Path(__file__).parent / 'fixtures/signatures/docmdp_p2_rsa.pdf').read_bytes()
    assert b'/P 2' in source
    source = source.replace(b'/P 2', f'/P {permission}'.encode(), 1)
    editor = op.IncrementalInkEditor(source)
    assert editor.apply([]).pdf_bytes == source
    mutation = op.InkMutation.add(0, [op.InkStroke(POINTS)], op.InkColor.gray(0.), 1.)
    if allowed:
        assert editor.apply([mutation]).pdf_bytes.startswith(source)
    else:
        with pytest.raises(op.PdfPermissionError, match='DocMDP'):
            editor.apply([mutation])
