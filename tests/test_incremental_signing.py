"""External signing must preserve exact digest coverage and original revisions."""
from datetime import datetime, timedelta, timezone
import re
import shutil
import subprocess
import sys
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.x509.oid import NameOID
import oxidize_pdf as pdf


def document():
    doc = pdf.Document()
    doc.add_page(pdf.Page.a4())
    return bytes(doc.save_to_bytes())


def covered(data, ranges):
    return b''.join(data[offset:offset + length] for offset, length in ranges)


def test_external_cms_exact_coverage_and_independent_verification(tmp_path):
    base = document()
    prepared = pdf.prepare_incremental_signature(base, pdf.SignaturePreparationOptions(pdf.SignatureTarget.new_field('approval')))
    assert prepared.prepared_pdf.startswith(base)
    assert prepared.bytes_to_digest == covered(prepared.prepared_pdf, prepared.byte_range)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Bridge test')])
    now = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(1).not_valid_before(now - timedelta(minutes=1)).not_valid_after(now + timedelta(days=1)).sign(key, hashes.SHA256()))
    cms = (pkcs7.PKCS7SignatureBuilder().set_data(prepared.bytes_to_digest).add_signer(cert, key, hashes.SHA256())
           .sign(serialization.Encoding.DER, [pkcs7.PKCS7Options.DetachedSignature, pkcs7.PKCS7Options.Binary]))
    result = prepared.finalize(cms)
    assert result.startswith(base)
    assert len(result) == len(prepared.prepared_pdf)
    assert covered(result, prepared.byte_range) == prepared.bytes_to_digest
    gap = sum(prepared.byte_range[0])
    embedded = bytes.fromhex(result[gap + 1:gap + 1 + len(cms) * 2].decode('ascii'))
    assert embedded == cms
    assert result == prepared.finalize(cms)
    # OpenSSL independently verifies the *embedded* CMS against final PDF bytes.
    # Linux CI requires this; other platforms still exercise real CMS creation/embedding.
    if sys.platform.startswith('linux'):
        openssl = shutil.which('openssl')
        assert openssl, 'Linux signing acceptance requires OpenSSL'
        (tmp_path / 'cms.der').write_bytes(embedded)
        (tmp_path / 'content.bin').write_bytes(covered(result, prepared.byte_range))
        checked = subprocess.run([openssl, 'cms', '-verify', '-binary', '-inform', 'DER', '-in', str(tmp_path / 'cms.der'),
                                  '-content', str(tmp_path / 'content.bin'), '-noverify', '-out', str(tmp_path / 'verified.bin')], capture_output=True)
        assert checked.returncode == 0, checked.stderr.decode()
        assert (tmp_path / 'verified.bin').read_bytes() == prepared.bytes_to_digest


def test_invalid_cms_can_be_retried_without_mutating_preparation():
    prepared = pdf.prepare_incremental_signature(document(), pdf.SignaturePreparationOptions(pdf.SignatureTarget.new_field('approval')))
    original = prepared.prepared_pdf
    with pytest.raises(pdf.PdfError):
        prepared.finalize(b'not DER CMS')
    assert prepared.prepared_pdf == original
    # Structural fixture, not a cryptographic authenticity assertion.
    assert len(prepared.finalize(bytes([0x30, 3, 2, 1, 1]))) == len(original)
    assert prepared.prepared_pdf == original


def test_existing_slot_appearance_and_full_option_dictionary():
    base = pdf.create_signature_slot(document(), 'approval', 0, (10, 20, 300, 150))
    appearance = pdf.SignatureAppearance(signer_name='Signer', signing_date='2026-10-11', text=['Approved'],
                                        watermark=pdf.SignatureWatermark(1, 1, bytes([20, 40, 80]), opacity=0.25))
    layout = appearance.layout((10, 20, 300, 150))
    assert 'Approved' in layout.lines
    assert 6 <= layout.font_size <= 12
    assert layout.margin > 0 and layout.line_height > 0 and layout.first_baseline > 0
    options = pdf.SignaturePreparationOptions(pdf.SignatureTarget.existing_field('approval', rectangle=(10, 20, 300, 150)),
        placeholder_bytes=2048, filter='Adobe.PPKLite', sub_filter='adbe.pkcs7.detached', reason='Reviewed', location='Madrid',
        contact_info='Tester', signing_time='D:20261011000000Z', certification=pdf.CertificationPermission.FormFillAndSign,
        field_lock=pdf.FieldLock.all(), additional_entries={'Profile': pdf.PdfValue.name('Bridge'), 'Review': pdf.PdfValue.dictionary({'Count': pdf.PdfValue.integer(2)})})
    prepared = pdf.prepare_incremental_signature(base, options, appearance)
    raw = prepared.prepared_pdf
    assert raw.startswith(base)
    for expected in [b'/Subtype /Image', b'/DocMDP', b'/FieldMDP', b'/P 2', b'/Profile /Bridge', b'/Count 2', b'/Reason']:
        assert expected in raw
    for key, expected in [('Reason', b'Reviewed'), ('Location', b'Madrid'), ('ContactInfo', b'Tester'), ('M', b'D:20261011000000Z')]:
        encoded = re.findall(rb'/' + key.encode() + rb'\s+<([0-9A-Fa-f]*)>', raw)[-1]
        assert bytes.fromhex(encoded.decode()) == expected
    assert prepared.byte_range[1][0] - sum(prepared.byte_range[0]) == 2048 * 2 + 2


@pytest.mark.parametrize('options', [
    lambda: pdf.SignaturePreparationOptions(pdf.SignatureTarget.new_field('bad', page_index=1)),
    lambda: pdf.SignaturePreparationOptions(pdf.SignatureTarget.existing_field('absent')),
    lambda: pdf.SignaturePreparationOptions(pdf.SignatureTarget.new_field('bad'), additional_entries={'Contents': pdf.PdfValue.string(b'override')}),
])
def test_invalid_targets_and_reserved_entries_are_rejected(options):
    with pytest.raises(pdf.PdfError):
        pdf.prepare_incremental_signature(document(), options())


def test_appearance_rejects_invalid_geometry_and_watermark():
    with pytest.raises(pdf.PdfError):
        pdf.SignatureAppearance(text=['Will not fit']).layout((0, 0, 1, 1))
    with pytest.raises(pdf.PdfError):
        pdf.prepare_incremental_signature(document(), pdf.SignaturePreparationOptions(pdf.SignatureTarget.new_field('bad', rectangle=(10, 20, 300, 150))),
            pdf.SignatureAppearance(watermark=pdf.SignatureWatermark(1, 1, b'bad-size')))


@pytest.mark.parametrize('permission,number', [
    (pdf.CertificationPermission.NoChanges, 1),
    (pdf.CertificationPermission.FormFillAndSign, 2),
    (pdf.CertificationPermission.FormFillSignAndAnnotate, 3),
])
@pytest.mark.parametrize('lock,action', [(pdf.FieldLock.include(['approval']), b'Include'), (pdf.FieldLock.exclude(['approval']), b'Exclude')])
def test_certification_lock_and_handler_options(permission, number, lock, action):
    options = pdf.SignaturePreparationOptions(pdf.SignatureTarget.new_field('approval'),
        certification=permission, field_lock=lock, filter='Custom.Handler', sub_filter='ETSI.CAdES.detached')
    raw = pdf.prepare_incremental_signature(document(), options).prepared_pdf
    assert b'/P ' + str(number).encode() in raw
    assert b'/Action /' + action in raw
    arrays = re.findall(rb'/Fields\s+\[([^\]]*)\]', raw)
    decoded = [[bytes.fromhex(v.decode()) for v in re.findall(rb'<([0-9A-Fa-f]+)>', array)] for array in arrays]
    assert [b'approval'] in decoded
    assert b'/Filter /Custom.Handler' in raw
    assert b'/SubFilter /ETSI.CAdES.detached' in raw


def test_widget_selection_is_not_silently_ignored():
    base = pdf.create_signature_slot(document(), 'approval', 0, (10, 20, 300, 150))
    with pytest.raises(pdf.PdfError):
        pdf.prepare_incremental_signature(base, pdf.SignaturePreparationOptions(
            pdf.SignatureTarget.existing_field('approval', widget_index=999)))
