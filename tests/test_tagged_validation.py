"""Independent PDF graphs exercise the read-only tagged validator contract."""
import zlib
import pytest
from oxidize_pdf import (
    PdfError, PdfParseError, PdfEncryptionError, Document, Page,
    TaggedPdfLimits, TaggedPdfValidationOptions, TaggedPdfObjectRef,
    TaggedPdfFindingCode as Code, TaggedPdfFindingSeverity as Severity,
    validate_tagged_pdf,
)


def tagged_pdf(*, owner=6, language=True, tagged=True, cycle=False, compressed=False, unassociated=False):
    content = b'/CustomP <</MCID 0>> BDC EMC\n/Artifact <</Subtype /Pagination>> BDC EMC'
    if unassociated:
        content += b'\n/P <</MCID 1>> BDC EMC'
    if compressed:
        content = zlib.compress(content)
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R ' + (b'/StructTreeRoot 5 0 R ' if tagged else b'') + (b'/Lang (en-US)' if language else b'') + b' >>',
        b'<< /Type /Pages /Count 1 /Kids [3 0 R] >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /StructParents 0 /Contents 4 0 R >>',
        b'<< /Length ' + str(len(content)).encode() + (b' /Filter /FlateDecode' if compressed else b'') + b' >>\nstream\n' + content + b'\nendstream',
        b'<< /Type /StructTreeRoot /K [6 7 R] /ParentTree 7 0 R /RoleMap << /CustomP /P >> /ClassMap << /C1 << /O /Layout /Vendor <00ff> >> >> >>',
        b'<< /Type /StructElem /S /CustomP /P 5 0 R /Pg 3 0 R /Lang (es) /Alt (alternative) /ActualText (actual) /T (title) /Vendor << /Raw <00ff> /Flag true >> /K [' + (b'6 7 R' if cycle else b'<< /Type /MCR /Pg 3 0 R /MCID 0 >>') + b'] >>',
        f'<< /Nums [0 [{owner} {7 if owner == 6 else 0} R]] >>'.encode(),
    ]
    result = bytearray(b'%PDF-1.7\n')
    offsets = []
    for number, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result.extend(f'{number} {7 if number == 6 else 0} obj\n'.encode() + obj + b'\nendobj\n')
    xref = len(result)
    result.extend(b'xref\n0 8\n0000000000 65535 f \n')
    for number, offset in enumerate(offsets, 1):
        result.extend(f'{offset:010} {7 if number == 6 else 0:05} n \n'.encode())
    result.extend(f'trailer\n<< /Size 8 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
    return bytes(result)


def test_complete_report_and_lossless_values():
    source = tagged_pdf()
    report = validate_tagged_pdf(source)
    assert report.tagged and report.valid
    assert report.findings == []
    assert report.structure_tree_root == TaggedPdfObjectRef(5, 0)
    assert report.role_map == {'CustomP': 'P'}
    assert report.class_names == ['C1']
    assert report.class_map['C1'].value['Vendor'].value == b'\x00\xff'
    assert report.parent_tree_entries == 1
    assert report.parent_tree[0].value[0].value == (6, 7)
    assert report.content_mcids == {TaggedPdfObjectRef(3, 0): [0]}
    element, = report.elements
    assert (element.object.object_number, element.object.generation) == (6, 7)
    assert element.parent == TaggedPdfObjectRef(5, 0)
    assert (element.structure_type, element.language, element.alternate_text, element.actual_text, element.title) == ('CustomP', 'es', 'alternative', 'actual', 'title')
    assert (element.child_count, element.marked_content_count) == (1, 1)
    assert set(element.dictionary_keys) == set(element.dictionary)
    assert element.dictionary['Vendor'].value['Raw'].value == b'\x00\xff'
    assert element.dictionary['Vendor'].value['Flag'].value is True
    artifact, = report.artifacts
    assert artifact.context == TaggedPdfObjectRef(3, 0)
    assert artifact.operation_index == 2
    assert artifact.subtype == 'Pagination'
    assert source == tagged_pdf()


def test_defaults_and_owned_snapshots():
    limits = TaggedPdfLimits()
    assert (limits.max_objects, limits.max_depth, limits.max_entries, limits.max_decoded_content_bytes) == (100000, 256, 1000000, 268435456)
    options = TaggedPdfValidationOptions(limits)
    assert options.limits.max_depth == 256
    report = validate_tagged_pdf(tagged_pdf(), options)
    report.elements.clear()
    report.role_map.clear()
    report.parent_tree.clear()
    report.class_map.clear()
    report.content_mcids.clear()
    report.elements[0].dictionary.clear()
    assert len(report.elements) == 1
    assert report.role_map == {'CustomP': 'P'}
    assert report.parent_tree[0].value[0].value == (6, 7)
    assert report.class_map['C1'].kind == 'dictionary'
    assert report.content_mcids[TaggedPdfObjectRef(3, 0)] == [0]
    assert 'Vendor' in report.elements[0].dictionary
    for obj, field in [(limits, 'max_depth'), (options, 'limits'), (report, 'valid'), (report.elements[0], 'title'), (TaggedPdfObjectRef(1, 0), 'generation')]:
        with pytest.raises(AttributeError):
            setattr(obj, field, None)


@pytest.mark.parametrize('field', ['max_objects', 'max_depth', 'max_entries', 'max_decoded_content_bytes'])
def test_each_budget_is_effective(field):
    options = TaggedPdfValidationOptions(TaggedPdfLimits(**{field: 0}))
    with pytest.raises(PdfError, match='(?i)limit|budget|exceed|depth'):
        validate_tagged_pdf(tagged_pdf(), options)
    assert validate_tagged_pdf(tagged_pdf()).valid


def test_findings_are_typed_and_warnings_do_not_certify():
    report = validate_tagged_pdf(tagged_pdf(owner=5))
    assert report.tagged and not report.valid
    finding = next(f for f in report.findings if f.code == Code.ParentTreeOwnerMismatch)
    assert finding.severity == Severity.Error
    assert finding.path and finding.message
    assert finding.object is not None
    warning = validate_tagged_pdf(tagged_pdf(language=False))
    assert not warning.valid
    assert any(f.code == Code.MissingDocumentLanguage and f.severity == Severity.Error for f in warning.findings)
    absent = validate_tagged_pdf(tagged_pdf(tagged=False))
    assert not absent.tagged and absent.valid
    assert any(f.code == Code.MissingStructureTree for f in absent.findings)
    assert absent.structure_tree_root is None
    assert absent.findings[0].severity == Severity.Warning


def test_cycles_terminate_with_findings():
    report = validate_tagged_pdf(tagged_pdf(cycle=True))
    assert not report.valid
    assert any(f.code == Code.StructureCycle for f in report.findings)


@pytest.mark.parametrize('data', [b'', b'not a PDF', b'%PDF-1.7\n'])
def test_malformed_input_is_an_error(data):
    with pytest.raises(PdfParseError):
        validate_tagged_pdf(data)


@pytest.mark.parametrize('field', ['max_objects', 'max_depth', 'max_entries', 'max_decoded_content_bytes'])
def test_unsigned_limit_boundaries(field):
    with pytest.raises(OverflowError):
        TaggedPdfLimits(**{field: -1})
    with pytest.raises(OverflowError):
        TaggedPdfLimits(**{field: 1 << 100})


def test_reference_hash_and_generation_boundaries():
    assert hash(TaggedPdfObjectRef(6, 7)) == hash(TaggedPdfObjectRef(6, 7))
    assert TaggedPdfObjectRef(6, 7) != TaggedPdfObjectRef(6, 0)
    for number, generation in [(-1, 0), (1 << 32, 0), (1, -1), (1, 65536)]:
        with pytest.raises(OverflowError):
            TaggedPdfObjectRef(number, generation)


def test_locked_document_is_rejected():
    document = Document()
    document.add_page(Page.a4())
    document.encrypt("test-user", "test-owner")
    with pytest.raises(PdfEncryptionError, match="unlocked"):
        validate_tagged_pdf(document.save_to_bytes())


@pytest.mark.parametrize('compressed', [False, True])
def test_decoded_byte_limit_boundary(compressed):
    source = tagged_pdf(compressed=compressed)
    length = len(b'/CustomP <</MCID 0>> BDC EMC\n/Artifact <</Subtype /Pagination>> BDC EMC')
    options = TaggedPdfValidationOptions(TaggedPdfLimits(max_decoded_content_bytes=length))
    assert validate_tagged_pdf(source, options).valid
    short = TaggedPdfValidationOptions(TaggedPdfLimits(max_decoded_content_bytes=length - 1))
    with pytest.raises(PdfError, match='decoded content bytes'):
        validate_tagged_pdf(source, short)
