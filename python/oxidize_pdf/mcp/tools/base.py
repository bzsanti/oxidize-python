"""Shared infrastructure for MCP tool implementations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxidize_pdf.mcp.config import McpConfig

_config: McpConfig | None = None


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
