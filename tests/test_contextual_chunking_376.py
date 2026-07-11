"""F2 (#376): contextual chunking — ContextMode / ContextFormat on
HybridChunkConfig and AnalysisPipeline.

Upstream oxidize-pdf 4.0.0 adds opt-in Contextual Retrieval: a deterministic
document + section snippet is prepended to each chunk's ``full_text`` (the
embedding text) while the display ``text`` stays context-free. Default mode is
``Heading`` (byte-identical to prior output).
"""

import pytest
import oxidize_pdf as op
from oxidize_pdf import experimental as spi


def _build_doc() -> bytes:
    doc = op.Document()
    page = op.Page.a4()
    page.set_font(op.Font.HELVETICA, 18.0)
    page.text_at(50.0, 780.0, "Quarterly Overview")
    page.set_font(op.Font.HELVETICA, 12.0)
    for i in range(10):
        page.text_at(
            50.0,
            750.0 - i * 20.0,
            f"Body paragraph {i} contains enough words to build a retrievable chunk.",
        )
    doc.add_page(page)
    return doc.save_to_bytes()


@pytest.fixture
def reader() -> op.PdfReader:
    return op.PdfReader.from_bytes(_build_doc())


class TestContextFormat:
    def test_variants_distinct(self):
        assert op.ContextFormat.Labeled != op.ContextFormat.Prose

    def test_variant_equality(self):
        assert op.ContextFormat.Labeled == op.ContextFormat.Labeled


class TestContextMode:
    def test_constructors_exist(self):
        assert op.ContextMode.none() is not None
        assert op.ContextMode.heading() is not None
        assert op.ContextMode.contextual(op.ContextFormat.Labeled) is not None

    def test_equality_by_variant(self):
        assert op.ContextMode.heading() == op.ContextMode.heading()
        assert op.ContextMode.none() != op.ContextMode.heading()

    def test_contextual_equality_by_format(self):
        assert op.ContextMode.contextual(op.ContextFormat.Labeled) == op.ContextMode.contextual(
            op.ContextFormat.Labeled
        )
        assert op.ContextMode.contextual(op.ContextFormat.Labeled) != op.ContextMode.contextual(
            op.ContextFormat.Prose
        )


class TestHybridChunkConfigContextMode:
    def test_default_is_heading(self):
        assert op.HybridChunkConfig().context_mode == op.ContextMode.heading()

    def test_custom_context_mode_roundtrips(self):
        mode = op.ContextMode.contextual(op.ContextFormat.Prose)
        cfg = op.HybridChunkConfig(context_mode=mode)
        assert cfg.context_mode == mode


class TestContextualChunking:
    def test_contextual_prefixes_full_text_with_source(self, reader):
        source = op.DocumentSource(filename="quarterly.pdf", doc_hash="h1")
        cfg = op.HybridChunkConfig(
            context_mode=op.ContextMode.contextual(op.ContextFormat.Labeled)
        )
        chunks = reader.rag_chunks_with_source_and_config(source, cfg)
        assert chunks
        first = chunks[0]
        # Embedding text carries the source context; display text does not.
        assert "quarterly.pdf" in first.full_text
        assert "quarterly.pdf" not in first.text

    def test_heading_mode_has_no_source_prefix(self, reader):
        source = op.DocumentSource(filename="quarterly.pdf", doc_hash="h1")
        cfg = op.HybridChunkConfig(context_mode=op.ContextMode.heading())
        chunks = reader.rag_chunks_with_source_and_config(source, cfg)
        assert chunks
        assert "quarterly.pdf" not in chunks[0].full_text


class TestAnalysisPipelineContextMode:
    def test_with_context_mode_changes_full_text(self, reader):
        source = op.DocumentSource(filename="pipe.pdf", doc_hash="ph")
        base = spi.AnalysisPipeline().with_source(source)
        ctx = spi.AnalysisPipeline().with_source(source).with_context_mode(
            op.ContextMode.contextual(op.ContextFormat.Labeled)
        )
        base_chunks = reader.rag_chunks_with_pipeline(base)
        ctx_chunks = reader.rag_chunks_with_pipeline(ctx)
        assert base_chunks and ctx_chunks
        assert ctx_chunks[0].full_text != base_chunks[0].full_text
        assert "pipe.pdf" in ctx_chunks[0].full_text
