use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBool, PyDict, PyList};

use oxidize_pdf::graphics::calibrated_color::{CalGrayColorSpace, CalRgbColorSpace, CalibratedColor};
use oxidize_pdf::graphics::lab_color::LabColor;
use oxidize_pdf::graphics::state::{BlendMode, LineDashPattern};
use oxidize_pdf::graphics::{
    ClippingPath, DeviceColorSpace, LineCap, LineJoin, PageColorSpace, ParameterisedFamily,
};
use oxidize_pdf::objects::{Dictionary, Object};

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

// ── PageColorSpace (GFX-019 — page-level colour-space resources) ────────────

/// Convert a single Python value to a PDF [`Object`] for color-space
/// parameter dictionaries. Supports the scalar/array shapes calibrated and
/// ICC parameter dicts use: int, float, str (PDF name), and lists thereof.
fn py_to_pdf_object(value: &Bound<'_, PyAny>) -> PyResult<Object> {
    // bool before int: Python bool is a subclass of int, so extract::<i64>()
    // would silently accept True/False as 1/0. PDF parameter dicts have no
    // boolean type, so a bool here is always a caller mistake — reject it.
    if value.is_instance_of::<PyBool>() {
        return Err(PyValueError::new_err(
            "bool is not a valid PDF parameter value; use int or float",
        ));
    }
    // int before float: f64 extraction would also accept Python ints, but a
    // PDF /N channel count must serialise as an integer, not 3.0.
    if let Ok(i) = value.extract::<i64>() {
        return Ok(Object::Integer(i));
    }
    if let Ok(f) = value.extract::<f64>() {
        return Ok(Object::Real(f));
    }
    if let Ok(s) = value.extract::<String>() {
        return Ok(Object::Name(s));
    }
    if let Ok(list) = value.cast::<PyList>() {
        let mut arr = Vec::with_capacity(list.len());
        for item in list.iter() {
            arr.push(py_to_pdf_object(&item)?);
        }
        return Ok(Object::Array(arr));
    }
    Err(PyValueError::new_err(
        "unsupported value in color-space parameter dict; use int, float, \
         str (a PDF name), or a list of those",
    ))
}

/// Convert a Python ``dict[str, ...]`` into a PDF [`Dictionary`] for the
/// `parameterised` escape-hatch constructor.
fn py_dict_to_dictionary(params: &Bound<'_, PyDict>) -> PyResult<Dictionary> {
    let mut dict = Dictionary::new();
    for (key, value) in params.iter() {
        let key = key.extract::<String>().map_err(|_| {
            PyValueError::new_err("color-space parameter dict keys must be strings")
        })?;
        dict.set(key, py_to_pdf_object(&value)?);
    }
    Ok(dict)
}

/// Extract the parameter [`Dictionary`] from a colour space's
/// `[/<family> <<params>>]` PDF array representation. The family name is
/// tracked separately by [`PageColorSpace::Parameterised`], so only the
/// parameter dictionary (the array's second element) is needed here.
///
/// Returns an error rather than an empty dictionary if no `Dictionary` is
/// present: a calibrated colour space with empty params (`[/CalGray <<>>]`)
/// is invalid (missing `/WhitePoint`), so a future upstream change to
/// `to_pdf_array` must surface as an explicit error, never a silent
/// malformed colour space.
fn params_dict_from_array(array: Vec<Object>) -> PyResult<Dictionary> {
    array
        .into_iter()
        .find_map(|o| match o {
            Object::Dictionary(d) => Some(d),
            _ => None,
        })
        .ok_or_else(|| {
            PyValueError::new_err(
                "color-space array carried no parameter dictionary; \
                 cannot build a valid calibrated color space",
            )
        })
}

/// A colour space registrable on a [`crate::page::PyPage`] via
/// ``add_color_space`` and emitted at ``/Resources/ColorSpace/<name>``
/// (ISO 32000-1 §8.6). Construct via the typed static factories; use
/// ``parameterised`` for families the typed constructors don't cover.
#[pyclass(name = "PageColorSpace", from_py_object)]
#[derive(Clone)]
pub struct PyPageColorSpace {
    pub inner: PageColorSpace,
}

#[pymethods]
impl PyPageColorSpace {
    /// A named device-space alias. `name` is one of ``DeviceGray``,
    /// ``DeviceRGB``, ``DeviceCMYK``, ``Pattern``.
    #[staticmethod]
    fn device(name: &str) -> PyResult<Self> {
        let device = match name {
            "DeviceGray" => DeviceColorSpace::Gray,
            "DeviceRGB" => DeviceColorSpace::Rgb,
            "DeviceCMYK" => DeviceColorSpace::Cmyk,
            "Pattern" => DeviceColorSpace::Pattern,
            other => {
                return Err(PyValueError::new_err(format!(
                    "unknown device color space {other:?}; expected DeviceGray, \
                     DeviceRGB, DeviceCMYK, or Pattern"
                )))
            }
        };
        Ok(Self {
            inner: PageColorSpace::DeviceAlias(device),
        })
    }

    /// An ICCBased colour space with `n` channels (1=Gray, 3=RGB, 4=CMYK)
    /// and a device `alternate` (e.g. ``DeviceRGB``). Raises ``ValueError``
    /// if `n` is not 1, 3, or 4 (ISO 32000-1 §8.6.5.5).
    #[staticmethod]
    fn icc_based(n: i64, alternate: &str) -> PyResult<Self> {
        if !matches!(n, 1 | 3 | 4) {
            return Err(PyValueError::new_err(format!(
                "ICC channel count /N must be 1 (Gray), 3 (RGB/Lab), or 4 (CMYK); got {n}"
            )));
        }
        let mut params = Dictionary::new();
        params.set("N", Object::Integer(n));
        params.set("Alternate", Object::Name(alternate.to_string()));
        Ok(Self {
            inner: PageColorSpace::Parameterised {
                family: ParameterisedFamily::IccBased,
                params,
            },
        })
    }

    /// A CalGray calibrated colour space built from a ``CalGrayColorSpace``.
    #[staticmethod]
    fn cal_gray(cs: &PyCalGrayColorSpace) -> PyResult<Self> {
        Ok(Self {
            inner: PageColorSpace::Parameterised {
                family: ParameterisedFamily::CalGray,
                params: params_dict_from_array(cs.inner.to_pdf_array())?,
            },
        })
    }

    /// A CalRGB calibrated colour space built from a ``CalRgbColorSpace``.
    #[staticmethod]
    fn cal_rgb(cs: &PyCalRgbColorSpace) -> PyResult<Self> {
        Ok(Self {
            inner: PageColorSpace::Parameterised {
                family: ParameterisedFamily::CalRgb,
                params: params_dict_from_array(cs.inner.to_pdf_array())?,
            },
        })
    }

    /// A Lab colour space built from a ``LabColorSpace``.
    #[staticmethod]
    fn lab(cs: &PyLabColorSpace) -> PyResult<Self> {
        Ok(Self {
            inner: PageColorSpace::Parameterised {
                family: ParameterisedFamily::Lab,
                params: params_dict_from_array(cs.inner.to_pdf_array())?,
            },
        })
    }

    /// Generic escape hatch. `family` is one of ``CalGray``, ``CalRGB``,
    /// ``Lab``, ``ICCBased``; `params` is a dict of raw PDF parameter
    /// entries (values: int, float, str, or list of those).
    #[staticmethod]
    fn parameterised(family: &str, params: &Bound<'_, PyDict>) -> PyResult<Self> {
        let family = match family {
            "CalGray" => ParameterisedFamily::CalGray,
            "CalRGB" => ParameterisedFamily::CalRgb,
            "Lab" => ParameterisedFamily::Lab,
            "ICCBased" => ParameterisedFamily::IccBased,
            other => {
                return Err(PyValueError::new_err(format!(
                    "unknown parameterised color-space family {other:?}; expected \
                     CalGray, CalRGB, Lab, or ICCBased"
                )))
            }
        };
        Ok(Self {
            inner: PageColorSpace::Parameterised {
                family,
                params: py_dict_to_dictionary(params)?,
            },
        })
    }

    fn __repr__(&self) -> String {
        match &self.inner {
            PageColorSpace::DeviceAlias(_) => "PageColorSpace.device(...)".to_string(),
            // pdf_name() yields the ISO name (CalRGB, ICCBased), not the Rust
            // variant name (CalRgb, IccBased), so the repr matches the PDF.
            PageColorSpace::Parameterised { family, .. } => {
                format!("PageColorSpace.{}(...)", family.pdf_name())
            }
            _ => "PageColorSpace(...)".to_string(),
        }
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
    m.add_class::<PyPageColorSpace>()?;
    Ok(())
}
