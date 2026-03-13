use pyo3::prelude::*;

// ── Color ──────────────────────────────────────────────────────────────────

#[pyclass(name = "Color", from_py_object)]
#[derive(Clone)]
pub struct PyColor {
    pub inner: oxidize_pdf::Color,
}

#[pymethods]
impl PyColor {
    #[staticmethod]
    fn rgb(r: f64, g: f64, b: f64) -> Self {
        Self {
            inner: oxidize_pdf::Color::rgb(r, g, b),
        }
    }

    #[staticmethod]
    fn gray(value: f64) -> Self {
        Self {
            inner: oxidize_pdf::Color::gray(value),
        }
    }

    #[staticmethod]
    fn cmyk(c: f64, m: f64, y: f64, k: f64) -> Self {
        Self {
            inner: oxidize_pdf::Color::cmyk(c, m, y, k),
        }
    }

    #[staticmethod]
    fn hex(hex_str: &str) -> Self {
        Self {
            inner: oxidize_pdf::Color::hex(hex_str),
        }
    }

    #[staticmethod]
    fn black() -> Self {
        Self {
            inner: oxidize_pdf::Color::black(),
        }
    }

    #[staticmethod]
    fn white() -> Self {
        Self {
            inner: oxidize_pdf::Color::white(),
        }
    }

    #[staticmethod]
    fn red() -> Self {
        Self {
            inner: oxidize_pdf::Color::red(),
        }
    }

    #[staticmethod]
    fn green() -> Self {
        Self {
            inner: oxidize_pdf::Color::green(),
        }
    }

    #[staticmethod]
    fn blue() -> Self {
        Self {
            inner: oxidize_pdf::Color::blue(),
        }
    }

    /// Red component (converts to RGB approximation if needed).
    #[getter]
    fn r(&self) -> f64 {
        self.inner.r()
    }

    /// Green component (converts to RGB approximation if needed).
    #[getter]
    fn g(&self) -> f64 {
        self.inner.g()
    }

    /// Blue component (converts to RGB approximation if needed).
    #[getter]
    fn b(&self) -> f64 {
        self.inner.b()
    }

    /// Gray value (only meaningful for Gray colors).
    #[getter]
    fn gray_value(&self) -> f64 {
        match self.inner {
            oxidize_pdf::Color::Gray(v) => v,
            _ => self.inner.r(), // approximate
        }
    }

    /// Cyan component (only meaningful for CMYK colors).
    #[getter]
    fn c(&self) -> f64 {
        match self.inner {
            oxidize_pdf::Color::Cmyk(c, _, _, _) => c,
            _ => 0.0,
        }
    }

    /// Magenta component (only meaningful for CMYK colors).
    #[getter]
    fn m(&self) -> f64 {
        match self.inner {
            oxidize_pdf::Color::Cmyk(_, m, _, _) => m,
            _ => 0.0,
        }
    }

    /// Yellow component (only meaningful for CMYK colors).
    #[getter]
    fn y(&self) -> f64 {
        match self.inner {
            oxidize_pdf::Color::Cmyk(_, _, y, _) => y,
            _ => 0.0,
        }
    }

    /// Key/black component (only meaningful for CMYK colors).
    #[getter]
    fn k(&self) -> f64 {
        match self.inner {
            oxidize_pdf::Color::Cmyk(_, _, _, k) => k,
            _ => 0.0,
        }
    }

    /// The color space: "RGB", "Gray", or "CMYK".
    #[getter]
    fn color_space(&self) -> &str {
        match self.inner {
            oxidize_pdf::Color::Rgb(_, _, _) => "RGB",
            oxidize_pdf::Color::Gray(_) => "Gray",
            oxidize_pdf::Color::Cmyk(_, _, _, _) => "CMYK",
        }
    }

    fn __repr__(&self) -> String {
        match self.inner {
            oxidize_pdf::Color::Rgb(r, g, b) => format!("Color.rgb({r}, {g}, {b})"),
            oxidize_pdf::Color::Gray(v) => format!("Color.gray({v})"),
            oxidize_pdf::Color::Cmyk(c, m, y, k) => format!("Color.cmyk({c}, {m}, {y}, {k})"),
        }
    }
}

// ── Point ──────────────────────────────────────────────────────────────────

#[pyclass(name = "Point", from_py_object)]
#[derive(Clone)]
pub struct PyPoint {
    pub inner: oxidize_pdf::Point,
}

#[pymethods]
impl PyPoint {
    #[new]
    fn new(x: f64, y: f64) -> Self {
        Self {
            inner: oxidize_pdf::Point::new(x, y),
        }
    }

    #[staticmethod]
    fn origin() -> Self {
        Self {
            inner: oxidize_pdf::Point::origin(),
        }
    }

    #[getter]
    fn x(&self) -> f64 {
        self.inner.x
    }

    #[getter]
    fn y(&self) -> f64 {
        self.inner.y
    }

    fn __repr__(&self) -> String {
        format!("Point({}, {})", self.inner.x, self.inner.y)
    }

    fn __eq__(&self, other: &PyPoint) -> bool {
        self.inner == other.inner
    }
}

// ── Rectangle ──────────────────────────────────────────────────────────────

#[pyclass(name = "Rectangle", from_py_object)]
#[derive(Clone)]
pub struct PyRectangle {
    pub inner: oxidize_pdf::Rectangle,
}

#[pymethods]
impl PyRectangle {
    #[new]
    fn new(lower_left: &PyPoint, upper_right: &PyPoint) -> Self {
        Self {
            inner: oxidize_pdf::Rectangle::new(lower_left.inner, upper_right.inner),
        }
    }

    #[staticmethod]
    fn from_xywh(x: f64, y: f64, width: f64, height: f64) -> Self {
        Self {
            inner: oxidize_pdf::Rectangle::from_position_and_size(x, y, width, height),
        }
    }

    #[getter]
    fn lower_left(&self) -> PyPoint {
        PyPoint {
            inner: self.inner.lower_left,
        }
    }

    #[getter]
    fn upper_right(&self) -> PyPoint {
        PyPoint {
            inner: self.inner.upper_right,
        }
    }

    #[getter]
    fn width(&self) -> f64 {
        self.inner.width()
    }

    #[getter]
    fn height(&self) -> f64 {
        self.inner.height()
    }

    #[getter]
    fn center(&self) -> PyPoint {
        PyPoint {
            inner: self.inner.center(),
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "Rectangle(Point({}, {}), Point({}, {}))",
            self.inner.lower_left.x,
            self.inner.lower_left.y,
            self.inner.upper_right.x,
            self.inner.upper_right.y,
        )
    }
}

// ── Margins ────────────────────────────────────────────────────────────────

#[pyclass(name = "Margins", from_py_object)]
#[derive(Clone)]
pub struct PyMargins {
    pub inner: oxidize_pdf::Margins,
}

#[pymethods]
impl PyMargins {
    #[new]
    #[pyo3(signature = (top = 0.0, right = 0.0, bottom = 0.0, left = 0.0))]
    fn new(top: f64, right: f64, bottom: f64, left: f64) -> Self {
        Self {
            inner: oxidize_pdf::Margins {
                top,
                right,
                bottom,
                left,
            },
        }
    }

    #[staticmethod]
    fn uniform(value: f64) -> Self {
        Self {
            inner: oxidize_pdf::Margins {
                top: value,
                right: value,
                bottom: value,
                left: value,
            },
        }
    }

    #[getter]
    fn top(&self) -> f64 {
        self.inner.top
    }

    #[getter]
    fn right(&self) -> f64 {
        self.inner.right
    }

    #[getter]
    fn bottom(&self) -> f64 {
        self.inner.bottom
    }

    #[getter]
    fn left(&self) -> f64 {
        self.inner.left
    }

    fn __repr__(&self) -> String {
        format!(
            "Margins(top={}, right={}, bottom={}, left={})",
            self.inner.top, self.inner.right, self.inner.bottom, self.inner.left
        )
    }
}

// ── Registration ───────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyColor>()?;
    m.add_class::<PyPoint>()?;
    m.add_class::<PyRectangle>()?;
    m.add_class::<PyMargins>()?;
    Ok(())
}
