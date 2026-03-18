use pyo3::prelude::*;

use oxidize_pdf::page_labels::{PageLabel, PageLabelStyle, PageLabelTree};

// ── PageLabelStyle ────────────────────────────────────────────────────────

#[pyclass(name = "PageLabelStyle", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyPageLabelStyle {
    pub inner: PageLabelStyle,
}

#[pymethods]
impl PyPageLabelStyle {
    #[classattr]
    const DECIMAL: PyPageLabelStyle = PyPageLabelStyle {
        inner: PageLabelStyle::DecimalArabic,
    };
    #[classattr]
    const ROMAN_UPPER: PyPageLabelStyle = PyPageLabelStyle {
        inner: PageLabelStyle::UppercaseRoman,
    };
    #[classattr]
    const ROMAN_LOWER: PyPageLabelStyle = PyPageLabelStyle {
        inner: PageLabelStyle::LowercaseRoman,
    };
    #[classattr]
    const ALPHA_UPPER: PyPageLabelStyle = PyPageLabelStyle {
        inner: PageLabelStyle::UppercaseLetters,
    };
    #[classattr]
    const ALPHA_LOWER: PyPageLabelStyle = PyPageLabelStyle {
        inner: PageLabelStyle::LowercaseLetters,
    };
    #[classattr]
    const NONE: PyPageLabelStyle = PyPageLabelStyle {
        inner: PageLabelStyle::None,
    };

    fn __repr__(&self) -> String {
        "PageLabelStyle(...)".to_string()
    }
}

// ── PageLabel ─────────────────────────────────────────────────────────────

#[pyclass(name = "PageLabel", from_py_object)]
#[derive(Clone)]
pub struct PyPageLabel {
    pub inner: PageLabel,
}

#[pymethods]
impl PyPageLabel {
    #[staticmethod]
    fn decimal() -> Self {
        Self {
            inner: PageLabel::decimal(),
        }
    }

    #[staticmethod]
    fn roman_uppercase() -> Self {
        Self {
            inner: PageLabel::roman_uppercase(),
        }
    }

    #[staticmethod]
    fn roman_lowercase() -> Self {
        Self {
            inner: PageLabel::roman_lowercase(),
        }
    }

    #[staticmethod]
    fn letters_uppercase() -> Self {
        Self {
            inner: PageLabel::letters_uppercase(),
        }
    }

    #[staticmethod]
    fn letters_lowercase() -> Self {
        Self {
            inner: PageLabel::letters_lowercase(),
        }
    }

    fn with_prefix(self_: PyRef<'_, Self>, prefix: &str) -> Self {
        Self {
            inner: self_.inner.clone().with_prefix(prefix),
        }
    }

    fn starting_at(self_: PyRef<'_, Self>, start: u32) -> Self {
        Self {
            inner: self_.inner.clone().starting_at(start),
        }
    }

    fn __repr__(&self) -> String {
        "PageLabel(...)".to_string()
    }
}

// ── PageLabelTree ─────────────────────────────────────────────────────────

#[pyclass(name = "PageLabelTree", from_py_object)]
#[derive(Clone)]
pub struct PyPageLabelTree {
    pub inner: PageLabelTree,
}

#[pymethods]
impl PyPageLabelTree {
    #[new]
    fn new() -> Self {
        Self {
            inner: PageLabelTree::new(),
        }
    }

    fn add_range(&mut self, start_page: u32, label: &PyPageLabel) {
        self.inner.add_range(start_page, label.inner.clone());
    }

    fn __repr__(&self) -> String {
        "PageLabelTree(...)".to_string()
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPageLabelStyle>()?;
    m.add_class::<PyPageLabel>()?;
    m.add_class::<PyPageLabelTree>()?;
    Ok(())
}
