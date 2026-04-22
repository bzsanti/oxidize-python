"""Tests for ``PdfReader.chunk_page()`` — per-page chunking (RAG-010).

This is the Python counterpart of .NET's
``PdfExtractor.ExtractChunksFromPageAsync()``. Both bridges must offer
single-page chunking so consumers can feed only the pages they care
about into a vector store, without re-chunking and filtering the
whole document.

Tests are SEMANTIC: build PDFs with unique markers per page, call
``chunk_page(i)``, verify each call returns chunks containing only
that page's marker. No shape-only smoke tests (lesson 2026-04-21).
"""

from __future__ import annotations

import pytest
import oxidize_pdf as op


# ── Fixture builder ──────────────────────────────────────────────────────

# Tokens chosen to be distinct, multi-character, and unlikely to collide
# with framework punctuation, so substring checks are unambiguous.
_PAGE_MARKERS = (
    "page-zero-marker-alpha",
    "page-one-marker-bravo",
    "page-two-marker-charlie",
)


def _build_three_page_pdf() -> bytes:
    """Three pages, each with one short paragraph carrying a unique marker.

    Each page's body is small enough (~10 tokens) that the default chunker
    (512 tokens) will emit at most one chunk per page.
    """
    doc = op.Document()
    for marker in _PAGE_MARKERS:
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA, 11.0)
        page.text_at(50.0, 750.0, f"Body line containing {marker} ends here.")
        doc.add_page(page)
    return doc.save_to_bytes()


def _build_long_page_pdf() -> bytes:
    """Two pages where each page's body is intentionally long (~150 tokens).

    Combined with a small chunk size, this forces the chunker to emit
    multiple chunks per page so we can verify chunk_index sequencing
    within a single page invocation.
    """
    doc = op.Document()
    for page_idx in range(2):
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA, 11.0)
        # Stack 8 lines of distinct content — enough text to overflow a
        # small chunk size and produce multiple chunks.
        for line_idx in range(8):
            marker = f"p{page_idx}-line{line_idx}-token-zzz"
            y = 760.0 - line_idx * 20.0
            page.text_at(50.0, y, f"Line {line_idx} contains {marker} repeatedly here.")
        doc.add_page(page)
    return doc.save_to_bytes()


# ── Tests ────────────────────────────────────────────────────────────────


class TestChunkPageBasic:
    """Per-page chunking returns only that page's content."""

    def test_each_page_returns_chunks_with_only_its_marker(self):
        pdf_bytes = _build_three_page_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        for page_idx, marker in enumerate(_PAGE_MARKERS):
            chunks = reader.chunk_page(page_idx)

            assert len(chunks) >= 1, (
                f"page {page_idx} produced 0 chunks; expected at least 1"
            )

            # Every chunk from page i must contain page i's marker
            for chunk in chunks:
                assert marker in chunk.content, (
                    f"page {page_idx} chunk does not contain expected marker "
                    f"{marker!r}; got: {chunk.content!r}"
                )

            # No chunk from page i may contain ANOTHER page's marker —
            # this is the contamination guard.
            other_markers = [m for m in _PAGE_MARKERS if m != marker]
            for chunk in chunks:
                for other in other_markers:
                    assert other not in chunk.content, (
                        f"page {page_idx} chunk leaked marker {other!r} from "
                        f"another page; got: {chunk.content!r}"
                    )

    def test_page_index_is_zero_based(self):
        # Per Phase 0 decision: the bridge is 0-based across the board.
        # Calling chunk_page(0) returns the FIRST page's content, not the
        # second.
        pdf_bytes = _build_three_page_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        chunks = reader.chunk_page(0)
        all_text = " ".join(c.content for c in chunks)
        assert _PAGE_MARKERS[0] in all_text
        assert _PAGE_MARKERS[1] not in all_text

    def test_default_chunk_size_and_overlap(self):
        # No explicit args => defaults (512 tokens, 50 overlap, matching
        # DocumentChunker.default()). Short body fits in one chunk.
        pdf_bytes = _build_three_page_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        chunks = reader.chunk_page(0)
        assert len(chunks) == 1, (
            f"short page should fit in a single default-sized chunk; "
            f"got {len(chunks)}"
        )

    def test_returned_chunks_expose_documentchunk_schema(self):
        # Verify the returned objects ARE DocumentChunks by exercising every
        # field with assertions on actual values — no bare hasattr() checks.
        pdf_bytes = _build_three_page_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        chunks = reader.chunk_page(0)
        assert len(chunks) >= 1

        chunk = chunks[0]
        # id: non-empty string identifier
        assert isinstance(chunk.id, str) and len(chunk.id) > 0
        # content: non-empty string with the page marker
        assert isinstance(chunk.content, str)
        assert _PAGE_MARKERS[0] in chunk.content
        # tokens: positive integer roughly proportional to content length
        assert isinstance(chunk.tokens, int)
        assert chunk.tokens > 0
        # page_numbers: list of ints (semantics tested elsewhere; here we
        # only assert the type contract)
        assert isinstance(chunk.page_numbers, list)
        for pn in chunk.page_numbers:
            assert isinstance(pn, int)
        # chunk_index: 0-based int, sequential
        assert isinstance(chunk.chunk_index, int)
        assert chunk.chunk_index == 0


class TestChunkPageMultipleChunks:
    """Long pages produce multiple chunks; sequencing and isolation hold."""

    def test_long_page_produces_multiple_sequential_chunks(self):
        pdf_bytes = _build_long_page_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        # Tight chunk size forces overflow into multiple chunks per page.
        chunks = reader.chunk_page(0, chunk_size=10, overlap=2)

        assert len(chunks) > 1, (
            f"chunk_size=10 on a ~150-token page should produce >1 chunk; "
            f"got {len(chunks)}"
        )

        indexes = [c.chunk_index for c in chunks]
        assert indexes == list(range(len(chunks))), (
            f"chunk_index must be sequential within a page; got {indexes}"
        )

    def test_long_pages_isolated_from_each_other(self):
        # The contamination guard is the key contract: even with multi-chunk
        # output, page 0 chunks must not contain page 1 markers, and vice
        # versa.
        pdf_bytes = _build_long_page_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        page0_chunks = reader.chunk_page(0, chunk_size=10, overlap=2)
        page1_chunks = reader.chunk_page(1, chunk_size=10, overlap=2)

        page0_text = " ".join(c.content for c in page0_chunks)
        page1_text = " ".join(c.content for c in page1_chunks)

        for line_idx in range(8):
            assert f"p0-line{line_idx}-token-zzz" in page0_text
            assert f"p1-line{line_idx}-token-zzz" in page1_text
            # Cross-contamination check
            assert f"p0-line{line_idx}-token-zzz" not in page1_text
            assert f"p1-line{line_idx}-token-zzz" not in page0_text


class TestChunkPageErrorCases:
    """Out-of-range pages and invalid configs raise the expected errors."""

    def test_out_of_range_page_raises(self):
        pdf_bytes = _build_three_page_pdf()  # 3 pages: valid indexes 0, 1, 2
        reader = op.PdfReader.from_bytes(pdf_bytes)

        with pytest.raises(op.PdfError):
            reader.chunk_page(99)

    def test_explicit_zero_chunk_size_raises(self):
        # Defensive: chunk_size=0 is meaningless. We expect either a
        # PdfError from the underlying chunker or a ValueError from
        # bridge-level validation. Either is acceptable; what we verify is
        # that we don't silently return garbage.
        pdf_bytes = _build_three_page_pdf()
        reader = op.PdfReader.from_bytes(pdf_bytes)

        with pytest.raises((op.PdfError, ValueError, OverflowError)):
            reader.chunk_page(0, chunk_size=0, overlap=0)
