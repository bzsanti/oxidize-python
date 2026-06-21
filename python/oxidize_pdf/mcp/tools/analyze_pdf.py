"""MCP tool: analyze_pdf — validate, detect corruption, check compliance, compare PDFs."""

import json
from typing import Annotated, Literal, Optional

from mcp.types import ToolAnnotations
from pydantic import Field

from oxidize_pdf.mcp.server import mcp


@mcp.tool(
    annotations=ToolAnnotations(
        title="Analyze / validate a PDF",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=False,
    )
)
def analyze_pdf(
    path: Annotated[
        str,
        Field(description="Path to the PDF file to analyze, relative to the workspace."),
    ],
    check: Annotated[
        Literal["validate", "corruption", "compliance", "compare"],
        Field(
            description="Which analysis to run: 'validate' = structural validity "
            "with error/warning counts; 'corruption' = damage severity and type; "
            "'compliance' = PDF/A conformance at compliance_level; 'compare' = "
            "diff against compare_path."
        ),
    ] = "validate",
    compare_path: Annotated[
        Optional[str],
        Field(
            description="Second PDF to diff against. Required when check='compare', "
            "ignored otherwise."
        ),
    ] = None,
    compliance_level: Annotated[
        Literal["a1a", "a1b", "a2a", "a2b", "a2u", "a3a", "a3b", "a3u"],
        Field(
            description="PDF/A conformance level to test. Used only when "
            "check='compliance'. Letter = conformance class (a/b/u), number = "
            "PDF/A part (1/2/3)."
        ),
    ] = "a1b",
) -> str:
    """Inspect a PDF's structural health or conformance (does not read content).

    Returns JSON keyed by the chosen check: validate → {valid, error_count,
    warning_count}; corruption → {corrupted, corruption_type, severity,
    found_pages, file_size, errors}; compliance → {level, is_valid,
    error_count, warning_count, compliance_percentage}; compare →
    {structurally_equivalent, content_equivalent, similarity_score,
    difference_count}. Read-only.

    Use this to verify a file is well-formed, archival-grade, or identical to
    another. To read titles/author/page counts use read_pdf; for the text use
    extract_text.
    """
    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    resolved, err = setup_pdf_path(path)
    if err:
        return err

    try:
        if check == "validate":
            return _check_validate(path, str(resolved))
        elif check == "corruption":
            return _check_corruption(path, str(resolved))
        elif check == "compliance":
            return _check_compliance(path, str(resolved), compliance_level)
        # check == "compare" (the Literal type guarantees no other value here)
        return _check_compare(path, str(resolved), compare_path)
    except Exception as e:
        return json.dumps({"error": str(e), "code": "PDF_ERROR"})


def _check_validate(client_path: str, resolved_path: str) -> str:
    from oxidize_pdf import validate_pdf

    result = validate_pdf(resolved_path)
    return json.dumps({
        "path": client_path,
        "check": "validate",
        "valid": result["is_valid"],
        "error_count": result["error_count"],
        "warning_count": result["warning_count"],
    })


def _check_corruption(client_path: str, resolved_path: str) -> str:
    from oxidize_pdf import detect_pdf_corruption

    report = detect_pdf_corruption(resolved_path)
    return json.dumps({
        "path": client_path,
        "check": "corruption",
        "corrupted": report.severity > 0,
        "corruption_type": str(report.corruption_type),
        "severity": report.severity,
        "found_pages": report.found_pages,
        "file_size": report.file_size,
        "errors": report.errors,
    })


_PDFA_LEVELS = {
    "a1a": ("PdfALevel", "A1A", "PDF/A-1A"),
    "a1b": ("PdfALevel", "A1B", "PDF/A-1B"),
    "a2a": ("PdfALevel", "A2A", "PDF/A-2A"),
    "a2b": ("PdfALevel", "A2B", "PDF/A-2B"),
    "a2u": ("PdfALevel", "A2U", "PDF/A-2U"),
    "a3a": ("PdfALevel", "A3A", "PDF/A-3A"),
    "a3b": ("PdfALevel", "A3B", "PDF/A-3B"),
    "a3u": ("PdfALevel", "A3U", "PDF/A-3U"),
}


def _check_compliance(
    client_path: str, resolved_path: str, compliance_level: str,
) -> str:
    from oxidize_pdf import PdfALevel, PdfAValidator

    _, attr_name, display_name = _PDFA_LEVELS[compliance_level.lower()]
    pdfa_level = getattr(PdfALevel, attr_name)

    with open(resolved_path, "rb") as f:
        data = f.read()

    validator = PdfAValidator(pdfa_level)
    validator.collect_all_errors(True)
    result = validator.validate_bytes(data)
    total_checks = result.error_count + result.warning_count
    passed_checks = total_checks - result.error_count
    pct = 100.0 if total_checks == 0 else round((passed_checks / total_checks) * 100, 2)

    return json.dumps({
        "path": client_path,
        "check": "compliance",
        "level": display_name,
        "is_valid": result.is_valid,
        "error_count": result.error_count,
        "warning_count": result.warning_count,
        "compliance_percentage": pct,
    })


def _check_compare(
    client_path: str,
    resolved_path: str,
    compare_path: str | None,
) -> str:
    if compare_path is None:
        return json.dumps({
            "error": "compare_path is required for check='compare'.",
            "code": "MISSING_PARAM",
        })

    from oxidize_pdf.mcp.tools.base import setup_pdf_path

    compare_resolved, err = setup_pdf_path(compare_path)
    if err:
        return err

    from oxidize_pdf import compare_pdfs

    with open(resolved_path, "rb") as f1, open(str(compare_resolved), "rb") as f2:
        data1 = f1.read()
        data2 = f2.read()

    result = compare_pdfs(data1, data2)
    return json.dumps({
        "path": client_path,
        "check": "compare",
        "structurally_equivalent": result["structurally_equivalent"],
        "content_equivalent": result["content_equivalent"],
        "similarity_score": result["similarity_score"],
        "difference_count": result["difference_count"],
    })
