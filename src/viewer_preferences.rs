use pyo3::prelude::*;

use oxidize_pdf::viewer_preferences::{
    Duplex, PageLayout, PageMode, PrintScaling, ViewerPreferences,
};

// ── PageLayout ─────────────────────────────────────────────────────────────

#[pyclass(name = "PageLayout", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyPageLayout {
    pub inner: PageLayout,
}

#[pymethods]
impl PyPageLayout {
    #[classattr]
    const SINGLE_PAGE: PyPageLayout = PyPageLayout {
        inner: PageLayout::SinglePage,
    };
    #[classattr]
    const ONE_COLUMN: PyPageLayout = PyPageLayout {
        inner: PageLayout::OneColumn,
    };
    #[classattr]
    const TWO_COLUMN_LEFT: PyPageLayout = PyPageLayout {
        inner: PageLayout::TwoColumnLeft,
    };
    #[classattr]
    const TWO_COLUMN_RIGHT: PyPageLayout = PyPageLayout {
        inner: PageLayout::TwoColumnRight,
    };
    #[classattr]
    const TWO_PAGE_LEFT: PyPageLayout = PyPageLayout {
        inner: PageLayout::TwoPageLeft,
    };
    #[classattr]
    const TWO_PAGE_RIGHT: PyPageLayout = PyPageLayout {
        inner: PageLayout::TwoPageRight,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            PageLayout::SinglePage => "SINGLE_PAGE",
            PageLayout::OneColumn => "ONE_COLUMN",
            PageLayout::TwoColumnLeft => "TWO_COLUMN_LEFT",
            PageLayout::TwoColumnRight => "TWO_COLUMN_RIGHT",
            PageLayout::TwoPageLeft => "TWO_PAGE_LEFT",
            PageLayout::TwoPageRight => "TWO_PAGE_RIGHT",
        };
        format!("PageLayout.{name}")
    }
}

// ── PageMode ───────────────────────────────────────────────────────────────

#[pyclass(name = "PageMode", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyPageMode {
    pub inner: PageMode,
}

#[pymethods]
impl PyPageMode {
    #[classattr]
    const USE_NONE: PyPageMode = PyPageMode {
        inner: PageMode::UseNone,
    };
    #[classattr]
    const USE_OUTLINES: PyPageMode = PyPageMode {
        inner: PageMode::UseOutlines,
    };
    #[classattr]
    const USE_THUMBS: PyPageMode = PyPageMode {
        inner: PageMode::UseThumbs,
    };
    #[classattr]
    const FULL_SCREEN: PyPageMode = PyPageMode {
        inner: PageMode::FullScreen,
    };
    #[classattr]
    const USE_OC: PyPageMode = PyPageMode {
        inner: PageMode::UseOC,
    };
    #[classattr]
    const USE_ATTACHMENTS: PyPageMode = PyPageMode {
        inner: PageMode::UseAttachments,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            PageMode::UseNone => "USE_NONE",
            PageMode::UseOutlines => "USE_OUTLINES",
            PageMode::UseThumbs => "USE_THUMBS",
            PageMode::FullScreen => "FULL_SCREEN",
            PageMode::UseOC => "USE_OC",
            PageMode::UseAttachments => "USE_ATTACHMENTS",
        };
        format!("PageMode.{name}")
    }
}

// ── PrintScaling ───────────────────────────────────────────────────────────

#[pyclass(name = "PrintScaling", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyPrintScaling {
    pub inner: PrintScaling,
}

#[pymethods]
impl PyPrintScaling {
    #[classattr]
    const NONE: PyPrintScaling = PyPrintScaling {
        inner: PrintScaling::None,
    };
    #[classattr]
    const APP_DEFAULT: PyPrintScaling = PyPrintScaling {
        inner: PrintScaling::AppDefault,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            PrintScaling::None => "NONE",
            PrintScaling::AppDefault => "APP_DEFAULT",
        };
        format!("PrintScaling.{name}")
    }
}

// ── Duplex ─────────────────────────────────────────────────────────────────

#[pyclass(name = "Duplex", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyDuplex {
    pub inner: Duplex,
}

#[pymethods]
impl PyDuplex {
    #[classattr]
    const SIMPLEX: PyDuplex = PyDuplex {
        inner: Duplex::Simplex,
    };
    #[classattr]
    const FLIP_SHORT_EDGE: PyDuplex = PyDuplex {
        inner: Duplex::DuplexFlipShortEdge,
    };
    #[classattr]
    const FLIP_LONG_EDGE: PyDuplex = PyDuplex {
        inner: Duplex::DuplexFlipLongEdge,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            Duplex::Simplex => "SIMPLEX",
            Duplex::DuplexFlipShortEdge => "FLIP_SHORT_EDGE",
            Duplex::DuplexFlipLongEdge => "FLIP_LONG_EDGE",
        };
        format!("Duplex.{name}")
    }
}

// ── ViewerPreferences ──────────────────────────────────────────────────────

#[pyclass(name = "ViewerPreferences", from_py_object)]
#[derive(Clone)]
pub struct PyViewerPreferences {
    pub inner: ViewerPreferences,
}

#[pymethods]
impl PyViewerPreferences {
    #[new]
    fn new() -> Self {
        Self {
            inner: ViewerPreferences::new(),
        }
    }

    fn hide_toolbar(self_: PyRef<'_, Self>, hide: bool) -> Self {
        Self {
            inner: self_.inner.clone().hide_toolbar(hide),
        }
    }

    fn hide_menubar(self_: PyRef<'_, Self>, hide: bool) -> Self {
        Self {
            inner: self_.inner.clone().hide_menubar(hide),
        }
    }

    fn hide_window_ui(self_: PyRef<'_, Self>, hide: bool) -> Self {
        Self {
            inner: self_.inner.clone().hide_window_ui(hide),
        }
    }

    fn fit_window(self_: PyRef<'_, Self>, fit: bool) -> Self {
        Self {
            inner: self_.inner.clone().fit_window(fit),
        }
    }

    fn center_window(self_: PyRef<'_, Self>, center: bool) -> Self {
        Self {
            inner: self_.inner.clone().center_window(center),
        }
    }

    fn display_doc_title(self_: PyRef<'_, Self>, display: bool) -> Self {
        Self {
            inner: self_.inner.clone().display_doc_title(display),
        }
    }

    fn page_layout(self_: PyRef<'_, Self>, layout: &PyPageLayout) -> Self {
        Self {
            inner: self_.inner.clone().page_layout(layout.inner),
        }
    }

    fn page_mode(self_: PyRef<'_, Self>, mode: &PyPageMode) -> Self {
        Self {
            inner: self_.inner.clone().page_mode(mode.inner),
        }
    }

    fn print_scaling(self_: PyRef<'_, Self>, scaling: &PyPrintScaling) -> Self {
        Self {
            inner: self_.inner.clone().print_scaling(scaling.inner),
        }
    }

    fn duplex(self_: PyRef<'_, Self>, duplex: &PyDuplex) -> Self {
        Self {
            inner: self_.inner.clone().duplex(duplex.inner),
        }
    }

    fn num_copies(self_: PyRef<'_, Self>, copies: u32) -> Self {
        Self {
            inner: self_.inner.clone().num_copies(copies),
        }
    }

    #[staticmethod]
    fn presentation() -> Self {
        Self {
            inner: ViewerPreferences::presentation(),
        }
    }

    #[staticmethod]
    fn reading() -> Self {
        Self {
            inner: ViewerPreferences::reading(),
        }
    }

    #[staticmethod]
    fn printing() -> Self {
        Self {
            inner: ViewerPreferences::printing(),
        }
    }

    #[staticmethod]
    fn minimal_ui() -> Self {
        Self {
            inner: ViewerPreferences::minimal_ui(),
        }
    }

    fn __repr__(&self) -> String {
        "ViewerPreferences(...)".to_string()
    }
}

// ── Registration ───────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPageLayout>()?;
    m.add_class::<PyPageMode>()?;
    m.add_class::<PyPrintScaling>()?;
    m.add_class::<PyDuplex>()?;
    m.add_class::<PyViewerPreferences>()?;
    Ok(())
}
