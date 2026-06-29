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


class TestSessionStoreSingletonRespectsConfig:
    """#115 Capa A: get_session_store honors cfg.max_sessions, not a hardcoded cap."""

    def test_store_enforces_configured_max_sessions(self, tmp_path, monkeypatch):
        from oxidize_pdf.mcp.sessions import SessionLimitError

        monkeypatch.setenv("OXIDIZE_WORKSPACE", str(tmp_path))
        monkeypatch.setenv("OXIDIZE_MAX_SESSIONS", "2")
        import oxidize_pdf.mcp.tools.base as base_module

        base_module._config = None
        base_module._session_store = None

        store = base_module.get_session_store()
        store.create({"title": "A"})
        store.create({"title": "B"})
        with pytest.raises(SessionLimitError):
            store.create({"title": "C"})


class TestEnforcePageLimit:
    """#115 Capa B: page-count gate returns RESOURCE_LIMIT before heavy work."""

    def _cfg(self, monkeypatch, tmp_path, max_pages):
        monkeypatch.setenv("OXIDIZE_WORKSPACE", str(tmp_path))
        monkeypatch.setenv("OXIDIZE_MAX_PAGES", str(max_pages))
        import oxidize_pdf.mcp.tools.base as base_module

        base_module._config = None
        return base_module

    def test_returns_none_when_within_limit(self, tmp_path, monkeypatch):
        base_module = self._cfg(monkeypatch, tmp_path, max_pages=10)
        assert base_module.enforce_page_limit(1) is None
        assert base_module.enforce_page_limit(10) is None

    def test_returns_resource_limit_error_when_exceeded(self, tmp_path, monkeypatch):
        base_module = self._cfg(monkeypatch, tmp_path, max_pages=5)
        err = base_module.enforce_page_limit(99)
        assert err is not None
        data = json.loads(err)
        assert data["code"] == "RESOURCE_LIMIT"
        assert "page" in data["error"].lower()

    def test_error_message_names_count_and_limit(self, tmp_path, monkeypatch):
        base_module = self._cfg(monkeypatch, tmp_path, max_pages=5)
        data = json.loads(base_module.enforce_page_limit(99))
        assert "99" in data["error"] and "5" in data["error"]

    def test_accepts_explicit_cfg(self, tmp_path, monkeypatch):
        from oxidize_pdf.mcp.config import McpConfig
        import oxidize_pdf.mcp.tools.base as base_module

        cfg = McpConfig(max_pages=3)
        assert base_module.enforce_page_limit(3, cfg=cfg) is None
        assert base_module.enforce_page_limit(4, cfg=cfg) is not None
