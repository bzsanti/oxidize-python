//! Advanced Tables bindings — Feature 61
//!
//! Wraps `oxidize_pdf::advanced_tables` for Python: cell styling, complex headers,
//! table builder, and page integration.

use pyo3::prelude::*;

use oxidize_pdf::advanced_tables::{
    AdvancedTable, AdvancedTableBuilder, BorderStyle, CellAlignment, CellData, CellStyle, Column,
    HeaderBuilder, HeaderCell, Padding, RowData, TableRenderer, ZebraConfig,
};

use crate::errors::to_py_err;
use crate::text::PyFont;
use crate::types::PyColor;

// ── CellAlignment ─────────────────────────────────────────────────────────

#[pyclass(name = "CellAlignment", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyCellAlignment {
    pub inner: CellAlignment,
}

#[pymethods]
impl PyCellAlignment {
    #[classattr]
    const LEFT: Self = Self { inner: CellAlignment::Left };
    #[classattr]
    const CENTER: Self = Self { inner: CellAlignment::Center };
    #[classattr]
    const RIGHT: Self = Self { inner: CellAlignment::Right };
    #[classattr]
    const JUSTIFY: Self = Self { inner: CellAlignment::Justify };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            CellAlignment::Left => "LEFT",
            CellAlignment::Center => "CENTER",
            CellAlignment::Right => "RIGHT",
            CellAlignment::Justify => "JUSTIFY",
        };
        format!("CellAlignment.{}", name)
    }
}

// ── CellBorderStyle ───────────────────────────────────────────────────────

#[pyclass(name = "CellBorderStyle", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyCellBorderStyle {
    pub inner: BorderStyle,
}

#[pymethods]
impl PyCellBorderStyle {
    #[classattr]
    const NONE: Self = Self { inner: BorderStyle::None };
    #[classattr]
    const SOLID: Self = Self { inner: BorderStyle::Solid };
    #[classattr]
    const DASHED: Self = Self { inner: BorderStyle::Dashed };
    #[classattr]
    const DOTTED: Self = Self { inner: BorderStyle::Dotted };
    #[classattr]
    const DOUBLE: Self = Self { inner: BorderStyle::Double };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            BorderStyle::None => "NONE",
            BorderStyle::Solid => "SOLID",
            BorderStyle::Dashed => "DASHED",
            BorderStyle::Dotted => "DOTTED",
            BorderStyle::Double => "DOUBLE",
        };
        format!("CellBorderStyle.{}", name)
    }
}

// ── CellPadding ───────────────────────────────────────────────────────────

#[pyclass(name = "CellPadding", from_py_object)]
#[derive(Clone)]
pub struct PyCellPadding {
    pub inner: Padding,
}

#[pymethods]
impl PyCellPadding {
    #[new]
    fn new(top: f64, right: f64, bottom: f64, left: f64) -> Self {
        Self { inner: Padding::new(top, right, bottom, left) }
    }

    #[staticmethod]
    fn uniform(padding: f64) -> Self {
        Self { inner: Padding::uniform(padding) }
    }

    #[staticmethod]
    fn symmetric(horizontal: f64, vertical: f64) -> Self {
        Self { inner: Padding::symmetric(horizontal, vertical) }
    }

    #[getter]
    fn top(&self) -> f64 {
        self.inner.top
    }

    #[getter]
    fn right(&self) -> f64 {
        self.inner.right
    }

    #[getter]
    fn bottom(&self) -> f64 {
        self.inner.bottom
    }

    #[getter]
    fn left(&self) -> f64 {
        self.inner.left
    }

    fn __repr__(&self) -> String {
        format!(
            "CellPadding(top={}, right={}, bottom={}, left={})",
            self.inner.top, self.inner.right, self.inner.bottom, self.inner.left
        )
    }
}

// ── CellStyle ─────────────────────────────────────────────────────────────

#[pyclass(name = "CellStyle", from_py_object)]
#[derive(Clone)]
pub struct PyCellStyle {
    pub inner: CellStyle,
}

#[pymethods]
impl PyCellStyle {
    #[new]
    fn new() -> Self {
        Self { inner: CellStyle::new() }
    }

    #[staticmethod]
    fn header() -> Self {
        Self { inner: CellStyle::header() }
    }

    #[staticmethod]
    fn data() -> Self {
        Self { inner: CellStyle::data() }
    }

    #[staticmethod]
    fn numeric() -> Self {
        Self { inner: CellStyle::numeric() }
    }

    #[staticmethod]
    fn alternating() -> Self {
        Self { inner: CellStyle::alternating() }
    }

    fn background_color(&self, color: &PyColor) -> Self {
        Self { inner: self.inner.clone().background_color(color.inner) }
    }

    fn text_color(&self, color: &PyColor) -> Self {
        Self { inner: self.inner.clone().text_color(color.inner) }
    }

    fn font(&self, font: &PyFont) -> Self {
        Self { inner: self.inner.clone().font(font.inner.clone()) }
    }

    fn font_size(&self, size: f64) -> Self {
        Self { inner: self.inner.clone().font_size(size) }
    }

    fn padding(&self, padding: &PyCellPadding) -> Self {
        Self { inner: self.inner.clone().padding(padding.inner) }
    }

    fn alignment(&self, alignment: &PyCellAlignment) -> Self {
        Self { inner: self.inner.clone().alignment(alignment.inner) }
    }

    fn border(&self, style: &PyCellBorderStyle, width: f64, color: &PyColor) -> Self {
        Self { inner: self.inner.clone().border(style.inner, width, color.inner) }
    }

    fn text_wrap(&self, wrap: bool) -> Self {
        Self { inner: self.inner.clone().text_wrap(wrap) }
    }

    fn min_height(&self, height: f64) -> Self {
        Self { inner: self.inner.clone().min_height(height) }
    }

    fn max_height(&self, height: f64) -> Self {
        Self { inner: self.inner.clone().max_height(height) }
    }

    fn __repr__(&self) -> String {
        format!("CellStyle(font_size={:?})", self.inner.font_size)
    }
}

// ── HeaderCell ────────────────────────────────────────────────────────────

#[pyclass(name = "HeaderCell", from_py_object)]
#[derive(Clone)]
pub struct PyHeaderCell {
    pub inner: HeaderCell,
}

#[pymethods]
impl PyHeaderCell {
    #[new]
    fn new(text: &str) -> Self {
        Self { inner: HeaderCell::new(text) }
    }

    fn colspan(&self, span: usize) -> Self {
        Self { inner: self.inner.clone().colspan(span) }
    }

    fn rowspan(&self, span: usize) -> Self {
        Self { inner: self.inner.clone().rowspan(span) }
    }

    fn style(&self, style: &PyCellStyle) -> Self {
        Self { inner: self.inner.clone().style(style.inner.clone()) }
    }

    #[getter]
    fn text(&self) -> &str {
        &self.inner.text
    }

    #[getter]
    fn span_cols(&self) -> usize {
        self.inner.colspan
    }

    #[getter]
    fn span_rows(&self) -> usize {
        self.inner.rowspan
    }

    fn __repr__(&self) -> String {
        format!(
            "HeaderCell(text={:?}, colspan={}, rowspan={})",
            self.inner.text, self.inner.colspan, self.inner.rowspan
        )
    }
}

// ── HeaderBuilder ─────────────────────────────────────────────────────────

#[pyclass(name = "HeaderBuilder")]
pub struct PyHeaderBuilder {
    inner: Option<HeaderBuilder>,
}

#[pymethods]
impl PyHeaderBuilder {
    #[new]
    fn new(total_columns: usize) -> Self {
        Self { inner: Some(HeaderBuilder::new(total_columns)) }
    }

    #[staticmethod]
    fn auto() -> Self {
        Self { inner: Some(HeaderBuilder::auto()) }
    }

    #[staticmethod]
    fn financial_report() -> Self {
        Self { inner: Some(HeaderBuilder::financial_report()) }
    }

    #[staticmethod]
    fn product_comparison(products: Vec<String>) -> Self {
        let refs: Vec<&str> = products.iter().map(|s| s.as_str()).collect();
        Self { inner: Some(HeaderBuilder::product_comparison(refs)) }
    }

    fn add_simple_row(&mut self, headers: Vec<String>) {
        if let Some(b) = self.inner.take() {
            let refs: Vec<&str> = headers.iter().map(|s| s.as_str()).collect();
            self.inner = Some(b.add_simple_row(refs));
        }
    }

    fn add_level(&mut self, headers: Vec<(String, usize)>) {
        if let Some(b) = self.inner.take() {
            let refs: Vec<(&str, usize)> =
                headers.iter().map(|(s, n)| (s.as_str(), *n)).collect();
            self.inner = Some(b.add_level(refs));
        }
    }

    fn default_style(&mut self, style: &PyCellStyle) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.default_style(style.inner.clone()));
        }
    }

    fn add_custom_row(&mut self, cells: Vec<PyRef<PyHeaderCell>>) {
        if let Some(b) = self.inner.take() {
            let cells: Vec<HeaderCell> = cells.iter().map(|c| c.inner.clone()).collect();
            self.inner = Some(b.add_custom_row(cells));
        }
    }

    fn add_group(&mut self, group_header: &str, sub_headers: Vec<String>) {
        if let Some(b) = self.inner.take() {
            let refs: Vec<&str> = sub_headers.iter().map(|s| s.as_str()).collect();
            self.inner = Some(b.add_group(group_header, refs));
        }
    }

    fn row_count(&self) -> usize {
        self.inner.as_ref().map(|b| b.row_count()).unwrap_or(0)
    }

    fn __repr__(&self) -> String {
        if let Some(b) = &self.inner {
            format!("HeaderBuilder(levels={}, cols={})", b.levels.len(), b.total_columns)
        } else {
            "HeaderBuilder(consumed)".to_string()
        }
    }
}

// ── AdvColumn ─────────────────────────────────────────────────────────────

#[pyclass(name = "AdvColumn", from_py_object)]
#[derive(Clone)]
pub struct PyAdvColumn {
    pub inner: Column,
}

#[pymethods]
impl PyAdvColumn {
    #[new]
    fn new(header: &str, width: f64) -> Self {
        Self { inner: Column::new(header, width) }
    }

    fn with_style(&self, style: &PyCellStyle) -> Self {
        Self { inner: self.inner.clone().with_style(style.inner.clone()) }
    }

    fn auto_resize(&self, min_width: Option<f64>, max_width: Option<f64>) -> Self {
        Self { inner: self.inner.clone().auto_resize(min_width, max_width) }
    }

    #[getter]
    fn header(&self) -> &str {
        &self.inner.header
    }

    #[getter]
    fn width(&self) -> f64 {
        self.inner.width
    }

    fn __repr__(&self) -> String {
        format!("AdvColumn(header={:?}, width={})", self.inner.header, self.inner.width)
    }
}

// ── CellData ──────────────────────────────────────────────────────────────

#[pyclass(name = "CellData", from_py_object)]
#[derive(Clone)]
pub struct PyCellData {
    pub inner: CellData,
}

#[pymethods]
impl PyCellData {
    #[new]
    fn new(content: &str) -> Self {
        Self { inner: CellData::new(content) }
    }

    fn with_style(&self, style: &PyCellStyle) -> Self {
        Self { inner: self.inner.clone().with_style(style.inner.clone()) }
    }

    fn colspan(&self, span: usize) -> Self {
        Self { inner: self.inner.clone().colspan(span) }
    }

    fn rowspan(&self, span: usize) -> Self {
        Self { inner: self.inner.clone().rowspan(span) }
    }

    #[getter]
    fn content(&self) -> &str {
        &self.inner.content
    }

    fn __repr__(&self) -> String {
        format!(
            "CellData(content={:?}, colspan={}, rowspan={})",
            self.inner.content, self.inner.colspan, self.inner.rowspan
        )
    }
}

// ── RowData ───────────────────────────────────────────────────────────────

#[pyclass(name = "RowData", from_py_object)]
#[derive(Clone)]
pub struct PyRowData {
    pub inner: RowData,
}

#[pymethods]
impl PyRowData {
    #[staticmethod]
    fn from_strings(content: Vec<String>) -> Self {
        let refs: Vec<&str> = content.iter().map(|s| s.as_str()).collect();
        Self { inner: RowData::from_strings(refs) }
    }

    #[staticmethod]
    fn from_cells(cells: Vec<PyRef<PyCellData>>) -> Self {
        let cells: Vec<CellData> = cells.iter().map(|c| c.inner.clone()).collect();
        Self { inner: RowData::from_cells(cells) }
    }

    fn with_style(&self, style: &PyCellStyle) -> Self {
        Self { inner: self.inner.clone().with_style(style.inner.clone()) }
    }

    fn min_height(&self, height: f64) -> Self {
        Self { inner: self.inner.clone().min_height(height) }
    }

    fn cell_count(&self) -> usize {
        self.inner.cells.len()
    }

    fn __repr__(&self) -> String {
        format!("RowData(cells={})", self.inner.cells.len())
    }
}

// ── ZebraConfig ───────────────────────────────────────────────────────────

#[pyclass(name = "ZebraConfig", from_py_object)]
#[derive(Clone)]
pub struct PyZebraConfig {
    pub inner: ZebraConfig,
}

#[pymethods]
impl PyZebraConfig {
    #[new]
    fn new(odd_color: Option<&PyColor>, even_color: Option<&PyColor>) -> Self {
        Self {
            inner: ZebraConfig::new(
                odd_color.map(|c| c.inner),
                even_color.map(|c| c.inner),
            ),
        }
    }

    #[staticmethod]
    fn simple(color: &PyColor) -> Self {
        Self { inner: ZebraConfig::simple(color.inner) }
    }

    fn __repr__(&self) -> String {
        format!(
            "ZebraConfig(odd={}, even={}, start_with_odd={})",
            self.inner.odd_color.is_some(),
            self.inner.even_color.is_some(),
            self.inner.start_with_odd
        )
    }
}

// ── AdvancedTable ─────────────────────────────────────────────────────────

#[pyclass(name = "AdvancedTable", from_py_object)]
#[derive(Clone)]
pub struct PyAdvancedTable {
    pub inner: AdvancedTable,
}

#[pymethods]
impl PyAdvancedTable {
    fn column_count(&self) -> usize {
        self.inner.column_count()
    }

    fn row_count(&self) -> usize {
        self.inner.row_count()
    }

    fn calculate_width(&self) -> f64 {
        self.inner.calculate_width()
    }

    fn __repr__(&self) -> String {
        format!(
            "AdvancedTable(cols={}, rows={})",
            self.inner.column_count(),
            self.inner.row_count()
        )
    }
}

// ── AdvancedTableBuilder ──────────────────────────────────────────────────

#[pyclass(name = "AdvancedTableBuilder")]
pub struct PyAdvancedTableBuilder {
    inner: Option<AdvancedTableBuilder>,
}

#[pymethods]
impl PyAdvancedTableBuilder {
    #[new]
    fn new() -> Self {
        Self { inner: Some(AdvancedTableBuilder::new()) }
    }

    fn add_column(&mut self, header: &str, width: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.add_column(header, width));
        }
    }

    fn add_styled_column(&mut self, header: &str, width: f64, style: &PyCellStyle) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.add_styled_column(header, width, style.inner.clone()));
        }
    }

    fn columns_equal_width(&mut self, headers: Vec<String>, total_width: f64) {
        if let Some(b) = self.inner.take() {
            let refs: Vec<&str> = headers.iter().map(|s| s.as_str()).collect();
            self.inner = Some(b.columns_equal_width(refs, total_width));
        }
    }

    fn add_row(&mut self, content: Vec<String>) {
        if let Some(b) = self.inner.take() {
            let refs: Vec<&str> = content.iter().map(|s| s.as_str()).collect();
            self.inner = Some(b.add_row(refs));
        }
    }

    fn add_row_cells(&mut self, cells: Vec<PyRef<PyCellData>>) {
        if let Some(b) = self.inner.take() {
            let cells: Vec<CellData> = cells.iter().map(|c| c.inner.clone()).collect();
            self.inner = Some(b.add_row_cells(cells));
        }
    }

    fn add_styled_row(&mut self, content: Vec<String>, style: &PyCellStyle) {
        if let Some(b) = self.inner.take() {
            let refs: Vec<&str> = content.iter().map(|s| s.as_str()).collect();
            self.inner = Some(b.add_styled_row(refs, style.inner.clone()));
        }
    }

    fn add_data(&mut self, data: Vec<Vec<String>>) {
        if let Some(b) = self.inner.take() {
            let refs: Vec<Vec<&str>> =
                data.iter().map(|row| row.iter().map(|s| s.as_str()).collect()).collect();
            self.inner = Some(b.add_data(refs));
        }
    }

    fn default_style(&mut self, style: &PyCellStyle) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.default_style(style.inner.clone()));
        }
    }

    fn data_style(&mut self, style: &PyCellStyle) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.data_style(style.inner.clone()));
        }
    }

    fn header_style(&mut self, style: &PyCellStyle) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.header_style(style.inner.clone()));
        }
    }

    fn show_header(&mut self, show: bool) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.show_header(show));
        }
    }

    fn title(&mut self, text: &str) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.title(text));
        }
    }

    fn position(&mut self, x: f64, y: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.position(x, y));
        }
    }

    fn complex_header(&mut self, header: &mut PyHeaderBuilder) {
        if let Some(b) = self.inner.take() {
            if let Some(h) = header.inner.take() {
                self.inner = Some(b.complex_header(h));
            } else {
                self.inner = Some(b);
            }
        }
    }

    fn zebra_stripes(&mut self, enabled: bool, color: &PyColor) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.zebra_stripes(enabled, color.inner));
        }
    }

    fn zebra_striping(&mut self, color: &PyColor) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.zebra_striping(color.inner));
        }
    }

    fn zebra_striping_custom(&mut self, config: &PyZebraConfig) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.zebra_striping_custom(config.inner.clone()));
        }
    }

    fn table_border(&mut self, enabled: bool) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.table_border(enabled));
        }
    }

    fn cell_spacing(&mut self, spacing: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.cell_spacing(spacing));
        }
    }

    fn total_width(&mut self, width: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.total_width(width));
        }
    }

    fn repeat_headers(&mut self, repeat: bool) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.repeat_headers(repeat));
        }
    }

    fn set_cell_style(&mut self, row: usize, col: usize, style: &PyCellStyle) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.set_cell_style(row, col, style.inner.clone()));
        }
    }

    fn financial_table(&mut self) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.financial_table());
        }
    }

    fn minimal_table(&mut self) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.minimal_table());
        }
    }

    fn build(&mut self) -> PyResult<PyAdvancedTable> {
        let b = self.inner.take().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("AdvancedTableBuilder already consumed")
        })?;
        b.build()
            .map(|t| PyAdvancedTable { inner: t })
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    fn __repr__(&self) -> String {
        if self.inner.is_some() {
            "AdvancedTableBuilder(active)".to_string()
        } else {
            "AdvancedTableBuilder(consumed)".to_string()
        }
    }
}

// ── AdvTableRenderer ──────────────────────────────────────────────────────

#[pyclass(name = "AdvTableRenderer")]
pub struct PyAdvTableRenderer {
    pub inner: TableRenderer,
}

#[pymethods]
impl PyAdvTableRenderer {
    #[new]
    fn new() -> Self {
        Self { inner: TableRenderer::new() }
    }

    fn render_table(
        &self,
        page: &mut crate::page::PyPage,
        table: &PyAdvancedTable,
        x: f64,
        y: f64,
    ) -> PyResult<f64> {
        self.inner
            .render_table(&mut page.inner, &table.inner, x, y)
            .map_err(to_py_err)
    }

    fn __repr__(&self) -> String {
        "AdvTableRenderer()".to_string()
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyCellAlignment>()?;
    m.add_class::<PyCellBorderStyle>()?;
    m.add_class::<PyCellPadding>()?;
    m.add_class::<PyCellStyle>()?;
    m.add_class::<PyHeaderCell>()?;
    m.add_class::<PyHeaderBuilder>()?;
    m.add_class::<PyAdvColumn>()?;
    m.add_class::<PyCellData>()?;
    m.add_class::<PyRowData>()?;
    m.add_class::<PyZebraConfig>()?;
    m.add_class::<PyAdvancedTable>()?;
    m.add_class::<PyAdvancedTableBuilder>()?;
    m.add_class::<PyAdvTableRenderer>()?;
    Ok(())
}
