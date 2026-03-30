"""Environment-based configuration for the oxidize-pdf MCP server."""

import os

__all__ = ["McpConfig"]
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class McpConfig:
    """Server configuration loaded from environment variables."""

    workspace_dir: Path = field(default_factory=lambda: _get_workspace_dir())
    max_file_size_bytes: int = field(default_factory=lambda: _get_max_file_size())
    max_session_age_seconds: int = field(
        default_factory=lambda: int(os.environ.get("OXIDIZE_SESSION_TIMEOUT", "3600"))
    )
    max_sessions: int = field(
        default_factory=lambda: int(os.environ.get("OXIDIZE_MAX_SESSIONS", "10"))
    )
    allowed_paths: list[Path] = field(default_factory=lambda: _get_allowed_paths())


def _get_workspace_dir() -> Path:
    env = os.environ.get("OXIDIZE_WORKSPACE")
    if env:
        return Path(env)
    return Path.home() / "Documents" / "oxidize-mcp"


def _get_max_file_size() -> int:
    mb = os.environ.get("OXIDIZE_MAX_FILE_SIZE_MB", "100")
    return int(mb) * 1024 * 1024


def _get_allowed_paths() -> list[Path]:
    raw = os.environ.get("OXIDIZE_ALLOWED_PATHS", "")
    if not raw:
        return []
    return [Path(p.strip()) for p in raw.split(",") if p.strip()]
