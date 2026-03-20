//! Page transitions bindings — Feature 60
//!
//! Wraps `oxidize_pdf::page_transitions` for Python: transition styles,
//! dimension, motion, direction enums, and PageTransition struct.

use pyo3::prelude::*;

use oxidize_pdf::page_transitions::{
    PageTransition, TransitionDimension, TransitionDirection, TransitionMotion, TransitionStyle,
};

// ── TransitionStyle ────────────────────────────────────────────────────────

#[pyclass(name = "TransitionStyle", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTransitionStyle {
    pub inner: TransitionStyle,
}

#[pymethods]
impl PyTransitionStyle {
    #[classattr]
    const SPLIT: Self = Self { inner: TransitionStyle::Split };
    #[classattr]
    const BLINDS: Self = Self { inner: TransitionStyle::Blinds };
    #[classattr]
    const BOX: Self = Self { inner: TransitionStyle::Box };
    #[classattr]
    const WIPE: Self = Self { inner: TransitionStyle::Wipe };
    #[classattr]
    const DISSOLVE: Self = Self { inner: TransitionStyle::Dissolve };
    #[classattr]
    const GLITTER: Self = Self { inner: TransitionStyle::Glitter };
    #[classattr]
    const REPLACE: Self = Self { inner: TransitionStyle::Replace };
    #[classattr]
    const FLY: Self = Self { inner: TransitionStyle::Fly };
    #[classattr]
    const PUSH: Self = Self { inner: TransitionStyle::Push };
    #[classattr]
    const COVER: Self = Self { inner: TransitionStyle::Cover };
    #[classattr]
    const UNCOVER: Self = Self { inner: TransitionStyle::Uncover };
    #[classattr]
    const FADE: Self = Self { inner: TransitionStyle::Fade };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            TransitionStyle::Split => "SPLIT",
            TransitionStyle::Blinds => "BLINDS",
            TransitionStyle::Box => "BOX",
            TransitionStyle::Wipe => "WIPE",
            TransitionStyle::Dissolve => "DISSOLVE",
            TransitionStyle::Glitter => "GLITTER",
            TransitionStyle::Replace => "REPLACE",
            TransitionStyle::Fly => "FLY",
            TransitionStyle::Push => "PUSH",
            TransitionStyle::Cover => "COVER",
            TransitionStyle::Uncover => "UNCOVER",
            TransitionStyle::Fade => "FADE",
        };
        format!("TransitionStyle.{}", name)
    }
}

// ── TransitionDimension ────────────────────────────────────────────────────

#[pyclass(name = "TransitionDimension", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTransitionDimension {
    pub inner: TransitionDimension,
}

#[pymethods]
impl PyTransitionDimension {
    #[classattr]
    const HORIZONTAL: Self = Self { inner: TransitionDimension::Horizontal };
    #[classattr]
    const VERTICAL: Self = Self { inner: TransitionDimension::Vertical };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            TransitionDimension::Horizontal => "HORIZONTAL",
            TransitionDimension::Vertical => "VERTICAL",
        };
        format!("TransitionDimension.{}", name)
    }
}

// ── TransitionMotion ───────────────────────────────────────────────────────

#[pyclass(name = "TransitionMotion", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTransitionMotion {
    pub inner: TransitionMotion,
}

#[pymethods]
impl PyTransitionMotion {
    #[classattr]
    const INWARD: Self = Self { inner: TransitionMotion::Inward };
    #[classattr]
    const OUTWARD: Self = Self { inner: TransitionMotion::Outward };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            TransitionMotion::Inward => "INWARD",
            TransitionMotion::Outward => "OUTWARD",
        };
        format!("TransitionMotion.{}", name)
    }
}

// ── TransitionDirection ────────────────────────────────────────────────────

#[pyclass(name = "TransitionDirection", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTransitionDirection {
    pub inner: TransitionDirection,
}

#[pymethods]
impl PyTransitionDirection {
    #[classattr]
    const LEFT_TO_RIGHT: Self = Self { inner: TransitionDirection::LeftToRight };
    #[classattr]
    const BOTTOM_TO_TOP: Self = Self { inner: TransitionDirection::BottomToTop };
    #[classattr]
    const RIGHT_TO_LEFT: Self = Self { inner: TransitionDirection::RightToLeft };
    #[classattr]
    const TOP_TO_BOTTOM: Self = Self { inner: TransitionDirection::TopToBottom };
    #[classattr]
    const TOP_LEFT_TO_BOTTOM_RIGHT: Self =
        Self { inner: TransitionDirection::TopLeftToBottomRight };

    #[staticmethod]
    fn custom(angle: u16) -> Self {
        Self { inner: TransitionDirection::Custom(angle) }
    }

    fn __repr__(&self) -> String {
        match self.inner {
            TransitionDirection::LeftToRight => "TransitionDirection.LEFT_TO_RIGHT".to_string(),
            TransitionDirection::BottomToTop => "TransitionDirection.BOTTOM_TO_TOP".to_string(),
            TransitionDirection::RightToLeft => "TransitionDirection.RIGHT_TO_LEFT".to_string(),
            TransitionDirection::TopToBottom => "TransitionDirection.TOP_TO_BOTTOM".to_string(),
            TransitionDirection::TopLeftToBottomRight => {
                "TransitionDirection.TOP_LEFT_TO_BOTTOM_RIGHT".to_string()
            }
            TransitionDirection::Custom(angle) => {
                format!("TransitionDirection.custom({})", angle)
            }
        }
    }
}

// ── PageTransition ─────────────────────────────────────────────────────────

#[pyclass(name = "PageTransition", from_py_object)]
#[derive(Clone)]
pub struct PyPageTransition {
    pub inner: PageTransition,
}

#[pymethods]
impl PyPageTransition {
    #[new]
    fn new(style: &PyTransitionStyle) -> Self {
        Self { inner: PageTransition::new(style.inner) }
    }

    fn with_duration(&self, duration: f32) -> Self {
        Self { inner: self.inner.clone().with_duration(duration) }
    }

    fn with_dimension(&self, dimension: &PyTransitionDimension) -> Self {
        Self { inner: self.inner.clone().with_dimension(dimension.inner) }
    }

    fn with_motion(&self, motion: &PyTransitionMotion) -> Self {
        Self { inner: self.inner.clone().with_motion(motion.inner) }
    }

    fn with_direction(&self, direction: &PyTransitionDirection) -> Self {
        Self { inner: self.inner.clone().with_direction(direction.inner) }
    }

    fn with_scale(&self, scale: f32) -> Self {
        Self { inner: self.inner.clone().with_scale(scale) }
    }

    fn with_area(&self, x: f32, y: f32, width: f32, height: f32) -> Self {
        Self { inner: self.inner.clone().with_area(x, y, width, height) }
    }

    // Convenience constructors

    #[staticmethod]
    fn split(dimension: &PyTransitionDimension, motion: &PyTransitionMotion) -> Self {
        Self { inner: PageTransition::split(dimension.inner, motion.inner) }
    }

    #[staticmethod]
    fn blinds(dimension: &PyTransitionDimension) -> Self {
        Self { inner: PageTransition::blinds(dimension.inner) }
    }

    #[staticmethod]
    fn box_transition(motion: &PyTransitionMotion) -> Self {
        Self { inner: PageTransition::box_transition(motion.inner) }
    }

    #[staticmethod]
    fn wipe(direction: &PyTransitionDirection) -> Self {
        Self { inner: PageTransition::wipe(direction.inner) }
    }

    #[staticmethod]
    fn dissolve() -> Self {
        Self { inner: PageTransition::dissolve() }
    }

    #[staticmethod]
    fn glitter(direction: &PyTransitionDirection) -> Self {
        Self { inner: PageTransition::glitter(direction.inner) }
    }

    #[staticmethod]
    fn replace() -> Self {
        Self { inner: PageTransition::replace() }
    }

    #[staticmethod]
    fn fly(direction: &PyTransitionDirection) -> Self {
        Self { inner: PageTransition::fly(direction.inner) }
    }

    #[staticmethod]
    fn push(direction: &PyTransitionDirection) -> Self {
        Self { inner: PageTransition::push(direction.inner) }
    }

    #[staticmethod]
    fn cover(direction: &PyTransitionDirection) -> Self {
        Self { inner: PageTransition::cover(direction.inner) }
    }

    #[staticmethod]
    fn uncover(direction: &PyTransitionDirection) -> Self {
        Self { inner: PageTransition::uncover(direction.inner) }
    }

    #[staticmethod]
    fn fade() -> Self {
        Self { inner: PageTransition::fade() }
    }

    fn __repr__(&self) -> String {
        let style_name = match self.inner.style {
            TransitionStyle::Split => "SPLIT",
            TransitionStyle::Blinds => "BLINDS",
            TransitionStyle::Box => "BOX",
            TransitionStyle::Wipe => "WIPE",
            TransitionStyle::Dissolve => "DISSOLVE",
            TransitionStyle::Glitter => "GLITTER",
            TransitionStyle::Replace => "REPLACE",
            TransitionStyle::Fly => "FLY",
            TransitionStyle::Push => "PUSH",
            TransitionStyle::Cover => "COVER",
            TransitionStyle::Uncover => "UNCOVER",
            TransitionStyle::Fade => "FADE",
        };
        format!("PageTransition(style=TransitionStyle.{})", style_name)
    }
}

// ── Registration ───────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTransitionStyle>()?;
    m.add_class::<PyTransitionDimension>()?;
    m.add_class::<PyTransitionMotion>()?;
    m.add_class::<PyTransitionDirection>()?;
    m.add_class::<PyPageTransition>()?;
    Ok(())
}
