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


class TestCheckPageCount:
    """#115 Capa B: page-count cap rejects oversized documents before heavy work."""

    def test_raises_when_count_exceeds_max(self):
        from oxidize_pdf.mcp.security import SecurityError, check_page_count

        with pytest.raises(SecurityError, match="(?i)page"):
            check_page_count(101, 100)

    def test_passes_when_count_equals_max(self):
        from oxidize_pdf.mcp.security import check_page_count

        check_page_count(100, 100)

    def test_passes_when_count_below_max(self):
        from oxidize_pdf.mcp.security import check_page_count

        check_page_count(1, 10000)

    def test_error_message_names_count_and_limit(self):
        from oxidize_pdf.mcp.security import SecurityError, check_page_count

        with pytest.raises(SecurityError) as exc:
            check_page_count(999, 5)
        msg = str(exc.value)
        assert "999" in msg and "5" in msg


class TestCheckOutputSize:
    """#115 Capa B: output-size cap bounds the serialized JSON response."""

    def test_raises_when_payload_bytes_exceed_max(self):
        from oxidize_pdf.mcp.security import SecurityError, check_output_size

        with pytest.raises(SecurityError, match="(?i)output|size"):
            check_output_size("x" * 1001, max_bytes=1000)

    def test_passes_when_payload_bytes_equal_max(self):
        from oxidize_pdf.mcp.security import check_output_size

        check_output_size("x" * 1000, max_bytes=1000)

    def test_measures_utf8_bytes_not_character_count(self):
        # "é" is 2 bytes in UTF-8; 501 chars -> 1002 bytes > 1000.
        from oxidize_pdf.mcp.security import SecurityError, check_output_size

        with pytest.raises(SecurityError):
            check_output_size("é" * 501, max_bytes=1000)

    def test_passes_empty_payload(self):
        from oxidize_pdf.mcp.security import check_output_size

        check_output_size("", max_bytes=1)


class TestCheckSessionContentSize:
    """#115 Capa A: per-session accumulated-content cap."""

    def test_raises_when_total_exceeds_max(self):
        from oxidize_pdf.mcp.security import SecurityError, check_session_content_size

        with pytest.raises(SecurityError, match="(?i)session"):
            check_session_content_size(101, 100)

    def test_passes_when_total_equals_max(self):
        from oxidize_pdf.mcp.security import check_session_content_size

        check_session_content_size(100, 100)

    def test_error_message_names_total_and_limit(self):
        from oxidize_pdf.mcp.security import SecurityError, check_session_content_size

        with pytest.raises(SecurityError) as exc:
            check_session_content_size(500, 20)
        msg = str(exc.value)
        assert "500" in msg and "20" in msg
