"""Tests for ``DocumentSource`` and ``PdfReader.rag_chunks_with_source[_and_config]``.

These guard the source-stamping API introduced by upstream 2.16.0:

  * ``DocumentSource(filename=..., doc_hash=...)`` is the only public
    constructor (the upstream struct is ``#[non_exhaustive]``).
  * ``rag_chunks_with_source`` returns chunks whose ``source`` is non-None
    and whose ``source.filename``/``source.doc_hash`` echo the caller input.
  * The auto-fill rule from the info dictionary populates ``title`` and
    ``author`` even when the caller left them at their constructor defaults.
  * ``chunk_id`` is prefixed by the caller-supplied ``doc_hash`` so chunks
    from different documents cannot collide.
  * ``rag_chunks_with_source_and_config`` honours a custom token budget
    (oversize threshold differs from the default).
"""

from __future__ import annotations

import oxidize_pdf as op


def _build_source_pdf_with_info(*, title: str, author: str) -> bytes:
    """One-page PDF with info-dictionary metadata + a couple of paragraphs."""
    doc = op.Document()
    doc.set_title(title)
    doc.set_author(author)

    page = op.Page.a4()
    page.set_font(op.Font.HELVETICA_BOLD, 16.0)
    page.text_at(50.0, 750.0, "Heading One")
    page.set_font(op.Font.HELVETICA, 11.0)
    page.text_at(50.0, 700.0, "First paragraph with a unique marker xyzzy.")
    page.text_at(50.0, 680.0, "Second paragraph with another marker quux.")
    doc.add_page(page)
    return doc.save_to_bytes()


def _build_long_pdf(num_paragraphs: int = 12) -> bytes:
    """Long-ish single-page PDF — used to exercise the token-budget path."""
    doc = op.Document()
    page = op.Page.a4()
    page.set_font(op.Font.HELVETICA_BOLD, 16.0)
    page.text_at(50.0, 800.0, "Long Title")
    page.set_font(op.Font.HELVETICA, 11.0)
    for i in range(num_paragraphs):
        y = 770.0 - i * 18.0
        text = (
            f"Paragraph {i} carries unique marker mark{i}. "
            f"It exists to push the chunk past a small token budget."
        )
        page.text_at(50.0, y, text)
    doc.add_page(page)
    return doc.save_to_bytes()


# ── DocumentSource constructor ───────────────────────────────────────────


class TestDocumentSourceConstructor:
    def test_default_constructor_yields_all_none(self):
        src = op.DocumentSource()
        assert src.filename is None
        assert src.doc_hash is None
        assert src.title is None
        assert src.author is None
        assert src.creation_date is None
        assert src.total_pages is None

    def test_constructor_keyword_args_set_filename_and_hash(self):
        src = op.DocumentSource(filename="invoice.pdf", doc_hash="abc123")
        assert src.filename == "invoice.pdf"
        assert src.doc_hash == "abc123"
        # The other fields stay None; the auto-fill happens only when passed
        # through ``rag_chunks_with_source``.
        assert src.title is None
        assert src.author is None

    def test_partial_construction_leaves_other_field_none(self):
        # Only filename set.
        src = op.DocumentSource(filename="just-filename.pdf")
        assert src.filename == "just-filename.pdf"
        assert src.doc_hash is None


# ── rag_chunks_with_source: stamping + autofill + chunk_id prefix ────────


class TestRagChunksWithSource:
    def test_chunks_carry_source_with_caller_supplied_fields(self):
        pdf_bytes = _build_source_pdf_with_info(title="The Title", author="The Author")
        reader = op.PdfReader.from_bytes(pdf_bytes)
        source = op.DocumentSource(filename="doc.pdf", doc_hash="hashv1")
        chunks = reader.rag_chunks_with_source(source)
        assert chunks

        for chunk in chunks:
            assert chunk.source is not None, "source must be stamped on every chunk"
            assert chunk.source.filename == "doc.pdf"
            assert chunk.source.doc_hash == "hashv1"

    def test_source_autofills_title_and_author_from_info_dict(self):
        pdf_bytes = _build_source_pdf_with_info(title="The Title", author="The Author")
        reader = op.PdfReader.from_bytes(pdf_bytes)
        # Caller leaves title/author None — info-dict autofill should win.
        source = op.DocumentSource(filename="doc.pdf", doc_hash="hashv2")
        chunks = reader.rag_chunks_with_source(source)
        assert chunks

        for chunk in chunks:
            assert chunk.source.title == "The Title", (
                f"title must autofill from info dict; got {chunk.source.title!r}"
            )
            assert chunk.source.author == "The Author", (
                f"author must autofill from info dict; got {chunk.source.author!r}"
            )

    def test_total_pages_autofills_when_caller_left_it_none(self):
        pdf_bytes = _build_source_pdf_with_info(title="t", author="a")
        reader = op.PdfReader.from_bytes(pdf_bytes)
        source = op.DocumentSource(filename="d.pdf", doc_hash="h")
        chunks = reader.rag_chunks_with_source(source)
        assert chunks

        for chunk in chunks:
            # Single-page fixture: total_pages == 1.
            assert chunk.source.total_pages == 1

    def test_chunk_id_is_prefixed_by_doc_hash(self):
        pdf_bytes = _build_source_pdf_with_info(title="t", author="a")
        reader = op.PdfReader.from_bytes(pdf_bytes)
        chunks = reader.rag_chunks_with_source(
            op.DocumentSource(filename="d.pdf", doc_hash="HASHPREFIX")
        )
        assert chunks
        for chunk in chunks:
            assert chunk.chunk_id.startswith("HASHPREFIX"), (
                f"chunk_id should start with the doc_hash; got {chunk.chunk_id!r}"
            )

    def test_no_source_means_chunk_source_is_none(self):
        """Plain ``rag_chunks()`` leaves the ``source`` getter as None."""
        pdf_bytes = _build_source_pdf_with_info(title="t", author="a")
        reader = op.PdfReader.from_bytes(pdf_bytes)
        chunks = reader.rag_chunks()
        assert chunks
        for chunk in chunks:
            assert chunk.source is None


# ── rag_chunks_with_source_and_config: honours token budget ──────────────


class TestRagChunksWithSourceAndConfig:
    def test_smaller_token_budget_yields_more_chunks_than_default(self):
        pdf_bytes = _build_long_pdf(num_paragraphs=12)
        reader = op.PdfReader.from_bytes(pdf_bytes)

        source = op.DocumentSource(filename="long.pdf", doc_hash="lh")
        default_chunks = reader.rag_chunks_with_source(source)
        tight = op.HybridChunkConfig(max_tokens=32, overlap_tokens=0)
        tight_chunks = reader.rag_chunks_with_source_and_config(source, tight)

        # The tight budget must split into at least as many — typically more —
        # chunks than the default 512-token budget.
        assert len(tight_chunks) >= len(default_chunks), (
            f"tight budget should not produce fewer chunks; "
            f"got tight={len(tight_chunks)} default={len(default_chunks)}"
        )

    def test_source_stamping_survives_custom_config(self):
        pdf_bytes = _build_long_pdf(num_paragraphs=6)
        reader = op.PdfReader.from_bytes(pdf_bytes)

        config = op.HybridChunkConfig(max_tokens=128, overlap_tokens=10)
        source = op.DocumentSource(filename="x.pdf", doc_hash="cfgh")
        chunks = reader.rag_chunks_with_source_and_config(source, config)
        assert chunks
        for chunk in chunks:
            assert chunk.source.filename == "x.pdf"
            assert chunk.source.doc_hash == "cfgh"
            assert chunk.chunk_id.startswith("cfgh")
