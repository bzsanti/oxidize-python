//! Tier 8 bindings — Enterprise / Advanced features (30-41).

use pyo3::prelude::*;
use pyo3::types::PyDict;

use oxidize_pdf::structure::{StandardStructureType, StructTree, StructureElement};

use crate::errors::to_py_err;

// ── Feature 30: Tagged PDF ────────────────────────────────────────────────

#[pyclass(name = "StandardStructureType", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyStandardStructureType {
    pub inner: StandardStructureType,
}

#[pymethods]
impl PyStandardStructureType {
    #[classattr] const DOCUMENT: Self = Self { inner: StandardStructureType::Document };
    #[classattr] const PART: Self = Self { inner: StandardStructureType::Part };
    #[classattr] const SECT: Self = Self { inner: StandardStructureType::Sect };
    #[classattr] const DIV: Self = Self { inner: StandardStructureType::Div };
    #[classattr] const ART: Self = Self { inner: StandardStructureType::Art };
    #[classattr] const BLOCK_QUOTE: Self = Self { inner: StandardStructureType::BlockQuote };
    #[classattr] const CAPTION: Self = Self { inner: StandardStructureType::Caption };
    #[classattr] const TOC: Self = Self { inner: StandardStructureType::TOC };
    #[classattr] const INDEX: Self = Self { inner: StandardStructureType::Index };
    #[classattr] const P: Self = Self { inner: StandardStructureType::P };
    #[classattr] const H: Self = Self { inner: StandardStructureType::H };
    #[classattr] const H1: Self = Self { inner: StandardStructureType::H1 };
    #[classattr] const H2: Self = Self { inner: StandardStructureType::H2 };
    #[classattr] const H3: Self = Self { inner: StandardStructureType::H3 };
    #[classattr] const H4: Self = Self { inner: StandardStructureType::H4 };
    #[classattr] const H5: Self = Self { inner: StandardStructureType::H5 };
    #[classattr] const H6: Self = Self { inner: StandardStructureType::H6 };
    #[classattr] const L: Self = Self { inner: StandardStructureType::L };
    #[classattr] const LI: Self = Self { inner: StandardStructureType::LI };
    #[classattr] const TABLE: Self = Self { inner: StandardStructureType::Table };
    #[classattr] const TR: Self = Self { inner: StandardStructureType::TR };
    #[classattr] const TH: Self = Self { inner: StandardStructureType::TH };
    #[classattr] const TD: Self = Self { inner: StandardStructureType::TD };
    #[classattr] const THEAD: Self = Self { inner: StandardStructureType::THead };
    #[classattr] const TBODY: Self = Self { inner: StandardStructureType::TBody };
    #[classattr] const TFOOT: Self = Self { inner: StandardStructureType::TFoot };
    #[classattr] const SPAN: Self = Self { inner: StandardStructureType::Span };
    #[classattr] const QUOTE: Self = Self { inner: StandardStructureType::Quote };
    #[classattr] const NOTE: Self = Self { inner: StandardStructureType::Note };
    #[classattr] const REFERENCE: Self = Self { inner: StandardStructureType::Reference };
    #[classattr] const CODE: Self = Self { inner: StandardStructureType::Code };
    #[classattr] const LINK: Self = Self { inner: StandardStructureType::Link };
    #[classattr] const ANNOT: Self = Self { inner: StandardStructureType::Annot };
    #[classattr] const FIGURE: Self = Self { inner: StandardStructureType::Figure };
    #[classattr] const FORMULA: Self = Self { inner: StandardStructureType::Formula };
    #[classattr] const FORM: Self = Self { inner: StandardStructureType::Form };

    fn __repr__(&self) -> String {
        format!("StandardStructureType.{}", self.inner.as_pdf_name())
    }
}

#[pyclass(name = "StructureElement", from_py_object)]
#[derive(Clone)]
pub struct PyStructureElement {
    pub inner: StructureElement,
}

#[pymethods]
impl PyStructureElement {
    #[new]
    fn new(stype: &PyStandardStructureType) -> Self {
        Self { inner: StructureElement::new(stype.inner.clone()) }
    }

    #[staticmethod]
    fn custom(name: &str) -> Self {
        Self { inner: StructureElement::new_custom(name) }
    }

    fn with_language(self_: PyRef<'_, Self>, lang: &str) -> Self {
        Self { inner: self_.inner.clone().with_language(lang) }
    }

    fn with_alt_text(self_: PyRef<'_, Self>, alt: &str) -> Self {
        Self { inner: self_.inner.clone().with_alt_text(alt) }
    }

    fn with_actual_text(self_: PyRef<'_, Self>, text: &str) -> Self {
        Self { inner: self_.inner.clone().with_actual_text(text) }
    }

    fn with_title(self_: PyRef<'_, Self>, title: &str) -> Self {
        Self { inner: self_.inner.clone().with_title(title) }
    }

    fn add_mcid(&mut self, page_index: usize, mcid: u32) {
        self.inner.add_mcid(page_index, mcid);
    }

    fn __repr__(&self) -> String { "StructureElement(...)".to_string() }
}

#[pyclass(name = "StructTree")]
pub struct PyStructTree {
    pub inner: StructTree,
}

#[pymethods]
impl PyStructTree {
    #[new]
    fn new() -> Self { Self { inner: StructTree::new() } }

    fn set_root(&mut self, element: PyStructureElement) -> usize {
        self.inner.set_root(element.inner)
    }

    fn add_child(&mut self, parent_index: usize, element: PyStructureElement) -> PyResult<usize> {
        self.inner.add_child(parent_index, element.inner)
            .map_err(pyo3::exceptions::PyValueError::new_err)
    }

    #[getter]
    fn length(&self) -> usize { self.inner.len() }

    #[getter]
    fn is_empty(&self) -> bool { self.inner.is_empty() }

    fn __repr__(&self) -> String { format!("StructTree(len={})", self.inner.len()) }
}

// ── Feature 31: Coordinate Systems ────────────────────────────────────────

#[pyclass(name = "CoordinateSystem", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyCoordinateSystem {
    pub inner: oxidize_pdf::CoordinateSystem,
}

#[pymethods]
impl PyCoordinateSystem {
    #[classattr]
    const PDF_STANDARD: Self = Self { inner: oxidize_pdf::CoordinateSystem::PdfStandard };
    #[classattr]
    const SCREEN_SPACE: Self = Self { inner: oxidize_pdf::CoordinateSystem::ScreenSpace };

    fn __repr__(&self) -> String {
        match &self.inner {
            oxidize_pdf::CoordinateSystem::PdfStandard => "CoordinateSystem.PDF_STANDARD",
            oxidize_pdf::CoordinateSystem::ScreenSpace => "CoordinateSystem.SCREEN_SPACE",
            _ => "CoordinateSystem.CUSTOM",
        }.to_string()
    }
}

// ── Feature 32: Calibrated Colors ─────────────────────────────────────────

#[pyclass(name = "LabColorSpace", from_py_object)]
#[derive(Clone)]
pub struct PyLabColorSpace {
    pub inner: oxidize_pdf::graphics::lab_color::LabColorSpace,
}

#[pymethods]
impl PyLabColorSpace {
    #[staticmethod]
    fn d50() -> Self { Self { inner: oxidize_pdf::graphics::lab_color::LabColorSpace::d50() } }

    #[staticmethod]
    fn d65() -> Self { Self { inner: oxidize_pdf::graphics::lab_color::LabColorSpace::d65() } }

    fn __repr__(&self) -> String { "LabColorSpace(...)".to_string() }
}

// ── Feature 33: Templates ─────────────────────────────────────────────────

#[pyclass(name = "TemplateContext", from_py_object)]
#[derive(Clone)]
pub struct PyTemplateContext {
    pub inner: oxidize_pdf::templates::TemplateContext,
}

#[pymethods]
impl PyTemplateContext {
    #[new]
    fn new() -> Self {
        Self {
            inner: oxidize_pdf::templates::TemplateContext::new(),
        }
    }

    /// Set a string variable.
    fn set(&mut self, key: &str, value: &str) {
        self.inner.set(key, value);
    }

    /// Set a floating-point number variable.
    fn set_number(&mut self, key: &str, value: f64) {
        self.inner.set_number(key, value);
    }

    /// Set an integer variable.
    fn set_integer(&mut self, key: &str, value: i64) {
        self.inner.set_integer(key, value);
    }

    /// Set a boolean variable.
    fn set_boolean(&mut self, key: &str, value: bool) {
        self.inner.set_boolean(key, value);
    }

    /// Check if a variable is set.
    fn has(&self, name: &str) -> bool {
        self.inner.has(name)
    }

    /// Get all variable names.
    fn keys(&self) -> Vec<String> {
        self.inner.keys()
    }

    /// Remove all variables.
    fn clear(&mut self) {
        self.inner.clear();
    }

    fn __repr__(&self) -> String {
        let keys = self.inner.keys();
        if keys.is_empty() {
            "TemplateContext(keys=0)".to_string()
        } else {
            format!("TemplateContext(keys={}, names={:?})", keys.len(), keys)
        }
    }
}

#[pyclass(name = "TemplateRenderer")]
pub struct PyTemplateRenderer {
    pub inner: oxidize_pdf::templates::TemplateRenderer,
}

#[pymethods]
impl PyTemplateRenderer {
    #[new]
    fn new() -> Self {
        Self {
            inner: oxidize_pdf::templates::TemplateRenderer::new(),
        }
    }

    /// Render a template string with the given context.
    fn render(&self, template: &str, ctx: &PyTemplateContext) -> PyResult<String> {
        self.inner
            .render(template, &ctx.inner)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    /// Get the list of required variable names in a template.
    fn get_required_variables(&self, template: &str) -> PyResult<Vec<String>> {
        self.inner
            .get_required_variables(template)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    /// Validate a template string. Raises ValueError if invalid.
    fn validate_template(&self, template: &str) -> PyResult<()> {
        self.inner
            .validate_template(template)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    /// Check if a template string contains any placeholders.
    fn has_placeholders(&self, template: &str) -> bool {
        self.inner.has_placeholders(template)
    }

    /// Analyze a template and return detailed information about its placeholders.
    fn analyze_template(&self, template: &str) -> PyResult<PyTemplateAnalysis> {
        let analysis = self
            .inner
            .analyze_template(template)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        Ok(PyTemplateAnalysis {
            total_placeholders: analysis.total_placeholders,
            unique_variables: analysis.unique_variables,
            variable_names: analysis.variable_names,
            placeholders: analysis
                .placeholders
                .into_iter()
                .map(|p| PyPlaceholder {
                    full_text: p.full_text,
                    variable_name: p.variable_name,
                    start: p.start,
                    end: p.end,
                })
                .collect(),
        })
    }

    fn __repr__(&self) -> String {
        "TemplateRenderer()".to_string()
    }
}

// ── TemplateParser ───────────────────────────────────────────────────────

/// Low-level template parser for extracting placeholders.
#[pyclass(name = "TemplateParser")]
pub struct PyTemplateParser {
    inner: oxidize_pdf::templates::TemplateParser,
}

#[pymethods]
impl PyTemplateParser {
    #[new]
    fn new() -> Self {
        Self {
            inner: oxidize_pdf::templates::TemplateParser::new(),
        }
    }

    /// Parse a template and return all placeholders found.
    fn parse(&self, template: &str) -> PyResult<Vec<PyPlaceholder>> {
        let placeholders = self
            .inner
            .parse(template)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        Ok(placeholders
            .into_iter()
            .map(|p| PyPlaceholder {
                full_text: p.full_text,
                variable_name: p.variable_name,
                start: p.start,
                end: p.end,
            })
            .collect())
    }

    /// Get unique variable names from a template.
    fn get_variable_names(&self, template: &str) -> PyResult<Vec<String>> {
        self.inner
            .get_variable_names(template)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    /// Check if a template string contains any placeholders.
    fn has_placeholders(&self, template: &str) -> bool {
        self.inner.has_placeholders(template)
    }

    /// Count the number of placeholders in a template.
    fn count_placeholders(&self, template: &str) -> usize {
        self.inner.count_placeholders(template)
    }

    fn __repr__(&self) -> String {
        "TemplateParser()".to_string()
    }
}

// ── TemplateAnalysis + Placeholder ───────────────────────────────────────

/// Result of analyzing a template — contains placeholder metadata.
#[pyclass(name = "TemplateAnalysis", frozen)]
pub struct PyTemplateAnalysis {
    #[pyo3(get)]
    pub total_placeholders: usize,
    #[pyo3(get)]
    pub unique_variables: usize,
    #[pyo3(get)]
    pub variable_names: Vec<String>,
    #[pyo3(get)]
    pub placeholders: Vec<PyPlaceholder>,
}

#[pymethods]
impl PyTemplateAnalysis {
    fn __repr__(&self) -> String {
        format!(
            "TemplateAnalysis(placeholders={}, unique={})",
            self.total_placeholders, self.unique_variables
        )
    }
}

/// A single placeholder found in a template string.
#[pyclass(name = "Placeholder", frozen, skip_from_py_object)]
#[derive(Clone)]
pub struct PyPlaceholder {
    #[pyo3(get)]
    pub full_text: String,
    #[pyo3(get)]
    pub variable_name: String,
    #[pyo3(get)]
    pub start: usize,
    #[pyo3(get)]
    pub end: usize,
}

#[pymethods]
impl PyPlaceholder {
    fn __repr__(&self) -> String {
        format!("Placeholder(name='{}', pos={})", self.variable_name, self.start)
    }
}

// ── Feature 34: OCR ───────────────────────────────────────────────────────

#[pyclass(name = "MockOcrProvider")]
pub struct PyMockOcrProvider {
    pub inner: oxidize_pdf::MockOcrProvider,
}

#[pymethods]
impl PyMockOcrProvider {
    #[new]
    fn new() -> Self { Self { inner: oxidize_pdf::MockOcrProvider::new() } }
    fn __repr__(&self) -> String { "MockOcrProvider(...)".to_string() }
}

#[pyclass(name = "OcrEngine", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyOcrEngine {
    pub inner: oxidize_pdf::OcrEngine,
}

#[pymethods]
impl PyOcrEngine {
    #[classattr]
    const TESSERACT: Self = Self { inner: oxidize_pdf::OcrEngine::Tesseract };
    #[classattr]
    const MOCK: Self = Self { inner: oxidize_pdf::OcrEngine::Mock };

    fn __repr__(&self) -> String { "OcrEngine(...)".to_string() }
}

// ── Feature 35: Batch Processing ──────────────────────────────────────────

#[pyclass(name = "BatchOptions", from_py_object)]
#[derive(Clone)]
pub struct PyBatchOptions {
    pub inner: oxidize_pdf::batch::BatchOptions,
}

#[pymethods]
impl PyBatchOptions {
    #[new]
    #[pyo3(signature = (parallelism=None, stop_on_error=None))]
    fn new(parallelism: Option<usize>, stop_on_error: Option<bool>) -> Self {
        let mut opts = oxidize_pdf::batch::BatchOptions::default();
        if let Some(p) = parallelism { opts.parallelism = p; }
        if let Some(s) = stop_on_error { opts.stop_on_error = s; }
        Self { inner: opts }
    }
    fn __repr__(&self) -> String {
        format!("BatchOptions(parallelism={})", self.inner.parallelism)
    }
}

// ── Feature 36: Streaming/Lazy ────────────────────────────────────────────

#[pyclass(name = "StreamingOptions", from_py_object)]
#[derive(Clone)]
pub struct PyStreamingOptions {
    pub inner: oxidize_pdf::streaming::StreamingOptions,
}

#[pymethods]
impl PyStreamingOptions {
    #[staticmethod]
    fn minimal_memory() -> Self {
        Self { inner: oxidize_pdf::streaming::StreamingOptions::minimal_memory() }
    }

    #[staticmethod]
    fn fast_processing() -> Self {
        Self { inner: oxidize_pdf::streaming::StreamingOptions::fast_processing() }
    }

    fn __repr__(&self) -> String { "StreamingOptions(...)".to_string() }
}

#[pyclass(name = "LazyDocument", unsendable)]
pub struct PyLazyDocument {
    pub inner: oxidize_pdf::memory::LazyDocument<std::fs::File>,
}

#[pymethods]
impl PyLazyDocument {
    #[staticmethod]
    fn open(path: &str) -> PyResult<Self> {
        let doc = oxidize_pdf::memory::LazyDocument::open(
            path, oxidize_pdf::memory::MemoryOptions::default(),
        ).map_err(to_py_err)?;
        Ok(Self { inner: doc })
    }

    #[getter]
    fn page_count(&self) -> u32 { self.inner.page_count() }

    fn __repr__(&self) -> String {
        format!("LazyDocument(pages={})", self.inner.page_count())
    }
}

// ── Feature 37: PDF Recovery ──────────────────────────────────────────────

#[pyfunction]
fn validate_pdf<'py>(path: &str, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
    let result = oxidize_pdf::recovery::validate_pdf(path).map_err(to_py_err)?;
    let dict = PyDict::new(py);
    dict.set_item("is_valid", result.is_valid)?;
    dict.set_item("error_count", result.errors.len())?;
    dict.set_item("warning_count", result.warnings.len())?;
    Ok(dict)
}

// ── Feature 38: PDF/A Validation ──────────────────────────────────────────

#[pyclass(name = "PdfALevel", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyPdfALevel {
    pub inner: oxidize_pdf::pdfa::PdfALevel,
}

#[pymethods]
impl PyPdfALevel {
    #[classattr]
    const A1A: Self = Self { inner: oxidize_pdf::pdfa::PdfALevel::A1a };
    #[classattr]
    const A1B: Self = Self { inner: oxidize_pdf::pdfa::PdfALevel::A1b };
    #[classattr]
    const A2A: Self = Self { inner: oxidize_pdf::pdfa::PdfALevel::A2a };
    #[classattr]
    const A2B: Self = Self { inner: oxidize_pdf::pdfa::PdfALevel::A2b };
    #[classattr]
    const A2U: Self = Self { inner: oxidize_pdf::pdfa::PdfALevel::A2u };
    #[classattr]
    const A3A: Self = Self { inner: oxidize_pdf::pdfa::PdfALevel::A3a };
    #[classattr]
    const A3B: Self = Self { inner: oxidize_pdf::pdfa::PdfALevel::A3b };
    #[classattr]
    const A3U: Self = Self { inner: oxidize_pdf::pdfa::PdfALevel::A3u };

    fn __repr__(&self) -> String {
        format!("PdfALevel.{}", self.inner)
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

/// PDF/A conformance level indicating the degree of compliance.
///
/// - **A** (Accessible): Full compliance including tagged structure and Unicode mapping.
/// - **B** (Basic): Visual appearance preservation only.
/// - **U** (Unicode): Basic compliance plus Unicode character mapping.
#[pyclass(name = "PdfAConformance", frozen, skip_from_py_object)]
#[derive(Clone)]
pub struct PyPdfAConformance {
    pub inner: oxidize_pdf::pdfa::PdfAConformance,
}

#[pymethods]
impl PyPdfAConformance {
    #[classattr]
    const A: Self = Self {
        inner: oxidize_pdf::pdfa::PdfAConformance::A,
    };
    #[classattr]
    const B: Self = Self {
        inner: oxidize_pdf::pdfa::PdfAConformance::B,
    };
    #[classattr]
    const U: Self = Self {
        inner: oxidize_pdf::pdfa::PdfAConformance::U,
    };

    fn __repr__(&self) -> String {
        format!("PdfAConformance.{}", self.inner)
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

/// Result of PDF/A validation — contains errors, warnings, and validity status.
#[pyclass(name = "PdfAValidationResult", frozen)]
pub struct PyPdfAValidationResult {
    #[pyo3(get)]
    pub is_valid: bool,
    #[pyo3(get)]
    pub errors: Vec<String>,
    #[pyo3(get)]
    pub warnings: Vec<String>,
}

#[pymethods]
impl PyPdfAValidationResult {
    /// Number of validation errors found.
    #[getter]
    fn error_count(&self) -> usize {
        self.errors.len()
    }

    /// Number of validation warnings found.
    #[getter]
    fn warning_count(&self) -> usize {
        self.warnings.len()
    }

    fn __repr__(&self) -> String {
        format!(
            "PdfAValidationResult(valid={}, errors={}, warnings={})",
            self.is_valid,
            self.errors.len(),
            self.warnings.len()
        )
    }
}

#[pyclass(name = "PdfAValidator", from_py_object)]
#[derive(Clone)]
pub struct PyPdfAValidator {
    pub inner: oxidize_pdf::pdfa::PdfAValidator,
}

#[pymethods]
impl PyPdfAValidator {
    #[new]
    fn new(level: &PyPdfALevel) -> Self {
        Self {
            inner: oxidize_pdf::pdfa::PdfAValidator::new(level.inner),
        }
    }

    /// Validate PDF data (bytes) against the configured PDF/A level.
    fn validate_bytes(&self, data: &[u8]) -> PyResult<PyPdfAValidationResult> {
        let cursor = std::io::Cursor::new(data.to_vec());
        let mut reader = oxidize_pdf::PdfReader::new(cursor).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Failed to parse PDF: {e}"))
        })?;
        let result = self.inner.validate(&mut reader).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Validation failed: {e}"))
        })?;
        Ok(PyPdfAValidationResult {
            is_valid: result.is_valid(),
            errors: result.errors().iter().map(|e| e.to_string()).collect(),
            warnings: result.warnings().iter().map(|w| w.to_string()).collect(),
        })
    }

    /// Set whether to collect all errors (true) or stop at first error (false).
    fn collect_all_errors(self_: PyRef<'_, Self>, collect: bool) -> Self {
        Self {
            inner: self_.inner.clone().collect_all_errors(collect),
        }
    }

    /// Get the configured PDF/A level.
    #[getter]
    fn level(&self) -> PyPdfALevel {
        PyPdfALevel {
            inner: self.inner.level(),
        }
    }

    fn __repr__(&self) -> String {
        format!("PdfAValidator(level={})", self.inner.level())
    }
}

// ── Feature 39: PDF Comparison ────────────────────────────────────────────

#[pyfunction]
fn compare_pdfs<'py>(generated: &[u8], reference: &[u8], py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
    let result = oxidize_pdf::verification::comparators::compare_pdfs(generated, reference)
        .map_err(to_py_err)?;
    let dict = PyDict::new(py);
    dict.set_item("structurally_equivalent", result.structurally_equivalent)?;
    dict.set_item("content_equivalent", result.content_equivalent)?;
    dict.set_item("similarity_score", result.similarity_score)?;
    dict.set_item("difference_count", result.differences.len())?;
    Ok(dict)
}

// ── Feature 41: Dashboards/Charts ─────────────────────────────────────────

// ── TrendDirection ───────────────────────────────────────────────────────

/// Trend direction for KPI cards.
#[pyclass(name = "TrendDirection", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTrendDirection {
    pub inner: oxidize_pdf::dashboard::TrendDirection,
}

#[pymethods]
impl PyTrendDirection {
    #[classattr]
    const UP: Self = Self {
        inner: oxidize_pdf::dashboard::TrendDirection::Up,
    };
    #[classattr]
    const DOWN: Self = Self {
        inner: oxidize_pdf::dashboard::TrendDirection::Down,
    };
    #[classattr]
    const FLAT: Self = Self {
        inner: oxidize_pdf::dashboard::TrendDirection::Flat,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            oxidize_pdf::dashboard::TrendDirection::Up => "UP",
            oxidize_pdf::dashboard::TrendDirection::Down => "DOWN",
            oxidize_pdf::dashboard::TrendDirection::Flat => "FLAT",
        };
        format!("TrendDirection.{name}")
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

// ── KpiCard ──────────────────────────────────────────────────────────────

#[pyclass(name = "KpiCard", from_py_object)]
#[derive(Clone)]
pub struct PyKpiCard {
    pub inner: oxidize_pdf::dashboard::KpiCard,
}

#[pymethods]
impl PyKpiCard {
    #[new]
    fn new(title: &str, value: &str) -> Self {
        Self {
            inner: oxidize_pdf::dashboard::KpiCard::new(title, value),
        }
    }

    /// Set trend indicator with change percentage and direction.
    fn with_trend(self_: PyRef<'_, Self>, change: f64, direction: &PyTrendDirection) -> Self {
        Self {
            inner: self_.inner.clone().with_trend(change, direction.inner),
        }
    }

    /// Set subtitle text below the value.
    fn with_subtitle(self_: PyRef<'_, Self>, subtitle: &str) -> Self {
        Self {
            inner: self_.inner.clone().with_subtitle(subtitle),
        }
    }

    /// Set sparkline data for a mini chart.
    fn with_sparkline(self_: PyRef<'_, Self>, data: Vec<f64>) -> Self {
        Self {
            inner: self_.inner.clone().with_sparkline(data),
        }
    }

    /// Set icon name for the KPI card.
    fn with_icon(self_: PyRef<'_, Self>, icon: &str) -> Self {
        Self {
            inner: self_.inner.clone().with_icon(icon),
        }
    }

    fn __repr__(&self) -> String {
        "KpiCard(...)".to_string()
    }
}

// ── DashboardTheme ───────────────────────────────────────────────────────

#[pyclass(name = "DashboardTheme", from_py_object)]
#[derive(Clone)]
pub struct PyDashboardTheme {
    pub inner: oxidize_pdf::dashboard::DashboardTheme,
}

#[pymethods]
impl PyDashboardTheme {
    #[staticmethod]
    fn corporate() -> Self {
        Self {
            inner: oxidize_pdf::dashboard::DashboardTheme::corporate(),
        }
    }

    #[staticmethod]
    fn minimal() -> Self {
        Self {
            inner: oxidize_pdf::dashboard::DashboardTheme::minimal(),
        }
    }

    #[staticmethod]
    fn dark() -> Self {
        Self {
            inner: oxidize_pdf::dashboard::DashboardTheme::dark(),
        }
    }

    #[staticmethod]
    fn colorful() -> Self {
        Self {
            inner: oxidize_pdf::dashboard::DashboardTheme::colorful(),
        }
    }

    fn __repr__(&self) -> String {
        "DashboardTheme(...)".to_string()
    }
}

// ── DashboardBuilder ─────────────────────────────────────────────────────

/// Dashboard builder. Accumulates configuration and builds on `build_to_page()`.
///
/// The Rust core uses a consuming builder pattern (`fn title(self) -> Self`),
/// which is incompatible with PyO3's `PyRef`. This wrapper stores config fields
/// and constructs the Rust builder only when `build_to_page()` is called.
#[pyclass(name = "DashboardBuilder", skip_from_py_object)]
#[derive(Clone)]
pub struct PyDashboardBuilder {
    title: Option<String>,
    subtitle: Option<String>,
    theme: Option<oxidize_pdf::dashboard::DashboardTheme>,
    author: Option<String>,
    kpi_rows: Vec<Vec<oxidize_pdf::dashboard::KpiCard>>,
}

#[pymethods]
impl PyDashboardBuilder {
    #[new]
    fn new() -> Self {
        Self {
            title: None,
            subtitle: None,
            theme: None,
            author: None,
            kpi_rows: Vec::new(),
        }
    }

    /// Set dashboard title.
    fn title(self_: PyRef<'_, Self>, title: &str) -> Self {
        let mut new = self_.clone();
        new.title = Some(title.to_string());
        new
    }

    /// Set dashboard subtitle.
    fn subtitle(self_: PyRef<'_, Self>, subtitle: &str) -> Self {
        let mut new = self_.clone();
        new.subtitle = Some(subtitle.to_string());
        new
    }

    /// Set dashboard theme.
    fn theme(self_: PyRef<'_, Self>, theme: &PyDashboardTheme) -> Self {
        let mut new = self_.clone();
        new.theme = Some(theme.inner.clone());
        new
    }

    /// Set dashboard author.
    fn author(self_: PyRef<'_, Self>, author: &str) -> Self {
        let mut new = self_.clone();
        new.author = Some(author.to_string());
        new
    }

    /// Add a row of KPI cards.
    fn add_kpi_row(self_: PyRef<'_, Self>, cards: Vec<PyKpiCard>) -> Self {
        let mut new = self_.clone();
        new.kpi_rows
            .push(cards.into_iter().map(|c| c.inner).collect());
        new
    }

    /// Build the dashboard and render it onto a page.
    fn build_to_page(&self, page: &mut crate::page::PyPage) -> PyResult<()> {
        let mut builder = oxidize_pdf::dashboard::DashboardBuilder::new();
        if let Some(ref t) = self.title {
            builder = builder.title(t.as_str());
        }
        if let Some(ref s) = self.subtitle {
            builder = builder.subtitle(s.as_str());
        }
        if let Some(ref theme) = self.theme {
            builder = builder.theme(theme.clone());
        }
        if let Some(ref a) = self.author {
            builder = builder.author(a.as_str());
        }
        for row in &self.kpi_rows {
            builder = builder.add_kpi_row(row.clone());
        }
        let dashboard = builder.build().map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Dashboard build failed: {e}"))
        })?;
        dashboard.render_to_page(&mut page.inner).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Dashboard render failed: {e}"))
        })?;
        Ok(())
    }

    /// Get the configured title, or None if not set.
    #[getter(get_title)]
    fn _get_title(&self) -> Option<String> {
        self.title.clone()
    }

    /// Get the configured subtitle, or None if not set.
    #[getter(get_subtitle)]
    fn _get_subtitle(&self) -> Option<String> {
        self.subtitle.clone()
    }

    /// Get the configured author, or None if not set.
    #[getter(get_author)]
    fn _get_author(&self) -> Option<String> {
        self.author.clone()
    }

    /// Get the number of KPI rows added.
    #[getter]
    fn kpi_row_count(&self) -> usize {
        self.kpi_rows.len()
    }

    fn __repr__(&self) -> String {
        let title = self.title.as_deref().unwrap_or("(untitled)");
        format!("DashboardBuilder(title='{title}')")
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyStandardStructureType>()?;
    m.add_class::<PyStructureElement>()?;
    m.add_class::<PyStructTree>()?;
    m.add_class::<PyCoordinateSystem>()?;
    m.add_class::<PyLabColorSpace>()?;
    m.add_class::<PyTemplateContext>()?;
    m.add_class::<PyTemplateRenderer>()?;
    m.add_class::<PyTemplateParser>()?;
    m.add_class::<PyTemplateAnalysis>()?;
    m.add_class::<PyPlaceholder>()?;
    m.add_class::<PyMockOcrProvider>()?;
    m.add_class::<PyOcrEngine>()?;
    m.add_class::<PyBatchOptions>()?;
    m.add_class::<PyStreamingOptions>()?;
    m.add_class::<PyLazyDocument>()?;
    m.add_function(wrap_pyfunction!(validate_pdf, m)?)?;
    m.add_class::<PyPdfALevel>()?;
    m.add_class::<PyPdfAConformance>()?;
    m.add_class::<PyPdfAValidationResult>()?;
    m.add_class::<PyPdfAValidator>()?;
    m.add_function(wrap_pyfunction!(compare_pdfs, m)?)?;
    m.add_class::<PyTrendDirection>()?;
    m.add_class::<PyKpiCard>()?;
    m.add_class::<PyDashboardTheme>()?;
    m.add_class::<PyDashboardBuilder>()?;
    Ok(())
}
