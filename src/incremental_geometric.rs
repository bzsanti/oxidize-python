//! Incremental Geometric annotation editing with validated geometry and appearance.
use crate::errors::to_py_err;
use oxidize_pdf::writer as core;
use oxidize_pdf::Point;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

#[pyclass(name = "GeometricColorSpace", frozen, eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyGeometricColorSpace {
    Gray,
    Rgb,
    Cmyk,
}
#[pyclass(name = "GeometricColor", frozen, eq, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub struct PyGeometricColor {
    inner: core::GeometricColor,
}
#[pymethods]
impl PyGeometricColor {
    #[staticmethod]
    fn rgb(components: [f64; 3]) -> PyResult<Self> {
        Ok(Self {
            inner: core::GeometricColor::rgb(components).map_err(to_py_err)?,
        })
    }
    #[staticmethod]
    fn gray(component: f64) -> PyResult<Self> {
        Ok(Self {
            inner: core::GeometricColor::gray(component).map_err(to_py_err)?,
        })
    }
    #[staticmethod]
    fn cmyk(components: [f64; 4]) -> PyResult<Self> {
        Ok(Self {
            inner: core::GeometricColor::cmyk(components).map_err(to_py_err)?,
        })
    }
    #[getter]
    fn space(&self) -> PyGeometricColorSpace {
        match self.inner {
            core::GeometricColor::Gray(_) => PyGeometricColorSpace::Gray,
            core::GeometricColor::Rgb(_) => PyGeometricColorSpace::Rgb,
            core::GeometricColor::Cmyk(_) => PyGeometricColorSpace::Cmyk,
        }
    }
    #[getter]
    fn components(&self) -> Vec<f64> {
        match self.inner {
            core::GeometricColor::Gray(v) => v.to_vec(),
            core::GeometricColor::Rgb(v) => v.to_vec(),
            core::GeometricColor::Cmyk(v) => v.to_vec(),
        }
    }
}
#[pyclass(name = "GeometricId", frozen, eq, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub struct PyGeometricId {
    inner: core::GeometricId,
}
#[pymethods]
impl PyGeometricId {
    #[new]
    fn new(object_number: u32, generation_number: u16) -> Self {
        Self {
            inner: core::GeometricId::new(object_number, generation_number),
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
#[pyclass(name = "GeometricLineEnding", frozen, eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyGeometricLineEnding {
    None_,
    Square,
    Circle,
    Diamond,
    OpenArrow,
    ClosedArrow,
    Butt,
    ROpenArrow,
    RClosedArrow,
    Slash,
}
impl From<PyGeometricLineEnding> for core::LineEnding {
    fn from(value: PyGeometricLineEnding) -> Self {
        match value {
            PyGeometricLineEnding::None_ => Self::None,
            PyGeometricLineEnding::Square => Self::Square,
            PyGeometricLineEnding::Circle => Self::Circle,
            PyGeometricLineEnding::Diamond => Self::Diamond,
            PyGeometricLineEnding::OpenArrow => Self::OpenArrow,
            PyGeometricLineEnding::ClosedArrow => Self::ClosedArrow,
            PyGeometricLineEnding::Butt => Self::Butt,
            PyGeometricLineEnding::ROpenArrow => Self::ROpenArrow,
            PyGeometricLineEnding::RClosedArrow => Self::RClosedArrow,
            PyGeometricLineEnding::Slash => Self::Slash,
        }
    }
}
impl From<core::LineEnding> for PyGeometricLineEnding {
    fn from(value: core::LineEnding) -> Self {
        match value {
            core::LineEnding::None => Self::None_,
            core::LineEnding::Square => Self::Square,
            core::LineEnding::Circle => Self::Circle,
            core::LineEnding::Diamond => Self::Diamond,
            core::LineEnding::OpenArrow => Self::OpenArrow,
            core::LineEnding::ClosedArrow => Self::ClosedArrow,
            core::LineEnding::Butt => Self::Butt,
            core::LineEnding::ROpenArrow => Self::ROpenArrow,
            core::LineEnding::RClosedArrow => Self::RClosedArrow,
            core::LineEnding::Slash => Self::Slash,
        }
    }
}
#[pyclass(name = "GeometricKind", frozen, eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyGeometricKind {
    Line,
    Square,
    Circle,
    Polygon,
    PolyLine,
}
/// Owned geometry; core validates coordinates and vertex counts atomically at apply.
#[pyclass(name = "GeometricGeometry", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyGeometricGeometry {
    inner: core::GeometricGeometry,
}
#[pymethods]
impl PyGeometricGeometry {
    #[staticmethod]
    #[pyo3(signature=(start,end,start_ending=PyGeometricLineEnding::None_,end_ending=PyGeometricLineEnding::None_))]
    fn line(
        start: (f64, f64),
        end: (f64, f64),
        start_ending: PyGeometricLineEnding,
        end_ending: PyGeometricLineEnding,
    ) -> Self {
        Self {
            inner: core::GeometricGeometry::Line {
                start: Point::new(start.0, start.1),
                end: Point::new(end.0, end.1),
                start_ending: start_ending.into(),
                end_ending: end_ending.into(),
            },
        }
    }
    #[staticmethod]
    fn square(rect: [f64; 4]) -> Self {
        Self {
            inner: core::GeometricGeometry::Square { rect },
        }
    }
    #[staticmethod]
    fn circle(rect: [f64; 4]) -> Self {
        Self {
            inner: core::GeometricGeometry::Circle { rect },
        }
    }
    #[staticmethod]
    fn polygon(vertices: Vec<(f64, f64)>) -> Self {
        Self {
            inner: core::GeometricGeometry::Polygon {
                vertices: vertices
                    .into_iter()
                    .map(|(x, y)| Point::new(x, y))
                    .collect(),
            },
        }
    }
    #[staticmethod]
    #[pyo3(signature=(vertices,start_ending=PyGeometricLineEnding::None_,end_ending=PyGeometricLineEnding::None_))]
    fn polyline(
        vertices: Vec<(f64, f64)>,
        start_ending: PyGeometricLineEnding,
        end_ending: PyGeometricLineEnding,
    ) -> Self {
        Self {
            inner: core::GeometricGeometry::PolyLine {
                vertices: vertices
                    .into_iter()
                    .map(|(x, y)| Point::new(x, y))
                    .collect(),
                start_ending: start_ending.into(),
                end_ending: end_ending.into(),
            },
        }
    }
    #[getter]
    fn kind(&self) -> PyGeometricKind {
        match &self.inner {
            core::GeometricGeometry::Line { .. } => PyGeometricKind::Line,
            core::GeometricGeometry::Square { .. } => PyGeometricKind::Square,
            core::GeometricGeometry::Circle { .. } => PyGeometricKind::Circle,
            core::GeometricGeometry::Polygon { .. } => PyGeometricKind::Polygon,
            core::GeometricGeometry::PolyLine { .. } => PyGeometricKind::PolyLine,
        }
    }
    #[getter]
    fn rect(&self) -> Option<[f64; 4]> {
        match &self.inner {
            core::GeometricGeometry::Square { rect } | core::GeometricGeometry::Circle { rect } => {
                Some(*rect)
            }
            _ => None,
        }
    }
    #[getter]
    fn vertices(&self) -> Option<Vec<(f64, f64)>> {
        match &self.inner {
            core::GeometricGeometry::Polygon { vertices }
            | core::GeometricGeometry::PolyLine { vertices, .. } => {
                Some(vertices.iter().map(|p| (p.x, p.y)).collect())
            }
            _ => None,
        }
    }
    #[getter]
    fn start(&self) -> Option<(f64, f64)> {
        match &self.inner {
            core::GeometricGeometry::Line { start, .. } => Some((start.x, start.y)),
            _ => None,
        }
    }
    #[getter]
    fn end(&self) -> Option<(f64, f64)> {
        match &self.inner {
            core::GeometricGeometry::Line { end, .. } => Some((end.x, end.y)),
            _ => None,
        }
    }
    #[getter]
    fn start_ending(&self) -> Option<PyGeometricLineEnding> {
        match &self.inner {
            core::GeometricGeometry::Line { start_ending, .. }
            | core::GeometricGeometry::PolyLine { start_ending, .. } => {
                Some((*start_ending).into())
            }
            _ => None,
        }
    }
    #[getter]
    fn end_ending(&self) -> Option<PyGeometricLineEnding> {
        match &self.inner {
            core::GeometricGeometry::Line { end_ending, .. }
            | core::GeometricGeometry::PolyLine { end_ending, .. } => Some((*end_ending).into()),
            _ => None,
        }
    }
}
#[pyclass(name = "GeometricStyle", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyGeometricStyle {
    inner: core::GeometricStyle,
}
#[pymethods]
impl PyGeometricStyle {
    #[new]
    #[pyo3(signature=(stroke_color,width,fill_color=None,dash_pattern=None,opacity=None))]
    fn new(
        stroke_color: PyGeometricColor,
        width: f64,
        fill_color: Option<PyGeometricColor>,
        dash_pattern: Option<Vec<f64>>,
        opacity: Option<f64>,
    ) -> PyResult<Self> {
        Ok(Self {
            inner: core::GeometricStyle {
                stroke_color: stroke_color.inner,
                width: core::GeometricWidth::new(width).map_err(to_py_err)?,
                fill_color: fill_color.map(|v| v.inner),
                dash_pattern: dash_pattern
                    .map(core::GeometricDashPattern::new)
                    .transpose()
                    .map_err(to_py_err)?,
                opacity: opacity
                    .map(core::GeometricOpacity::new)
                    .transpose()
                    .map_err(to_py_err)?,
            },
        })
    }
    #[getter]
    fn stroke_color(&self) -> PyGeometricColor {
        PyGeometricColor {
            inner: self.inner.stroke_color,
        }
    }
    #[getter]
    fn fill_color(&self) -> Option<PyGeometricColor> {
        self.inner
            .fill_color
            .map(|inner| PyGeometricColor { inner })
    }
    #[getter]
    fn width(&self) -> f64 {
        self.inner.width.value()
    }
    #[getter]
    fn opacity(&self) -> Option<f64> {
        self.inner.opacity.map(|v| v.value())
    }
    #[getter]
    fn dash_pattern(&self) -> Option<Vec<f64>> {
        self.inner
            .dash_pattern
            .as_ref()
            .map(|v| v.values().to_vec())
    }
}
#[pyclass(name = "GeometricAnnotation", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyGeometricAnnotation {
    inner: core::GeometricAnnotation,
}
#[pymethods]
impl PyGeometricAnnotation {
    #[getter]
    fn id(&self) -> PyGeometricId {
        PyGeometricId {
            inner: self.inner.id,
        }
    }
    #[getter]
    fn page_index(&self) -> u32 {
        self.inner.page_index
    }
    #[getter]
    fn geometry(&self) -> PyGeometricGeometry {
        PyGeometricGeometry {
            inner: self.inner.geometry.clone(),
        }
    }
    #[getter]
    fn style(&self) -> PyGeometricStyle {
        PyGeometricStyle {
            inner: self.inner.style.clone(),
        }
    }
}
#[pyclass(name = "GeometricMutation", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyGeometricMutation {
    inner: core::GeometricMutation,
}
#[pymethods]
impl PyGeometricMutation {
    #[staticmethod]
    fn add(page_index: u32, geometry: PyGeometricGeometry, style: PyGeometricStyle) -> Self {
        Self {
            inner: core::GeometricMutation::Add {
                page_index,
                geometry: geometry.inner,
                style: style.inner,
            },
        }
    }
    #[staticmethod]
    fn update(id: PyGeometricId, geometry: PyGeometricGeometry, style: PyGeometricStyle) -> Self {
        Self {
            inner: core::GeometricMutation::Update {
                id: id.inner,
                geometry: geometry.inner,
                style: style.inner,
            },
        }
    }
    #[staticmethod]
    fn remove(id: PyGeometricId) -> Self {
        Self {
            inner: core::GeometricMutation::Remove { id: id.inner },
        }
    }
}
#[pyclass(name = "GeometricUpdate", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyGeometricUpdate {
    inner: core::GeometricUpdate,
}
#[pymethods]
impl PyGeometricUpdate {
    #[getter]
    fn pdf_bytes<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.inner.pdf_bytes)
    }
    #[getter]
    fn annotations(&self) -> Vec<PyGeometricAnnotation> {
        self.inner
            .annotations
            .iter()
            .cloned()
            .map(|inner| PyGeometricAnnotation { inner })
            .collect()
    }
}
/// Owns an immutable PDF snapshot. Every apply returns an independent new revision.
#[pyclass(name = "IncrementalGeometricEditor", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyIncrementalGeometricEditor {
    base: Vec<u8>,
}
#[pymethods]
impl PyIncrementalGeometricEditor {
    #[new]
    fn new(pdf: &[u8]) -> Self {
        Self { base: pdf.to_vec() }
    }
    fn annotations(&self, py: Python<'_>) -> PyResult<Vec<PyGeometricAnnotation>> {
        let values = py
            .detach(|| core::IncrementalGeometricEditor::new(&self.base).annotations())
            .map_err(to_py_err)?;
        Ok(values
            .into_iter()
            .map(|inner| PyGeometricAnnotation { inner })
            .collect())
    }
    fn apply(
        &self,
        py: Python<'_>,
        mutations: Vec<PyGeometricMutation>,
    ) -> PyResult<PyGeometricUpdate> {
        let mutations: Vec<_> = mutations.into_iter().map(|m| m.inner).collect();
        let inner = py
            .detach(|| core::IncrementalGeometricEditor::new(&self.base).apply(&mutations))
            .map_err(to_py_err)?;
        Ok(PyGeometricUpdate { inner })
    }
}
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyGeometricColorSpace>()?;
    m.add_class::<PyGeometricColor>()?;
    m.add_class::<PyGeometricId>()?;
    m.add_class::<PyGeometricLineEnding>()?;
    m.add_class::<PyGeometricKind>()?;
    m.add_class::<PyGeometricGeometry>()?;
    m.add_class::<PyGeometricStyle>()?;
    m.add_class::<PyGeometricAnnotation>()?;
    m.add_class::<PyGeometricMutation>()?;
    m.add_class::<PyGeometricUpdate>()?;
    m.add_class::<PyIncrementalGeometricEditor>()?;
    Ok(())
}
