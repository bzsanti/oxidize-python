"""Atomic existing-annotation edits preserve bytes, identities and core validation."""
from pathlib import Path
import pytest
import oxidize_pdf as op
from test_existing_document import fixture_pdf

QUAD = [(10., 50.), (80., 50.), (10., 35.), (80., 35.)]


def revision(base, result):
    assert isinstance(result, bytes)
    assert result.startswith(base)
    assert result.count(b'%%EOF') == base.count(b'%%EOF') + 1
    assert op.PdfReader.from_bytes(result).page_count == 2






@pytest.mark.parametrize('alignment', [op.FreeTextAlignment.Left, op.FreeTextAlignment.Center, op.FreeTextAlignment.Right])
def test_free_text_full_options_update_and_removal(tmp_path, alignment):
    _, base = fixture_pdf(tmp_path / 'free.pdf')
    editor = op.IncrementalFreeTextEditor(base)
    added = editor.apply([op.FreeTextMutation.add(0, [10., 20., 180., 80.], 'Hola', '/Helv 12 Tf 0 g', alignment)])
    revision(base, added.pdf_bytes)
    annotation, = added.annotations
    assert (annotation.page_index, annotation.contents, annotation.alignment) == (0, 'Hola', alignment)
    assert annotation.rect == [10., 20., 180., 80.]
    assert annotation.default_appearance == '/Helv 12 Tf 0 g'
    reader = op.IncrementalFreeTextEditor(added.pdf_bytes)
    assert reader.annotations()[0].id == annotation.id
    edited = reader.apply([op.FreeTextMutation.update(annotation.id, [20., 30., 190., 90.], 'Nuevo', '/Helv 10 Tf 1 0 0 rg', op.FreeTextAlignment.Center)])
    revision(added.pdf_bytes, edited.pdf_bytes)
    current, = edited.annotations
    assert current.id == annotation.id
    assert current.contents == 'Nuevo' and current.rect == [20., 30., 190., 90.]
    assert current.default_appearance == '/Helv 10 Tf 1 0 0 rg'
    assert current.alignment == op.FreeTextAlignment.Center
    removed = op.IncrementalFreeTextEditor(edited.pdf_bytes).apply([op.FreeTextMutation.remove(current.id)])
    revision(edited.pdf_bytes, removed.pdf_bytes)
    assert removed.annotations == []


@pytest.mark.parametrize('kind', ['FreeText'])
def test_invalid_annotation_batch_does_not_mutate_editor(tmp_path, kind):
    _, base = fixture_pdf(tmp_path / 'invalid.pdf')
    editor = getattr(op, 'Incremental' + kind + 'Editor')(base)
    identity = getattr(op, kind + 'Id')(9999, 7)
    with pytest.raises(op.PdfError):
        editor.apply([getattr(op, kind + 'Mutation').remove(identity)])
    assert editor.apply([]).pdf_bytes == base
    with pytest.raises(op.PdfError):
        getattr(op, 'Incremental' + kind + 'Editor')(b'broken').apply([])




@pytest.mark.parametrize('kind', ['FreeText'])
@pytest.mark.parametrize('permission,allowed', [(1,False),(2,False),(3,True)])
def test_annotation_edits_enforce_docmdp_permissions(kind, permission, allowed):
    # Synthetic policy variants invalidate the original signature. This checks
    # permissions, not cryptographic validity (covered separately by CMS tests).
    base = (Path(__file__).parent / 'fixtures/signatures/docmdp_p2_rsa.pdf').read_bytes()
    assert b'/P 2' in base
    base = base.replace(b'/P 2', f'/P {permission}'.encode(), 1)
    editor = getattr(op, 'Incremental' + kind + 'Editor')(base)
    assert editor.apply([]).pdf_bytes == base
    mutation = op.FreeTextMutation.add(0, [10.,20.,180.,80.], 'Policy', '/Helv 12 Tf 0 g', op.FreeTextAlignment.Left)
    if allowed:
        assert editor.apply([mutation]).pdf_bytes.startswith(base)
    else:
        with pytest.raises(op.PdfError, match='DocMDP'):
            editor.apply([mutation])

@pytest.mark.parametrize('rect,contents,appearance', [
    ([10.,20.,10.,80.], 'Text', '/Helv 12 Tf 0 g'),
    ([10.,20.,float('nan'),80.], 'Text', '/Helv 12 Tf 0 g'),
    ([10.,20.,180.,80.], '', '/Helv 12 Tf 0 g'),
    ([10.,20.,180.,80.], 'Text', 'not a default appearance'),
])
def test_free_text_invalid_batch_is_atomic(tmp_path, rect, contents, appearance):
    _, base = fixture_pdf(tmp_path / 'invalid-batch.pdf')
    editor = op.IncrementalFreeTextEditor(base)
    good = op.FreeTextMutation.add(0, [10.,20.,180.,80.], 'Valid', '/Helv 12 Tf 0 g', op.FreeTextAlignment.Left)
    bad = op.FreeTextMutation.add(0, rect, contents, appearance, op.FreeTextAlignment.Left)
    with pytest.raises(op.PdfParseError):
        editor.apply([good, bad])
    assert editor.annotations() == []
    assert editor.apply([]).pdf_bytes == base
    assert len(editor.apply([good]).annotations) == 1
