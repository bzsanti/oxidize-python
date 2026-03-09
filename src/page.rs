use pyo3::prelude::*;

use crate::errors::to_py_err;
use crate::text::PyFont;
use crate::types::{PyColor, PyMargins};

#[pyclass(name = "Page", from_py_object)]
#[derive(Clone)]
pub struct PyPage {
    pub inner: oxidize_pdf::Page,
}

#[pymethods]
impl PyPage {
    #[new]
    fn new(width: f64, height: f64) -> Self {
        Self {
            inner: oxidize_pdf::Page::new(width, height),
        }
    }

    #[staticmethod]
    fn a4() -> Self {
        Self {
            inner: oxidize_pdf::Page::a4(),
        }
    }

    #[staticmethod]
    fn a4_landscape() -> Self {
        Self {
            inner: oxidize_pdf::Page::a4_landscape(),
        }
    }

    #[staticmethod]
    fn letter() -> Self {
        Self {
            inner: oxidize_pdf::Page::letter(),
        }
    }

    #[staticmethod]
    fn letter_landscape() -> Self {
        Self {
            inner: oxidize_pdf::Page::letter_landscape(),
        }
    }

    #[staticmethod]
    fn legal() -> Self {
        Self {
            inner: oxidize_pdf::Page::legal(),
        }
    }

    #[staticmethod]
    fn legal_landscape() -> Self {
        Self {
            inner: oxidize_pdf::Page::legal_landscape(),
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
    fn margins(&self) -> PyMargins {
        PyMargins {
            inner: self.inner.margins().clone(),
        }
    }

    fn set_margins(&mut self, margins: &PyMargins) {
        self.inner.set_margins(
            margins.inner.left,
            margins.inner.right,
            margins.inner.top,
            margins.inner.bottom,
        );
    }

    fn __repr__(&self) -> String {
        format!("Page({}x{})", self.inner.width(), self.inner.height())
    }

    // ── Text operations ────────────────────────────────────────────────

    /// Set the current font and size for subsequent text operations.
    fn set_font(&mut self, font: &PyFont, size: f64) {
        self.inner.text().set_font(font.inner.clone(), size);
    }

    /// Set the text fill color for subsequent text operations.
    fn set_text_color(&mut self, color: &PyColor) {
        self.inner.text().set_fill_color(color.inner);
    }

    /// Set character spacing for subsequent text operations.
    fn set_character_spacing(&mut self, spacing: f64) {
        self.inner.text().set_character_spacing(spacing);
    }

    /// Set word spacing for subsequent text operations.
    fn set_word_spacing(&mut self, spacing: f64) {
        self.inner.text().set_word_spacing(spacing);
    }

    /// Set text leading (line spacing) for subsequent text operations.
    fn set_leading(&mut self, leading: f64) {
        self.inner.text().set_leading(leading);
    }

    /// Write text at the given position.
    fn text_at(&mut self, x: f64, y: f64, text: &str) -> PyResult<()> {
        self.inner
            .text()
            .at(x, y)
            .write(text)
            .map_err(to_py_err)?;
        Ok(())
    }

    // ── Graphics operations ────────────────────────────────────────────

    /// Set the fill color for subsequent graphics operations.
    fn set_fill_color(&mut self, color: &PyColor) {
        self.inner.graphics().set_fill_color(color.inner);
    }

    /// Set the stroke color for subsequent graphics operations.
    fn set_stroke_color(&mut self, color: &PyColor) {
        self.inner.graphics().set_stroke_color(color.inner);
    }

    /// Set the line width for subsequent stroke operations.
    fn set_line_width(&mut self, width: f64) {
        self.inner.graphics().set_line_width(width);
    }

    /// Set fill opacity (0.0 = transparent, 1.0 = opaque).
    fn set_fill_opacity(&mut self, opacity: f64) {
        self.inner.graphics().set_fill_opacity(opacity);
    }

    /// Set stroke opacity (0.0 = transparent, 1.0 = opaque).
    fn set_stroke_opacity(&mut self, opacity: f64) {
        self.inner.graphics().set_stroke_opacity(opacity);
    }

    /// Draw a rectangle path (does not fill or stroke — call fill/stroke after).
    fn draw_rect(&mut self, x: f64, y: f64, width: f64, height: f64) {
        self.inner.graphics().rect(x, y, width, height);
    }

    /// Draw a circle path.
    fn draw_circle(&mut self, cx: f64, cy: f64, radius: f64) {
        self.inner.graphics().circle(cx, cy, radius);
    }

    /// Move the current point to (x, y) without drawing.
    fn move_to(&mut self, x: f64, y: f64) {
        self.inner.graphics().move_to(x, y);
    }

    /// Draw a line from the current point to (x, y).
    fn line_to(&mut self, x: f64, y: f64) {
        self.inner.graphics().line_to(x, y);
    }

    /// Draw a cubic Bézier curve from the current point.
    fn curve_to(&mut self, x1: f64, y1: f64, x2: f64, y2: f64, x3: f64, y3: f64) {
        self.inner.graphics().curve_to(x1, y1, x2, y2, x3, y3);
    }

    /// Close the current path by drawing a line back to the starting point.
    fn close_path(&mut self) {
        self.inner.graphics().close_path();
    }

    /// Fill the current path.
    fn fill(&mut self) {
        self.inner.graphics().fill();
    }

    /// Stroke the current path.
    fn stroke(&mut self) {
        self.inner.graphics().stroke();
    }

    /// Fill and then stroke the current path.
    fn fill_and_stroke(&mut self) {
        self.inner.graphics().fill_stroke();
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPage>()?;
    Ok(())
}
