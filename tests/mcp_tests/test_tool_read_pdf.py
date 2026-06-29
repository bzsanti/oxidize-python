"""Tests for the read_pdf MCP tool."""

import json

import pytest


class TestReadPdfMetadata:
    """F-013: read_pdf returns correct metadata from a PDF."""

    pytestmark = pytest.mark.asyncio

    async def test_returns_page_count(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool("read_pdf", {"path": str(sample_pdf)})
        out = json.loads(result.content[0].text)
        assert out["page_count"] == 1

    async def test_returns_version(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool("read_pdf", {"path": str(sample_pdf)})
        out = json.loads(result.content[0].text)
        assert out["version"] == "1.7"

    async def test_returns_encryption_status(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool("read_pdf", {"path": str(sample_pdf)})
        out = json.loads(result.content[0].text)
        assert out["is_encrypted"] is False

    async def test_returns_title_and_author(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool("read_pdf", {"path": str(sample_pdf)})
        out = json.loads(result.content[0].text)
        assert out["title"] == "Test Document"
        assert out["author"] == "Test Author"

    async def test_returns_path(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool("read_pdf", {"path": str(sample_pdf)})
        out = json.loads(result.content[0].text)
        assert out["path"] == str(sample_pdf)

    async def test_missing_file_returns_error(self, mcp_client, mcp_workspace):
        result = await mcp_client.call_tool(
            "read_pdf", {"path": str(mcp_workspace / "nonexistent.pdf")}
        )
        out = json.loads(result.content[0].text)
        assert "error" in out
        assert out.get("code") == "SECURITY_ERROR"

    async def test_multipage_pdf_returns_correct_count(
        self, mcp_client, sample_pdf_with_text
    ):
        result = await mcp_client.call_tool(
            "read_pdf", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert out["page_count"] == 2


class TestReadPdfPageDetails:
    """F-013: read_pdf with include_page_details returns per-page info."""

    pytestmark = pytest.mark.asyncio

    async def test_page_details_included_when_requested(
        self, mcp_client, sample_pdf
    ):
        result = await mcp_client.call_tool(
            "read_pdf", {"path": str(sample_pdf), "include_page_details": True}
        )
        out = json.loads(result.content[0].text)
        assert "pages" in out
        assert len(out["pages"]) == 1
        page = out["pages"][0]
        assert page["index"] == 0
        assert page["width"] > 0
        assert page["height"] > 0

    async def test_page_details_omitted_by_default(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool("read_pdf", {"path": str(sample_pdf)})
        out = json.loads(result.content[0].text)
        assert out.get("pages") is None


class TestReadPdfEncrypted:
    """F-014: read_pdf handles encrypted PDFs."""

    pytestmark = pytest.mark.asyncio

    async def test_encrypted_without_password_shows_encrypted(
        self, mcp_client, encrypted_pdf
    ):
        result = await mcp_client.call_tool(
            "read_pdf", {"path": str(encrypted_pdf)}
        )
        out = json.loads(result.content[0].text)
        assert out["is_encrypted"] is True

    async def test_encrypted_with_correct_password(
        self, mcp_client, encrypted_pdf
    ):
        result = await mcp_client.call_tool(
            "read_pdf", {"path": str(encrypted_pdf), "password": "userpass"}
        )
        out = json.loads(result.content[0].text)
        assert out["page_count"] == 1
        assert "error" not in out


class TestReadPdfSecurity:
    """F-015: read_pdf enforces path security."""

    pytestmark = pytest.mark.asyncio

    async def test_rejects_path_outside_workspace(self, mcp_client):
        result = await mcp_client.call_tool(
            "read_pdf", {"path": "/etc/passwd"}
        )
        out = json.loads(result.content[0].text)
        assert "error" in out
        assert out.get("code") == "SECURITY_ERROR"

    async def test_rejects_path_traversal(self, mcp_client, mcp_workspace):
        result = await mcp_client.call_tool(
            "read_pdf", {"path": str(mcp_workspace / ".." / ".." / "etc" / "passwd")}
        )
        out = json.loads(result.content[0].text)
        assert "error" in out
        assert out.get("code") == "SECURITY_ERROR"

    async def test_response_uses_client_path_not_resolved(
        self, mcp_client, sample_pdf
    ):
        """The response must use the client-provided path, not leak an internal resolved path."""
        client_path = str(sample_pdf)
        result = await mcp_client.call_tool("read_pdf", {"path": client_path})
        out = json.loads(result.content[0].text)
        assert out["path"] == client_path


class TestReadPdfPageCountCap:
    """#115 Capa B: read_pdf rejects documents over the page-count cap."""

    pytestmark = pytest.mark.asyncio

    async def test_rejects_real_pdf_over_cap(self, mcp_client, sample_pdf, monkeypatch):
        monkeypatch.setenv("OXIDIZE_MAX_PAGES", "0")
        result = await mcp_client.call_tool("read_pdf", {"path": str(sample_pdf)})
        out = json.loads(result.content[0].text)
        assert out["code"] == "RESOURCE_LIMIT"
        assert "page" in out["error"].lower()


class TestReadPdfOutputCap:
    """#115 Capa B: read_pdf bounds the serialized response size."""

    pytestmark = pytest.mark.asyncio

    async def test_rejects_when_output_exceeds_cap(
        self, mcp_client, sample_pdf, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_OUTPUT_BYTES", "10")
        result = await mcp_client.call_tool("read_pdf", {"path": str(sample_pdf)})
        out = json.loads(result.content[0].text)
        assert out["code"] == "RESOURCE_LIMIT"

    async def test_passes_when_output_within_cap(
        self, mcp_client, sample_pdf, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_OUTPUT_BYTES", str(10 * 1024 * 1024))
        result = await mcp_client.call_tool("read_pdf", {"path": str(sample_pdf)})
        out = json.loads(result.content[0].text)
        assert out["page_count"] == 1
        assert "error" not in out
