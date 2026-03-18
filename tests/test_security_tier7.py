"""Tests for Tier 7 — Advanced Security (Features 27-29)."""

import pytest


# ── Feature 27: AES-256 Encryption ────────────────────────────────────────


class TestEncryptionStrength:
    def test_encryption_strength_variants(self):
        from oxidize_pdf import EncryptionStrength

        assert EncryptionStrength.RC4_40 is not None
        assert EncryptionStrength.RC4_128 is not None
        assert EncryptionStrength.AES_128 is not None
        assert EncryptionStrength.AES_256 is not None

    def test_encrypt_aes256(self):
        from oxidize_pdf import Document, EncryptionStrength, Font, Page

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Secret content")
        doc.add_page(page)

        doc.encrypt("user123", "owner456", strength=EncryptionStrength.AES_256)
        assert doc.is_encrypted

        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
        assert len(data) > 100

    def test_encrypt_aes128(self):
        from oxidize_pdf import Document, EncryptionStrength, Page

        doc = Document()
        doc.add_page(Page.a4())
        doc.encrypt("u", "o", strength=EncryptionStrength.AES_128)
        assert doc.is_encrypted

        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_encrypt_default_remains_rc4_128(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.add_page(Page.a4())
        doc.encrypt("u", "o")
        assert doc.is_encrypted

        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


# ── Feature 28: Digital Signatures (detection) ────────────────────────────


class TestSignatureDetection:
    def test_detect_signatures_unsigned(self, tmp_dir):
        from oxidize_pdf import Document, Font, Page, PdfReader

        path = tmp_dir / "unsigned.pdf"
        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 700.0, "Unsigned document")
        doc.add_page(page)
        doc.save(str(path))

        reader = PdfReader.open(str(path))
        sigs = reader.detect_signatures()
        assert isinstance(sigs, list)
        assert len(sigs) == 0


# ── Feature 29: Public Key Encryption (type exposure) ─────────────────────


class TestRecipient:
    def test_recipient_from_certificate_invalid(self):
        from oxidize_pdf import PdfError, Recipient

        with pytest.raises((PdfError, ValueError)):
            Recipient.from_certificate(b"not a valid certificate")
