//! External CMS signing: typed options, immutable preparation, no private-key handling.
use crate::errors::PdfError;
use oxidize_pdf::parser::objects::{
    PdfArray, PdfDictionary, PdfName, PdfObject, PdfStream, PdfString,
};
use oxidize_pdf::signatures as sig;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::collections::HashMap;
fn error(e: sig::SignatureError) -> PyErr {
    PdfError::new_err(e.to_string())
}
fn rect(v: (f64, f64, f64, f64)) -> sig::SignatureRect {
    sig::SignatureRect {
        left: v.0,
        bottom: v.1,
        right: v.2,
        top: v.3,
    }
}
fn dictionary(values: HashMap<String, PyPdfValue>) -> PdfDictionary {
    let mut result = PdfDictionary::new();
    for (key, value) in values {
        result.insert(key, value.inner);
    }
    result
}
/// A typed PDF object value for profile-specific dictionary entries.
#[pyclass(name = "PdfValue", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyPdfValue {
    inner: PdfObject,
}
#[pymethods]
impl PyPdfValue {
    #[staticmethod]
    fn null() -> Self {
        Self {
            inner: PdfObject::Null,
        }
    }
    #[staticmethod]
    fn boolean(value: bool) -> Self {
        Self {
            inner: PdfObject::Boolean(value),
        }
    }
    #[staticmethod]
    fn integer(value: i64) -> Self {
        Self {
            inner: PdfObject::Integer(value),
        }
    }
    #[staticmethod]
    fn real(value: f64) -> Self {
        Self {
            inner: PdfObject::Real(value),
        }
    }
    #[staticmethod]
    fn string(value: Vec<u8>) -> Self {
        Self {
            inner: PdfObject::String(PdfString::new(value)),
        }
    }
    #[staticmethod]
    fn name(value: String) -> Self {
        Self {
            inner: PdfObject::Name(PdfName(value)),
        }
    }
    #[staticmethod]
    fn array(values: Vec<PyPdfValue>) -> Self {
        Self {
            inner: PdfObject::Array(PdfArray(values.into_iter().map(|v| v.inner).collect())),
        }
    }
    #[staticmethod]
    fn dictionary(values: HashMap<String, PyPdfValue>) -> Self {
        Self {
            inner: PdfObject::Dictionary(dictionary(values)),
        }
    }
    #[staticmethod]
    fn stream(values: HashMap<String, PyPdfValue>, data: Vec<u8>) -> Self {
        Self {
            inner: PdfObject::Stream(PdfStream {
                dict: dictionary(values),
                data,
            }),
        }
    }
    #[staticmethod]
    fn reference(number: u32, generation: u16) -> Self {
        Self {
            inner: PdfObject::Reference(number, generation),
        }
    }
}
#[pyclass(name = "SignatureTarget", frozen, from_py_object)]
#[derive(Clone)]
pub struct PySignatureTarget {
    inner: sig::SignatureTarget,
}
#[pymethods]
impl PySignatureTarget {
    #[staticmethod]
    #[pyo3(signature=(field_name, page_index=0, rectangle=None))]
    fn new_field(
        field_name: String,
        page_index: usize,
        rectangle: Option<(f64, f64, f64, f64)>,
    ) -> Self {
        Self {
            inner: sig::SignatureTarget::New {
                field_name,
                page_index,
                rect: rectangle.map(rect),
            },
        }
    }
    #[staticmethod]
    #[pyo3(signature=(field_name, widget_index=None, rectangle=None))]
    fn existing_field(
        field_name: String,
        widget_index: Option<usize>,
        rectangle: Option<(f64, f64, f64, f64)>,
    ) -> Self {
        Self {
            inner: sig::SignatureTarget::Existing {
                field_name,
                widget_index,
                rect: rectangle.map(rect),
            },
        }
    }
}
#[pyclass(name = "CertificationPermission", eq, eq_int, frozen, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyCertificationPermission {
    NoChanges = 1,
    FormFillAndSign = 2,
    FormFillSignAndAnnotate = 3,
}
impl From<PyCertificationPermission> for sig::CertificationPermission {
    fn from(p: PyCertificationPermission) -> Self {
        match p {
            PyCertificationPermission::NoChanges => Self::NoChanges,
            PyCertificationPermission::FormFillAndSign => Self::FormFillAndSign,
            PyCertificationPermission::FormFillSignAndAnnotate => Self::FormFillSignAndAnnotate,
        }
    }
}
#[pyclass(name = "FieldLock", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyFieldLock {
    inner: sig::FieldLock,
}
#[pymethods]
impl PyFieldLock {
    #[staticmethod]
    fn all() -> Self {
        Self {
            inner: sig::FieldLock::All,
        }
    }
    #[staticmethod]
    fn include(fields: Vec<String>) -> Self {
        Self {
            inner: sig::FieldLock::Include(fields),
        }
    }
    #[staticmethod]
    fn exclude(fields: Vec<String>) -> Self {
        Self {
            inner: sig::FieldLock::Exclude(fields),
        }
    }
}
#[pyclass(name = "SignaturePreparationOptions", frozen, from_py_object)]
#[derive(Clone)]
pub struct PySignaturePreparationOptions {
    inner: sig::SignaturePreparationOptions,
}
#[pymethods]
impl PySignaturePreparationOptions {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature=(target, *, placeholder_bytes=16384, filter="Adobe.PPKLite", sub_filter="adbe.pkcs7.detached", reason=None, location=None, contact_info=None, signing_time=None, certification=None, field_lock=None, additional_entries=None))]
    fn new(
        target: PySignatureTarget,
        placeholder_bytes: usize,
        filter: &str,
        sub_filter: &str,
        reason: Option<String>,
        location: Option<String>,
        contact_info: Option<String>,
        signing_time: Option<String>,
        certification: Option<PyCertificationPermission>,
        field_lock: Option<PyFieldLock>,
        additional_entries: Option<HashMap<String, PyPdfValue>>,
    ) -> Self {
        Self {
            inner: sig::SignaturePreparationOptions {
                target: target.inner,
                placeholder_bytes,
                filter: filter.into(),
                sub_filter: sub_filter.into(),
                reason,
                location,
                contact_info,
                signing_time,
                certification: certification.map(Into::into),
                field_lock: field_lock.map(|f| f.inner),
                additional_signature_entries: dictionary(additional_entries.unwrap_or_default()),
            },
        }
    }
}
#[pyclass(name = "SignatureWatermark", frozen, from_py_object)]
#[derive(Clone)]
pub struct PySignatureWatermark {
    inner: sig::SignatureWatermark,
}
#[pymethods]
impl PySignatureWatermark {
    #[new]
    #[pyo3(signature=(width,height,rgb,opacity=1.0))]
    fn new(width: u32, height: u32, rgb: Vec<u8>, opacity: f32) -> Self {
        Self {
            inner: sig::SignatureWatermark {
                width,
                height,
                rgb,
                opacity,
            },
        }
    }
}
#[pyclass(name = "SignatureAppearanceLayout", frozen, from_py_object, get_all)]
#[derive(Clone)]
pub struct PySignatureAppearanceLayout {
    pub lines: Vec<String>,
    pub font_size: f64,
    pub margin: f64,
    pub first_baseline: f64,
    pub line_height: f64,
}
impl From<sig::SignatureAppearanceLayout> for PySignatureAppearanceLayout {
    fn from(l: sig::SignatureAppearanceLayout) -> Self {
        Self {
            lines: l.lines,
            font_size: l.font_size,
            margin: l.margin,
            first_baseline: l.first_baseline,
            line_height: l.line_height,
        }
    }
}
#[pyclass(name = "SignatureAppearance", frozen, from_py_object)]
#[derive(Clone)]
pub struct PySignatureAppearance {
    inner: sig::SignatureAppearance,
}
#[pymethods]
impl PySignatureAppearance {
    #[new]
    #[pyo3(signature=(*, signer_name=None, signing_date=None,text=None,watermark=None))]
    fn new(
        signer_name: Option<String>,
        signing_date: Option<String>,
        text: Option<Vec<String>>,
        watermark: Option<PySignatureWatermark>,
    ) -> Self {
        Self {
            inner: sig::SignatureAppearance {
                signer_name,
                signing_date,
                text: text.unwrap_or_default(),
                watermark: watermark.map(|w| w.inner),
            },
        }
    }
    fn layout(&self, rectangle: (f64, f64, f64, f64)) -> PyResult<PySignatureAppearanceLayout> {
        self.inner
            .layout(rect(rectangle))
            .map(Into::into)
            .map_err(error)
    }
}
/// Immutable preparation. Finalize returns a new PDF and supports retries.
#[pyclass(name = "PreparedSignature", frozen)]
pub struct PyPreparedSignature {
    inner: sig::PreparedSignature,
}
#[pymethods]
impl PyPreparedSignature {
    #[getter]
    fn prepared_pdf<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, self.inner.prepared_pdf())
    }
    #[getter]
    fn byte_range(&self) -> Vec<(u64, u64)> {
        self.inner.byte_range().ranges().to_vec()
    }
    #[getter]
    fn bytes_to_digest<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.inner.bytes_to_digest())
    }
    /// Embed DER CMS after structural/size checks; does not verify authenticity.
    fn finalize<'py>(&self, py: Python<'py>, cms: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
        let bytes = py
            .detach(|| self.inner.clone().finalize(cms))
            .map_err(error)?;
        Ok(PyBytes::new(py, &bytes))
    }
}
/// Prepare an incremental revision for an external signer; private keys stay with the caller.
#[pyfunction]
#[pyo3(signature=(base,options,appearance=None))]
fn prepare_incremental_signature(
    py: Python<'_>,
    base: &[u8],
    options: PySignaturePreparationOptions,
    appearance: Option<PySignatureAppearance>,
) -> PyResult<PyPreparedSignature> {
    py.detach(|| match appearance {
        Some(a) => {
            sig::prepare_incremental_signature_with_appearance(base, &options.inner, &a.inner)
        }
        None => sig::prepare_incremental_signature(base, &options.inner),
    })
    .map(|inner| PyPreparedSignature { inner })
    .map_err(error)
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPdfValue>()?;
    m.add_class::<PySignatureTarget>()?;
    m.add_class::<PyCertificationPermission>()?;
    m.add_class::<PyFieldLock>()?;
    m.add_class::<PySignaturePreparationOptions>()?;
    m.add_class::<PySignatureWatermark>()?;
    m.add_class::<PySignatureAppearanceLayout>()?;
    m.add_class::<PySignatureAppearance>()?;
    m.add_class::<PyPreparedSignature>()?;
    m.add_function(wrap_pyfunction!(prepare_incremental_signature, m)?)?;
    Ok(())
}
