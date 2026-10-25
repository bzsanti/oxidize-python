"""Real PDF contracts for #254/#255; fixture syntax is independent of the writer."""
import zlib

import pytest
import oxidize_pdf as pdf


def pdf_bytes(texts, *, box=(0, 0, 321, 456), rotation=0, compressed=False, broken_page=None):
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    kids = []
    for index, text in enumerate(texts):
        page_id = len(objects) + 1
        kids.append(f'{page_id} 0 R')
        objects.append((f'<< /Type /Page /Parent 2 0 R /Contents {page_id + 1} 0 R >>').encode())
        content = b'BT /F1 12 Tf 30 100 Td (' + text.encode('ascii') + b') Tj ET'
        if compressed:
            content = zlib.compress(content)
            if index == broken_page:
                content = b'NOT A ZLIB STREAM'
        filter_entry = b' /Filter /FlateDecode' if compressed else b''
        objects.append(b'<< /Length %d' % len(content) + filter_entry + b' >>\nstream\n' + content + b'\nendstream')
    objects[1] = (f'<< /Type /Pages /Count {len(texts)} /Kids [{" ".join(kids)}] '
                  f'/MediaBox [{" ".join(map(str, box))}] /Rotate {rotation} '
                  '/Resources << /Font << /F1 3 0 R >> >> >>').encode()
    result = b'%PDF-1.7\n'
    offsets = []
    for number, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result += f'{number} 0 obj\n'.encode() + obj + b'\nendobj\n'
    xref = len(result)
    result += f'xref\n0 {len(objects) + 1}\n'.encode() + b'0000000000 65535 f \n'
    result += b''.join(b'%010d 00000 n \n' % offset for offset in offsets)
    return result + f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()


def write_pdf(tmp_path, texts, **options):
    path = tmp_path / 'input.pdf'
    path.write_bytes(pdf_bytes(texts, **options))
    return str(path)


@pytest.mark.parametrize('compressed', [False, True])
def test_exact_single_page_and_eof(tmp_path, compressed):
    path = write_pdf(tmp_path, ['REAL-PARITY-SENTINEL'], compressed=compressed)
    reader = pdf.PdfReader.open(path)
    with pdf.PageStreamer.open(path) as stream:
        assert stream.total_pages() == reader.page_count == 1
        page = stream.next()
        assert page is not None
        assert (page.number, page.width, page.height) == (0, 321, 456)
        assert page.media_box() == [0, 0, 321, 456]
        assert page.extract_text_streaming() == reader.extract_text_from_page(0) == 'REAL-PARITY-SENTINEL'
        assert stream.next() is None
        assert stream.next() is None
    assert page.extract_text_streaming() == 'REAL-PARITY-SENTINEL'


@pytest.mark.parametrize('count', [0, 1, 2, 5])
def test_exact_iteration_and_retained_pages(tmp_path, count):
    texts = [f'SENTINEL-{i}' for i in range(count)]
    with pdf.PageStreamer.open(write_pdf(tmp_path, texts)) as stream:
        pages = [stream.next() for _ in range(count)]
        assert all(page is not None for page in pages)
        assert stream.total_pages() == count
        assert stream.next() is None
    assert [page.number for page in pages] == list(range(count))
    assert [page.extract_text_streaming() for page in pages] == texts


def test_inherited_box_rotation_and_seek(tmp_path):
    path = write_pdf(tmp_path, ['Alpha', 'Bravo', 'Charlie'], box=(10, 20, 331, 476), rotation=90)
    with pdf.PageStreamer.open(path) as stream:
        stream.seek_to_page(2)
        page = stream.next()
        assert page is not None
        assert (page.number, page.width, page.height) == (2, 456, 321)
        assert page.media_box() == [10, 20, 331, 476]
        assert page.extract_text_streaming() == 'Charlie'
        assert stream.next() is None
        stream.seek_to_page(0)
        assert stream.next().extract_text_streaming() == 'Alpha'
        with pytest.raises(IndexError):
            stream.seek_to_page(4)
        assert stream.next().extract_text_streaming() == 'Bravo'
        stream.seek_to_page(3)
        assert stream.next() is None


@pytest.mark.parametrize('data', [b'', b'This is not a PDF', b'%PDF-1.7\n'])
def test_invalid_input_is_rejected(tmp_path, data):
    path = tmp_path / 'invalid.pdf'
    path.write_bytes(data)
    with pytest.raises(pdf.PdfParseError):
        pdf.PageStreamer.open(str(path))


def test_missing_file_is_io_error(tmp_path):
    with pytest.raises(pdf.PdfIoError):
        pdf.PageStreamer.open(str(tmp_path / 'missing.pdf'))


def test_locked_document_is_rejected(tmp_path):
    document = pdf.Document()
    document.add_page(pdf.Page.a4())
    document.encrypt('user', 'owner')
    path = tmp_path / 'locked.pdf'
    document.save(str(path))
    with pytest.raises(pdf.PdfEncryptionError):
        pdf.PageStreamer.open(str(path))


def test_close_releases_file_and_preserves_page(tmp_path):
    path = write_pdf(tmp_path, ['Kept'])
    stream = pdf.PageStreamer.open(path)
    page = stream.next()
    assert page is not None
    stream.close()
    stream.close()
    for action in (stream.next, lambda: stream.seek_to_page(0), stream.__enter__):
        with pytest.raises(ValueError, match='closed'):
            action()
    assert stream.total_pages() == 1
    from pathlib import Path
    Path(path).unlink()  # Also exercises descriptor closure on Windows CI.
    assert page.extract_text_streaming() == 'Kept'


def test_context_manager_closes_after_exception(tmp_path):
    stream = pdf.PageStreamer.open(write_pdf(tmp_path, ['Kept']))
    with pytest.raises(LookupError):
        with stream:
            raise LookupError('caller failure')
    with pytest.raises(ValueError, match='closed'):
        stream.next()


def test_only_selected_page_is_decoded_and_failure_does_not_advance(tmp_path):
    path = write_pdf(tmp_path, ['First', 'Broken', 'Last'], compressed=True, broken_page=1)
    with pdf.PageStreamer.open(path) as stream:
        assert stream.next().extract_text_streaming() == 'First'
        for _ in range(2):
            with pytest.raises(pdf.PdfParseError):
                stream.next()
        stream.seek_to_page(2)
        assert stream.next().extract_text_streaming() == 'Last'
        assert stream.next() is None
