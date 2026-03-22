//! Charts bindings — Feature 58
//!
//! Wraps `oxidize_pdf::charts` for Python: bar charts, pie charts, line charts,
//! chart renderer, and dashboard wrappers.

use pyo3::prelude::*;

use oxidize_pdf::charts::{
    BarChart, BarChartBuilder, BarOrientation, ChartType, DashboardBarChart, DashboardLineChart,
    DashboardPieChart, DataSeries, LegendPosition, LineChart, LineChartBuilder, PieChart,
    PieChartBuilder, PieSegment,
};

use crate::errors::to_py_err;
use crate::text::PyFont;
use crate::types::PyColor;

// ── ChartType ─────────────────────────────────────────────────────────────

#[pyclass(name = "ChartType", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyChartType {
    pub inner: ChartType,
}

#[pymethods]
impl PyChartType {
    #[classattr]
    const VERTICAL_BAR: Self = Self { inner: ChartType::VerticalBar };
    #[classattr]
    const HORIZONTAL_BAR: Self = Self { inner: ChartType::HorizontalBar };
    #[classattr]
    const PIE: Self = Self { inner: ChartType::Pie };
    #[classattr]
    const LINE: Self = Self { inner: ChartType::Line };
    #[classattr]
    const AREA: Self = Self { inner: ChartType::Area };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            ChartType::VerticalBar => "VERTICAL_BAR",
            ChartType::HorizontalBar => "HORIZONTAL_BAR",
            ChartType::Pie => "PIE",
            ChartType::Line => "LINE",
            ChartType::Area => "AREA",
        };
        format!("ChartType.{}", name)
    }
}

// ── LegendPosition ────────────────────────────────────────────────────────

#[pyclass(name = "LegendPosition", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyLegendPosition {
    pub inner: LegendPosition,
}

#[pymethods]
impl PyLegendPosition {
    #[classattr]
    const NONE: Self = Self { inner: LegendPosition::None };
    #[classattr]
    const RIGHT: Self = Self { inner: LegendPosition::Right };
    #[classattr]
    const BOTTOM: Self = Self { inner: LegendPosition::Bottom };
    #[classattr]
    const TOP: Self = Self { inner: LegendPosition::Top };
    #[classattr]
    const LEFT: Self = Self { inner: LegendPosition::Left };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            LegendPosition::None => "NONE",
            LegendPosition::Right => "RIGHT",
            LegendPosition::Bottom => "BOTTOM",
            LegendPosition::Top => "TOP",
            LegendPosition::Left => "LEFT",
        };
        format!("LegendPosition.{}", name)
    }
}

// ── BarOrientation ────────────────────────────────────────────────────────

#[pyclass(name = "BarOrientation", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyBarOrientation {
    pub inner: BarOrientation,
}

#[pymethods]
impl PyBarOrientation {
    #[classattr]
    const VERTICAL: Self = Self { inner: BarOrientation::Vertical };
    #[classattr]
    const HORIZONTAL: Self = Self { inner: BarOrientation::Horizontal };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            BarOrientation::Vertical => "VERTICAL",
            BarOrientation::Horizontal => "HORIZONTAL",
        };
        format!("BarOrientation.{}", name)
    }
}

// ── ChartData ─────────────────────────────────────────────────────────────

#[pyclass(name = "ChartData", from_py_object)]
#[derive(Clone)]
pub struct PyChartData {
    pub inner: oxidize_pdf::charts::ChartData,
}

#[pymethods]
impl PyChartData {
    #[new]
    fn new(label: &str, value: f64) -> Self {
        Self {
            inner: oxidize_pdf::charts::ChartData::new(label, value),
        }
    }

    fn color(&self, color: &PyColor) -> Self {
        Self {
            inner: self.inner.clone().color(color.inner),
        }
    }

    fn highlighted(&self) -> Self {
        Self {
            inner: self.inner.clone().highlighted(),
        }
    }

    fn __repr__(&self) -> String {
        format!("ChartData(label={:?}, value={})", self.inner.label, self.inner.value)
    }
}

// ── BarChart ──────────────────────────────────────────────────────────────

#[pyclass(name = "BarChart", from_py_object)]
#[derive(Clone)]
pub struct PyBarChart {
    pub inner: BarChart,
}

#[pymethods]
impl PyBarChart {
    fn __repr__(&self) -> String {
        format!("BarChart(title={:?}, bars={})", self.inner.title, self.inner.data.len())
    }
}

// ── BarChartBuilder ───────────────────────────────────────────────────────

#[pyclass(name = "BarChartBuilder")]
pub struct PyBarChartBuilder {
    inner: Option<BarChartBuilder>,
}

#[pymethods]
impl PyBarChartBuilder {
    #[new]
    fn new() -> Self {
        Self { inner: Some(BarChartBuilder::new()) }
    }

    fn title(&mut self, title: &str) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.title(title));
        }
    }

    fn add_data(&mut self, data: &PyChartData) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.add_data(data.inner.clone()));
        }
    }

    fn data(&mut self, data: Vec<PyRef<PyChartData>>) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.data(data.iter().map(|d| d.inner.clone()).collect()));
        }
    }

    fn orientation(&mut self, orientation: &PyBarOrientation) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.orientation(orientation.inner));
        }
    }

    fn colors(&mut self, colors: Vec<PyRef<PyColor>>) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.colors(colors.iter().map(|c| c.inner).collect()));
        }
    }

    fn title_font(&mut self, font: &PyFont, size: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.title_font(font.inner.clone(), size));
        }
    }

    fn label_font(&mut self, font: &PyFont, size: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.label_font(font.inner.clone(), size));
        }
    }

    fn value_font(&mut self, font: &PyFont, size: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.value_font(font.inner.clone(), size));
        }
    }

    fn legend_position(&mut self, position: &PyLegendPosition) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.legend_position(position.inner));
        }
    }

    fn background_color(&mut self, color: &PyColor) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.background_color(color.inner));
        }
    }

    fn show_values(&mut self, show: bool) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.show_values(show));
        }
    }

    fn show_grid(&mut self, show: bool) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.show_grid(show));
        }
    }

    fn grid_color(&mut self, color: &PyColor) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.grid_color(color.inner));
        }
    }

    fn bar_spacing(&mut self, spacing: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.bar_spacing(spacing));
        }
    }

    fn bar_border(&mut self, color: &PyColor, width: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.bar_border(color.inner, width));
        }
    }

    fn bar_width_range(&mut self, min_width: f64, max_width: Option<f64>) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.bar_width_range(min_width, max_width));
        }
    }

    fn simple_data(&mut self, values: Vec<f64>) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.simple_data(values));
        }
    }

    fn labeled_data(&mut self, data: Vec<(String, f64)>) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(
                b.labeled_data(data.iter().map(|(l, v)| (l.as_str(), *v)).collect()),
            );
        }
    }

    fn financial_style(&mut self) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.financial_style());
        }
    }

    fn minimal_style(&mut self) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.minimal_style());
        }
    }

    fn progress_style(&mut self, color: &PyColor) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.progress_style(color.inner));
        }
    }

    fn build(&mut self) -> PyResult<PyBarChart> {
        let b = self.inner.take().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("BarChartBuilder already consumed")
        })?;
        Ok(PyBarChart { inner: b.build() })
    }

    fn __repr__(&self) -> String {
        if self.inner.is_some() {
            "BarChartBuilder(active)".to_string()
        } else {
            "BarChartBuilder(consumed)".to_string()
        }
    }
}

// ── DataSeries ────────────────────────────────────────────────────────────

#[pyclass(name = "DataSeries", from_py_object)]
#[derive(Clone)]
pub struct PyDataSeries {
    pub inner: DataSeries,
}

#[pymethods]
impl PyDataSeries {
    #[new]
    fn new(name: &str, color: &PyColor) -> Self {
        Self {
            inner: DataSeries::new(name, color.inner),
        }
    }

    fn y_data(&self, values: Vec<f64>) -> Self {
        Self { inner: self.inner.clone().y_data(values) }
    }

    fn xy_data(&self, data: Vec<(f64, f64)>) -> Self {
        Self { inner: self.inner.clone().xy_data(data) }
    }

    fn line_style(&self, width: f64) -> Self {
        Self { inner: self.inner.clone().line_style(width) }
    }

    fn markers(&self, show: bool, size: f64) -> Self {
        Self { inner: self.inner.clone().markers(show, size) }
    }

    fn fill_area(&self, fill_color: Option<&PyColor>) -> Self {
        Self {
            inner: self.inner.clone().fill_area(fill_color.map(|c| c.inner)),
        }
    }

    fn __repr__(&self) -> String {
        format!("DataSeries(name={:?}, points={})", self.inner.name, self.inner.data.len())
    }
}

// ── LineChart ─────────────────────────────────────────────────────────────

#[pyclass(name = "LineChart", from_py_object)]
#[derive(Clone)]
pub struct PyLineChart {
    pub inner: LineChart,
}

#[pymethods]
impl PyLineChart {
    fn __repr__(&self) -> String {
        format!(
            "LineChart(title={:?}, series={})",
            self.inner.title,
            self.inner.series.len()
        )
    }
}

// ── LineChartBuilder ──────────────────────────────────────────────────────

#[pyclass(name = "LineChartBuilder")]
pub struct PyLineChartBuilder {
    inner: Option<LineChartBuilder>,
}

#[pymethods]
impl PyLineChartBuilder {
    #[new]
    fn new() -> Self {
        Self { inner: Some(LineChartBuilder::new()) }
    }

    fn title(&mut self, title: &str) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.title(title));
        }
    }

    fn add_series(&mut self, series: &PyDataSeries) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.add_series(series.inner.clone()));
        }
    }

    fn axis_labels(&mut self, x_label: &str, y_label: &str) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.axis_labels(x_label, y_label));
        }
    }

    fn title_font(&mut self, font: &PyFont, size: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.title_font(font.inner.clone(), size));
        }
    }

    fn label_font(&mut self, font: &PyFont, size: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.label_font(font.inner.clone(), size));
        }
    }

    fn axis_font(&mut self, font: &PyFont, size: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.axis_font(font.inner.clone(), size));
        }
    }

    fn legend_position(&mut self, position: &PyLegendPosition) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.legend_position(position.inner));
        }
    }

    fn background_color(&mut self, color: &PyColor) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.background_color(color.inner));
        }
    }

    fn grid(&mut self, show: bool, color: &PyColor, lines: usize) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.grid(show, color.inner, lines));
        }
    }

    fn x_range(&mut self, min: f64, max: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.x_range(min, max));
        }
    }

    fn y_range(&mut self, min: f64, max: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.y_range(min, max));
        }
    }

    fn add_simple_series(&mut self, name: &str, values: Vec<f64>, color: &PyColor) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.add_simple_series(name, values, color.inner));
        }
    }

    fn build(&mut self) -> PyResult<PyLineChart> {
        let b = self.inner.take().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("LineChartBuilder already consumed")
        })?;
        Ok(PyLineChart { inner: b.build() })
    }

    fn __repr__(&self) -> String {
        if self.inner.is_some() {
            "LineChartBuilder(active)".to_string()
        } else {
            "LineChartBuilder(consumed)".to_string()
        }
    }
}

// ── PieSegment ────────────────────────────────────────────────────────────

#[pyclass(name = "PieSegment", from_py_object)]
#[derive(Clone)]
pub struct PyPieSegment {
    pub inner: PieSegment,
}

#[pymethods]
impl PyPieSegment {
    #[new]
    fn new(label: &str, value: f64, color: &PyColor) -> Self {
        Self {
            inner: PieSegment::new(label, value, color.inner),
        }
    }

    fn exploded(&self, distance: f64) -> Self {
        Self { inner: self.inner.clone().exploded(distance) }
    }

    fn show_percentage(&self, show: bool) -> Self {
        Self { inner: self.inner.clone().show_percentage(show) }
    }

    fn show_label(&self, show: bool) -> Self {
        Self { inner: self.inner.clone().show_label(show) }
    }

    fn __repr__(&self) -> String {
        format!(
            "PieSegment(label={:?}, value={})",
            self.inner.label, self.inner.value
        )
    }
}

// ── PieChart ──────────────────────────────────────────────────────────────

#[pyclass(name = "PieChart", from_py_object)]
#[derive(Clone)]
pub struct PyPieChart {
    pub inner: PieChart,
}

#[pymethods]
impl PyPieChart {
    fn __repr__(&self) -> String {
        format!(
            "PieChart(title={:?}, segments={})",
            self.inner.title,
            self.inner.segments.len()
        )
    }
}

// ── PieChartBuilder ───────────────────────────────────────────────────────

#[pyclass(name = "PieChartBuilder")]
pub struct PyPieChartBuilder {
    inner: Option<PieChartBuilder>,
}

#[pymethods]
impl PyPieChartBuilder {
    #[new]
    fn new() -> Self {
        Self { inner: Some(PieChartBuilder::new()) }
    }

    fn title(&mut self, title: &str) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.title(title));
        }
    }

    fn add_segment(&mut self, segment: &PyPieSegment) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.add_segment(segment.inner.clone()));
        }
    }

    fn segments(&mut self, segments: Vec<PyRef<PyPieSegment>>) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.segments(segments.iter().map(|s| s.inner.clone()).collect()));
        }
    }

    fn colors(&mut self, colors: Vec<PyRef<PyColor>>) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.colors(colors.iter().map(|c| c.inner).collect()));
        }
    }

    fn title_font(&mut self, font: &PyFont, size: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.title_font(font.inner.clone(), size));
        }
    }

    fn label_font(&mut self, font: &PyFont, size: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.label_font(font.inner.clone(), size));
        }
    }

    fn percentage_font(&mut self, font: &PyFont, size: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.percentage_font(font.inner.clone(), size));
        }
    }

    fn legend_position(&mut self, position: &PyLegendPosition) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.legend_position(position.inner));
        }
    }

    fn background_color(&mut self, color: &PyColor) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.background_color(color.inner));
        }
    }

    fn show_percentages(&mut self, show: bool) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.show_percentages(show));
        }
    }

    fn show_labels(&mut self, show: bool) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.show_labels(show));
        }
    }

    fn start_angle(&mut self, angle: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.start_angle(angle));
        }
    }

    fn border(&mut self, color: &PyColor, width: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.border(color.inner, width));
        }
    }

    fn label_settings(&mut self, distance: f64, min_angle: f64) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.label_settings(distance, min_angle));
        }
    }

    fn data(&mut self, data: Vec<PyRef<PyChartData>>) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.data(data.iter().map(|d| d.inner.clone()).collect()));
        }
    }

    fn simple_data(&mut self, values: Vec<f64>) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.simple_data(values));
        }
    }

    fn labeled_data(&mut self, data: Vec<(String, f64)>) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(
                b.labeled_data(data.iter().map(|(l, v)| (l.as_str(), *v)).collect()),
            );
        }
    }

    fn financial_style(&mut self) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.financial_style());
        }
    }

    fn minimal_style(&mut self) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.minimal_style());
        }
    }

    fn donut_style(&mut self) {
        if let Some(b) = self.inner.take() {
            self.inner = Some(b.donut_style());
        }
    }

    fn build(&mut self) -> PyResult<PyPieChart> {
        let b = self.inner.take().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("PieChartBuilder already consumed")
        })?;
        Ok(PyPieChart { inner: b.build() })
    }

    fn __repr__(&self) -> String {
        if self.inner.is_some() {
            "PieChartBuilder(active)".to_string()
        } else {
            "PieChartBuilder(consumed)".to_string()
        }
    }
}

// ── ChartRenderer ─────────────────────────────────────────────────────────

#[pyclass(name = "ChartRenderer")]
pub struct PyChartRenderer {
    pub inner: oxidize_pdf::charts::ChartRenderer,
}

#[pymethods]
impl PyChartRenderer {
    #[new]
    fn new() -> Self {
        Self { inner: oxidize_pdf::charts::ChartRenderer::new() }
    }

    fn render_bar_chart(
        &self,
        page: &mut crate::page::PyPage,
        chart: &PyBarChart,
        x: f64,
        y: f64,
        width: f64,
        height: f64,
    ) -> PyResult<()> {
        self.inner
            .render_bar_chart(&mut page.inner, &chart.inner, x, y, width, height)
            .map_err(to_py_err)
    }

    fn render_pie_chart(
        &self,
        page: &mut crate::page::PyPage,
        chart: &PyPieChart,
        x: f64,
        y: f64,
        radius: f64,
    ) -> PyResult<()> {
        self.inner
            .render_pie_chart(&mut page.inner, &chart.inner, x, y, radius)
            .map_err(to_py_err)
    }

    fn render_line_chart(
        &self,
        page: &mut crate::page::PyPage,
        chart: &PyLineChart,
        x: f64,
        y: f64,
        width: f64,
        height: f64,
    ) -> PyResult<()> {
        self.inner
            .render_line_chart(&mut page.inner, &chart.inner, x, y, width, height)
            .map_err(to_py_err)
    }

    fn __repr__(&self) -> String {
        "ChartRenderer()".to_string()
    }
}

// ── Dashboard wrappers ────────────────────────────────────────────────────

#[pyclass(name = "DashboardBarChart", from_py_object)]
#[derive(Clone)]
pub struct PyDashboardBarChart {
    pub inner: DashboardBarChart,
}

#[pymethods]
impl PyDashboardBarChart {
    #[new]
    fn new(chart: &PyBarChart) -> Self {
        Self { inner: DashboardBarChart::new(chart.inner.clone()) }
    }

    fn span(&self, columns: u8) -> Self {
        Self { inner: self.inner.clone().span(columns) }
    }

    fn __repr__(&self) -> String {
        "DashboardBarChart(...)".to_string()
    }
}

#[pyclass(name = "DashboardPieChart", from_py_object)]
#[derive(Clone)]
pub struct PyDashboardPieChart {
    pub inner: DashboardPieChart,
}

#[pymethods]
impl PyDashboardPieChart {
    #[new]
    fn new(chart: &PyPieChart) -> Self {
        Self { inner: DashboardPieChart::new(chart.inner.clone()) }
    }

    fn span(&self, columns: u8) -> Self {
        Self { inner: self.inner.clone().span(columns) }
    }

    fn __repr__(&self) -> String {
        "DashboardPieChart(...)".to_string()
    }
}

#[pyclass(name = "DashboardLineChart", from_py_object)]
#[derive(Clone)]
pub struct PyDashboardLineChart {
    pub inner: DashboardLineChart,
}

#[pymethods]
impl PyDashboardLineChart {
    #[new]
    fn new(chart: &PyLineChart) -> Self {
        Self { inner: DashboardLineChart::new(chart.inner.clone()) }
    }

    fn span(&self, columns: u8) -> Self {
        Self { inner: self.inner.clone().span(columns) }
    }

    fn __repr__(&self) -> String {
        "DashboardLineChart(...)".to_string()
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyChartType>()?;
    m.add_class::<PyLegendPosition>()?;
    m.add_class::<PyBarOrientation>()?;
    m.add_class::<PyChartData>()?;
    m.add_class::<PyBarChart>()?;
    m.add_class::<PyBarChartBuilder>()?;
    m.add_class::<PyDataSeries>()?;
    m.add_class::<PyLineChart>()?;
    m.add_class::<PyLineChartBuilder>()?;
    m.add_class::<PyPieSegment>()?;
    m.add_class::<PyPieChart>()?;
    m.add_class::<PyPieChartBuilder>()?;
    m.add_class::<PyChartRenderer>()?;
    m.add_class::<PyDashboardBarChart>()?;
    m.add_class::<PyDashboardPieChart>()?;
    m.add_class::<PyDashboardLineChart>()?;
    Ok(())
}
