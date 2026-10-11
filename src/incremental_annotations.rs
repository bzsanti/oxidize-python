//! Typed incremental free-text editing. Core owns validation.
use crate::errors::to_py_err;
use oxidize_pdf::writer as core;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

#[pyclass(name = "FreeTextAlignment", frozen, eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyFreeTextAlignment {
    Left,
    Center,
    Right,
}
impl From<PyFreeTextAlignment> for core::FreeTextAlignment {
    fn from(v: PyFreeTextAlignment) -> Self {
        match v {
            PyFreeTextAlignment::Left => Self::Left,
            PyFreeTextAlignment::Center => Self::Center,
            PyFreeTextAlignment::Right => Self::Right,
        }
    }
}
impl From<core::FreeTextAlignment> for PyFreeTextAlignment {
    fn from(v: core::FreeTextAlignment) -> Self {
        match v {
            core::FreeTextAlignment::Left => Self::Left,
            core::FreeTextAlignment::Center => Self::Center,
            core::FreeTextAlignment::Right => Self::Right,
        }
    }
}

#[pyclass(name = "FreeTextId", frozen, eq, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub struct PyFreeTextId {
    inner: core::FreeTextId,
}
#[pymethods]
impl PyFreeTextId {
    #[new]
    fn new(object_number: u32, generation_number: u16) -> Self {
        Self {
            inner: core::FreeTextId::new(object_number, generation_number),
        }
    }
    #[getter]
    fn object_number(&self) -> u32 {
        self.inner.object_number
    }
    #[getter]
    fn generation_number(&self) -> u16 {
        self.inner.generation_number
    }
}
#[pyclass(name = "FreeText", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyFreeText {
    inner: core::FreeText,
}
#[pymethods]
impl PyFreeText {
    #[getter]
    fn id(&self) -> PyFreeTextId {
        PyFreeTextId {
            inner: self.inner.id,
        }
    }
    #[getter]
    fn page_index(&self) -> u32 {
        self.inner.page_index
    }
    #[getter]
    fn contents(&self) -> String {
        self.inner.contents.clone()
    }
    #[getter]
    fn rect(&self) -> [f64; 4] {
        self.inner.rect
    }
    #[getter]
    fn default_appearance(&self) -> String {
        self.inner.default_appearance.clone()
    }
    #[getter]
    fn alignment(&self) -> PyFreeTextAlignment {
        self.inner.alignment.into()
    }
}

#[pyclass(name = "FreeTextMutation", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyFreeTextMutation {
    inner: core::FreeTextMutation,
}
#[pymethods]
impl PyFreeTextMutation {
    #[staticmethod]
    fn remove(id: PyFreeTextId) -> Self {
        Self {
            inner: core::FreeTextMutation::Remove { id: id.inner },
        }
    }
    #[staticmethod]
    fn add(
        page_index: u32,
        rect: [f64; 4],
        contents: String,
        default_appearance: String,
        alignment: PyFreeTextAlignment,
    ) -> Self {
        Self {
            inner: core::FreeTextMutation::Add {
                page_index,
                rect,
                contents,
                default_appearance,
                alignment: alignment.into(),
            },
        }
    }
    #[staticmethod]
    fn update(
        id: PyFreeTextId,
        rect: [f64; 4],
        contents: String,
        default_appearance: String,
        alignment: PyFreeTextAlignment,
    ) -> Self {
        Self {
            inner: core::FreeTextMutation::Update {
                id: id.inner,
                rect,
                contents,
                default_appearance,
                alignment: alignment.into(),
            },
        }
    }
}

#[pyclass(name = "FreeTextUpdate", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyFreeTextUpdate {
    inner: core::FreeTextUpdate,
}
#[pymethods]
impl PyFreeTextUpdate {
    #[getter]
    fn pdf_bytes<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.inner.pdf_bytes)
    }
    #[getter]
    fn annotations(&self) -> Vec<PyFreeText> {
        self.inner
            .annotations
            .iter()
            .cloned()
            .map(|inner| PyFreeText { inner })
            .collect()
    }
}
/// Immutable editor over an owned PDF snapshot; apply returns a new revision.
#[pyclass(name = "IncrementalFreeTextEditor", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyIncrementalFreeTextEditor {
    base: Vec<u8>,
}
#[pymethods]
impl PyIncrementalFreeTextEditor {
    #[new]
    fn new(pdf: &[u8]) -> Self {
        Self { base: pdf.to_vec() }
    }
    fn annotations(&self, py: Python<'_>) -> PyResult<Vec<PyFreeText>> {
        let result = py
            .detach(|| core::IncrementalFreeTextEditor::new(&self.base).annotations())
            .map_err(to_py_err)?;
        Ok(result
            .into_iter()
            .map(|inner| PyFreeText { inner })
            .collect())
    }
    fn apply(
        &self,
        py: Python<'_>,
        mutations: Vec<PyFreeTextMutation>,
    ) -> PyResult<PyFreeTextUpdate> {
        let mutations: Vec<_> = mutations.into_iter().map(|m| m.inner).collect();
        let inner = py
            .detach(|| core::IncrementalFreeTextEditor::new(&self.base).apply(&mutations))
            .map_err(to_py_err)?;
        Ok(PyFreeTextUpdate { inner })
    }
}
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyFreeTextAlignment>()?;
    m.add_class::<PyFreeTextId>()?;
    m.add_class::<PyFreeText>()?;
    m.add_class::<PyFreeTextMutation>()?;
    m.add_class::<PyFreeTextUpdate>()?;
    m.add_class::<PyIncrementalFreeTextEditor>()?;
    Ok(())
}
