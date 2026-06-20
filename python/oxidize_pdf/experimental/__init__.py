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

from typing import Any, Protocol, runtime_checkable

from oxidize_pdf._oxidize_pdf import (
    AnalysisPipeline,
    ChunkGroup,
    ClassLabel,
    ClassifyContext,
    DocumentSource,
    Element,
    EnrichContext,
)


@runtime_checkable
class ChunkingStrategy(Protocol):
    """Structural contract for a strategy passed to
    :meth:`AnalysisPipeline.with_chunking`.

    An implementation groups the document's ordered elements into chunks; the
    pipeline still owns ``chunk_id``, prev/next links and the rest of the
    :class:`oxidize_pdf.RagChunk` metadata. Implement it on any class — the
    Protocol is ``runtime_checkable``, so subclassing is optional, but
    annotating ``class MyChunker(ChunkingStrategy)`` lets a type checker catch a
    misnamed or wrong-arity ``chunk`` before it reaches the pipeline.
    """

    def chunk(self, elements: list[Element]) -> list[ChunkGroup]: ...


@runtime_checkable
class ElementClassifier(Protocol):
    """Structural contract for a classifier passed to
    :meth:`AnalysisPipeline.with_classifier`.

    Returns an open :class:`ClassLabel` for the element under ``ctx.index``, or
    ``None`` to leave it unlabelled. Look only at a small constant window of
    ``ctx.elements`` so the classification pass stays O(N).
    """

    def classify(
        self, element: Element, ctx: ClassifyContext
    ) -> ClassLabel | None: ...


@runtime_checkable
class MetadataEnricher(Protocol):
    """Structural contract for an enricher passed to
    :meth:`AnalysisPipeline.with_enricher`.

    Mutates ``extra`` in place to add provider-specific fields to the chunk's
    metadata bag after the pipeline has derived its own metadata.
    """

    def enrich(self, ctx: EnrichContext, extra: dict[str, Any]) -> None: ...


__all__ = [
    "AnalysisPipeline",
    "ChunkGroup",
    "ChunkingStrategy",
    "ClassLabel",
    "ClassifyContext",
    "DocumentSource",
    "Element",
    "ElementClassifier",
    "EnrichContext",
    "MetadataEnricher",
]
