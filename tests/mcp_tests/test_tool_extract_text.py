"""Tests for the extract_text MCP tool."""

import json

import pytest


class TestExtractTextAllPages:
    """F-016: extract_text returns text from all pages."""

    pytestmark = pytest.mark.asyncio

    async def test_extracts_text_from_all_pages(self, mcp_client, sample_pdf_with_text):
        result = await mcp_client.call_tool(
            "extract_text", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert "text" in out
        assert "Chapter 1" in out["text"]
        assert "Chapter 2" in out["text"]

    async def test_returns_page_count(self, mcp_client, sample_pdf_with_text):
        result = await mcp_client.call_tool(
            "extract_text", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert out["page_count"] == 2

    async def test_extracts_from_single_page_pdf(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool(
            "extract_text", {"path": str(sample_pdf)}
        )
        out = json.loads(result.content[0].text)
        assert "Hello from page 1" in out["text"]


class TestExtractTextSinglePage:
    """F-017: extract_text with page parameter extracts from a specific page."""

    pytestmark = pytest.mark.asyncio

    async def test_extracts_specific_page(self, mcp_client, sample_pdf_with_text):
        result = await mcp_client.call_tool(
            "extract_text", {"path": str(sample_pdf_with_text), "page": 0}
        )
        out = json.loads(result.content[0].text)
        assert "Chapter 1" in out["text"]
        assert "Chapter 2" not in out["text"]
        assert out["page"] == 0

    async def test_extracts_second_page(self, mcp_client, sample_pdf_with_text):
        result = await mcp_client.call_tool(
            "extract_text", {"path": str(sample_pdf_with_text), "page": 1}
        )
        out = json.loads(result.content[0].text)
        assert "Chapter 2" in out["text"]
        assert out["page"] == 1

    async def test_invalid_page_returns_error(self, mcp_client, sample_pdf_with_text):
        result = await mcp_client.call_tool(
            "extract_text", {"path": str(sample_pdf_with_text), "page": 999}
        )
        out = json.loads(result.content[0].text)
        assert "error" in out

    async def test_encrypted_with_password_extracts(self, mcp_client, encrypted_pdf):
        result = await mcp_client.call_tool(
            "extract_text", {"path": str(encrypted_pdf), "password": "userpass"}
        )
        out = json.loads(result.content[0].text)
        assert "text" in out
        assert "error" not in out


class _FakeReader:
    """Stand-in PdfReader whose heavy ops fail if invoked, to prove the gate
    runs first."""

    is_encrypted = False

    def __init__(self, page_count):
        self._page_count = page_count

    @property
    def page_count(self):
        return self._page_count

    def extract_text(self):
        raise AssertionError("extract_text must not run once the page cap is exceeded")

    def extract_text_from_page(self, index):
        raise AssertionError("extract_text_from_page must not run once the cap is exceeded")


def _fake_pdfreader(page_count):
    class _FakePdfReader:
        @staticmethod
        def open(path):
            return _FakeReader(page_count)

    return _FakePdfReader


class TestExtractTextPageCountCap:
    """#115 Capa B: extract_text rejects documents over the page-count cap."""

    pytestmark = pytest.mark.asyncio

    async def test_rejects_real_pdf_over_cap(self, mcp_client, sample_pdf, monkeypatch):
        monkeypatch.setenv("OXIDIZE_MAX_PAGES", "0")
        result = await mcp_client.call_tool(
            "extract_text", {"path": str(sample_pdf)}
        )
        out = json.loads(result.content[0].text)
        assert out["code"] == "RESOURCE_LIMIT"
        assert "page" in out["error"].lower()

    async def test_extraction_never_called_when_over_cap(
        self, mcp_client, sample_pdf, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_PAGES", "5")
        monkeypatch.setattr("oxidize_pdf.PdfReader", _fake_pdfreader(999))
        # _FakeReader.extract_text raises AssertionError; reaching it fails the test.
        result = await mcp_client.call_tool(
            "extract_text", {"path": str(sample_pdf)}
        )
        out = json.loads(result.content[0].text)
        assert out["code"] == "RESOURCE_LIMIT"


class TestExtractTextSecurity:
    """F-018: extract_text enforces path security."""

    pytestmark = pytest.mark.asyncio

    async def test_rejects_unsafe_path(self, mcp_client):
        result = await mcp_client.call_tool(
            "extract_text", {"path": "/etc/shadow"}
        )
        out = json.loads(result.content[0].text)
        assert "error" in out
        assert out.get("code") == "SECURITY_ERROR"

    async def test_rejects_traversal(self, mcp_client, mcp_workspace):
        result = await mcp_client.call_tool(
            "extract_text", {"path": str(mcp_workspace / ".." / ".." / "etc" / "passwd")}
        )
        out = json.loads(result.content[0].text)
        assert out.get("code") == "SECURITY_ERROR"


class TestExtractTextOutputCap:
    """#115 Capa B: extract_text bounds the serialized response size."""

    pytestmark = pytest.mark.asyncio

    async def test_rejects_when_output_exceeds_cap(
        self, mcp_client, sample_pdf_with_text, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_OUTPUT_BYTES", "10")
        result = await mcp_client.call_tool(
            "extract_text", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert out["code"] == "RESOURCE_LIMIT"
        assert "output" in out["error"].lower() or "size" in out["error"].lower()

    async def test_passes_when_output_within_cap(
        self, mcp_client, sample_pdf_with_text, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_OUTPUT_BYTES", str(10 * 1024 * 1024))
        result = await mcp_client.call_tool(
            "extract_text", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert "text" in out
        assert "error" not in out
