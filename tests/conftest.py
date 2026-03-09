"""Shared fixtures for oxidize-pdf tests."""

import tempfile
import pathlib

import pytest


@pytest.fixture
def tmp_dir():
    """Temporary directory for test output files."""
    with tempfile.TemporaryDirectory(prefix="oxidize_pdf_test_") as d:
        yield pathlib.Path(d)


@pytest.fixture
def output_pdf(tmp_dir):
    """Path for a single output PDF file."""
    return tmp_dir / "output.pdf"
