"""Native annotation editors, independent PDF fixtures and external-reader checks."""
import base64
import json
from pathlib import Path
import shutil
import struct
import subprocess

import pytest
import oxidize_pdf as p

N = p.IncrementalTextNoteEditor
H = p.IncrementalHighlightEditor
NM = p.TextNoteMutation
HM = p.HighlightMutation
QUAD = [(40., 90.), (100., 90.), (40., 70.), (100., 70.)]
SECOND_QUAD = [(120., 150.), (170., 150.), (120., 130.), (170., 130.)]
TEXT = 'café 世界 😀'


def annotation_pdf(*, indirect=False, xref_stream=False, mode='normal', permission=None):
    """Two pages, rotated/inherited crop bounds, foreign annotation and opaque keys."""
    content = b'0 0 1 rg 50 200 60 40 re f\n'
    note = b'<< /Type /Annot /Subtype /Text /Rect [40 50 70 90] /Contents (old note) /Name /Comment /Open true /Vendor << /Raw <00ff> >> >>'
    mark = b'<< /Type /Annot /Subtype /Highlight /Rect [40 70 100 90] /QuadPoints [40 90 100 90 40 70 100 70] /C [1 0.5 0] /CA 0.75 /Contents (old highlight) /Vendor <00ff> >>'
    entries = b'[7 9 R 8 4 R 9 0 R]'
    if mode == 'direct_note':
        entries = b'[' + note + b' 8 4 R 9 0 R]'
    if mode == 'direct_highlight':
        entries = b'[7 9 R ' + mark + b' 9 0 R]'
    annots = b'10 0 R' if indirect else entries
    second_annots = annots if mode == 'shared' else b'[]'
    catalog = b'<< /Type /Catalog /Pages 2 0 R /Metadata 11 0 R'
    if permission is not None:
        catalog += b' /Perms << /DocMDP 13 0 R >>'
    catalog += b' >>'
    metadata = b'<x:xmpmeta xmlns:x="adobe:ns:meta/">untouched</x:xmpmeta>'
    objects = [
        (1, 0, catalog),
        (2, 0, b'<< /Type /Pages /Count 2 /Kids [3 0 R 4 0 R] /MediaBox [10 20 310 420] /CropBox [20 30 290 400] >>'),
        (3, 0, b'<< /Type /Page /Parent 2 0 R /Rotate 90 /Contents 5 0 R /Resources << >> /Annots ' + annots + b' >>'),
        (4, 0, b'<< /Type /Page /Parent 2 0 R /Contents 6 0 R /Resources << >> /Annots ' + second_annots + b' >>'),
        (5, 0, b'<< /Length ' + str(len(content)).encode() + b' >>\nstream\n' + content + b'endstream'),
        (6, 0, b'<< /Length 0 >>\nstream\n\nendstream'),
        (7, 9, note), (8, 4, mark),
        (9, 0, b'<< /Type /Annot /Subtype /Link /Rect [200 200 220 220] /A << /S /URI /URI (https://example.invalid/) >> >>'),
        (10, 0, entries),
        (11, 0, b'<< /Type /Metadata /Subtype /XML /Length ' + str(len(metadata)).encode() + b' >>\nstream\n' + metadata + b'\nendstream'),
        (12, 0, b'<< /Title (preserved title) /Producer (independent fixture) >>'),
    ]
    if permission is not None:
        objects.append((13, 0, b'<< /Type /Sig /ByteRange [0 0000000000 0000000000 0000000000] /Contents <00> /Reference [<< /TransformMethod /DocMDP /TransformParams << /Type /TransformParams /P ' + str(permission).encode() + b' /V /1.2 >> >>] >>'))
    data = bytearray(b'%PDF-1.7\n')
    offsets = []
    for number, generation, body in objects:
        offsets.append((len(data), generation))
        data.extend(f'{number} {generation} obj\n'.encode() + body + b'\nendobj\n')
    xref = len(data)
    size = len(objects) + 1
    if xref_stream:
        entries_bytes = struct.pack('>BIH', 0, 0, 65535)
        for offset, generation in offsets:
            entries_bytes += struct.pack('>BIH', 1, offset, generation)
        entries_bytes += struct.pack('>BIH', 1, xref, 0)
        data.extend(f'{size} 0 obj\n<< /Type /XRef /Size {size + 1} /Root 1 0 R /Info 12 0 R /W [1 4 2] /Length {len(entries_bytes)} >>\nstream\n'.encode() + entries_bytes + b'\nendstream\nendobj\n')
    else:
        data.extend(f'xref\n0 {size}\n0000000000 65535 f \n'.encode())
        for offset, generation in offsets:
            data.extend(f'{offset:010} {generation:05} n \n'.encode())
        data.extend(f'trailer\n<< /Size {size} /Root 1 0 R /Info 12 0 R >>\n'.encode())
    data.extend(f'startxref\n{xref}\n%%EOF\n'.encode())
    if permission is not None:
        gap = data.index(b'/Contents <00>') + len(b'/Contents ')
        ranges = f'[0 {gap:010} {gap + 4:010} {len(data) - gap - 4:010}]'.encode()
        data = data.replace(b'[0 0000000000 0000000000 0000000000]', ranges)
    return bytes(data)


def highlight_add(page=0, *, opacity=None, contents=None):
    return HM.add(page, [p.HighlightQuad(QUAD), p.HighlightQuad(SECOND_QUAD)], p.HighlightColor([0.2, 0.4, 0.8]), opacity, contents)


def assert_revision(base, result):
    assert result.startswith(base) and len(result) > len(base)
    assert result.count(b'%%EOF') == base.count(b'%%EOF') + 1
    assert p.PdfReader.from_bytes(result).page_count == 2


@pytest.mark.parametrize('indirect', [False, True])
@pytest.mark.parametrize('xref_stream', [False, True])
def test_note_full_lifecycle_identity_and_order(indirect, xref_stream):
    source = annotation_pdf(indirect=indirect, xref_stream=xref_stream)
    editor = N(source)
    note, = editor.notes()
    assert (note.id, note.page_index, note.position, note.contents) == (p.TextNoteId(7, 9), 0, (40., 50.), 'old note')
    assert editor.apply([]).pdf_bytes == source and editor.apply([]).added_notes == []
    added = editor.apply([NM.add(1, (60., 80.), TEXT), NM.add(0, (100., 120.), 'second')])
    assert_revision(source, added.pdf_bytes)
    assert [(v.page_index, v.position, v.contents) for v in added.added_notes] == [(1, (60., 80.), TEXT), (0, (100., 120.), 'second')]
    assert added.added_notes[0].id != added.added_notes[1].id
    assert all(v.id.generation_number == 0 for v in added.added_notes)
    current = N(added.pdf_bytes)
    assert [(v.page_index, v.contents) for v in current.notes()] == [(0, 'old note'), (0, 'second'), (1, TEXT)]
    updated = current.apply([NM.update(note.id, (90., 110.), TEXT)])
    assert_revision(added.pdf_bytes, updated.pdf_bytes)
    assert updated.added_notes == []
    changed = next(v for v in N(updated.pdf_bytes).notes() if v.id == note.id)
    assert changed.position == (90., 110.) and changed.contents == TEXT
    removed = N(updated.pdf_bytes).apply([NM.remove(note.id)])
    assert_revision(updated.pdf_bytes, removed.pdf_bytes)
    assert {v.id for v in N(removed.pdf_bytes).notes()} == {v.id for v in added.added_notes}
    assert editor.notes()[0].contents == 'old note'


@pytest.mark.parametrize('indirect', [False, True])
@pytest.mark.parametrize('xref_stream', [False, True])
@pytest.mark.parametrize('value', [None, 0., .25, 1.])
def test_highlight_full_results_geometry_and_optional_fields(indirect, xref_stream, value):
    source = annotation_pdf(indirect=indirect, xref_stream=xref_stream)
    editor = H(source)
    old, = editor.highlights()
    assert old.id == p.HighlightId(8, 4) and old.rect == [40., 70., 100., 90.]
    assert old.quadrilaterals[0].points == QUAD and old.opacity.value == .75
    assert old.color.components == [1., .5, 0.] and old.contents == 'old highlight'
    assert editor.apply([]).pdf_bytes == source
    assert editor.apply([]).highlights[0].id == old.id
    opacity = None if value is None else p.HighlightOpacity(value)
    added = editor.apply([highlight_add(1, opacity=opacity, contents=TEXT if value is not None else None)])
    assert_revision(source, added.pdf_bytes)
    assert len(added.highlights) == 2 and added.highlights[0].id == old.id
    new = added.highlights[1]
    assert new.page_index == 1 and new.rect == [40., 70., 170., 150.]
    assert [v.points for v in new.quadrilaterals] == [QUAD, SECOND_QUAD]
    assert new.color.components == [.2, .4, .8]
    assert (None if new.opacity is None else new.opacity.value) == value
    assert new.contents == (TEXT if value is not None else None)
    removed = H(added.pdf_bytes).apply([HM.remove(old.id)])
    assert_revision(added.pdf_bytes, removed.pdf_bytes)
    assert [v.id for v in removed.highlights] == [new.id]
    assert H(removed.pdf_bytes).highlights()[0].contents == new.contents
    assert editor.highlights()[0].id == old.id


def test_owned_values_mutations_and_input_validation():
    points = QUAD.copy()
    quad = p.HighlightQuad(points)
    points.clear()
    quad.points.clear()
    color = p.HighlightColor([.2, .4, .8])
    color.components.clear()
    opacity = p.HighlightOpacity(.4)
    assert quad.points == QUAD and color.components == [.2, .4, .8] and opacity.value == .4
    quads = [quad]
    add = HM.add(1, quads, color, opacity, '')
    quads.clear()
    assert (add.kind, add.id, add.page_index, add.contents) == ('add', None, 1, '')
    assert add.color == color and add.opacity == opacity and add.quadrilaterals[0] == quad
    add.quadrilaterals.clear()
    assert len(add.quadrilaterals) == 1
    hid = p.HighlightId(8, 4)
    remove = HM.remove(hid)
    assert (remove.kind, remove.id, remove.quadrilaterals, remove.color, remove.opacity, remove.contents, remove.page_index) == ('remove', hid, None, None, None, None, None)
    nid = p.TextNoteId(7, 9)
    for mutation, kind, ident, page, position, contents in [
        (NM.add(1, (40., 50.), TEXT), 'add', None, 1, (40., 50.), TEXT),
        (NM.update(nid, (60., 80.), 'edited'), 'update', nid, None, (60., 80.), 'edited'),
        (NM.remove(nid), 'remove', nid, None, None, None),
    ]:
        assert (mutation.kind, mutation.id, mutation.page_index, mutation.position, mutation.contents) == (kind, ident, page, position, contents)
    result = H(annotation_pdf()).apply([add])
    result.highlights.clear()
    result.highlights[0].quadrilaterals.clear()
    assert len(result.highlights) == 2 and result.highlights[0].quadrilaterals[0].points == QUAD
    assert result.highlights[1].contents == ''
    for obj, name in [(quad, 'points'), (color, 'components'), (opacity, 'value'), (nid, 'object_number'), (add, 'kind'), (result.highlights[0], 'contents')]:
        with pytest.raises(AttributeError):
            setattr(obj, name, None)
    assert hash(nid) == hash(p.TextNoteId(7, 9)) and nid != p.TextNoteId(7, 0)
    assert hash(hid) == hash(p.HighlightId(8, 4)) and hid != p.HighlightId(8, 0)
    for cls in [p.TextNoteId, p.HighlightId]:
        for number, generation in [(-1, 0), (1 << 32, 0), (1, -1), (1, 65536)]:
            with pytest.raises(OverflowError):
                cls(number, generation)
    with pytest.raises(TypeError):
        NM.remove(hid)
    with pytest.raises(TypeError):
        HM.remove(nid)
    with pytest.raises(OverflowError):
        NM.add(-1, (40., 50.), 'bad')
    with pytest.raises(TypeError):
        HM.add(0, [quad], color, .4)


@pytest.mark.parametrize('make', [
    lambda: p.HighlightColor([0., -0.01, 1.]),
    lambda: p.HighlightColor([0., 1.01, 1.]),
    lambda: p.HighlightColor([0., float('nan'), 1.]),
    lambda: p.HighlightOpacity(float('inf')),
    lambda: p.HighlightOpacity(-0.01),
    lambda: p.HighlightOpacity(1.01),
    lambda: p.HighlightQuad([(0., 0.)] * 4),
    lambda: p.HighlightQuad([(0., 0.), (1., 1.), (2., 2.), (3., 3.)]),
    lambda: p.HighlightQuad([(0., 1.), (1., 0.), (0., 0.), (1., 1.)]),
    lambda: p.HighlightQuad([(0., 1.), (float('nan'), 1.), (0., 0.), (1., 0.)]),
])
def test_highlight_validated_values_reject_invalid_inputs(make):
    with pytest.raises(p.PdfError):
        make()


@pytest.mark.parametrize('bad', [
    lambda: NM.add(2, (40., 50.), 'bad page'),
    lambda: NM.add(0, (40., 50.), ' \t'),
    lambda: NM.add(0, (19., 50.), 'outside crop'),
    lambda: NM.add(0, (271., 50.), 'outside crop'),
    lambda: NM.add(0, (float('nan'), 50.), 'nonfinite'),
    lambda: NM.update(p.TextNoteId(7, 9), (261., 100.), 'width remains 30'),
    lambda: NM.update(p.TextNoteId(7, 0), (40., 50.), 'wrong generation'),
    lambda: NM.remove(p.TextNoteId(8, 4)),
    lambda: NM.remove(p.TextNoteId(999, 0)),
])
def test_note_invalid_batch_is_atomic_and_retryable(bad):
    source = annotation_pdf()
    editor = N(source)
    good = NM.add(1, (40., 50.), 'valid')
    with pytest.raises(p.PdfError):
        editor.apply([good, bad()])
    assert editor.apply([]).pdf_bytes == source and len(editor.notes()) == 1
    assert editor.apply([good]).added_notes[0].contents == 'valid'


@pytest.mark.parametrize('bad', [
    lambda: highlight_add(2),
    lambda: HM.add(0, [], p.HighlightColor([1., 1., 0.])),
    lambda: HM.add(0, [p.HighlightQuad([(10., 90.), (100., 90.), (10., 70.), (100., 70.)])], p.HighlightColor([1., 1., 0.])),
    lambda: HM.remove(p.HighlightId(8, 0)),
    lambda: HM.remove(p.HighlightId(7, 9)),
    lambda: HM.remove(p.HighlightId(999, 0)),
])
def test_highlight_invalid_batch_is_atomic_and_retryable(bad):
    source = annotation_pdf()
    editor = H(source)
    with pytest.raises(p.PdfError):
        editor.apply([highlight_add(), bad()])
    assert editor.apply([]).pdf_bytes == source and len(editor.highlights()) == 1
    assert len(editor.apply([highlight_add()]).highlights) == 2


@pytest.mark.parametrize('kind', ['note', 'highlight'])
def test_conflicting_targets_and_wrong_mutation_types(kind):
    editor = N(annotation_pdf()) if kind == 'note' else H(annotation_pdf())
    mutation = NM.remove(p.TextNoteId(7, 9)) if kind == 'note' else HM.remove(p.HighlightId(8, 4))
    with pytest.raises(p.PdfError, match='more than once'):
        editor.apply([mutation, mutation])
    if kind == 'note':
        with pytest.raises(p.PdfError, match='more than once'):
            editor.apply([NM.update(p.TextNoteId(7, 9), (50., 60.), 'edit'), mutation])
    with pytest.raises(TypeError):
        editor.apply([highlight_add() if kind == 'note' else NM.add(0, (40., 50.), 'note')])


@pytest.mark.parametrize('kind,action', [('note','add'), ('note','remove'), ('note','update'), ('highlight','add'), ('highlight','remove')])
@pytest.mark.parametrize('permission', [1, 2, 3])
def test_docmdp_preserves_read_noop_and_enforces_mutations(kind, permission, action):
    source = annotation_pdf(permission=permission)
    editor = N(source) if kind == 'note' else H(source)
    assert len(editor.notes() if kind == 'note' else editor.highlights()) == 1
    assert editor.apply([]).pdf_bytes == source
    if kind == 'note':
        mutations = {'add': NM.add(0, (40., 50.), 'policy'), 'remove': NM.remove(p.TextNoteId(7, 9)), 'update': NM.update(p.TextNoteId(7, 9), (50., 60.), 'updated')}
    else:
        mutations = {'add': highlight_add(), 'remove': HM.remove(p.HighlightId(8, 4))}
    if permission == 3:
        result = editor.apply([mutations[action]])
        assert_revision(source, result.pdf_bytes)
        count = len(N(result.pdf_bytes).notes() if kind == 'note' else H(result.pdf_bytes).highlights())
        assert count == (2 if action == 'add' else 0 if action == 'remove' else 1)
    else:
        with pytest.raises(p.PdfPermissionError, match='DocMDP'):
            editor.apply([mutations[action]])
    assert editor.apply([]).pdf_bytes == source


@pytest.mark.parametrize('kind', ['note', 'highlight'])
def test_original_certification_fixture_rejects_p2(kind):
    source = (Path(__file__).parent / 'fixtures/signatures/docmdp_p2_rsa.pdf').read_bytes()
    editor = N(source) if kind == 'note' else H(source)
    mutation = NM.add(0, (40., 50.), 'policy') if kind == 'note' else highlight_add()
    with pytest.raises(p.PdfPermissionError, match='DocMDP'):
        editor.apply([mutation])


@pytest.mark.parametrize('kind', ['note', 'highlight'])
@pytest.mark.parametrize('mode', ['shared', 'direct'])
def test_unsupported_annotation_identity_rejected(kind, mode):
    source = annotation_pdf(mode=('direct_' + kind if mode == 'direct' else 'shared'))
    editor = N(source) if kind == 'note' else H(source)
    for operation in [editor.notes if kind == 'note' else editor.highlights, lambda: editor.apply([])]:
        with pytest.raises(p.PdfError):
            operation()


@pytest.mark.parametrize('kind', ['note', 'highlight'])
def test_encrypted_and_malformed_input_rejected(kind):
    doc = p.Document()
    doc.add_page(p.Page.a4())
    doc.encrypt('user', 'owner')
    for source in [b'', b'not PDF', doc.save_to_bytes()]:
        editor = N(source) if kind == 'note' else H(source)
        for operation in [editor.notes if kind == 'note' else editor.highlights, lambda: editor.apply([])]:
            with pytest.raises(p.PdfError):
                operation()


@pytest.mark.skipif(shutil.which('qpdf') is None, reason='qpdf independent reader unavailable')
@pytest.mark.parametrize('indirect', [False, True])
@pytest.mark.parametrize('xref_stream', [False, True])
def test_external_objects_unicode_metadata_and_content_preserved(tmp_path, indirect, xref_stream):
    source = annotation_pdf(indirect=indirect, xref_stream=xref_stream)
    first = N(source).apply([NM.update(p.TextNoteId(7, 9), (90., 110.), TEXT), NM.add(1, (60., 80.), 'added')])
    second = H(first.pdf_bytes).apply([highlight_add(1, opacity=p.HighlightOpacity(.25), contents=TEXT)])
    assert second.pdf_bytes.startswith(first.pdf_bytes) and first.pdf_bytes.startswith(source)
    before = tmp_path / 'before.pdf'
    after = tmp_path / 'after.pdf'
    before.write_bytes(source)
    after.write_bytes(second.pdf_bytes)
    def objects(path):
        subprocess.run(['qpdf', '--check', str(path)], capture_output=True, check=True, timeout=30)
        result = subprocess.run(['qpdf', '--json', '--json-stream-data=inline', str(path)], capture_output=True, check=True, timeout=30)
        return json.loads(result.stdout)['qpdf'][1]
    original, edited = objects(before), objects(after)
    for number in [1, 2, 5, 6, 9, 11, 12]:
        assert edited[f'obj:{number} 0 R'] == original[f'obj:{number} 0 R']
    note = edited['obj:7 9 R']['value']
    assert note['/Contents'] == 'u:' + TEXT and note['/Rect'] == [90, 110, 120, 150]
    assert note['/Name'] == '/Comment' and note['/Open'] is True and note['/Vendor']['/Raw'] == 'b:00ff'
    mark = second.highlights[-1]
    entry = edited[f'obj:{mark.id.object_number} {mark.id.generation_number} R']['value']
    assert entry['/QuadPoints'] == [40, 90, 100, 90, 40, 70, 100, 70, 120, 150, 170, 150, 120, 130, 170, 130]
    assert entry['/Rect'] == [40, 70, 170, 150] and entry['/C'] == [.2, .4, .8] and entry['/CA'] == .25
    assert entry['/Contents'] == 'u:' + TEXT
    assert base64.b64decode(edited['obj:5 0 R']['stream']['data']) == b'0 0 1 rg 50 200 60 40 re f\n'
    if shutil.which('pdftoppm'):
        for path in [before, after]:
            subprocess.run(['pdftoppm', '-hide-annotations', '-r', '36', '-f', '1', '-singlefile', str(path), str(path.with_suffix(''))], check=True, capture_output=True, timeout=30)
        assert before.with_suffix('.ppm').read_bytes() == after.with_suffix('.ppm').read_bytes()
