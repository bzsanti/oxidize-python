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
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e))
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
    fn new() -> Self { Self { inner: oxidize_pdf::templates::TemplateContext::new() } }

    fn set(&mut self, key: &str, value: &str) {
        self.inner.set(key, value);
    }

    fn __repr__(&self) -> String { "TemplateContext(...)".to_string() }
}

#[pyclass(name = "TemplateRenderer")]
pub struct PyTemplateRenderer {
    pub inner: oxidize_pdf::templates::TemplateRenderer,
}

#[pymethods]
impl PyTemplateRenderer {
    #[new]
    fn new() -> Self { Self { inner: oxidize_pdf::templates::TemplateRenderer::new() } }

    fn render(&self, template: &str, ctx: &PyTemplateContext) -> PyResult<String> {
        self.inner.render(template, &ctx.inner)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
    }

    fn __repr__(&self) -> String { "TemplateRenderer(...)".to_string() }
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
    #[classattr] const A1B: Self = Self { inner: oxidize_pdf::pdfa::PdfALevel::A1b };
    #[classattr] const A2B: Self = Self { inner: oxidize_pdf::pdfa::PdfALevel::A2b };
    #[classattr] const A3B: Self = Self { inner: oxidize_pdf::pdfa::PdfALevel::A3b };

    fn __repr__(&self) -> String { "PdfALevel(...)".to_string() }
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
        Self { inner: oxidize_pdf::pdfa::PdfAValidator::new(level.inner) }
    }
    fn __repr__(&self) -> String { "PdfAValidator(...)".to_string() }
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

// ── Feature 40: Semantic Marking ──────────────────────────────────────────

#[pyclass(name = "EntityType", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyEntityType {
    _private: (),
}

#[pymethods]
impl PyEntityType {
    fn __repr__(&self) -> String { "EntityType(...)".to_string() }
}

// ── Feature 41: Dashboards/Charts ─────────────────────────────────────────

#[pyclass(name = "DashboardBuilder", unsendable)]
pub struct PyDashboardBuilder {
    pub inner: oxidize_pdf::dashboard::DashboardBuilder,
}

#[pymethods]
impl PyDashboardBuilder {
    #[new]
    fn new() -> Self { Self { inner: oxidize_pdf::dashboard::DashboardBuilder::new() } }
    fn __repr__(&self) -> String { "DashboardBuilder(...)".to_string() }
}

#[pyclass(name = "DashboardTheme", from_py_object)]
#[derive(Clone)]
pub struct PyDashboardTheme {
    pub inner: oxidize_pdf::dashboard::DashboardTheme,
}

#[pymethods]
impl PyDashboardTheme {
    #[staticmethod]
    fn corporate() -> Self { Self { inner: oxidize_pdf::dashboard::DashboardTheme::corporate() } }

    #[staticmethod]
    fn minimal() -> Self { Self { inner: oxidize_pdf::dashboard::DashboardTheme::minimal() } }

    fn __repr__(&self) -> String { "DashboardTheme(...)".to_string() }
}

#[pyclass(name = "KpiCard", from_py_object)]
#[derive(Clone)]
pub struct PyKpiCard {
    pub inner: oxidize_pdf::dashboard::KpiCard,
}

#[pymethods]
impl PyKpiCard {
    #[new]
    fn new(title: &str, value: &str) -> Self {
        Self { inner: oxidize_pdf::dashboard::KpiCard::new(title, value) }
    }
    fn __repr__(&self) -> String { "KpiCard(...)".to_string() }
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
    m.add_class::<PyMockOcrProvider>()?;
    m.add_class::<PyOcrEngine>()?;
    m.add_class::<PyBatchOptions>()?;
    m.add_class::<PyStreamingOptions>()?;
    m.add_class::<PyLazyDocument>()?;
    m.add_function(wrap_pyfunction!(validate_pdf, m)?)?;
    m.add_class::<PyPdfALevel>()?;
    m.add_class::<PyPdfAValidator>()?;
    m.add_function(wrap_pyfunction!(compare_pdfs, m)?)?;
    m.add_class::<PyEntityType>()?;
    m.add_class::<PyDashboardBuilder>()?;
    m.add_class::<PyDashboardTheme>()?;
    m.add_class::<PyKpiCard>()?;
    Ok(())
}
