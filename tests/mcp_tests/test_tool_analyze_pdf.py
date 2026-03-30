"""Tests for the analyze_pdf MCP tool."""

import json

import pytest


class TestAnalyzePdfValidate:
    """F-021: analyze_pdf with check=validate."""

    pytestmark = pytest.mark.asyncio

    async def test_validate_returns_valid_for_good_pdf(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool(
            "analyze_pdf", {"path": str(sample_pdf), "check": "validate"}
        )
        out = json.loads(result.content[0].text)
        assert out["valid"] is True
        assert out["check"] == "validate"

    async def test_validate_returns_error_counts(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool(
            "analyze_pdf", {"path": str(sample_pdf), "check": "validate"}
        )
        out = json.loads(result.content[0].text)
        assert "error_count" in out
        assert "warning_count" in out
        assert isinstance(out["error_count"], int)
        assert isinstance(out["warning_count"], int)

    async def test_validate_returns_path(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool(
            "analyze_pdf", {"path": str(sample_pdf), "check": "validate"}
        )
        out = json.loads(result.content[0].text)
        assert out["path"] == str(sample_pdf)

    async def test_validate_rejects_unsafe_path(self, mcp_client):
        result = await mcp_client.call_tool(
            "analyze_pdf", {"path": "/etc/passwd", "check": "validate"}
        )
        out = json.loads(result.content[0].text)
        assert out.get("code") == "SECURITY_ERROR"


class TestAnalyzePdfCorruption:
    """F-022: analyze_pdf with check=corruption."""

    pytestmark = pytest.mark.asyncio

    async def test_corruption_check_on_valid_pdf(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool(
            "analyze_pdf", {"path": str(sample_pdf), "check": "corruption"}
        )
        out = json.loads(result.content[0].text)
        assert "corrupted" in out
        assert out["check"] == "corruption"
        assert "severity" in out

    async def test_corruption_returns_details(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool(
            "analyze_pdf", {"path": str(sample_pdf), "check": "corruption"}
        )
        out = json.loads(result.content[0].text)
        assert "corruption_type" in out
        assert "found_pages" in out
        assert "file_size" in out


class TestAnalyzePdfCompliance:
    """F-022: analyze_pdf with check=compliance."""

    pytestmark = pytest.mark.asyncio

    async def test_compliance_check_returns_structure(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool(
            "analyze_pdf", {"path": str(sample_pdf), "check": "compliance"}
        )
        out = json.loads(result.content[0].text)
        assert out["check"] == "compliance"
        assert "is_valid" in out
        assert "error_count" in out
        assert "warning_count" in out
        assert "compliance_percentage" in out
        assert isinstance(out["compliance_percentage"], (int, float))
        assert out["level"] == "PDF/A-1B"


class TestAnalyzePdfCompare:
    """F-023: analyze_pdf with check=compare."""

    pytestmark = pytest.mark.asyncio

    async def test_compare_identical_pdfs(
        self, mcp_client, sample_pdf, sample_pdf_copy
    ):
        result = await mcp_client.call_tool(
            "analyze_pdf",
            {
                "path": str(sample_pdf),
                "check": "compare",
                "compare_path": str(sample_pdf_copy),
            },
        )
        out = json.loads(result.content[0].text)
        assert out["check"] == "compare"
        assert "structurally_equivalent" in out
        assert "similarity_score" in out

    async def test_compare_returns_difference_count(
        self, mcp_client, sample_pdf, sample_pdf_copy
    ):
        result = await mcp_client.call_tool(
            "analyze_pdf",
            {
                "path": str(sample_pdf),
                "check": "compare",
                "compare_path": str(sample_pdf_copy),
            },
        )
        out = json.loads(result.content[0].text)
        assert "difference_count" in out
        assert isinstance(out["difference_count"], int)

    async def test_compare_missing_compare_path_returns_error(
        self, mcp_client, sample_pdf
    ):
        result = await mcp_client.call_tool(
            "analyze_pdf", {"path": str(sample_pdf), "check": "compare"}
        )
        out = json.loads(result.content[0].text)
        assert "error" in out

    async def test_compare_invalid_compare_path_returns_error(
        self, mcp_client, sample_pdf, mcp_workspace
    ):
        result = await mcp_client.call_tool(
            "analyze_pdf",
            {
                "path": str(sample_pdf),
                "check": "compare",
                "compare_path": str(mcp_workspace / "nonexistent.pdf"),
            },
        )
        out = json.loads(result.content[0].text)
        assert "error" in out

    async def test_unknown_check_returns_error(self, mcp_client, sample_pdf):
        result = await mcp_client.call_tool(
            "analyze_pdf", {"path": str(sample_pdf), "check": "quantum_analysis"}
        )
        out = json.loads(result.content[0].text)
        assert "error" in out
