"""Unstable Analysis SPI — extension points for the RAG chunking pipeline.

The contents of this submodule mirror the upstream Rust crate's
``unstable-spi`` surface (``ChunkingStrategy``, ``ElementClassifier``,
``MetadataEnricher``, ``AnalysisPipeline``). The Rust surface is
**exempt from semver while experimental** and may change between releases;
this Python submodule inherits the same instability guarantee.

Typical use::

    import oxidize_pdf as op
    from oxidize_pdf import experimental as spi

    class OnePerElement:
        def chunk(self, elements):
            return [spi.ChunkGroup(elements=[e]) for e in elements]

    reader = op.PdfReader.from_bytes(pdf_bytes)
    chunks = reader.rag_chunks_with_pipeline(
        spi.AnalysisPipeline().with_chunking(OnePerElement())
    )

A custom strategy decides element-to-chunk grouping; the pipeline still owns
``chunk_id``, prev/next links and the full :class:`oxidize_pdf.RagChunk`
metadata. The default pipeline (no overrides) reproduces
:meth:`oxidize_pdf.PdfReader.rag_chunks` exactly.
"""

from __future__ import annotations

from oxidize_pdf._oxidize_pdf import (
    AnalysisPipeline,
    ChunkGroup,
    ClassLabel,
    ClassifyContext,
    EnrichContext,
)

__all__ = [
    "AnalysisPipeline",
    "ChunkGroup",
    "ClassLabel",
    "ClassifyContext",
    "EnrichContext",
]
