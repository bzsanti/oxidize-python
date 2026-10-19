"""Effective options using independently serialized PDFs and native consumers."""
import sys
import zlib
from pathlib import Path

import pytest
import oxidize_pdf as p


def fixture(tmp_path, *, texts=('ONE', 'TWO'), compressed=False, extra=None, split=False):
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    kids, contents = [], []
    for text in texts:
        page = len(objects) + 1
        kids.append(f'{page} 0 R')
        streams = [] if text is None else [b'BT /F1 12 Tf 30 100 Td (' + text.encode() + b') Tj ET']
        if split and text is not None:
            streams = [b'BT /F1 12 Tf 30 100 Td', b'(' + text.encode() + b') Tj ET']
        contents.append(b'\n'.join(streams))
        refs = ' '.join(f'{page + i + 1} 0 R' for i in range(len(streams)))
        objects.append(f'<< /Type /Page /Parent 2 0 R /Contents [{refs}] >>'.encode())
        for data in streams:
            encoded = zlib.compress(data) if compressed else data
            filter_entry = b' /Filter /FlateDecode' if compressed else b''
            objects.append(b'<< /Length ' + str(len(encoded)).encode() + filter_entry + b' >>\nstream\n' + encoded + b'\nendstream')
    objects[1] = (f'<< /Type /Pages /Kids [{" ".join(kids)}] /Count {len(kids)} '
                  '/MediaBox [10 20 331 476] /Rotate 90 /Resources << /Font << /F1 3 0 R >> >> >>').encode()
    if extra is not None:
        objects.append(extra)
    result, offsets = bytearray(b'%PDF-1.7\n'), []
    for i, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result.extend(f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n')
    xref = len(result)
    result.extend(f'xref\n0 {len(objects)+1}\n'.encode() + b'0000000000 65535 f \n')
    for offset in offsets:
        result.extend(f'{offset:010d} 00000 n \n'.encode())
    result.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
    path = tmp_path / 'options.pdf'
    path.write_bytes(result)
    return str(path), contents, len(objects)


def test_defaults_presets_builders_and_owned_configuration(tmp_path):
    s = p.StreamingOptions()
    assert (s.buffer_size, s.page_cache_size, s.max_content_stream_size, s.progressive_hints, s.memory_limit) == (262144, 3, 10485760, True, 104857600)
    assert (p.StreamingOptions.minimal_memory().buffer_size, p.StreamingOptions.fast_processing().page_cache_size) == (65536, 10)
    changed = s.with_buffer_size(7).with_page_cache_size(0).with_memory_limit(0)
    assert (changed.buffer_size, changed.page_cache_size, changed.memory_limit) == (7, 0, 0)
    assert s.buffer_size == 262144
    m = p.MemoryOptions()
    assert (m.lazy_loading, m.memory_mapping, m.cache_size, m.streaming, m.buffer_size, m.mmap_threshold) == (True, True, 1000, True, 65536, 10485760)
    small, large = p.MemoryOptions.small_file(), p.MemoryOptions.large_file()
    assert (small.lazy_loading, small.cache_size, small.buffer_size, small.mmap_threshold) == (False, 0, 16384, 2 * sys.maxsize + 1)
    assert (large.cache_size, large.buffer_size, large.mmap_threshold) == (5000, 262144, 1048576)
    m2 = m.with_lazy_loading(False).with_memory_mapping(False).with_cache_size(2).with_streaming(False)
    assert (m2.lazy_loading, m2.memory_mapping, m2.cache_size, m2.streaming) == (False, False, 2, False)
    with pytest.raises(AttributeError):
        m.cache_size = 42
    with pytest.raises(AttributeError):
        s.memory_limit = 42
    path, _, _ = fixture(tmp_path)
    with p.LazyDocument.open(path, p.MemoryOptions(buffer_size=0, mmap_threshold=123)) as doc:
        config = doc.configuration()
        assert config.requested.buffer_size == 0 and config.effective.buffer_size == 1
        assert config.requested.mmap_threshold == 123
        assert config.effective.mmap_threshold == 2 * sys.maxsize + 1
        assert not config.effective.memory_mapping and not config.effective.streaming
        assert config.unsupported == [p.UnsupportedMemoryOption.MemoryMapping, p.UnsupportedMemoryOption.Streaming]
        config.unsupported.clear()
        assert len(config.unsupported) == 2
    assert config.requested.cache_size == 1000
    with p.LazyDocument.open(path, m2) as doc:
        assert doc.configuration().unsupported == []


@pytest.mark.parametrize('compressed', [False, True])
@pytest.mark.parametrize('split', [False, True])
def test_decoded_content_limit_boundary_and_retry(tmp_path, compressed, split):
    path, contents, _ = fixture(tmp_path, texts=('LIMIT-' * 100,), compressed=compressed, split=split)
    limit = len(contents[0])
    for budget in [0, limit - 1]:
        with p.StreamingDocument.open(path, p.StreamingOptions(max_content_stream_size=budget)) as doc:
            for _ in range(2):
                with pytest.raises(p.PdfError):
                    doc.next_page()
                assert doc.cached_pages() == doc.memory_usage() == 0
    with p.StreamingDocument.open(path, p.StreamingOptions(max_content_stream_size=limit)) as doc:
        page = doc.next_page()
        assert page.extract_text_streaming() == 'LIMIT-' * 100
        assert (page.number, page.width, page.height, page.media_box()) == (0, 321, 456, [10, 20, 331, 476])
        assert doc.next_page() is None
        assert doc.next_page() is None


@pytest.mark.parametrize('capacity,budget_factor,expected', [(0, 2, 0), (2, 0, 0), (2, 1, 1), (1, 2, 1), (2, 2, 2)])
def test_stream_cache_budgets_eviction_clear_and_retained_pages(tmp_path, capacity, budget_factor, expected):
    path, contents, _ = fixture(tmp_path, compressed=True)
    payload_size = len(contents[0]) + len('ONE')
    options = p.StreamingOptions(buffer_size=0, page_cache_size=capacity, memory_limit=budget_factor * payload_size)
    doc = p.StreamingDocument.open(path, options)
    config = doc.configuration()
    assert config.requested.buffer_size == 0 and config.effective.buffer_size == 1
    assert config.progressive_hints_unsupported and not config.effective.progressive_hints
    first, second = doc.next_page(), doc.next_page()
    assert first.extract_text_streaming() == 'ONE' and second.extract_text_streaming() == 'TWO'
    assert doc.cached_pages() == expected
    assert doc.memory_usage() == expected * payload_size
    doc.clear_cache()
    assert doc.cached_pages() == doc.memory_usage() == 0
    doc.close()
    doc.close()
    Path(path).unlink()  # Windows also verifies the source descriptor is closed.
    assert first.extract_text_streaming() == 'ONE' and config.requested.page_cache_size == capacity
    for action in (doc.next_page, doc.clear_cache, doc.memory_usage, doc.cached_pages, doc.configuration, doc.__enter__):
        with pytest.raises(ValueError, match='closed'):
            action()


def test_stream_budget_one_byte_short_does_not_retain(tmp_path):
    path, contents, _ = fixture(tmp_path, texts=('ONE',))
    with p.StreamingDocument.open(path, p.StreamingOptions(memory_limit=len(contents[0]) + 2, progressive_hints=False)) as doc:
        assert not doc.configuration().progressive_hints_unsupported
        assert doc.next_page().extract_text_streaming() == 'ONE'
        assert doc.cached_pages() == doc.memory_usage() == 0


@pytest.mark.parametrize('capacity', [0, 1, 2])
def test_lazy_cache_loading_eviction_and_clear(tmp_path, capacity):
    path, _, _ = fixture(tmp_path)
    doc = p.LazyDocument.open(path, p.MemoryOptions(cache_size=capacity))
    assert doc.page_count == 2
    first = doc.get_object(1)
    assert first.value['Type'].value == 'Catalog'
    doc.get_object(1)
    assert doc.memory_stats().cache_hits == (1 if capacity else 0)
    doc.get_object(2)
    doc.get_object(1)
    stats = doc.memory_stats()
    assert stats.cached_objects == min(capacity, 2)
    assert stats.cache_hits == {0: 0, 1: 1, 2: 2}[capacity]
    assert stats.cache_misses == {0: 4, 1: 3, 2: 2}[capacity]
    doc.clear_cache()
    assert doc.memory_stats().cached_objects == 0
    doc.get_object(1)
    assert doc.memory_stats().cache_misses == stats.cache_misses + 1
    assert stats.cache_misses == {0: 4, 1: 3, 2: 2}[capacity]  # owned snapshot
    page = doc.get_page(0)
    assert (page.width, page.height, page.rotation) == (456, 321, 90)
    doc.preload_page(0)
    for number, generation in [(0, 0), (1, 1), (999, 0)]:
        with pytest.raises(p.PdfError):
            doc.get_object(number, generation)
    with pytest.raises(p.PdfError):
        doc.get_page(2)
    doc.close()
    Path(path).unlink()
    assert first.value['Type'].value == 'Catalog' and page.width == 456
    assert doc.page_count == 2
    for action in (lambda: doc.get_object(1), lambda: doc.get_page(0), doc.memory_stats, doc.clear_cache, doc.configuration, doc.__enter__):
        with pytest.raises(ValueError, match='closed'):
            action()


def test_lazy_defers_unrelated_invalid_object_while_eager_rejects(tmp_path):
    path, _, number = fixture(tmp_path, extra=b'<< /Broken (unterminated')
    with p.LazyDocument.open(path, p.MemoryOptions(lazy_loading=True)) as doc:
        assert doc.page_count == 2 and doc.get_page(0).width == 456
        with pytest.raises(p.PdfError):
            doc.get_object(number)
    with pytest.raises(p.PdfError):
        p.LazyDocument.open(path, p.MemoryOptions(lazy_loading=False))


@pytest.mark.parametrize('factory,option', [(p.StreamingDocument, p.StreamingOptions), (p.LazyDocument, p.MemoryOptions)])
def test_normalized_buffers_preserve_reads_and_invalid_sizes_fail(tmp_path, factory, option):
    path, _, _ = fixture(tmp_path)
    for size in [0, 1, 17, 65536]:
        with factory.open(path, option(buffer_size=size)) as doc:
            assert doc.configuration().effective.buffer_size == max(size, 1)
            if isinstance(doc, p.LazyDocument):
                assert doc.get_object(3).value['BaseFont'].value == 'Helvetica'
            else:
                assert doc.next_page().extract_text_streaming() == 'ONE'
    with pytest.raises(p.PdfError, match='addressable'):
        factory.open(path, option(buffer_size=2 * sys.maxsize + 1))
    for size in [-1, 2**100]:
        with pytest.raises(OverflowError):
            option(buffer_size=size)
    with pytest.raises(TypeError):
        factory.open(path, p.MemoryOptions() if option is p.StreamingOptions else p.StreamingOptions())


@pytest.mark.parametrize('factory', [p.StreamingDocument, p.LazyDocument])
def test_input_errors_and_context_exception(tmp_path, factory):
    with pytest.raises(p.PdfParseError if factory is p.LazyDocument else p.PdfIoError):
        factory.open(str(tmp_path / 'missing.pdf'))
    bad = tmp_path / 'bad.pdf'
    bad.write_bytes(b'not a PDF')
    with pytest.raises(p.PdfError):
        factory.open(str(bad))
    path, _, _ = fixture(tmp_path)
    doc = factory.open(path)
    with pytest.raises(RuntimeError, match='sentinel'):
        with doc:
            raise RuntimeError('sentinel')
    with pytest.raises(ValueError, match='closed'):
        doc.__enter__()


@pytest.mark.parametrize('factory', [p.StreamingDocument, p.LazyDocument])
def test_encrypted_source_is_not_silently_accepted(tmp_path, factory):
    doc = p.Document()
    page = p.Page.a4()
    page.set_font(p.Font.HELVETICA, 12)
    page.text_at(30, 100, 'LOCKED-SENTINEL')
    doc.add_page(page)
    doc.encrypt('user', 'owner')
    path = tmp_path / 'locked.pdf'
    doc.save(str(path))
    with pytest.raises(p.PdfError):
        factory.open(str(path))


def test_zero_content_budget_accepts_empty_content(tmp_path):
    path, _, _ = fixture(tmp_path, texts=(None,))
    with p.StreamingDocument.open(path, p.StreamingOptions(max_content_stream_size=0, memory_limit=0)) as doc:
        assert doc.next_page().extract_text_streaming() == ''
        assert doc.next_page() is None
        assert doc.memory_usage() == 0


@pytest.mark.parametrize('options', [p.StreamingOptions.minimal_memory(), p.StreamingOptions.fast_processing()])
def test_streaming_presets_consume_real_pages(tmp_path, options):
    path, _, _ = fixture(tmp_path)
    with p.StreamingDocument.open(path, options) as doc:
        assert doc.next_page().extract_text_streaming() == 'ONE'
        assert doc.next_page().extract_text_streaming() == 'TWO'
        assert doc.next_page() is None
