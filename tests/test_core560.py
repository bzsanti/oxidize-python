"""Core 5.6.0 behavior through packaged public Python APIs."""
from pathlib import Path

import oxidize_pdf as op
import pytest


def reader(name):
    return op.PdfReader.from_bytes((Path(__file__).parent / "fixtures/core560" / (name + ".pdf")).read_bytes())


@pytest.mark.parametrize("name,flag,ordinary,enabled", [
    ("visual", "visual_line_order", "12-34-56\nAccount No.\nPayments to be made to:", "Account No. 12-34-56\nPayments to be made to:"),
    ("fallback", "incomplete_tounicode_encoding_fallback", "����� �����", "Hello world"),
    ("annotation", "include_annotation_appearances", "Body", "Body\nNote"),
])
def test_opt_in_reaches_all_extraction_routes(name, flag, ordinary, enabled):
    doc = reader(name)
    assert getattr(op.ExtractionOptions(), flag) is False
    assert doc.extract_page_text(0, op.ExtractionOptions()).text == ordinary
    options = op.ExtractionOptions(**{flag: True})
    assert getattr(options, flag) is True
    assert doc.extract_page_text(0, options).text == enabled
    assert doc.extract_text_with_options(options) == [enabled]
    recovered = doc.extract_page_text_with_recovery(0, max_stream_bytes=4096, options=options)
    assert recovered.text.text == enabled
    assert recovered.diagnostics == []


def test_tj_default_and_explicit_old_threshold():
    doc = reader("tj")
    assert doc.extract_page_text(0, op.ExtractionOptions()).text == "Alpha Beta"
    assert doc.extract_page_text(0, op.ExtractionOptions(tj_space_threshold=0.2)).text == "AlphaBeta"


def test_annotation_recovery_preserves_diagnostics_and_budgets():
    doc = reader("annotation-damaged")
    options = op.ExtractionOptions(include_annotation_appearances=True)
    assert doc.extract_page_text(0, op.ExtractionOptions()).text == "Body"
    with pytest.raises(op.PdfParseError):
        doc.extract_page_text(0, options)
    result = doc.extract_page_text_with_recovery(0, max_stream_bytes=4096, options=options)
    assert result.text.text == "Body\nNote"
    diagnostic, = result.diagnostics
    assert diagnostic.location == "annotation_appearance"
    assert diagnostic.object_id == (7, 0)
    assert diagnostic.contents_index is None and diagnostic.form_name is None
    assert diagnostic.action == "recovered" and diagnostic.kind == "unverified"
    with pytest.raises(op.PdfParseError):
        doc.extract_page_text_with_recovery(0, max_stream_bytes=2, options=options)
    bounded = doc.extract_page_text_with_recovery(0, max_stream_bytes=4096,
        options=op.ExtractionOptions(include_annotation_appearances=True, max_extracted_bytes=6))
    assert bounded.text.truncated and len(bounded.text.text.encode()) <= 6
