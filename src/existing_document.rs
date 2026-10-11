//! Explicit existing-document policies and complete planning reports.
use crate::operations::op_err_to_py;
use crate::operations::PyPageRange;
use oxidize_pdf::operations::{existing_document as core, PageMutationReport};
use pyo3::prelude::*;

#[pyclass(name = "DocumentStructure", eq, eq_int, frozen, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyDocumentStructure {
    Forms,
    Outlines,
    NamesAndAttachments,
    NamedDestinations,
    OptionalContent,
    StructureTree,
    MetadataStream,
    PageLabels,
    DigitalSignatures,
    Encryption,
    Annotations,
    DocumentInfo,
}
impl From<core::DocumentStructure> for PyDocumentStructure {
    fn from(v: core::DocumentStructure) -> Self {
        match v {
            core::DocumentStructure::Forms => Self::Forms,
            core::DocumentStructure::Outlines => Self::Outlines,
            core::DocumentStructure::NamesAndAttachments => Self::NamesAndAttachments,
            core::DocumentStructure::NamedDestinations => Self::NamedDestinations,
            core::DocumentStructure::OptionalContent => Self::OptionalContent,
            core::DocumentStructure::StructureTree => Self::StructureTree,
            core::DocumentStructure::MetadataStream => Self::MetadataStream,
            core::DocumentStructure::PageLabels => Self::PageLabels,
            core::DocumentStructure::DigitalSignatures => Self::DigitalSignatures,
            core::DocumentStructure::Encryption => Self::Encryption,
            core::DocumentStructure::Annotations => Self::Annotations,
            core::DocumentStructure::DocumentInfo => Self::DocumentInfo,
        }
    }
}

#[pyclass(name = "StructureDisposition", eq, eq_int, frozen, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyStructureDisposition {
    Preserved,
    FirstInputWins,
    Rejected,
    Discarded,
}
impl From<core::StructureDisposition> for PyStructureDisposition {
    fn from(v: core::StructureDisposition) -> Self {
        match v {
            core::StructureDisposition::Preserved => Self::Preserved,
            core::StructureDisposition::FirstInputWins => Self::FirstInputWins,
            core::StructureDisposition::Rejected => Self::Rejected,
            core::StructureDisposition::Discarded => Self::Discarded,
        }
    }
}

#[pyclass(name = "ExistingDocumentEngine", eq, eq_int, frozen, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyExistingDocumentEngine {
    PreserveBase,
    Reconstruct,
}
impl From<core::ExistingDocumentEngine> for PyExistingDocumentEngine {
    fn from(v: core::ExistingDocumentEngine) -> Self {
        match v {
            core::ExistingDocumentEngine::PreserveBase => Self::PreserveBase,
            core::ExistingDocumentEngine::Reconstruct => Self::Reconstruct,
        }
    }
}

#[pyclass(name = "InputSemanticRole", eq, eq_int, frozen, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyInputSemanticRole {
    PreservedBase,
    ImportedPages,
    ReconstructedPages,
}
impl From<core::InputSemanticRole> for PyInputSemanticRole {
    fn from(v: core::InputSemanticRole) -> Self {
        match v {
            core::InputSemanticRole::PreservedBase => Self::PreservedBase,
            core::InputSemanticRole::ImportedPages => Self::ImportedPages,
            core::InputSemanticRole::ReconstructedPages => Self::ReconstructedPages,
        }
    }
}

#[pyclass(name = "ExistingDocumentPolicy", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyExistingDocumentPolicy {
    inner: core::ExistingDocumentPolicy,
}
#[pymethods]
impl PyExistingDocumentPolicy {
    #[staticmethod]
    #[pyo3(signature=(page_labels_first_input_wins=false))]
    fn preserve_base(page_labels_first_input_wins: bool) -> Self {
        let inner = core::ExistingDocumentPolicy::preserve_base().with_page_labels(
            if page_labels_first_input_wins {
                core::DocumentStructurePolicy::FirstInputWins
            } else {
                core::DocumentStructurePolicy::Reject
            },
        );
        Self { inner }
    }
    #[staticmethod]
    #[pyo3(signature=(metadata_from_first=false))]
    fn reconstruct(metadata_from_first: bool) -> Self {
        Self {
            inner: if metadata_from_first {
                core::ExistingDocumentPolicy::reconstruct_with_metadata_from_first()
            } else {
                core::ExistingDocumentPolicy::reconstruct()
            },
        }
    }
}
#[pyclass(name = "ExistingDocumentMergeInput", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyExistingDocumentMergeInput {
    inner: core::ExistingDocumentMergeInput,
}
#[pymethods]
impl PyExistingDocumentMergeInput {
    #[new]
    #[pyo3(signature=(path, pages=None))]
    fn new(path: String, pages: Option<PyPageRange>) -> Self {
        Self {
            inner: core::ExistingDocumentMergeInput {
                path: path.into(),
                pages: pages.map(|p| p.inner),
            },
        }
    }
    #[getter]
    fn path(&self) -> String {
        self.inner.path.to_string_lossy().into_owned()
    }
    #[getter]
    fn pages(&self) -> Option<PyPageRange> {
        self.inner.pages.clone().map(|inner| PyPageRange { inner })
    }
}

#[pyclass(name = "PageMutationReport", frozen, from_py_object, get_all)]
#[derive(Clone)]
pub struct PyPageMutationReport {
    pub replaced_objects: Vec<(u32, u16)>,
    pub added_objects: Vec<(u32, u16)>,
    pub unreachable_objects: Vec<(u32, u16)>,
    pub page_count: usize,
}

#[pyclass(name = "StructureSemanticReport", frozen, from_py_object, get_all)]
#[derive(Clone)]
pub struct PyStructureSemanticReport {
    pub structure: PyDocumentStructure,
    pub disposition: PyStructureDisposition,
}

#[pyclass(name = "InputSemanticReport", frozen, from_py_object, get_all)]
#[derive(Clone)]
pub struct PyInputSemanticReport {
    pub path: String,
    pub role: PyInputSemanticRole,
    pub structures: Vec<PyStructureSemanticReport>,
    pub selected_pages: Vec<usize>,
}

#[pyclass(
    name = "ExistingDocumentExecutionPlan",
    frozen,
    from_py_object,
    get_all
)]
#[derive(Clone)]
pub struct PyExistingDocumentExecutionPlan {
    pub page_count: usize,
    pub incremental: Option<PyPageMutationReport>,
}

#[pyclass(name = "SemanticPreservationReport", frozen, from_py_object, get_all)]
#[derive(Clone)]
pub struct PySemanticPreservationReport {
    pub engine: PyExistingDocumentEngine,
    pub inputs: Vec<PyInputSemanticReport>,
    pub plan: PyExistingDocumentExecutionPlan,
}

impl From<PageMutationReport> for PyPageMutationReport {
    fn from(r: PageMutationReport) -> Self {
        Self {
            replaced_objects: r.replaced_objects,
            added_objects: r.added_objects,
            unreachable_objects: r.unreachable_objects,
            page_count: r.page_count,
        }
    }
}
impl From<core::SemanticPreservationReport> for PySemanticPreservationReport {
    fn from(r: core::SemanticPreservationReport) -> Self {
        let page_count = r.plan.page_count();
        let incremental = match r.plan {
            core::ExistingDocumentExecutionPlan::Incremental(p) => Some(p.into()),
            core::ExistingDocumentExecutionPlan::Reconstruct { .. } => None,
        };
        Self {
            engine: r.engine.into(),
            plan: PyExistingDocumentExecutionPlan {
                page_count,
                incremental,
            },
            inputs: r
                .inputs
                .into_iter()
                .map(|i| PyInputSemanticReport {
                    path: i.path.to_string_lossy().into_owned(),
                    role: i.role.into(),
                    selected_pages: i.selected_pages,
                    structures: i
                        .structures
                        .into_iter()
                        .map(|s| PyStructureSemanticReport {
                            structure: s.structure.into(),
                            disposition: s.disposition.into(),
                        })
                        .collect(),
                })
                .collect(),
        }
    }
}

#[pyfunction]
fn plan_merge_existing_pdfs(
    py: Python<'_>,
    inputs: Vec<PyExistingDocumentMergeInput>,
    policy: PyExistingDocumentPolicy,
) -> PyResult<PySemanticPreservationReport> {
    let inputs: Vec<_> = inputs.into_iter().map(|i| i.inner).collect();
    py.detach(move || core::plan_merge_pdfs(&inputs, policy.inner))
        .map(|r| r.into())
        .map_err(op_err_to_py)
}

#[pyfunction]
fn merge_existing_pdfs(
    py: Python<'_>,
    inputs: Vec<PyExistingDocumentMergeInput>,
    output: String,
    policy: PyExistingDocumentPolicy,
) -> PyResult<PySemanticPreservationReport> {
    let inputs: Vec<_> = inputs.into_iter().map(|i| i.inner).collect();
    py.detach(move || core::merge_pdfs(&inputs, output, policy.inner))
        .map(|r| r.into())
        .map_err(op_err_to_py)
}

#[pyfunction]
fn plan_extract_existing_pdf_pages(
    py: Python<'_>,
    input: String,
    pages: Vec<usize>,
    policy: PyExistingDocumentPolicy,
) -> PyResult<PySemanticPreservationReport> {
    py.detach(move || core::plan_extract_pdf_pages(input, &pages, policy.inner))
        .map(|r| r.into())
        .map_err(op_err_to_py)
}

#[pyfunction]
fn extract_existing_pdf_pages(
    py: Python<'_>,
    input: String,
    pages: Vec<usize>,
    output: String,
    policy: PyExistingDocumentPolicy,
) -> PyResult<PySemanticPreservationReport> {
    py.detach(move || core::extract_pdf_pages(input, output, &pages, policy.inner))
        .map(|r| r.into())
        .map_err(op_err_to_py)
}

#[pyfunction]
fn plan_split_existing_pdf(
    py: Python<'_>,
    input: String,
    ranges: Vec<PyPageRange>,
    policy: PyExistingDocumentPolicy,
) -> PyResult<Vec<PySemanticPreservationReport>> {
    let ranges: Vec<_> = ranges.into_iter().map(|r| r.inner).collect();
    py.detach(move || core::plan_split_pdf(input, &ranges, policy.inner))
        .map(|r| r.into_iter().map(Into::into).collect())
        .map_err(op_err_to_py)
}

#[pyfunction]
fn split_existing_pdf(
    py: Python<'_>,
    input: String,
    ranges: Vec<PyPageRange>,
    outputs: Vec<String>,
    policy: PyExistingDocumentPolicy,
) -> PyResult<Vec<PySemanticPreservationReport>> {
    let ranges: Vec<_> = ranges.into_iter().map(|r| r.inner).collect();
    let outputs: Vec<std::path::PathBuf> = outputs.into_iter().map(Into::into).collect();
    py.detach(move || core::split_pdf(input, &ranges, &outputs, policy.inner))
        .map(|r| r.into_iter().map(Into::into).collect())
        .map_err(op_err_to_py)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPageMutation>()?;
    m.add_function(wrap_pyfunction!(plan_pdf_page_mutations, m)?)?;
    m.add_function(wrap_pyfunction!(mutate_pdf_pages_lossless, m)?)?;
    m.add_class::<PyDocumentStructure>()?;
    m.add_class::<PyStructureDisposition>()?;
    m.add_class::<PyExistingDocumentEngine>()?;
    m.add_class::<PyInputSemanticRole>()?;
    m.add_class::<PyPageMutationReport>()?;
    m.add_class::<PyStructureSemanticReport>()?;
    m.add_class::<PyInputSemanticReport>()?;
    m.add_class::<PyExistingDocumentExecutionPlan>()?;
    m.add_class::<PySemanticPreservationReport>()?;
    m.add_class::<PyExistingDocumentPolicy>()?;
    m.add_class::<PyExistingDocumentMergeInput>()?;
    m.add_function(wrap_pyfunction!(plan_merge_existing_pdfs, m)?)?;
    m.add_function(wrap_pyfunction!(merge_existing_pdfs, m)?)?;
    m.add_function(wrap_pyfunction!(plan_extract_existing_pdf_pages, m)?)?;
    m.add_function(wrap_pyfunction!(extract_existing_pdf_pages, m)?)?;
    m.add_function(wrap_pyfunction!(plan_split_existing_pdf, m)?)?;
    m.add_function(wrap_pyfunction!(split_existing_pdf, m)?)?;
    Ok(())
}

/// One zero-based operation, evaluated after preceding operations in the batch.
#[pyclass(name = "PageMutation", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyPageMutation {
    inner: oxidize_pdf::operations::PageMutation,
}
#[pymethods]
impl PyPageMutation {
    #[staticmethod]
    fn move_page(from_index: usize, to_index: usize) -> Self {
        Self {
            inner: oxidize_pdf::operations::PageMutation::Move {
                from: from_index,
                to: to_index,
            },
        }
    }
    #[staticmethod]
    fn rotate(page: usize, degrees: i32) -> Self {
        Self {
            inner: oxidize_pdf::operations::PageMutation::Rotate { page, degrees },
        }
    }
    #[staticmethod]
    fn delete(page: usize) -> Self {
        Self {
            inner: oxidize_pdf::operations::PageMutation::Delete { page },
        }
    }
    #[staticmethod]
    fn duplicate(page: usize, at: usize) -> Self {
        Self {
            inner: oxidize_pdf::operations::PageMutation::Duplicate { page, at },
        }
    }
    #[staticmethod]
    fn insert(source: String, page: usize, at: usize) -> Self {
        Self {
            inner: oxidize_pdf::operations::PageMutation::Insert {
                source: source.into(),
                page,
                at,
            },
        }
    }
}
#[pyfunction]
fn plan_pdf_page_mutations(
    py: Python<'_>,
    input: String,
    operations: Vec<PyPageMutation>,
) -> PyResult<PyPageMutationReport> {
    let batch = oxidize_pdf::operations::PageMutationBatch {
        operations: operations.into_iter().map(|o| o.inner).collect(),
    };
    py.detach(move || oxidize_pdf::operations::plan_pdf_page_mutations(input, &batch))
        .map(Into::into)
        .map_err(op_err_to_py)
}
#[pyfunction]
fn mutate_pdf_pages_lossless(
    py: Python<'_>,
    input: String,
    output: String,
    operations: Vec<PyPageMutation>,
) -> PyResult<PyPageMutationReport> {
    let batch = oxidize_pdf::operations::PageMutationBatch {
        operations: operations.into_iter().map(|o| o.inner).collect(),
    };
    py.detach(move || oxidize_pdf::operations::mutate_pdf_pages_lossless(input, output, &batch))
        .map(Into::into)
        .map_err(op_err_to_py)
}
