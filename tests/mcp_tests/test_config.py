"""F-004: Config module — environment-based settings."""

import pytest
from pathlib import Path


def test_config_has_defaults():
    from oxidize_pdf.mcp.config import McpConfig

    cfg = McpConfig()
    assert cfg.workspace_dir is not None
    assert cfg.max_session_age_seconds > 0
    assert cfg.max_file_size_bytes > 0


def test_config_defaults_are_sane():
    from oxidize_pdf.mcp.config import McpConfig

    cfg = McpConfig()
    assert cfg.max_session_age_seconds == 3600
    assert cfg.max_file_size_bytes == 100 * 1024 * 1024
    assert cfg.max_sessions == 10


def test_config_workspace_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("OXIDIZE_WORKSPACE", str(tmp_path))
    from oxidize_pdf.mcp.config import McpConfig

    cfg = McpConfig()
    assert cfg.workspace_dir == tmp_path


def test_config_max_file_size_from_env(monkeypatch):
    monkeypatch.setenv("OXIDIZE_MAX_FILE_SIZE_MB", "50")
    from oxidize_pdf.mcp.config import McpConfig

    cfg = McpConfig()
    assert cfg.max_file_size_bytes == 50 * 1024 * 1024


def test_config_allowed_paths_from_env(monkeypatch):
    monkeypatch.setenv("OXIDIZE_ALLOWED_PATHS", "/tmp/a, /tmp/b")
    from oxidize_pdf.mcp.config import McpConfig

    cfg = McpConfig()
    assert len(cfg.allowed_paths) == 2


def test_config_raises_on_invalid_max_file_size(monkeypatch):
    monkeypatch.setenv("OXIDIZE_MAX_FILE_SIZE_MB", "not_a_number")
    from oxidize_pdf.mcp.config import McpConfig

    with pytest.raises(ValueError):
        McpConfig()


def test_config_raises_on_invalid_session_timeout(monkeypatch):
    monkeypatch.setenv("OXIDIZE_SESSION_TIMEOUT", "abc")
    from oxidize_pdf.mcp.config import McpConfig

    with pytest.raises(ValueError):
        McpConfig()


def test_config_raises_on_invalid_max_sessions(monkeypatch):
    monkeypatch.setenv("OXIDIZE_MAX_SESSIONS", "not_int")
    from oxidize_pdf.mcp.config import McpConfig

    with pytest.raises(ValueError):
        McpConfig()


def test_config_workspace_default_is_safe_for_ci(monkeypatch):
    """Config creation must not raise even when the default workspace doesn't exist."""
    monkeypatch.delenv("OXIDIZE_WORKSPACE", raising=False)
    from oxidize_pdf.mcp.config import McpConfig

    cfg = McpConfig()
    assert cfg.workspace_dir is not None
    assert isinstance(cfg.workspace_dir, Path)
