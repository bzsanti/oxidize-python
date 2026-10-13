"""Strict public consumer for issue #260; callback/result types must not be Any."""
from oxidize_pdf import (
    ContextMode, Element, ElementGraph, ExtractionProfile, HybridChunkConfig,
    MergePolicy, PartitionConfig, PdfReader, RagChunk, ReadingOrderStrategy,
)


def analyze(reader: PdfReader) -> tuple[list[Element], ElementGraph, list[RagChunk], str, str]:
    config = PartitionConfig(detect_tables=False, header_zone=0.1, footer_zone=0.1,
        detect_headers_footers=False, title_min_font_ratio=1.8,
        reading_order=ReadingOrderStrategy.xy_cut(10), min_table_confidence=0.7,
        prefer_ruling_tables=False, detect_spatial_tables=False)
    elements: list[Element] = reader.partition_with(config)
    profiled: list[Element] = reader.partition_with_profile(ExtractionProfile.PRESENTATION)
    elements, graph = reader.partition_graph(config)
    for section in graph.top_level_sections():
        children: list[int] = graph.elements_in_section(section)
        assert children == graph.children_of(section)
        parent: int | None = graph.parent_of(section)
        following: int | None = graph.next_of(section)
        previous: int | None = graph.prev_of(section)
        assert parent is None or parent >= 0
        assert following is None or following >= 0
        assert previous is None or previous >= 0
    chunks_config = HybridChunkConfig(128, 0, ContextMode.none(), merge_adjacent=False,
                                     propagate_headings=False, merge_policy=MergePolicy.SAME_TYPE_ONLY)
    chunks: list[RagChunk] = reader.rag_chunks_with(chunks_config)
    chunks = reader.rag_chunks_with_counter(chunks_config, lambda text: len(text.encode('utf-8')))
    for chunk in chunks:
        count: int = chunk.token_estimate
        oversized: bool = chunk.is_oversized
        full: str = chunk.full_text
        assert count >= 0 and (full or not oversized)
        for region in chunk.page_regions:
            width: float = region.bbox.width
            assert width >= 0
    assert isinstance(profiled, list)
    return elements, graph, chunks, reader.to_json(), reader.to_element_markdown()
