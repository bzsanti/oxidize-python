from oxidize_pdf import (
    PdfValue, SignatureTarget, CertificationPermission, FieldLock,
    SignaturePreparationOptions, SignatureWatermark, SignatureAppearance,
    PreparedSignature, prepare_incremental_signature,
)

def prepare(base: bytes) -> PreparedSignature:
    options = SignaturePreparationOptions(SignatureTarget.new_field('approval', rectangle=(10, 20, 300, 150)),
        certification=CertificationPermission.FormFillAndSign, field_lock=FieldLock.all(),
        additional_entries={'Profile': PdfValue.name('Bridge')})
    appearance = SignatureAppearance(text=['Approved'], watermark=SignatureWatermark(1, 1, b'abc'))
    result = prepare_incremental_signature(base, options, appearance)
    assert isinstance(result.prepared_pdf, bytes)
    assert isinstance(result.bytes_to_digest, bytes)
    for offset, length in result.byte_range:
        assert offset >= 0 and length >= 0
    return result
