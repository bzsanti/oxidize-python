use pyo3::prelude::*;

use oxidize_pdf::graphics::state::{BlendMode, LineDashPattern};
use oxidize_pdf::graphics::{ClippingPath, LineCap, LineJoin};

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

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyLineCap>()?;
    m.add_class::<PyLineJoin>()?;
    m.add_class::<PyLineDashPattern>()?;
    m.add_class::<PyBlendMode>()?;
    m.add_class::<PyClippingPath>()?;
    Ok(())
}
