"""Tests for ``oxidize_pdf.experimental.AnalysisPipeline`` + custom ``ChunkingStrategy``.

These guard the Fase 4 surface of the unstable Analysis SPI:

  * ``ChunkGroup`` is constructible from Python and round-trips elements +
    heading_context.
  * A Python class that implements ``chunk(self, elements)`` can be plugged
    into ``AnalysisPipeline.with_chunking(...)`` and its decisions reach the
    final ``RagChunk`` boundaries.
  * The default pipeline (no strategy injected) reproduces ``rag_chunks()``.
  * Errors raised inside the Python strategy surface as PyErr to the caller,
    not as silent empty output.

The submodule lives at ``oxidize_pdf.experimental`` to mark the API as
unstable (matches upstream's ``unstable-spi`` semver-exempt status).
"""

from __future__ import annotations

import pytest
import oxidize_pdf as op
from oxidize_pdf import experimental as spi


# ── Fixture builder ──────────────────────────────────────────────────────


def _build_titled_paragraphs_pdf() -> bytes:
    """One page: title + 4 paragraphs with unique markers."""
    doc = op.Document()
    page = op.Page.a4()
    page.set_font(op.Font.HELVETICA_BOLD, 16.0)
    page.text_at(50.0, 750.0, "Document Title")
    page.set_font(op.Font.HELVETICA, 11.0)
    for i, marker in enumerate(("alpha", "bravo", "charlie", "delta")):
        y = 720.0 - i * 18.0
        page.text_at(50.0, y, f"Paragraph {i} with marker {marker}.")
    doc.add_page(page)
    return doc.save_to_bytes()


# ── ChunkGroup constructor & accessors ───────────────────────────────────


class TestChunkGroup:
    def test_construct_from_elements_and_optional_heading(self):
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        elements = reader.partition()
        assert len(elements) >= 2

        group = spi.ChunkGroup(elements=elements[:2], heading_context="Sect")
        assert group.heading_context == "Sect"
        assert len(group.elements) == 2

    def test_heading_context_defaults_to_none(self):
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        elements = reader.partition()
        group = spi.ChunkGroup(elements=elements[:1])
        assert group.heading_context is None


# ── Default AnalysisPipeline parity with rag_chunks() ────────────────────


class TestAnalysisPipelineDefault:
    def test_default_pipeline_matches_rag_chunks_chunk_ids(self):
        """``AnalysisPipeline()`` with no overrides reproduces ``rag_chunks()``."""
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        baseline = reader.rag_chunks()
        via_pipeline = reader.rag_chunks_with_pipeline(spi.AnalysisPipeline())

        # Same chunk count + identical id sequence + identical text.
        assert len(baseline) == len(via_pipeline)
        for a, b in zip(baseline, via_pipeline):
            assert a.chunk_id == b.chunk_id
            assert a.text == b.text
            assert a.token_estimate == b.token_estimate


# ── Custom strategy: one element per chunk ───────────────────────────────


class TestCustomChunkingStrategy:
    def test_strategy_emitting_one_group_per_element_produces_n_chunks(self):
        """A strategy that emits one group per element produces N chunks."""

        class OnePerElement:
            def chunk(self, elements):
                return [spi.ChunkGroup(elements=[e]) for e in elements]

        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        elements = reader.partition()
        chunks = reader.rag_chunks_with_pipeline(
            spi.AnalysisPipeline().with_chunking(OnePerElement())
        )

        assert len(chunks) == len(elements), (
            f"one-per-element strategy must produce {len(elements)} chunks, "
            f"got {len(chunks)}"
        )

    def test_whole_document_strategy_produces_single_chunk(self):
        """A strategy that emits one group with all elements yields one chunk."""

        class WholeDocument:
            def chunk(self, elements):
                if not elements:
                    return []
                return [spi.ChunkGroup(elements=list(elements))]

        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        chunks = reader.rag_chunks_with_pipeline(
            spi.AnalysisPipeline().with_chunking(WholeDocument())
        )
        assert len(chunks) == 1, f"whole-document strategy must produce 1 chunk, got {len(chunks)}"


# ── Strategy error propagation ───────────────────────────────────────────


class TestStrategyErrorPropagation:
    def test_strategy_raising_exception_surfaces_to_caller(self):
        class Broken:
            def chunk(self, elements):
                raise ValueError("intentional failure inside Python strategy")

        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        pipeline = spi.AnalysisPipeline().with_chunking(Broken())

        with pytest.raises(Exception) as excinfo:
            reader.rag_chunks_with_pipeline(pipeline)
        # The error message should reach the caller (not be swallowed).
        assert "intentional failure" in str(excinfo.value)
