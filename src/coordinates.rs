//! Owned coordinate transformations from the published core.
use crate::types::PyPoint;
use oxidize_pdf::coordinate_system::TransformMatrix;
use pyo3::prelude::*;

/// Affine matrix with immutable components. Angles are in radians.
#[pyclass(name = "TransformMatrix", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTransformMatrix {
    pub inner: TransformMatrix,
}

#[pymethods]
impl PyTransformMatrix {
    #[new]
    fn new(a: f64, b: f64, c: f64, d: f64, e: f64, f: f64) -> Self {
        Self {
            inner: TransformMatrix::new(a, b, c, d, e, f),
        }
    }
    #[classattr]
    const IDENTITY: Self = Self {
        inner: TransformMatrix::IDENTITY,
    };
    #[getter]
    fn a(&self) -> f64 {
        self.inner.a
    }
    #[getter]
    fn b(&self) -> f64 {
        self.inner.b
    }
    #[getter]
    fn c(&self) -> f64 {
        self.inner.c
    }
    #[getter]
    fn d(&self) -> f64 {
        self.inner.d
    }
    #[getter]
    fn e(&self) -> f64 {
        self.inner.e
    }
    #[getter]
    fn f(&self) -> f64 {
        self.inner.f
    }
    #[staticmethod]
    fn translate(tx: f64, ty: f64) -> Self {
        Self {
            inner: TransformMatrix::translate(tx, ty),
        }
    }
    #[staticmethod]
    fn scale(sx: f64, sy: f64) -> Self {
        Self {
            inner: TransformMatrix::scale(sx, sy),
        }
    }
    #[staticmethod]
    fn rotate(angle: f64) -> Self {
        Self {
            inner: TransformMatrix::rotate(angle),
        }
    }
    #[staticmethod]
    fn flip_y(page_height: f64) -> Self {
        Self {
            inner: TransformMatrix::flip_y(page_height),
        }
    }
    /// Return self * other: apply other first, then self.
    fn multiply(&self, other: &Self) -> Self {
        Self {
            inner: self.inner.multiply(&other.inner),
        }
    }
    fn transform_point(&self, point: &PyPoint) -> PyPoint {
        PyPoint {
            inner: self.inner.transform_point(point.inner),
        }
    }
    fn to_pdf_ctm(&self) -> String {
        self.inner.to_pdf_ctm()
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTransformMatrix>()?;
    m.add_class::<PyRenderContext>()
}

/// Mutable core rendering context. Conversions use coordinate_system and
/// page_height, not the independently stored current_transform field.
#[pyclass(name = "RenderContext")]
pub struct PyRenderContext {
    inner: oxidize_pdf::coordinate_system::RenderContext,
}

#[pymethods]
impl PyRenderContext {
    #[new]
    fn new(
        coordinate_system: &crate::tier8::PyCoordinateSystem,
        page_width: f64,
        page_height: f64,
    ) -> Self {
        Self {
            inner: oxidize_pdf::coordinate_system::RenderContext::new(
                coordinate_system.inner,
                page_width,
                page_height,
            ),
        }
    }
    #[getter]
    fn coordinate_system(&self) -> crate::tier8::PyCoordinateSystem {
        crate::tier8::PyCoordinateSystem {
            inner: self.inner.coordinate_system,
        }
    }
    #[setter]
    fn set_coordinate_system(&mut self, value: &crate::tier8::PyCoordinateSystem) {
        self.inner.coordinate_system = value.inner;
    }
    #[getter]
    fn page_width(&self) -> f64 {
        self.inner.page_width
    }
    #[setter]
    fn set_page_width(&mut self, value: f64) {
        self.inner.page_width = value;
    }
    #[getter]
    fn page_height(&self) -> f64 {
        self.inner.page_height
    }
    #[setter]
    fn set_page_height(&mut self, value: f64) {
        self.inner.page_height = value;
    }
    #[getter]
    fn current_transform(&self) -> PyTransformMatrix {
        PyTransformMatrix {
            inner: self.inner.current_transform,
        }
    }
    #[setter]
    fn set_current_transform(&mut self, value: &PyTransformMatrix) {
        self.inner.current_transform = value.inner;
    }
    fn to_pdf_standard(&self, point: &PyPoint) -> PyPoint {
        PyPoint {
            inner: self.inner.to_pdf_standard(point.inner),
        }
    }
    fn y_to_pdf(&self, y: f64) -> f64 {
        self.inner.y_to_pdf(y)
    }
}
