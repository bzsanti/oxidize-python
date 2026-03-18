use pyo3::prelude::*;

use oxidize_pdf::annotations::{
    Annotation, AnnotationType, BorderStyle, BorderStyleType, Icon, MarkupAnnotation, MarkupType,
    TextAnnotation,
};

use crate::types::{PyColor, PyPoint, PyRectangle};

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

    fn with_border(self_: PyRef<'_, Self>, border: &PyBorderStyle) -> Self {
        Self {
            inner: self_.inner.clone().with_border(border.inner.clone()),
        }
    }

    fn __repr__(&self) -> String {
        format!("Annotation({:?})", self.inner.annotation_type.pdf_name())
    }
}

// ── MarkupType ────────────────────────────────────────────────────────────

#[pyclass(name = "MarkupType", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyMarkupType {
    pub inner: MarkupType,
}

#[pymethods]
impl PyMarkupType {
    #[classattr]
    const HIGHLIGHT: PyMarkupType = PyMarkupType { inner: MarkupType::Highlight };
    #[classattr]
    const UNDERLINE: PyMarkupType = PyMarkupType { inner: MarkupType::Underline };
    #[classattr]
    const STRIKE_OUT: PyMarkupType = PyMarkupType { inner: MarkupType::StrikeOut };
    #[classattr]
    const SQUIGGLY: PyMarkupType = PyMarkupType { inner: MarkupType::Squiggly };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            MarkupType::Highlight => "HIGHLIGHT",
            MarkupType::Underline => "UNDERLINE",
            MarkupType::StrikeOut => "STRIKE_OUT",
            MarkupType::Squiggly => "SQUIGGLY",
        };
        format!("MarkupType.{name}")
    }
}

// ── MarkupAnnotation ──────────────────────────────────────────────────────

#[pyclass(name = "MarkupAnnotation", from_py_object)]
#[derive(Clone)]
pub struct PyMarkupAnnotation {
    pub inner: MarkupAnnotation,
}

#[pymethods]
impl PyMarkupAnnotation {
    #[staticmethod]
    fn highlight(rect: &PyRectangle) -> Self {
        Self { inner: MarkupAnnotation::highlight(rect.inner) }
    }

    #[staticmethod]
    fn underline(rect: &PyRectangle) -> Self {
        Self { inner: MarkupAnnotation::underline(rect.inner) }
    }

    #[staticmethod]
    fn strikeout(rect: &PyRectangle) -> Self {
        Self { inner: MarkupAnnotation::strikeout(rect.inner) }
    }

    #[staticmethod]
    fn squiggly(rect: &PyRectangle) -> Self {
        Self { inner: MarkupAnnotation::squiggly(rect.inner) }
    }

    fn with_author(self_: PyRef<'_, Self>, author: &str) -> Self {
        Self { inner: self_.inner.clone().with_author(author) }
    }

    fn with_contents(self_: PyRef<'_, Self>, contents: &str) -> Self {
        Self { inner: self_.inner.clone().with_contents(contents) }
    }

    fn with_color(self_: PyRef<'_, Self>, color: &PyColor) -> Self {
        Self { inner: self_.inner.clone().with_color(color.inner) }
    }

    fn to_annotation(self_: PyRef<'_, Self>) -> PyAnnotation {
        PyAnnotation { inner: self_.inner.clone().to_annotation() }
    }

    fn __repr__(&self) -> String {
        "MarkupAnnotation(...)".to_string()
    }
}

// ── AnnotationIcon ────────────────────────────────────────────────────────

#[pyclass(name = "AnnotationIcon", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyAnnotationIcon {
    pub inner: Icon,
}

#[pymethods]
impl PyAnnotationIcon {
    #[classattr]
    const COMMENT: PyAnnotationIcon = PyAnnotationIcon { inner: Icon::Comment };
    #[classattr]
    const NOTE: PyAnnotationIcon = PyAnnotationIcon { inner: Icon::Note };
    #[classattr]
    const KEY: PyAnnotationIcon = PyAnnotationIcon { inner: Icon::Key };
    #[classattr]
    const HELP: PyAnnotationIcon = PyAnnotationIcon { inner: Icon::Help };
    #[classattr]
    const NEW_PARAGRAPH: PyAnnotationIcon = PyAnnotationIcon { inner: Icon::NewParagraph };
    #[classattr]
    const PARAGRAPH: PyAnnotationIcon = PyAnnotationIcon { inner: Icon::Paragraph };
    #[classattr]
    const INSERT: PyAnnotationIcon = PyAnnotationIcon { inner: Icon::Insert };

    fn __repr__(&self) -> String {
        format!("AnnotationIcon.{}", self.inner.pdf_name())
    }
}

// ── TextAnnotation ────────────────────────────────────────────────────────

#[pyclass(name = "TextAnnotation", from_py_object)]
#[derive(Clone)]
pub struct PyTextAnnotation {
    pub inner: TextAnnotation,
}

#[pymethods]
impl PyTextAnnotation {
    #[new]
    fn new(position: &PyPoint) -> Self {
        Self { inner: TextAnnotation::new(position.inner) }
    }

    fn with_icon(self_: PyRef<'_, Self>, icon: &PyAnnotationIcon) -> Self {
        Self { inner: self_.inner.clone().with_icon(icon.inner) }
    }

    fn with_contents(self_: PyRef<'_, Self>, contents: &str) -> Self {
        Self { inner: self_.inner.clone().with_contents(contents) }
    }

    fn open(self_: PyRef<'_, Self>) -> Self {
        Self { inner: self_.inner.clone().open() }
    }

    fn to_annotation(self_: PyRef<'_, Self>) -> PyAnnotation {
        PyAnnotation { inner: self_.inner.clone().to_annotation() }
    }

    fn __repr__(&self) -> String {
        "TextAnnotation(...)".to_string()
    }
}

// ── BorderStyleType ───────────────────────────────────────────────────────

#[pyclass(name = "BorderStyleType", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyBorderStyleType {
    pub inner: BorderStyleType,
}

#[pymethods]
impl PyBorderStyleType {
    #[classattr]
    const SOLID: PyBorderStyleType = PyBorderStyleType { inner: BorderStyleType::Solid };
    #[classattr]
    const DASHED: PyBorderStyleType = PyBorderStyleType { inner: BorderStyleType::Dashed };
    #[classattr]
    const BEVELED: PyBorderStyleType = PyBorderStyleType { inner: BorderStyleType::Beveled };
    #[classattr]
    const INSET: PyBorderStyleType = PyBorderStyleType { inner: BorderStyleType::Inset };
    #[classattr]
    const UNDERLINE: PyBorderStyleType = PyBorderStyleType { inner: BorderStyleType::Underline };

    fn __repr__(&self) -> String {
        format!("BorderStyleType.{}", self.inner.pdf_name())
    }
}

// ── BorderStyle ───────────────────────────────────────────────────────────

#[pyclass(name = "BorderStyle", from_py_object)]
#[derive(Clone)]
pub struct PyBorderStyle {
    pub inner: BorderStyle,
}

#[pymethods]
impl PyBorderStyle {
    #[new]
    #[pyo3(signature = (width=1.0, style=None))]
    fn new(width: f64, style: Option<&PyBorderStyleType>) -> Self {
        let bs = BorderStyle {
            width,
            style: style.map(|s| s.inner.clone()).unwrap_or(BorderStyleType::Solid),
            dash_pattern: None,
        };
        Self { inner: bs }
    }

    fn __repr__(&self) -> String {
        format!("BorderStyle(width={}, style={})", self.inner.width, self.inner.style.pdf_name())
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyAnnotationType>()?;
    m.add_class::<PyAnnotation>()?;
    m.add_class::<PyMarkupType>()?;
    m.add_class::<PyMarkupAnnotation>()?;
    m.add_class::<PyAnnotationIcon>()?;
    m.add_class::<PyTextAnnotation>()?;
    m.add_class::<PyBorderStyleType>()?;
    m.add_class::<PyBorderStyle>()?;
    Ok(())
}
