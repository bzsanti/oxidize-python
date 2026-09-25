"""Tests for the secure_pdf MCP tool."""

import json

import pytest


class TestSecurePdfEncrypt:
    """F-035: secure_pdf encrypt operation."""

    pytestmark = pytest.mark.asyncio

    async def test_encrypt_creates_encrypted_pdf(
        self, mcp_client, sample_pdf, mcp_workspace
    ):
        from oxidize_pdf import PdfReader

        out = mcp_workspace / "secure.pdf"
        result = await mcp_client.call_tool(
            "secure_pdf",
            {
                "operation": "encrypt",
                "input_path": str(sample_pdf),
                "output_path": str(out),
                "user_password": "user123",
                "owner_password": "owner123",
            },
        )
        resp = json.loads(result.content[0].text)
        assert resp.get("status") == "ok"
        assert out.exists()
        reader = PdfReader.open(str(out))
        assert reader.is_encrypted


class TestSecurePdfPermissions:
    """F-036: secure_pdf permissions operation."""

    pytestmark = pytest.mark.asyncio

    async def test_check_permissions(self, mcp_client, encrypted_pdf):
        result = await mcp_client.call_tool(
            "secure_pdf",
            {
                "operation": "permissions",
                "input_path": str(encrypted_pdf),
                "password": "userpass",
            },
        )
        resp = json.loads(result.content[0].text)
        assert "permissions" in resp


class TestSecurePdfVerifySignatures:
    """F-036: secure_pdf verify_signatures operation."""

    pytestmark = pytest.mark.asyncio

    async def test_verify_signatures(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool(
            "secure_pdf",
            {"operation": "verify_signatures", "input_path": str(sample_pdf)},
        )
        resp = json.loads(result.content[0].text)
        assert "signatures" in resp


@pytest.mark.asyncio
async def test_encrypt_text_without_font_name(mcp_client, sample_pdf, mcp_workspace, monkeypatch):
    """Extraction permits a missing font name; encryption still preserves text."""
    from types import SimpleNamespace
    import oxidize_pdf

    real_reader = oxidize_pdf.PdfReader

    class ReaderWithoutFont:
        page_count = 1

        def metadata(self):
            return SimpleNamespace(title="Missing font", author=None)

        def get_page(self, index):
            return SimpleNamespace(width=595.28, height=841.89)

        @staticmethod
        def extract_text_chunks(index):
            return [SimpleNamespace(font_name=None, font_size=12.0, x=50.0, y=700.0, text="Unnamed font")]

    monkeypatch.setattr(oxidize_pdf, "PdfReader", SimpleNamespace(open=lambda path: ReaderWithoutFont()))
    out = mcp_workspace / "unnamed-font.pdf"
    result = await mcp_client.call_tool("secure_pdf", {
        "operation": "encrypt", "input_path": str(sample_pdf), "output_path": str(out),
        "user_password": "user", "owner_password": "owner",
    })
    assert json.loads(result.content[0].text).get("status") == "ok"
    saved = real_reader.open(str(out))
    saved.unlock("user")
    assert "Unnamed font" in "\n".join(saved.extract_text())
