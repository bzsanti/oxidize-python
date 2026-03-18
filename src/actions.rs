use pyo3::prelude::*;

use oxidize_pdf::actions;
use oxidize_pdf::actions::{HideAction, LaunchAction, NamedAction, StandardNamedAction, SubmitFormAction};
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

// ── LaunchAction ──────────────────────────────────────────────────────────

#[pyclass(name = "LaunchAction", from_py_object)]
#[derive(Clone)]
pub struct PyLaunchAction {
    pub inner: LaunchAction,
}

#[pymethods]
impl PyLaunchAction {
    #[new]
    fn new(file: &str) -> Self {
        Self { inner: LaunchAction::new(file) }
    }

    #[staticmethod]
    fn application(app: &str) -> Self {
        Self { inner: LaunchAction::application(app) }
    }

    #[staticmethod]
    fn document(path: &str) -> Self {
        Self { inner: LaunchAction::document(path) }
    }

    fn with_params(self_: PyRef<'_, Self>, params: &str) -> Self {
        Self { inner: self_.inner.clone().with_params(params) }
    }

    fn in_new_window(self_: PyRef<'_, Self>, new_window: bool) -> Self {
        Self { inner: self_.inner.clone().in_new_window(new_window) }
    }

    fn __repr__(&self) -> String {
        format!("LaunchAction(file={:?})", self.inner.file)
    }
}

// ── StandardNamedAction ───────────────────────────────────────────────────

#[pyclass(name = "StandardNamedAction", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyStandardNamedAction {
    pub inner: StandardNamedAction,
}

#[pymethods]
impl PyStandardNamedAction {
    #[classattr] const NEXT_PAGE: Self = Self { inner: StandardNamedAction::NextPage };
    #[classattr] const PREV_PAGE: Self = Self { inner: StandardNamedAction::PrevPage };
    #[classattr] const FIRST_PAGE: Self = Self { inner: StandardNamedAction::FirstPage };
    #[classattr] const LAST_PAGE: Self = Self { inner: StandardNamedAction::LastPage };
    #[classattr] const GO_BACK: Self = Self { inner: StandardNamedAction::GoBack };
    #[classattr] const GO_FORWARD: Self = Self { inner: StandardNamedAction::GoForward };
    #[classattr] const PRINT: Self = Self { inner: StandardNamedAction::Print };
    #[classattr] const SAVE_AS: Self = Self { inner: StandardNamedAction::SaveAs };
    #[classattr] const FULL_SCREEN: Self = Self { inner: StandardNamedAction::FullScreen };
    #[classattr] const FIT_PAGE: Self = Self { inner: StandardNamedAction::FitPage };
    #[classattr] const FIT_WIDTH: Self = Self { inner: StandardNamedAction::FitWidth };
    #[classattr] const FIT_HEIGHT: Self = Self { inner: StandardNamedAction::FitHeight };
    #[classattr] const FIND: Self = Self { inner: StandardNamedAction::Find };
    #[classattr] const BOOKMARKS: Self = Self { inner: StandardNamedAction::Bookmarks };

    fn __repr__(&self) -> String {
        format!("StandardNamedAction.{}", self.inner.to_name())
    }
}

// ── NamedAction ───────────────────────────────────────────────────────────

#[pyclass(name = "NamedAction", from_py_object)]
#[derive(Clone)]
pub struct PyNamedAction {
    pub inner: NamedAction,
}

#[pymethods]
impl PyNamedAction {
    #[staticmethod]
    fn standard(action: &PyStandardNamedAction) -> Self {
        Self { inner: NamedAction::standard(action.inner) }
    }

    #[staticmethod]
    fn custom(name: &str) -> Self {
        Self { inner: NamedAction::custom(name) }
    }

    #[staticmethod]
    fn next_page() -> Self { Self { inner: NamedAction::next_page() } }
    #[staticmethod]
    fn prev_page() -> Self { Self { inner: NamedAction::prev_page() } }
    #[staticmethod]
    fn first_page() -> Self { Self { inner: NamedAction::first_page() } }
    #[staticmethod]
    fn last_page() -> Self { Self { inner: NamedAction::last_page() } }
    #[staticmethod]
    fn print() -> Self { Self { inner: NamedAction::print() } }
    #[staticmethod]
    fn full_screen() -> Self { Self { inner: NamedAction::full_screen() } }
    #[staticmethod]
    fn fit_page() -> Self { Self { inner: NamedAction::fit_page() } }
    #[staticmethod]
    fn fit_width() -> Self { Self { inner: NamedAction::fit_width() } }

    fn name(&self) -> &str {
        self.inner.name()
    }

    fn __repr__(&self) -> String {
        format!("NamedAction({:?})", self.inner.name())
    }
}

// ── SubmitFormAction ──────────────────────────────────────────────────────

#[pyclass(name = "SubmitFormAction", from_py_object)]
#[derive(Clone)]
pub struct PySubmitFormAction {
    pub inner: SubmitFormAction,
}

#[pymethods]
impl PySubmitFormAction {
    #[new]
    fn new(url: &str) -> Self {
        Self { inner: SubmitFormAction::new(url) }
    }

    fn as_html(self_: PyRef<'_, Self>) -> Self {
        Self { inner: self_.inner.clone().as_html() }
    }

    fn as_xml(self_: PyRef<'_, Self>) -> Self {
        Self { inner: self_.inner.clone().as_xml() }
    }

    fn as_pdf(self_: PyRef<'_, Self>) -> Self {
        Self { inner: self_.inner.clone().as_pdf() }
    }

    fn with_fields(self_: PyRef<'_, Self>, fields: Vec<String>) -> Self {
        Self { inner: self_.inner.clone().with_fields(fields) }
    }

    fn with_charset(self_: PyRef<'_, Self>, charset: &str) -> Self {
        Self { inner: self_.inner.clone().with_charset(charset) }
    }

    fn __repr__(&self) -> String {
        format!("SubmitFormAction(url={:?})", self.inner.url)
    }
}

// ── HideAction ────────────────────────────────────────────────────────────

#[pyclass(name = "HideAction", from_py_object)]
#[derive(Clone)]
pub struct PyHideAction {
    pub inner: HideAction,
}

#[pymethods]
impl PyHideAction {
    #[new]
    fn new(targets: Vec<String>) -> Self {
        Self { inner: HideAction::new(targets) }
    }

    fn hide(self_: PyRef<'_, Self>) -> Self {
        Self { inner: self_.inner.clone().hide() }
    }

    fn show(self_: PyRef<'_, Self>) -> Self {
        Self { inner: self_.inner.clone().show() }
    }

    fn __repr__(&self) -> String {
        format!("HideAction(targets={:?})", self.inner.targets)
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
    m.add_class::<PyLaunchAction>()?;
    m.add_class::<PyStandardNamedAction>()?;
    m.add_class::<PyNamedAction>()?;
    m.add_class::<PySubmitFormAction>()?;
    m.add_class::<PyHideAction>()?;
    Ok(())
}
