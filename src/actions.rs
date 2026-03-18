use pyo3::prelude::*;

use oxidize_pdf::actions;
use oxidize_pdf::structure::{Destination, NamedDestinations, PageDestination};

// ── UriAction ─────────────────────────────────────────────────────────────

#[pyclass(name = "UriAction", from_py_object)]
#[derive(Clone)]
pub struct PyUriAction {
    pub inner: actions::UriAction,
}

#[pymethods]
impl PyUriAction {
    #[new]
    fn new(uri: &str) -> Self {
        Self {
            inner: actions::UriAction::new(uri),
        }
    }

    #[staticmethod]
    fn web(url: &str) -> Self {
        Self {
            inner: actions::UriAction::web(url),
        }
    }

    #[staticmethod]
    fn email(address: &str) -> Self {
        Self {
            inner: actions::UriAction::email(address),
        }
    }

    fn __repr__(&self) -> String {
        format!("UriAction(uri={:?})", self.inner.uri)
    }
}

// ── GoToAction ────────────────────────────────────────────────────────────

#[pyclass(name = "GoToAction", from_py_object)]
#[derive(Clone)]
pub struct PyGoToAction {
    pub inner: actions::GoToAction,
}

#[pymethods]
impl PyGoToAction {
    #[staticmethod]
    fn to_page(page_number: u32) -> Self {
        Self {
            inner: actions::GoToAction::to_page(page_number),
        }
    }

    #[staticmethod]
    #[pyo3(signature = (page_number, x, y, zoom=None))]
    fn to_page_xyz(page_number: u32, x: f64, y: f64, zoom: Option<f64>) -> Self {
        Self {
            inner: actions::GoToAction::to_page_xyz(page_number, x, y, zoom),
        }
    }

    fn __repr__(&self) -> String {
        "GoToAction(...)".to_string()
    }
}

// ── JavaScriptAction ──────────────────────────────────────────────────────

#[pyclass(name = "JavaScriptAction", from_py_object)]
#[derive(Clone)]
pub struct PyJavaScriptAction {
    pub inner: actions::JavaScriptAction,
}

#[pymethods]
impl PyJavaScriptAction {
    #[new]
    fn new(script: &str) -> Self {
        Self {
            inner: actions::JavaScriptAction::new(script),
        }
    }

    fn __repr__(&self) -> String {
        "JavaScriptAction(...)".to_string()
    }
}

// ── ResetFormAction ───────────────────────────────────────────────────────

#[pyclass(name = "ResetFormAction", from_py_object)]
#[derive(Clone)]
pub struct PyResetFormAction {
    pub inner: actions::ResetFormAction,
}

#[pymethods]
impl PyResetFormAction {
    #[new]
    fn new() -> Self {
        Self {
            inner: actions::ResetFormAction::new(),
        }
    }

    fn __repr__(&self) -> String {
        "ResetFormAction(...)".to_string()
    }
}

// ── Destination ───────────────────────────────────────────────────────────

#[pyclass(name = "Destination", from_py_object)]
#[derive(Clone)]
pub struct PyDestination {
    pub inner: Destination,
}

#[pymethods]
impl PyDestination {
    #[staticmethod]
    fn fit(page_number: u32) -> Self {
        Self {
            inner: Destination::fit(PageDestination::PageNumber(page_number)),
        }
    }

    #[staticmethod]
    fn xyz(page_number: u32, left: f64, top: f64, zoom: f64) -> Self {
        Self {
            inner: Destination::xyz(
                PageDestination::PageNumber(page_number),
                Some(left),
                Some(top),
                Some(zoom),
            ),
        }
    }

    #[staticmethod]
    fn fit_h(page_number: u32, top: f64) -> Self {
        Self {
            inner: Destination::fit_h(
                PageDestination::PageNumber(page_number),
                Some(top),
            ),
        }
    }

    #[staticmethod]
    fn fit_v(page_number: u32, left: f64) -> Self {
        Self {
            inner: Destination::fit_v(
                PageDestination::PageNumber(page_number),
                Some(left),
            ),
        }
    }

    #[staticmethod]
    fn fit_b(page_number: u32) -> Self {
        Self {
            inner: Destination::fit_b(PageDestination::PageNumber(page_number)),
        }
    }

    fn __repr__(&self) -> String {
        "Destination(...)".to_string()
    }
}

// ── NamedDestinations ─────────────────────────────────────────────────────

#[pyclass(name = "NamedDestinations")]
pub struct PyNamedDestinations {
    pub inner: NamedDestinations,
}

#[pymethods]
impl PyNamedDestinations {
    #[new]
    fn new() -> Self {
        Self {
            inner: NamedDestinations::new(),
        }
    }

    /// Add a named destination.
    fn add(&mut self, name: &str, destination: &PyDestination) {
        self.inner
            .add_destination(name.to_string(), destination.inner.to_array());
    }

    fn __repr__(&self) -> String {
        "NamedDestinations(...)".to_string()
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyUriAction>()?;
    m.add_class::<PyGoToAction>()?;
    m.add_class::<PyJavaScriptAction>()?;
    m.add_class::<PyResetFormAction>()?;
    m.add_class::<PyDestination>()?;
    m.add_class::<PyNamedDestinations>()?;
    Ok(())
}
