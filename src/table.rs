use pyo3::prelude::*;

use oxidize_pdf::text::table::{GridStyle, HeaderStyle, Table, TableCell, TableOptions};

use crate::errors::to_py_err;
use crate::text::PyFont;
use crate::types::PyColor;

// ── GridStyle ──────────────────────────────────────────────────────────────

#[pyclass(name = "GridStyle", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyGridStyle {
    pub inner: GridStyle,
}

#[pymethods]
impl PyGridStyle {
    #[classattr]
    const NONE: PyGridStyle = PyGridStyle {
        inner: GridStyle::None,
    };
    #[classattr]
    const HORIZONTAL: PyGridStyle = PyGridStyle {
        inner: GridStyle::Horizontal,
    };
    #[classattr]
    const VERTICAL: PyGridStyle = PyGridStyle {
        inner: GridStyle::Vertical,
    };
    #[classattr]
    const FULL: PyGridStyle = PyGridStyle {
        inner: GridStyle::Full,
    };
    #[classattr]
    const OUTLINE: PyGridStyle = PyGridStyle {
        inner: GridStyle::Outline,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            GridStyle::None => "NONE",
            GridStyle::Horizontal => "HORIZONTAL",
            GridStyle::Vertical => "VERTICAL",
            GridStyle::Full => "FULL",
            GridStyle::Outline => "OUTLINE",
        };
        format!("GridStyle.{name}")
    }
}

// ── HeaderStyle ────────────────────────────────────────────────────────────

#[pyclass(name = "HeaderStyle", from_py_object)]
#[derive(Clone)]
pub struct PyHeaderStyle {
    pub inner: HeaderStyle,
}

#[pymethods]
impl PyHeaderStyle {
    #[new]
    #[pyo3(signature = (background_color=None, text_color=None, font=None, bold=true))]
    fn new(
        background_color: Option<&PyColor>,
        text_color: Option<&PyColor>,
        font: Option<&PyFont>,
        bold: bool,
    ) -> Self {
        Self {
            inner: HeaderStyle {
                background_color: background_color
                    .map(|c| c.inner)
                    .unwrap_or(oxidize_pdf::Color::rgb(0.9, 0.9, 0.9)),
                text_color: text_color
                    .map(|c| c.inner)
                    .unwrap_or(oxidize_pdf::Color::black()),
                font: font
                    .map(|f| f.inner.clone())
                    .unwrap_or(oxidize_pdf::Font::HelveticaBold),
                bold,
            },
        }
    }

    fn __repr__(&self) -> String {
        format!("HeaderStyle(bold={})", self.inner.bold)
    }
}

// ── TableOptions ───────────────────────────────────────────────────────────

#[pyclass(name = "TableOptions", from_py_object)]
#[derive(Clone)]
pub struct PyTableOptions {
    pub inner: TableOptions,
}

#[pymethods]
impl PyTableOptions {
    #[new]
    #[pyo3(signature = (
        border_width=None,
        cell_padding=None,
        row_height=None,
        font=None,
        font_size=None,
        text_color=None,
        border_color=None,
        grid_style=None,
        header_style=None,
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        border_width: Option<f64>,
        cell_padding: Option<f64>,
        row_height: Option<f64>,
        font: Option<&PyFont>,
        font_size: Option<f64>,
        text_color: Option<&PyColor>,
        border_color: Option<&PyColor>,
        grid_style: Option<&PyGridStyle>,
        header_style: Option<&PyHeaderStyle>,
    ) -> Self {
        let mut opts = TableOptions::default();
        if let Some(v) = border_width {
            opts.border_width = v;
        }
        if let Some(v) = cell_padding {
            opts.cell_padding = v;
        }
        if let Some(v) = row_height {
            opts.row_height = v;
        }
        if let Some(f) = font {
            opts.font = f.inner.clone();
        }
        if let Some(v) = font_size {
            opts.font_size = v;
        }
        if let Some(c) = text_color {
            opts.text_color = c.inner;
        }
        if let Some(c) = border_color {
            opts.border_color = c.inner;
        }
        if let Some(g) = grid_style {
            opts.grid_style = g.inner;
        }
        if let Some(h) = header_style {
            opts.header_style = Some(h.inner.clone());
        }
        Self { inner: opts }
    }

    fn __repr__(&self) -> String {
        format!(
            "TableOptions(border_width={}, font_size={}, cell_padding={})",
            self.inner.border_width, self.inner.font_size, self.inner.cell_padding
        )
    }
}

// ── TableCell ──────────────────────────────────────────────────────────────

#[pyclass(name = "TableCell", from_py_object)]
#[derive(Clone)]
pub struct PyTableCell {
    pub inner: TableCell,
}

#[pymethods]
impl PyTableCell {
    #[new]
    fn new(content: &str) -> Self {
        Self {
            inner: TableCell::new(content.to_string()),
        }
    }

    #[staticmethod]
    fn with_colspan(content: &str, colspan: usize) -> Self {
        Self {
            inner: TableCell::with_colspan(content.to_string(), colspan),
        }
    }

    fn set_background_color(&mut self, color: &PyColor) {
        self.inner.set_background_color(color.inner);
    }

    fn __repr__(&self) -> String {
        "TableCell(...)".to_string()
    }
}

// ── TableStyle ─────────────────────────────────────────────────────────────

#[pyclass(name = "TableStyle", from_py_object)]
#[derive(Clone)]
pub struct PyTableStyle {
    pub inner: oxidize_pdf::TableStyle,
}

#[pymethods]
impl PyTableStyle {
    #[staticmethod]
    fn minimal() -> Self {
        Self {
            inner: oxidize_pdf::TableStyle::minimal(),
        }
    }

    #[staticmethod]
    fn simple() -> Self {
        Self {
            inner: oxidize_pdf::TableStyle::simple(),
        }
    }

    #[staticmethod]
    fn professional() -> Self {
        Self {
            inner: oxidize_pdf::TableStyle::professional(),
        }
    }

    #[staticmethod]
    fn colorful() -> Self {
        Self {
            inner: oxidize_pdf::TableStyle::colorful(),
        }
    }

    fn __repr__(&self) -> String {
        "TableStyle(...)".to_string()
    }
}

// ── Table ──────────────────────────────────────────────────────────────────

#[pyclass(name = "Table", from_py_object)]
#[derive(Clone)]
pub struct PyTable {
    pub inner: Table,
}

#[pymethods]
impl PyTable {
    #[new]
    fn new(column_widths: Vec<f64>) -> Self {
        Self {
            inner: Table::new(column_widths),
        }
    }

    #[staticmethod]
    fn with_equal_columns(num_columns: usize, total_width: f64) -> Self {
        Self {
            inner: Table::with_equal_columns(num_columns, total_width),
        }
    }

    fn add_row(&mut self, cells: Vec<String>) -> PyResult<()> {
        self.inner.add_row(cells).map_err(to_py_err)?;
        Ok(())
    }

    fn add_header_row(&mut self, cells: Vec<String>) -> PyResult<()> {
        self.inner.add_header_row(cells).map_err(to_py_err)?;
        Ok(())
    }

    fn add_custom_row(&mut self, cells: Vec<PyTableCell>) -> PyResult<()> {
        let inner_cells: Vec<TableCell> = cells.into_iter().map(|c| c.inner).collect();
        self.inner.add_custom_row(inner_cells).map_err(to_py_err)?;
        Ok(())
    }

    fn set_options(&mut self, options: &PyTableOptions) {
        self.inner.set_options(options.inner.clone());
    }

    fn set_position(&mut self, x: f64, y: f64) {
        self.inner.set_position(x, y);
    }

    #[getter]
    fn width(&self) -> f64 {
        self.inner.get_width()
    }

    #[getter]
    fn height(&self) -> f64 {
        self.inner.get_height()
    }

    fn __repr__(&self) -> String {
        format!(
            "Table(width={}, height={})",
            self.inner.get_width(),
            self.inner.get_height()
        )
    }
}

// ── Registration ───────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyGridStyle>()?;
    m.add_class::<PyHeaderStyle>()?;
    m.add_class::<PyTableOptions>()?;
    m.add_class::<PyTableCell>()?;
    m.add_class::<PyTableStyle>()?;
    m.add_class::<PyTable>()?;
    Ok(())
}
