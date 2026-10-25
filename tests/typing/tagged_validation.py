from oxidize_pdf import (
    PdfValue, TaggedPdfLimits, TaggedPdfValidationOptions, TaggedPdfObjectRef,
    TaggedPdfFindingCode, TaggedPdfFindingSeverity, TaggedPdfValidationReport,
    validate_tagged_pdf,
)


def inspect(data: bytes) -> TaggedPdfValidationReport:
    report = validate_tagged_pdf(data, TaggedPdfValidationOptions(TaggedPdfLimits(max_depth=32)))
    maps: dict[int, PdfValue] = report.parent_tree
    mcids: dict[TaggedPdfObjectRef, list[int]] = report.content_mcids
    for element in report.elements:
        dictionary: dict[str, PdfValue] = element.dictionary
        title: str | None = element.title
        assert dictionary or title is None
    for finding in report.findings:
        code: TaggedPdfFindingCode = finding.code
        severity: TaggedPdfFindingSeverity = finding.severity
        assert code is not None and severity is not None
    assert maps is not None and mcids is not None
    return report
