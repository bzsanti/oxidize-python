"""Tests for Tier 18 — F79 Compliance System + F80 PDF Comparison Deep."""

import pytest
import oxidize_pdf as op
from oxidize_pdf import Document


# ═══════════════════════════════════════════════════════════════════════════════
# F79 — Compliance System
# ═══════════════════════════════════════════════════════════════════════════════

from oxidize_pdf import (
    VerificationLevel,
    ComplianceStats,
    IsoRequirement,
    RequirementInfo,
    ComplianceSystem,
)


class TestVerificationLevel:
    def test_not_implemented(self):
        assert VerificationLevel.NOT_IMPLEMENTED is not None

    def test_code_exists(self):
        assert VerificationLevel.CODE_EXISTS is not None

    def test_generates_pdf(self):
        assert VerificationLevel.GENERATES_PDF is not None

    def test_content_verified(self):
        assert VerificationLevel.CONTENT_VERIFIED is not None

    def test_iso_compliant(self):
        assert VerificationLevel.ISO_COMPLIANT is not None

    def test_as_percentage(self):
        assert VerificationLevel.NOT_IMPLEMENTED.as_percentage == 0.0
        assert VerificationLevel.CODE_EXISTS.as_percentage == 25.0
        assert VerificationLevel.GENERATES_PDF.as_percentage == 50.0
        assert VerificationLevel.CONTENT_VERIFIED.as_percentage == 75.0
        assert VerificationLevel.ISO_COMPLIANT.as_percentage == 100.0

    def test_repr(self):
        assert "VerificationLevel" in repr(VerificationLevel.NOT_IMPLEMENTED)


class TestComplianceStats:
    def test_type_exists(self):
        assert ComplianceStats is not None

    def test_has_expected_getters(self):
        expected = [
            "total_requirements",
            "implemented_requirements",
            "average_compliance_percentage",
            "level_0_count",
            "level_1_count",
            "level_2_count",
            "level_3_count",
            "level_4_count",
        ]
        for attr in expected:
            assert hasattr(ComplianceStats, attr) or attr in dir(ComplianceStats), (
                f"ComplianceStats missing expected getter: {attr}"
            )


class TestIsoRequirement:
    def test_type_exists(self):
        assert IsoRequirement is not None

    def test_has_expected_getters(self):
        expected = [
            "id", "name", "description", "iso_reference",
            "implementation", "test_file", "level", "verified", "notes",
        ]
        for attr in expected:
            assert hasattr(IsoRequirement, attr) or attr in dir(IsoRequirement), (
                f"IsoRequirement missing expected getter: {attr}"
            )


class TestRequirementInfo:
    def test_type_exists(self):
        assert RequirementInfo is not None

    def test_has_expected_getters(self):
        expected = [
            "id", "name", "description", "iso_reference",
            "requirement_type", "page", "level", "implementation",
            "test_file", "verified", "last_checked", "notes",
        ]
        for attr in expected:
            assert hasattr(RequirementInfo, attr) or attr in dir(RequirementInfo), (
                f"RequirementInfo missing expected getter: {attr}"
            )


class TestComplianceSystem:
    def test_type_exists(self):
        assert ComplianceSystem is not None


# ═══════════════════════════════════════════════════════════════════════════════
# F80 — PDF Comparison Deep
# ═══════════════════════════════════════════════════════════════════════════════

from oxidize_pdf import (
    DifferenceSeverity,
    PdfDifference,
    ComparisonResult,
    extract_pdf_differences,
    pdfs_structurally_equivalent,
    compare_pdfs_deep,
)


class TestDifferenceSeverity:
    def test_critical(self):
        assert DifferenceSeverity.CRITICAL is not None

    def test_important(self):
        assert DifferenceSeverity.IMPORTANT is not None

    def test_minor(self):
        assert DifferenceSeverity.MINOR is not None

    def test_cosmetic(self):
        assert DifferenceSeverity.COSMETIC is not None

    def test_repr(self):
        assert "DifferenceSeverity" in repr(DifferenceSeverity.CRITICAL)


class TestPdfDifference:
    def test_type_exists(self):
        assert PdfDifference is not None

    def test_has_expected_getters(self):
        expected = ["location", "expected", "actual", "severity"]
        for attr in expected:
            assert hasattr(PdfDifference, attr) or attr in dir(PdfDifference), (
                f"PdfDifference missing expected getter: {attr}"
            )

    def test_properties_from_comparison(self):
        """Differences returned from compare_pdfs_deep have correct property types."""
        import oxidize_pdf as op
        doc1 = op.Document()
        doc1.set_title("First")
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Version A")
        doc1.add_page(page)
        pdf1 = doc1.save_to_bytes()

        doc2 = op.Document()
        doc2.set_title("Second")
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Version B")
        doc2.add_page(page)
        pdf2 = doc2.save_to_bytes()

        result = compare_pdfs_deep(pdf1, pdf2)
        for diff in result.differences:
            assert isinstance(diff.location, str)
            assert isinstance(diff.expected, str)
            assert isinstance(diff.actual, str)
            assert isinstance(diff.severity, DifferenceSeverity)


class TestComparisonResult:
    def test_type_exists(self):
        assert ComparisonResult is not None

    def test_has_expected_getters(self):
        expected = [
            "structurally_equivalent", "content_equivalent",
            "differences", "similarity_score",
        ]
        for attr in expected:
            assert hasattr(ComparisonResult, attr) or attr in dir(ComparisonResult), (
                f"ComparisonResult missing expected getter: {attr}"
            )

    def test_property_types_from_comparison(self):
        """Properties returned from compare_pdfs_deep have correct types."""
        import oxidize_pdf as op
        doc = op.Document()
        doc.set_title("Test")
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Hello")
        doc.add_page(page)
        pdf = doc.save_to_bytes()

        result = compare_pdfs_deep(pdf, pdf)
        assert isinstance(result.structurally_equivalent, bool)
        assert isinstance(result.content_equivalent, bool)
        assert isinstance(result.similarity_score, float)
        assert isinstance(result.differences, list)


class TestComparePdfsDeep:
    def _make_pdf_bytes(self, title="Test"):
        doc = op.Document()
        doc.set_title(title)
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, f"Content: {title}")
        doc.add_page(page)
        return doc.save_to_bytes()

    def test_compare_identical_pdfs(self):
        pdf = self._make_pdf_bytes()
        result = compare_pdfs_deep(pdf, pdf)
        assert isinstance(result, ComparisonResult)
        assert result.similarity_score > 0.5

    def test_compare_result_properties(self):
        pdf = self._make_pdf_bytes()
        result = compare_pdfs_deep(pdf, pdf)
        assert isinstance(result.structurally_equivalent, bool)
        assert isinstance(result.content_equivalent, bool)
        assert isinstance(result.similarity_score, float)
        assert isinstance(result.differences, list)

    def test_compare_different_pdfs(self):
        pdf1 = self._make_pdf_bytes("First")
        pdf2 = self._make_pdf_bytes("Second")
        result = compare_pdfs_deep(pdf1, pdf2)
        assert isinstance(result, ComparisonResult)

    def test_difference_has_properties(self):
        pdf1 = self._make_pdf_bytes("First")
        pdf2 = self._make_pdf_bytes("Second")
        result = compare_pdfs_deep(pdf1, pdf2)
        if result.differences:
            diff = result.differences[0]
            assert isinstance(diff, PdfDifference)
            assert isinstance(diff.location, str)
            assert isinstance(diff.expected, str)
            assert isinstance(diff.actual, str)
            assert isinstance(diff.severity, DifferenceSeverity)


class TestExtractPdfDifferences:
    def _make_pdf_bytes(self, title="Test"):
        doc = op.Document()
        doc.set_title(title)
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, f"Content: {title}")
        doc.add_page(page)
        return doc.save_to_bytes()

    def test_function_exists(self):
        assert callable(extract_pdf_differences)

    def test_extract_from_identical(self):
        pdf = self._make_pdf_bytes()
        diffs = extract_pdf_differences(pdf, pdf)
        assert isinstance(diffs, list)

    def test_extract_from_different(self):
        pdf1 = self._make_pdf_bytes("A")
        pdf2 = self._make_pdf_bytes("B")
        diffs = extract_pdf_differences(pdf1, pdf2)
        assert isinstance(diffs, list)


class TestPdfsStructurallyEquivalent:
    def _make_pdf_bytes(self, title="Test"):
        doc = op.Document()
        doc.set_title(title)
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA, 12.0)
        page.text_at(100.0, 700.0, "Hello")
        doc.add_page(page)
        return doc.save_to_bytes()

    def test_function_exists(self):
        assert callable(pdfs_structurally_equivalent)

    def test_identical_pdfs(self):
        pdf = self._make_pdf_bytes()
        result = pdfs_structurally_equivalent(pdf, pdf)
        assert isinstance(result, bool)

    def test_with_invalid_data(self):
        """Invalid PDF bytes should not crash."""
        result = pdfs_structurally_equivalent(b"not a pdf", b"also not")
        assert isinstance(result, bool)
