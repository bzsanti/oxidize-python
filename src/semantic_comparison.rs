//! Bounded, revision-aware comparison over owned PDF byte snapshots.
use crate::errors::to_py_err;
use oxidize_pdf::verification::semantic_comparison as core;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
#[pyclass(name = "SemanticDifferenceClass", frozen, eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PySemanticDifferenceClass {
    Visual,
    Textual,
    Structural,
    Metadata,
    Security,
    SerializationOnly,
}
impl From<core::SemanticDifferenceClass> for PySemanticDifferenceClass {
    fn from(value: core::SemanticDifferenceClass) -> Self {
        match value {
            core::SemanticDifferenceClass::Visual => Self::Visual,
            core::SemanticDifferenceClass::Textual => Self::Textual,
            core::SemanticDifferenceClass::Structural => Self::Structural,
            core::SemanticDifferenceClass::Metadata => Self::Metadata,
            core::SemanticDifferenceClass::Security => Self::Security,
            core::SemanticDifferenceClass::SerializationOnly => Self::SerializationOnly,
        }
    }
}
#[pyclass(name = "RevisionObjectChangeKind", frozen, eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyRevisionObjectChangeKind {
    Added,
    Replaced,
    Freed,
}
impl From<core::RevisionObjectChangeKind> for PyRevisionObjectChangeKind {
    fn from(value: core::RevisionObjectChangeKind) -> Self {
        match value {
            core::RevisionObjectChangeKind::Added => Self::Added,
            core::RevisionObjectChangeKind::Replaced => Self::Replaced,
            core::RevisionObjectChangeKind::Freed => Self::Freed,
        }
    }
}
#[pyclass(name = "SemanticComparisonLimits", frozen, from_py_object)]
#[derive(Clone)]
pub struct PySemanticComparisonLimits {
    inner: core::SemanticComparisonLimits,
}
#[pymethods]
impl PySemanticComparisonLimits {
    #[new]
    #[pyo3(signature=(*,max_objects=100000,max_depth=256,max_decoded_stream_bytes=268435456,max_canonical_bytes=268435456,max_extracted_text_bytes=67108864,max_unreachable_objects=10000,max_revisions=1024))]
    fn new(
        max_objects: usize,
        max_depth: usize,
        max_decoded_stream_bytes: usize,
        max_canonical_bytes: usize,
        max_extracted_text_bytes: usize,
        max_unreachable_objects: usize,
        max_revisions: usize,
    ) -> Self {
        Self {
            inner: core::SemanticComparisonLimits {
                max_objects,
                max_depth,
                max_decoded_stream_bytes,
                max_canonical_bytes,
                max_extracted_text_bytes,
                max_unreachable_objects,
                max_revisions,
            },
        }
    }
    #[getter]
    fn max_objects(&self) -> usize {
        self.inner.max_objects
    }
    #[getter]
    fn max_depth(&self) -> usize {
        self.inner.max_depth
    }
    #[getter]
    fn max_decoded_stream_bytes(&self) -> usize {
        self.inner.max_decoded_stream_bytes
    }
    #[getter]
    fn max_canonical_bytes(&self) -> usize {
        self.inner.max_canonical_bytes
    }
    #[getter]
    fn max_extracted_text_bytes(&self) -> usize {
        self.inner.max_extracted_text_bytes
    }
    #[getter]
    fn max_unreachable_objects(&self) -> usize {
        self.inner.max_unreachable_objects
    }
    #[getter]
    fn max_revisions(&self) -> usize {
        self.inner.max_revisions
    }
}
#[pyclass(name = "SemanticComparisonOptions", frozen, from_py_object)]
#[derive(Clone)]
pub struct PySemanticComparisonOptions {
    inner: core::SemanticComparisonOptions,
}
#[pymethods]
impl PySemanticComparisonOptions {
    #[new]
    #[pyo3(signature=(limits=None))]
    fn new(limits: Option<PySemanticComparisonLimits>) -> Self {
        Self {
            inner: core::SemanticComparisonOptions {
                limits: limits.map(|v| v.inner).unwrap_or_default(),
            },
        }
    }
    #[getter]
    fn limits(&self) -> PySemanticComparisonLimits {
        PySemanticComparisonLimits {
            inner: self.inner.limits.clone(),
        }
    }
}
#[pyclass(name = "SemanticPdfDifference", frozen, from_py_object)]
#[derive(Clone)]
pub struct PySemanticPdfDifference {
    inner: core::SemanticPdfDifference,
}
#[pymethods]
impl PySemanticPdfDifference {
    #[getter]
    fn path(&self) -> String {
        self.inner.path.clone()
    }
    #[getter]
    fn class_(&self) -> PySemanticDifferenceClass {
        self.inner.r#class.into()
    }
    #[getter]
    fn description(&self) -> String {
        self.inner.description.clone()
    }
}
#[pyclass(name = "RevisionObjectChange", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyRevisionObjectChange {
    inner: core::RevisionObjectChange,
}
#[pymethods]
impl PyRevisionObjectChange {
    #[getter]
    fn object_number(&self) -> u32 {
        self.inner.object_number
    }
    #[getter]
    fn generation(&self) -> u16 {
        self.inner.generation
    }
    #[getter]
    fn kind(&self) -> PyRevisionObjectChangeKind {
        self.inner.kind.into()
    }
}
#[pyclass(name = "PdfRevisionSummary", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyPdfRevisionSummary {
    inner: core::PdfRevisionSummary,
}
#[pymethods]
impl PyPdfRevisionSummary {
    #[getter]
    fn index(&self) -> usize {
        self.inner.index
    }
    #[getter]
    fn xref_offset(&self) -> u64 {
        self.inner.xref_offset
    }
    #[getter]
    fn object_changes(&self) -> Vec<PyRevisionObjectChange> {
        self.inner
            .object_changes
            .iter()
            .cloned()
            .map(|inner| PyRevisionObjectChange { inner })
            .collect()
    }
    #[getter]
    fn semantic_fingerprint<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.inner.semantic_fingerprint)
    }
}
#[pyclass(name = "SemanticComparisonResult", frozen, from_py_object)]
#[derive(Clone)]
pub struct PySemanticComparisonResult {
    inner: core::SemanticComparisonResult,
}
#[pymethods]
impl PySemanticComparisonResult {
    #[getter]
    fn semantically_equal(&self) -> bool {
        self.inner.semantically_equal
    }
    #[getter]
    fn differences(&self) -> Vec<PySemanticPdfDifference> {
        self.inner
            .differences
            .iter()
            .cloned()
            .map(|inner| PySemanticPdfDifference { inner })
            .collect()
    }
    #[getter]
    fn left_revisions(&self) -> Vec<PyPdfRevisionSummary> {
        self.inner
            .left_revisions
            .iter()
            .cloned()
            .map(|inner| PyPdfRevisionSummary { inner })
            .collect()
    }
    #[getter]
    fn right_revisions(&self) -> Vec<PyPdfRevisionSummary> {
        self.inner
            .right_revisions
            .iter()
            .cloned()
            .map(|inner| PyPdfRevisionSummary { inner })
            .collect()
    }
    #[getter]
    fn left_unreachable_objects(&self) -> Vec<(u32, u16)> {
        self.inner.left_unreachable_objects.clone()
    }
    #[getter]
    fn right_unreachable_objects(&self) -> Vec<(u32, u16)> {
        self.inner.right_unreachable_objects.clone()
    }
    #[getter]
    fn semantically_equivalent_objects(&self) -> Vec<((u32, u16), (u32, u16))> {
        self.inner.semantically_equivalent_objects.clone()
    }
}
/// Compare supported semantic domains and physical revision histories.
/// Limits do not bound input copies or all parser allocations. Not a renderer.
#[pyfunction]
#[pyo3(signature=(left,right,options=None))]
fn compare_pdfs_semantically(
    py: Python<'_>,
    left: &[u8],
    right: &[u8],
    options: Option<PySemanticComparisonOptions>,
) -> PyResult<PySemanticComparisonResult> {
    let left = left.to_vec();
    let right = right.to_vec();
    let options = options.map(|v| v.inner).unwrap_or_default();
    let inner = py
        .detach(|| core::compare_pdfs_semantically(&left, &right, &options))
        .map_err(to_py_err)?;
    Ok(PySemanticComparisonResult { inner })
}
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PySemanticDifferenceClass>()?;
    m.add_class::<PyRevisionObjectChangeKind>()?;
    m.add_class::<PySemanticComparisonLimits>()?;
    m.add_class::<PySemanticComparisonOptions>()?;
    m.add_class::<PySemanticPdfDifference>()?;
    m.add_class::<PyRevisionObjectChange>()?;
    m.add_class::<PyPdfRevisionSummary>()?;
    m.add_class::<PySemanticComparisonResult>()?;
    m.add_function(wrap_pyfunction!(compare_pdfs_semantically, m)?)?;
    Ok(())
}
