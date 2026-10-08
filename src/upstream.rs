//! Application-facing additions from core 5.2–5.4.
use crate::errors::PdfError;
use crate::text_extraction::PyExtractedText;
use oxidize_pdf::parser::filters::FlateRecoveryKind;
use oxidize_pdf::text::{RecoveredText, RecoveryLocation, TextRecoveryAction};
use oxidize_pdf::{document::BuildIdentification, signatures as sig};
use pyo3::prelude::*;
use pyo3::types::PyBytes;

#[pyclass(name = "BuildIdentification", eq, eq_int, frozen, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyBuildIdentification {
    Enabled,
    Disabled,
}
impl From<PyBuildIdentification> for BuildIdentification {
    fn from(v: PyBuildIdentification) -> Self {
        match v {
            PyBuildIdentification::Enabled => Self::Enabled,
            PyBuildIdentification::Disabled => Self::Disabled,
        }
    }
}
impl From<BuildIdentification> for PyBuildIdentification {
    fn from(v: BuildIdentification) -> Self {
        match v {
            BuildIdentification::Enabled => Self::Enabled,
            BuildIdentification::Disabled => Self::Disabled,
        }
    }
}

/// A recovered or omitted stream, including its location and original error.
#[pyclass(name = "TextRecoveryDiagnostic", frozen, from_py_object, get_all)]
#[derive(Clone)]
pub struct PyTextRecoveryDiagnostic {
    pub location: String,
    pub contents_index: Option<usize>,
    pub form_name: Option<String>,
    pub object_id: Option<(u32, u16)>,
    pub action: String,
    pub filter_index: Option<usize>,
    pub kind: Option<String>,
    pub error: String,
}

#[pyclass(name = "RecoveredText", frozen)]
pub struct PyRecoveredText {
    #[pyo3(get)]
    pub page_index: u32,
    text: PyExtractedText,
    #[pyo3(get)]
    pub diagnostics: Vec<PyTextRecoveryDiagnostic>,
}
#[pymethods]
impl PyRecoveredText {
    #[getter]
    fn text(&self) -> PyExtractedText {
        PyExtractedText {
            inner: self.text.inner.clone(),
        }
    }
}
impl PyRecoveredText {
    pub fn from_core(value: RecoveredText) -> PyResult<Self> {
        let diagnostics = value
            .diagnostics
            .into_iter()
            .map(|d| {
                let (location, contents_index, form_name, object_id) = match d.location {
                    RecoveryLocation::PageContents(i) => ("page_contents", Some(i), None, None),
                    RecoveryLocation::FormXObject { name, object } => {
                        ("form_xobject", None, Some(name), Some(object))
                    }
                    _ => return Err(PdfError::new_err("Unsupported recovery location")),
                };
                let (action, filter_index, kind, error) = match d.action {
                    TextRecoveryAction::Recovered(f) => {
                        let kind = match f.kind {
                            FlateRecoveryKind::Unverified => "unverified",
                            FlateRecoveryKind::Incomplete => "incomplete",
                            _ => return Err(PdfError::new_err("Unsupported recovery kind")),
                        };
                        (
                            "recovered",
                            Some(f.filter_index),
                            Some(kind.to_owned()),
                            f.error,
                        )
                    }
                    TextRecoveryAction::Omitted { error } => ("omitted", None, None, error),
                    _ => return Err(PdfError::new_err("Unsupported recovery action")),
                };
                Ok(PyTextRecoveryDiagnostic {
                    location: location.into(),
                    contents_index,
                    form_name,
                    object_id,
                    action: action.into(),
                    filter_index,
                    kind,
                    error,
                })
            })
            .collect::<PyResult<Vec<_>>>()?;
        Ok(Self {
            page_index: value.page_index,
            text: PyExtractedText { inner: value.text },
            diagnostics,
        })
    }
}

/// Application-prepared field. Completion is distinct from cryptographic signing.
#[pyclass(name = "SignatureSlot", frozen, get_all)]
pub struct PySignatureSlot {
    name: String,
    metadata: String,
    page_index: usize,
    rotation: i32,
    rect: (f64, f64, f64, f64),
    completed: bool,
    digitally_signed: bool,
}
impl From<sig::SignatureSlot> for PySignatureSlot {
    fn from(s: sig::SignatureSlot) -> Self {
        Self {
            name: s.name,
            metadata: s.metadata,
            page_index: s.page_index,
            rotation: s.rotation,
            rect: (s.rect.left, s.rect.bottom, s.rect.right, s.rect.top),
            completed: s.completed,
            digitally_signed: s.digitally_signed,
        }
    }
}
fn signature_error(e: sig::SignatureError) -> PyErr {
    PdfError::new_err(e.to_string())
}

/// Create a slot incrementally; rect is (left, bottom, right, top) in PDF points.
#[pyfunction]
#[pyo3(signature = (base, field_name, page_index, rect, *, metadata=""))]
fn create_signature_slot<'py>(
    py: Python<'py>,
    base: &[u8],
    field_name: &str,
    page_index: usize,
    rect: (f64, f64, f64, f64),
    metadata: &str,
) -> PyResult<Bound<'py, PyBytes>> {
    let rect = sig::SignatureRect {
        left: rect.0,
        bottom: rect.1,
        right: rect.2,
        top: rect.3,
    };
    let bytes = py
        .detach(|| sig::create_signature_slot(base, field_name, page_index, rect, metadata))
        .map_err(signature_error)?;
    Ok(PyBytes::new(py, &bytes))
}
#[pyfunction]
fn list_signature_slots(py: Python<'_>, base: &[u8]) -> PyResult<Vec<PySignatureSlot>> {
    py.detach(|| sig::list_signature_slots(base))
        .map(|v| v.into_iter().map(Into::into).collect())
        .map_err(signature_error)
}
#[pyfunction]
fn read_signature_slot(py: Python<'_>, base: &[u8], field_name: &str) -> PyResult<PySignatureSlot> {
    py.detach(|| sig::read_signature_slot(base, field_name))
        .map(Into::into)
        .map_err(signature_error)
}
#[pyfunction]
fn remove_signature_slot<'py>(
    py: Python<'py>,
    base: &[u8],
    field_name: &str,
) -> PyResult<Bound<'py, PyBytes>> {
    let bytes = py
        .detach(|| sig::remove_signature_slot(base, field_name))
        .map_err(signature_error)?;
    Ok(PyBytes::new(py, &bytes))
}
/// Draw normalized [0,1] strokes and optional label. This does not create CMS.
#[pyfunction]
#[pyo3(signature = (base, field_name, strokes, *, complete=false, label=None))]
fn draw_signature_slot<'py>(
    py: Python<'py>,
    base: &[u8],
    field_name: &str,
    strokes: Vec<Vec<[f64; 2]>>,
    complete: bool,
    label: Option<&str>,
) -> PyResult<Bound<'py, PyBytes>> {
    let bytes = py
        .detach(|| sig::draw_signature_slot(base, field_name, &strokes, complete, label))
        .map_err(signature_error)?;
    Ok(PyBytes::new(py, &bytes))
}
/// Complete handwriting only; digitally_signed remains false.
#[pyfunction]
#[pyo3(signature = (base, field_name, strokes, *, complete=true))]
fn complete_signature_slot<'py>(
    py: Python<'py>,
    base: &[u8],
    field_name: &str,
    strokes: Vec<Vec<[f64; 2]>>,
    complete: bool,
) -> PyResult<Bound<'py, PyBytes>> {
    let bytes = py
        .detach(|| sig::complete_signature_slot(base, field_name, &strokes, complete))
        .map_err(signature_error)?;
    Ok(PyBytes::new(py, &bytes))
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyBuildIdentification>()?;
    m.add_class::<PyTextRecoveryDiagnostic>()?;
    m.add_class::<PyRecoveredText>()?;
    m.add_class::<PySignatureSlot>()?;
    m.add_function(wrap_pyfunction!(create_signature_slot, m)?)?;
    m.add_function(wrap_pyfunction!(list_signature_slots, m)?)?;
    m.add_function(wrap_pyfunction!(read_signature_slot, m)?)?;
    m.add_function(wrap_pyfunction!(remove_signature_slot, m)?)?;
    m.add_function(wrap_pyfunction!(draw_signature_slot, m)?)?;
    m.add_function(wrap_pyfunction!(complete_signature_slot, m)?)?;
    Ok(())
}
