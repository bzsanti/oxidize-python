use pyo3::prelude::*;

use oxidize_pdf::annotations::{Annotation, AnnotationType};

use crate::types::{PyColor, PyRectangle};

// ── AnnotationType ────────────────────────────────────────────────────────

#[pyclass(name = "AnnotationType", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyAnnotationType {
    pub inner: AnnotationType,
}

#[pymethods]
impl PyAnnotationType {
    #[classattr]
    const TEXT: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Text };
    #[classattr]
    const LINK: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Link };
    #[classattr]
    const FREE_TEXT: PyAnnotationType = PyAnnotationType { inner: AnnotationType::FreeText };
    #[classattr]
    const LINE: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Line };
    #[classattr]
    const SQUARE: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Square };
    #[classattr]
    const CIRCLE: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Circle };
    #[classattr]
    const POLYGON: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Polygon };
    #[classattr]
    const POLY_LINE: PyAnnotationType = PyAnnotationType { inner: AnnotationType::PolyLine };
    #[classattr]
    const HIGHLIGHT: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Highlight };
    #[classattr]
    const UNDERLINE: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Underline };
    #[classattr]
    const SQUIGGLY: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Squiggly };
    #[classattr]
    const STRIKE_OUT: PyAnnotationType = PyAnnotationType { inner: AnnotationType::StrikeOut };
    #[classattr]
    const STAMP: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Stamp };
    #[classattr]
    const CARET: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Caret };
    #[classattr]
    const INK: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Ink };
    #[classattr]
    const POPUP: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Popup };
    #[classattr]
    const FILE_ATTACHMENT: PyAnnotationType = PyAnnotationType { inner: AnnotationType::FileAttachment };
    #[classattr]
    const SOUND: PyAnnotationType = PyAnnotationType { inner: AnnotationType::Sound };

    fn __repr__(&self) -> String {
        format!("AnnotationType.{}", self.inner.pdf_name())
    }
}

// ── Annotation ────────────────────────────────────────────────────────────

#[pyclass(name = "Annotation", from_py_object)]
#[derive(Clone)]
pub struct PyAnnotation {
    pub inner: Annotation,
}

#[pymethods]
impl PyAnnotation {
    #[new]
    fn new(annotation_type: &PyAnnotationType, rect: &PyRectangle) -> Self {
        Self {
            inner: Annotation::new(annotation_type.inner.clone(), rect.inner),
        }
    }

    fn with_contents(self_: PyRef<'_, Self>, contents: &str) -> Self {
        Self {
            inner: self_.inner.clone().with_contents(contents),
        }
    }

    fn with_subject(self_: PyRef<'_, Self>, subject: &str) -> Self {
        Self {
            inner: self_.inner.clone().with_subject(subject),
        }
    }

    fn with_name(self_: PyRef<'_, Self>, name: &str) -> Self {
        Self {
            inner: self_.inner.clone().with_name(name),
        }
    }

    fn with_color(self_: PyRef<'_, Self>, color: &PyColor) -> Self {
        Self {
            inner: self_.inner.clone().with_color(color.inner),
        }
    }

    fn __repr__(&self) -> String {
        format!("Annotation({:?})", self.inner.annotation_type.pdf_name())
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyAnnotationType>()?;
    m.add_class::<PyAnnotation>()?;
    Ok(())
}
