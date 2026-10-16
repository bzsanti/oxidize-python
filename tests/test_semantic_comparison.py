"""Independent PDF serialization tests the semantic comparator, not its writer."""
import re
import shutil
import subprocess
import zlib
import pytest
import oxidize_pdf as p

C = p.SemanticDifferenceClass
K = p.RevisionObjectChangeKind


def fixture(*, text=b'Hello', title=b'Title', compressed=False, shift=0, orphan=None, language=b'en', creation=b'20260101000000Z'):
    content = b'BT /F1 12 Tf 20 80 Td (' + text + b') Tj ET'
    if compressed:
        content = zlib.compress(content)
    def ref(n):
        return f'{n + shift} 0 R'.encode()
    objects = [
        b'<< /Type /Catalog /Pages ' + ref(2) + b' /Lang (' + language + b') >>',
        b'<< /Type /Pages /Count 1 /Kids [' + ref(3) + b'] >>',
        b'<< /Type /Page /Parent ' + ref(2) + b' /MediaBox [0 0 200 100] /Resources << /Font << /F1 ' + ref(5) + b' >> >> /Contents ' + ref(4) + b' >>',
        b'<< /Length ' + str(len(content)).encode() + (b' /Filter /FlateDecode' if compressed else b'') + b' >>\nstream\n' + content + b'\nendstream',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
        b'<< /Title (' + title + b') /CreationDate (D:' + creation + b') >>',
    ]
    if orphan is not None:
        objects.append(b'(' + orphan + b')')
    data = bytearray(b'%PDF-1.7\n')
    offsets = []
    for i, value in enumerate(objects, 1):
        offsets.append(len(data))
        data += f'{i + shift} 0 obj\n'.encode() + value + b'\nendobj\n'
    xref = len(data)
    size = len(objects) + shift + 1
    data += f'xref\n0 {size}\n0000000000 65535 f \n'.encode()
    data += b'0000000000 00000 f \n' * shift
    for offset in offsets:
        data += f'{offset:010} 00000 n \n'.encode()
    data += b'trailer\n<< /Size ' + str(size).encode() + b' /Root ' + ref(1) + b' /Info ' + ref(6) + b' >>\nstartxref\n' + str(xref).encode() + b'\n%%EOF\n'
    return bytes(data)


def revision(source, number, value, *, generation=0, free=False):
    previous = int(re.findall(rb'startxref\s+(\d+)', source)[-1])
    data = bytearray(source)
    offset = len(data)
    if not free:
        data += f'{number} {generation} obj\n'.encode() + value + b'\nendobj\n'
    xref = len(data)
    data += f'xref\n{number} 1\n'.encode()
    data += (f'0000000000 {generation:05} f \n' if free else f'{offset:010} {generation:05} n \n').encode()
    data += f'trailer\n<< /Size {max(8, number + 1)} /Root 1 0 R /Info 6 0 R /Prev {previous} >>\nstartxref\n{xref}\n%%EOF\n'.encode()
    return bytes(data)


def test_identical_complete_owned_result():
    source = fixture()
    result = p.compare_pdfs_semantically(source, source)
    assert result.semantically_equal and result.differences == []
    assert result.left_unreachable_objects == result.right_unreachable_objects == []
    assert ((1, 0), (1, 0)) in result.semantically_equivalent_objects
    first, = result.left_revisions
    assert first.index == 0 and source[first.xref_offset:].startswith(b'xref')
    assert len(first.semantic_fingerprint) == 32 and isinstance(first.semantic_fingerprint, bytes)
    assert sorted((v.object_number, v.generation) for v in first.object_changes) == [(i, 0) for i in range(1, 7)]
    assert all(v.kind == K.Added for v in first.object_changes)
    assert first.semantic_fingerprint == result.right_revisions[0].semantic_fingerprint
    result.left_revisions.clear()
    first.object_changes.clear()
    result.semantically_equivalent_objects.clear()
    assert len(result.left_revisions) == 1 and len(result.left_revisions[0].object_changes) == 6
    assert result.semantically_equivalent_objects
    with pytest.raises(AttributeError):
        result.semantically_equal = False


@pytest.mark.parametrize('options', [dict(compressed=True), dict(shift=10), dict(creation=b'20260202000000Z')])
def test_normalized_serialization(options):
    result = p.compare_pdfs_semantically(fixture(), fixture(**options))
    assert result.semantically_equal
    assert [(v.path, v.class_) for v in result.differences] == [('/Serialization', C.SerializationOnly)]
    assert result.differences[0].description
    if 'shift' in options:
        assert ((1, 0), (11, 0)) in result.semantically_equivalent_objects


@pytest.mark.parametrize('options,expected', [
    (dict(text=b'Changed'), C.Textual),
    (dict(title=b'Other'), C.Metadata),
    (dict(language=b'es'), C.Structural),
    (dict(text=b'Changed'), C.Visual),
])
def test_changed_domains(options, expected):
    result = p.compare_pdfs_semantically(fixture(), fixture(**options))
    assert not result.semantically_equal
    assert expected in [v.class_ for v in result.differences]
    assert [v.path for v in result.differences] == sorted(v.path for v in result.differences)


def test_history_detects_restored_metadata():
    original = fixture()
    changed = revision(original, 6, b'<< /Title (Changed) >>')
    restored = revision(changed, 6, b'<< /Title (Title) >>')
    result = p.compare_pdfs_semantically(original, restored)
    assert not result.semantically_equal
    assert any(v.path == '/Revisions' and v.class_ == C.Structural for v in result.differences)
    assert not any(v.path == '/Trailer/Info' for v in result.differences)
    assert [v.index for v in result.right_revisions] == [0, 1, 2]
    assert [v.xref_offset for v in result.right_revisions] == [int(x) for x in re.findall(rb'startxref\s+(\d+)', restored)]
    for history in result.right_revisions[1:]:
        item, = history.object_changes
        assert (item.object_number, item.generation, item.kind) == (6, 0, K.Replaced)
    assert result.right_revisions[0].semantic_fingerprint == result.right_revisions[2].semantic_fingerprint
    assert result.right_revisions[0].semantic_fingerprint != result.right_revisions[1].semantic_fingerprint


def test_unreachable_generations_and_freed_objects():
    source = fixture()
    added = revision(source, 7, b'(orphan)', generation=4)
    result = p.compare_pdfs_semantically(source, added)
    assert not result.semantically_equal and result.right_unreachable_objects == [(7, 4)]
    item, = result.right_revisions[-1].object_changes
    assert (item.object_number, item.generation, item.kind) == (7, 4, K.Added)
    freed = revision(added, 7, b'', generation=5, free=True)
    result = p.compare_pdfs_semantically(source, freed)
    assert result.right_unreachable_objects == []
    item, = result.right_revisions[-1].object_changes
    assert (item.object_number, item.generation, item.kind) == (7, 5, K.Freed)
    assert not result.semantically_equal  # Historical orphan remains observable.


LIMITS = ['max_objects', 'max_depth', 'max_decoded_stream_bytes', 'max_canonical_bytes',
          'max_extracted_text_bytes', 'max_unreachable_objects', 'max_revisions']


@pytest.mark.parametrize('field', LIMITS)
def test_each_limit_is_enforced(field):
    source = fixture(orphan=b'unreachable')
    options = p.SemanticComparisonOptions(p.SemanticComparisonLimits(**{field: 0}))
    assert getattr(options.limits, field) == 0
    with pytest.raises(p.PdfError, match='limit|budget'):
        p.compare_pdfs_semantically(source, source, options)
    assert p.compare_pdfs_semantically(source, source).semantically_equal


@pytest.mark.parametrize('side', ['left', 'right'])
def test_operand_errors(side):
    values = dict(left=fixture(), right=fixture())
    values[side] = b'not a PDF'
    with pytest.raises(p.PdfParseError):
        p.compare_pdfs_semantically(**values)
    document = p.Document()
    document.add_page(p.Page.a4())
    document.encrypt('test-user', 'test-owner')
    values[side] = document.save_to_bytes()
    with pytest.raises(p.PdfPermissionError, match='decrypted'):
        p.compare_pdfs_semantically(**values)


def test_defaults_and_unsigned_boundaries():
    limits = p.SemanticComparisonOptions().limits
    assert [getattr(limits, name) for name in LIMITS] == [100000, 256, 268435456, 268435456, 67108864, 10000, 1024]
    for name in LIMITS:
        with pytest.raises(OverflowError):
            p.SemanticComparisonLimits(**{name: -1})


@pytest.mark.skipif(not all(shutil.which(t) for t in ('qpdf', 'pdftotext')), reason='independent PDF tools unavailable')
def test_independent_readers_and_xref_stream(tmp_path):
    original = tmp_path / 'original.pdf'
    transformed = tmp_path / 'xref-stream.pdf'
    changed = tmp_path / 'changed.pdf'
    original.write_bytes(fixture())
    changed.write_bytes(fixture(text=b'Changed'))
    subprocess.run(['qpdf', '--object-streams=generate', str(original), str(transformed)], check=True, capture_output=True)
    equal = p.compare_pdfs_semantically(original.read_bytes(), transformed.read_bytes())
    # Core includes physical ObjStm/XRef containers in unreachable-object semantics.
    # Preserve this conservative result; do not claim layout-independent equality.
    assert not equal.semantically_equal
    assert [(d.path, d.class_) for d in equal.differences] == [('/Revisions', C.Structural), ('/UnreachableObjects', C.Structural)]
    assert equal.right_unreachable_objects
    texts = [subprocess.run(['pdftotext', str(path), '-'], check=True, capture_output=True).stdout for path in (original, transformed, changed)]
    assert texts[0] == texts[1] and texts[0] != texts[2]
    different = p.compare_pdfs_semantically(original.read_bytes(), changed.read_bytes())
    assert any(d.class_ == C.Textual for d in different.differences)


def test_right_operand_uses_its_own_limits():
    options = p.SemanticComparisonOptions(p.SemanticComparisonLimits(max_unreachable_objects=0))
    with pytest.raises(p.PdfError, match='unreachable objects limit'):
        p.compare_pdfs_semantically(fixture(), fixture(orphan=b'extra'), options)
    assert p.compare_pdfs_semantically(fixture(), fixture(), options).semantically_equal


def test_security_difference_for_docmdp_policy():
    from pathlib import Path
    source = (Path(__file__).parent / 'fixtures/signatures/docmdp_p2_rsa.pdf').read_bytes()
    assert b'/P 2' in source
    # Permission interpretation only, not authenticity of the altered signature.
    changed = source.replace(b'/P 2', b'/P 3', 1)
    result = p.compare_pdfs_semantically(source, changed)
    assert not result.semantically_equal
    assert any(d.class_ == C.Security for d in result.differences)


@pytest.mark.parametrize('compressed', [False, True])
def test_decoded_budget_counts_traversal(compressed):
    source = fixture(compressed=compressed)
    # Core charges repeated semantic traversals, not just unique stream sizes.
    length = len(b'BT /F1 12 Tf 20 80 Td (Hello) Tj ET')
    generous = p.SemanticComparisonOptions(p.SemanticComparisonLimits(max_decoded_stream_bytes=4096))
    short = p.SemanticComparisonOptions(p.SemanticComparisonLimits(max_decoded_stream_bytes=length))
    assert p.compare_pdfs_semantically(source, source, generous).semantically_equal
    with pytest.raises(p.PdfError, match='decoded stream bytes limit'):
        p.compare_pdfs_semantically(source, source, short)
