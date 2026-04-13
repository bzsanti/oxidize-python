use pyo3::prelude::*;

use oxidize_pdf::layout::{
    centered_image_x, fit_image_dimensions, FlowLayout, PageConfig, RichText, TextSpan,
};
use oxidize_pdf::text::text_block::{measure_text_block, TextBlockMetrics};

use crate::document::PyDocument;
use crate::errors::to_py_err;
use crate::table::PyTable;
use crate::text::PyFont;
use crate::types::PyColor;

// ── PageConfig ────────────────────────────────────────────────────────────

#[pyclass(name = "PageConfig", from_py_object)]
#[derive(Clone)]
pub struct PyPageConfig {
    pub inner: PageConfig,
}

#[pymethods]
impl PyPageConfig {
    #[new]
    fn new(
        width: f64,
        height: f64,
        margin_left: f64,
        margin_right: f64,
        margin_top: f64,
        margin_bottom: f64,
    ) -> Self {
        Self {
            inner: PageConfig::new(width, height, margin_left, margin_right, margin_top, margin_bottom),
        }
    }

    #[staticmethod]
    fn a4() -> Self {
        Self {
            inner: PageConfig::a4(),
        }
    }

    #[staticmethod]
    fn a4_with_margins(left: f64, right: f64, top: f64, bottom: f64) -> Self {
        Self {
            inner: PageConfig::a4_with_margins(left, right, top, bottom),
        }
    }

    #[getter]
    fn width(&self) -> f64 {
        self.inner.width
    }

    #[getter]
    fn height(&self) -> f64 {
        self.inner.height
    }

    #[getter]
    fn margin_left(&self) -> f64 {
        self.inner.margin_left
    }

    #[getter]
    fn margin_right(&self) -> f64 {
        self.inner.margin_right
    }

    #[getter]
    fn margin_top(&self) -> f64 {
        self.inner.margin_top
    }

    #[getter]
    fn margin_bottom(&self) -> f64 {
        self.inner.margin_bottom
    }

    fn content_width(&self) -> f64 {
        self.inner.content_width()
    }

    fn usable_height(&self) -> f64 {
        self.inner.usable_height()
    }

    fn __repr__(&self) -> String {
        format!(
            "PageConfig({}×{}, margins=[{},{},{},{}])",
            self.inner.width,
            self.inner.height,
            self.inner.margin_left,
            self.inner.margin_right,
            self.inner.margin_top,
            self.inner.margin_bottom,
        )
    }
}

// ── TextBlockMetrics ──────────────────────────────────────────────────────

#[pyclass(name = "TextBlockMetrics", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTextBlockMetrics {
    pub inner: TextBlockMetrics,
}

#[pymethods]
impl PyTextBlockMetrics {
    #[getter]
    fn width(&self) -> f64 {
        self.inner.width
    }

    #[getter]
    fn height(&self) -> f64 {
        self.inner.height
    }

    #[getter]
    fn line_count(&self) -> usize {
        self.inner.line_count
    }

    fn __repr__(&self) -> String {
        format!(
            "TextBlockMetrics(width={:.2}, height={:.2}, line_count={})",
            self.inner.width, self.inner.height, self.inner.line_count,
        )
    }
}

// ── TextSpan ──────────────────────────────────────────────────────────────

#[pyclass(name = "TextSpan", from_py_object)]
#[derive(Clone)]
pub struct PyTextSpan {
    pub inner: TextSpan,
}

#[pymethods]
impl PyTextSpan {
    #[new]
    fn new(text: &str, font: &PyFont, font_size: f64, color: &PyColor) -> Self {
        Self {
            inner: TextSpan::new(text, font.inner.clone(), font_size, color.inner),
        }
    }

    fn measure_width(&self) -> f64 {
        self.inner.measure_width()
    }

    fn __repr__(&self) -> String {
        format!(
            "TextSpan(\"{}\", font_size={:.1})",
            self.inner.text, self.inner.font_size,
        )
    }
}

// ── RichText ──────────────────────────────────────────────────────────────

#[pyclass(name = "RichText")]
pub struct PyRichText {
    pub inner: RichText,
}

#[pymethods]
impl PyRichText {
    #[new]
    fn new(spans: Vec<PyTextSpan>) -> Self {
        let rust_spans = spans.into_iter().map(|s| s.inner).collect();
        Self {
            inner: RichText::new(rust_spans),
        }
    }

    fn total_width(&self) -> f64 {
        self.inner.total_width()
    }

    fn max_font_size(&self) -> f64 {
        self.inner.max_font_size()
    }

    fn __repr__(&self) -> String {
        format!("RichText(spans={})", self.inner.spans().len())
    }
}

// ── Free functions ────────────────────────────────────────────────────────

#[pyfunction]
#[pyo3(name = "fit_image_dimensions")]
fn py_fit_image_dimensions(
    img_width: u32,
    img_height: u32,
    max_width: f64,
    max_height: f64,
) -> (f64, f64) {
    fit_image_dimensions(img_width, img_height, max_width, max_height)
}

#[pyfunction]
#[pyo3(name = "centered_image_x")]
fn py_centered_image_x(margin_left: f64, content_width: f64, image_width: f64) -> f64 {
    centered_image_x(margin_left, content_width, image_width)
}

#[pyfunction]
#[pyo3(name = "measure_text_block")]
fn py_measure_text_block(
    text: &str,
    font: &PyFont,
    font_size: f64,
    line_height: f64,
    max_width: f64,
) -> PyTextBlockMetrics {
    PyTextBlockMetrics {
        inner: measure_text_block(text, &font.inner, font_size, line_height, max_width),
    }
}

// ── FlowLayout ───────────────────────────────────────────────────────────

#[pyclass(name = "FlowLayout")]
pub struct PyFlowLayout {
    inner: FlowLayout,
}

#[pymethods]
impl PyFlowLayout {
    #[new]
    fn new(config: &PyPageConfig) -> Self {
        Self {
            inner: FlowLayout::new(config.inner.clone()),
        }
    }

    fn add_text(&mut self, text: &str, font: &PyFont, font_size: f64) {
        self.inner.add_text(text, font.inner.clone(), font_size);
    }

    fn add_text_with_line_height(
        &mut self,
        text: &str,
        font: &PyFont,
        font_size: f64,
        line_height: f64,
    ) {
        self.inner
            .add_text_with_line_height(text, font.inner.clone(), font_size, line_height);
    }

    fn add_spacer(&mut self, points: f64) {
        self.inner.add_spacer(points);
    }

    fn add_table(&mut self, table: &PyTable) {
        self.inner.add_table(table.inner.clone());
    }

    fn add_rich_text(&mut self, rich: &PyRichText) {
        let spans: Vec<TextSpan> = rich.inner.spans().to_vec();
        self.inner.add_rich_text(RichText::new(spans));
    }

    fn build_into(&self, doc: &mut PyDocument) -> PyResult<()> {
        self.inner.build_into(&mut doc.inner).map_err(to_py_err)
    }
}

// ── Module registration ───────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPageConfig>()?;
    m.add_class::<PyTextBlockMetrics>()?;
    m.add_class::<PyTextSpan>()?;
    m.add_class::<PyRichText>()?;
    m.add_class::<PyFlowLayout>()?;
    m.add_function(wrap_pyfunction!(py_fit_image_dimensions, m)?)?;
    m.add_function(wrap_pyfunction!(py_centered_image_x, m)?)?;
    m.add_function(wrap_pyfunction!(py_measure_text_block, m)?)?;
    Ok(())
}
