"""Tagged editor contracts against an independently serialized structure graph."""
from pathlib import Path
import subprocess
import shutil
import pytest
import oxidize_pdf as p
from test_tagged_validation import tagged_pdf

E = p.IncrementalTaggedPdfEditor
M = p.TaggedPdfMutation
R = p.TaggedPdfObjectRef
V = p.PdfValue
ROOT, ELEMENT, PAGE = R(5, 0), R(6, 7), R(3, 0)


def test_identity_plan_and_snapshots():
    source = tagged_pdf()
    editor = E(source)
    assert editor.preparation_objects() == []
    assert editor.preflight().valid
    plan = editor.plan([])
    assert plan.changed_objects == [] and plan.mutations == []
    report = editor.apply([])
    assert report.pdf_bytes == source
    assert report.validation_before.valid and report.validation_after.valid
    assert editor.plan([M.set_element_attribute(ELEMENT, 'Alt', V.string(b'alternative'))]).changed_objects == []


def test_attribute_preservation_and_external_reader(tmp_path):
    source = tagged_pdf()
    mutation = M.set_element_attribute(ELEMENT, 'T', V.string(b'new title'))
    editor = E(source)
    plan = editor.plan([mutation])
    assert [(v.object, v.kind) for v in plan.changed_objects] == [(ELEMENT, p.TaggedPdfChangedObjectKind.StructureElement)]
    request, = plan.mutations
    assert (request.kind, request.element, request.attribute_key, request.value.value) == ('set_element_attribute', ELEMENT, 'T', b'new title')
    assert request.parent is None and request.index is None
    report = editor.apply([mutation])
    assert report.pdf_bytes.startswith(source) and len(report.pdf_bytes) > len(source)
    assert report.validation_before.elements[0].title == 'title'
    after = report.validation_after
    assert after.valid and after.elements[0].title == 'new title'
    assert after.elements[0].object == ELEMENT
    assert after.elements[0].dictionary['Vendor'].value['Raw'].value == b'\x00\xff'
    assert after.class_map['C1'].value['Vendor'].value == b'\x00\xff'
    assert after.role_map == {'CustomP': 'P'}
    report.plan.changed_objects.clear()
    report.validation_after.elements.clear()
    assert len(report.plan.changed_objects) == 1 and len(report.validation_after.elements) == 1
    assert editor.apply([]).pdf_bytes == source
    removed = E(report.pdf_bytes).apply([M.set_element_attribute(ELEMENT, 'T')])
    assert removed.validation_after.elements[0].title is None


def test_create_reparent_and_mutation_fields():
    source = tagged_pdf()
    mutation = M.create_element(ROOT, 'Div', {'Vendor': V.string(b'opaque')}, 0)
    assert mutation.parent == ROOT and mutation.structure_type == 'Div' and mutation.index == 0
    assert mutation.attributes['Vendor'].value == b'opaque'
    mutation.attributes.clear()
    report = E(source).apply([mutation])
    created, = [v for v in report.validation_after.elements if v.structure_type == 'Div']
    assert created.parent == ROOT and created.dictionary['Vendor'].value == b'opaque'
    move = M.reparent_element(ELEMENT, created.object)
    assert move.element == ELEMENT and move.new_parent == created.object
    moved = E(report.pdf_bytes).apply([move])
    assert moved.pdf_bytes.startswith(report.pdf_bytes)
    existing, = [v for v in moved.validation_after.elements if v.object == ELEMENT]
    assert existing.parent == created.object and existing.marked_content_count == 1
    assert moved.validation_after.valid


def test_parent_tree_add_remove_and_mcid():
    source = tagged_pdf()
    add = M.set_parent_tree_entry(42, V.reference(6, 7))
    assert add.parent_tree_key == 42 and add.value.value == (6, 7)
    report = E(source).apply([add])
    assert report.validation_after.parent_tree[42].value == (6, 7)
    assert report.validation_after.parent_tree[0].value[0].value == (6, 7)
    removed = E(report.pdf_bytes).apply([M.set_parent_tree_entry(42)])
    assert 42 not in removed.validation_after.parent_tree
    assert removed.validation_after.parent_tree[0].value[0].value == (6, 7)
    association = M.associate_mcid(ELEMENT, PAGE, 1)
    assert association.element == ELEMENT and association.page == PAGE and association.mcid == 1
    associated = E(tagged_pdf(unassociated=True)).apply([association])
    assert associated.validation_after.content_mcids[PAGE] == [0, 1]
    assert associated.validation_after.parent_tree[0].value[0].value == (6, 7)


def test_language_preparation_and_recovery():
    source = tagged_pdf(language=False)
    original = E(source)
    prepared = original.with_document_language('es-ES').with_recovered_indexes()
    assert R(1, 0) in prepared.preparation_objects()
    report = prepared.apply([])
    assert report.pdf_bytes.startswith(source) and report.validation_after.valid
    assert report.plan.changed_objects == []
    assert original.apply([]).pdf_bytes == source
    with pytest.raises(p.PdfError, match='already present'):
        prepared.with_document_language('en')
    with pytest.raises(p.PdfError, match='blank'):
        original.with_document_language(' ')
    assert prepared.apply([]).pdf_bytes == report.pdf_bytes


@pytest.mark.parametrize('mutation', [
    M.set_element_attribute(ELEMENT, 'P', V.reference(5, 0)),
    M.set_element_attribute(R(999, 0), 'Alt', V.string(b'value')),
    M.reparent_element(ELEMENT, ELEMENT),
    M.associate_mcid(ELEMENT, PAGE, 999),
    M.create_element(ROOT, 'P', index=999),
])
def test_invalid_batch_is_atomic(mutation):
    source = tagged_pdf()
    editor = E(source)
    for operation in (editor.plan, editor.apply):
        with pytest.raises(p.PdfError):
            operation([M.set_element_attribute(ELEMENT, 'T', V.string(b'changed')), mutation])
    assert editor.apply([]).pdf_bytes == source
    assert editor.apply([M.set_element_attribute(ELEMENT, 'T', V.string(b'retry'))]).validation_after.elements[0].title == 'retry'


@pytest.mark.parametrize('permission', [1, 2, 3])
def test_docmdp_rejects_structure_edits(permission):
    source = (Path(__file__).parent / 'fixtures/signatures/docmdp_p2_rsa.pdf').read_bytes()
    source = source.replace(b'/P 2', f'/P {permission}'.encode(), 1)
    editor = E(source)
    for operation in (editor.plan, editor.apply):
        with pytest.raises(p.PdfPermissionError, match='DocMDP'):
            operation([M.set_element_attribute(ELEMENT, 'T', V.string(b'changed'))])


def test_limits_and_input_errors():
    editor = E(tagged_pdf()).with_validation_options(p.TaggedPdfValidationOptions(p.TaggedPdfLimits(max_objects=1)))
    for operation in (editor.plan, editor.apply):
        with pytest.raises(p.PdfError):
            operation([])
    for data in (b'', b'not a PDF'):
        with pytest.raises(p.PdfError):
            E(data).apply([])
    with pytest.raises(OverflowError):
        M.associate_mcid(ELEMENT, PAGE, -1)
    with pytest.raises(OverflowError):
        M.create_element(ROOT, 'P', index=-1)


@pytest.mark.skipif(shutil.which("qpdf") is None, reason="qpdf independent reader unavailable")
def test_external_qpdf(tmp_path):
    report = E(tagged_pdf()).apply([M.set_element_attribute(ELEMENT, "T", V.string(b"new title"))])
    path = tmp_path / 'edited.pdf'
    path.write_bytes(report.pdf_bytes)
    result = subprocess.run(['qpdf', '--show-object=6,7', str(path)], capture_output=True, check=True)
    assert b'/T (new title)' in result.stdout and b'/Raw <00ff>' in result.stdout


@pytest.mark.parametrize("values", [(b"changed", b"title"), (None, b"title"), (b"changed", None)])
def test_repeated_attribute_mutations_observe_batch_order(values, tmp_path):
    """A later assignment must see the intermediate state (#762)."""
    mutations = [M.set_element_attribute(ELEMENT, "T", None if v is None else V.string(v)) for v in values]
    report = E(tagged_pdf()).apply(mutations)
    expected = None if values[-1] is None else values[-1].decode()
    assert report.validation_after.elements[0].title == expected
    assert E(report.pdf_bytes).preflight().elements[0].title == expected
    if shutil.which("qpdf"):
        path = tmp_path / "batch.pdf"
        path.write_bytes(report.pdf_bytes)
        obj = subprocess.run(["qpdf", "--show-object=6,7", str(path)], check=True, capture_output=True).stdout
        if expected is None:
            assert b"/T " not in obj
        else:
            assert b"/T (title)" in obj


def prepared_fixture(*, missing_indexes=False, language=True, missing_description=False, xref_stream=False, permission=None):
    """Serialize objects/xref independently, including generation 7 and binary xref."""
    import re
    import struct
    source = tagged_pdf(language=language)
    objects = {(int(n), int(g)): body for n, g, body in re.findall(rb'(\d+) (\d+) obj\n(.*?)\nendobj', source, re.S)}
    if missing_indexes:
        objects[3, 0] = objects[3, 0].replace(b'/StructParents 0 ', b'')
        objects[5, 0] = objects[5, 0].replace(b'/ParentTree 7 0 R ', b'')
    if missing_description:
        objects[6, 7] = objects[6, 7].replace(b'/S /CustomP', b'/S /Figure').replace(b'/Alt (alternative) ', b'').replace(b'/ActualText (actual) ', b'')
    if permission is not None:
        objects[1, 0] = objects[1, 0][:-2] + b'/Perms << /DocMDP 8 0 R >> >>'
        objects[8, 0] = (b'<< /Type /Sig /ByteRange [0 0000000000 0000000000 0000000000] /Contents <00> /Reference [<< /TransformMethod /DocMDP /TransformParams << /Type /TransformParams /P ' + str(permission).encode() + b' /V /1.2 >> >>] >>')
    size = len(objects) + 1
    data = bytearray(b'%PDF-1.7\n')
    offsets = {}
    for (number, generation), body in sorted(objects.items()):
        offsets[number] = (len(data), generation)
        data.extend(f'{number} {generation} obj\n'.encode() + body + b'\nendobj\n')
    xref = len(data)
    if xref_stream:
        entries = struct.pack('>BIH', 0, 0, 65535)
        for number in range(1, size):
            entries += struct.pack('>BIH', 1, *offsets[number])
        entries += struct.pack('>BIH', 1, xref, 0)
        data.extend(f'{size} 0 obj\n<< /Type /XRef /Size {size + 1} /Root 1 0 R /W [1 4 2] /Length {len(entries)} >>\nstream\n'.encode() + entries + b'\nendstream\nendobj\n')
    else:
        data.extend(f'xref\n0 {size}\n0000000000 65535 f \n'.encode())
        for number in range(1, size):
            offset, generation = offsets[number]
            data.extend(f'{offset:010} {generation:05} n \n'.encode())
        data.extend(f'trailer\n<< /Size {size} /Root 1 0 R >>\n'.encode())
    data.extend(f'startxref\n{xref}\n%%EOF\n'.encode())
    if permission is not None:
        gap = data.index(b'/Contents <00>') + len(b'/Contents ')
        ranges = f'[0 {gap:010} {gap + 4:010} {len(data) - gap - 4:010}]'.encode()
        data = data.replace(b'[0 0000000000 0000000000 0000000000]', ranges)
    return bytes(data)


@pytest.mark.parametrize('xref_stream', [False, True])
@pytest.mark.parametrize('missing_indexes', [False, True])
@pytest.mark.parametrize('language', [False, True])
def test_recovery_preparation_matrix_and_xref_inventory(xref_stream, missing_indexes, language, tmp_path):
    source = prepared_fixture(missing_indexes=missing_indexes, language=language, xref_stream=xref_stream)
    original = E(source)
    before = p.validate_tagged_pdf(source)
    if missing_indexes:
        assert not before.valid
    recovered = original.with_recovered_indexes()
    preflight = recovered.preflight()
    assert preflight.content_mcids[PAGE] == [0]
    assert preflight.parent_tree[0].value[0].value == (6, 7)
    if not language:
        assert not preflight.valid
        with pytest.raises(p.PdfError):
            recovered.apply([])
        recovered = recovered.with_document_language('es-ES')
    preparation = recovered.preparation_objects()
    if missing_indexes:
        assert PAGE in preparation
    if not language:
        assert R(1, 0) in preparation
    assert len(preparation) == len(set(preparation))
    prepared = recovered.apply([])
    assert prepared.validation_after.valid and prepared.pdf_bytes.startswith(source)
    assert prepared.plan.changed_objects == []
    assert original.apply([]).pdf_bytes == source
    report = recovered.apply([M.set_element_attribute(ELEMENT, 'T', V.string(b'prepared title'))])
    assert report.pdf_bytes.startswith(prepared.pdf_bytes)
    assert report.validation_after.elements[0].title == 'prepared title'
    assert report.validation_after.elements[0].object == ELEMENT
    if xref_stream:
        assert b'/Type /XRef' in report.pdf_bytes[len(source):]
        if missing_indexes or not language:
            assert any(obj.object_number >= 8 for obj in preparation)
    if shutil.which('qpdf'):
        path = tmp_path / 'prepared.pdf'
        path.write_bytes(report.pdf_bytes)
        subprocess.run(['qpdf', '--check', str(path)], check=True, capture_output=True, timeout=30)
        obj = subprocess.run(['qpdf', '--show-object=6,7', str(path)], check=True, capture_output=True, timeout=30).stdout
        assert b'/T (prepared title)' in obj and b'/Raw <00ff>' in obj


def test_preparation_requires_explicit_metadata_and_preserves_existing_descriptions():
    source = prepared_fixture(missing_indexes=True, language=False, missing_description=True)
    editor = E(source).with_recovered_indexes().with_document_language('es')
    assert not editor.preflight().valid
    with pytest.raises(p.PdfError):
        editor.apply([])
    for value in [None, V.string(b' '), V.integer(42)]:
        for operation in [editor.plan, editor.apply]:
            with pytest.raises(p.PdfError):
                operation([M.set_element_attribute(ELEMENT, 'Alt', value)])
    repaired = editor.apply([M.set_element_attribute(ELEMENT, 'Alt', V.string(b'a described figure'))])
    assert repaired.pdf_bytes.startswith(source) and repaired.validation_after.valid
    assert repaired.validation_after.elements[0].alternate_text == 'a described figure'
    existing = E(tagged_pdf()).with_recovered_indexes()
    for operation in [existing.plan, existing.apply]:
        with pytest.raises(p.PdfError, match='overwrite'):
            operation([M.set_element_attribute(ELEMENT, 'Alt', V.string(b'replacement'))])


@pytest.mark.parametrize('permission', [1, 2, 3])
def test_all_preparation_entry_points_enforce_docmdp(permission):
    # Independently serialized policy fixture, not a cryptographic signature.
    source = prepared_fixture(language=False, permission=permission)
    editor = E(source)
    for operation in [editor.preflight, editor.with_recovered_indexes,
                      lambda: editor.with_document_language('es'),
                      lambda: editor.plan([]), lambda: editor.apply([])]:
        with pytest.raises(p.PdfPermissionError, match='DocMDP'):
            operation()


def test_encrypted_source_rejected_by_all_editor_operations():
    doc = p.Document()
    doc.add_page(p.Page.a4())
    doc.encrypt('user', 'owner')
    editor = E(doc.save_to_bytes())
    for operation in [editor.preflight, editor.with_recovered_indexes,
                      lambda: editor.with_document_language('es'),
                      lambda: editor.plan([]), lambda: editor.apply([])]:
        with pytest.raises(p.PdfError):
            operation()


@pytest.mark.parametrize('field', ['max_objects', 'max_depth', 'max_entries', 'max_decoded_content_bytes'])
def test_editor_validation_budgets_reach_plan_apply_and_preflight(field):
    editor = E(tagged_pdf()).with_validation_options(p.TaggedPdfValidationOptions(p.TaggedPdfLimits(**{field: 0})))
    for operation in [editor.preflight, lambda: editor.plan([]), lambda: editor.apply([])]:
        with pytest.raises(p.PdfError, match='(?i)limit|budget|exceed|depth'):
            operation()
