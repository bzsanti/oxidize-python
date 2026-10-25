"""Binary payloads and parsed values from the published incremental parser."""
import pytest
import oxidize_pdf as pdf


def stream_pdf(payload=b"  \xff binary  \nsecond line\n"):
    """Serialize an independent, complete PDF with an exact stream length."""
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] /Contents 4 0 R >>",
               b"<< /Length " + str(len(payload)).encode() + b" >>\nstream\n" + payload + b"\nendstream"]
    data = bytearray(b"%PDF-1.7\n")
    offsets = []
    for number, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(data)
    data.extend(b"xref\n0 5\n0000000000 65535 f \n")
    for offset in offsets:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n" + str(xref).encode() + b"\n%%EOF\n")
    return bytes(data)


def test_stream_payload_and_legacy_fields_survive_drain():
    parser = pdf.IncrementalParser()
    payload = b'actual payload\nsecond line\n'
    parser.feed(stream_pdf(payload))
    events = parser.take_events()
    assert events[0] == {'type': 'header', 'version': '1.7'}
    streams = [e for e in events if e['type'] == 'stream_data']
    assert streams == [{'type': 'stream_data', 'object_id': 4, 'data_len': len(payload), 'data': payload}]
    objects = [e for e in events if e['type'] == 'object_end']
    assert objects[0]['object'].value['Type'].value == 'Catalog'
    assert objects[-1]['object'].kind == 'stream'
    assert parser.take_events() == []
    assert streams[0]['data'] == payload


@pytest.mark.parametrize('chunk_size', [1, 7, 64, 4096])
def test_chunked_feed_retains_binary_stream(chunk_size):
    source = stream_pdf()
    parser = pdf.IncrementalParser()
    for offset in range(0, len(source), chunk_size):
        parser.feed(source[offset:offset + chunk_size])
    events = parser.take_events()
    assert [e['data'] for e in events if e['type'] == 'stream_data'] == [b'  \xff binary  \nsecond line\n']
    assert parser.is_complete()


def test_real_objects_xref_and_trailer_are_emitted():
    parser = pdf.IncrementalParser()
    parser.feed(stream_pdf())
    events = parser.take_events()
    assert [e['object'].kind for e in events if e['type'] == 'object_end'] == ['dictionary', 'dictionary', 'dictionary', 'stream']
    xref, = [e for e in events if e['type'] == 'xref']
    assert xref['entry_count'] == 5
    assert xref['entries'][0] == {'object_number': 0, 'generation': 65535, 'offset': 0, 'in_use': False}
    source = stream_pdf()
    for entry in xref['entries'][1:]:
        assert entry['in_use'] and entry['generation'] == 0
        assert source[entry['offset']:].startswith(f"{entry['object_number']} 0 obj".encode())
    trailer, = [e for e in events if e['type'] == 'trailer']
    assert trailer['dict']['Root'].value == (1, 0)
    assert trailer['dict']['Size'].value == 5
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
