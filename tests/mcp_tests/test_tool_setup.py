"""Tests for shared tool infrastructure: config singleton and setup_pdf_path helper."""

import json
from pathlib import Path

import pytest


class TestConfigSingleton:
    def test_get_config_returns_same_instance(self, monkeypatch, tmp_path):
        monkeypatch.setenv("OXIDIZE_WORKSPACE", str(tmp_path))
        import oxidize_pdf.mcp.tools.base as base_module

        base_module._config = None
        cfg1 = base_module.get_config()
        cfg2 = base_module.get_config()
        assert cfg1 is cfg2

    def test_get_config_reads_env(self, monkeypatch, tmp_path):
        monkeypatch.setenv("OXIDIZE_WORKSPACE", str(tmp_path))
        import oxidize_pdf.mcp.tools.base as base_module

        base_module._config = None
        cfg = base_module.get_config()
        assert cfg.workspace_dir == tmp_path


class TestSetupPdfPath:
    def test_returns_resolved_path_for_valid_file(self, tmp_path, monkeypatch):
        monkeypatch.setenv("OXIDIZE_WORKSPACE", str(tmp_path))
        import oxidize_pdf.mcp.tools.base as base_module

        base_module._config = None
        pdf = tmp_path / "test.pdf"
        pdf.write_bytes(b"dummy")
        resolved, error = base_module.setup_pdf_path(str(pdf))
        assert error is None
        assert resolved == pdf.resolve()

    def test_returns_error_for_path_outside_workspace(self, tmp_path, monkeypatch):
        monkeypatch.setenv("OXIDIZE_WORKSPACE", str(tmp_path))
        import oxidize_pdf.mcp.tools.base as base_module

        base_module._config = None
        resolved, error = base_module.setup_pdf_path("/etc/passwd")
        assert resolved is None
        assert error is not None
        data = json.loads(error)
        assert data["code"] == "SECURITY_ERROR"

    def test_returns_error_for_oversized_file(self, tmp_path, monkeypatch):
        monkeypatch.setenv("OXIDIZE_WORKSPACE", str(tmp_path))
        monkeypatch.setenv("OXIDIZE_MAX_FILE_SIZE_MB", "0")
        import oxidize_pdf.mcp.tools.base as base_module

        base_module._config = None
        pdf = tmp_path / "big.pdf"
        pdf.write_bytes(b"x" * 200)
        resolved, error = base_module.setup_pdf_path(str(pdf))
        assert resolved is None
        data = json.loads(error)
        assert data["code"] == "SECURITY_ERROR"
