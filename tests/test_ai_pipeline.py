"""Tests for F59 — AI/ML Pipeline module."""

import pytest
import oxidize_pdf as op


# ── Helpers ────────────────────────────────────────────────────────────────

def _create_sample_pdf() -> bytes:
    """Create a sample PDF with text for AI testing."""
    doc = op.Document()
    page = op.Page.a4()
    page.set_font(op.Font.HELVETICA, 12.0)
    page.text_at(50.0, 750.0, "Chapter 1: Introduction")
    page.text_at(50.0, 720.0, "This is the first paragraph of the document.")
    page.text_at(50.0, 700.0, "It contains important information about the topic.")
    doc.add_page(page)
    page2 = op.Page.a4()
    page2.set_font(op.Font.HELVETICA, 12.0)
    page2.text_at(50.0, 750.0, "Chapter 2: Details")
    page2.text_at(50.0, 720.0, "More detailed information follows here.")
    doc.add_page(page2)
    return doc.save_to_bytes()


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    return _create_sample_pdf()


@pytest.fixture
def sample_reader(sample_pdf_bytes) -> op.PdfReader:
    return op.PdfReader.from_bytes(sample_pdf_bytes)


# ── DocumentChunker ────────────────────────────────────────────────────────

class TestDocumentChunker:
    def test_constructor(self):
        chunker = op.DocumentChunker(512, 50)
        assert chunker is not None

    def test_default(self):
        chunker = op.DocumentChunker.default()
        assert chunker is not None

    def test_chunk_text_returns_list(self):
        chunker = op.DocumentChunker(10, 2)
        chunks = chunker.chunk_text("word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11")
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_chunk_text_returns_document_chunks(self):
        chunker = op.DocumentChunker(10, 2)
        chunks = chunker.chunk_text("hello world foo bar baz")
        assert len(chunks) >= 1
        chunk = chunks[0]
        assert hasattr(chunk, "id")
        assert hasattr(chunk, "content")
        assert hasattr(chunk, "tokens")
        assert hasattr(chunk, "page_numbers")
        assert hasattr(chunk, "chunk_index")

    def test_chunk_text_empty(self):
        chunker = op.DocumentChunker(10, 2)
        chunks = chunker.chunk_text("")
        assert chunks == []

    def test_estimate_tokens(self):
        count = op.DocumentChunker.estimate_tokens("hello world")
        assert count >= 2

    def test_estimate_tokens_empty(self):
        count = op.DocumentChunker.estimate_tokens("")
        assert count == 0

    def test_chunk_index_sequential(self):
        chunker = op.DocumentChunker(5, 1)
        text = " ".join(f"word{i}" for i in range(20))
        chunks = chunker.chunk_text(text)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_chunk_ids_unique(self):
        chunker = op.DocumentChunker(5, 1)
        text = " ".join(f"word{i}" for i in range(20))
        chunks = chunker.chunk_text(text)
        ids = [c.id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_repr(self):
        chunker = op.DocumentChunker(10, 2)
        chunks = chunker.chunk_text("hello world foo bar")
        assert len(chunks) >= 1
        r = repr(chunks[0])
        assert "DocumentChunk" in r


# ── MarkdownExporter ───────────────────────────────────────────────────────

class TestMarkdownExporter:
    def test_constructor_with_options(self):
        opts = op.MarkdownOptions(include_metadata=True, include_page_numbers=False)
        exporter = op.MarkdownExporter(opts)
        assert exporter is not None

    def test_default(self):
        exporter = op.MarkdownExporter.default()
        assert exporter is not None

    def test_export(self):
        exporter = op.MarkdownExporter.default()
        result = exporter.export("Hello world")
        assert isinstance(result, str)
        assert "Hello world" in result

    def test_export_text_staticmethod(self):
        result = op.MarkdownExporter.export_text("Sample text.")
        assert isinstance(result, str)
        assert "Sample text." in result
        assert "# Document" in result

    def test_export_text_empty(self):
        result = op.MarkdownExporter.export_text("")
        assert "# Document" in result

    def test_markdown_options_attributes(self):
        opts = op.MarkdownOptions(include_metadata=True, include_page_numbers=False)
        assert opts.include_metadata is True
        assert opts.include_page_numbers is False

    def test_markdown_options_repr(self):
        opts = op.MarkdownOptions(include_metadata=True, include_page_numbers=True)
        assert "MarkdownOptions" in repr(opts)


# ── ExtractionProfile ──────────────────────────────────────────────────────

class TestExtractionProfile:
    def test_standard(self):
        p = op.ExtractionProfile.STANDARD
        assert "STANDARD" in repr(p)

    def test_academic(self):
        p = op.ExtractionProfile.ACADEMIC
        assert "ACADEMIC" in repr(p)

    def test_form(self):
        p = op.ExtractionProfile.FORM
        assert "FORM" in repr(p)

    def test_government(self):
        p = op.ExtractionProfile.GOVERNMENT
        assert "GOVERNMENT" in repr(p)

    def test_dense(self):
        p = op.ExtractionProfile.DENSE
        assert "DENSE" in repr(p)

    def test_presentation(self):
        p = op.ExtractionProfile.PRESENTATION
        assert "PRESENTATION" in repr(p)

    def test_rag(self):
        p = op.ExtractionProfile.RAG
        assert "RAG" in repr(p)


# ── ReadingOrderStrategy ───────────────────────────────────────────────────

class TestReadingOrderStrategy:
    def test_simple(self):
        s = op.ReadingOrderStrategy.SIMPLE
        assert "SIMPLE" in repr(s)

    def test_none(self):
        s = op.ReadingOrderStrategy.NONE
        assert "NONE" in repr(s)

    def test_xy_cut(self):
        s = op.ReadingOrderStrategy.xy_cut(20.0)
        assert "xy_cut" in repr(s)
        assert "20" in repr(s)


# ── PartitionConfig ────────────────────────────────────────────────────────

class TestPartitionConfig:
    def test_constructor(self):
        cfg = op.PartitionConfig()
        assert cfg is not None

    def test_without_tables(self):
        cfg = op.PartitionConfig().without_tables()
        assert cfg is not None

    def test_without_headers_footers(self):
        cfg = op.PartitionConfig().without_headers_footers()
        assert cfg is not None

    def test_with_reading_order(self):
        cfg = op.PartitionConfig().with_reading_order(op.ReadingOrderStrategy.SIMPLE)
        assert cfg is not None

    def test_with_reading_order_xy_cut(self):
        cfg = op.PartitionConfig().with_reading_order(op.ReadingOrderStrategy.xy_cut(15.0))
        assert cfg is not None

    def test_with_title_min_font_ratio(self):
        cfg = op.PartitionConfig().with_title_min_font_ratio(1.5)
        assert cfg is not None

    def test_with_min_table_confidence(self):
        cfg = op.PartitionConfig().with_min_table_confidence(0.7)
        assert cfg is not None

    def test_repr(self):
        cfg = op.PartitionConfig()
        assert "PartitionConfig" in repr(cfg)

    def test_chaining(self):
        cfg = (
            op.PartitionConfig()
            .without_tables()
            .without_headers_footers()
            .with_title_min_font_ratio(1.4)
        )
        assert cfg is not None


# ── MergePolicy ────────────────────────────────────────────────────────────

class TestMergePolicy:
    def test_same_type_only(self):
        p = op.MergePolicy.SAME_TYPE_ONLY
        assert "SAME_TYPE_ONLY" in repr(p)

    def test_any_inline_content(self):
        p = op.MergePolicy.ANY_INLINE_CONTENT
        assert "ANY_INLINE_CONTENT" in repr(p)


# ── HybridChunkConfig ──────────────────────────────────────────────────────

class TestHybridChunkConfig:
    def test_default_constructor(self):
        cfg = op.HybridChunkConfig()
        assert cfg.max_tokens == 512
        assert cfg.overlap_tokens == 50

    def test_custom_constructor(self):
        cfg = op.HybridChunkConfig(256, 30)
        assert cfg.max_tokens == 256
        assert cfg.overlap_tokens == 30

    def test_repr(self):
        cfg = op.HybridChunkConfig(256, 25)
        assert "HybridChunkConfig" in repr(cfg)


# ── SemanticChunkConfig ────────────────────────────────────────────────────

class TestSemanticChunkConfig:
    def test_constructor(self):
        cfg = op.SemanticChunkConfig(256)
        assert cfg.max_tokens == 256

    def test_with_overlap(self):
        cfg = op.SemanticChunkConfig(512).with_overlap(75)
        assert cfg.overlap_tokens == 75

    def test_repr(self):
        cfg = op.SemanticChunkConfig(512)
        assert "SemanticChunkConfig" in repr(cfg)


# ── PdfReader.to_markdown ──────────────────────────────────────────────────

class TestPdfReaderToMarkdown:
    def test_returns_string(self, sample_reader):
        result = sample_reader.to_markdown()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_document_header(self, sample_reader):
        result = sample_reader.to_markdown()
        # MarkdownExporter produces "# Document" header (deprecated path)
        assert "#" in result or "Document" in result


# ── PdfReader.to_contextual ────────────────────────────────────────────────

class TestPdfReaderToContextual:
    def test_returns_string(self, sample_reader):
        result = sample_reader.to_contextual()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_content_marker(self, sample_reader):
        result = sample_reader.to_contextual()
        assert "content" in result.lower() or "document" in result.lower()


# ── PdfReader.chunk ────────────────────────────────────────────────────────

class TestPdfReaderChunk:
    def test_returns_list(self, sample_reader):
        chunks = sample_reader.chunk(100, 10)
        assert isinstance(chunks, list)

    def test_chunks_have_content(self, sample_reader):
        chunks = sample_reader.chunk(50, 5)
        if len(chunks) > 0:
            chunk = chunks[0]
            assert isinstance(chunk.content, str)
            assert isinstance(chunk.tokens, int)
            assert isinstance(chunk.chunk_index, int)
            assert chunk.chunk_index == 0

    def test_document_chunk_repr(self, sample_reader):
        chunks = sample_reader.chunk(100, 10)
        if len(chunks) > 0:
            r = repr(chunks[0])
            assert "DocumentChunk" in r


# ── PdfReader.partition ────────────────────────────────────────────────────

class TestPdfReaderPartition:
    def test_returns_list(self, sample_reader):
        elements = sample_reader.partition()
        assert isinstance(elements, list)

    def test_elements_have_properties(self, sample_reader):
        elements = sample_reader.partition()
        for element in elements:
            assert hasattr(element, "type_name")
            assert hasattr(element, "text")
            assert hasattr(element, "display_text")
            assert hasattr(element, "page")
            assert isinstance(element.type_name, str)
            assert element.type_name in (
                "title", "paragraph", "table", "header", "footer",
                "list_item", "image", "code_block", "key_value",
            )
            assert isinstance(element.page, int)

    def test_element_repr(self, sample_reader):
        elements = sample_reader.partition()
        if len(elements) > 0:
            r = repr(elements[0])
            assert "Element" in r

    def test_page_numbers_valid(self, sample_reader):
        elements = sample_reader.partition()
        for element in elements:
            assert element.page >= 0


# ── PdfReader.rag_chunks ───────────────────────────────────────────────────

class TestPdfReaderRagChunks:
    def test_returns_list(self, sample_reader):
        chunks = sample_reader.rag_chunks()
        assert isinstance(chunks, list)

    def test_rag_chunks_have_properties(self, sample_reader):
        chunks = sample_reader.rag_chunks()
        for chunk in chunks:
            assert hasattr(chunk, "chunk_index")
            assert hasattr(chunk, "text")
            assert hasattr(chunk, "full_text")
            assert hasattr(chunk, "page_numbers")
            assert hasattr(chunk, "element_types")
            assert hasattr(chunk, "heading_context")
            assert hasattr(chunk, "token_estimate")
            assert hasattr(chunk, "is_oversized")

    def test_chunk_index_sequential(self, sample_reader):
        chunks = sample_reader.rag_chunks()
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_page_numbers_valid(self, sample_reader):
        chunks = sample_reader.rag_chunks()
        for chunk in chunks:
            assert isinstance(chunk.page_numbers, list)
            for p in chunk.page_numbers:
                assert p >= 0

    def test_element_types_strings(self, sample_reader):
        chunks = sample_reader.rag_chunks()
        for chunk in chunks:
            for t in chunk.element_types:
                assert isinstance(t, str)

    def test_token_estimate_positive(self, sample_reader):
        chunks = sample_reader.rag_chunks()
        for chunk in chunks:
            assert chunk.token_estimate >= 0

    def test_rag_chunk_repr(self, sample_reader):
        chunks = sample_reader.rag_chunks()
        if len(chunks) > 0:
            r = repr(chunks[0])
            assert "RagChunk" in r

    def test_text_is_string(self, sample_reader):
        chunks = sample_reader.rag_chunks()
        for chunk in chunks:
            assert isinstance(chunk.text, str)
            assert isinstance(chunk.full_text, str)


# ── PdfReader.rag_chunks_with_profile ─────────────────────────────────────

class TestPdfReaderRagChunksWithProfile:
    def test_standard_profile(self, sample_reader):
        chunks = sample_reader.rag_chunks_with_profile(op.ExtractionProfile.STANDARD)
        assert isinstance(chunks, list)

    def test_rag_profile(self, sample_reader):
        chunks = sample_reader.rag_chunks_with_profile(op.ExtractionProfile.RAG)
        assert isinstance(chunks, list)

    def test_academic_profile(self, sample_reader):
        chunks = sample_reader.rag_chunks_with_profile(op.ExtractionProfile.ACADEMIC)
        assert isinstance(chunks, list)

    def test_chunks_have_correct_types(self, sample_reader):
        chunks = sample_reader.rag_chunks_with_profile(op.ExtractionProfile.STANDARD)
        for chunk in chunks:
            assert hasattr(chunk, "chunk_index")
            assert hasattr(chunk, "text")
            assert hasattr(chunk, "page_numbers")


# ── PyElement properties ───────────────────────────────────────────────────

class TestPyElementProperties:
    def test_type_name_is_valid(self, sample_reader):
        elements = sample_reader.partition()
        valid_types = {
            "title", "paragraph", "table", "header", "footer",
            "list_item", "image", "code_block", "key_value",
        }
        for element in elements:
            assert element.type_name in valid_types

    def test_text_is_string(self, sample_reader):
        elements = sample_reader.partition()
        for element in elements:
            assert isinstance(element.text, str)

    def test_display_text_is_string(self, sample_reader):
        elements = sample_reader.partition()
        for element in elements:
            assert isinstance(element.display_text, str)

    def test_page_is_int(self, sample_reader):
        elements = sample_reader.partition()
        for element in elements:
            assert isinstance(element.page, int)
            assert element.page >= 0


# ── PyRagChunk properties ──────────────────────────────────────────────────

class TestPyRagChunkProperties:
    def test_all_properties_accessible(self, sample_reader):
        chunks = sample_reader.rag_chunks()
        for chunk in chunks:
            _ = chunk.chunk_index
            _ = chunk.text
            _ = chunk.full_text
            _ = chunk.page_numbers
            _ = chunk.element_types
            _ = chunk.heading_context
            _ = chunk.token_estimate
            _ = chunk.is_oversized

    def test_heading_context_optional(self, sample_reader):
        chunks = sample_reader.rag_chunks()
        for chunk in chunks:
            assert chunk.heading_context is None or isinstance(chunk.heading_context, str)

    def test_is_oversized_bool(self, sample_reader):
        chunks = sample_reader.rag_chunks()
        for chunk in chunks:
            assert isinstance(chunk.is_oversized, bool)


# ── PyDocumentChunk properties ─────────────────────────────────────────────

class TestPyDocumentChunkProperties:
    def test_all_properties_accessible(self, sample_reader):
        chunks = sample_reader.chunk(100, 10)
        for chunk in chunks:
            _ = chunk.id
            _ = chunk.content
            _ = chunk.tokens
            _ = chunk.page_numbers
            _ = chunk.chunk_index

    def test_page_numbers_list(self, sample_reader):
        chunks = sample_reader.chunk(100, 10)
        for chunk in chunks:
            assert isinstance(chunk.page_numbers, list)

    def test_content_is_non_empty(self, sample_reader):
        chunks = sample_reader.chunk(50, 5)
        if len(chunks) > 0:
            assert len(chunks[0].content) > 0
