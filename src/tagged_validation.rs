//! Bounded tagged-PDF inspection. Structural validity is not PDF/UA certification.
use crate::errors::to_py_err;
use crate::signing::{dictionary_values, PyPdfValue};
use oxidize_pdf::verification::tagged_pdf as core;
use pyo3::prelude::*;
use std::collections::HashMap;

#[pyclass(name = "TaggedPdfFindingSeverity", frozen, eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyTaggedPdfFindingSeverity {
    Error,
    Warning,
}
impl From<core::TaggedPdfFindingSeverity> for PyTaggedPdfFindingSeverity {
    fn from(value: core::TaggedPdfFindingSeverity) -> Self {
        match value {
            core::TaggedPdfFindingSeverity::Error => Self::Error,
            core::TaggedPdfFindingSeverity::Warning => Self::Warning,
        }
    }
}
#[pyclass(name = "TaggedPdfFindingCode", frozen, eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyTaggedPdfFindingCode {
    MissingStructureTree,
    InvalidStructureTreeRoot,
    InvalidStructureElement,
    DirectStructureElement,
    MissingStructureType,
    BrokenParentLink,
    DuplicateStructureReference,
    StructureCycle,
    InvalidMarkedContentReference,
    MissingMarkedContent,
    InvalidObjectReference,
    MissingParentTree,
    InvalidParentTree,
    MissingStructParents,
    MissingParentTreeEntry,
    ParentTreeOwnerMismatch,
    UnmappedCustomRole,
    InvalidRoleMap,
    InvalidClassMap,
    InvalidReadingOrder,
    InvalidTableStructure,
    InvalidListStructure,
    InvalidLinkStructure,
    InvalidArtifact,
    MissingDocumentLanguage,
    MissingAlternateText,
    InvalidHeadingOrder,
}
impl From<core::TaggedPdfFindingCode> for PyTaggedPdfFindingCode {
    fn from(value: core::TaggedPdfFindingCode) -> Self {
        match value {
            core::TaggedPdfFindingCode::MissingStructureTree => Self::MissingStructureTree,
            core::TaggedPdfFindingCode::InvalidStructureTreeRoot => Self::InvalidStructureTreeRoot,
            core::TaggedPdfFindingCode::InvalidStructureElement => Self::InvalidStructureElement,
            core::TaggedPdfFindingCode::DirectStructureElement => Self::DirectStructureElement,
            core::TaggedPdfFindingCode::MissingStructureType => Self::MissingStructureType,
            core::TaggedPdfFindingCode::BrokenParentLink => Self::BrokenParentLink,
            core::TaggedPdfFindingCode::DuplicateStructureReference => {
                Self::DuplicateStructureReference
            }
            core::TaggedPdfFindingCode::StructureCycle => Self::StructureCycle,
            core::TaggedPdfFindingCode::InvalidMarkedContentReference => {
                Self::InvalidMarkedContentReference
            }
            core::TaggedPdfFindingCode::MissingMarkedContent => Self::MissingMarkedContent,
            core::TaggedPdfFindingCode::InvalidObjectReference => Self::InvalidObjectReference,
            core::TaggedPdfFindingCode::MissingParentTree => Self::MissingParentTree,
            core::TaggedPdfFindingCode::InvalidParentTree => Self::InvalidParentTree,
            core::TaggedPdfFindingCode::MissingStructParents => Self::MissingStructParents,
            core::TaggedPdfFindingCode::MissingParentTreeEntry => Self::MissingParentTreeEntry,
            core::TaggedPdfFindingCode::ParentTreeOwnerMismatch => Self::ParentTreeOwnerMismatch,
            core::TaggedPdfFindingCode::UnmappedCustomRole => Self::UnmappedCustomRole,
            core::TaggedPdfFindingCode::InvalidRoleMap => Self::InvalidRoleMap,
            core::TaggedPdfFindingCode::InvalidClassMap => Self::InvalidClassMap,
            core::TaggedPdfFindingCode::InvalidReadingOrder => Self::InvalidReadingOrder,
            core::TaggedPdfFindingCode::InvalidTableStructure => Self::InvalidTableStructure,
            core::TaggedPdfFindingCode::InvalidListStructure => Self::InvalidListStructure,
            core::TaggedPdfFindingCode::InvalidLinkStructure => Self::InvalidLinkStructure,
            core::TaggedPdfFindingCode::InvalidArtifact => Self::InvalidArtifact,
            core::TaggedPdfFindingCode::MissingDocumentLanguage => Self::MissingDocumentLanguage,
            core::TaggedPdfFindingCode::MissingAlternateText => Self::MissingAlternateText,
            core::TaggedPdfFindingCode::InvalidHeadingOrder => Self::InvalidHeadingOrder,
        }
    }
}
#[pyclass(name = "TaggedPdfObjectRef", frozen, from_py_object, eq, hash)]
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
pub struct PyTaggedPdfObjectRef {
    inner: core::TaggedPdfObjectRef,
}
#[pymethods]
impl PyTaggedPdfObjectRef {
    #[new]
    fn new(object_number: u32, generation: u16) -> Self {
        Self {
            inner: core::TaggedPdfObjectRef {
                object_number,
                generation,
            },
        }
    }
    #[getter]
    fn object_number(&self) -> u32 {
        self.inner.object_number
    }
    #[getter]
    fn generation(&self) -> u16 {
        self.inner.generation
    }
}
#[pyclass(name = "TaggedPdfLimits", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTaggedPdfLimits {
    inner: core::TaggedPdfLimits,
}
#[pymethods]
impl PyTaggedPdfLimits {
    #[new]
    #[pyo3(signature=(*,max_objects=100_000,max_depth=256,max_entries=1_000_000,max_decoded_content_bytes=268_435_456))]
    fn new(
        max_objects: usize,
        max_depth: usize,
        max_entries: usize,
        max_decoded_content_bytes: usize,
    ) -> Self {
        Self {
            inner: core::TaggedPdfLimits {
                max_objects,
                max_depth,
                max_entries,
                max_decoded_content_bytes,
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
    fn max_entries(&self) -> usize {
        self.inner.max_entries
    }
    #[getter]
    fn max_decoded_content_bytes(&self) -> usize {
        self.inner.max_decoded_content_bytes
    }
}
#[pyclass(name = "TaggedPdfValidationOptions", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTaggedPdfValidationOptions {
    inner: core::TaggedPdfValidationOptions,
}
#[pymethods]
impl PyTaggedPdfValidationOptions {
    #[new]
    #[pyo3(signature=(limits=None))]
    fn new(limits: Option<PyTaggedPdfLimits>) -> Self {
        Self {
            inner: core::TaggedPdfValidationOptions {
                limits: limits.map(|v| v.inner).unwrap_or_default(),
            },
        }
    }
    #[getter]
    fn limits(&self) -> PyTaggedPdfLimits {
        PyTaggedPdfLimits {
            inner: self.inner.limits.clone(),
        }
    }
}
#[pyclass(name = "TaggedPdfFinding", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTaggedPdfFinding {
    inner: core::TaggedPdfFinding,
}
#[pymethods]
impl PyTaggedPdfFinding {
    #[getter]
    fn severity(&self) -> PyTaggedPdfFindingSeverity {
        self.inner.severity.into()
    }
    #[getter]
    fn code(&self) -> PyTaggedPdfFindingCode {
        self.inner.code.into()
    }
    #[getter]
    fn path(&self) -> String {
        self.inner.path.clone()
    }
    #[getter]
    fn message(&self) -> String {
        self.inner.message.clone()
    }
    #[getter]
    fn object(&self) -> Option<PyTaggedPdfObjectRef> {
        self.inner
            .object
            .map(|inner| PyTaggedPdfObjectRef { inner })
    }
}
#[pyclass(name = "TaggedPdfStructureElement", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTaggedPdfStructureElement {
    inner: core::TaggedPdfStructureElement,
}
#[pymethods]
impl PyTaggedPdfStructureElement {
    #[getter]
    fn object(&self) -> PyTaggedPdfObjectRef {
        PyTaggedPdfObjectRef {
            inner: self.inner.object,
        }
    }
    #[getter]
    fn parent(&self) -> Option<PyTaggedPdfObjectRef> {
        self.inner
            .parent
            .map(|inner| PyTaggedPdfObjectRef { inner })
    }
    #[getter]
    fn structure_type(&self) -> Option<String> {
        self.inner.structure_type.clone()
    }
    #[getter]
    fn language(&self) -> Option<String> {
        self.inner.language.clone()
    }
    #[getter]
    fn alternate_text(&self) -> Option<String> {
        self.inner.alternate_text.clone()
    }
    #[getter]
    fn actual_text(&self) -> Option<String> {
        self.inner.actual_text.clone()
    }
    #[getter]
    fn title(&self) -> Option<String> {
        self.inner.title.clone()
    }
    #[getter]
    fn child_count(&self) -> usize {
        self.inner.child_count
    }
    #[getter]
    fn marked_content_count(&self) -> usize {
        self.inner.marked_content_count
    }
    #[getter]
    fn dictionary_keys(&self) -> Vec<String> {
        self.inner.dictionary_keys.clone()
    }
    #[getter]
    fn dictionary(&self) -> HashMap<String, PyPdfValue> {
        dictionary_values(&self.inner.dictionary)
    }
}
#[pyclass(name = "TaggedPdfArtifact", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTaggedPdfArtifact {
    inner: core::TaggedPdfArtifact,
}
#[pymethods]
impl PyTaggedPdfArtifact {
    #[getter]
    fn context(&self) -> PyTaggedPdfObjectRef {
        PyTaggedPdfObjectRef {
            inner: self.inner.context,
        }
    }
    #[getter]
    fn operation_index(&self) -> usize {
        self.inner.operation_index
    }
    #[getter]
    fn subtype(&self) -> Option<String> {
        self.inner.subtype.clone()
    }
}
#[pyclass(name = "TaggedPdfValidationReport", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTaggedPdfValidationReport {
    inner: core::TaggedPdfValidationReport,
}
#[pymethods]
impl PyTaggedPdfValidationReport {
    #[getter]
    fn tagged(&self) -> bool {
        self.inner.tagged
    }
    #[getter]
    fn valid(&self) -> bool {
        self.inner.valid
    }
    #[getter]
    fn structure_tree_root(&self) -> Option<PyTaggedPdfObjectRef> {
        self.inner
            .structure_tree_root
            .map(|inner| PyTaggedPdfObjectRef { inner })
    }
    #[getter]
    fn role_map(&self) -> HashMap<String, String> {
        self.inner.role_map.clone().into_iter().collect()
    }
    #[getter]
    fn class_names(&self) -> Vec<String> {
        self.inner.class_names.clone()
    }
    #[getter]
    fn class_map(&self) -> HashMap<String, PyPdfValue> {
        self.inner
            .class_map
            .iter()
            .map(|(k, v)| (k.clone(), PyPdfValue { inner: v.clone() }))
            .collect()
    }
    #[getter]
    fn parent_tree_entries(&self) -> usize {
        self.inner.parent_tree_entries
    }
    #[getter]
    fn parent_tree(&self) -> HashMap<i64, PyPdfValue> {
        self.inner
            .parent_tree
            .iter()
            .map(|(k, v)| (*k, PyPdfValue { inner: v.clone() }))
            .collect()
    }
    #[getter]
    fn content_mcids(&self) -> HashMap<PyTaggedPdfObjectRef, Vec<i64>> {
        self.inner
            .content_mcids
            .iter()
            .map(|(k, v)| (PyTaggedPdfObjectRef { inner: *k }, v.clone()))
            .collect()
    }
    #[getter]
    fn artifacts(&self) -> Vec<PyTaggedPdfArtifact> {
        self.inner
            .artifacts
            .iter()
            .cloned()
            .map(|inner| PyTaggedPdfArtifact { inner })
            .collect()
    }
    #[getter]
    fn elements(&self) -> Vec<PyTaggedPdfStructureElement> {
        self.inner
            .elements
            .iter()
            .cloned()
            .map(|inner| PyTaggedPdfStructureElement { inner })
            .collect()
    }
    #[getter]
    fn findings(&self) -> Vec<PyTaggedPdfFinding> {
        self.inner
            .findings
            .iter()
            .cloned()
            .map(|inner| PyTaggedPdfFinding { inner })
            .collect()
    }
}
/// Inspect immutable PDF bytes with explicit budgets. Findings are not errors;
/// malformed/locked input and exceeded budgets propagate as Python exceptions.
/// `valid` does not certify PDF/UA and can be true for an untagged document.
#[pyfunction]
#[pyo3(signature=(pdf,options=None))]
fn validate_tagged_pdf(
    py: Python<'_>,
    pdf: &[u8],
    options: Option<PyTaggedPdfValidationOptions>,
) -> PyResult<PyTaggedPdfValidationReport> {
    let bytes = pdf.to_vec();
    let options = options.map(|v| v.inner).unwrap_or_default();
    let inner = py
        .detach(|| core::validate_tagged_pdf(&bytes, &options))
        .map_err(to_py_err)?;
    Ok(PyTaggedPdfValidationReport { inner })
}
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTaggedPdfFindingSeverity>()?;
    m.add_class::<PyTaggedPdfFindingCode>()?;
    m.add_class::<PyTaggedPdfObjectRef>()?;
    m.add_class::<PyTaggedPdfLimits>()?;
    m.add_class::<PyTaggedPdfValidationOptions>()?;
    m.add_class::<PyTaggedPdfFinding>()?;
    m.add_class::<PyTaggedPdfStructureElement>()?;
    m.add_class::<PyTaggedPdfArtifact>()?;
    m.add_class::<PyTaggedPdfValidationReport>()?;
    m.add_function(wrap_pyfunction!(validate_tagged_pdf, m)?)?;
    Ok(())
}
