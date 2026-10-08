"""Public contracts for the core 5.4.1 bridge; fixtures use explicit PDF syntax."""
import zlib

import pytest
import oxidize_pdf as op


def pdf_with_stream(data, *, filtered=False, catalog=b"", form=False):
    """Write exact lengths/xref offsets, allowing controlled damaged Flate payloads."""
    def stream(payload, extra=b""):
        return b"<< /Length %d %s >>\nstream\n" % (len(payload), extra) + payload + b"\nendstream"
    filter_spec = b"/Filter /FlateDecode" if filtered else b""
    resources = b"/Font << /F1 4 0 R >>"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R " + catalog + b" >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << "
        + resources + (b" /XObject << /Fm 6 0 R >>" if form else b"")
        + b" >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        stream(b"/Fm Do" if form else data, b"" if form else filter_spec),
    ]
    if form:
        objects.append(stream(data, filter_spec + b" /Type /XObject /Subtype /Form /BBox [0 0 612 792] /Resources << " + resources + b" >>"))
    result = b"%PDF-1.4\n"
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result += b"%d 0 obj\n" % i + obj + b"\nendobj\n"
    start = len(result)
    result += b"xref\n0 %d\n0000000000 65535 f \n" % len(offsets)
    result += b"".join(b"%010d 00000 n \n" % o for o in offsets[1:])
    result += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(offsets), start)
    return result


TEXT = b"BT /F1 12 Tf 72 720 Td (Recovery sample) Tj ET"


def test_effective_version_includes_catalog_override():
    reader = op.PdfReader.from_bytes(pdf_with_stream(TEXT, catalog=b"/Version /2.0"))
    assert reader.version == "1.4"
    assert reader.effective_version == "2.0"


@pytest.mark.parametrize("form", [False, True])
def test_recovery_preserves_unverified_diagnostics_and_strict_failure(form):
    data = pdf_with_stream(zlib.compress(TEXT)[:-4], filtered=True, form=form)
    reader = op.PdfReader.from_bytes(data)
    with pytest.raises(op.PdfParseError):
        reader.extract_text_from_page(0)
    result = reader.extract_page_text_with_recovery(0, max_stream_bytes=4096)
    assert result.page_index == 0
    assert result.text.text.strip() == "Recovery sample"
    assert not result.text.truncated
    assert len(result.diagnostics) == 1
    d = result.diagnostics[0]
    assert d.action == "recovered" and d.kind == "unverified"
    assert d.filter_index == 0 and d.error
    assert d.location == ("form_xobject" if form else "page_contents")
    assert d.contents_index == (None if form else 0)
    assert d.form_name == ("Fm" if form else None)
    assert d.object_id == ((6, 0) if form else None)
    # Explicit recovery must not make subsequent ordinary extraction tolerant.
    with pytest.raises(op.PdfParseError):
        reader.extract_text_from_page(0)
    results = reader.extract_text_with_recovery(max_stream_bytes=4096)
    assert results[0].text.text == result.text.text
    assert results[0].diagnostics[0].kind == "unverified"


def test_verified_recovery_has_no_diagnostics_and_honors_text_cap():
    reader = op.PdfReader.from_bytes(pdf_with_stream(zlib.compress(TEXT), filtered=True))
    result = reader.extract_page_text_with_recovery(0, max_stream_bytes=4096)
    assert result.text.text.strip() == "Recovery sample"
    assert result.diagnostics == []
    bounded = reader.extract_text_with_recovery(max_stream_bytes=4096, options=op.ExtractionOptions(max_extracted_bytes=3))[0]
    assert bounded.text.truncated and len(bounded.text.text.encode()) <= 3
    assert bounded.diagnostics == []


def test_omitted_content_is_observable():
    reader = op.PdfReader.from_bytes(pdf_with_stream(b"\xff\xff\xff", filtered=True))
    result = reader.extract_page_text_with_recovery(0, max_stream_bytes=4096)
    assert result.text.text == ""
    d, = result.diagnostics
    assert d.action == "omitted" and d.kind is None and d.filter_index is None
    assert d.contents_index == 0 and d.error


@pytest.mark.parametrize("filtered", [False, True])
def test_recovery_never_swallows_stream_limit(filtered):
    reader = op.PdfReader.from_bytes(pdf_with_stream(zlib.compress(TEXT) if filtered else TEXT, filtered=filtered))
    with pytest.raises(op.PdfParseError):
        reader.extract_page_text_with_recovery(0, max_stream_bytes=3)
    with pytest.raises(OverflowError):
        reader.extract_page_text_with_recovery(0, max_stream_bytes=-1)
    with pytest.raises(op.PdfParseError):
        reader.extract_page_text_with_recovery(99, max_stream_bytes=4096)


def test_nbsp_opt_in_applies_to_text_and_fragments():
    reader = op.PdfReader.from_bytes(pdf_with_stream(b"BT /F1 12 Tf 72 720 Td (hello\xa0world) Tj ET"))
    default = op.ExtractionOptions()
    normalized = op.ExtractionOptions(normalize_non_breaking_spaces=True, preserve_layout=True)
    assert not default.normalize_non_breaking_spaces
    assert normalized.normalize_non_breaking_spaces
    assert "hello\xa0world" in reader.extract_text_with_options(default)[0]
    assert "hello world" in reader.extract_text_with_options(normalized)[0]
    assert "hello world" in reader.extract_page_text(0, normalized).text
    assert any("hello world" in f.text for f in reader.extract_fragments_from_page(0, normalized))
    assert any("hello world" in f.text for f in reader.extract_fragments_with_options(normalized)[0])
    assert "hello world" in reader.extract_page_text_with_recovery(0, max_stream_bytes=4096, options=normalized).text.text


def test_build_identification_controls_serialized_info():
    def output(policy):
        doc = op.Document()
        doc.add_page(op.Page.a4())
        assert doc.build_identification == op.BuildIdentification.Enabled
        doc.set_build_identification(policy)
        assert doc.build_identification == policy
        doc.set_creator("Application")
        return bytes(doc.save_to_bytes())
    enabled = output(op.BuildIdentification.Enabled)
    disabled = output(op.BuildIdentification.Disabled)
    for key in (b"/oxidize-pdf-build", b"/oxidize-pdf-edition", b"/oxidize-pdf-features"):
        assert key in enabled and key not in disabled
    assert b"Application" in disabled
    assert op.PdfReader.from_bytes(disabled).page_count == 1


@pytest.fixture
def slot_pdf():
    base = pdf_with_stream(TEXT)
    prepared = op.create_signature_slot(base, "Signer-1", 0, (50, 50, 250, 150), metadata="Participante ñ")
    assert isinstance(prepared, bytes) and prepared.startswith(base)
    return base, prepared


def test_slot_create_list_read_remove_preserves_source(slot_pdf):
    base, prepared = slot_pdf
    assert op.list_signature_slots(base) == []
    slot, = op.list_signature_slots(prepared)
    assert slot.name == "Signer-1" and slot.metadata == "Participante ñ"
    assert slot.page_index == 0 and slot.rotation == 0
    assert slot.rect == (50, 50, 250, 150)
    assert not slot.completed and not slot.digitally_signed
    assert op.read_signature_slot(prepared, slot.name).metadata == slot.metadata
    removed = op.remove_signature_slot(prepared, slot.name)
    assert removed.startswith(prepared) and op.list_signature_slots(removed) == []
    assert op.PdfReader.from_bytes(removed).extract_text()[0].strip() == "Recovery sample"
    with pytest.raises(op.PdfError):
        op.read_signature_slot(removed, slot.name)


STROKES = [[(0.1, 0.2), (0.4, 0.8), (0.9, 0.3)]]


def test_slot_handwriting_is_not_crypto_and_completed_is_immutable(slot_pdf):
    _, prepared = slot_pdf
    drawn = op.draw_signature_slot(prepared, "Signer-1", STROKES, label="Reviewed")
    assert drawn.startswith(prepared)
    assert not op.read_signature_slot(drawn, "Signer-1").completed
    completed = op.complete_signature_slot(drawn, "Signer-1", STROKES)
    assert completed.startswith(drawn)
    slot = op.read_signature_slot(completed, "Signer-1")
    assert slot.completed and not slot.digitally_signed
    for operation in (lambda: op.remove_signature_slot(completed, "Signer-1"),
                      lambda: op.draw_signature_slot(completed, "Signer-1", STROKES)):
        with pytest.raises(op.PdfError):
            operation()
    assert op.PdfReader.from_bytes(completed).page_count == 1


@pytest.mark.parametrize("name,page,rect", [("bad name", 0, (1, 1, 10, 10)), ("ok", 99, (1, 1, 10, 10)), ("ok", 0, (1, 1, float("nan"), 10)), ("ok", 0, (1, 1, 9999, 10))])
def test_slot_invalid_inputs_fail(name, page, rect):
    with pytest.raises(op.PdfError):
        op.create_signature_slot(pdf_with_stream(TEXT), name, page, rect)


def test_slot_rejects_duplicate_identity_and_invalid_strokes(slot_pdf):
    _, prepared = slot_pdf
    with pytest.raises(op.PdfError):
        op.create_signature_slot(prepared, "Signer-1", 0, (50, 50, 250, 150))
    for strokes in ([], [[(0, 0)]], [[(0, 0), (2, 2)]], [[(0, 0), (float("nan"), 1)]]):
        with pytest.raises(op.PdfError):
            op.complete_signature_slot(prepared, "Signer-1", strokes)


def test_incomplete_recovery_retains_distinct_status():
    payload = zlib.compress(TEXT + b" " * 100)
    reader = op.PdfReader.from_bytes(pdf_with_stream(payload[:-7], filtered=True))
    result = reader.extract_page_text_with_recovery(0, max_stream_bytes=4096)
    assert result.text.text.strip() == "Recovery sample"
    diagnostic, = result.diagnostics
    assert diagnostic.kind == "incomplete" and diagnostic.action == "recovered"
    assert diagnostic.error


def test_signature_preparation_rejects_invalid_certification_policy():
    # A declared certification must not be ignored just because its target is bad.
    base = pdf_with_stream(TEXT, catalog=b"/Perms << /DocMDP 4 0 R >>")
    with pytest.raises(op.PdfError, match="signature|DocMDP|certification"):
        op.create_signature_slot(base, "Signer", 0, (50, 50, 250, 150))


def test_signature_preparation_rejects_encrypted_document():
    doc = op.Document()
    doc.add_page(op.Page.a4())
    doc.encrypt("reader", "owner")
    base = bytes(doc.save_to_bytes())
    with pytest.raises(op.PdfError):
        op.create_signature_slot(base, "Signer", 0, (50, 50, 250, 150))
