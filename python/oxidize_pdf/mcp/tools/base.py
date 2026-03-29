"""Shared infrastructure for MCP tool implementations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxidize_pdf.mcp.config import McpConfig

from oxidize_pdf.mcp.sessions import SessionStore

_config: McpConfig | None = None
_session_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    """Return the process-level SessionStore singleton."""
    global _session_store
    if _session_store is None:
        _session_store = SessionStore(max_age_seconds=3600, max_sessions=100)
    return _session_store


def get_config() -> McpConfig:
    """Return the process-level McpConfig singleton.

    Reads environment variables once on first call.
    """
    global _config
    if _config is None:
        from oxidize_pdf.mcp.config import McpConfig

        _config = McpConfig()
    return _config


def setup_pdf_path(
    path: str,
    *,
    cfg: McpConfig | None = None,
) -> tuple[Path | None, str | None]:
    """Validate path and check file size.

    Returns (resolved_path, None) on success.
    Returns (None, error_json_str) on failure.
    """
    from oxidize_pdf.mcp.security import SecurityError, check_file_size, validate_path

    if cfg is None:
        cfg = get_config()

    try:
        resolved = validate_path(
            path,
            cfg.workspace_dir,
            must_exist=True,
            allowed_extensions={".pdf"},
            extra_allowed=cfg.allowed_paths,
        )
        check_file_size(resolved, cfg.max_file_size_bytes)
        return resolved, None
    except SecurityError as exc:
        return None, json.dumps({"error": str(exc), "code": "SECURITY_ERROR"})


def setup_directory_path(
    path: str,
    *,
    cfg: McpConfig | None = None,
) -> tuple[Path | None, str | None]:
    """Validate a directory path (must exist).

    Returns (resolved_path, None) on success.
    Returns (None, error_json_str) on failure.
    """
    from oxidize_pdf.mcp.security import SecurityError, validate_path

    if cfg is None:
        cfg = get_config()

    try:
        resolved = validate_path(
            path,
            cfg.workspace_dir,
            must_exist=True,
            allowed_extensions=None,
            extra_allowed=cfg.allowed_paths,
        )
        return resolved, None
    except SecurityError as exc:
        return None, json.dumps({"error": str(exc), "code": "SECURITY_ERROR"})


def setup_output_path(
    path: str,
    *,
    cfg: McpConfig | None = None,
    allowed_extensions: set[str] | None = None,
) -> tuple[Path | None, str | None]:
    """Validate an output path (does not need to exist yet).

    Returns (resolved_path, None) on success.
    Returns (None, error_json_str) on failure.
    """
    from oxidize_pdf.mcp.security import SecurityError, validate_path

    if cfg is None:
        cfg = get_config()

    if allowed_extensions is None:
        allowed_extensions = {".pdf"}

    try:
        resolved = validate_path(
            path,
            cfg.workspace_dir,
            must_exist=False,
            allowed_extensions=allowed_extensions,
            extra_allowed=cfg.allowed_paths,
        )
        return resolved, None
    except SecurityError as exc:
        return None, json.dumps({"error": str(exc), "code": "SECURITY_ERROR"})
