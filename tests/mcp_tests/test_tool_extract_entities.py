"""Tests for the extract_entities MCP tool."""

import json

import pytest


class TestExtractEntities:
    """F-024: extract_entities tool."""

    pytestmark = pytest.mark.asyncio

    async def test_extract_entities_returns_real_content(
        self, mcp_client, sample_pdf_with_text
    ):
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert "entities" in out
        assert isinstance(out["entities"], list)
        assert len(out["entities"]) > 0, "Should extract real entities from PDF with text"

        entity = out["entities"][0]
        assert "text" in entity
        assert "page" in entity
        assert "x" in entity
        assert "y" in entity
        assert "font_size" in entity
        assert isinstance(entity["text"], str)
        assert len(entity["text"]) > 0

    async def test_extract_entities_page_count_matches(
        self, mcp_client, sample_pdf_with_text
    ):
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert out["page_count"] == 2
        assert out["entity_count"] == len(out["entities"])

    async def test_extract_entities_contains_known_text(
        self, mcp_client, sample_pdf_with_text
    ):
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        all_text = " ".join(e["text"] for e in out["entities"])
        assert "Chapter 1" in all_text
        assert "Chapter 2" in all_text

    async def test_extract_entities_returns_path(
        self, mcp_client, sample_pdf_with_text
    ):
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert out["path"] == str(sample_pdf_with_text)

    async def test_extract_entities_rejects_unsafe_path(self, mcp_client):
        result = await mcp_client.call_tool(
            "extract_entities", {"path": "/etc/passwd"}
        )
        out = json.loads(result.content[0].text)
        assert out.get("code") == "SECURITY_ERROR"


class _FakeEntitiesReader:
    is_encrypted = False

    def __init__(self, page_count):
        self._page_count = page_count

    @property
    def page_count(self):
        return self._page_count

    def extract_text_chunks(self, index):
        raise AssertionError("extract_text_chunks must not run once the cap is exceeded")


def _fake_pdfreader(page_count):
    class _FakePdfReader:
        @staticmethod
        def open(path):
            return _FakeEntitiesReader(page_count)

    return _FakePdfReader


class TestExtractEntitiesPageCountCap:
    """#115 Capa B: extract_entities rejects documents over the page-count cap."""

    pytestmark = pytest.mark.asyncio

    async def test_rejects_real_pdf_over_cap(
        self, mcp_client, sample_pdf_with_text, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_PAGES", "0")
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert out["code"] == "RESOURCE_LIMIT"
        assert "page" in out["error"].lower()

    async def test_extraction_never_called_when_over_cap(
        self, mcp_client, sample_pdf, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_PAGES", "5")
        monkeypatch.setattr("oxidize_pdf.PdfReader", _fake_pdfreader(999))
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf)}
        )
        out = json.loads(result.content[0].text)
        assert out["code"] == "RESOURCE_LIMIT"


class TestExtractEntitiesOutputCap:
    """#115 Capa B: extract_entities bounds the serialized response size."""

    pytestmark = pytest.mark.asyncio

    async def test_rejects_when_output_exceeds_cap(
        self, mcp_client, sample_pdf_with_text, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_OUTPUT_BYTES", "10")
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert out["code"] == "RESOURCE_LIMIT"

    async def test_passes_when_output_within_cap(
        self, mcp_client, sample_pdf_with_text, monkeypatch
    ):
        monkeypatch.setenv("OXIDIZE_MAX_OUTPUT_BYTES", str(10 * 1024 * 1024))
        result = await mcp_client.call_tool(
            "extract_entities", {"path": str(sample_pdf_with_text)}
        )
        out = json.loads(result.content[0].text)
        assert "entities" in out
        assert "error" not in out
