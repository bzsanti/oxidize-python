"""Issue #260: configuration must change real extraction, not just API shape."""
import json

import pytest
import oxidize_pdf as pdf


def document(content: bytes) -> bytes:
    """Independent one-page PDF syntax; all positions and strings are test inputs."""
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 600 800] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>',
        b'<< /Length %d >>\nstream\n' % len(content) + content + b'\nendstream',
    ]
    data = b'%PDF-1.7\n'
    offsets = []
    for i, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data += b'%d 0 obj\n' % i + obj + b'\nendobj\n'
    xref = len(data)
    data += b'xref\n0 7\n0000000000 65535 f \n'
    data += b''.join(b'%010d 00000 n \n' % offset for offset in offsets)
    return data + b'trailer\n<< /Size 7 /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % xref


PROSE = (b'BT /F2 20 Tf 50 700 Td (Section Alpha) Tj ET\n'
         b'BT /F1 10 Tf 50 620 Td (First body sentence.) Tj ET\n'
         b'BT /F1 10 Tf 50 520 Td (Second body sentence.) Tj ET\n')
TABLE = (b'100 100 m 300 100 l S 100 150 m 300 150 l S 100 200 m 300 200 l S\n'
         b'100 100 m 100 200 l S 200 100 m 200 200 l S 300 100 m 300 200 l S\n'
         b'BT /F1 10 Tf 120 170 Td (Name) Tj ET\n'
         b'BT /F1 10 Tf 220 170 Td (Value) Tj ET\n'
         b'BT /F1 10 Tf 120 120 Td (Alpha) Tj ET\n'
         b'BT /F1 10 Tf 220 120 Td (42) Tj ET\n')


def reader(content=PROSE):
    return pdf.PdfReader.from_bytes(document(content))


def test_partition_config_reaches_table_and_header_detection():
    r = reader(TABLE)
    assert any(e.type_name == 'table' for e in r.partition())
    ungrouped = r.partition_with(pdf.PartitionConfig().without_tables())
    assert ungrouped and all(e.type_name != 'table' for e in ungrouped)
    assert all(word in ' '.join(e.text for e in ungrouped) for word in ('Name', 'Value', 'Alpha', '42'))
    r = reader(b'BT /F1 10 Tf 50 780 Td (Running header) Tj ET\n' + PROSE)
    assert any(e.type_name == 'header' and e.text == 'Running header' for e in r.partition())
    without = r.partition_with(pdf.PartitionConfig().without_headers_footers())
    assert all(e.type_name != 'header' for e in without)
    assert any(e.text == 'Running header' for e in without)


def test_partition_options_all_fields_and_immutable_builders():
    config = pdf.PartitionConfig(detect_tables=False, detect_headers_footers=False,
        title_min_font_ratio=2.0, header_zone=0.1, footer_zone=0.2,
        reading_order=pdf.ReadingOrderStrategy.NONE, min_table_confidence=0.8,
        prefer_ruling_tables=False, detect_spatial_tables=False)
    assert (config.detect_tables, config.detect_headers_footers, config.prefer_ruling_tables,
            config.detect_spatial_tables) == (False, False, False, False)
    assert (config.title_min_font_ratio, config.header_zone, config.footer_zone,
            config.min_table_confidence) == (2, 0.1, 0.2, 0.8)
    assert repr(config.reading_order) == repr(pdf.ReadingOrderStrategy.NONE)
    original = pdf.PartitionConfig()
    changed = original.without_tables()
    assert original.detect_tables and not changed.detect_tables


def test_partition_profile_and_title_threshold_change_classification():
    r = reader()
    assert [e.text for e in r.partition_with_profile(pdf.ExtractionProfile.STANDARD)] == [
        'Section Alpha', 'First body sentence.', 'Second body sentence.']
    assert r.partition_with(pdf.PartitionConfig())[0].type_name == 'title'
    assert r.partition_with(pdf.PartitionConfig(title_min_font_ratio=10))[0].type_name != 'title'


def test_element_graph_preserves_relationships_and_rejects_bad_indices():
    elements, graph = reader().partition_graph(pdf.PartitionConfig())
    assert [e.text for e in elements] == ['Section Alpha', 'First body sentence.', 'Second body sentence.']
    assert len(graph) == 3 and not graph.is_empty()
    assert graph.top_level_sections() == [0]
    assert graph.parent_of(0) is None
    assert graph.children_of(0) == graph.elements_in_section(0) == [1, 2]
    assert graph.parent_of(1) == graph.parent_of(2) == 0
    assert [graph.next_of(i) for i in range(3)] == [1, 2, None]
    assert [graph.prev_of(i) for i in range(3)] == [None, 0, 1]
    for method in (graph.parent_of, graph.children_of, graph.next_of, graph.prev_of, graph.elements_in_section):
        with pytest.raises(IndexError):
            method(3)
        with pytest.raises((IndexError, OverflowError)):
            method(-1)
    empty_elements, empty_graph = reader(b'').partition_graph(pdf.PartitionConfig())
    assert empty_elements == [] and len(empty_graph) == 0 and empty_graph.is_empty()
    assert empty_graph.top_level_sections() == []


def test_custom_counter_controls_splits_and_estimates():
    r = reader(b'BT /F1 10 Tf 50 600 Td (Alpha. Bravo. Charlie.) Tj ET')
    config = pdf.HybridChunkConfig(max_tokens=10, overlap_tokens=0)
    assert len(r.rag_chunks_with(config)) == 1
    calls = []
    def counter(text):
        calls.append(text)
        return len(text)
    chunks = r.rag_chunks_with_counter(config, counter)
    assert [c.text for c in chunks] == ['Alpha.', 'Bravo.', 'Charlie.']
    assert [c.token_estimate for c in chunks] == [6, 6, 8]
    assert calls and all(not c.is_oversized for c in chunks)
    assert [c.chunk_index for c in chunks] == [0, 1, 2]
    assert all(c.page_numbers == [0] for c in chunks)


def test_nonadditive_counter_measures_whole_joined_text():
    r = reader(b'BT /F1 10 Tf 50 620 Td (Alpha) Tj ET\nBT /F1 10 Tf 50 520 Td (Bravo) Tj ET')
    # Deliberately non-additive: the join costs more than either fragment.
    def counter(text):
        return 100 if '\n' in text else 1
    chunks = r.rag_chunks_with_counter(pdf.HybridChunkConfig(max_tokens=2), counter)
    assert [c.text for c in chunks] == ['Alpha', 'Bravo']
    assert [c.token_estimate for c in chunks] == [1, 1]


def test_counter_failure_is_preserved_and_reader_can_be_reused():
    r = reader()
    marker = LookupError('counter failed')
    calls = []
    def counter(text):
        calls.append(text)
        raise marker
    with pytest.raises(LookupError) as caught:
        r.rag_chunks_with_counter(pdf.HybridChunkConfig(), counter)
    assert caught.value is marker and len(calls) == 1
    assert r.rag_chunks_with_counter(pdf.HybridChunkConfig(), lambda s: len(s.split()))


@pytest.mark.parametrize('value', [-1, 1.5, 'one', 2**100, True])
def test_counter_rejects_invalid_counts(value):
    with pytest.raises((TypeError, OverflowError, ValueError)):
        reader().rag_chunks_with_counter(pdf.HybridChunkConfig(), lambda _: value)


def test_hybrid_configuration_retains_all_core_fields():
    cfg = pdf.HybridChunkConfig(128, 7, pdf.ContextMode.none(), merge_adjacent=False,
                               propagate_headings=False, merge_policy=pdf.MergePolicy.SAME_TYPE_ONLY)
    assert (cfg.max_tokens, cfg.overlap_tokens, cfg.merge_adjacent, cfg.propagate_headings) == (128, 7, False, False)
    assert cfg.context_mode == pdf.ContextMode.none()
    assert repr(cfg.merge_policy) == repr(pdf.MergePolicy.SAME_TYPE_ONLY)
    chunks = reader().rag_chunks_with(cfg)
    assert [c.text for c in chunks] == ['Section Alpha', 'First body sentence.', 'Second body sentence.']
    assert all(c.heading_context is None and c.full_text == c.text for c in chunks)


def test_document_exports_contain_document_content():
    r = reader()
    markdown = r.to_element_markdown()
    assert '# Section Alpha' in markdown and 'First body sentence.' in markdown
    payload = json.loads(r.to_json())
    assert payload == {'type': 'document', 'page_count': 1, 'pages': [
        {'page_number': 1, 'content': 'Section Alpha\nFirst body sentence.\nSecond body sentence.'}]}


@pytest.mark.parametrize('method,args', [
    ('partition_with', lambda: (pdf.PartitionConfig(),)),
    ('partition_with_profile', lambda: (pdf.ExtractionProfile.STANDARD,)),
    ('partition_graph', lambda: (pdf.PartitionConfig(),)),
    ('rag_chunks_with', lambda: (pdf.HybridChunkConfig(),)),
    ('rag_chunks_with_counter', lambda: (pdf.HybridChunkConfig(), len)),
    ('to_json', lambda: ()), ('to_element_markdown', lambda: ()),
])
def test_new_reader_paths_reject_locked_documents(method, args):
    doc = pdf.Document()
    doc.add_page(pdf.Page.a4())
    doc.encrypt('test-user', 'test-owner')
    r = pdf.PdfReader.from_bytes(doc.save_to_bytes())
    with pytest.raises(pdf.PdfError):
        getattr(r, method)(*args())


def test_nondefault_profile_and_graph_configuration_are_applied():
    content = b'BT /F1 10 Tf 50 750 Td (Profile Header) Tj ET\n' + PROSE
    r = reader(content)
    assert r.partition_with_profile(pdf.ExtractionProfile.STANDARD)[0].type_name == 'paragraph'
    assert r.partition_with_profile(pdf.ExtractionProfile.PRESENTATION)[0].type_name == 'header'
    elements, graph = reader(TABLE).partition_graph(pdf.PartitionConfig(detect_tables=False))
    assert elements and all(e.type_name != 'table' for e in elements)
    assert len(graph) == len(elements)


def test_invalid_counter_on_empty_input_and_reentry():
    with pytest.raises(TypeError, match='callable'):
        reader(b'').rag_chunks_with_counter(pdf.HybridChunkConfig(), None)
    r = reader()
    def reentrant_counter(text):
        r.partition()
        return len(text)
    with pytest.raises(RuntimeError, match='borrow'):
        r.rag_chunks_with_counter(pdf.HybridChunkConfig(), reentrant_counter)
    assert r.partition()[0].text == 'Section Alpha'
