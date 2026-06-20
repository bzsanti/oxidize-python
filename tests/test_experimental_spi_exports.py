"""Tests for the convenience re-exports and SPI Protocol contracts of
``oxidize_pdf.experimental``.

Two guarantees, both about the *surface* of the unstable Analysis SPI rather
than its runtime behaviour (that is covered by
``test_analysis_pipeline_*.py``):

  * ``Element`` and ``DocumentSource`` — the value types a custom strategy,
    classifier or enricher has to reference — are importable directly from the
    ``experimental`` submodule and are the *same* objects as the ones on the
    package root. A user who stays inside ``from oxidize_pdf import
    experimental as spi`` never has to reach into a second namespace to annotate
    a ``chunk(elements)`` callback or build a ``with_source(...)`` argument.

  * The three SPI contracts (``ChunkingStrategy``, ``ElementClassifier``,
    ``MetadataEnricher``) are exposed as ``runtime_checkable`` Protocols whose
    method names match exactly what the native adapters invoke
    (``chunk`` / ``classify`` / ``enrich``). A class with the right method name
    satisfies the Protocol; a typo'd name does not. This pins the Python-side
    contract to the Rust adapter call sites in ``src/experimental_spi.rs``.
"""

from __future__ import annotations

import oxidize_pdf as op
from oxidize_pdf import experimental as spi


class TestConvenienceReExports:
    def test_element_is_reexported_and_identical_to_root(self):
        assert spi.Element is op.Element

    def test_document_source_is_reexported_and_identical_to_root(self):
        assert spi.DocumentSource is op.DocumentSource

    def test_value_types_listed_in_all(self):
        assert "Element" in spi.__all__
        assert "DocumentSource" in spi.__all__


class TestChunkingStrategyProtocol:
    def test_conforming_class_satisfies_protocol(self):
        class Chunker:
            def chunk(self, elements):
                return []

        assert isinstance(Chunker(), spi.ChunkingStrategy)

    def test_typo_in_method_name_fails_protocol(self):
        class Broken:
            def cahnk(self, elements):  # deliberate typo
                return []

        assert not isinstance(Broken(), spi.ChunkingStrategy)


class TestElementClassifierProtocol:
    def test_conforming_class_satisfies_protocol(self):
        class Classifier:
            def classify(self, element, ctx):
                return None

        assert isinstance(Classifier(), spi.ElementClassifier)

    def test_missing_method_fails_protocol(self):
        class Broken:
            def label(self, element, ctx):
                return None

        assert not isinstance(Broken(), spi.ElementClassifier)


class TestMetadataEnricherProtocol:
    def test_conforming_class_satisfies_protocol(self):
        class Enricher:
            def enrich(self, ctx, extra):
                pass

        assert isinstance(Enricher(), spi.MetadataEnricher)

    def test_missing_method_fails_protocol(self):
        class Broken:
            def enhance(self, ctx, extra):
                pass

        assert not isinstance(Broken(), spi.MetadataEnricher)


class TestProtocolsExported:
    def test_protocols_listed_in_all(self):
        for name in ("ChunkingStrategy", "ElementClassifier", "MetadataEnricher"):
            assert name in spi.__all__
