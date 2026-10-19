//! Owned wrappers for the native Text and Highlight incremental editors.
use crate::errors::to_py_err;
use oxidize_pdf::{writer as core, Point};
use pyo3::prelude::*;
use pyo3::types::PyBytes;
#[pyclass(name = "TextNoteId", frozen, from_py_object, eq, hash)]
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
pub struct PyTextNoteId {
    inner: core::TextNoteId,
}
#[pymethods]
impl PyTextNoteId {
    #[new]
    fn new(object_number: u32, generation_number: u16) -> Self {
        Self {
            inner: core::TextNoteId::new(object_number, generation_number),
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
#[pyclass(name = "HighlightId", frozen, from_py_object, eq, hash)]
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
pub struct PyHighlightId {
    inner: core::HighlightId,
}
#[pymethods]
impl PyHighlightId {
    #[new]
    fn new(object_number: u32, generation_number: u16) -> Self {
        Self {
            inner: core::HighlightId::new(object_number, generation_number),
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
#[pyclass(name = "HighlightQuad", frozen, from_py_object, eq)]
#[derive(Clone, Copy, PartialEq)]
pub struct PyHighlightQuad {
    inner: core::HighlightQuad,
}
#[pymethods]
impl PyHighlightQuad {
    #[new]
    fn new(points: [(f64, f64); 4]) -> PyResult<Self> {
        Ok(Self {
            inner: core::HighlightQuad::new(points.map(|(x, y)| Point::new(x, y)))
                .map_err(to_py_err)?,
        })
    }
    #[getter]
    fn points(&self) -> Vec<(f64, f64)> {
        self.inner.points().iter().map(|p| (p.x, p.y)).collect()
    }
}
#[pyclass(name = "HighlightColor", frozen, from_py_object, eq)]
#[derive(Clone, Copy, PartialEq)]
pub struct PyHighlightColor {
    inner: core::HighlightColor,
}
#[pymethods]
impl PyHighlightColor {
    #[new]
    fn new(components: [f64; 3]) -> PyResult<Self> {
        Ok(Self {
            inner: core::HighlightColor::new(components).map_err(to_py_err)?,
        })
    }
    #[getter]
    fn components(&self) -> [f64; 3] {
        self.inner.components()
    }
}
#[pyclass(name = "HighlightOpacity", frozen, from_py_object, eq)]
#[derive(Clone, Copy, PartialEq)]
pub struct PyHighlightOpacity {
    inner: core::HighlightOpacity,
}
#[pymethods]
impl PyHighlightOpacity {
    #[new]
    fn new(value: f64) -> PyResult<Self> {
        Ok(Self {
            inner: core::HighlightOpacity::new(value).map_err(to_py_err)?,
        })
    }
    #[getter]
    fn value(&self) -> f64 {
        self.inner.value()
    }
}
#[pyclass(name = "TextNote", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTextNote {
    inner: core::TextNote,
}
#[pymethods]
impl PyTextNote {
    #[getter]
    fn id(&self) -> PyTextNoteId {
        PyTextNoteId {
            inner: self.inner.id,
        }
    }
    #[getter]
    fn page_index(&self) -> u32 {
        self.inner.page_index
    }
    #[getter]
    fn position(&self) -> (f64, f64) {
        (self.inner.position.x, self.inner.position.y)
    }
    #[getter]
    fn contents(&self) -> &str {
        &self.inner.contents
    }
}
#[pyclass(name = "Highlight", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyHighlight {
    inner: core::Highlight,
}
#[pymethods]
impl PyHighlight {
    #[getter]
    fn id(&self) -> PyHighlightId {
        PyHighlightId {
            inner: self.inner.id,
        }
    }
    #[getter]
    fn page_index(&self) -> u32 {
        self.inner.page_index
    }
    #[getter]
    fn rect(&self) -> [f64; 4] {
        self.inner.rect
    }
    #[getter]
    fn quadrilaterals(&self) -> Vec<PyHighlightQuad> {
        self.inner
            .quadrilaterals
            .iter()
            .map(|v| PyHighlightQuad { inner: *v })
            .collect()
    }
    #[getter]
    fn color(&self) -> PyHighlightColor {
        PyHighlightColor {
            inner: self.inner.color,
        }
    }
    #[getter]
    fn opacity(&self) -> Option<PyHighlightOpacity> {
        self.inner.opacity.map(|inner| PyHighlightOpacity { inner })
    }
    #[getter]
    fn contents(&self) -> Option<&str> {
        self.inner.contents.as_deref()
    }
}
#[pyclass(name = "TextNoteMutation", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTextNoteMutation {
    inner: core::TextNoteMutation,
}
#[pymethods]
impl PyTextNoteMutation {
    #[staticmethod]
    fn add(page_index: u32, position: (f64, f64), contents: String) -> Self {
        Self {
            inner: core::TextNoteMutation::Add {
                page_index,
                position: Point::new(position.0, position.1),
                contents,
            },
        }
    }
    #[staticmethod]
    fn update(id: PyTextNoteId, position: (f64, f64), contents: String) -> Self {
        Self {
            inner: core::TextNoteMutation::Update {
                id: id.inner,
                position: Point::new(position.0, position.1),
                contents,
            },
        }
    }
    #[staticmethod]
    fn remove(id: PyTextNoteId) -> Self {
        Self {
            inner: core::TextNoteMutation::Remove { id: id.inner },
        }
    }
    #[getter]
    fn kind(&self) -> &'static str {
        match self.inner {
            core::TextNoteMutation::Add { .. } => "add",
            core::TextNoteMutation::Update { .. } => "update",
            core::TextNoteMutation::Remove { .. } => "remove",
        }
    }
    #[getter]
    fn id(&self) -> Option<PyTextNoteId> {
        match self.inner {
            core::TextNoteMutation::Update { id, .. } | core::TextNoteMutation::Remove { id } => {
                Some(PyTextNoteId { inner: id })
            }
            _ => None,
        }
    }
    #[getter]
    fn page_index(&self) -> Option<u32> {
        match self.inner {
            core::TextNoteMutation::Add { page_index, .. } => Some(page_index),
            _ => None,
        }
    }
    #[getter]
    fn position(&self) -> Option<(f64, f64)> {
        match self.inner {
            core::TextNoteMutation::Add { position, .. }
            | core::TextNoteMutation::Update { position, .. } => Some((position.x, position.y)),
            _ => None,
        }
    }
    #[getter]
    fn contents(&self) -> Option<&str> {
        match &self.inner {
            core::TextNoteMutation::Add { contents, .. }
            | core::TextNoteMutation::Update { contents, .. } => Some(contents),
            _ => None,
        }
    }
}
#[pyclass(name = "HighlightMutation", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyHighlightMutation {
    inner: core::HighlightMutation,
}
#[pymethods]
impl PyHighlightMutation {
    #[staticmethod]
    #[pyo3(signature=(page_index, quadrilaterals, color, opacity=None, contents=None))]
    fn add(
        page_index: u32,
        quadrilaterals: Vec<PyHighlightQuad>,
        color: PyHighlightColor,
        opacity: Option<PyHighlightOpacity>,
        contents: Option<String>,
    ) -> Self {
        Self {
            inner: core::HighlightMutation::Add {
                page_index,
                quadrilaterals: quadrilaterals.into_iter().map(|v| v.inner).collect(),
                color: color.inner,
                opacity: opacity.map(|v| v.inner),
                contents,
            },
        }
    }
    #[staticmethod]
    fn remove(id: PyHighlightId) -> Self {
        Self {
            inner: core::HighlightMutation::Remove { id: id.inner },
        }
    }
    #[getter]
    fn kind(&self) -> &'static str {
        match self.inner {
            core::HighlightMutation::Add { .. } => "add",
            core::HighlightMutation::Remove { .. } => "remove",
        }
    }
    #[getter]
    fn id(&self) -> Option<PyHighlightId> {
        match self.inner {
            core::HighlightMutation::Remove { id } => Some(PyHighlightId { inner: id }),
            _ => None,
        }
    }
    #[getter]
    fn page_index(&self) -> Option<u32> {
        match self.inner {
            core::HighlightMutation::Add { page_index, .. } => Some(page_index),
            _ => None,
        }
    }
    #[getter]
    fn quadrilaterals(&self) -> Option<Vec<PyHighlightQuad>> {
        match &self.inner {
            core::HighlightMutation::Add { quadrilaterals, .. } => Some(
                quadrilaterals
                    .iter()
                    .map(|v| PyHighlightQuad { inner: *v })
                    .collect(),
            ),
            _ => None,
        }
    }
    #[getter]
    fn color(&self) -> Option<PyHighlightColor> {
        match self.inner {
            core::HighlightMutation::Add { color, .. } => Some(PyHighlightColor { inner: color }),
            _ => None,
        }
    }
    #[getter]
    fn opacity(&self) -> Option<PyHighlightOpacity> {
        match self.inner {
            core::HighlightMutation::Add { opacity, .. } => {
                opacity.map(|inner| PyHighlightOpacity { inner })
            }
            _ => None,
        }
    }
    #[getter]
    fn contents(&self) -> Option<&str> {
        match &self.inner {
            core::HighlightMutation::Add { contents, .. } => contents.as_deref(),
            _ => None,
        }
    }
}
#[pyclass(name = "TextNoteUpdate", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTextNoteUpdate {
    inner: core::TextNoteUpdate,
}
#[pymethods]
impl PyTextNoteUpdate {
    #[getter]
    fn pdf_bytes<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.inner.pdf_bytes)
    }
    #[getter]
    fn added_notes(&self) -> Vec<PyTextNote> {
        self.inner
            .added_notes
            .iter()
            .cloned()
            .map(|inner| PyTextNote { inner })
            .collect()
    }
}
/// Immutable source snapshot; each apply returns an independent revision.
#[pyclass(name = "IncrementalTextNoteEditor", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyIncrementalTextNoteEditor {
    base: Vec<u8>,
}
#[pymethods]
impl PyIncrementalTextNoteEditor {
    #[new]
    fn new(pdf: &[u8]) -> Self {
        Self { base: pdf.to_vec() }
    }
    fn notes(&self, py: Python<'_>) -> PyResult<Vec<PyTextNote>> {
        let values = py
            .detach(|| core::IncrementalTextNoteEditor::new(&self.base).notes())
            .map_err(to_py_err)?;
        Ok(values
            .into_iter()
            .map(|inner| PyTextNote { inner })
            .collect())
    }
    fn apply(
        &self,
        py: Python<'_>,
        mutations: Vec<PyTextNoteMutation>,
    ) -> PyResult<PyTextNoteUpdate> {
        let mutations: Vec<_> = mutations.into_iter().map(|v| v.inner).collect();
        let inner = py
            .detach(|| core::IncrementalTextNoteEditor::new(&self.base).apply(&mutations))
            .map_err(to_py_err)?;
        Ok(PyTextNoteUpdate { inner })
    }
}
#[pyclass(name = "HighlightUpdate", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyHighlightUpdate {
    inner: core::HighlightUpdate,
}
#[pymethods]
impl PyHighlightUpdate {
    #[getter]
    fn pdf_bytes<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.inner.pdf_bytes)
    }
    #[getter]
    fn highlights(&self) -> Vec<PyHighlight> {
        self.inner
            .highlights
            .iter()
            .cloned()
            .map(|inner| PyHighlight { inner })
            .collect()
    }
}
/// Immutable source snapshot; each apply returns an independent revision.
#[pyclass(name = "IncrementalHighlightEditor", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyIncrementalHighlightEditor {
    base: Vec<u8>,
}
#[pymethods]
impl PyIncrementalHighlightEditor {
    #[new]
    fn new(pdf: &[u8]) -> Self {
        Self { base: pdf.to_vec() }
    }
    fn highlights(&self, py: Python<'_>) -> PyResult<Vec<PyHighlight>> {
        let values = py
            .detach(|| core::IncrementalHighlightEditor::new(&self.base).highlights())
            .map_err(to_py_err)?;
        Ok(values
            .into_iter()
            .map(|inner| PyHighlight { inner })
            .collect())
    }
    fn apply(
        &self,
        py: Python<'_>,
        mutations: Vec<PyHighlightMutation>,
    ) -> PyResult<PyHighlightUpdate> {
        let mutations: Vec<_> = mutations.into_iter().map(|v| v.inner).collect();
        let inner = py
            .detach(|| core::IncrementalHighlightEditor::new(&self.base).apply(&mutations))
            .map_err(to_py_err)?;
        Ok(PyHighlightUpdate { inner })
    }
}
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTextNoteId>()?;
    m.add_class::<PyHighlightId>()?;
    m.add_class::<PyHighlightQuad>()?;
    m.add_class::<PyHighlightColor>()?;
    m.add_class::<PyHighlightOpacity>()?;
    m.add_class::<PyTextNote>()?;
    m.add_class::<PyHighlight>()?;
    m.add_class::<PyTextNoteMutation>()?;
    m.add_class::<PyHighlightMutation>()?;
    m.add_class::<PyTextNoteUpdate>()?;
    m.add_class::<PyIncrementalTextNoteEditor>()?;
    m.add_class::<PyHighlightUpdate>()?;
    m.add_class::<PyIncrementalHighlightEditor>()?;
    Ok(())
}
