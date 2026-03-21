use std::io::Cursor;

use pyo3::prelude::*;
use oxidize_pdf::graphics::extraction::{
    LineOrientation, VectorLine, ExtractedGraphics, ExtractionConfig, GraphicsExtractor,
};

// ── PyLineOrientation ─────────────────────────────────────────────────────

/// Orientation of a vector line segment.
///
/// Variants: ``HORIZONTAL``, ``VERTICAL``, ``DIAGONAL``.
#[pyclass(name = "LineOrientation", frozen, from_py_object, eq)]
#[derive(Clone, Copy, PartialEq, Eq)]
pub struct PyLineOrientation {
    pub inner: LineOrientation,
}

#[pymethods]
impl PyLineOrientation {
    #[classattr]
    const HORIZONTAL: Self = Self { inner: LineOrientation::Horizontal };

    #[classattr]
    const VERTICAL: Self = Self { inner: LineOrientation::Vertical };

    #[classattr]
    const DIAGONAL: Self = Self { inner: LineOrientation::Diagonal };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            LineOrientation::Horizontal => "HORIZONTAL",
            LineOrientation::Vertical => "VERTICAL",
            LineOrientation::Diagonal => "DIAGONAL",
        };
        format!("LineOrientation.{}", name)
    }
}

// ── PyVectorLine ──────────────────────────────────────────────────────────

/// A vector line segment extracted from PDF graphics.
///
/// Constructor: ``VectorLine(x1, y1, x2, y2, stroke_width, is_stroked)``.
/// Computed: ``orientation``, ``length()``, ``midpoint()``.
#[pyclass(name = "VectorLine", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyVectorLine {
    pub inner: VectorLine,
}

#[pymethods]
impl PyVectorLine {
    #[new]
    fn new(x1: f64, y1: f64, x2: f64, y2: f64, stroke_width: f64, is_stroked: bool) -> Self {
        Self {
            inner: VectorLine::new(x1, y1, x2, y2, stroke_width, is_stroked, None),
        }
    }

    #[getter]
    fn x1(&self) -> f64 { self.inner.x1 }

    #[getter]
    fn y1(&self) -> f64 { self.inner.y1 }

    #[getter]
    fn x2(&self) -> f64 { self.inner.x2 }

    #[getter]
    fn y2(&self) -> f64 { self.inner.y2 }

    #[getter]
    fn orientation(&self) -> PyLineOrientation {
        PyLineOrientation { inner: self.inner.orientation }
    }

    #[getter]
    fn stroke_width(&self) -> f64 { self.inner.stroke_width }

    #[getter]
    fn is_stroked(&self) -> bool { self.inner.is_stroked }

    #[getter]
    fn length(&self) -> f64 { self.inner.length() }

    #[getter]
    fn midpoint(&self) -> (f64, f64) { self.inner.midpoint() }

    fn __repr__(&self) -> String {
        format!(
            "VectorLine(({}, {}) -> ({}, {}), orientation={:?})",
            self.inner.x1, self.inner.y1, self.inner.x2, self.inner.y2,
            match self.inner.orientation {
                LineOrientation::Horizontal => "HORIZONTAL",
                LineOrientation::Vertical => "VERTICAL",
                LineOrientation::Diagonal => "DIAGONAL",
            }
        )
    }
}

// ── PyExtractedGraphics ───────────────────────────────────────────────────

/// Container for vector line segments extracted from a PDF page.
///
/// Use ``add_line()`` to populate, then inspect via ``lines``,
/// ``horizontal_lines``, ``vertical_lines``, ``has_table_structure``.
#[pyclass(name = "ExtractedGraphics", from_py_object)]
#[derive(Clone)]
pub struct PyExtractedGraphics {
    pub inner: ExtractedGraphics,
}

#[pymethods]
impl PyExtractedGraphics {
    #[new]
    fn new() -> Self {
        Self { inner: ExtractedGraphics::new() }
    }

    fn add_line(&mut self, line: &PyVectorLine) {
        self.inner.add_line(line.inner.clone());
    }

    #[getter]
    fn lines(&self) -> Vec<PyVectorLine> {
        self.inner.lines.iter().map(|l| PyVectorLine { inner: l.clone() }).collect()
    }

    #[getter]
    fn horizontal_count(&self) -> usize { self.inner.horizontal_count }

    #[getter]
    fn vertical_count(&self) -> usize { self.inner.vertical_count }

    #[getter]
    fn has_table_structure(&self) -> bool { self.inner.has_table_structure() }

    #[getter]
    fn horizontal_lines(&self) -> Vec<PyVectorLine> {
        self.inner
            .horizontal_lines()
            .map(|l| PyVectorLine { inner: l.clone() })
            .collect()
    }

    #[getter]
    fn vertical_lines(&self) -> Vec<PyVectorLine> {
        self.inner
            .vertical_lines()
            .map(|l| PyVectorLine { inner: l.clone() })
            .collect()
    }

    fn __repr__(&self) -> String {
        format!(
            "ExtractedGraphics(lines={}, h={}, v={})",
            self.inner.lines.len(),
            self.inner.horizontal_count,
            self.inner.vertical_count
        )
    }
}

// ── PyExtractionConfig ────────────────────────────────────────────────────

/// Configuration for the graphics extractor.
///
/// Constructor: ``ExtractionConfig(min_line_length=1.0, extract_diagonals=False, stroked_only=True)``.
#[pyclass(name = "ExtractionConfig", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyExtractionConfig {
    pub inner: ExtractionConfig,
}

#[pymethods]
impl PyExtractionConfig {
    #[new]
    #[pyo3(signature = (min_line_length = 1.0, extract_diagonals = false, stroked_only = true))]
    fn new(min_line_length: f64, extract_diagonals: bool, stroked_only: bool) -> Self {
        Self {
            inner: ExtractionConfig {
                min_line_length,
                extract_diagonals,
                stroked_only,
            },
        }
    }

    #[getter]
    fn min_line_length(&self) -> f64 { self.inner.min_line_length }

    #[getter]
    fn extract_diagonals(&self) -> bool { self.inner.extract_diagonals }

    #[getter]
    fn stroked_only(&self) -> bool { self.inner.stroked_only }

    fn __repr__(&self) -> String {
        format!(
            "ExtractionConfig(min_line_length={}, extract_diagonals={}, stroked_only={})",
            self.inner.min_line_length, self.inner.extract_diagonals, self.inner.stroked_only
        )
    }
}

// ── PyGraphicsExtractor ───────────────────────────────────────────────────

/// Extracts vector graphics (line segments) from PDF pages.
///
/// Constructor: ``GraphicsExtractor(config=None)`` — pass an
/// ``ExtractionConfig`` or omit for defaults.
/// Method: ``extract_from_bytes(pdf_bytes, page_index)`` → ``ExtractedGraphics``.
#[pyclass(name = "GraphicsExtractor")]
pub struct PyGraphicsExtractor {
    inner: GraphicsExtractor,
}

#[pymethods]
impl PyGraphicsExtractor {
    #[new]
    #[pyo3(signature = (config = None))]
    fn new(config: Option<&PyExtractionConfig>) -> Self {
        let extractor = match config {
            Some(c) => GraphicsExtractor::new(c.inner.clone()),
            None => GraphicsExtractor::default(),
        };
        Self { inner: extractor }
    }

    fn extract_from_bytes(
        &mut self,
        pdf_bytes: &[u8],
        page_index: usize,
    ) -> PyResult<PyExtractedGraphics> {
        let cursor = Cursor::new(pdf_bytes.to_vec());
        let reader = oxidize_pdf::PdfReader::new(cursor)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Failed to open PDF: {}", e)))?;
        let document = oxidize_pdf::PdfDocument::new(reader);
        let graphics = self
            .inner
            .extract_from_page(&document, page_index)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Extraction failed: {}", e)))?;
        Ok(PyExtractedGraphics { inner: graphics })
    }

    fn __repr__(&self) -> String {
        "GraphicsExtractor(...)".to_string()
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyLineOrientation>()?;
    m.add_class::<PyVectorLine>()?;
    m.add_class::<PyExtractedGraphics>()?;
    m.add_class::<PyExtractionConfig>()?;
    m.add_class::<PyGraphicsExtractor>()?;
    Ok(())
}
