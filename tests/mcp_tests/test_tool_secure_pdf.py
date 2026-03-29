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
