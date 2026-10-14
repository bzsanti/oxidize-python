"""Preserve core event payloads without claiming its placeholders are parsed data."""
import pytest
import oxidize_pdf as pdf


def test_stream_payload_and_legacy_fields_survive_drain():
    parser = pdf.IncrementalParser()
    parser.feed(b'%PDF-1.7\n17 0 obj\nstream\nactual payload\nsecond line\nendstream\nendobj\n')
    events = parser.take_events()
    assert [e['type'] for e in events] == ['header', 'object_start', 'stream_data', 'stream_data', 'object_end']
    assert events[0] == {'type': 'header', 'version': '1.7'}
    assert events[1] == {'type': 'object_start', 'id': 17, 'generation': 0}
    assert events[2:4] == [
        {'type': 'stream_data', 'object_id': 17, 'data_len': 14, 'data': b'actual payload'},
        {'type': 'stream_data', 'object_id': 17, 'data_len': 11, 'data': b'second line'},
    ]
    assert events[4]['object'].kind == 'null'
    assert events[4]['object'].value is None
    assert parser.take_events() == []
    parser.feed(b'18 3 obj\nendobj\n')
    assert parser.take_events()[-1]['generation'] == 3
    assert events[2]['data'] == b'actual payload'


def test_chunked_feed_retains_complete_ascii_line():
    parser = pdf.IncrementalParser()
    for chunk in [b'1 0 obj\nstr', b'eam\nactual ', b'payload\nendstream\nendobj\n']:
        parser.feed(chunk)
    assert [e['data'] for e in parser.take_events() if e['type'] == 'stream_data'] == [b'actual payload']


def test_upstream_placeholders_and_loss_are_explicit():
    parser = pdf.IncrementalParser()
    parser.feed(b'1 0 obj\nstream\n  \xff binary  \nendstream\nendobj\nxref\n0 1\n0000000000 65535 f\ntrailer\n<< /Size 1 >>\n%%EOF\n')
    events = parser.take_events()
    assert [e['data'] for e in events if e['type'] == 'stream_data'] == [b'\xef\xbf\xbd binary']
    assert [e['object'].kind for e in events if e['type'] == 'object_end'] == ['null']
    assert not any(e['type'] in ('xref', 'trailer') for e in events)
    assert events[-1] == {'type': 'end_of_file'}
    assert parser.is_complete()


@pytest.mark.parametrize('factory,kind,expected', [
    (lambda: pdf.PdfValue.null(), 'null', None),
    (lambda: pdf.PdfValue.boolean(True), 'boolean', True),
    (lambda: pdf.PdfValue.integer(-(2**63)), 'integer', -(2**63)),
    (lambda: pdf.PdfValue.real(1.25), 'real', 1.25),
    (lambda: pdf.PdfValue.string(b'\x00\xff'), 'string', b'\x00\xff'),
    (lambda: pdf.PdfValue.name('A/B'), 'name', 'A/B'),
    (lambda: pdf.PdfValue.reference(2**32 - 1, 65535), 'reference', (2**32 - 1, 65535)),
])
def test_pdf_value_scalar_inspection(factory, kind, expected):
    value = factory()
    assert value.kind == kind
    assert value.value == expected and type(value.value) is type(expected)
    with pytest.raises(AttributeError):
        value.kind = 'changed'


def test_nested_pdf_values_are_owned_and_inspectable():
    value = pdf.PdfValue.dictionary({'Items': pdf.PdfValue.array([
        pdf.PdfValue.string(b'\x00\xff'), pdf.PdfValue.reference(42, 7)])})
    snapshot = value.value
    assert value.kind == 'dictionary'
    items = snapshot['Items']
    assert items.kind == 'array'
    assert items.value[0].value == b'\x00\xff'
    assert items.value[1].value == (42, 7)
    snapshot.clear()
    assert value.value['Items'].value[0].value == b'\x00\xff'
    stream = pdf.PdfValue.stream({'Length': pdf.PdfValue.integer(2)}, b'\x00\xff')
    assert stream.kind == 'stream'
    dictionary, data = stream.value
    assert dictionary['Length'].value == 2 and data == b'\x00\xff'


def test_invalid_feed_type_does_not_discard_pending_events():
    parser = pdf.IncrementalParser()
    parser.feed(b'%PDF-1.7\n')
    with pytest.raises(TypeError):
        parser.feed('not bytes')
    assert parser.take_events() == [{'type': 'header', 'version': '1.7'}]
