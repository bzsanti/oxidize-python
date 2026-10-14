"""Signature errors retain machine-readable variants across public entry points."""
import pickle

import pytest
import oxidize_pdf as pdf


def document():
    doc = pdf.Document()
    doc.add_page(pdf.Page.a4())
    return bytes(doc.save_to_bytes())


def test_preparation_and_slots_preserve_signature_errors():
    base = document()
    options = pdf.SignaturePreparationOptions(pdf.SignatureTarget.new_field('invalid', page_index=99))
    with pytest.raises(pdf.PdfError) as caught:
        pdf.prepare_incremental_signature(base, options)
    error = caught.value
    assert isinstance(error, pdf.PdfSignatureError)
    assert error.code == 'invalid_signature_dict'
    assert set(error.details) == {'details'}
    assert isinstance(error.details['details'], str)
    assert str(error) and error.args == (str(error),)
    with pytest.raises(pdf.PdfSignatureError) as slot:
        pdf.read_signature_slot(base, 'missing')
    assert slot.value.code == 'invalid_signature_dict'
    assert set(slot.value.details) == {'details'}


def test_cms_error_preserves_base_message_and_pickle():
    prepared = pdf.prepare_incremental_signature(document(), pdf.SignaturePreparationOptions(pdf.SignatureTarget.new_field('approval')))
    with pytest.raises(pdf.PdfSignatureError) as caught:
        prepared.finalize(b'not CMS')
    error = caught.value
    assert error.code == 'cms_parsing_failed'
    assert isinstance(error.details['details'], str)
    restored = pickle.loads(pickle.dumps(error))
    assert type(restored) is type(error)
    assert restored.code == error.code and restored.details == error.details
    assert str(restored) == str(error)
    assert len(prepared.finalize(bytes([0x30, 3, 2, 1, 1]))) == len(prepared.prepared_pdf)


def test_byterange_preserves_integer_details_and_legacy_valueerror():
    with pytest.raises(ValueError) as caught:
        pdf.compute_pdf_hash(b'1234', pdf.ByteRange([(2, 9)]), pdf.DigestAlgorithm.SHA256)
    error = caught.value
    assert isinstance(error, pdf.PdfSignatureError)
    assert error.code == 'byte_range_exceeds_document'
    assert error.details == {'offset': 2, 'length': 9, 'document_size': 4}
    assert all(type(value) is int for value in error.details.values())
    with pytest.raises(pdf.PdfSignatureError) as invalid:
        pdf.compute_pdf_hash(b'', pdf.ByteRange([(2**64 - 1, 1)]), pdf.DigestAlgorithm.SHA256)
    assert invalid.value.code == 'invalid_byte_range'
    assert set(invalid.value.details) == {'details'}


def test_legacy_runtimeerror_is_preserved():
    with pytest.raises(RuntimeError) as caught:
        pdf.parse_pkcs7_signature(b'not DER CMS')
    assert isinstance(caught.value, pdf.PdfSignatureError)
    assert caught.value.code == 'cms_parsing_failed'
    assert set(caught.value.details) == {'details'}


@pytest.mark.parametrize('signed_attributes', [False, True])
def test_aggregate_verification_rejects_invalid_crypto(signed_attributes):
    from datetime import datetime, timedelta, timezone
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.serialization import pkcs7
    from cryptography.x509.oid import NameOID

    prepared = pdf.prepare_incremental_signature(document(), pdf.SignaturePreparationOptions(pdf.SignatureTarget.new_field('approval')))
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Error contract test')])
    now = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(2).not_valid_before(now - timedelta(minutes=1))
            .not_valid_after(now + timedelta(days=1)).sign(key, hashes.SHA256()))
    options = [pkcs7.PKCS7Options.DetachedSignature, pkcs7.PKCS7Options.Binary]
    if not signed_attributes:
        options.append(pkcs7.PKCS7Options.NoAttributes)
    cms = (pkcs7.PKCS7SignatureBuilder().set_data(prepared.bytes_to_digest).add_signer(cert, key, hashes.SHA256())
           .sign(serialization.Encoding.DER, options))
    valid = pdf.verify_pdf_signatures(prepared.finalize(cms))[0]
    assert valid['valid'] is True
    # Flip a bit in the RSA signature, inside /Contents and outside ByteRange.
    # Preserve DER structure and signed document bytes.
    invalid_cms = cms[:-1] + bytes([cms[-1] ^ 1])
    invalid = pdf.verify_pdf_signatures(prepared.finalize(invalid_cms))[0]
    assert invalid['valid'] is False
    assert invalid['error_code'] == 'signature_verification_failed'
    assert isinstance(invalid['error_details']['details'], str)
    assert invalid['error']
    assert valid['error'] is None
    assert valid['error_code'] is None and valid['error_details'] is None
    # Change a covered byte while retaining a parseable PDF header.
    modified = bytearray(prepared.finalize(cms))
    assert modified.startswith(b'%PDF-1.')
    modified[7] = ord('6') if modified[7] != ord('6') else ord('7')
    changed_document = pdf.verify_pdf_signatures(bytes(modified))[0]
    assert changed_document['valid'] is False
    expected = 'hash_verification_failed' if signed_attributes else 'signature_verification_failed'
    assert changed_document['error_code'] == expected


def test_aggregate_cms_parse_error_retains_details():
    prepared = pdf.prepare_incremental_signature(document(), pdf.SignaturePreparationOptions(pdf.SignatureTarget.new_field('approval')))
    result = pdf.verify_pdf_signatures(prepared.finalize(bytes([0x30, 3, 2, 1, 1])))[0]
    assert result['valid'] is False
    assert result['error_code'] == 'cms_parsing_failed'
    assert isinstance(result['error_details']['details'], str)
    assert result['error']


def test_standalone_detection_preserves_missing_field():
    prepared = pdf.prepare_incremental_signature(document(), pdf.SignaturePreparationOptions(pdf.SignatureTarget.new_field('approval')))
    malformed = prepared.prepared_pdf.replace(b'/ByteRange', b'/ByteRonge')
    assert malformed != prepared.prepared_pdf
    with pytest.raises(pdf.PdfSignatureError) as caught:
        pdf.verify_pdf_signatures(malformed)
    assert caught.value.code == 'missing_field'
    assert caught.value.details == {'field': 'ByteRange'}
