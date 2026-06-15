"""Tests for the unstable ``ElementClassifier`` SPI (Fase 5).

A custom classifier assigns an open string label to each element before
chunking; the label is stored on :attr:`Element.class_label` and may be
read by a custom chunking strategy to drive boundaries.

These tests guard:

  * ``ClassLabel`` is constructible and ``str``-comparable.
  * ``ClassifyContext`` exposes ``elements`` and ``index`` read-only.
  * The classifier output reaches ``Element.class_label`` and is visible
    to a chunking strategy in the same pipeline.
  * Errors raised inside the Python classifier surface as PyErr.
"""

from __future__ import annotations

import pytest
import oxidize_pdf as op
from oxidize_pdf import experimental as spi


def _build_pdf_with_three_paragraphs() -> bytes:
    doc = op.Document()
    page = op.Page.a4()
    page.set_font(op.Font.HELVETICA_BOLD, 16.0)
    page.text_at(50.0, 750.0, "Section Heading")
    page.set_font(op.Font.HELVETICA, 11.0)
    page.text_at(50.0, 700.0, "First paragraph carrying marker alpha here.")
    page.text_at(50.0, 680.0, "Second paragraph carrying marker bravo there.")
    page.text_at(50.0, 660.0, "Third paragraph carrying marker charlie now.")
    doc.add_page(page)
    return doc.save_to_bytes()


# ── ClassLabel constructor & equality ────────────────────────────────────


class TestClassLabel:
    def test_constructible_from_string(self):
        label = spi.ClassLabel("clause")
        assert label.as_str() == "clause"

    def test_label_equals_underlying_string(self):
        label = spi.ClassLabel("definition")
        assert label == "definition"

    def test_str_returns_label_value(self):
        label = spi.ClassLabel("rule")
        assert str(label) == "rule"


# ── ClassifyContext shape ────────────────────────────────────────────────


class TestClassifyContext:
    def test_context_passed_to_classifier_exposes_elements_and_index(self):
        observed_indices = []
        observed_lengths = []

        class IndexRecorder:
            def classify(self, element, ctx):
                observed_indices.append(ctx.index)
                observed_lengths.append(len(ctx.elements))
                return None

        reader = op.PdfReader.from_bytes(_build_pdf_with_three_paragraphs())
        pipeline = spi.AnalysisPipeline().with_classifier(IndexRecorder())
        reader.rag_chunks_with_pipeline(pipeline)

        # The classifier is called once per element, indices are contiguous
        # from 0 to len-1, and ctx.elements length is constant across calls.
        n = len(observed_indices)
        assert n > 0
        assert observed_indices == list(range(n))
        assert observed_lengths == [n] * n


# ── Classifier output reaches Element.class_label ────────────────────────


class TestClassifierLabelsTravel:
    def test_strategy_sees_class_label_set_by_classifier(self):
        """A classifier sets a label; a custom strategy reads it via ``element.class_label``."""

        class TitleClassifier:
            def classify(self, element, ctx):
                if element.type_name == "title":
                    return spi.ClassLabel("HEADING")
                return spi.ClassLabel("BODY")

        seen_labels: list[str | None] = []

        class LabelReader:
            def chunk(self, elements):
                for e in elements:
                    seen_labels.append(e.class_label)
                # Trivial strategy: one chunk per element so we surface them.
                return [spi.ChunkGroup(elements=[e]) for e in elements]

        reader = op.PdfReader.from_bytes(_build_pdf_with_three_paragraphs())
        pipeline = (
            spi.AnalysisPipeline()
            .with_classifier(TitleClassifier())
            .with_chunking(LabelReader())
        )
        reader.rag_chunks_with_pipeline(pipeline)

        assert seen_labels, "strategy must have seen at least one element"
        # At least one HEADING and one BODY label among the elements.
        assert "HEADING" in seen_labels
        assert "BODY" in seen_labels
        # No element is unlabeled because the classifier returns a label for every input.
        assert None not in seen_labels


# ── Classifier returning None leaves the label unset ─────────────────────


class TestClassifierReturningNone:
    def test_none_keeps_class_label_unset(self):
        class AlwaysNone:
            def classify(self, element, ctx):
                return None

        seen_labels: list[str | None] = []

        class LabelReader:
            def chunk(self, elements):
                for e in elements:
                    seen_labels.append(e.class_label)
                return [spi.ChunkGroup(elements=[e]) for e in elements]

        reader = op.PdfReader.from_bytes(_build_pdf_with_three_paragraphs())
        pipeline = (
            spi.AnalysisPipeline()
            .with_classifier(AlwaysNone())
            .with_chunking(LabelReader())
        )
        reader.rag_chunks_with_pipeline(pipeline)

        assert seen_labels
        assert all(label is None for label in seen_labels), (
            f"all labels must be None when classifier returns None, got {seen_labels}"
        )


# ── Classifier error propagation ─────────────────────────────────────────


class TestClassifierErrorPropagation:
    def test_classifier_exception_surfaces_to_caller(self):
        class Broken:
            def classify(self, element, ctx):
                raise RuntimeError("classifier blew up on purpose")

        reader = op.PdfReader.from_bytes(_build_pdf_with_three_paragraphs())
        pipeline = spi.AnalysisPipeline().with_classifier(Broken())

        with pytest.raises(Exception) as excinfo:
            reader.rag_chunks_with_pipeline(pipeline)
        assert "blew up on purpose" in str(excinfo.value)
