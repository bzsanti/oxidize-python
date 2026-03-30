"""Tests for MCP resources."""

import json

import pytest


class TestFontsResource:
    """F-043: oxidize://fonts resource."""

    pytestmark = pytest.mark.asyncio

    async def test_fonts_listed(self, mcp_client):
        resources = await mcp_client.list_resources()
        uris = [str(r.uri) for r in resources]
        assert "oxidize://fonts" in uris

    async def test_fonts_content(self, mcp_client):
        resource = await mcp_client.read_resource("oxidize://fonts")
        data = json.loads(resource[0].text)
        assert isinstance(data, list)
        assert len(data) > 0
        assert any("Helvetica" in f for f in data)


class TestPageSizesResource:
    """F-044: oxidize://page-sizes resource."""

    pytestmark = pytest.mark.asyncio

    async def test_page_sizes_listed(self, mcp_client):
        resources = await mcp_client.list_resources()
        uris = [str(r.uri) for r in resources]
        assert "oxidize://page-sizes" in uris

    async def test_page_sizes_content(self, mcp_client):
        resource = await mcp_client.read_resource("oxidize://page-sizes")
        data = json.loads(resource[0].text)
        assert "a4" in data
        assert "letter" in data
        assert isinstance(data["a4"]["width"], (int, float))


class TestCapabilitiesResource:
    """F-045: oxidize://capabilities resource."""

    pytestmark = pytest.mark.asyncio

    async def test_capabilities_content(self, mcp_client):
        resource = await mcp_client.read_resource("oxidize://capabilities")
        data = json.loads(resource[0].text)
        assert "tools" in data
        assert "read_pdf" in data["tools"]
        assert "version" in data


class TestVersionResource:
    """F-046: oxidize://version resource."""

    pytestmark = pytest.mark.asyncio

    async def test_version_content(self, mcp_client):
        resource = await mcp_client.read_resource("oxidize://version")
        data = json.loads(resource[0].text)
        assert "oxidize_pdf" in data
        assert "mcp_server" in data
        assert isinstance(data["oxidize_pdf"], str)


class TestWorkspaceResource:
    """F-047: oxidize://workspace resource."""

    pytestmark = pytest.mark.asyncio

    async def test_workspace_content(self, mcp_client, sample_pdf):
        resource = await mcp_client.read_resource("oxidize://workspace")
        data = json.loads(resource[0].text)
        assert "files" in data
        assert "workspace_dir" in data
        assert isinstance(data["files"], list)


class TestSessionResource:
    """F-048: oxidize://session/{id} resource."""

    pytestmark = pytest.mark.asyncio

    async def test_session_valid(self, mcp_client):
        create = await mcp_client.call_tool("create_pdf", {"title": "Res Test"})
        sid = json.loads(create.content[0].text)["session_id"]
        resource = await mcp_client.read_resource(f"oxidize://session/{sid}")
        data = json.loads(resource[0].text)
        assert data["session_id"] == sid
        assert data["title"] == "Res Test"

    async def test_session_missing_returns_null(self, mcp_client):
        resource = await mcp_client.read_resource("oxidize://session/nonexistent")
        data = json.loads(resource[0].text)
        assert data is None
