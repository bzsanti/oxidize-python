"""MCP tool: manipulate_pdf — split, merge, rotate, extract_pages, reverse, overlay."""

import json
from typing import Annotated, Literal

from mcp.types import ToolAnnotations
from pydantic import Field

from oxidize_pdf.mcp.server import mcp


@mcp.tool(
    annotations=ToolAnnotations(
        title="Restructure PDF pages",
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=False,
    )
)
def manipulate_pdf(
    operation: Annotated[
        Literal["split", "merge", "rotate", "extract_pages", "reverse", "overlay"],
        Field(
            description="Page operation: 'split' one PDF into per-page files; "
            "'merge' several PDFs into one; 'rotate' all pages; 'extract_pages' "
            "a subset; 'reverse' page order; 'overlay' one PDF on top of another."
        ),
    ],
    input_path: Annotated[
        str | None,
        Field(
            description="Source PDF. Required for every operation except 'merge' "
            "(which uses input_paths)."
        ),
    ] = None,
    input_paths: Annotated[
        list[str] | None,
        Field(description="Ordered list of PDFs to combine. Required for 'merge'."),
    ] = None,
    output_path: Annotated[
        str | None,
        Field(
            description="Output location, overwritten if it exists. For 'split' "
            "this is an existing directory; for all other operations a .pdf file."
        ),
    ] = None,
    degrees: Annotated[
        int | None,
        Field(description="Clockwise rotation in degrees (e.g. 90, 180, 270). Required for 'rotate'."),
    ] = None,
    page_indices: Annotated[
        list[int] | None,
        Field(
            description="0-based page indices to keep, in order. Required for "
            "'extract_pages'."
        ),
    ] = None,
    overlay_path: Annotated[
        str | None,
        Field(description="PDF stamped on top of input_path. Required for 'overlay'."),
    ] = None,
) -> str:
    """Restructure the pages of existing PDF file(s) and write a new PDF.

    Each operation writes to output_path (overwriting any existing file) and
    returns JSON {status, operation}; on a missing required argument it returns
    {error, code}. Per-operation requirements: merge→input_paths; rotate→degrees;
    extract_pages→page_indices; overlay→overlay_path; split→output_path is a
    directory. Page indices are 0-based.

    Use this for page-level structure. To stamp notes/highlights use
    annotate_pdf; to fill form fields use manage_forms; to encrypt use secure_pdf.
    """
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
