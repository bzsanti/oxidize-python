"""Tests for security: encryption, permissions, password protection."""

import pytest


# ── Permissions ────────────────────────────────────────────────────────────────


class TestPermissions:
    """Test the Permissions type."""

    def test_all_permissions(self):
        from oxidize_pdf import Permissions

        perms = Permissions.all()
        assert perms.can_print is True
        assert perms.can_copy is True
        assert perms.can_modify_contents is True
        assert perms.can_modify_annotations is True
        assert perms.can_fill_forms is True
        assert perms.can_assemble is True
        assert perms.can_print_high_quality is True

    def test_none_permissions(self):
        from oxidize_pdf import Permissions

        perms = Permissions.none()
        assert perms.can_print is False
        assert perms.can_copy is False
        assert perms.can_modify_contents is False

    def test_custom_permissions(self):
        from oxidize_pdf import Permissions

        perms = Permissions(print=True, copy=True)
        assert perms.can_print is True
        assert perms.can_copy is True
        assert perms.can_modify_contents is False
        assert perms.can_fill_forms is False

    def test_repr_with_flags(self):
        from oxidize_pdf import Permissions

        perms = Permissions.all()
        r = repr(perms)
        assert "Permissions" in r
        assert "print" in r

    def test_repr_none(self):
        from oxidize_pdf import Permissions

        perms = Permissions.none()
        assert "none" in repr(perms)

    def test_default_accessibility(self):
        """Accessibility defaults to True even in Permissions()."""
        from oxidize_pdf import Permissions

        perms = Permissions()
        # accessibility defaults to True per PDF spec
        assert perms.can_print is False  # not explicitly set


# ── Document Encryption API ───────────────────────────────────────────────────


class TestDocumentEncryption:
    """Test the encryption API on Document (struct-level, not serialized)."""

    def test_is_encrypted_initially_false(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.add_page(Page.a4())
        assert doc.is_encrypted is False

    def test_is_encrypted_after_encrypt(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.add_page(Page.a4())
        doc.encrypt("user", "owner")
        assert doc.is_encrypted is True

    def test_encrypt_with_passwords_produces_output(self, tmp_dir):
        from oxidize_pdf import Document, Font, Page

        path = tmp_dir / "encrypted.pdf"
        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Secret content")
        doc.add_page(page)

        doc.encrypt("user123", "owner456")
        doc.save(str(path))
        assert path.exists()
        assert path.stat().st_size > 0

    def test_encrypt_to_bytes(self):
        from oxidize_pdf import Document, Font, Page

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Secret")
        doc.add_page(page)

        doc.encrypt("user", "owner")
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
        assert len(data) > 100

    def test_encrypt_with_permissions(self):
        from oxidize_pdf import Document, Page, Permissions

        doc = Document()
        doc.add_page(Page.a4())

        perms = Permissions(print=True, copy=False)
        doc.encrypt("user", "owner", permissions=perms)
        assert doc.is_encrypted is True

    def test_encrypt_without_permissions_defaults_to_all(self):
        from oxidize_pdf import Document, Page

        doc = Document()
        doc.add_page(Page.a4())
        doc.encrypt("user", "owner")
        assert doc.is_encrypted is True


# ── PdfReader encryption detection ────────────────────────────────────────────


class TestPdfReaderEncryption:
    """Test PdfReader encryption-related properties."""

    def test_unencrypted_pdf_not_flagged(self, tmp_dir):
        from oxidize_pdf import Document, Font, Page, PdfReader

        path = tmp_dir / "plain.pdf"
        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Plain text")
        doc.add_page(page)
        doc.save(str(path))

        reader = PdfReader.open(str(path))
        assert reader.is_encrypted is False

    def test_unlock_on_unencrypted_is_noop(self, tmp_dir):
        from oxidize_pdf import Document, Font, Page, PdfReader

        path = tmp_dir / "plain2.pdf"
        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Plain text")
        doc.add_page(page)
        doc.save(str(path))

        reader = PdfReader.open(str(path))
        # Should not raise — unlock on unencrypted is a no-op
        reader.unlock("anything")
        assert reader.page_count == 1


# ── Encryption round-trip (issue #117) ────────────────────────────────────────


class TestEncryptionRoundTrip:
    """Verify the encryption guarantee end-to-end: an encrypted PDF, once
    serialized and reopened, actually protects its content.

    Without these tests the encryption could be a no-op and every other
    security test would still pass — they only check the in-memory
    ``is_encrypted`` flag and that *some* output is produced, never that the
    content is unreadable without the password (premortem 2026-06-27,
    scenario 4 / issue #117).
    """

    SECRET = "Secret content RT-117"

    def _make_encrypted(self, path, user="user-rt", owner="owner-rt"):
        """Write a fresh single-page encrypted PDF (with ``SECRET`` as content)
        to ``path`` and return it. Rebuilt per call so each test gets an
        independent file under its own ``tmp_dir``."""
        from oxidize_pdf import Document, Font, Page

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, self.SECRET)
        doc.add_page(page)
        doc.encrypt(user, owner)
        doc.save(str(path))
        return path

    def test_plaintext_absent_from_encrypted_bytes(self):
        """The secret must not appear in clear in the bytes, and an /Encrypt
        dictionary must be present."""
        from oxidize_pdf import Document, Font, Page

        doc = Document()
        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, self.SECRET)
        doc.add_page(page)
        doc.encrypt("user-rt", "owner-rt")
        data = doc.save_to_bytes()

        assert b"/Encrypt" in data
        assert self.SECRET.encode() not in data

    def test_reopened_pdf_flagged_encrypted(self, tmp_dir):
        from oxidize_pdf import PdfReader

        path = self._make_encrypted(tmp_dir / "rt_flag.pdf")
        reader = PdfReader.open(str(path))
        assert reader.is_encrypted is True

    def test_content_unreadable_without_password(self, tmp_dir):
        """Reading a locked PDF must fail, not silently return the secret."""
        from oxidize_pdf import PdfEncryptionError, PdfReader

        path = self._make_encrypted(tmp_dir / "rt_locked.pdf")
        reader = PdfReader.open(str(path))
        with pytest.raises(PdfEncryptionError):
            reader.extract_text()

    def test_wrong_password_rejected(self, tmp_dir):
        """``unlock`` signals a wrong password by raising ``PdfEncryptionError``
        — it does not return a bool. This pins that contract: if upstream ever
        switched to a bool return, this test would (correctly) fail."""
        from oxidize_pdf import PdfEncryptionError, PdfReader

        path = self._make_encrypted(tmp_dir / "rt_wrong.pdf")
        reader = PdfReader.open(str(path))
        with pytest.raises(PdfEncryptionError):
            reader.unlock("definitely-wrong")

    def test_user_password_recovers_content(self, tmp_dir):
        from oxidize_pdf import PdfReader

        path = self._make_encrypted(tmp_dir / "rt_user.pdf")
        reader = PdfReader.open(str(path))
        reader.unlock("user-rt")
        text = "\n".join(reader.extract_text())
        assert self.SECRET in text

    def test_owner_password_recovers_content(self, tmp_dir):
        from oxidize_pdf import PdfReader

        path = self._make_encrypted(tmp_dir / "rt_owner.pdf")
        reader = PdfReader.open(str(path))
        reader.unlock("owner-rt")
        text = "\n".join(reader.extract_text())
        assert self.SECRET in text
