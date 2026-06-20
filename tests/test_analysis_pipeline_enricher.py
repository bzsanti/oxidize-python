"""Tests for the unstable ``MetadataEnricher`` SPI + ``AnalysisPipeline.with_source`` (Fase 6).

These guard:

  * ``RagChunk.extra`` returns the open metadata bag as ``dict[str, Any]``.
  * A Python enricher with ``enrich(self, ctx, extra)`` mutates the extra
    dict in place and the writes survive into the final ``RagChunk.extra``.
  * The ``EnrichContext`` exposes ``text``, ``elements``, ``heading_path``.
  * Multiple enrichers run in registration order; later enrichers see the
    earlier enrichers' writes.
  * ``AnalysisPipeline.with_source(...)`` stamps source-document metadata
    on the resulting chunks (same effect as ``rag_chunks_with_source``).
  * Errors raised inside the Python enricher surface as PyErr.
"""

from __future__ import annotations

import pytest
import oxidize_pdf as op
from oxidize_pdf import experimental as spi


def _build_doc() -> bytes:
    doc = op.Document()
    page = op.Page.a4()
    page.set_font(op.Font.HELVETICA_BOLD, 16.0)
    page.text_at(50.0, 750.0, "Section Title")
    page.set_font(op.Font.HELVETICA, 11.0)
    page.text_at(50.0, 700.0, "Paragraph one carries marker alpha.")
    page.text_at(50.0, 680.0, "Paragraph two carries marker bravo.")
    doc.add_page(page)
    return doc.save_to_bytes()


# ── RagChunk.extra default state ─────────────────────────────────────────


class TestExtraDefault:
    def test_extra_is_empty_dict_when_no_enricher_ran(self):
        reader = op.PdfReader.from_bytes(_build_doc())
        chunks = reader.rag_chunks()
        assert chunks
        for chunk in chunks:
            assert chunk.extra == {}, (
                f"extra should be empty without an enricher, got {chunk.extra!r}"
            )


# ── Single enricher writes to extra ──────────────────────────────────────


class TestSingleEnricher:
    def test_enricher_can_write_strings_to_extra(self):
        class Tagger:
            def enrich(self, ctx, extra):
                extra["provider.tag"] = "value-A"
                extra["provider.count"] = 42

        reader = op.PdfReader.from_bytes(_build_doc())
        pipeline = spi.AnalysisPipeline().with_enricher(Tagger())
        chunks = reader.rag_chunks_with_pipeline(pipeline)
        assert chunks

        for chunk in chunks:
            assert chunk.extra["provider.tag"] == "value-A"
            assert chunk.extra["provider.count"] == 42

    def test_enricher_can_write_nested_structures(self):
        class NestedTagger:
            def enrich(self, ctx, extra):
                extra["provider.meta"] = {"score": 0.75, "tags": ["x", "y"]}

        reader = op.PdfReader.from_bytes(_build_doc())
        pipeline = spi.AnalysisPipeline().with_enricher(NestedTagger())
        chunks = reader.rag_chunks_with_pipeline(pipeline)
        assert chunks

        for chunk in chunks:
            meta = chunk.extra["provider.meta"]
            assert meta["score"] == 0.75
            assert meta["tags"] == ["x", "y"]


# ── EnrichContext shape ──────────────────────────────────────────────────


class TestEnrichContext:
    def test_ctx_exposes_text_elements_and_heading_path(self):
        observed = []

        class Inspector:
            def enrich(self, ctx, extra):
                observed.append({
                    "text": ctx.text,
                    "n_elements": len(ctx.elements),
                    "heading_path": list(ctx.heading_path),
                })

        reader = op.PdfReader.from_bytes(_build_doc())
        pipeline = spi.AnalysisPipeline().with_enricher(Inspector())
        chunks = reader.rag_chunks_with_pipeline(pipeline)
        assert chunks
        assert len(observed) == len(chunks)

        # The text the enricher saw matches the chunk text.
        for chunk, snap in zip(chunks, observed):
            assert snap["text"] == chunk.text
            assert snap["heading_path"] == chunk.heading_path
            assert snap["n_elements"] >= 1


# ── Multiple enrichers compose ───────────────────────────────────────────


class TestEnricherComposition:
    def test_later_enricher_sees_earlier_writes(self):
        class First:
            def enrich(self, ctx, extra):
                extra["stage"] = "first"
                extra["count"] = 1

        class Second:
            def enrich(self, ctx, extra):
                # Read the previous enricher's write.
                assert extra.get("stage") == "first"
                extra["stage"] = "second"
                extra["count"] = extra["count"] + 1

        reader = op.PdfReader.from_bytes(_build_doc())
        pipeline = (
            spi.AnalysisPipeline()
            .with_enricher(First())
            .with_enricher(Second())
        )
        chunks = reader.rag_chunks_with_pipeline(pipeline)
        assert chunks

        for chunk in chunks:
            assert chunk.extra["stage"] == "second"
            assert chunk.extra["count"] == 2


# ── AnalysisPipeline.with_source ─────────────────────────────────────────


class TestPipelineWithSource:
    def test_with_source_stamps_chunks(self):
        reader = op.PdfReader.from_bytes(_build_doc())
        source = op.DocumentSource(filename="pl.pdf", doc_hash="plhash")
        pipeline = spi.AnalysisPipeline().with_source(source)
        chunks = reader.rag_chunks_with_pipeline(pipeline)
        assert chunks

        for chunk in chunks:
            assert chunk.source is not None
            assert chunk.source.filename == "pl.pdf"
            assert chunk.source.doc_hash == "plhash"
            assert chunk.chunk_id.startswith("plhash")


# ── Enricher error propagation ───────────────────────────────────────────


class TestEnricherErrorPropagation:
    def test_enricher_exception_surfaces_to_caller(self):
        class Broken:
            def enrich(self, ctx, extra):
                raise KeyError("enricher exploded as planned")

        reader = op.PdfReader.from_bytes(_build_doc())
        pipeline = spi.AnalysisPipeline().with_enricher(Broken())

        with pytest.raises(Exception) as excinfo:
            reader.rag_chunks_with_pipeline(pipeline)
        assert "enricher exploded" in str(excinfo.value)


# ── Capstone: chunking + classifier + enricher composed ──────────────────


class TestPipelineCapstone:
    def test_strategy_classifier_and_enricher_compose_without_interference(self):
        """All three SPI extensions wired together: chunks are formed by the
        strategy, every element carries the classifier's label, and every
        chunk carries the enricher's writes — with no field clobbered."""

        class TitleVsBodyClassifier:
            def classify(self, element, ctx):
                if element.type_name == "title":
                    return spi.ClassLabel("HEADING")
                return spi.ClassLabel("BODY")

        class OnePerElementStrategy:
            def chunk(self, elements):
                return [spi.ChunkGroup(elements=[e]) for e in elements]

        class LabelEnricher:
            def enrich(self, ctx, extra):
                # Each chunk has exactly one element thanks to the strategy.
                element = ctx.elements[0]
                extra["seen.label"] = element.class_label
                extra["seen.heading_path"] = list(ctx.heading_path)

        reader = op.PdfReader.from_bytes(_build_doc())
        pipeline = (
            spi.AnalysisPipeline()
            .with_classifier(TitleVsBodyClassifier())
            .with_chunking(OnePerElementStrategy())
            .with_enricher(LabelEnricher())
        )
        chunks = reader.rag_chunks_with_pipeline(pipeline)
        assert chunks

        labels = [c.extra["seen.label"] for c in chunks]
        assert "HEADING" in labels
        assert "BODY" in labels

        # The pipeline-derived ChunkMetadata fields (chunk_id chain, etc.) are
        # not clobbered by the enricher's writes.
        for c in chunks:
            assert c.chunk_id
            assert c.extra["seen.heading_path"] == c.heading_path
