"""Published-core adoption: signed /Lock/P is independent of DocMDP."""
import pytest
import oxidize_pdf as pdf

# Structural CMS is sufficient for policy activation; authenticity has separate real-CMS tests.
CMS = bytes.fromhex('302306092a864886f70d010702a01630140201013100300b06092a864886f70d0107013100')


def field_pdf(permission):
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R /AcroForm << /Fields [4 0 R] >> >>',
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Annots [4 0 R] >>',
        (f'<< /Type /Annot /Subtype /Widget /FT /Sig /T (First) /P 3 0 R /Rect [0 0 0 0] '
         f'/Lock << /Type /SigFieldLock /P {permission} /Action /Include /Fields [(Unrelated)] >> >>').encode(),
    ]
    data = bytearray(b'%PDF-2.0\n')
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f'{number} 0 obj\n'.encode() + obj + b'\nendobj\n')
    xref = len(data)
    data.extend(b'xref\n0 5\n0000000000 65535 f \n')
    for offset in offsets[1:]:
        data.extend(f'{offset:010} 00000 n \n'.encode())
    data.extend(f'trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
    return bytes(data)


def sign_first(base):
    return bytes(pdf.prepare_incremental_signature(base, pdf.SignaturePreparationOptions(
        pdf.SignatureTarget.existing_field('First'))).finalize(CMS))


def second_options():
    return pdf.SignaturePreparationOptions(pdf.SignatureTarget.new_field('Second'))


def test_signed_p1_denies_second_signature_without_docmdp():
    signed = sign_first(field_pdf('1'))
    assert b'/DocMDP' not in signed
    with pytest.raises(pdf.PdfError, match='(?i)(permission|P1|changes|forbid|denied|sign)'):
        pdf.prepare_incremental_signature(signed, second_options())


@pytest.mark.parametrize('permission', ['2', '3'])
def test_p2_and_p3_allow_second_signature(permission):
    signed = sign_first(field_pdf(permission))
    prepared = pdf.prepare_incremental_signature(signed, second_options())
    assert bytes(prepared.prepared_pdf).startswith(signed)


def test_unsigned_p1_does_not_activate_policy():
    base = field_pdf('1')
    assert bytes(pdf.prepare_incremental_signature(base, second_options()).prepared_pdf).startswith(base)
