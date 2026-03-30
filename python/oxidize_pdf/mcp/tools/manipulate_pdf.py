"""MCP tool: manipulate_pdf — split, merge, rotate, extract_pages, reverse, overlay."""

import json

from oxidize_pdf.mcp.server import mcp

_VALID_OPERATIONS = frozenset({
    "split", "merge", "rotate", "extract_pages", "reverse", "overlay",
})


@mcp.tool()
def manipulate_pdf(
    operation: str,
    input_path: str | None = None,
    input_paths: list[str] | None = None,
    output_path: str | None = None,
    degrees: int | None = None,
    page_indices: list[int] | None = None,
    overlay_path: str | None = None,
) -> str:
    """Manipulate PDF files with various operations.

    Operations:
    - split: Split a PDF into individual pages (output_path is a directory).
    - merge: Merge multiple PDFs into one (requires input_paths).
    - rotate: Rotate all pages by degrees (requires degrees).
    - extract_pages: Extract specific pages (requires page_indices).
    - reverse: Reverse page order.
    - overlay: Overlay one PDF on another (requires overlay_path).
    """
    if operation not in _VALID_OPERATIONS:
        return json.dumps({
            "error": f"Unknown operation: '{operation}'. "
            f"Valid operations: {', '.join(sorted(_VALID_OPERATIONS))}.",
            "code": "INVALID_OPERATION",
        })

    try:
        if operation == "split":
            return _op_split(input_path=input_path, output_path=output_path)
        elif operation == "merge":
            return _op_merge(input_paths=input_paths, output_path=output_path)
        elif operation == "rotate":
            return _op_rotate(
                input_path=input_path, output_path=output_path, degrees=degrees,
            )
        elif operation == "extract_pages":
            return _op_extract_pages(
                input_path=input_path, output_path=output_path,
                page_indices=page_indices,
            )
        elif operation == "reverse":
            return _op_reverse(input_path=input_path, output_path=output_path)
        else:
            return _op_overlay(
                input_path=input_path, output_path=output_path,
                overlay_path=overlay_path,
            )
    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})


def _validate_input(input_path: str | None) -> tuple[str | None, str | None]:
    """Validate a single input path. Returns (resolved_str, error_json)."""
    if input_path is None:
        return None, json.dumps({
            "error": "input_path is required.",
            "code": "MISSING_PARAM",
        })
    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    resolved, err = setup_pdf_path(input_path)
    if err:
        return None, err
    return str(resolved), None


def _validate_output(output_path: str | None) -> tuple[str | None, str | None]:
    """Validate an output file path. Returns (resolved_str, error_json)."""
    if output_path is None:
        return None, json.dumps({
            "error": "output_path is required.",
            "code": "MISSING_PARAM",
        })
    from oxidize_pdf.mcp.tools.base import setup_output_path

    resolved, err = setup_output_path(output_path)
    if err:
        return None, err
    return str(resolved), None


def _validate_output_dir(output_path: str | None) -> tuple[str | None, str | None]:
    """Validate an output directory path. Returns (resolved_str, error_json)."""
    if output_path is None:
        return None, json.dumps({
            "error": "output_path is required.",
            "code": "MISSING_PARAM",
        })
    from oxidize_pdf.mcp.tools.base import setup_directory_path

    resolved, err = setup_directory_path(output_path)
    if err:
        return None, err
    return str(resolved), None


def _op_split(*, input_path: str | None, output_path: str | None) -> str:
    input_resolved, err = _validate_input(input_path)
    if err:
        return err
    output_resolved, err = _validate_output_dir(output_path)
    if err:
        return err

    from oxidize_pdf import split_pdf

    split_pdf(input_resolved, output_resolved)
    return json.dumps({"status": "ok", "operation": "split"})


def _op_merge(*, input_paths: list[str] | None, output_path: str | None) -> str:
    if not input_paths:
        return json.dumps({
            "error": "input_paths is required for merge.",
            "code": "MISSING_PARAM",
        })

    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    resolved_paths = []
    for p in input_paths:
        resolved, err = setup_pdf_path(p)
        if err:
            return err
        resolved_paths.append(str(resolved))

    output_resolved, err = _validate_output(output_path)
    if err:
        return err

    from oxidize_pdf import merge_pdfs

    merge_pdfs(resolved_paths, output_resolved)
    return json.dumps({"status": "ok", "operation": "merge"})


def _op_rotate(
    *,
    input_path: str | None,
    output_path: str | None,
    degrees: int | None,
) -> str:
    input_resolved, err = _validate_input(input_path)
    if err:
        return err
    output_resolved, err = _validate_output(output_path)
    if err:
        return err

    if degrees is None:
        return json.dumps({
            "error": "degrees is required for rotate.",
            "code": "MISSING_PARAM",
        })

    from oxidize_pdf import rotate_pdf

    rotate_pdf(input_resolved, output_resolved, degrees)
    return json.dumps({"status": "ok", "operation": "rotate"})


def _op_extract_pages(
    *,
    input_path: str | None,
    output_path: str | None,
    page_indices: list[int] | None,
) -> str:
    input_resolved, err = _validate_input(input_path)
    if err:
        return err
    output_resolved, err = _validate_output(output_path)
    if err:
        return err

    if page_indices is None:
        return json.dumps({
            "error": "page_indices is required for extract_pages.",
            "code": "MISSING_PARAM",
        })

    from oxidize_pdf import extract_pages

    extract_pages(input_resolved, output_resolved, page_indices)
    return json.dumps({"status": "ok", "operation": "extract_pages"})


def _op_reverse(*, input_path: str | None, output_path: str | None) -> str:
    input_resolved, err = _validate_input(input_path)
    if err:
        return err
    output_resolved, err = _validate_output(output_path)
    if err:
        return err

    from oxidize_pdf import reverse_pdf_pages

    reverse_pdf_pages(input_resolved, output_resolved)
    return json.dumps({"status": "ok", "operation": "reverse"})


def _op_overlay(
    *,
    input_path: str | None,
    output_path: str | None,
    overlay_path: str | None,
) -> str:
    input_resolved, err = _validate_input(input_path)
    if err:
        return err
    output_resolved, err = _validate_output(output_path)
    if err:
        return err

    if overlay_path is None:
        return json.dumps({
            "error": "overlay_path is required for overlay.",
            "code": "MISSING_PARAM",
        })

    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    overlay_resolved, err = setup_pdf_path(overlay_path)
    if err:
        return err

    from oxidize_pdf import OverlayOptions, overlay_pdf

    overlay_pdf(input_resolved, str(overlay_resolved), output_resolved, OverlayOptions())
    return json.dumps({"status": "ok", "operation": "overlay"})
