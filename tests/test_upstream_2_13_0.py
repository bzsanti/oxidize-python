"""Tests for upstream oxidize-pdf 2.13.0 features exposed in the bridge.

Covers:
- Per-chunk and document-level language detection (#293).
- Token-efficient chunk serialization round-trip (#291).
- JSON chunk export via the ChunkExporter surface.
- PartitionConfig.prefer_ruling_tables / without_ruling_tables (#292).
"""

import json

import pytest
import oxidize_pdf as op


# Unambiguous, multi-sentence prose so whatlang produces a reliable detection.
ENGLISH = (
    "The quick brown fox jumps over the lazy dog near the river bank. "
    "This document describes the architecture of a distributed software system "
    "in considerable detail, explaining how the individual components communicate "
    "with one another and why each design decision was made the way it was. "
    "Performance, reliability, and maintainability were the guiding principles "
    "throughout the entire engineering process."
)

SPANISH = (
    "El veloz murciélago hindú comía feliz cardillo y kiwi junto al río. "
    "Este documento describe la arquitectura de un sistema de software distribuido "
    "con bastante detalle, explicando cómo se comunican los distintos componentes "
    "entre sí y por qué se tomó cada decisión de diseño de la manera en que se hizo. "
    "El rendimiento, la fiabilidad y la mantenibilidad fueron los principios rectores "
    "durante todo el proceso de ingeniería."
)


# ── Language detection ───────────────────────────────────────────────────────

class TestLanguageDetection:
    def test_language_none_by_default(self):
        chunker = op.DocumentChunker(512, 50)
        chunks = chunker.chunk_text(ENGLISH)
        assert len(chunks) >= 1
        assert all(c.language is None for c in chunks)

    def test_with_language_detection_returns_chunker(self):
        chunker = op.DocumentChunker(512, 50).with_language_detection(True)
        assert chunker is not None
        chunks = chunker.chunk_text(ENGLISH)
        assert len(chunks) >= 1

    def test_detects_english(self):
        chunker = op.DocumentChunker(512, 50).with_language_detection(True)
        chunks = chunker.chunk_text(ENGLISH)
        assert chunks[0].language is not None
        assert chunks[0].language.code == "eng"

    def test_detects_spanish(self):
        chunker = op.DocumentChunker(512, 50).with_language_detection(True)
        chunks = chunker.chunk_text(SPANISH)
        assert chunks[0].language is not None
        assert chunks[0].language.code == "spa"

    def test_detected_language_fields(self):
        chunker = op.DocumentChunker(512, 50).with_language_detection(True)
        lang = chunker.chunk_text(ENGLISH)[0].language
        assert isinstance(lang.code, str)
        assert isinstance(lang.confidence, float)
        assert 0.0 <= lang.confidence <= 1.0
        assert isinstance(lang.reliable, bool)

    def test_detected_language_repr(self):
        chunker = op.DocumentChunker(512, 50).with_language_detection(True)
        lang = chunker.chunk_text(ENGLISH)[0].language
        assert "DetectedLanguage" in repr(lang)
        assert "eng" in repr(lang)

    def test_document_language_english(self):
        chunker = op.DocumentChunker(512, 50).with_language_detection(True)
        chunks = chunker.chunk_text(ENGLISH)
        dominant = op.DocumentChunker.document_language(chunks)
        assert dominant is not None
        assert dominant.code == "eng"

    def test_document_language_none_without_detection(self):
        chunker = op.DocumentChunker(512, 50)
        chunks = chunker.chunk_text(ENGLISH)
        assert op.DocumentChunker.document_language(chunks) is None

    def test_document_language_empty_list(self):
        assert op.DocumentChunker.document_language([]) is None


# ── TokenEfficientExporter ───────────────────────────────────────────────────

class TestTokenEfficientExporter:
    def _chunks(self):
        return op.DocumentChunker(40, 5).chunk_text(ENGLISH)

    def test_export_starts_with_magic_and_header(self):
        out = op.TokenEfficientExporter().export_chunks(self._chunks())
        lines = out.splitlines()
        assert lines[0] == "#oxct/1"
        assert lines[1].startswith("id\ttokens\tchunk_index\t")
        assert "content" in lines[1]

    def test_round_trip_preserves_chunks(self):
        chunks = self._chunks()
        assert len(chunks) >= 2  # ensure multi-row coverage
        serialized = op.TokenEfficientExporter().export_chunks(chunks)
        restored = op.TokenEfficientExporter.parse_chunks(serialized)
        assert len(restored) == len(chunks)
        for original, parsed in zip(chunks, restored):
            assert parsed.content == original.content
            assert parsed.chunk_index == original.chunk_index
            assert parsed.tokens == original.tokens
            assert parsed.page_numbers == original.page_numbers

    def test_parse_chunks_rejects_wrong_magic(self):
        with pytest.raises(Exception):
            op.TokenEfficientExporter.parse_chunks("not-a-valid-header\nfoo")

    def test_repr(self):
        assert "TokenEfficientExporter" in repr(op.TokenEfficientExporter())


# ── JsonExporter (chunks) ────────────────────────────────────────────────────

class TestJsonExporter:
    def _chunks(self):
        return op.DocumentChunker(40, 5).chunk_text(ENGLISH)

    def test_export_chunks_shape(self):
        chunks = self._chunks()
        out = op.JsonExporter.default().export_chunks(chunks)
        doc = json.loads(out)
        assert doc["type"] == "chunked_document"
        assert doc["chunk_count"] == len(chunks)
        assert len(doc["chunks"]) == len(chunks)
        assert doc["chunks"][0]["content"] == chunks[0].content
        assert doc["chunks"][0]["chunk_index"] == chunks[0].chunk_index

    def test_export_text(self):
        out = op.JsonExporter.default().export("Hello world")
        doc = json.loads(out)
        assert doc["type"] == "document"
        assert doc["content"] == "Hello world"

    def test_constructor_options(self):
        exporter = op.JsonExporter(pretty_print=False, include_chunks=False)
        out = exporter.export("compact")
        # pretty_print=False produces single-line JSON (no embedded newline).
        assert "\n" not in out
        assert json.loads(out)["content"] == "compact"


# ── PartitionConfig ruling tables ────────────────────────────────────────────

class TestPartitionConfigRulingTables:
    def test_default_prefers_ruling_tables(self):
        assert op.PartitionConfig().prefer_ruling_tables is True

    def test_without_ruling_tables(self):
        cfg = op.PartitionConfig().without_ruling_tables()
        assert cfg.prefer_ruling_tables is False

    def test_without_ruling_tables_chains(self):
        cfg = (
            op.PartitionConfig()
            .without_tables()
            .without_ruling_tables()
            .with_title_min_font_ratio(1.4)
        )
        assert cfg.prefer_ruling_tables is False

    def test_repr_includes_flag(self):
        assert "prefer_ruling_tables" in repr(op.PartitionConfig())
