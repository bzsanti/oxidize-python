"""F-005 & F-006: Security module — path validation and file size enforcement."""

import pytest


class TestValidatePath:
    def test_safe_path_within_workspace(self, tmp_path):
        from oxidize_pdf.mcp.security import validate_path

        safe = tmp_path / "file.pdf"
        safe.touch()
        result = validate_path(str(safe), workspace=tmp_path)
        assert result == safe.resolve()

    def test_rejects_traversal(self, tmp_path):
        from oxidize_pdf.mcp.security import SecurityError, validate_path

        with pytest.raises(SecurityError, match="outside allowed"):
            validate_path(
                str(tmp_path / ".." / "etc" / "passwd"), workspace=tmp_path
            )

    def test_rejects_absolute_outside_workspace(self, tmp_path):
        from oxidize_pdf.mcp.security import SecurityError, validate_path

        with pytest.raises(SecurityError):
            validate_path("/etc/passwd", workspace=tmp_path)

    def test_rejects_nonexistent_when_must_exist(self, tmp_path):
        from oxidize_pdf.mcp.security import SecurityError, validate_path

        with pytest.raises(SecurityError, match="not found"):
            validate_path(
                str(tmp_path / "missing.pdf"), workspace=tmp_path, must_exist=True
            )

    def test_allows_nonexistent_output(self, tmp_path):
        from oxidize_pdf.mcp.security import validate_path

        out = tmp_path / "output.pdf"
        result = validate_path(str(out), workspace=tmp_path, must_exist=False)
        assert result == out.resolve()

    def test_rejects_non_pdf_extension(self, tmp_path):
        from oxidize_pdf.mcp.security import SecurityError, validate_path

        f = tmp_path / "evil.exe"
        f.touch()
        with pytest.raises(SecurityError, match="extension"):
            validate_path(
                str(f), workspace=tmp_path, allowed_extensions={".pdf"}
            )

    def test_allows_pdf_extension(self, tmp_path):
        from oxidize_pdf.mcp.security import validate_path

        f = tmp_path / "doc.pdf"
        f.touch()
        result = validate_path(
            str(f), workspace=tmp_path, allowed_extensions={".pdf"}
        )
        assert result == f.resolve()

    def test_legitimate_path_with_dotdot_inside_workspace(self, tmp_path):
        """A path containing .. that resolves INSIDE the workspace must be accepted."""
        from oxidize_pdf.mcp.security import validate_path

        subdir = tmp_path / "subdir"
        subdir.mkdir()
        f = subdir / "doc.pdf"
        f.touch()
        path_with_dotdot = str(subdir / ".." / "subdir" / "doc.pdf")
        result = validate_path(path_with_dotdot, workspace=tmp_path)
        assert result == f.resolve()

    def test_allows_extra_allowed_paths(self, tmp_path):
        from oxidize_pdf.mcp.security import validate_path

        extra_dir = tmp_path / "extra"
        extra_dir.mkdir()
        f = extra_dir / "doc.pdf"
        f.touch()

        workspace = tmp_path / "workspace"
        workspace.mkdir()

        result = validate_path(
            str(f), workspace=workspace, extra_allowed=[extra_dir]
        )
        assert result == f.resolve()


class TestCheckFileSize:
    def test_passes_within_limit(self, tmp_path):
        from oxidize_pdf.mcp.security import check_file_size

        f = tmp_path / "small.pdf"
        f.write_bytes(b"x" * 1024)
        check_file_size(f, max_bytes=1024 * 1024)

    def test_rejects_oversized(self, tmp_path):
        from oxidize_pdf.mcp.security import SecurityError, check_file_size

        f = tmp_path / "big.pdf"
        f.write_bytes(b"x" * 200)
        with pytest.raises(SecurityError, match="too large"):
            check_file_size(f, max_bytes=100)

    def test_raises_security_error_when_stat_fails(self, tmp_path):
        """OSError from stat() must be converted to SecurityError."""
        from unittest.mock import patch

        from oxidize_pdf.mcp.security import SecurityError, check_file_size

        f = tmp_path / "file.pdf"
        f.write_bytes(b"data")
        with patch.object(type(f), "stat", side_effect=OSError("permission denied")):
            with pytest.raises(SecurityError, match="Cannot stat"):
                check_file_size(f, max_bytes=1024 * 1024)
