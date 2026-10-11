//! Incremental Ink annotation editing with validated geometry and appearance.
use crate::errors::to_py_err;
use oxidize_pdf::writer as core;
use oxidize_pdf::Point;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

#[pyclass(name = "InkColorSpace", frozen, eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyInkColorSpace {
    Gray,
    Rgb,
    Cmyk,
}
#[pyclass(name = "InkColor", frozen, eq, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub struct PyInkColor {
    inner: core::InkColor,
}
#[pymethods]
impl PyInkColor {
    #[staticmethod]
    fn rgb(components: [f64; 3]) -> PyResult<Self> {
        Ok(Self {
            inner: core::InkColor::new(components).map_err(to_py_err)?,
        })
    }
    #[staticmethod]
    fn gray(component: f64) -> PyResult<Self> {
        Ok(Self {
            inner: core::InkColor::gray(component).map_err(to_py_err)?,
        })
    }
    #[staticmethod]
    fn cmyk(components: [f64; 4]) -> PyResult<Self> {
        Ok(Self {
            inner: core::InkColor::cmyk(components).map_err(to_py_err)?,
        })
    }
    #[getter]
    fn space(&self) -> PyInkColorSpace {
        match self.inner {
            core::InkColor::Gray(_) => PyInkColorSpace::Gray,
            core::InkColor::Rgb(_) => PyInkColorSpace::Rgb,
            core::InkColor::Cmyk(_) => PyInkColorSpace::Cmyk,
        }
    }
    #[getter]
    fn components(&self) -> Vec<f64> {
        match self.inner {
            core::InkColor::Gray(v) => v.to_vec(),
            core::InkColor::Rgb(v) => v.to_vec(),
            core::InkColor::Cmyk(v) => v.to_vec(),
        }
    }
}
#[pyclass(name = "InkStroke", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyInkStroke {
    inner: core::InkStroke,
}
#[pymethods]
impl PyInkStroke {
    #[new]
    fn new(points: Vec<(f64, f64)>) -> PyResult<Self> {
        Ok(Self {
            inner: core::InkStroke::new(
                points.into_iter().map(|(x, y)| Point::new(x, y)).collect(),
            )
            .map_err(to_py_err)?,
        })
    }
    #[getter]
    fn points(&self) -> Vec<(f64, f64)> {
        self.inner.points().iter().map(|p| (p.x, p.y)).collect()
    }
}
#[pyclass(name = "InkId", frozen, eq, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub struct PyInkId {
    inner: core::InkId,
}
#[pymethods]
impl PyInkId {
    #[new]
    fn new(object_number: u32, generation_number: u16) -> Self {
        Self {
            inner: core::InkId::new(object_number, generation_number),
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
#[pyclass(name = "Ink", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyInk {
    inner: core::Ink,
}
#[pymethods]
impl PyInk {
    #[getter]
    fn id(&self) -> PyInkId {
        PyInkId {
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
    fn strokes(&self) -> Vec<PyInkStroke> {
        self.inner
            .strokes
            .iter()
            .cloned()
            .map(|inner| PyInkStroke { inner })
            .collect()
    }
    #[getter]
    fn color(&self) -> PyInkColor {
        PyInkColor {
            inner: self.inner.color,
        }
    }
    #[getter]
    fn width(&self) -> f64 {
        self.inner.width.value()
    }
    #[getter]
    fn opacity(&self) -> Option<f64> {
        self.inner.opacity.map(|v| v.value())
    }
}
#[pyclass(name = "InkMutation", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyInkMutation {
    inner: core::InkMutation,
}
#[pymethods]
impl PyInkMutation {
    #[staticmethod]
    fn remove(id: PyInkId) -> Self {
        Self {
            inner: core::InkMutation::Remove { id: id.inner },
        }
    }
    #[staticmethod]
    #[pyo3(signature=(page_index,strokes,color,width,opacity=None))]
    fn add(
        page_index: u32,
        strokes: Vec<PyInkStroke>,
        color: PyInkColor,
        width: f64,
        opacity: Option<f64>,
    ) -> PyResult<Self> {
        let strokes = strokes.into_iter().map(|s| s.inner).collect();
        let width = core::InkWidth::new(width).map_err(to_py_err)?;
        let opacity = opacity
            .map(core::InkOpacity::new)
            .transpose()
            .map_err(to_py_err)?;
        Ok(Self {
            inner: core::InkMutation::Add {
                page_index,
                strokes,
                color: color.inner,
                width,
                opacity,
            },
        })
    }
    #[staticmethod]
    #[pyo3(signature=(id,strokes,color,width,opacity=None))]
    fn update(
        id: PyInkId,
        strokes: Vec<PyInkStroke>,
        color: PyInkColor,
        width: f64,
        opacity: Option<f64>,
    ) -> PyResult<Self> {
        let strokes = strokes.into_iter().map(|s| s.inner).collect();
        let width = core::InkWidth::new(width).map_err(to_py_err)?;
        let opacity = opacity
            .map(core::InkOpacity::new)
            .transpose()
            .map_err(to_py_err)?;
        Ok(Self {
            inner: core::InkMutation::Update {
                id: id.inner,
                strokes,
                color: color.inner,
                width,
                opacity,
            },
        })
    }
}
#[pyclass(name = "InkUpdate", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyInkUpdate {
    inner: core::InkUpdate,
}
#[pymethods]
impl PyInkUpdate {
    #[getter]
    fn pdf_bytes<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.inner.pdf_bytes)
    }
    #[getter]
    fn annotations(&self) -> Vec<PyInk> {
        self.inner
            .annotations
            .iter()
            .cloned()
            .map(|inner| PyInk { inner })
            .collect()
    }
}
/// Owns an immutable PDF snapshot. Every apply returns an independent new revision.
#[pyclass(name = "IncrementalInkEditor", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyIncrementalInkEditor {
    base: Vec<u8>,
}
#[pymethods]
impl PyIncrementalInkEditor {
    #[new]
    fn new(pdf: &[u8]) -> Self {
        Self { base: pdf.to_vec() }
    }
    fn annotations(&self, py: Python<'_>) -> PyResult<Vec<PyInk>> {
        let values = py
            .detach(|| core::IncrementalInkEditor::new(&self.base).annotations())
            .map_err(to_py_err)?;
        Ok(values.into_iter().map(|inner| PyInk { inner }).collect())
    }
    fn apply(&self, py: Python<'_>, mutations: Vec<PyInkMutation>) -> PyResult<PyInkUpdate> {
        let mutations: Vec<_> = mutations.into_iter().map(|m| m.inner).collect();
        let inner = py
            .detach(|| core::IncrementalInkEditor::new(&self.base).apply(&mutations))
            .map_err(to_py_err)?;
        Ok(PyInkUpdate { inner })
    }
}
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyInkColorSpace>()?;
    m.add_class::<PyInkColor>()?;
    m.add_class::<PyInkStroke>()?;
    m.add_class::<PyInkId>()?;
    m.add_class::<PyInk>()?;
    m.add_class::<PyInkMutation>()?;
    m.add_class::<PyInkUpdate>()?;
    m.add_class::<PyIncrementalInkEditor>()?;
    Ok(())
}
