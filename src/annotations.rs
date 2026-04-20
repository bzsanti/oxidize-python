use pyo3::prelude::*;

use oxidize_pdf::annotations::{
    Annotation, AnnotationType, BorderStyle, BorderStyleType, CircleAnnotation,
    FileAttachmentAnnotation, FileAttachmentIcon, FreeTextAnnotation, HighlightAnnotation,
    HighlightMode, Icon, InkAnnotation, LineAnnotation, LineEndingStyle, LinkAction,
    LinkAnnotation, MarkupAnnotation, MarkupType, PolygonAnnotation, PolylineAnnotation,
    PopupAnnotation, PopupFlags, QuadPoints, SquareAnnotation, StampAnnotation, StampName,
    TextAnnotation,
};

use crate::types::{PyColor, PyPoint, PyRectangle};

/// Helper: set `annotation.contents` on a core annotation struct.
/// Used by specific annotation types whose core struct does not expose
/// a `with_contents()` builder method.
/// TODO: Remove when oxidize-pdf core adds `with_contents()` to specific annotation types.
fn set_annotation_contents(annotation: &mut Annotation, contents: &str) {
    annotation.contents = Some(contents.to_string());
}

// ── AnnotationType ────────────────────────────────────────────────────────

/// Enumeration of PDF annotation types (Text, Link, FreeText, Line, etc.).
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

    fn __eq__(&self, other: &Self) -> bool {
        self.inner.pdf_name() == other.inner.pdf_name()
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut h = std::collections::hash_map::DefaultHasher::new();
        self.inner.pdf_name().hash(&mut h);
        h.finish()
    }
}

// ── Annotation ────────────────────────────────────────────────────────────

/// Generic PDF annotation wrapper.
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
            inner: Annotation::new(annotation_type.inner, rect.inner),
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

/// Text markup annotation type (Highlight, Underline, StrikeOut, Squiggly).
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

    fn __eq__(&self, other: &Self) -> bool {
        self.__repr__() == other.__repr__()
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut h = std::collections::hash_map::DefaultHasher::new();
        self.__repr__().hash(&mut h);
        h.finish()
    }
}

// ── MarkupAnnotation ──────────────────────────────────────────────────────

/// Text markup annotation (highlight, underline, strikeout, squiggly).
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
        let type_name = match self.inner.markup_type {
            MarkupType::Highlight => "Highlight",
            MarkupType::Underline => "Underline",
            MarkupType::StrikeOut => "StrikeOut",
            MarkupType::Squiggly => "Squiggly",
        };
        format!("MarkupAnnotation(type={type_name})")
    }
}

// ── AnnotationIcon ────────────────────────────────────────────────────────

/// Icon types for text annotations.
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

    fn __eq__(&self, other: &Self) -> bool {
        self.__repr__() == other.__repr__()
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut h = std::collections::hash_map::DefaultHasher::new();
        self.__repr__().hash(&mut h);
        h.finish()
    }
}

// ── TextAnnotation ────────────────────────────────────────────────────────

/// Text (sticky note) annotation at a specific position.
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
        let r = &self.inner.annotation.rect;
        format!("TextAnnotation(pos=({}, {}))", r.lower_left.x, r.lower_left.y)
    }
}

// ── BorderStyleType ───────────────────────────────────────────────────────

/// Border style types for annotations.
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

    fn __eq__(&self, other: &Self) -> bool {
        self.__repr__() == other.__repr__()
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut h = std::collections::hash_map::DefaultHasher::new();
        self.__repr__().hash(&mut h);
        h.finish()
    }
}

// ── BorderStyle ───────────────────────────────────────────────────────────

/// Border style configuration for annotations.
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
            style: style.map(|s| s.inner).unwrap_or(BorderStyleType::Solid),
            dash_pattern: None,
        };
        Self { inner: bs }
    }

    fn __repr__(&self) -> String {
        format!("BorderStyle(width={}, style={})", self.inner.width, self.inner.style.pdf_name())
    }
}

// ── LineEndingStyle ───────────────────────────────────────────────────────

/// Line ending styles for line and polyline annotations.
#[pyclass(name = "LineEndingStyle", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyLineEndingStyle {
    pub inner: LineEndingStyle,
}

#[pymethods]
impl PyLineEndingStyle {
    #[classattr]
    const NONE: PyLineEndingStyle = PyLineEndingStyle {
        inner: LineEndingStyle::None,
    };
    #[classattr]
    const SQUARE: PyLineEndingStyle = PyLineEndingStyle {
        inner: LineEndingStyle::Square,
    };
    #[classattr]
    const CIRCLE: PyLineEndingStyle = PyLineEndingStyle {
        inner: LineEndingStyle::Circle,
    };
    #[classattr]
    const DIAMOND: PyLineEndingStyle = PyLineEndingStyle {
        inner: LineEndingStyle::Diamond,
    };
    #[classattr]
    const OPEN_ARROW: PyLineEndingStyle = PyLineEndingStyle {
        inner: LineEndingStyle::OpenArrow,
    };
    #[classattr]
    const CLOSED_ARROW: PyLineEndingStyle = PyLineEndingStyle {
        inner: LineEndingStyle::ClosedArrow,
    };
    #[classattr]
    const BUTT: PyLineEndingStyle = PyLineEndingStyle {
        inner: LineEndingStyle::Butt,
    };
    #[classattr]
    const R_OPEN_ARROW: PyLineEndingStyle = PyLineEndingStyle {
        inner: LineEndingStyle::ROpenArrow,
    };
    #[classattr]
    const R_CLOSED_ARROW: PyLineEndingStyle = PyLineEndingStyle {
        inner: LineEndingStyle::RClosedArrow,
    };
    #[classattr]
    const SLASH: PyLineEndingStyle = PyLineEndingStyle {
        inner: LineEndingStyle::Slash,
    };

    fn __repr__(&self) -> String {
        format!("LineEndingStyle.{}", self.inner.pdf_name())
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.__repr__() == other.__repr__()
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut h = std::collections::hash_map::DefaultHasher::new();
        self.__repr__().hash(&mut h);
        h.finish()
    }
}

// ── BorderEffectStyle ────────────────────────────────────────────────────

/// Border effect style for geometric annotations.
///
/// Standalone type — the core defines `BorderEffectStyle` in `annotation_type.rs`
/// but does NOT re-export it from `annotations::mod.rs` (v2.3.2). When the core
/// adds the re-export, this should be replaced with a wrapper around the core type.
#[pyclass(name = "BorderEffectStyle", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyBorderEffectStyle {
    pub is_cloudy: bool,
}

#[pymethods]
impl PyBorderEffectStyle {
    #[classattr]
    const SOLID: PyBorderEffectStyle = PyBorderEffectStyle { is_cloudy: false };
    #[classattr]
    const CLOUDY: PyBorderEffectStyle = PyBorderEffectStyle { is_cloudy: true };

    fn __repr__(&self) -> String {
        let name = if self.is_cloudy { "CLOUDY" } else { "SOLID" };
        format!("BorderEffectStyle.{name}")
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.is_cloudy == other.is_cloudy
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut h = std::collections::hash_map::DefaultHasher::new();
        self.is_cloudy.hash(&mut h);
        h.finish()
    }
}

// ── BorderEffect ─────────────────────────────────────────────────────────

/// Border effect for geometric annotations (circle, square).
///
/// Standalone type — the core defines `BorderEffect` in `annotation_type.rs`
/// but does NOT re-export it from `annotations::mod.rs` (v2.3.2). When the core
/// adds the re-export, this should be replaced with a wrapper.
///
/// Use `CircleAnnotation.with_cloudy_border(intensity)` or
/// `SquareAnnotation.with_cloudy_border(intensity)` to apply effects directly.
#[pyclass(name = "BorderEffect", frozen, skip_from_py_object)]
#[derive(Clone)]
pub struct PyBorderEffect {
    pub is_cloudy: bool,
    pub intensity: f64,
}

#[pymethods]
impl PyBorderEffect {
    #[new]
    #[pyo3(signature = (style=None, intensity=1.0))]
    fn new(style: Option<&PyBorderEffectStyle>, intensity: f64) -> Self {
        Self {
            is_cloudy: style.map(|s| s.is_cloudy).unwrap_or(false),
            intensity,
        }
    }

    #[getter]
    fn is_cloudy(&self) -> bool {
        self.is_cloudy
    }

    #[getter]
    fn intensity(&self) -> f64 {
        self.intensity
    }

    fn __repr__(&self) -> String {
        let style = if self.is_cloudy { "CLOUDY" } else { "SOLID" };
        format!("BorderEffect(style={}, intensity={})", style, self.intensity)
    }
}

// ── CircleAnnotation ─────────────────────────────────────────────────────

/// Circle annotation with optional interior color and border effect.
#[pyclass(name = "CircleAnnotation", skip_from_py_object)]
#[derive(Clone)]
pub struct PyCircleAnnotation {
    inner: CircleAnnotation,
}

#[pymethods]
impl PyCircleAnnotation {
    #[new]
    fn new(rect: &PyRectangle) -> Self {
        Self {
            inner: CircleAnnotation::new(rect.inner),
        }
    }

    /// Set interior (fill) color.
    fn with_interior_color(self_: PyRef<'_, Self>, color: &PyColor) -> Self {
        Self {
            inner: self_.inner.clone().with_interior_color(color.inner),
        }
    }

    /// Set cloudy border effect with given intensity (0.0-2.0).
    fn with_cloudy_border(self_: PyRef<'_, Self>, intensity: f64) -> Self {
        Self {
            inner: self_.inner.clone().with_cloudy_border(intensity),
        }
    }

    /// Set annotation contents text.
    fn with_contents(self_: PyRef<'_, Self>, contents: &str) -> Self {
        let mut inner = self_.inner.clone();
        set_annotation_contents(&mut inner.annotation, contents);
        Self { inner }
    }

    /// Convert to a generic Annotation for adding to a page.
    fn to_annotation(self_: PyRef<'_, Self>) -> PyAnnotation {
        PyAnnotation {
            inner: self_.inner.clone().to_annotation(),
        }
    }

    fn __repr__(&self) -> String {
        let r = &self.inner.annotation.rect;
        format!(
            "CircleAnnotation(rect=({}, {}, {}, {}))",
            r.lower_left.x, r.lower_left.y, r.upper_right.x, r.upper_right.y
        )
    }
}

// ── SquareAnnotation ─────────────────────────────────────────────────────

/// Square annotation with optional interior color and border effect.
#[pyclass(name = "SquareAnnotation", skip_from_py_object)]
#[derive(Clone)]
pub struct PySquareAnnotation {
    inner: SquareAnnotation,
}

#[pymethods]
impl PySquareAnnotation {
    #[new]
    fn new(rect: &PyRectangle) -> Self {
        Self {
            inner: SquareAnnotation::new(rect.inner),
        }
    }

    /// Set interior (fill) color.
    fn with_interior_color(self_: PyRef<'_, Self>, color: &PyColor) -> Self {
        Self {
            inner: self_.inner.clone().with_interior_color(color.inner),
        }
    }

    /// Set cloudy border effect with given intensity (0.0-2.0).
    fn with_cloudy_border(self_: PyRef<'_, Self>, intensity: f64) -> Self {
        Self {
            inner: self_.inner.clone().with_cloudy_border(intensity),
        }
    }

    /// Set annotation contents text.
    fn with_contents(self_: PyRef<'_, Self>, contents: &str) -> Self {
        let mut inner = self_.inner.clone();
        set_annotation_contents(&mut inner.annotation, contents);
        Self { inner }
    }

    /// Convert to a generic Annotation for adding to a page.
    fn to_annotation(self_: PyRef<'_, Self>) -> PyAnnotation {
        PyAnnotation {
            inner: self_.inner.clone().to_annotation(),
        }
    }

    fn __repr__(&self) -> String {
        let r = &self.inner.annotation.rect;
        format!(
            "SquareAnnotation(rect=({}, {}, {}, {}))",
            r.lower_left.x, r.lower_left.y, r.upper_right.x, r.upper_right.y
        )
    }
}

// ── LineAnnotation ───────────────────────────────────────────────────────

/// Line annotation with configurable endings and interior color.
#[pyclass(name = "LineAnnotation", skip_from_py_object)]
#[derive(Clone)]
pub struct PyLineAnnotation {
    inner: LineAnnotation,
}

#[pymethods]
impl PyLineAnnotation {
    #[new]
    fn new(start: &PyPoint, end: &PyPoint) -> Self {
        Self {
            inner: LineAnnotation::new(start.inner, end.inner),
        }
    }

    /// Set line ending styles for start and end.
    fn with_endings(
        self_: PyRef<'_, Self>,
        start: &PyLineEndingStyle,
        end: &PyLineEndingStyle,
    ) -> Self {
        Self {
            inner: self_.inner.clone().with_endings(start.inner, end.inner),
        }
    }

    /// Set interior color for line endings.
    fn with_interior_color(self_: PyRef<'_, Self>, color: &PyColor) -> Self {
        Self {
            inner: self_.inner.clone().with_interior_color(color.inner),
        }
    }

    /// Set annotation contents text.
    fn with_contents(self_: PyRef<'_, Self>, contents: &str) -> Self {
        let mut inner = self_.inner.clone();
        set_annotation_contents(&mut inner.annotation, contents);
        Self { inner }
    }

    /// Convert to a generic Annotation for adding to a page.
    fn to_annotation(self_: PyRef<'_, Self>) -> PyAnnotation {
        PyAnnotation {
            inner: self_.inner.clone().to_annotation(),
        }
    }

    fn __repr__(&self) -> String {
        let s = &self.inner.start;
        let e = &self.inner.end;
        format!(
            "LineAnnotation(start=({}, {}), end=({}, {}))",
            s.x, s.y, e.x, e.y
        )
    }
}

// ── StampName ─────────────────────────────────────────────────────────────

/// Standard stamp names for stamp annotations.
#[pyclass(name = "StampName", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyStampName {
    pub inner: StampName,
}

#[pymethods]
impl PyStampName {
    #[classattr]
    const APPROVED: PyStampName = PyStampName { inner: StampName::Approved };
    #[classattr]
    const EXPERIMENTAL: PyStampName = PyStampName { inner: StampName::Experimental };
    #[classattr]
    const NOT_APPROVED: PyStampName = PyStampName { inner: StampName::NotApproved };
    #[classattr]
    const AS_IS: PyStampName = PyStampName { inner: StampName::AsIs };
    #[classattr]
    const EXPIRED: PyStampName = PyStampName { inner: StampName::Expired };
    #[classattr]
    const NOT_FOR_PUBLIC_RELEASE: PyStampName = PyStampName { inner: StampName::NotForPublicRelease };
    #[classattr]
    const CONFIDENTIAL: PyStampName = PyStampName { inner: StampName::Confidential };
    #[classattr]
    const FINAL: PyStampName = PyStampName { inner: StampName::Final };
    #[classattr]
    const SOLD: PyStampName = PyStampName { inner: StampName::Sold };
    #[classattr]
    const DEPARTMENTAL: PyStampName = PyStampName { inner: StampName::Departmental };
    #[classattr]
    const FOR_COMMENT: PyStampName = PyStampName { inner: StampName::ForComment };
    #[classattr]
    const TOP_SECRET: PyStampName = PyStampName { inner: StampName::TopSecret };
    #[classattr]
    const DRAFT: PyStampName = PyStampName { inner: StampName::Draft };
    #[classattr]
    const FOR_PUBLIC_RELEASE: PyStampName = PyStampName { inner: StampName::ForPublicRelease };

    /// Create a custom stamp name.
    #[staticmethod]
    fn custom(name: &str) -> Self {
        Self {
            inner: StampName::Custom(name.to_string()),
        }
    }

    fn __repr__(&self) -> String {
        format!("StampName.{}", self.inner.pdf_name())
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.__repr__() == other.__repr__()
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut h = std::collections::hash_map::DefaultHasher::new();
        self.__repr__().hash(&mut h);
        h.finish()
    }
}

// ── StampAnnotation ──────────────────────────────────────────────────────

/// Stamp annotation with a predefined or custom stamp name.
#[pyclass(name = "StampAnnotation", skip_from_py_object)]
#[derive(Clone)]
pub struct PyStampAnnotation {
    inner: StampAnnotation,
}

#[pymethods]
impl PyStampAnnotation {
    #[new]
    fn new(rect: &PyRectangle, stamp_name: &PyStampName) -> Self {
        Self {
            inner: StampAnnotation::new(rect.inner, stamp_name.inner.clone()),
        }
    }

    /// Set annotation contents text.
    fn with_contents(self_: PyRef<'_, Self>, contents: &str) -> Self {
        let mut inner = self_.inner.clone();
        set_annotation_contents(&mut inner.annotation, contents);
        Self { inner }
    }

    /// Convert to a generic Annotation for adding to a page.
    fn to_annotation(self_: PyRef<'_, Self>) -> PyAnnotation {
        PyAnnotation {
            inner: self_.inner.clone().to_annotation(),
        }
    }

    fn __repr__(&self) -> String {
        format!("StampAnnotation(name={})", self.inner.stamp_name.pdf_name())
    }
}

// ── FileAttachmentIcon ───────────────────────────────────────────────────

/// Icon types for file attachment annotations.
#[pyclass(name = "FileAttachmentIcon", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyFileAttachmentIcon {
    pub inner: FileAttachmentIcon,
}

#[pymethods]
impl PyFileAttachmentIcon {
    #[classattr]
    const GRAPH: PyFileAttachmentIcon = PyFileAttachmentIcon { inner: FileAttachmentIcon::Graph };
    #[classattr]
    const PAPERCLIP: PyFileAttachmentIcon = PyFileAttachmentIcon { inner: FileAttachmentIcon::Paperclip };
    #[classattr]
    const PUSH_PIN: PyFileAttachmentIcon = PyFileAttachmentIcon { inner: FileAttachmentIcon::PushPin };
    #[classattr]
    const TAG: PyFileAttachmentIcon = PyFileAttachmentIcon { inner: FileAttachmentIcon::Tag };

    fn __repr__(&self) -> String {
        format!("FileAttachmentIcon.{}", self.inner.pdf_name())
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.__repr__() == other.__repr__()
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut h = std::collections::hash_map::DefaultHasher::new();
        self.__repr__().hash(&mut h);
        h.finish()
    }
}

// ── FileAttachmentAnnotation ─────────────────────────────────────────────

/// File attachment annotation that embeds a file in the PDF.
#[pyclass(name = "FileAttachmentAnnotation", skip_from_py_object)]
#[derive(Clone)]
pub struct PyFileAttachmentAnnotation {
    inner: FileAttachmentAnnotation,
}

#[pymethods]
impl PyFileAttachmentAnnotation {
    #[new]
    fn new(rect: &PyRectangle, file_name: &str, file_data: Vec<u8>) -> Self {
        Self {
            inner: FileAttachmentAnnotation::new(rect.inner, file_name.to_string(), file_data),
        }
    }

    /// Set MIME type for the attached file.
    fn with_mime_type(self_: PyRef<'_, Self>, mime_type: &str) -> Self {
        Self {
            inner: self_.inner.clone().with_mime_type(mime_type.to_string()),
        }
    }

    /// Set icon for the attachment.
    fn with_icon(self_: PyRef<'_, Self>, icon: &PyFileAttachmentIcon) -> Self {
        Self {
            inner: self_.inner.clone().with_icon(icon.inner.clone()),
        }
    }

    /// Convert to a generic Annotation for adding to a page.
    fn to_annotation(self_: PyRef<'_, Self>) -> PyAnnotation {
        PyAnnotation {
            inner: self_.inner.clone().to_annotation(),
        }
    }

    fn __repr__(&self) -> String {
        format!("FileAttachmentAnnotation(file={})", self.inner.file_name)
    }
}

// ── FreeTextAnnotation ───────────────────────────────────────────────────

/// Free text annotation that displays text directly on the page.
#[pyclass(name = "FreeTextAnnotation", skip_from_py_object)]
#[derive(Clone)]
pub struct PyFreeTextAnnotation {
    inner: FreeTextAnnotation,
}

#[pymethods]
impl PyFreeTextAnnotation {
    #[new]
    fn new(rect: &PyRectangle, text: &str) -> Self {
        Self {
            inner: FreeTextAnnotation::new(rect.inner, text),
        }
    }

    /// Set text justification. Valid values: 0 (left), 1 (center), 2 (right).
    ///
    /// Raises ``ValueError`` if quadding is not in the range 0–2.
    fn with_justification(self_: PyRef<'_, Self>, quadding: i32) -> PyResult<Self> {
        if !(0..=2).contains(&quadding) {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "justification must be 0, 1, or 2, got {quadding}"
            )));
        }
        Ok(Self {
            inner: self_.inner.clone().with_justification(quadding),
        })
    }

    /// Convert to a generic Annotation for adding to a page.
    fn to_annotation(self_: PyRef<'_, Self>) -> PyAnnotation {
        PyAnnotation {
            inner: self_.inner.clone().to_annotation(),
        }
    }

    fn __repr__(&self) -> String {
        let r = &self.inner.annotation.rect;
        format!(
            "FreeTextAnnotation(rect=({}, {}, {}, {}))",
            r.lower_left.x, r.lower_left.y, r.upper_right.x, r.upper_right.y
        )
    }
}

// ── InkAnnotation ────────────────────────────────────────────────────────

/// Ink annotation for freehand drawing (multiple strokes).
#[pyclass(name = "InkAnnotation", skip_from_py_object)]
#[derive(Clone)]
pub struct PyInkAnnotation {
    inner: InkAnnotation,
}

#[pymethods]
impl PyInkAnnotation {
    #[new]
    fn new() -> Self {
        Self {
            inner: InkAnnotation::new(),
        }
    }

    /// Add a stroke (list of Points) to the ink annotation.
    ///
    /// An empty list is accepted — it creates a zero-point stroke entry.
    /// The PDF spec does not forbid empty ink lists; behavior is viewer-dependent.
    fn add_stroke(self_: PyRef<'_, Self>, points: Vec<PyPoint>) -> Self {
        let rust_points = points.iter().map(|p| p.inner).collect();
        Self {
            inner: self_.inner.clone().add_stroke(rust_points),
        }
    }

    /// Convert to a generic Annotation for adding to a page.
    fn to_annotation(self_: PyRef<'_, Self>) -> PyAnnotation {
        PyAnnotation {
            inner: self_.inner.clone().to_annotation(),
        }
    }

    fn __repr__(&self) -> String {
        let total_points: usize = self.inner.ink_lists.iter().map(|s| s.len()).sum();
        format!(
            "InkAnnotation(strokes={}, points={})",
            self.inner.ink_lists.len(),
            total_points
        )
    }
}

// ── PolygonAnnotation ────────────────────────────────────────────────────

/// Polygon annotation — closed shape defined by vertices.
#[pyclass(name = "PolygonAnnotation", skip_from_py_object)]
#[derive(Clone)]
pub struct PyPolygonAnnotation {
    inner: PolygonAnnotation,
}

#[pymethods]
impl PyPolygonAnnotation {
    #[new]
    fn new(vertices: Vec<PyPoint>) -> PyResult<Self> {
        if vertices.len() < 3 {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "PolygonAnnotation requires at least 3 vertices, got {}",
                vertices.len()
            )));
        }
        let pts = vertices.iter().map(|p| p.inner).collect();
        Ok(Self {
            inner: PolygonAnnotation::new(pts),
        })
    }

    /// Set line (stroke) color.
    fn with_line_color(self_: PyRef<'_, Self>, color: &PyColor) -> Self {
        Self {
            inner: self_.inner.clone().with_line_color(Some(color.inner)),
        }
    }

    /// Set fill color.
    fn with_fill_color(self_: PyRef<'_, Self>, color: &PyColor) -> Self {
        Self {
            inner: self_.inner.clone().with_fill_color(Some(color.inner)),
        }
    }

    /// Set opacity. Values are clamped to [0.0, 1.0] by the core — no error
    /// is raised for out-of-range values.
    fn with_opacity(self_: PyRef<'_, Self>, opacity: f64) -> Self {
        Self {
            inner: self_.inner.clone().with_opacity(opacity),
        }
    }

    /// Set line width.
    fn with_line_width(self_: PyRef<'_, Self>, width: f64) -> Self {
        Self {
            inner: self_.inner.clone().with_line_width(width),
        }
    }

    /// Convert to a generic Annotation for adding to a page.
    ///
    /// May raise ``ValueError`` if the core serialization fails (e.g., invalid
    /// polygon state).
    fn to_annotation(self_: PyRef<'_, Self>) -> PyResult<PyAnnotation> {
        let ann = self_
            .inner
            .to_annotation()
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        Ok(PyAnnotation { inner: ann })
    }

    fn __repr__(&self) -> String {
        format!("PolygonAnnotation(vertices={})", self.inner.vertices.len())
    }
}

// ── PolylineAnnotation ───────────────────────────────────────────────────

/// Polyline annotation — open shape defined by vertices.
#[pyclass(name = "PolylineAnnotation", skip_from_py_object)]
#[derive(Clone)]
pub struct PyPolylineAnnotation {
    inner: PolylineAnnotation,
}

#[pymethods]
impl PyPolylineAnnotation {
    #[new]
    fn new(vertices: Vec<PyPoint>) -> PyResult<Self> {
        if vertices.len() < 2 {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "PolylineAnnotation requires at least 2 vertices, got {}",
                vertices.len()
            )));
        }
        let pts = vertices.iter().map(|p| p.inner).collect();
        Ok(Self {
            inner: PolylineAnnotation::new(pts),
        })
    }

    /// Set line (stroke) color.
    fn with_line_color(self_: PyRef<'_, Self>, color: &PyColor) -> Self {
        Self {
            inner: self_.inner.clone().with_line_color(Some(color.inner)),
        }
    }

    /// Set line width.
    fn with_line_width(self_: PyRef<'_, Self>, width: f64) -> Self {
        Self {
            inner: self_.inner.clone().with_line_width(width),
        }
    }

    /// Set opacity. Values are clamped to [0.0, 1.0] by the core — no error
    /// is raised for out-of-range values.
    fn with_opacity(self_: PyRef<'_, Self>, opacity: f64) -> Self {
        Self {
            inner: self_.inner.clone().with_opacity(opacity),
        }
    }

    /// Convert to a generic Annotation for adding to a page.
    ///
    /// May raise ``ValueError`` if the core serialization fails (e.g., invalid
    /// polyline state).
    fn to_annotation(self_: PyRef<'_, Self>) -> PyResult<PyAnnotation> {
        let ann = self_
            .inner
            .to_annotation()
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        Ok(PyAnnotation { inner: ann })
    }

    fn __repr__(&self) -> String {
        format!(
            "PolylineAnnotation(vertices={})",
            self.inner.vertices.len()
        )
    }
}

// ── QuadPoints ───────────────────────────────────────────────────────────

/// Quad points defining highlighted regions (8 floats per quadrilateral).
#[pyclass(name = "QuadPoints", from_py_object)]
#[derive(Clone)]
pub struct PyQuadPoints {
    pub inner: QuadPoints,
}

#[pymethods]
impl PyQuadPoints {
    #[new]
    fn new(points: Vec<f64>) -> PyResult<Self> {
        if points.is_empty() || points.len() % 8 != 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "QuadPoints requires a non-empty multiple of 8 floats (8 per quadrilateral), got {}",
                points.len()
            )));
        }
        Ok(Self {
            inner: QuadPoints { points },
        })
    }

    /// Create quad points from a rectangle.
    #[staticmethod]
    fn from_rect(rect: &PyRectangle) -> Self {
        Self {
            inner: QuadPoints::from_rect(&rect.inner),
        }
    }

    fn __repr__(&self) -> String {
        format!("QuadPoints(len={})", self.inner.points.len())
    }
}

// ── HighlightAnnotation ──────────────────────────────────────────────────

/// Highlight annotation using quad points.
#[pyclass(name = "HighlightAnnotation", skip_from_py_object)]
#[derive(Clone)]
pub struct PyHighlightAnnotation {
    inner: HighlightAnnotation,
}

#[pymethods]
impl PyHighlightAnnotation {
    #[new]
    fn new(rect: &PyRectangle) -> Self {
        Self {
            inner: HighlightAnnotation::new(rect.inner),
        }
    }

    /// Create with explicit quad points.
    #[staticmethod]
    fn with_quad_points(rect: &PyRectangle, quad_points: &PyQuadPoints) -> Self {
        let mut ha = HighlightAnnotation::new(rect.inner);
        ha.quad_points = quad_points.inner.clone();
        Self { inner: ha }
    }

    /// Convert to a generic Annotation for adding to a page.
    fn to_annotation(self_: PyRef<'_, Self>) -> PyAnnotation {
        PyAnnotation {
            inner: self_.inner.clone().to_annotation(),
        }
    }

    fn __repr__(&self) -> String {
        let r = &self.inner.annotation.rect;
        format!(
            "HighlightAnnotation(rect=({}, {}, {}, {}))",
            r.lower_left.x, r.lower_left.y, r.upper_right.x, r.upper_right.y
        )
    }
}

// ── PopupFlags ───────────────────────────────────────────────────────────

/// Flags controlling popup annotation behavior.
#[pyclass(name = "PopupFlags", from_py_object)]
#[derive(Clone)]
pub struct PyPopupFlags {
    pub inner: PopupFlags,
}

#[pymethods]
impl PyPopupFlags {
    #[new]
    #[pyo3(signature = (no_rotate=false, no_zoom=false))]
    fn new(no_rotate: bool, no_zoom: bool) -> Self {
        Self {
            inner: PopupFlags {
                no_rotate,
                no_zoom,
            },
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "PopupFlags(no_rotate={}, no_zoom={})",
            self.inner.no_rotate, self.inner.no_zoom
        )
    }
}

// ── PopupAnnotation ──────────────────────────────────────────────────────

/// Popup annotation for displaying text in a popup window.
#[pyclass(name = "PopupAnnotation", skip_from_py_object)]
#[derive(Clone)]
pub struct PyPopupAnnotation {
    inner: PopupAnnotation,
}

#[pymethods]
impl PyPopupAnnotation {
    #[new]
    fn new(rect: &PyRectangle) -> Self {
        Self {
            inner: PopupAnnotation::new(rect.inner),
        }
    }

    /// Set whether popup is initially open.
    fn with_open(self_: PyRef<'_, Self>, open: bool) -> Self {
        Self {
            inner: self_.inner.clone().with_open(open),
        }
    }

    /// Set popup contents text.
    fn with_contents(self_: PyRef<'_, Self>, contents: &str) -> Self {
        Self {
            inner: self_.inner.clone().with_contents(contents),
        }
    }

    /// Set popup background color.
    fn with_color(self_: PyRef<'_, Self>, color: &PyColor) -> Self {
        Self {
            inner: self_.inner.clone().with_color(Some(color.inner)),
        }
    }

    /// Set popup behavior flags (no_rotate, no_zoom).
    fn with_flags(self_: PyRef<'_, Self>, flags: &PyPopupFlags) -> Self {
        Self {
            inner: self_.inner.clone().with_flags(flags.inner),
        }
    }

    /// Convert to a generic Annotation for adding to a page.
    ///
    /// May raise ``ValueError`` if the core serialization fails (e.g., invalid
    /// popup state).
    fn to_annotation(self_: PyRef<'_, Self>) -> PyResult<PyAnnotation> {
        let ann = self_
            .inner
            .to_annotation()
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        Ok(PyAnnotation { inner: ann })
    }

    fn __repr__(&self) -> String {
        let r = &self.inner.rect;
        format!(
            "PopupAnnotation(rect=({}, {}, {}, {}))",
            r.lower_left.x, r.lower_left.y, r.upper_right.x, r.upper_right.y
        )
    }
}

// ── HighlightMode ────────────────────────────────────────────────────────

/// Highlight mode for link annotations.
#[pyclass(name = "HighlightMode", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyHighlightMode {
    pub inner: HighlightMode,
}

#[pymethods]
impl PyHighlightMode {
    #[classattr]
    const NONE: PyHighlightMode = PyHighlightMode {
        inner: HighlightMode::None,
    };
    #[classattr]
    const INVERT: PyHighlightMode = PyHighlightMode {
        inner: HighlightMode::Invert,
    };
    #[classattr]
    const OUTLINE: PyHighlightMode = PyHighlightMode {
        inner: HighlightMode::Outline,
    };
    #[classattr]
    const PUSH: PyHighlightMode = PyHighlightMode {
        inner: HighlightMode::Push,
    };

    fn __repr__(&self) -> String {
        format!("HighlightMode.{}", self.inner.pdf_name())
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.__repr__() == other.__repr__()
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut h = std::collections::hash_map::DefaultHasher::new();
        self.__repr__().hash(&mut h);
        h.finish()
    }
}

// ── LinkAnnotation ───────────────────────────────────────────────────────

/// Link annotation with factory methods for common link types.
#[pyclass(name = "LinkAnnotation", skip_from_py_object)]
#[derive(Clone)]
pub struct PyLinkAnnotation {
    inner: LinkAnnotation,
}

#[pymethods]
impl PyLinkAnnotation {
    /// Create a link to a URI.
    #[staticmethod]
    fn to_uri(rect: &PyRectangle, uri: &str) -> Self {
        Self {
            inner: LinkAnnotation::to_uri(rect.inner, uri),
        }
    }

    /// Create a named action link (e.g., "NextPage", "PrevPage").
    #[staticmethod]
    fn named_action(rect: &PyRectangle, name: &str) -> Self {
        Self {
            inner: LinkAnnotation::new(
                rect.inner,
                LinkAction::Named {
                    name: name.to_string(),
                },
            ),
        }
    }

    /// Set highlight mode for the link.
    fn with_highlight_mode(self_: PyRef<'_, Self>, mode: &PyHighlightMode) -> Self {
        Self {
            inner: self_.inner.clone().with_highlight_mode(mode.inner),
        }
    }

    /// Convert to a generic Annotation for adding to a page.
    fn to_annotation(self_: PyRef<'_, Self>) -> PyAnnotation {
        PyAnnotation {
            inner: self_.inner.clone().to_annotation(),
        }
    }

    fn __repr__(&self) -> String {
        let r = &self.inner.annotation.rect;
        format!(
            "LinkAnnotation(rect=({}, {}, {}, {}))",
            r.lower_left.x, r.lower_left.y, r.upper_right.x, r.upper_right.y
        )
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
    m.add_class::<PyLineEndingStyle>()?;
    m.add_class::<PyBorderEffectStyle>()?;
    m.add_class::<PyBorderEffect>()?;
    m.add_class::<PyCircleAnnotation>()?;
    m.add_class::<PySquareAnnotation>()?;
    m.add_class::<PyLineAnnotation>()?;
    m.add_class::<PyStampName>()?;
    m.add_class::<PyStampAnnotation>()?;
    m.add_class::<PyFileAttachmentIcon>()?;
    m.add_class::<PyFileAttachmentAnnotation>()?;
    m.add_class::<PyFreeTextAnnotation>()?;
    m.add_class::<PyInkAnnotation>()?;
    m.add_class::<PyPolygonAnnotation>()?;
    m.add_class::<PyPolylineAnnotation>()?;
    m.add_class::<PyQuadPoints>()?;
    m.add_class::<PyHighlightAnnotation>()?;
    m.add_class::<PyPopupFlags>()?;
    m.add_class::<PyPopupAnnotation>()?;
    m.add_class::<PyHighlightMode>()?;
    m.add_class::<PyLinkAnnotation>()?;
    Ok(())
}
