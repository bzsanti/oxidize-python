"""Path validation and sandbox enforcement for the MCP server."""

from pathlib import Path

__all__ = ["SecurityError", "validate_path", "check_file_size"]


class SecurityError(ValueError):
    """Raised when a path fails security validation."""


def validate_path(
    path: str,
    workspace: Path,
    *,
    must_exist: bool = True,
    allowed_extensions: set[str] | None = None,
    extra_allowed: list[Path] | None = None,
) -> Path:
    """Validate and resolve a path within the workspace sandbox.

    Args:
        path: Raw path string from tool input.
        workspace: The workspace directory (sandbox root).
        must_exist: If True, the resolved path must exist on disk.
        allowed_extensions: If set, only these file extensions are permitted.
        extra_allowed: Additional directories outside workspace that are permitted.

    Returns:
        The resolved, validated Path.

    Raises:
        SecurityError: If the path fails any validation check.
    """
    resolved = Path(path).resolve()
    workspace_resolved = workspace.resolve()

    allowed_roots = [workspace_resolved]
    if extra_allowed:
        allowed_roots.extend(p.resolve() for p in extra_allowed)

    if not any(resolved == root or _is_child_of(resolved, root) for root in allowed_roots):
        raise SecurityError(
            f"Path {resolved} is outside allowed directories"
        )

    if must_exist and not resolved.exists():
        raise SecurityError(f"Path not found: {resolved}")

    if allowed_extensions is not None:
        _check_extension(resolved, allowed_extensions)

    return resolved


def check_file_size(path: Path, max_bytes: int) -> None:
    """Raise SecurityError if the file exceeds the size limit or cannot be stat'd."""
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise SecurityError(f"Cannot stat file: {exc}") from exc
    if size > max_bytes:
        raise SecurityError(
            f"File too large: {size} bytes (max {max_bytes} bytes)"
        )


def _check_extension(path: Path, allowed: set[str]) -> None:
    """Raise SecurityError if the file extension is not in the allowed set."""
    ext = path.suffix.lower()
    if ext not in allowed:
        raise SecurityError(
            f"File extension '{ext}' not allowed (expected one of {allowed})"
        )


def _is_child_of(child: Path, parent: Path) -> bool:
    """Check if child is a descendant of parent."""
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False
