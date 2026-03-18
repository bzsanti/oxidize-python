use pyo3::prelude::*;

use oxidize_pdf::PageLists;
use oxidize_pdf::PageTables;

use crate::annotations::PyAnnotation;
use crate::errors::to_py_err;
use crate::graphics::{PyBlendMode, PyClippingPath, PyLineCap, PyLineDashPattern, PyLineJoin};
use crate::image::PyImage;
use crate::list::{PyBulletStyle, PyOrderedList, PyOrderedListStyle, PyUnorderedList};
use crate::table::{PyTable, PyTableStyle};
use crate::text::{PyFont, PyHeaderFooter, PyTextAlign, PyTextRenderingMode};
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

    #[getter]
    fn rotation(&self) -> i32 {
        self.inner.get_rotation()
    }

    fn set_rotation(&mut self, degrees: i32) {
        self.inner.set_rotation(degrees);
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

    /// Set horizontal text scaling (100.0 = normal).
    fn set_horizontal_scaling(&mut self, scale: f64) {
        self.inner.text().set_horizontal_scaling(scale);
    }

    /// Set text rise (positive = superscript, negative = subscript).
    fn set_text_rise(&mut self, rise: f64) {
        self.inner.text().set_text_rise(rise);
    }

    /// Set the text rendering mode.
    fn set_rendering_mode(&mut self, mode: &PyTextRenderingMode) {
        self.inner.text().set_rendering_mode(mode.inner);
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

    /// Set the line cap style.
    fn set_line_cap(&mut self, cap: &PyLineCap) {
        self.inner.graphics().set_line_cap(cap.inner);
    }

    /// Set the line join style.
    fn set_line_join(&mut self, join: &PyLineJoin) {
        self.inner.graphics().set_line_join(join.inner);
    }

    /// Set the miter limit for line joins.
    fn set_miter_limit(&mut self, limit: f64) {
        self.inner.graphics().set_miter_limit(limit);
    }

    /// Set the line dash pattern.
    fn set_dash_pattern(&mut self, pattern: &PyLineDashPattern) {
        self.inner
            .graphics()
            .set_line_dash_pattern(pattern.inner.clone());
    }

    /// Save the current graphics state.
    fn save_graphics_state(&mut self) {
        self.inner.graphics().save_state();
    }

    /// Restore the previously saved graphics state.
    fn restore_graphics_state(&mut self) {
        self.inner.graphics().restore_state();
    }

    /// Set a clipping path.
    fn set_clipping_path(&mut self, path: &PyClippingPath) -> PyResult<()> {
        self.inner
            .graphics()
            .set_clipping_path(path.inner.clone())
            .map_err(to_py_err)?;
        Ok(())
    }

    /// Clear the clipping path.
    fn clear_clipping(&mut self) {
        self.inner.graphics().clear_clipping();
    }

    /// Set the blend mode.
    fn set_blend_mode(&mut self, mode: &PyBlendMode) -> PyResult<()> {
        self.inner
            .graphics()
            .set_blend_mode(mode.inner.clone())
            .map_err(to_py_err)?;
        Ok(())
    }

    // ── Coordinate system ─────────────────────────────────────────────

    /// Set the coordinate system for this page.
    fn set_coordinate_system(&mut self, cs: &crate::tier8::PyCoordinateSystem) {
        self.inner.set_coordinate_system(cs.inner.clone());
    }

    // ── Annotation operations ─────────────────────────────────────────

    /// Add an annotation to this page.
    fn add_annotation(&mut self, annotation: &PyAnnotation) {
        self.inner.add_annotation(annotation.inner.clone());
    }

    // ── Table operations ────────────────────────────────────────────────

    /// Render a table at the given position.
    fn add_simple_table(&mut self, table: &PyTable, x: f64, y: f64) -> PyResult<()> {
        self.inner
            .add_simple_table(&table.inner, x, y)
            .map_err(to_py_err)?;
        Ok(())
    }

    /// Create and render a quick table from raw data.
    #[pyo3(signature = (data, x, y, width, options=None))]
    fn add_quick_table(
        &mut self,
        data: Vec<Vec<String>>,
        x: f64,
        y: f64,
        width: f64,
        options: Option<&crate::table::PyTableOptions>,
    ) -> PyResult<()> {
        self.inner
            .add_quick_table(data, x, y, width, options.map(|o| o.inner.clone()))
            .map_err(to_py_err)?;
        Ok(())
    }

    /// Render a styled table with headers.
    fn add_styled_table(
        &mut self,
        headers: Vec<String>,
        data: Vec<Vec<String>>,
        x: f64,
        y: f64,
        width: f64,
        style: &PyTableStyle,
    ) -> PyResult<()> {
        self.inner
            .add_styled_table(headers, data, x, y, width, style.inner.clone())
            .map_err(to_py_err)?;
        Ok(())
    }

    // ── List operations ──────────────────────────────────────────────────

    /// Render an ordered list at the given position.
    fn add_ordered_list(&mut self, list: &PyOrderedList, x: f64, y: f64) -> PyResult<()> {
        self.inner
            .add_ordered_list(&list.inner, x, y)
            .map_err(to_py_err)?;
        Ok(())
    }

    /// Render an unordered list at the given position.
    fn add_unordered_list(&mut self, list: &PyUnorderedList, x: f64, y: f64) -> PyResult<()> {
        self.inner
            .add_unordered_list(&list.inner, x, y)
            .map_err(to_py_err)?;
        Ok(())
    }

    /// Quick ordered list from items.
    fn add_quick_ordered_list(
        &mut self,
        items: Vec<String>,
        x: f64,
        y: f64,
        style: &PyOrderedListStyle,
    ) -> PyResult<()> {
        self.inner
            .add_quick_ordered_list(items, x, y, style.inner)
            .map_err(to_py_err)?;
        Ok(())
    }

    /// Quick unordered list from items.
    fn add_quick_unordered_list(
        &mut self,
        items: Vec<String>,
        x: f64,
        y: f64,
        bullet: &PyBulletStyle,
    ) -> PyResult<()> {
        self.inner
            .add_quick_unordered_list(items, x, y, bullet.inner)
            .map_err(to_py_err)?;
        Ok(())
    }

    // ── Image operations ─────────────────────────────────────────────────

    /// Register a named image on this page.
    fn add_image(&mut self, name: &str, image: &PyImage) {
        self.inner.add_image(name, image.inner.clone());
    }

    /// Draw a previously registered image at the given position and size.
    fn draw_image(
        &mut self,
        name: &str,
        x: f64,
        y: f64,
        width: f64,
        height: f64,
    ) -> PyResult<()> {
        self.inner
            .draw_image(name, x, y, width, height)
            .map_err(to_py_err)
    }

    // ── Header/Footer operations ─────────────────────────────────────────

    /// Set a header on this page.
    fn set_header(&mut self, header: &PyHeaderFooter) {
        self.inner.set_header(header.inner.clone());
    }

    /// Set a footer on this page.
    fn set_footer(&mut self, footer: &PyHeaderFooter) {
        self.inner.set_footer(footer.inner.clone());
    }

    // ── Text flow (aligned / wrapped text) ──────────────────────────────

    /// Write text with word-wrapping and optional alignment.
    ///
    /// Uses the font previously set with ``set_font``. The text is wrapped
    /// within the page content area (respecting margins).
    ///
    /// Args:
    ///     x: Starting X position.
    ///     y: Starting Y position.
    ///     text: The text to write.
    ///     align: Optional ``TextAlign`` value (defaults to ``TextAlign.LEFT``).
    #[pyo3(signature = (x, y, text, align = None))]
    fn text_flow_at(
        &mut self,
        x: f64,
        y: f64,
        text: &str,
        align: Option<&PyTextAlign>,
    ) -> PyResult<()> {
        let mut ctx = self.inner.text_flow();

        ctx.at(x, y);

        if let Some(a) = align {
            ctx.set_alignment(a.inner);
        }

        ctx.write_wrapped(text).map_err(to_py_err)?;

        self.inner.add_text_flow(&ctx);
        Ok(())
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPage>()?;
    Ok(())
}
