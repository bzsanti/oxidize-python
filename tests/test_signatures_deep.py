"""Tests for F75 — Signatures Deep: verification types, trust store, certificate validation."""

import pytest
from oxidize_pdf import (
    PdfReader,
    # New F75 types
    DigestAlgorithm,
    SignatureAlgorithm,
    ByteRange,
    SignatureField,
    TrustStore,
    ParsedSignature,
    HashVerificationResult,
    SignatureVerificationResult,
    CertificateValidationResult,
    FullSignatureValidationResult,
    # New F75 functions
    compute_pdf_hash,
    parse_pkcs7_signature,
    verify_pdf_signature,
    validate_pdf_certificate,
    has_incremental_update,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════════════


class TestDigestAlgorithm:
    def test_sha256(self):
        assert DigestAlgorithm.SHA256 is not None

    def test_sha384(self):
        assert DigestAlgorithm.SHA384 is not None

    def test_sha512(self):
        assert DigestAlgorithm.SHA512 is not None

    def test_name(self):
        assert DigestAlgorithm.SHA256.name == "SHA-256"

    def test_oid(self):
        oid = DigestAlgorithm.SHA256.oid
        assert isinstance(oid, str)
        assert len(oid) > 0


class TestSignatureAlgorithm:
    def test_rsa_sha256(self):
        assert SignatureAlgorithm.RSA_SHA256 is not None

    def test_rsa_sha384(self):
        assert SignatureAlgorithm.RSA_SHA384 is not None

    def test_rsa_sha512(self):
        assert SignatureAlgorithm.RSA_SHA512 is not None

    def test_ecdsa_sha256(self):
        assert SignatureAlgorithm.ECDSA_SHA256 is not None

    def test_ecdsa_sha384(self):
        assert SignatureAlgorithm.ECDSA_SHA384 is not None

    def test_name(self):
        assert SignatureAlgorithm.RSA_SHA256.name == "RSA-SHA256"

    def test_digest_algorithm(self):
        da = SignatureAlgorithm.RSA_SHA256.digest_algorithm
        assert isinstance(da, DigestAlgorithm)


# ═══════════════════════════════════════════════════════════════════════════════
# ByteRange
# ═══════════════════════════════════════════════════════════════════════════════


class TestByteRange:
    def test_create(self):
        br = ByteRange([(0, 100), (200, 300)])
        assert br is not None

    def test_from_array(self):
        br = ByteRange.from_array([0, 100, 200, 300])
        assert br is not None

    def test_ranges(self):
        br = ByteRange([(0, 100), (200, 300)])
        ranges = br.ranges
        assert len(ranges) == 2
        assert ranges[0] == (0, 100)

    def test_total_bytes(self):
        br = ByteRange([(0, 100), (200, 300)])
        assert br.total_bytes == 400

    def test_len(self):
        br = ByteRange([(0, 100), (200, 300)])
        assert len(br) == 2

    def test_is_empty(self):
        br = ByteRange([])
        assert br.is_empty is True

    def test_not_empty(self):
        br = ByteRange([(0, 100)])
        assert br.is_empty is False

    def test_validate_valid(self):
        br = ByteRange([(0, 100), (200, 300)])
        assert br.validate() is True

    def test_repr(self):
        br = ByteRange([(0, 100)])
        assert "ByteRange" in repr(br)


# ═══════════════════════════════════════════════════════════════════════════════
# TrustStore
# ═══════════════════════════════════════════════════════════════════════════════


class TestTrustStore:
    def test_mozilla_roots(self):
        ts = TrustStore.mozilla_roots()
        assert ts is not None
        assert ts.root_count > 0
        assert ts.is_mozilla_bundle is True

    def test_empty(self):
        ts = TrustStore.empty()
        assert ts.root_count == 0
        assert ts.is_mozilla_bundle is False

    def test_repr(self):
        ts = TrustStore.mozilla_roots()
        assert "TrustStore" in repr(ts)


# ═══════════════════════════════════════════════════════════════════════════════
# SignatureField
# ═══════════════════════════════════════════════════════════════════════════════


class TestSignatureField:
    def test_create(self):
        br = ByteRange([(0, 100), (200, 300)])
        sf = SignatureField("adbe.pkcs7.detached", br, b"\x00" * 32)
        assert sf is not None

    def test_filter(self):
        br = ByteRange([(0, 100)])
        sf = SignatureField("adbe.pkcs7.detached", br, b"\x00" * 32)
        assert sf.filter == "adbe.pkcs7.detached"

    def test_is_pkcs7_detached(self):
        br = ByteRange([(0, 100)])
        sf = SignatureField("adbe.pkcs7.detached", br, b"\x00")
        # sub_filter not set — depends on implementation
        assert isinstance(sf.is_pkcs7_detached, bool)

    def test_is_pades(self):
        br = ByteRange([(0, 100)])
        sf = SignatureField("adbe.pkcs7.detached", br, b"\x00")
        assert isinstance(sf.is_pades, bool)

    def test_contents_size(self):
        br = ByteRange([(0, 100)])
        sf = SignatureField("adbe.pkcs7.detached", br, b"\x00" * 64)
        assert sf.contents_size == 64

    def test_repr(self):
        br = ByteRange([(0, 100)])
        sf = SignatureField("adbe.pkcs7.detached", br, b"\x00")
        assert "SignatureField" in repr(sf)


# ═══════════════════════════════════════════════════════════════════════════════
# Result Types (read-only wrappers, created from verification functions)
# ═══════════════════════════════════════════════════════════════════════════════


class TestHashVerificationResult:
    """HashVerificationResult is returned from compute_pdf_hash, not constructed directly."""

    def test_type_exists(self):
        assert HashVerificationResult is not None

    def test_has_expected_getters(self):
        expected = ["computed_hash", "algorithm", "bytes_hashed"]
        for attr in expected:
            assert hasattr(HashVerificationResult, attr) or attr in dir(HashVerificationResult), (
                f"HashVerificationResult missing expected getter: {attr}"
            )


class TestSignatureVerificationResult:
    """SignatureVerificationResult is returned from verify_pdf_signature."""

    def test_type_exists(self):
        assert SignatureVerificationResult is not None

    def test_has_expected_getters(self):
        expected = [
            "hash_valid", "signature_valid", "digest_algorithm",
            "signature_algorithm", "details",
        ]
        for attr in expected:
            assert hasattr(SignatureVerificationResult, attr) or attr in dir(SignatureVerificationResult), (
                f"SignatureVerificationResult missing expected getter: {attr}"
            )


class TestCertificateValidationResult:
    """CertificateValidationResult is returned from validate_pdf_certificate."""

    def test_type_exists(self):
        assert CertificateValidationResult is not None

    def test_has_expected_getters(self):
        expected = [
            "subject", "issuer", "valid_from", "valid_to",
            "is_time_valid", "is_trusted", "is_signature_capable", "warnings",
        ]
        for attr in expected:
            assert hasattr(CertificateValidationResult, attr) or attr in dir(CertificateValidationResult), (
                f"CertificateValidationResult missing expected getter: {attr}"
            )


class TestFullSignatureValidationResult:
    """FullSignatureValidationResult aggregates all validation results."""

    def test_type_exists(self):
        assert FullSignatureValidationResult is not None

    def test_has_expected_getters(self):
        expected = [
            "field", "signer_name", "signing_time", "hash_valid",
            "signature_valid", "certificate_result",
            "has_modifications_after_signing", "errors", "warnings",
        ]
        for attr in expected:
            assert hasattr(FullSignatureValidationResult, attr) or attr in dir(FullSignatureValidationResult), (
                f"FullSignatureValidationResult missing expected getter: {attr}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Standalone Functions (smoke tests — need real PDF with signatures for full test)
# ═══════════════════════════════════════════════════════════════════════════════


class TestComputePdfHash:
    def test_function_exists(self):
        assert callable(compute_pdf_hash)

    def test_with_empty_pdf_raises(self):
        br = ByteRange([(0, 10)])
        with pytest.raises(Exception):
            compute_pdf_hash(b"not a pdf", br, DigestAlgorithm.SHA256)


class TestParsePkcs7Signature:
    def test_function_exists(self):
        assert callable(parse_pkcs7_signature)

    def test_with_invalid_data_raises(self):
        with pytest.raises(Exception):
            parse_pkcs7_signature(b"not a pkcs7 signature")


class TestVerifyPdfSignature:
    def test_function_exists(self):
        assert callable(verify_pdf_signature)


class TestValidatePdfCertificate:
    def test_function_exists(self):
        assert callable(validate_pdf_certificate)

    def test_with_invalid_cert_raises(self):
        ts = TrustStore.empty()
        with pytest.raises(Exception):
            validate_pdf_certificate(b"not a certificate", ts)


class TestHasIncrementalUpdate:
    def test_function_exists(self):
        assert callable(has_incremental_update)

    def test_with_no_update(self):
        br = ByteRange([(0, 10)])
        result = has_incremental_update(b"short data", br)
        assert isinstance(result, bool)
