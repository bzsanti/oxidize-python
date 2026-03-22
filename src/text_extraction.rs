//! Text Extraction Deep bindings — Tier 14 (F71-F74)
//!
//! Wraps `oxidize_pdf::text` extraction, plain-text, column-layout, and
//! validation APIs for Python.

use pyo3::prelude::*;

use oxidize_pdf::text::{
    ColumnContent, ColumnLayout, ColumnOptions, ExtractionOptions, LineBreakMode, MatchType,
    PlainTextConfig, PlainTextResult, TextMatch, TextValidationResult, TextValidator,
};

use crate::text::PyFont;
use crate::types::PyColor;

// ── ExtractionOptions (F71) ───────────────────────────────────────────────

/// Advanced text extraction options controlling layout preservation and spacing.
#[pyclass(name = "ExtractionOptions", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyExtractionOptions {
    pub inner: ExtractionOptions,
}

#[pymethods]
impl PyExtractionOptions {
    #[new]
    #[pyo3(signature = (
        preserve_layout = false,
        space_threshold = 0.3,
        newline_threshold = 10.0,
        sort_by_position = true,
        detect_columns = false,
        column_threshold = 50.0,
        merge_hyphenated = true,
        track_space_decisions = false,
    ))]
    fn new(
        preserve_layout: bool,
        space_threshold: f64,
        newline_threshold: f64,
        sort_by_position: bool,
        detect_columns: bool,
        column_threshold: f64,
        merge_hyphenated: bool,
        track_space_decisions: bool,
    ) -> Self {
        Self {
            inner: ExtractionOptions {
                preserve_layout,
                space_threshold,
                newline_threshold,
                sort_by_position,
                detect_columns,
                column_threshold,
                merge_hyphenated,
                track_space_decisions,
            },
        }
    }

    #[getter]
    fn preserve_layout(&self) -> bool {
        self.inner.preserve_layout
    }

    #[getter]
    fn space_threshold(&self) -> f64 {
        self.inner.space_threshold
    }

    #[getter]
    fn newline_threshold(&self) -> f64 {
        self.inner.newline_threshold
    }

    #[getter]
    fn sort_by_position(&self) -> bool {
        self.inner.sort_by_position
    }

    #[getter]
    fn detect_columns(&self) -> bool {
        self.inner.detect_columns
    }

    #[getter]
    fn column_threshold(&self) -> f64 {
        self.inner.column_threshold
    }

    #[getter]
    fn merge_hyphenated(&self) -> bool {
        self.inner.merge_hyphenated
    }

    #[getter]
    fn track_space_decisions(&self) -> bool {
        self.inner.track_space_decisions
    }

    fn __repr__(&self) -> String {
        format!(
            "ExtractionOptions(preserve_layout={}, space_threshold={}, newline_threshold={}, \
             sort_by_position={}, detect_columns={}, column_threshold={}, \
             merge_hyphenated={}, track_space_decisions={})",
            self.inner.preserve_layout,
            self.inner.space_threshold,
            self.inner.newline_threshold,
            self.inner.sort_by_position,
            self.inner.detect_columns,
            self.inner.column_threshold,
            self.inner.merge_hyphenated,
            self.inner.track_space_decisions,
        )
    }
}

// ── LineBreakMode (F72) ───────────────────────────────────────────────────

/// Controls how line breaks are handled during plain text extraction.
#[pyclass(name = "LineBreakMode", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyLineBreakMode {
    pub inner: LineBreakMode,
}

#[pymethods]
impl PyLineBreakMode {
    #[classattr]
    const AUTO: Self = Self { inner: LineBreakMode::Auto };
    #[classattr]
    const PRESERVE_ALL: Self = Self { inner: LineBreakMode::PreserveAll };
    #[classattr]
    const NORMALIZE: Self = Self { inner: LineBreakMode::Normalize };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            LineBreakMode::Auto => "AUTO",
            LineBreakMode::PreserveAll => "PRESERVE_ALL",
            LineBreakMode::Normalize => "NORMALIZE",
        };
        format!("LineBreakMode.{}", name)
    }
}

// ── PlainTextConfig (F72) ─────────────────────────────────────────────────

/// Configuration for plain text extraction from PDF pages.
#[pyclass(name = "PlainTextConfig", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyPlainTextConfig {
    pub inner: PlainTextConfig,
}

#[pymethods]
impl PyPlainTextConfig {
    #[new]
    #[pyo3(signature = (
        space_threshold = 0.3,
        newline_threshold = 10.0,
        preserve_layout = false,
        line_break_mode = None,
    ))]
    fn new(
        space_threshold: f64,
        newline_threshold: f64,
        preserve_layout: bool,
        line_break_mode: Option<&PyLineBreakMode>,
    ) -> Self {
        let mode = line_break_mode.map(|m| m.inner).unwrap_or(LineBreakMode::Auto);
        Self {
            inner: PlainTextConfig {
                space_threshold,
                newline_threshold,
                preserve_layout,
                line_break_mode: mode,
            },
        }
    }

    /// Dense preset: lower thresholds for tightly-spaced text.
    #[staticmethod]
    fn dense() -> Self {
        Self { inner: PlainTextConfig::dense() }
    }

    /// Loose preset: higher thresholds for wide-spaced text.
    #[staticmethod]
    fn loose() -> Self {
        Self { inner: PlainTextConfig::loose() }
    }

    /// Layout-preserving preset.
    #[staticmethod]
    fn preserve_layout() -> Self {
        Self { inner: PlainTextConfig::preserve_layout() }
    }

    #[getter]
    fn space_threshold(&self) -> f64 {
        self.inner.space_threshold
    }

    #[getter]
    fn newline_threshold(&self) -> f64 {
        self.inner.newline_threshold
    }

    #[getter]
    fn preserve_layout_flag(&self) -> bool {
        self.inner.preserve_layout
    }

    #[getter]
    fn line_break_mode(&self) -> PyLineBreakMode {
        PyLineBreakMode { inner: self.inner.line_break_mode }
    }

    fn __repr__(&self) -> String {
        format!(
            "PlainTextConfig(space_threshold={}, newline_threshold={}, preserve_layout={})",
            self.inner.space_threshold, self.inner.newline_threshold, self.inner.preserve_layout,
        )
    }
}

// ── PlainTextResult (F72) ─────────────────────────────────────────────────

/// Result of plain text extraction from a PDF page.
#[pyclass(name = "PlainTextResult", frozen)]
pub struct PyPlainTextResult {
    pub inner: PlainTextResult,
}

#[pymethods]
impl PyPlainTextResult {
    /// Extracted text content.
    #[getter]
    fn text(&self) -> &str {
        &self.inner.text
    }

    /// Number of lines in the extracted text.
    #[getter]
    fn line_count(&self) -> usize {
        self.inner.line_count
    }

    /// Total character count of the extracted text.
    #[getter]
    fn char_count(&self) -> usize {
        self.inner.char_count
    }

    fn __repr__(&self) -> String {
        format!(
            "PlainTextResult(line_count={}, char_count={})",
            self.inner.line_count, self.inner.char_count,
        )
    }
}

// ── ColumnLayout (F73) ────────────────────────────────────────────────────

/// Multi-column layout configuration for PDF documents.
#[pyclass(name = "ColumnLayout", from_py_object)]
#[derive(Clone)]
pub struct PyColumnLayout {
    pub inner: ColumnLayout,
}

#[pymethods]
impl PyColumnLayout {
    /// Create a column layout with equal-width columns.
    #[new]
    fn new(column_count: usize, total_width: f64, column_gap: f64) -> Self {
        Self { inner: ColumnLayout::new(column_count, total_width, column_gap) }
    }

    /// Create a column layout with custom per-column widths.
    #[staticmethod]
    fn with_custom_widths(column_widths: Vec<f64>, column_gap: f64) -> Self {
        Self { inner: ColumnLayout::with_custom_widths(column_widths, column_gap) }
    }

    /// Number of columns.
    #[getter]
    fn column_count(&self) -> usize {
        self.inner.column_count()
    }

    /// Total layout width in points.
    #[getter]
    fn total_width(&self) -> f64 {
        self.inner.total_width()
    }

    /// Width of the column at the given 0-based index, or None if out of range.
    fn column_width(&self, index: usize) -> Option<f64> {
        self.inner.column_width(index)
    }

    fn __repr__(&self) -> String {
        format!(
            "ColumnLayout(column_count={}, total_width={})",
            self.inner.column_count(),
            self.inner.total_width(),
        )
    }
}

// ── ColumnOptions (F73) ───────────────────────────────────────────────────

/// Styling options for column layouts.
#[pyclass(name = "ColumnOptions", from_py_object)]
#[derive(Clone)]
pub struct PyColumnOptions {
    pub inner: ColumnOptions,
}

#[pymethods]
impl PyColumnOptions {
    #[new]
    #[pyo3(signature = (
        font = None,
        font_size = 10.0,
        line_height = 1.2,
        text_color = None,
        balance_columns = true,
        show_separators = false,
        separator_color = None,
        separator_width = 0.5,
    ))]
    fn new(
        font: Option<&PyFont>,
        font_size: f64,
        line_height: f64,
        text_color: Option<&PyColor>,
        balance_columns: bool,
        show_separators: bool,
        separator_color: Option<&PyColor>,
        separator_width: f64,
    ) -> Self {
        let mut opts = ColumnOptions::default();
        if let Some(f) = font {
            opts.font = f.inner.clone();
        }
        opts.font_size = font_size;
        opts.line_height = line_height;
        if let Some(c) = text_color {
            opts.text_color = c.inner;
        }
        opts.balance_columns = balance_columns;
        opts.show_separators = show_separators;
        if let Some(c) = separator_color {
            opts.separator_color = c.inner;
        }
        opts.separator_width = separator_width;
        Self { inner: opts }
    }

    fn __repr__(&self) -> String {
        format!(
            "ColumnOptions(font_size={}, line_height={}, balance_columns={})",
            self.inner.font_size, self.inner.line_height, self.inner.balance_columns,
        )
    }
}

// ── ColumnContent (F73) ───────────────────────────────────────────────────

/// Text content for flowing across columns.
#[pyclass(name = "ColumnContent", from_py_object)]
#[derive(Clone)]
pub struct PyColumnContent {
    pub inner: ColumnContent,
}

#[pymethods]
impl PyColumnContent {
    /// Create column content from a text string.
    #[new]
    fn new(text: &str) -> Self {
        Self { inner: ColumnContent::new(text) }
    }

    fn __repr__(&self) -> String {
        "ColumnContent(...)".to_string()
    }
}

// ── MatchType (F74) ───────────────────────────────────────────────────────

/// Type of text match found by the TextValidator.
#[pyclass(name = "MatchType", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyMatchType {
    pub inner: MatchType,
}

#[pymethods]
impl PyMatchType {
    #[classattr]
    const DATE: Self = Self { inner: MatchType::Date };
    #[classattr]
    const CONTRACT_NUMBER: Self = Self { inner: MatchType::ContractNumber };
    #[classattr]
    const PARTY_NAME: Self = Self { inner: MatchType::PartyName };
    #[classattr]
    const MONETARY_AMOUNT: Self = Self { inner: MatchType::MonetaryAmount };
    #[classattr]
    const LOCATION: Self = Self { inner: MatchType::Location };

    /// Create a custom match type with the given name.
    #[staticmethod]
    fn custom(name: &str) -> Self {
        Self { inner: MatchType::Custom(name.to_string()) }
    }

    fn __repr__(&self) -> String {
        match &self.inner {
            MatchType::Date => "MatchType.DATE".to_string(),
            MatchType::ContractNumber => "MatchType.CONTRACT_NUMBER".to_string(),
            MatchType::PartyName => "MatchType.PARTY_NAME".to_string(),
            MatchType::MonetaryAmount => "MatchType.MONETARY_AMOUNT".to_string(),
            MatchType::Location => "MatchType.LOCATION".to_string(),
            MatchType::Custom(name) => format!("MatchType.custom({:?})", name),
        }
    }
}

// ── TextMatch (F74) ───────────────────────────────────────────────────────

/// A specific match found by TextValidator.
#[pyclass(name = "TextMatch", frozen)]
pub struct PyTextMatch {
    pub inner: TextMatch,
}

#[pymethods]
impl PyTextMatch {
    /// The matched text string.
    #[getter]
    fn text(&self) -> &str {
        &self.inner.text
    }

    /// Byte offset of this match in the original text.
    #[getter]
    fn position(&self) -> usize {
        self.inner.position
    }

    /// Byte length of this match.
    #[getter]
    fn length(&self) -> usize {
        self.inner.length
    }

    /// Confidence score [0.0, 1.0] for this match.
    #[getter]
    fn confidence(&self) -> f64 {
        self.inner.confidence
    }

    /// The type of this match.
    #[getter]
    fn match_type(&self) -> PyMatchType {
        PyMatchType { inner: self.inner.match_type.clone() }
    }

    fn __repr__(&self) -> String {
        format!(
            "TextMatch(text={:?}, position={}, length={}, confidence={})",
            self.inner.text, self.inner.position, self.inner.length, self.inner.confidence,
        )
    }
}

// ── TextValidationResult (F74) ────────────────────────────────────────────

/// Result returned by TextValidator methods.
#[pyclass(name = "TextValidationResult", frozen)]
pub struct PyTextValidationResult {
    pub inner: TextValidationResult,
}

#[pymethods]
impl PyTextValidationResult {
    /// Whether any matches were found.
    #[getter]
    fn found(&self) -> bool {
        self.inner.found
    }

    /// List of all matches.
    #[getter]
    fn matches(&self) -> Vec<PyTextMatch> {
        self.inner
            .matches
            .iter()
            .map(|m| PyTextMatch { inner: m.clone() })
            .collect()
    }

    /// Overall confidence score [0.0, 1.0].
    #[getter]
    fn confidence(&self) -> f64 {
        self.inner.confidence
    }

    /// Additional metadata extracted during validation.
    #[getter]
    fn metadata(&self) -> std::collections::HashMap<String, String> {
        self.inner.metadata.clone()
    }

    fn __repr__(&self) -> String {
        format!(
            "TextValidationResult(found={}, matches={}, confidence={})",
            self.inner.found,
            self.inner.matches.len(),
            self.inner.confidence,
        )
    }
}

// ── TextValidator (F74) ───────────────────────────────────────────────────

/// Validates and searches text for contract elements like dates, amounts, etc.
#[pyclass(name = "TextValidator")]
pub struct PyTextValidator {
    inner: TextValidator,
}

#[pymethods]
impl PyTextValidator {
    #[new]
    fn new() -> Self {
        Self { inner: TextValidator::new() }
    }

    /// Search for a specific target string in text (case-insensitive).
    fn search_for_target(&self, text: &str, target: &str) -> PyTextValidationResult {
        PyTextValidationResult { inner: self.inner.search_for_target(text, target) }
    }

    /// Validate contract text: finds dates, amounts, party names, etc.
    fn validate_contract_text(&self, text: &str) -> PyTextValidationResult {
        PyTextValidationResult { inner: self.inner.validate_contract_text(text) }
    }

    /// Extract key information from contract text.
    ///
    /// Returns a dict mapping category names (e.g. "dates", "monetary_amounts",
    /// "organizations") to lists of matched strings.
    fn extract_key_info<'py>(
        &self,
        py: Python<'py>,
        text: &str,
    ) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
        use pyo3::types::{PyDict, PyList};

        let extracted = self.inner.extract_key_info(text);
        let dict = PyDict::new(py);
        for (key, values) in extracted {
            let list = PyList::new(py, values.iter().map(|v| v.as_str()))?;
            dict.set_item(key, list)?;
        }
        Ok(dict)
    }

    fn __repr__(&self) -> String {
        "TextValidator()".to_string()
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // F71
    m.add_class::<PyExtractionOptions>()?;
    // F72
    m.add_class::<PyLineBreakMode>()?;
    m.add_class::<PyPlainTextConfig>()?;
    m.add_class::<PyPlainTextResult>()?;
    // F73
    m.add_class::<PyColumnLayout>()?;
    m.add_class::<PyColumnOptions>()?;
    m.add_class::<PyColumnContent>()?;
    // F74
    m.add_class::<PyMatchType>()?;
    m.add_class::<PyTextMatch>()?;
    m.add_class::<PyTextValidationResult>()?;
    m.add_class::<PyTextValidator>()?;
    Ok(())
}
