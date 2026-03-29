"""MCP tool: analyze_pdf — validate, detect corruption, check compliance, compare PDFs."""

import json

from oxidize_pdf.mcp.server import mcp


@mcp.tool()
def analyze_pdf(
    path: str,
    check: str = "validate",
    compare_path: str | None = None,
    compliance_level: str = "a1b",
) -> str:
    """Analyze a PDF file with various checks.

    Available checks:
    - validate: Validate PDF structure and return error/warning counts.
    - corruption: Detect corruption and report severity, type, and page count.
    - compliance: Check PDF/A compliance (level via compliance_level: a1a, a1b, a2a, a2b, a2u, a3a, a3b, a3u).
    - compare: Compare two PDFs for structural and content equivalence (requires compare_path).
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
        elif check == "compare":
            return _check_compare(path, str(resolved), compare_path)
        else:
            return json.dumps({
                "error": f"Unknown check type: '{check}'. "
                "Valid checks: validate, corruption, compliance, compare.",
                "code": "INVALID_CHECK",
            })
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

    level_key = compliance_level.lower()
    if level_key not in _PDFA_LEVELS:
        return json.dumps({
            "error": f"Unknown compliance level: '{compliance_level}'. "
            f"Valid levels: {', '.join(sorted(_PDFA_LEVELS))}.",
            "code": "INVALID_LEVEL",
        })

    _, attr_name, display_name = _PDFA_LEVELS[level_key]
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
