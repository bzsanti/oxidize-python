use pyo3::prelude::*;

use oxidize_pdf::graphics::calibrated_color::{CalGrayColorSpace, CalRgbColorSpace, CalibratedColor};
use oxidize_pdf::graphics::lab_color::LabColor;
use oxidize_pdf::graphics::state::{BlendMode, LineDashPattern};
use oxidize_pdf::graphics::{ClippingPath, LineCap, LineJoin};

use crate::tier8::PyLabColorSpace;

// ── LineCap ───────────────────────────────────────────────────────────────

#[pyclass(name = "LineCap", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyLineCap {
    pub inner: LineCap,
}

#[pymethods]
impl PyLineCap {
    #[classattr]
    const BUTT: PyLineCap = PyLineCap {
        inner: LineCap::Butt,
    };
    #[classattr]
    const ROUND: PyLineCap = PyLineCap {
        inner: LineCap::Round,
    };
    #[classattr]
    const SQUARE: PyLineCap = PyLineCap {
        inner: LineCap::Square,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            LineCap::Butt => "BUTT",
            LineCap::Round => "ROUND",
            LineCap::Square => "SQUARE",
        };
        format!("LineCap.{name}")
    }
}

// ── LineJoin ──────────────────────────────────────────────────────────────

#[pyclass(name = "LineJoin", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyLineJoin {
    pub inner: LineJoin,
}

#[pymethods]
impl PyLineJoin {
    #[classattr]
    const MITER: PyLineJoin = PyLineJoin {
        inner: LineJoin::Miter,
    };
    #[classattr]
    const ROUND: PyLineJoin = PyLineJoin {
        inner: LineJoin::Round,
    };
    #[classattr]
    const BEVEL: PyLineJoin = PyLineJoin {
        inner: LineJoin::Bevel,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            LineJoin::Miter => "MITER",
            LineJoin::Round => "ROUND",
            LineJoin::Bevel => "BEVEL",
        };
        format!("LineJoin.{name}")
    }
}

// ── LineDashPattern ───────────────────────────────────────────────────────

#[pyclass(name = "LineDashPattern", from_py_object)]
#[derive(Clone)]
pub struct PyLineDashPattern {
    pub inner: LineDashPattern,
}

#[pymethods]
impl PyLineDashPattern {
    #[new]
    fn new(array: Vec<f64>, phase: f64) -> Self {
        Self {
            inner: LineDashPattern::new(array, phase),
        }
    }

    #[staticmethod]
    fn solid() -> Self {
        Self {
            inner: LineDashPattern::solid(),
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "LineDashPattern(array={:?}, phase={})",
            self.inner.array, self.inner.phase
        )
    }
}

// ── BlendMode ─────────────────────────────────────────────────────────────

#[pyclass(name = "BlendMode", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyBlendMode {
    pub inner: BlendMode,
}

#[pymethods]
impl PyBlendMode {
    #[classattr]
    const NORMAL: PyBlendMode = PyBlendMode {
        inner: BlendMode::Normal,
    };
    #[classattr]
    const MULTIPLY: PyBlendMode = PyBlendMode {
        inner: BlendMode::Multiply,
    };
    #[classattr]
    const SCREEN: PyBlendMode = PyBlendMode {
        inner: BlendMode::Screen,
    };
    #[classattr]
    const OVERLAY: PyBlendMode = PyBlendMode {
        inner: BlendMode::Overlay,
    };
    #[classattr]
    const SOFT_LIGHT: PyBlendMode = PyBlendMode {
        inner: BlendMode::SoftLight,
    };
    #[classattr]
    const HARD_LIGHT: PyBlendMode = PyBlendMode {
        inner: BlendMode::HardLight,
    };
    #[classattr]
    const COLOR_DODGE: PyBlendMode = PyBlendMode {
        inner: BlendMode::ColorDodge,
    };
    #[classattr]
    const COLOR_BURN: PyBlendMode = PyBlendMode {
        inner: BlendMode::ColorBurn,
    };
    #[classattr]
    const DARKEN: PyBlendMode = PyBlendMode {
        inner: BlendMode::Darken,
    };
    #[classattr]
    const LIGHTEN: PyBlendMode = PyBlendMode {
        inner: BlendMode::Lighten,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            BlendMode::Normal => "NORMAL",
            BlendMode::Multiply => "MULTIPLY",
            BlendMode::Screen => "SCREEN",
            BlendMode::Overlay => "OVERLAY",
            BlendMode::SoftLight => "SOFT_LIGHT",
            BlendMode::HardLight => "HARD_LIGHT",
            BlendMode::ColorDodge => "COLOR_DODGE",
            BlendMode::ColorBurn => "COLOR_BURN",
            BlendMode::Darken => "DARKEN",
            BlendMode::Lighten => "LIGHTEN",
            _ => "OTHER",
        };
        format!("BlendMode.{name}")
    }
}

// ── ClippingPath ──────────────────────────────────────────────────────────

#[pyclass(name = "ClippingPath", from_py_object)]
#[derive(Clone)]
pub struct PyClippingPath {
    pub inner: ClippingPath,
}

#[pymethods]
impl PyClippingPath {
    #[staticmethod]
    fn rect(x: f64, y: f64, width: f64, height: f64) -> Self {
        Self {
            inner: ClippingPath::rect(x, y, width, height),
        }
    }

    #[staticmethod]
    fn circle(cx: f64, cy: f64, radius: f64) -> Self {
        Self {
            inner: ClippingPath::circle(cx, cy, radius),
        }
    }

    #[staticmethod]
    fn ellipse(cx: f64, cy: f64, rx: f64, ry: f64) -> Self {
        Self {
            inner: ClippingPath::ellipse(cx, cy, rx, ry),
        }
    }

    fn __repr__(&self) -> String {
        "ClippingPath(...)".to_string()
    }
}

// ── CalGrayColorSpace ─────────────────────────────────────────────────────

#[pyclass(name = "CalGrayColorSpace", from_py_object)]
#[derive(Clone)]
pub struct PyCalGrayColorSpace {
    pub inner: CalGrayColorSpace,
}

#[pymethods]
impl PyCalGrayColorSpace {
    #[new]
    fn new() -> Self {
        Self { inner: CalGrayColorSpace::new() }
    }

    #[staticmethod]
    fn d50() -> Self {
        Self { inner: CalGrayColorSpace::d50() }
    }

    #[staticmethod]
    fn d65() -> Self {
        Self { inner: CalGrayColorSpace::d65() }
    }

    fn with_gamma(self_: PyRef<'_, Self>, gamma: f64) -> Self {
        Self { inner: self_.inner.clone().with_gamma(gamma) }
    }

    fn with_white_point(self_: PyRef<'_, Self>, white_point: [f64; 3]) -> Self {
        Self { inner: self_.inner.clone().with_white_point(white_point) }
    }

    fn with_black_point(self_: PyRef<'_, Self>, black_point: [f64; 3]) -> Self {
        Self { inner: self_.inner.clone().with_black_point(black_point) }
    }

    #[getter]
    fn gamma(&self) -> f64 {
        self.inner.gamma
    }

    #[getter]
    fn white_point(&self) -> [f64; 3] {
        self.inner.white_point
    }

    fn __repr__(&self) -> String {
        format!("CalGrayColorSpace(gamma={})", self.inner.gamma)
    }
}

// ── CalRgbColorSpace ──────────────────────────────────────────────────────

#[pyclass(name = "CalRgbColorSpace", from_py_object)]
#[derive(Clone)]
pub struct PyCalRgbColorSpace {
    pub inner: CalRgbColorSpace,
}

#[pymethods]
impl PyCalRgbColorSpace {
    #[new]
    fn new() -> Self {
        Self { inner: CalRgbColorSpace::new() }
    }

    #[staticmethod]
    fn srgb() -> Self {
        Self { inner: CalRgbColorSpace::srgb() }
    }

    #[staticmethod]
    fn adobe_rgb() -> Self {
        Self { inner: CalRgbColorSpace::adobe_rgb() }
    }

    #[staticmethod]
    fn d65() -> Self {
        Self { inner: CalRgbColorSpace::d65() }
    }

    fn with_gamma(self_: PyRef<'_, Self>, gamma: [f64; 3]) -> Self {
        Self { inner: self_.inner.clone().with_gamma(gamma) }
    }

    fn with_white_point(self_: PyRef<'_, Self>, white_point: [f64; 3]) -> Self {
        Self { inner: self_.inner.clone().with_white_point(white_point) }
    }

    fn with_matrix(self_: PyRef<'_, Self>, matrix: [f64; 9]) -> Self {
        Self { inner: self_.inner.clone().with_matrix(matrix) }
    }

    #[getter]
    fn gamma(&self) -> (f64, f64, f64) {
        (self.inner.gamma[0], self.inner.gamma[1], self.inner.gamma[2])
    }

    fn __repr__(&self) -> String {
        "CalRgbColorSpace(...)".to_string()
    }
}

// ── CalibratedColor ───────────────────────────────────────────────────────

#[pyclass(name = "CalibratedColor", from_py_object)]
#[derive(Clone)]
pub struct PyCalibratedColor {
    pub inner: CalibratedColor,
}

#[pymethods]
impl PyCalibratedColor {
    #[staticmethod]
    fn cal_gray(value: f64, cs: &PyCalGrayColorSpace) -> Self {
        Self { inner: CalibratedColor::cal_gray(value, cs.inner.clone()) }
    }

    #[staticmethod]
    fn cal_rgb(rgb: [f64; 3], cs: &PyCalRgbColorSpace) -> Self {
        Self { inner: CalibratedColor::cal_rgb(rgb, cs.inner.clone()) }
    }

    fn values(&self) -> Vec<f64> {
        self.inner.values()
    }

    fn __repr__(&self) -> String {
        format!("CalibratedColor({:?})", self.inner.values())
    }
}

// ── LabColor ──────────────────────────────────────────────────────────────

#[pyclass(name = "LabColor", from_py_object)]
#[derive(Clone)]
pub struct PyLabColor {
    pub inner: LabColor,
}

#[pymethods]
impl PyLabColor {
    #[new]
    fn new(l: f64, a: f64, b: f64, cs: &PyLabColorSpace) -> Self {
        Self { inner: LabColor::new(l, a, b, cs.inner.clone()) }
    }

    #[staticmethod]
    fn white() -> Self {
        Self { inner: LabColor::white() }
    }

    #[staticmethod]
    fn black() -> Self {
        Self { inner: LabColor::black() }
    }

    #[staticmethod]
    fn gray() -> Self {
        Self { inner: LabColor::gray() }
    }

    #[getter]
    fn l(&self) -> f64 {
        self.inner.l
    }

    #[getter]
    fn a(&self) -> f64 {
        self.inner.a
    }

    #[getter]
    fn b(&self) -> f64 {
        self.inner.b
    }

    fn values(&self) -> Vec<f64> {
        self.inner.values()
    }

    fn delta_e(&self, other: &PyLabColor) -> f64 {
        self.inner.delta_e(&other.inner)
    }

    fn __repr__(&self) -> String {
        format!("LabColor(l={}, a={}, b={})", self.inner.l, self.inner.a, self.inner.b)
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyLineCap>()?;
    m.add_class::<PyLineJoin>()?;
    m.add_class::<PyLineDashPattern>()?;
    m.add_class::<PyBlendMode>()?;
    m.add_class::<PyClippingPath>()?;
    m.add_class::<PyCalGrayColorSpace>()?;
    m.add_class::<PyCalRgbColorSpace>()?;
    m.add_class::<PyCalibratedColor>()?;
    m.add_class::<PyLabColor>()?;
    Ok(())
}
