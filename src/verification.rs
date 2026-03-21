use pyo3::prelude::*;

use oxidize_pdf::verification::iso_matrix::{ComplianceSystem, RequirementInfo};
use oxidize_pdf::verification::{IsoRequirement, VerificationLevel};
use oxidize_pdf::verification::{extract_pdf_differences, pdfs_structurally_equivalent};
use oxidize_pdf::{ComparisonResult, DifferenceSeverity, PdfDifference};
use oxidize_pdf::ComplianceStats;
use oxidize_pdf::compare_pdfs;

// ═══════════════════════════════════════════════════════════════════════════
// F79 — Compliance System
// ═══════════════════════════════════════════════════════════════════════════

// ── VerificationLevel ───────────────────────────────────────────────────────

/// Verification level for ISO 32000-1 compliance tracking.
///
/// Represents how thoroughly a feature has been verified:
///
/// - ``NOT_IMPLEMENTED`` (0) — Feature not implemented (0% compliance)
/// - ``CODE_EXISTS`` (1) — Code exists, doesn't crash (25%)
/// - ``GENERATES_PDF`` (2) — Generates a valid PDF (50%)
/// - ``CONTENT_VERIFIED`` (3) — Content verified with parser (75%)
/// - ``ISO_COMPLIANT`` (4) — ISO compliant with external validation (100%)
#[pyclass(name = "VerificationLevel", frozen)]
#[derive(Clone, Copy)]
pub struct PyVerificationLevel {
    pub inner: VerificationLevel,
}

#[pymethods]
impl PyVerificationLevel {
    /// Not implemented — 0% compliance.
    #[classattr]
    const NOT_IMPLEMENTED: Self = Self { inner: VerificationLevel::NotImplemented };

    /// Code exists, doesn't crash — 25% compliance.
    #[classattr]
    const CODE_EXISTS: Self = Self { inner: VerificationLevel::CodeExists };

    /// Generates valid PDF — 50% compliance.
    #[classattr]
    const GENERATES_PDF: Self = Self { inner: VerificationLevel::GeneratesPdf };

    /// Content verified with parser — 75% compliance.
    #[classattr]
    const CONTENT_VERIFIED: Self = Self { inner: VerificationLevel::ContentVerified };

    /// ISO compliant with external validation — 100% compliance.
    #[classattr]
    const ISO_COMPLIANT: Self = Self { inner: VerificationLevel::IsoCompliant };

    /// Return the compliance percentage for this level (0.0–100.0).
    #[getter]
    fn as_percentage(&self) -> f64 {
        self.inner.as_percentage()
    }

    fn __repr__(&self) -> String {
        let name = match self.inner {
            VerificationLevel::NotImplemented => "NOT_IMPLEMENTED",
            VerificationLevel::CodeExists => "CODE_EXISTS",
            VerificationLevel::GeneratesPdf => "GENERATES_PDF",
            VerificationLevel::ContentVerified => "CONTENT_VERIFIED",
            VerificationLevel::IsoCompliant => "ISO_COMPLIANT",
        };
        format!("VerificationLevel.{name}")
    }
}

// ── ComplianceStats ─────────────────────────────────────────────────────────

/// Aggregate compliance statistics calculated from the ISO compliance matrix.
#[pyclass(name = "ComplianceStats", frozen)]
#[derive(Clone)]
pub struct PyComplianceStats {
    pub inner: ComplianceStats,
}

#[pymethods]
impl PyComplianceStats {
    /// Total number of tracked ISO requirements.
    #[getter]
    fn total_requirements(&self) -> u32 {
        self.inner.total_requirements
    }

    /// Number of requirements with at least level 1 (CodeExists).
    #[getter]
    fn implemented_requirements(&self) -> u32 {
        self.inner.implemented_requirements
    }

    /// Average compliance percentage across all requirements (0.0–100.0).
    #[getter]
    fn average_compliance_percentage(&self) -> f64 {
        self.inner.average_compliance_percentage
    }

    /// Number of requirements at level 0 (NotImplemented).
    #[getter]
    fn level_0_count(&self) -> u32 {
        self.inner.level_0_count
    }

    /// Number of requirements at level 1 (CodeExists).
    #[getter]
    fn level_1_count(&self) -> u32 {
        self.inner.level_1_count
    }

    /// Number of requirements at level 2 (GeneratesPdf).
    #[getter]
    fn level_2_count(&self) -> u32 {
        self.inner.level_2_count
    }

    /// Number of requirements at level 3 (ContentVerified).
    #[getter]
    fn level_3_count(&self) -> u32 {
        self.inner.level_3_count
    }

    /// Number of requirements at level 4 (IsoCompliant).
    #[getter]
    fn level_4_count(&self) -> u32 {
        self.inner.level_4_count
    }

    /// Return the average compliance percentage formatted for display (e.g. ``"73.5%"``).
    fn compliance_percentage_display(&self) -> String {
        self.inner.compliance_percentage_display()
    }

    /// Return the implementation percentage (requirements at level >= 1).
    fn implementation_percentage(&self) -> f64 {
        self.inner.implementation_percentage()
    }

    fn __repr__(&self) -> String {
        format!(
            "ComplianceStats(total={}, implemented={}, avg_compliance={:.1}%)",
            self.inner.total_requirements,
            self.inner.implemented_requirements,
            self.inner.average_compliance_percentage,
        )
    }
}

// ── IsoRequirement ──────────────────────────────────────────────────────────

/// An individual ISO 32000-1 requirement with its current verification status.
#[pyclass(name = "IsoRequirement", frozen)]
#[derive(Clone)]
pub struct PyIsoRequirement {
    pub inner: IsoRequirement,
}

#[pymethods]
impl PyIsoRequirement {
    /// Unique requirement identifier (e.g. ``"7.5.2.1"``).
    #[getter]
    fn id(&self) -> &str {
        &self.inner.id
    }

    /// Human-readable requirement name.
    #[getter]
    fn name(&self) -> &str {
        &self.inner.name
    }

    /// Detailed description of the requirement.
    #[getter]
    fn description(&self) -> &str {
        &self.inner.description
    }

    /// ISO section reference (e.g. ``"7.5.2, Table 3.25"``).
    #[getter]
    fn iso_reference(&self) -> &str {
        &self.inner.iso_reference
    }

    /// Implementation note, if available.
    #[getter]
    fn implementation(&self) -> Option<&str> {
        self.inner.implementation.as_deref()
    }

    /// Test file path, if available.
    #[getter]
    fn test_file(&self) -> Option<&str> {
        self.inner.test_file.as_deref()
    }

    /// Current verification level for this requirement.
    #[getter]
    fn level(&self) -> PyVerificationLevel {
        PyVerificationLevel { inner: self.inner.level }
    }

    /// Whether the requirement has been verified.
    #[getter]
    fn verified(&self) -> bool {
        self.inner.verified
    }

    /// Additional notes about the requirement or implementation.
    #[getter]
    fn notes(&self) -> &str {
        &self.inner.notes
    }

    fn __repr__(&self) -> String {
        format!(
            "IsoRequirement(id={:?}, level={:?}, verified={})",
            self.inner.id,
            self.inner.level.as_percentage(),
            self.inner.verified,
        )
    }
}

// ── RequirementInfo ─────────────────────────────────────────────────────────

/// Combined requirement information merging matrix definition with current status.
#[pyclass(name = "RequirementInfo", frozen)]
#[derive(Clone)]
pub struct PyRequirementInfo {
    pub inner: RequirementInfo,
}

#[pymethods]
impl PyRequirementInfo {
    /// Unique requirement identifier.
    #[getter]
    fn id(&self) -> &str {
        &self.inner.id
    }

    /// Human-readable requirement name.
    #[getter]
    fn name(&self) -> &str {
        &self.inner.name
    }

    /// Detailed description of the requirement.
    #[getter]
    fn description(&self) -> &str {
        &self.inner.description
    }

    /// ISO section reference.
    #[getter]
    fn iso_reference(&self) -> &str {
        &self.inner.iso_reference
    }

    /// Requirement type (``"mandatory"``, ``"optional"``, etc.).
    #[getter]
    fn requirement_type(&self) -> &str {
        &self.inner.requirement_type
    }

    /// Page number in ISO 32000-1 specification.
    #[getter]
    fn page(&self) -> u32 {
        self.inner.page
    }

    /// Verification level as a raw integer (0–4).
    #[getter]
    fn level(&self) -> u8 {
        self.inner.level
    }

    /// Implementation path or module reference.
    #[getter]
    fn implementation(&self) -> &str {
        &self.inner.implementation
    }

    /// Test file path.
    #[getter]
    fn test_file(&self) -> &str {
        &self.inner.test_file
    }

    /// Whether the requirement has been verified.
    #[getter]
    fn verified(&self) -> bool {
        self.inner.verified
    }

    /// Date when the requirement was last checked.
    #[getter]
    fn last_checked(&self) -> &str {
        &self.inner.last_checked
    }

    /// Additional notes.
    #[getter]
    fn notes(&self) -> &str {
        &self.inner.notes
    }

    fn __repr__(&self) -> String {
        format!(
            "RequirementInfo(id={:?}, level={}, verified={})",
            self.inner.id, self.inner.level, self.inner.verified,
        )
    }
}

// ── ComplianceSystem ────────────────────────────────────────────────────────

/// Combined compliance system that merges ISO matrix definitions with verification status.
///
/// Loaded from two TOML files: ``ISO_COMPLIANCE_MATRIX.toml`` (immutable definitions)
/// and ``ISO_VERIFICATION_STATUS.toml`` (mutable status). Use ``load()`` to instantiate.
///
/// Example::
///
///     system = ComplianceSystem.load(
///         matrix_path="ISO_COMPLIANCE_MATRIX.toml",
///         status_path="ISO_VERIFICATION_STATUS.toml",
///     )
///     stats = system.calculate_compliance_stats()
///     print(stats.compliance_percentage_display())
#[pyclass(name = "ComplianceSystem")]
pub struct PyComplianceSystem {
    pub inner: ComplianceSystem,
}

#[pymethods]
impl PyComplianceSystem {
    /// Load the compliance system from two TOML files.
    ///
    /// ``matrix_path`` points to the immutable ISO matrix file.
    /// ``status_path`` points to the mutable verification status file.
    #[staticmethod]
    fn load(matrix_path: &str, status_path: &str) -> PyResult<Self> {
        use oxidize_pdf::verification::iso_matrix::load_verification_status;
        use oxidize_pdf::load_matrix;
        let matrix = load_matrix(matrix_path)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        let status = load_verification_status(status_path)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok(Self { inner: ComplianceSystem { matrix, status } })
    }

    /// Calculate compliance statistics from the current status.
    fn calculate_compliance_stats(&self) -> PyComplianceStats {
        PyComplianceStats { inner: self.inner.calculate_compliance_stats() }
    }

    /// Return all requirements with their current verification status.
    fn get_all_requirements(&self) -> Vec<PyIsoRequirement> {
        self.inner
            .get_all_requirements()
            .into_iter()
            .map(|r| PyIsoRequirement { inner: r })
            .collect()
    }

    /// Return combined definition + status for a single requirement by ID.
    fn get_requirement_info(&self, id: &str) -> Option<PyRequirementInfo> {
        self.inner
            .get_requirement_info(id)
            .map(|r| PyRequirementInfo { inner: r })
    }

    /// Return requirements for a specific section (e.g. ``"section_7_5"``).
    fn get_section_requirements(&self, section_id: &str) -> Option<Vec<PyIsoRequirement>> {
        self.inner
            .get_section_requirements(section_id)
            .map(|reqs| reqs.into_iter().map(|r| PyIsoRequirement { inner: r }).collect())
    }

    /// Return requirements with level 0 (NotImplemented).
    fn get_unimplemented_requirements(&self) -> Vec<PyIsoRequirement> {
        self.inner
            .get_unimplemented_requirements()
            .into_iter()
            .map(|r| PyIsoRequirement { inner: r })
            .collect()
    }

    /// Return requirements at level 1 or 2 (partially implemented).
    fn get_partially_implemented_requirements(&self) -> Vec<PyIsoRequirement> {
        self.inner
            .get_partially_implemented_requirements()
            .into_iter()
            .map(|r| PyIsoRequirement { inner: r })
            .collect()
    }

    /// Return requirements at level 4 (IsoCompliant).
    fn get_compliant_requirements(&self) -> Vec<PyIsoRequirement> {
        self.inner
            .get_compliant_requirements()
            .into_iter()
            .map(|r| PyIsoRequirement { inner: r })
            .collect()
    }

    fn __repr__(&self) -> String {
        let stats = self.inner.calculate_compliance_stats();
        format!(
            "ComplianceSystem(requirements={}, compliance={})",
            stats.total_requirements,
            stats.compliance_percentage_display(),
        )
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// F80 — PDF Comparison Deep
// ═══════════════════════════════════════════════════════════════════════════

// ── DifferenceSeverity ──────────────────────────────────────────────────────

/// Severity level of a detected difference between two PDFs.
///
/// Variants:
///
/// - ``CRITICAL`` — breaks ISO compliance
/// - ``IMPORTANT`` — may affect functionality
/// - ``MINOR`` — does not affect compliance
/// - ``COSMETIC`` — timestamps, IDs, whitespace, etc.
#[pyclass(name = "DifferenceSeverity", frozen)]
#[derive(Clone)]
pub struct PyDifferenceSeverity {
    pub inner: DifferenceSeverity,
}

#[pymethods]
impl PyDifferenceSeverity {
    /// Critical difference — breaks ISO compliance.
    #[classattr]
    #[allow(non_snake_case)]
    fn CRITICAL() -> Self {
        Self { inner: DifferenceSeverity::Critical }
    }

    /// Important difference — may affect functionality.
    #[classattr]
    #[allow(non_snake_case)]
    fn IMPORTANT() -> Self {
        Self { inner: DifferenceSeverity::Important }
    }

    /// Minor difference — does not affect compliance.
    #[classattr]
    #[allow(non_snake_case)]
    fn MINOR() -> Self {
        Self { inner: DifferenceSeverity::Minor }
    }

    /// Cosmetic difference — timestamps, IDs, whitespace, etc.
    #[classattr]
    #[allow(non_snake_case)]
    fn COSMETIC() -> Self {
        Self { inner: DifferenceSeverity::Cosmetic }
    }

    fn __repr__(&self) -> String {
        let name = match self.inner {
            DifferenceSeverity::Critical => "CRITICAL",
            DifferenceSeverity::Important => "IMPORTANT",
            DifferenceSeverity::Minor => "MINOR",
            DifferenceSeverity::Cosmetic => "COSMETIC",
        };
        format!("DifferenceSeverity.{name}")
    }
}

// ── PdfDifference ───────────────────────────────────────────────────────────

/// A single detected difference between two PDFs.
#[pyclass(name = "PdfDifference", frozen)]
#[derive(Clone)]
pub struct PyPdfDifference {
    pub inner: PdfDifference,
}

#[pymethods]
impl PyPdfDifference {
    /// Location in the PDF where the difference was found.
    #[getter]
    fn location(&self) -> &str {
        &self.inner.location
    }

    /// Expected value (from the reference PDF).
    #[getter]
    fn expected(&self) -> &str {
        &self.inner.expected
    }

    /// Actual value (from the generated PDF).
    #[getter]
    fn actual(&self) -> &str {
        &self.inner.actual
    }

    /// Severity of this difference.
    #[getter]
    fn severity(&self) -> PyDifferenceSeverity {
        PyDifferenceSeverity { inner: self.inner.severity.clone() }
    }

    fn __repr__(&self) -> String {
        let severity_name = match self.inner.severity {
            DifferenceSeverity::Critical => "CRITICAL",
            DifferenceSeverity::Important => "IMPORTANT",
            DifferenceSeverity::Minor => "MINOR",
            DifferenceSeverity::Cosmetic => "COSMETIC",
        };
        format!(
            "PdfDifference(location={:?}, severity={})",
            self.inner.location, severity_name,
        )
    }
}

// ── ComparisonResult ────────────────────────────────────────────────────────

/// Result of a deep PDF comparison between a generated and a reference PDF.
#[pyclass(name = "ComparisonResult", frozen)]
#[derive(Clone)]
pub struct PyComparisonResult {
    pub inner: ComparisonResult,
}

#[pymethods]
impl PyComparisonResult {
    /// ``True`` if both PDFs are structurally equivalent (only minor/cosmetic differences).
    #[getter]
    fn structurally_equivalent(&self) -> bool {
        self.inner.structurally_equivalent
    }

    /// ``True`` if both PDFs are content-equivalent (only cosmetic differences).
    #[getter]
    fn content_equivalent(&self) -> bool {
        self.inner.content_equivalent
    }

    /// List of all detected differences.
    #[getter]
    fn differences(&self) -> Vec<PyPdfDifference> {
        self.inner
            .differences
            .iter()
            .map(|d| PyPdfDifference { inner: d.clone() })
            .collect()
    }

    /// Similarity score between 0.0 (completely different) and 1.0 (identical).
    #[getter]
    fn similarity_score(&self) -> f64 {
        self.inner.similarity_score
    }

    fn __repr__(&self) -> String {
        format!(
            "ComparisonResult(structurally_equivalent={}, similarity_score={:.3}, differences={})",
            self.inner.structurally_equivalent,
            self.inner.similarity_score,
            self.inner.differences.len(),
        )
    }
}

// ── Standalone Functions ─────────────────────────────────────────────────────

/// Perform a deep comparison of two PDFs, returning a ``ComparisonResult``.
///
/// ``generated`` and ``reference`` are raw PDF bytes.
/// Raises ``RuntimeError`` if either PDF cannot be parsed.
#[pyfunction]
fn compare_pdfs_deep_py(generated: &[u8], reference: &[u8]) -> PyResult<PyComparisonResult> {
    compare_pdfs(generated, reference)
        .map(|r| PyComparisonResult { inner: r })
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
}

/// Extract the list of differences between two PDFs without a full comparison result.
///
/// ``generated`` and ``reference`` are raw PDF bytes.
/// Raises ``RuntimeError`` if either PDF cannot be parsed.
#[pyfunction]
fn extract_pdf_differences_py(generated: &[u8], reference: &[u8]) -> PyResult<Vec<PyPdfDifference>> {
    extract_pdf_differences(generated, reference)
        .map(|diffs| diffs.into_iter().map(|d| PyPdfDifference { inner: d }).collect())
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
}

/// Return ``True`` if the two PDFs are structurally equivalent.
///
/// This is a quick boolean check that ignores minor and cosmetic differences.
#[pyfunction]
fn pdfs_structurally_equivalent_py(generated: &[u8], reference: &[u8]) -> bool {
    pdfs_structurally_equivalent(generated, reference)
}

// ── Register ─────────────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // F79 types
    m.add_class::<PyVerificationLevel>()?;
    m.add_class::<PyComplianceStats>()?;
    m.add_class::<PyIsoRequirement>()?;
    m.add_class::<PyRequirementInfo>()?;
    m.add_class::<PyComplianceSystem>()?;
    // F80 types
    m.add_class::<PyDifferenceSeverity>()?;
    m.add_class::<PyPdfDifference>()?;
    m.add_class::<PyComparisonResult>()?;
    // F80 functions
    m.add_function(wrap_pyfunction!(compare_pdfs_deep_py, m)?)?;
    m.add_function(wrap_pyfunction!(extract_pdf_differences_py, m)?)?;
    m.add_function(wrap_pyfunction!(pdfs_structurally_equivalent_py, m)?)?;
    Ok(())
}
