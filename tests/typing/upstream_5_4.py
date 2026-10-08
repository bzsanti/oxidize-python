"""Strict consumer contracts for the newly connected upstream APIs."""
from oxidize_pdf import (
    BuildIdentification, Document, ExtractionOptions, PdfReader,
    RecoveredText, SignatureSlot, TextRecoveryDiagnostic,
    create_signature_slot, read_signature_slot, list_signature_slots,
    draw_signature_slot, complete_signature_slot, remove_signature_slot,
)


def consume(data: bytes) -> None:
    doc = Document()
    doc.set_build_identification(BuildIdentification.Disabled)
    policy: BuildIdentification = doc.build_identification
    reader = PdfReader.from_bytes(data)
    version: str = reader.effective_version
    options = ExtractionOptions(normalize_non_breaking_spaces=True)
    result: RecoveredText = reader.extract_page_text_with_recovery(0, max_stream_bytes=4096, options=options)
    pages: list[RecoveredText] = reader.extract_text_with_recovery(max_stream_bytes=4096, options=options)
    diagnostics: list[TextRecoveryDiagnostic] = result.diagnostics
    for diagnostic in diagnostics:
        location: str = diagnostic.location
        object_id: tuple[int, int] | None = diagnostic.object_id
        error: str = diagnostic.error
    text: str = result.text.text
    prepared: bytes = create_signature_slot(data, "Signer", 0, (10, 10, 100, 100), metadata="Signer")
    slots: list[SignatureSlot] = list_signature_slots(prepared)
    slot: SignatureSlot = read_signature_slot(prepared, "Signer")
    rect: tuple[float, float, float, float] = slot.rect
    strokes: list[list[tuple[float, float]]] = [[(0, 0), (1, 1)]]
    drawn: bytes = draw_signature_slot(prepared, "Signer", strokes, label="Reviewed")
    completed: bytes = complete_signature_slot(drawn, "Signer", strokes)
    removed: bytes = remove_signature_slot(prepared, "Signer")
