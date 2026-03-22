use pyo3::prelude::*;

// ── OrderedListStyle ──────────────────────────────────────────────────────

#[pyclass(name = "OrderedListStyle", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyOrderedListStyle {
    pub inner: oxidize_pdf::OrderedListStyle,
}

#[pymethods]
impl PyOrderedListStyle {
    #[classattr]
    const DECIMAL: PyOrderedListStyle = PyOrderedListStyle {
        inner: oxidize_pdf::OrderedListStyle::Decimal,
    };
    #[classattr]
    const LOWER_ALPHA: PyOrderedListStyle = PyOrderedListStyle {
        inner: oxidize_pdf::OrderedListStyle::LowerAlpha,
    };
    #[classattr]
    const UPPER_ALPHA: PyOrderedListStyle = PyOrderedListStyle {
        inner: oxidize_pdf::OrderedListStyle::UpperAlpha,
    };
    #[classattr]
    const LOWER_ROMAN: PyOrderedListStyle = PyOrderedListStyle {
        inner: oxidize_pdf::OrderedListStyle::LowerRoman,
    };
    #[classattr]
    const UPPER_ROMAN: PyOrderedListStyle = PyOrderedListStyle {
        inner: oxidize_pdf::OrderedListStyle::UpperRoman,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            oxidize_pdf::OrderedListStyle::Decimal => "DECIMAL",
            oxidize_pdf::OrderedListStyle::LowerAlpha => "LOWER_ALPHA",
            oxidize_pdf::OrderedListStyle::UpperAlpha => "UPPER_ALPHA",
            oxidize_pdf::OrderedListStyle::LowerRoman => "LOWER_ROMAN",
            oxidize_pdf::OrderedListStyle::UpperRoman => "UPPER_ROMAN",
            _ => "OTHER",
        };
        format!("OrderedListStyle.{name}")
    }
}

// ── BulletStyle ───────────────────────────────────────────────────────────

#[pyclass(name = "BulletStyle", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyBulletStyle {
    pub inner: oxidize_pdf::BulletStyle,
}

#[pymethods]
impl PyBulletStyle {
    #[classattr]
    const DISC: PyBulletStyle = PyBulletStyle {
        inner: oxidize_pdf::BulletStyle::Disc,
    };
    #[classattr]
    const CIRCLE: PyBulletStyle = PyBulletStyle {
        inner: oxidize_pdf::BulletStyle::Circle,
    };
    #[classattr]
    const SQUARE: PyBulletStyle = PyBulletStyle {
        inner: oxidize_pdf::BulletStyle::Square,
    };
    #[classattr]
    const DASH: PyBulletStyle = PyBulletStyle {
        inner: oxidize_pdf::BulletStyle::Dash,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            oxidize_pdf::BulletStyle::Disc => "DISC",
            oxidize_pdf::BulletStyle::Circle => "CIRCLE",
            oxidize_pdf::BulletStyle::Square => "SQUARE",
            oxidize_pdf::BulletStyle::Dash => "DASH",
            _ => "CUSTOM",
        };
        format!("BulletStyle.{name}")
    }
}

// ── OrderedList ───────────────────────────────────────────────────────────

#[pyclass(name = "OrderedList", from_py_object)]
#[derive(Clone)]
pub struct PyOrderedList {
    pub inner: oxidize_pdf::OrderedList,
}

#[pymethods]
impl PyOrderedList {
    #[new]
    fn new(style: &PyOrderedListStyle) -> Self {
        Self {
            inner: oxidize_pdf::OrderedList::new(style.inner),
        }
    }

    fn add_item(&mut self, text: &str) {
        self.inner.add_item(text.to_string());
    }

    fn set_start_number(&mut self, start: u32) {
        self.inner.set_start_number(start);
    }

    #[getter]
    fn height(&self) -> f64 {
        self.inner.get_height()
    }

    fn __repr__(&self) -> String {
        "OrderedList(...)".to_string()
    }
}

// ── UnorderedList ─────────────────────────────────────────────────────────

#[pyclass(name = "UnorderedList", from_py_object)]
#[derive(Clone)]
pub struct PyUnorderedList {
    pub inner: oxidize_pdf::UnorderedList,
}

#[pymethods]
impl PyUnorderedList {
    #[new]
    fn new(bullet_style: &PyBulletStyle) -> Self {
        Self {
            inner: oxidize_pdf::UnorderedList::new(bullet_style.inner),
        }
    }

    fn add_item(&mut self, text: &str) {
        self.inner.add_item(text.to_string());
    }

    #[getter]
    fn height(&self) -> f64 {
        self.inner.get_height()
    }

    fn __repr__(&self) -> String {
        "UnorderedList(...)".to_string()
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyOrderedListStyle>()?;
    m.add_class::<PyBulletStyle>()?;
    m.add_class::<PyOrderedList>()?;
    m.add_class::<PyUnorderedList>()?;
    Ok(())
}
