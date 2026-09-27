"""Public binding checks using external certificate and CMS fixtures."""
from pathlib import Path

import pytest
from oxidize_pdf import TrustStore, parse_pkcs7_signature, validate_pdf_certificate

FIXTURES = Path(__file__).parent / "fixtures" / "certificates_627"


@pytest.mark.parametrize("store", [TrustStore.empty, TrustStore.mozilla_roots])
def test_external_root_is_not_implicitly_trusted(store):
    result = validate_pdf_certificate((FIXTURES / "cms_root.der").read_bytes(), store())
    assert not result.is_trusted
    assert not result.is_valid()
    assert result.subject == "oxidize-pdf fixture root"


@pytest.mark.parametrize("filename,algorithm,subject", [
    ("cms_rsa_sha256.der", "RSA-SHA256", "oxidize-pdf RSA fixture"),
    ("cms_ecdsa_sha256.der", "ECDSA-SHA256", "oxidize-pdf ECDSA fixture"),
])
def test_external_signed_cms_retains_signer_identity(filename, algorithm, subject):
    parsed = parse_pkcs7_signature((FIXTURES / filename).read_bytes())
    assert parsed.signature_algorithm.name == algorithm
    assert parsed.digest_algorithm.name == "SHA-256"
    certificate = validate_pdf_certificate(bytes(parsed.signer_certificate_der), TrustStore.empty())
    assert certificate.subject == subject
    assert not certificate.is_trusted


def test_malformed_certificate_does_not_succeed():
    with pytest.raises(RuntimeError, match="[Cc]ertificate"):
        validate_pdf_certificate(b"not DER", TrustStore.empty())
