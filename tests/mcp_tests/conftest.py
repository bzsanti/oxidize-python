"""Shared fixtures for MCP server tests."""

import pytest


@pytest.fixture
def mcp_workspace(tmp_path):
    """Temporary workspace directory for MCP operations."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def sample_pdf(mcp_workspace):
    """A minimal PDF file in the workspace for testing."""
    from oxidize_pdf import Document, Font, Page

    path = mcp_workspace / "sample.pdf"
    doc = Document()
    doc.set_title("Test Document")
    doc.set_author("Test Author")

    page = Page.a4()
    page.set_font(Font.HELVETICA, 12.0)
    page.text_at(100.0, 700.0, "Hello from page 1")
    doc.add_page(page)

    doc.save(str(path))
    return path


@pytest.fixture
def sample_pdf_with_text(mcp_workspace):
    """A multi-page PDF with known text content."""
    from oxidize_pdf import Document, Font, Page

    path = mcp_workspace / "text_sample.pdf"
    doc = Document()

    page1 = Page.a4()
    page1.set_font(Font.HELVETICA, 12.0)
    page1.text_at(50.0, 750.0, "Chapter 1: Introduction")
    page1.text_at(50.0, 720.0, "Hello World. This is page one.")
    doc.add_page(page1)

    page2 = Page.a4()
    page2.set_font(Font.COURIER, 12.0)
    page2.text_at(50.0, 750.0, "Chapter 2: Details")
    page2.text_at(50.0, 720.0, "More information on page two.")
    doc.add_page(page2)

    doc.save(str(path))
    return path


@pytest.fixture
def two_page_pdf(mcp_workspace):
    """A 2-page PDF for manipulation tests."""
    from oxidize_pdf import Document, Font, Page

    path = mcp_workspace / "two_page.pdf"
    doc = Document()

    page1 = Page.a4()
    page1.set_font(Font.HELVETICA, 12.0)
    page1.text_at(100.0, 700.0, "Page one content")
    doc.add_page(page1)

    page2 = Page.a4()
    page2.set_font(Font.COURIER, 12.0)
    page2.text_at(100.0, 700.0, "Page two content")
    doc.add_page(page2)

    doc.save(str(path))
    return path


@pytest.fixture
def sample_pdf_copy(mcp_workspace, sample_pdf):
    """A copy of sample_pdf for comparison tests."""
    import shutil

    copy_path = mcp_workspace / "sample_copy.pdf"
    shutil.copy2(sample_pdf, copy_path)
    return copy_path


@pytest.fixture
def encrypted_pdf(mcp_workspace):
    """An encrypted PDF with known passwords."""
    from oxidize_pdf import Document, Font, Page

    path = mcp_workspace / "encrypted.pdf"
    doc = Document()

    page = Page.a4()
    page.set_font(Font.HELVETICA, 12.0)
    page.text_at(100.0, 700.0, "Secret content")
    doc.add_page(page)

    doc.encrypt("userpass", "ownerpass")
    doc.save(str(path))
    return path


@pytest.fixture(autouse=True)
def _reset_config_singleton():
    """Reset the McpConfig singleton between tests to avoid cross-test contamination."""
    yield
    try:
        import oxidize_pdf.mcp.tools.base as base_module

        base_module._config = None
    except ImportError:
        pass


@pytest.fixture
async def mcp_client(mcp_workspace, monkeypatch):
    """FastMCP in-memory test client."""
    monkeypatch.setenv("OXIDIZE_WORKSPACE", str(mcp_workspace))

    from fastmcp.client import Client
    from oxidize_pdf.mcp.server import mcp

    async with Client(mcp) as client:
        yield client
