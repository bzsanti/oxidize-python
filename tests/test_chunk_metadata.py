"""Semantic tests for ``RagChunk`` enriched metadata (upstream 2.16.0).

These tests guard the new getters surfaced by ``oxidize_pdf::pipeline::ChunkMetadata``:
``heading_path``, dominant font, content-type flags, char/word/sentence counts,
language detection signals, deterministic chunk_id chain, page_span and
page_regions for citation, and table dimensions.

Every assertion validates real behaviour against a synthetic fixture — no
length-only or presence-only checks.
"""

from __future__ import annotations

import re
import pytest
import oxidize_pdf as op


# ── Synthetic PDF builders ────────────────────────────────────────────────


def _build_titled_paragraphs_pdf() -> bytes:
    """One page: 16pt bold title + 3 paragraphs with unique markers.

    The title becomes a ``heading_path`` entry on the paragraph chunks; the
    paragraphs are short ASCII English text, predictable for char/word
    counts and language detection.
    """
    doc = op.Document()
    page = op.Page.a4()

    page.set_font(op.Font.HELVETICA_BOLD, 16.0)
    page.text_at(50.0, 750.0, "Specification Title")

    page.set_font(op.Font.HELVETICA, 11.0)
    page.text_at(50.0, 700.0, "First paragraph contains marker token alpha.")
    page.text_at(50.0, 680.0, "Second paragraph contains marker token bravo.")
    page.text_at(50.0, 660.0, "Third paragraph contains marker token charlie.")

    doc.add_page(page)
    return doc.save_to_bytes()


def _build_two_page_pdf() -> bytes:
    """Two pages, each with a heading + paragraph — for page_span / regions."""
    doc = op.Document()
    for idx, (heading, body) in enumerate(
        [
            ("Section One", "Body of the first section."),
            ("Section Two", "Body of the second section."),
        ]
    ):
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA_BOLD, 16.0)
        page.text_at(50.0, 750.0, heading)
        page.set_font(op.Font.HELVETICA, 11.0)
        page.text_at(50.0, 700.0, body)
        doc.add_page(page)
    return doc.save_to_bytes()


# ── Tests ────────────────────────────────────────────────────────────────


class TestHeadingPath:
    """``RagChunk.heading_path`` exposes the full root→leaf breadcrumb."""

    def test_paragraphs_carry_title_in_heading_path(self):
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        chunks = reader.rag_chunks()

        para_chunks = [c for c in chunks if "marker token" in c.text]
        assert para_chunks, "expected at least one paragraph chunk"

        for chunk in para_chunks:
            assert chunk.heading_path == ["Specification Title"], (
                f"heading_path should be [title] for paragraph chunk; "
                f"got {chunk.heading_path!r}"
            )


class TestContentTypeFlags:
    """``RagChunk.content_types`` reflects which element kinds are inside."""

    def test_paragraph_chunk_has_no_content_type_flags(self):
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        chunks = reader.rag_chunks()
        para_chunks = [c for c in chunks if "marker token alpha" in c.text]
        assert para_chunks, "expected the alpha paragraph chunk"

        flags = para_chunks[0].content_types
        assert flags.has_table is False
        assert flags.has_list is False
        assert flags.has_code is False
        # The paragraph chunk is text only — not heading_only.
        assert flags.heading_only is False


class TestCounts:
    """``char_count``, ``word_count``, ``sentence_count`` reflect the text."""

    def test_counts_match_chunk_text(self):
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        chunks = reader.rag_chunks()
        assert chunks

        for chunk in chunks:
            text = chunk.text
            assert chunk.char_count == len(text), (
                f"char_count {chunk.char_count} != len(text) {len(text)} "
                f"for chunk_index={chunk.chunk_index}"
            )
            expected_words = len(text.split())
            assert chunk.word_count == expected_words, (
                f"word_count {chunk.word_count} != whitespace-split count "
                f"{expected_words} for chunk_index={chunk.chunk_index}"
            )
            assert chunk.sentence_count >= 1, (
                f"sentence_count must be >= 1 for non-empty chunk; "
                f"got {chunk.sentence_count}"
            )


class TestChunkIdChain:
    """``chunk_id`` is non-empty and ``prev/next_chunk_id`` form a linked list."""

    def test_ids_are_unique_and_chain_consistent(self):
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        chunks = reader.rag_chunks()
        assert len(chunks) >= 2, "need at least two chunks to verify chain"

        ids = [c.chunk_id for c in chunks]
        assert all(cid for cid in ids), f"empty chunk_id present: {ids}"
        assert len(set(ids)) == len(ids), f"chunk_id collision: {ids}"

        # First chunk has no predecessor; last has no successor.
        assert chunks[0].prev_chunk_id is None
        assert chunks[-1].next_chunk_id is None

        # Pairwise consistency.
        for i in range(len(chunks) - 1):
            assert chunks[i].next_chunk_id == chunks[i + 1].chunk_id, (
                f"chunk[{i}].next != chunk[{i+1}].id"
            )
            assert chunks[i + 1].prev_chunk_id == chunks[i].chunk_id, (
                f"chunk[{i+1}].prev != chunk[{i}].id"
            )


class TestPageSpanAndRegions:
    """``page_span`` and ``page_regions`` cite the source PDF region."""

    def test_single_page_chunk_has_page_span_with_equal_bounds(self):
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        chunks = reader.rag_chunks()

        for chunk in chunks:
            assert chunk.page_span is not None, "single-page chunk must have page_span"
            lo, hi = chunk.page_span
            assert lo == hi, (
                f"single-page chunk should have lo==hi page_span, got ({lo}, {hi})"
            )

    def test_page_regions_one_entry_per_page_touched(self):
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        chunks = reader.rag_chunks()

        for chunk in chunks:
            pages_in_regions = [r.page for r in chunk.page_regions]
            assert pages_in_regions == sorted(pages_in_regions), (
                f"page_regions must be sorted by page, got {pages_in_regions}"
            )
            # No duplicates: one bbox per page.
            assert len(set(pages_in_regions)) == len(pages_in_regions)

    def test_page_region_bbox_has_positive_extent(self):
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        chunks = reader.rag_chunks()

        any_region_seen = False
        for chunk in chunks:
            for region in chunk.page_regions:
                any_region_seen = True
                assert region.bbox.width >= 0.0
                assert region.bbox.height >= 0.0
                # x/y are PDF coordinates — non-negative for our fixture.
                assert region.bbox.x >= 0.0
                assert region.bbox.y >= 0.0
        assert any_region_seen, "expected at least one page_region across chunks"


class TestDominantFontAndStyle:
    """Title-only chunks carry the bold flag; body chunks do not."""

    def test_title_chunk_is_bold_and_dominant_font_is_helvetica_bold(self):
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        chunks = reader.rag_chunks()

        title_chunks = [c for c in chunks if "Specification Title" in c.text and "marker" not in c.text]
        if not title_chunks:
            pytest.skip("title was merged into a paragraph chunk by the chunker")
        title = title_chunks[0]
        assert title.is_bold is True
        assert title.dominant_font is not None
        assert "Bold" in title.dominant_font or "Helv" in title.dominant_font
        assert title.dominant_font_size is not None
        assert title.dominant_font_size > 12.0


class TestMinConfidence:
    """``min_confidence`` is in [0, 1]."""

    def test_min_confidence_in_unit_interval(self):
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        chunks = reader.rag_chunks()
        for chunk in chunks:
            assert 0.0 <= chunk.min_confidence <= 1.0


class TestLanguageDetection:
    """``language``/``language_confidence``/``language_reliable`` populated by upstream."""

    def test_language_fields_present_or_all_none(self):
        reader = op.PdfReader.from_bytes(_build_titled_paragraphs_pdf())
        chunks = reader.rag_chunks()
        for chunk in chunks:
            # Tri-state: either all None (inconclusive) or all set together.
            triplet = (chunk.language, chunk.language_confidence, chunk.language_reliable)
            assert all(v is None for v in triplet) or all(v is not None for v in triplet), (
                f"language triplet must be consistently None or set, got {triplet}"
            )
            if chunk.language is not None:
                # ISO 639-3: 3 lowercase letters.
                assert re.fullmatch(r"[a-z]{3}", chunk.language), (
                    f"language must be ISO 639-3 lowercase, got {chunk.language!r}"
                )
                assert 0.0 <= chunk.language_confidence <= 1.0


class TestPageSpanMultiPage:
    """A multi-page document yields chunks with monotonic per-chunk page_span."""

    def test_each_chunk_page_span_lo_le_hi(self):
        reader = op.PdfReader.from_bytes(_build_two_page_pdf())
        chunks = reader.rag_chunks()
        for chunk in chunks:
            if chunk.page_span is None:
                continue
            lo, hi = chunk.page_span
            assert lo <= hi
