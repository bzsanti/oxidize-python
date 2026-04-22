"""Semantic regression tests for ``PdfReader.rag_chunks()`` disjointness.

These tests guard against the v0.4.2 / oxidize-pdf-core 2.5.4 bug where
``HybridChunker::chunk()`` re-injected just-flushed elements back into the
working buffer through the ``overlap_tokens > 0`` branch, producing chunks
that grew quadratically — every chunk i+1 contained chunk i as a prefix.
That made ``rag_chunks()`` unusable for RAG ingestion despite the API
shape looking correct.

The contract verified here:

  * Pairwise disjointness: no chunk's text is a substring of another's.
  * Marker uniqueness: each unique paragraph marker present in the source
    PDF must appear in exactly one chunk.
  * Bounded fan-out: the number of chunks must not exceed the number of
    source elements (a strict upper bound; quadratic duplication blows
    past it immediately).

These are SEMANTIC tests (input → expected output), not shape smoke tests.
The 2026-04-21 audit lesson is the reason this file exists separately
from ``test_ai_pipeline.py``.
"""

from __future__ import annotations

import pytest
import oxidize_pdf as op


# ── Synthetic PDF builders ────────────────────────────────────────────────

# Markers chosen to be unique and unlikely to collide with framework
# punctuation, so substring checks are unambiguous.
_TITLE_MARKER = "HEAD-ALPHA"
_PARA_MARKERS = ("alpha-content-line", "bravo-content-line", "charlie-content-line")


def _build_title_then_paragraphs_pdf() -> bytes:
    """One page: 16pt bold title + three 11pt paragraphs.

    Mirrors the core regression test
    ``end_to_end_pdf_produces_disjoint_chunks`` so a failure here is
    directly comparable to the upstream test.
    """
    doc = op.Document()
    page = op.Page.a4()

    page.set_font(op.Font.HELVETICA_BOLD, 16.0)
    page.text_at(50.0, 750.0, _TITLE_MARKER)

    page.set_font(op.Font.HELVETICA, 11.0)
    page.text_at(50.0, 700.0, f"Para1 body paragraph {_PARA_MARKERS[0]}.")
    page.text_at(50.0, 680.0, f"Para2 body paragraph {_PARA_MARKERS[1]}.")
    page.text_at(50.0, 660.0, f"Para3 body paragraph {_PARA_MARKERS[2]}.")

    doc.add_page(page)
    return doc.save_to_bytes()


def _build_multi_section_pdf() -> bytes:
    """Two sections, each with title + two paragraphs, on separate pages.

    Exercises a longer element stream where the bug manifested most
    dramatically (later chunks accumulate every prior chunk).
    """
    doc = op.Document()

    for section_idx, section_label in enumerate(("SECTION-ONE", "SECTION-TWO")):
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA_BOLD, 16.0)
        page.text_at(50.0, 750.0, section_label)

        page.set_font(op.Font.HELVETICA, 11.0)
        for para_idx in range(3):
            marker = f"sec{section_idx}-para{para_idx}-unique-token"
            y = 700.0 - para_idx * 20.0
            page.text_at(50.0, y, f"Body line {marker} ends here.")

        doc.add_page(page)

    return doc.save_to_bytes()


# ── Generic semantic assertions ──────────────────────────────────────────


def _assert_chunks_pairwise_disjoint(chunks) -> None:
    """No chunk's text may be a substring of another chunk's text."""
    for i in range(len(chunks)):
        for j in range(i + 1, len(chunks)):
            ti = chunks[i].text
            tj = chunks[j].text
            assert ti, f"chunk[{i}].text is empty"
            assert tj, f"chunk[{j}].text is empty"
            assert ti not in tj, (
                f"chunk[{i}].text is a substring of chunk[{j}].text "
                f"(quadratic accumulation bug)\n"
                f"  i={ti!r}\n  j={tj!r}"
            )
            assert tj not in ti, (
                f"chunk[{j}].text is a substring of chunk[{i}].text "
                f"(quadratic accumulation bug)\n"
                f"  i={ti!r}\n  j={tj!r}"
            )


def _assert_marker_appears_exactly_once(chunks, marker: str) -> None:
    occurrences = sum(1 for c in chunks if marker in c.text)
    assert occurrences == 1, (
        f"marker {marker!r} must appear in exactly one chunk, "
        f"found in {occurrences}\n"
        f"  chunks: {[c.text for c in chunks]}"
    )


# ── Tests ────────────────────────────────────────────────────────────────


class TestRagChunksDisjointness:
    """``PdfReader.rag_chunks()`` MUST emit element-disjoint chunks."""

    def test_title_plus_paragraphs_chunks_are_disjoint(self):
        pdf_bytes = _build_title_then_paragraphs_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        chunks = reader.rag_chunks()

        assert len(chunks) > 0, "rag_chunks() must emit at least one chunk"
        _assert_chunks_pairwise_disjoint(chunks)

    def test_each_paragraph_marker_appears_in_exactly_one_chunk(self):
        pdf_bytes = _build_title_then_paragraphs_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        chunks = reader.rag_chunks()

        for marker in _PARA_MARKERS:
            _assert_marker_appears_exactly_once(chunks, marker)

    def test_chunk_count_bounded_by_source_elements(self):
        """4 source elements (title + 3 paragraphs) → at most 4 chunks.

        The pre-fix output produced 4 chunks where each later one
        contained all earlier ones, so this bound was technically met
        for this fixture — but the multi-section variant below makes
        the violation visible.
        """
        pdf_bytes = _build_title_then_paragraphs_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        chunks = reader.rag_chunks()

        # Title + 3 paragraphs = 4 source elements; chunker may merge but
        # MUST NOT split a paragraph or duplicate elements.
        assert len(chunks) <= 4, (
            f"chunk count ({len(chunks)}) exceeds source element count (4); "
            "duplication suspected"
        )

    def test_multi_section_pdf_chunks_are_disjoint(self):
        pdf_bytes = _build_multi_section_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        chunks = reader.rag_chunks()

        assert len(chunks) > 0
        _assert_chunks_pairwise_disjoint(chunks)

    def test_multi_section_each_marker_appears_once(self):
        pdf_bytes = _build_multi_section_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        chunks = reader.rag_chunks()

        for section_idx in range(2):
            for para_idx in range(3):
                marker = f"sec{section_idx}-para{para_idx}-unique-token"
                _assert_marker_appears_exactly_once(chunks, marker)

    def test_multi_section_chunk_count_bounded(self):
        pdf_bytes = _build_multi_section_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        chunks = reader.rag_chunks()

        # 2 sections * (1 title + 3 paragraphs) = 8 source elements.
        # Pre-fix behaviour produced more chunks than elements because
        # type-boundary flushes triggered every other element.
        assert len(chunks) <= 8, (
            f"chunk count ({len(chunks)}) exceeds source element count (8); "
            "duplication suspected"
        )


class TestRagChunksDisjointnessAcrossProfiles:
    """Disjointness contract MUST hold for every extraction profile."""

    @pytest.mark.parametrize(
        "profile",
        [
            op.ExtractionProfile.STANDARD,
            op.ExtractionProfile.RAG,
            op.ExtractionProfile.ACADEMIC,
        ],
    )
    def test_profile_emits_disjoint_chunks(self, profile):
        pdf_bytes = _build_multi_section_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        chunks = reader.rag_chunks_with_profile(profile)

        assert len(chunks) > 0
        _assert_chunks_pairwise_disjoint(chunks)

    @pytest.mark.parametrize(
        "profile",
        [
            op.ExtractionProfile.STANDARD,
            op.ExtractionProfile.RAG,
            op.ExtractionProfile.ACADEMIC,
        ],
    )
    def test_profile_marker_uniqueness(self, profile):
        pdf_bytes = _build_multi_section_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        chunks = reader.rag_chunks_with_profile(profile)

        for section_idx in range(2):
            for para_idx in range(3):
                marker = f"sec{section_idx}-para{para_idx}-unique-token"
                _assert_marker_appears_exactly_once(chunks, marker)
