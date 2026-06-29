"""Shared infrastructure for MCP tool implementations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxidize_pdf.mcp.config import McpConfig

from oxidize_pdf.mcp.sessions import SessionStore

PAGE_SIZES: dict[str, dict[str, float]] = {
    "a4": {"width": 595.28, "height": 841.89},
    "a4_landscape": {"width": 841.89, "height": 595.28},
    "letter": {"width": 612.0, "height": 792.0},
    "letter_landscape": {"width": 792.0, "height": 612.0},
    "legal": {"width": 612.0, "height": 1008.0},
    "legal_landscape": {"width": 1008.0, "height": 612.0},
}

_config: McpConfig | None = None
_session_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    """Return the process-level SessionStore singleton, configured from McpConfig."""
    global _session_store
    if _session_store is None:
        cfg = get_config()
        _session_store = SessionStore(
            max_age_seconds=cfg.max_session_age_seconds,
            max_sessions=cfg.max_sessions,
        )
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


def enforce_page_limit(
    page_count: int,
    *,
    cfg: McpConfig | None = None,
) -> str | None:
    """Gate heavy per-page work on the configured page-count cap.

    Call after the page count is known (cheap) and before any extraction or
    rendering. Returns an error JSON string when the cap is exceeded, or None
    when the document is within the limit.
    """
    from oxidize_pdf.mcp.security import SecurityError, check_page_count

    if cfg is None:
        cfg = get_config()

    try:
        check_page_count(page_count, cfg.max_pages)
        return None
    except SecurityError as exc:
        return json.dumps({"error": str(exc), "code": "RESOURCE_LIMIT"})


def apply_output_cap(
    result_json: str,
    *,
    cfg: McpConfig | None = None,
) -> str:
    """Bound the serialized tool response to the configured output-size cap.

    Returns the response unchanged when within the limit, or an error JSON
    string with code RESOURCE_LIMIT when it exceeds the cap.
    """
    from oxidize_pdf.mcp.security import SecurityError, check_output_size

    if cfg is None:
        cfg = get_config()

    try:
        check_output_size(result_json, cfg.max_output_bytes)
        return result_json
    except SecurityError as exc:
        return json.dumps({"error": str(exc), "code": "RESOURCE_LIMIT"})


def enforce_session_byte_limit(
    projected_bytes: int,
    *,
    cfg: McpConfig | None = None,
) -> str | None:
    """Gate session growth on the configured per-session content-size cap.

    Call with the session's accumulated content size after the pending add.
    Returns an error JSON string when the cap would be exceeded, or None when
    the session is still within the limit.
    """
    from oxidize_pdf.mcp.security import SecurityError, check_session_content_size

    if cfg is None:
        cfg = get_config()

    try:
        check_session_content_size(projected_bytes, cfg.max_session_bytes)
        return None
    except SecurityError as exc:
        return json.dumps({"error": str(exc), "code": "RESOURCE_LIMIT"})


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
