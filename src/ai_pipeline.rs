//! AI/ML Pipeline bindings — Feature 59
//!
//! Wraps `oxidize_pdf::ai` and `oxidize_pdf::pipeline` for Python:
//! document chunking, markdown export, element partitioning, and RAG chunks.

use pyo3::prelude::*;

use oxidize_pdf::ai::{
    ChunkExporter, DetectedLanguage, DocumentChunk, DocumentChunker, JsonExporter, JsonOptions,
    MarkdownExporter, MarkdownOptions, TokenEfficientExporter,
};
use oxidize_pdf::pipeline::{
    ContentTypeFlags, ContextFormat, ContextMode, DocumentSource, Element, ElementBBox,
    ExtractionProfile, HybridChunkConfig, MergePolicy, PageRegion, PartitionConfig, RagChunk,
    ReadingOrderStrategy, RichCell, SemanticChunkConfig, TableStructure,
};

use crate::errors::to_py_err;

fn pdf_err_to_py(err: oxidize_pdf::PdfError) -> PyErr {
    to_py_err(err)
}

// ── PyDetectedLanguage ─────────────────────────────────────────────────────

/// A language detected for a chunk or aggregated over a document.
///
/// `code` is the ISO 639-3 code (e.g. `"eng"`, `"spa"`, `"cmn"`). Short or
/// ambiguous text can yield an unreliable detection with an effectively-random
/// code; gate routing on `reliable` (and `confidence`).
#[pyclass(name = "DetectedLanguage", frozen)]
pub struct PyDetectedLanguage {
    pub inner: DetectedLanguage,
}

#[pymethods]
impl PyDetectedLanguage {
    /// ISO 639-3 language code (e.g. "eng", "spa").
    #[getter]
    fn code(&self) -> &str {
        &self.inner.code
    }

    /// Detector confidence in `[0.0, 1.0]`.
    #[getter]
    fn confidence(&self) -> f32 {
        self.inner.confidence
    }

    /// Whether the detector considers this detection reliable.
    #[getter]
    fn reliable(&self) -> bool {
        self.inner.reliable
    }

    fn __repr__(&self) -> String {
        format!(
            "DetectedLanguage(code={:?}, confidence={:.4}, reliable={})",
            self.inner.code, self.inner.confidence, self.inner.reliable,
        )
    }
}

// ── PyDocumentChunk ────────────────────────────────────────────────────────

/// A chunk of a PDF document suitable for LLM processing.
#[pyclass(name = "DocumentChunk", frozen)]
pub struct PyDocumentChunk {
    pub inner: DocumentChunk,
}

#[pymethods]
impl PyDocumentChunk {
    /// Unique identifier for this chunk (e.g., "chunk_0").
    #[getter]
    fn id(&self) -> &str {
        &self.inner.id
    }

    /// The text content of this chunk.
    #[getter]
    fn content(&self) -> &str {
        &self.inner.content
    }

    /// Estimated number of tokens in this chunk.
    #[getter]
    fn tokens(&self) -> usize {
        self.inner.tokens
    }

    /// Page numbers where this chunk's content appears (1-indexed).
    #[getter]
    fn page_numbers(&self) -> Vec<usize> {
        self.inner.page_numbers.clone()
    }

    /// Index of this chunk in the sequence (0-indexed).
    #[getter]
    fn chunk_index(&self) -> usize {
        self.inner.chunk_index
    }

    /// Detected language for this chunk, or `None` if language detection did not
    /// run (`DocumentChunker.with_language_detection(True)`).
    #[getter]
    fn language(&self) -> Option<PyDetectedLanguage> {
        self.inner
            .metadata
            .language
            .clone()
            .map(|inner| PyDetectedLanguage { inner })
    }

    fn __repr__(&self) -> String {
        format!(
            "DocumentChunk(id={:?}, tokens={}, chunk_index={})",
            self.inner.id, self.inner.tokens, self.inner.chunk_index,
        )
    }
}

// ── PyDocumentChunker ──────────────────────────────────────────────────────

/// Configurable document chunker for splitting PDFs into LLM-friendly pieces.
#[pyclass(name = "DocumentChunker")]
pub struct PyDocumentChunker {
    inner: DocumentChunker,
}

#[pymethods]
impl PyDocumentChunker {
    #[new]
    fn new(chunk_size: usize, overlap: usize) -> Self {
        Self { inner: DocumentChunker::new(chunk_size, overlap) }
    }

    /// Create a default chunker (512 tokens, 50 overlap).
    #[staticmethod]
    fn default() -> Self {
        Self { inner: DocumentChunker::default() }
    }

    /// Enable per-chunk language detection (ISO 639-3 via `whatlang`).
    ///
    /// When enabled, each chunk's `language` is populated during `chunk_text`.
    /// Disabled by default.
    fn with_language_detection(&self, enabled: bool) -> Self {
        Self { inner: self.inner.clone().with_language_detection(enabled) }
    }

    /// Chunk a text string into fixed-size pieces with overlap.
    fn chunk_text(&self, text: &str) -> PyResult<Vec<PyDocumentChunk>> {
        let chunks = self.inner.chunk_text(text).map_err(pdf_err_to_py)?;
        Ok(chunks.into_iter().map(|c| PyDocumentChunk { inner: c }).collect())
    }

    /// Estimate the number of tokens in a text string.
    #[staticmethod]
    fn estimate_tokens(text: &str) -> usize {
        DocumentChunker::estimate_tokens(text)
    }

    /// Dominant language across chunks carrying a detected language, weighted by
    /// chunk content length. Returns `None` if no chunk has a detected language.
    #[staticmethod]
    fn document_language(chunks: Vec<PyRef<PyDocumentChunk>>) -> Option<PyDetectedLanguage> {
        let owned: Vec<DocumentChunk> = chunks.iter().map(|c| c.inner.clone()).collect();
        DocumentChunker::document_language(&owned).map(|inner| PyDetectedLanguage { inner })
    }

    fn __repr__(&self) -> String {
        "DocumentChunker(...)".to_string()
    }
}

// ── PyMarkdownOptions ──────────────────────────────────────────────────────

/// Configuration options for Markdown export.
#[pyclass(name = "MarkdownOptions", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyMarkdownOptions {
    pub inner: MarkdownOptions,
}

#[pymethods]
impl PyMarkdownOptions {
    #[new]
    fn new(include_metadata: bool, include_page_numbers: bool) -> Self {
        Self {
            inner: MarkdownOptions { include_metadata, include_page_numbers },
        }
    }

    #[getter]
    fn include_metadata(&self) -> bool {
        self.inner.include_metadata
    }

    #[getter]
    fn include_page_numbers(&self) -> bool {
        self.inner.include_page_numbers
    }

    fn __repr__(&self) -> String {
        format!(
            "MarkdownOptions(include_metadata={}, include_page_numbers={})",
            self.inner.include_metadata, self.inner.include_page_numbers,
        )
    }
}

// ── PyMarkdownExporter ─────────────────────────────────────────────────────

/// Exporter for converting PDF content to Markdown format.
#[pyclass(name = "MarkdownExporter")]
pub struct PyMarkdownExporter {
    inner: MarkdownExporter,
}

#[pymethods]
impl PyMarkdownExporter {
    #[new]
    fn new(options: &PyMarkdownOptions) -> Self {
        Self { inner: MarkdownExporter::new(options.inner.clone()) }
    }

    /// Create a Markdown exporter with default options.
    #[staticmethod]
    fn default() -> Self {
        Self { inner: MarkdownExporter::default() }
    }

    /// Export text using the configured options.
    fn export(&self, text: &str) -> PyResult<String> {
        self.inner.export(text).map_err(pdf_err_to_py)
    }

    /// Export plain text to Markdown format (static convenience method).
    #[staticmethod]
    fn export_text(text: &str) -> PyResult<String> {
        MarkdownExporter::export_text(text).map_err(pdf_err_to_py)
    }

    fn __repr__(&self) -> String {
        "MarkdownExporter(...)".to_string()
    }
}

// ── PyTokenEfficientExporter ───────────────────────────────────────────────

/// Token-efficient, tabular serializer for RAG chunks (upstream #291).
///
/// Declares the column names once in a header line, then emits one tab-separated
/// row per chunk — roughly halving the serialized-token count versus JSON while
/// staying fully round-trippable via `parse_chunks`.
#[pyclass(name = "TokenEfficientExporter")]
pub struct PyTokenEfficientExporter {
    inner: TokenEfficientExporter,
}

#[pymethods]
impl PyTokenEfficientExporter {
    #[new]
    fn new() -> Self {
        Self { inner: TokenEfficientExporter::new() }
    }

    /// Serialize chunks to the token-efficient tabular format.
    fn export_chunks(&self, chunks: Vec<PyRef<PyDocumentChunk>>) -> PyResult<String> {
        let owned: Vec<DocumentChunk> = chunks.iter().map(|c| c.inner.clone()).collect();
        self.inner.export_chunks(&owned).map_err(pdf_err_to_py)
    }

    /// Parse a token-efficient document back into chunks (inverse of
    /// `export_chunks`). Raises on a wrong version marker, wrong header, or a row
    /// whose column count does not match the header.
    #[staticmethod]
    fn parse_chunks(input: &str) -> PyResult<Vec<PyDocumentChunk>> {
        TokenEfficientExporter::parse_chunks(input)
            .map(|v| v.into_iter().map(|inner| PyDocumentChunk { inner }).collect())
            .map_err(pdf_err_to_py)
    }

    fn __repr__(&self) -> String {
        "TokenEfficientExporter()".to_string()
    }
}

// ── PyJsonExporter ─────────────────────────────────────────────────────────

/// Exporter for converting PDF content and RAG chunks to JSON.
#[pyclass(name = "JsonExporter")]
pub struct PyJsonExporter {
    inner: JsonExporter,
}

#[pymethods]
impl PyJsonExporter {
    #[new]
    #[pyo3(signature = (pretty_print = true, include_chunks = false))]
    fn new(pretty_print: bool, include_chunks: bool) -> Self {
        Self { inner: JsonExporter::new(JsonOptions { pretty_print, include_chunks }) }
    }

    /// Create a JSON exporter with default options (pretty-printed).
    #[staticmethod]
    fn default() -> Self {
        Self { inner: JsonExporter::default() }
    }

    /// Export text to a simple JSON document using the configured options.
    fn export(&self, text: &str) -> PyResult<String> {
        self.inner.export(text).map_err(pdf_err_to_py)
    }

    /// Serialize chunks to a structured `chunked_document` JSON object.
    fn export_chunks(&self, chunks: Vec<PyRef<PyDocumentChunk>>) -> PyResult<String> {
        let owned: Vec<DocumentChunk> = chunks.iter().map(|c| c.inner.clone()).collect();
        self.inner.export_chunks(&owned).map_err(pdf_err_to_py)
    }

    fn __repr__(&self) -> String {
        "JsonExporter(...)".to_string()
    }
}

// ── PyExtractionProfile ────────────────────────────────────────────────────

/// Pre-configured extraction profiles for different document types.
#[pyclass(name = "ExtractionProfile", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyExtractionProfile {
    pub inner: ExtractionProfile,
}

#[pymethods]
impl PyExtractionProfile {
    #[classattr]
    const STANDARD: Self = Self { inner: ExtractionProfile::Standard };
    #[classattr]
    const ACADEMIC: Self = Self { inner: ExtractionProfile::Academic };
    #[classattr]
    const FORM: Self = Self { inner: ExtractionProfile::Form };
    #[classattr]
    const GOVERNMENT: Self = Self { inner: ExtractionProfile::Government };
    #[classattr]
    const DENSE: Self = Self { inner: ExtractionProfile::Dense };
    #[classattr]
    const PRESENTATION: Self = Self { inner: ExtractionProfile::Presentation };
    #[classattr]
    const RAG: Self = Self { inner: ExtractionProfile::Rag };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            ExtractionProfile::Standard => "STANDARD",
            ExtractionProfile::Academic => "ACADEMIC",
            ExtractionProfile::Form => "FORM",
            ExtractionProfile::Government => "GOVERNMENT",
            ExtractionProfile::Dense => "DENSE",
            ExtractionProfile::Presentation => "PRESENTATION",
            ExtractionProfile::Rag => "RAG",
        };
        format!("ExtractionProfile.{}", name)
    }
}

// ── PyReadingOrderStrategy ─────────────────────────────────────────────────

/// Strategy for ordering text fragments before classification.
#[pyclass(name = "ReadingOrderStrategy", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyReadingOrderStrategy {
    pub inner: ReadingOrderStrategy,
}

#[pymethods]
impl PyReadingOrderStrategy {
    #[classattr]
    const SIMPLE: Self = Self { inner: ReadingOrderStrategy::Simple };
    #[classattr]
    const NONE: Self = Self { inner: ReadingOrderStrategy::None };

    /// XY-Cut recursive algorithm with minimum gap parameter.
    #[staticmethod]
    fn xy_cut(min_gap: f64) -> Self {
        Self { inner: ReadingOrderStrategy::XYCut { min_gap } }
    }

    fn __repr__(&self) -> String {
        match self.inner {
            ReadingOrderStrategy::Simple => "ReadingOrderStrategy.SIMPLE".to_string(),
            ReadingOrderStrategy::None => "ReadingOrderStrategy.NONE".to_string(),
            ReadingOrderStrategy::XYCut { min_gap } => {
                format!("ReadingOrderStrategy.xy_cut({})", min_gap)
            }
        }
    }
}

// ── PyPartitionConfig ──────────────────────────────────────────────────────

/// Configuration for the document partitioner.
#[pyclass(name = "PartitionConfig", from_py_object)]
#[derive(Clone)]
pub struct PyPartitionConfig {
    pub inner: PartitionConfig,
}

#[pymethods]
impl PyPartitionConfig {
    #[new]
    fn new() -> Self {
        Self { inner: PartitionConfig::new() }
    }

    /// Disable table detection.
    fn without_tables(&self) -> Self {
        Self { inner: self.inner.clone().without_tables() }
    }

    /// Disable header/footer detection.
    fn without_headers_footers(&self) -> Self {
        Self { inner: self.inner.clone().without_headers_footers() }
    }

    /// Set the reading order strategy.
    fn with_reading_order(&self, strategy: &PyReadingOrderStrategy) -> Self {
        Self { inner: self.inner.clone().with_reading_order(strategy.inner.clone()) }
    }

    /// Set the minimum font size ratio for title detection.
    fn with_title_min_font_ratio(&self, ratio: f64) -> Self {
        Self { inner: self.inner.clone().with_title_min_font_ratio(ratio) }
    }

    /// Set the minimum confidence threshold for table detection.
    fn with_min_table_confidence(&self, threshold: f64) -> Self {
        Self { inner: self.inner.clone().with_min_table_confidence(threshold) }
    }

    /// Disable the ruling-based (vector-grid) table detector. Only the spatial
    /// detector runs and no page graphics are extracted.
    fn without_ruling_tables(&self) -> Self {
        let mut inner = self.inner.clone();
        inner.prefer_ruling_tables = false;
        Self { inner }
    }

    /// Whether the ruling-based table detector is preferred (default true).
    #[getter]
    fn prefer_ruling_tables(&self) -> bool {
        self.inner.prefer_ruling_tables
    }

    fn __repr__(&self) -> String {
        format!(
            "PartitionConfig(detect_tables={}, detect_headers_footers={}, prefer_ruling_tables={})",
            self.inner.detect_tables,
            self.inner.detect_headers_footers,
            self.inner.prefer_ruling_tables,
        )
    }
}

// ── PyMergePolicy ──────────────────────────────────────────────────────────

/// Policy for which adjacent element types can be merged into a single chunk.
#[pyclass(name = "MergePolicy", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyMergePolicy {
    pub inner: MergePolicy,
}

#[pymethods]
impl PyMergePolicy {
    #[classattr]
    const SAME_TYPE_ONLY: Self = Self { inner: MergePolicy::SameTypeOnly };
    #[classattr]
    const ANY_INLINE_CONTENT: Self = Self { inner: MergePolicy::AnyInlineContent };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            MergePolicy::SameTypeOnly => "SAME_TYPE_ONLY",
            MergePolicy::AnyInlineContent => "ANY_INLINE_CONTENT",
        };
        format!("MergePolicy.{}", name)
    }
}

// ── ContextFormat / ContextMode (#376) ─────────────────────────────────────

/// Rendering format for the contextual-retrieval prefix prepended to a chunk's
/// embedding text under :meth:`ContextMode.contextual`.
///
/// New in oxidize-python 0.15.0 (oxidize-pdf 4.0.0, issue #376).
#[pyclass(name = "ContextFormat", eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyContextFormat {
    /// Labelled key/value lines (e.g. ``Document: …``).
    Labeled,
    /// Flowing prose sentence.
    Prose,
}

impl PyContextFormat {
    fn to_core(self) -> ContextFormat {
        match self {
            PyContextFormat::Labeled => ContextFormat::Labeled,
            PyContextFormat::Prose => ContextFormat::Prose,
        }
    }

    fn from_core(f: ContextFormat) -> Option<Self> {
        match f {
            ContextFormat::Labeled => Some(PyContextFormat::Labeled),
            ContextFormat::Prose => Some(PyContextFormat::Prose),
            _ => None,
        }
    }
}

/// How much document/section context to fold into a chunk's embedding text
/// (``full_text``). The display ``text`` is never affected.
///
/// Construct via the :meth:`none`, :meth:`heading`, or :meth:`contextual`
/// static methods. The default on :class:`HybridChunkConfig` is
/// :meth:`heading`, which is byte-identical to prior output.
///
/// New in oxidize-python 0.15.0 (oxidize-pdf 4.0.0, issue #376).
#[pyclass(name = "ContextMode", frozen, from_py_object)]
#[derive(Clone, Copy)]
pub struct PyContextMode {
    pub inner: ContextMode,
}

#[pymethods]
impl PyContextMode {
    /// No context: ``full_text`` equals the display ``text``.
    #[staticmethod]
    fn none() -> Self {
        Self { inner: ContextMode::None }
    }

    /// Heading breadcrumb only (default). Byte-identical to prior output.
    #[staticmethod]
    fn heading() -> Self {
        Self { inner: ContextMode::Heading }
    }

    /// Prepend a deterministic document + section snippet (title/author or
    /// filename, heading breadcrumb, optional page span) to ``full_text``.
    #[staticmethod]
    fn contextual(format: &PyContextFormat) -> Self {
        Self { inner: ContextMode::Contextual(format.to_core()) }
    }

    /// The contextual format, or ``None`` for the non-contextual modes.
    #[getter]
    fn format(&self) -> Option<PyContextFormat> {
        match self.inner {
            ContextMode::Contextual(f) => PyContextFormat::from_core(f),
            _ => None,
        }
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.inner == other.inner
    }

    fn __repr__(&self) -> String {
        self.describe()
    }
}

impl PyContextMode {
    /// Rust-visible repr, callable from other bridge modules.
    pub(crate) fn describe(&self) -> String {
        match self.inner {
            ContextMode::None => "ContextMode.none()".to_string(),
            ContextMode::Heading => "ContextMode.heading()".to_string(),
            ContextMode::Contextual(f) => format!("ContextMode.contextual({f:?})"),
        }
    }
}

// ── PyHybridChunkConfig ────────────────────────────────────────────────────

/// Configuration for hybrid chunking.
#[pyclass(name = "HybridChunkConfig", from_py_object)]
#[derive(Clone)]
pub struct PyHybridChunkConfig {
    pub inner: HybridChunkConfig,
}

#[pymethods]
impl PyHybridChunkConfig {
    #[new]
    #[pyo3(signature = (max_tokens = 512, overlap_tokens = 50, context_mode = None))]
    fn new(
        max_tokens: usize,
        overlap_tokens: usize,
        context_mode: Option<PyContextMode>,
    ) -> Self {
        Self {
            inner: HybridChunkConfig {
                max_tokens,
                overlap_tokens,
                context_mode: context_mode.map(|m| m.inner).unwrap_or_default(),
                ..HybridChunkConfig::default()
            },
        }
    }

    #[getter]
    fn max_tokens(&self) -> usize {
        self.inner.max_tokens
    }

    #[getter]
    fn overlap_tokens(&self) -> usize {
        self.inner.overlap_tokens
    }

    /// The contextual-retrieval mode applied to each chunk's ``full_text``.
    /// New in oxidize-python 0.15.0 (oxidize-pdf 4.0.0, issue #376).
    #[getter]
    fn context_mode(&self) -> PyContextMode {
        PyContextMode { inner: self.inner.context_mode }
    }

    fn __repr__(&self) -> String {
        format!(
            "HybridChunkConfig(max_tokens={}, overlap_tokens={}, context_mode={})",
            self.inner.max_tokens,
            self.inner.overlap_tokens,
            PyContextMode { inner: self.inner.context_mode }.__repr__(),
        )
    }
}

// ── PySemanticChunkConfig ──────────────────────────────────────────────────

/// Configuration for semantic chunking.
#[pyclass(name = "SemanticChunkConfig", from_py_object)]
#[derive(Clone)]
pub struct PySemanticChunkConfig {
    pub inner: SemanticChunkConfig,
}

#[pymethods]
impl PySemanticChunkConfig {
    #[new]
    fn new(max_tokens: usize) -> Self {
        Self { inner: SemanticChunkConfig::new(max_tokens) }
    }

    /// Set overlap tokens.
    fn with_overlap(&self, overlap: usize) -> Self {
        Self { inner: self.inner.clone().with_overlap(overlap) }
    }

    #[getter]
    fn max_tokens(&self) -> usize {
        self.inner.max_tokens
    }

    #[getter]
    fn overlap_tokens(&self) -> usize {
        self.inner.overlap_tokens
    }

    fn __repr__(&self) -> String {
        format!(
            "SemanticChunkConfig(max_tokens={}, overlap_tokens={})",
            self.inner.max_tokens, self.inner.overlap_tokens,
        )
    }
}

// ── RichCell / TableStructure (#375) ───────────────────────────────────────

/// One cell of a rich table, including its span and header flag.
///
/// New in oxidize-python 0.15.0 (oxidize-pdf 4.0.0, issue #375).
#[pyclass(name = "RichCell", frozen)]
pub struct PyRichCell {
    pub inner: RichCell,
}

#[pymethods]
impl PyRichCell {
    /// 0-based row index of the cell's top-left anchor.
    #[getter]
    fn row(&self) -> usize {
        self.inner.row
    }

    /// 0-based column index of the cell's top-left anchor.
    #[getter]
    fn col(&self) -> usize {
        self.inner.col
    }

    /// Number of rows the cell spans (``>= 1``).
    #[getter]
    fn row_span(&self) -> usize {
        self.inner.row_span
    }

    /// Number of columns the cell spans (``>= 1``).
    #[getter]
    fn col_span(&self) -> usize {
        self.inner.col_span
    }

    /// Cell text.
    #[getter]
    fn text(&self) -> &str {
        &self.inner.text
    }

    /// Whether the cell belongs to a header row.
    #[getter]
    fn is_header(&self) -> bool {
        self.inner.is_header
    }

    fn __repr__(&self) -> String {
        format!(
            "RichCell(row={}, col={}, row_span={}, col_span={}, is_header={}, text={:?})",
            self.inner.row,
            self.inner.col,
            self.inner.row_span,
            self.inner.col_span,
            self.inner.is_header,
            self.inner.text,
        )
    }
}

/// Rich table structure: merged cells and header rows, present only when a hard
/// signal (drawn grid / structure tags) revealed it.
///
/// New in oxidize-python 0.15.0 (oxidize-pdf 4.0.0, issue #375).
#[pyclass(name = "TableStructure", frozen)]
pub struct PyTableStructure {
    pub inner: TableStructure,
}

#[pymethods]
impl PyTableStructure {
    /// All cells, each carrying its position, span, and header flag. Interior
    /// positions of a merged cell are omitted (only the anchor is present).
    #[getter]
    fn cells(&self) -> Vec<PyRichCell> {
        self.inner
            .cells
            .iter()
            .map(|c| PyRichCell { inner: c.clone() })
            .collect()
    }

    /// Number of rows in the base grid.
    #[getter]
    fn num_rows(&self) -> usize {
        self.inner.num_rows
    }

    /// Number of columns in the base grid.
    #[getter]
    fn num_cols(&self) -> usize {
        self.inner.num_cols
    }

    /// Number of leading header rows (0 = none, 1 = single, >1 = multi-level).
    #[getter]
    fn header_rows(&self) -> usize {
        self.inner.header_rows
    }

    fn __repr__(&self) -> String {
        format!(
            "TableStructure(num_rows={}, num_cols={}, header_rows={}, cells={})",
            self.inner.num_rows,
            self.inner.num_cols,
            self.inner.header_rows,
            self.inner.cells.len(),
        )
    }
}

// ── PyElement ──────────────────────────────────────────────────────────────

/// A typed document element extracted from a PDF page.
///
/// Wraps `oxidize_pdf::pipeline::Element` with simplified read-only access.
#[pyclass(name = "Element", frozen)]
pub struct PyElement {
    pub inner: oxidize_pdf::pipeline::Element,
}

#[pymethods]
impl PyElement {
    /// Snake-case type name: "title", "paragraph", "table", etc.
    #[getter]
    fn type_name(&self) -> &'static str {
        self.inner.type_name()
    }

    /// Primary text content of this element.
    #[getter]
    fn text(&self) -> String {
        self.inner.text().to_string()
    }

    /// Human-readable text representation (tables show pipe-separated rows).
    #[getter]
    fn display_text(&self) -> String {
        self.inner.display_text()
    }

    /// Page number (0-indexed) where this element appears.
    #[getter]
    fn page(&self) -> u32 {
        self.inner.page()
    }

    /// Rich table structure (merged cells + header rows) for table elements
    /// where a hard signal — a drawn grid or PDF structure tags — revealed it.
    /// ``None`` for non-table elements and for borderless/un-tagged tables that
    /// only carry the flat row view.
    ///
    /// New in oxidize-python 0.15.0 (oxidize-pdf 4.0.0, issue #375).
    #[getter]
    fn table_structure(&self) -> Option<PyTableStructure> {
        match &self.inner {
            Element::Table(t) => t
                .structure
                .clone()
                .map(|inner| PyTableStructure { inner }),
            _ => None,
        }
    }

    /// Open class label assigned by a custom
    /// :class:`oxidize_pdf.experimental.ElementClassifier` before chunking.
    /// ``None`` when no classifier ran or the classifier returned ``None``.
    ///
    /// Only available with the `unstable-spi` feature — the upstream
    /// `class_label` field is gated by it.
    #[cfg(feature = "unstable-spi")]
    #[getter]
    fn class_label(&self) -> Option<String> {
        self.inner.metadata().class_label.clone()
    }

    fn __repr__(&self) -> String {
        format!(
            "Element(type={:?}, page={})",
            self.inner.type_name(),
            self.inner.page(),
        )
    }
}

// ── PyElementBBox ──────────────────────────────────────────────────────────

/// Axis-aligned bounding box for a pipeline element or page region.
///
/// PDF coordinate system: origin at bottom-left, `y` grows upward.
#[pyclass(name = "ElementBBox", frozen, skip_from_py_object)]
#[derive(Clone, Copy)]
pub struct PyElementBBox {
    pub inner: ElementBBox,
}

#[pymethods]
impl PyElementBBox {
    /// Left edge X coordinate (PDF points).
    #[getter]
    fn x(&self) -> f64 {
        self.inner.x
    }

    /// Bottom edge Y coordinate (PDF points, origin at page bottom).
    #[getter]
    fn y(&self) -> f64 {
        self.inner.y
    }

    /// Width of the bounding box (PDF points).
    #[getter]
    fn width(&self) -> f64 {
        self.inner.width
    }

    /// Height of the bounding box (PDF points).
    #[getter]
    fn height(&self) -> f64 {
        self.inner.height
    }

    fn __repr__(&self) -> String {
        format!(
            "ElementBBox(x={:.2}, y={:.2}, width={:.2}, height={:.2})",
            self.inner.x, self.inner.y, self.inner.width, self.inner.height,
        )
    }
}

// ── PyContentTypeFlags ─────────────────────────────────────────────────────

/// Boolean flags describing the kinds of content present in a chunk.
#[pyclass(name = "ContentTypeFlags", frozen, skip_from_py_object)]
#[derive(Clone, Copy)]
pub struct PyContentTypeFlags {
    pub inner: ContentTypeFlags,
}

#[pymethods]
impl PyContentTypeFlags {
    /// True if the chunk contains at least one table element.
    #[getter]
    fn has_table(&self) -> bool {
        self.inner.has_table
    }

    /// True if the chunk contains at least one list item.
    #[getter]
    fn has_list(&self) -> bool {
        self.inner.has_list
    }

    /// True if the chunk contains at least one code block.
    #[getter]
    fn has_code(&self) -> bool {
        self.inner.has_code
    }

    /// True if the chunk is composed solely of heading (title) elements.
    #[getter]
    fn heading_only(&self) -> bool {
        self.inner.heading_only
    }

    fn __repr__(&self) -> String {
        format!(
            "ContentTypeFlags(has_table={}, has_list={}, has_code={}, heading_only={})",
            self.inner.has_table,
            self.inner.has_list,
            self.inner.has_code,
            self.inner.heading_only,
        )
    }
}

// ── PyPageRegion ───────────────────────────────────────────────────────────

/// Citation anchor for a chunk on a single page: the page number and the
/// union bounding box of the chunk's elements on that page.
#[pyclass(name = "PageRegion", frozen, skip_from_py_object)]
#[derive(Clone, Copy)]
pub struct PyPageRegion {
    pub inner: PageRegion,
}

#[pymethods]
impl PyPageRegion {
    /// Page number (as stored on the elements — 0-indexed in core).
    #[getter]
    fn page(&self) -> u32 {
        self.inner.page
    }

    /// Union bounding box of the chunk's elements on this page.
    #[getter]
    fn bbox(&self) -> PyElementBBox {
        PyElementBBox {
            inner: self.inner.bbox,
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "PageRegion(page={}, bbox=ElementBBox(x={:.2}, y={:.2}, w={:.2}, h={:.2}))",
            self.inner.page,
            self.inner.bbox.x,
            self.inner.bbox.y,
            self.inner.bbox.width,
            self.inner.bbox.height,
        )
    }
}

// ── PyDocumentSource ───────────────────────────────────────────────────────

/// Metadata about the source document a chunk came from.
///
/// Construct with the keyword args ``filename`` and/or ``doc_hash``; the rest
/// (``title``/``author``/``creation_date``/``total_pages``) is auto-filled by
/// :meth:`PdfReader.rag_chunks_with_source` from the PDF info dictionary
/// when the caller leaves them at the default (``None``).
#[pyclass(name = "DocumentSource", frozen, skip_from_py_object)]
#[derive(Clone)]
pub struct PyDocumentSource {
    pub inner: DocumentSource,
}

#[pymethods]
impl PyDocumentSource {
    #[new]
    #[pyo3(signature = (filename = None, doc_hash = None))]
    fn new(filename: Option<String>, doc_hash: Option<String>) -> Self {
        Self {
            inner: DocumentSource::with_file(filename, doc_hash),
        }
    }

    /// Document title from the info dictionary, if present (auto-filled).
    #[getter]
    fn title(&self) -> Option<String> {
        self.inner.title.clone()
    }

    /// Document author from the info dictionary, if present (auto-filled).
    #[getter]
    fn author(&self) -> Option<String> {
        self.inner.author.clone()
    }

    /// Creation date string from the info dictionary, if present.
    #[getter]
    fn creation_date(&self) -> Option<String> {
        self.inner.creation_date.clone()
    }

    /// Originating file name (caller-supplied).
    #[getter]
    fn filename(&self) -> Option<String> {
        self.inner.filename.clone()
    }

    /// Stable document hash (caller-supplied; used as the ``chunk_id`` prefix).
    #[getter]
    fn doc_hash(&self) -> Option<String> {
        self.inner.doc_hash.clone()
    }

    /// Total page count of the source document.
    #[getter]
    fn total_pages(&self) -> Option<u32> {
        self.inner.total_pages
    }

    fn __repr__(&self) -> String {
        format!(
            "DocumentSource(filename={:?}, doc_hash={:?}, title={:?}, author={:?}, total_pages={:?})",
            self.inner.filename,
            self.inner.doc_hash,
            self.inner.title,
            self.inner.author,
            self.inner.total_pages,
        )
    }
}

// ── PyRagChunk ─────────────────────────────────────────────────────────────

/// A RAG-ready chunk with full metadata for vector store ingestion.
#[pyclass(name = "RagChunk", frozen)]
pub struct PyRagChunk {
    pub inner: RagChunk,
}

#[pymethods]
impl PyRagChunk {
    /// Sequential index of this chunk in the document (0-based).
    #[getter]
    fn chunk_index(&self) -> usize {
        self.inner.chunk_index
    }

    /// Chunk text content (elements joined by newlines).
    #[getter]
    fn text(&self) -> &str {
        &self.inner.text
    }

    /// Text with heading context prepended — use this for embedding generation.
    #[getter]
    fn full_text(&self) -> &str {
        &self.inner.full_text
    }

    /// Page numbers where this chunk's elements appear.
    #[getter]
    fn page_numbers(&self) -> Vec<u32> {
        self.inner.page_numbers.clone()
    }

    /// Type names of each element (e.g. "title", "paragraph", "table").
    #[getter]
    fn element_types(&self) -> Vec<String> {
        self.inner.element_types.clone()
    }

    /// Heading context inherited from the nearest parent heading.
    #[getter]
    fn heading_context(&self) -> Option<String> {
        self.inner.heading_context.clone()
    }

    /// Approximate token count (word-count proxy).
    #[getter]
    fn token_estimate(&self) -> usize {
        self.inner.token_estimate
    }

    /// Whether the chunk exceeds the configured max_tokens.
    #[getter]
    fn is_oversized(&self) -> bool {
        self.inner.is_oversized
    }

    // ── ChunkMetadata getters (upstream 2.16.0) ──────────────────────────

    /// Full section breadcrumb, root→leaf (e.g. `["1 Intro", "1.2 Scope"]`).
    #[getter]
    fn heading_path(&self) -> Vec<String> {
        self.inner.metadata.heading_path.clone()
    }

    /// Dominant font (char-weighted majority across the chunk's elements).
    #[getter]
    fn dominant_font(&self) -> Option<String> {
        self.inner.metadata.dominant_font.clone()
    }

    /// Dominant font size in points (char-weighted majority).
    #[getter]
    fn dominant_font_size(&self) -> Option<f64> {
        self.inner.metadata.dominant_font_size
    }

    /// True if the majority of characters in the chunk are bold.
    #[getter]
    fn is_bold(&self) -> bool {
        self.inner.metadata.is_bold
    }

    /// True if the majority of characters in the chunk are italic.
    #[getter]
    fn is_italic(&self) -> bool {
        self.inner.metadata.is_italic
    }

    /// Lowest classification confidence among the chunk's elements.
    #[getter]
    fn min_confidence(&self) -> f32 {
        self.inner.metadata.min_confidence
    }

    /// Content-type flags derived from element types.
    #[getter]
    fn content_types(&self) -> PyContentTypeFlags {
        PyContentTypeFlags {
            inner: self.inner.metadata.content_types,
        }
    }

    /// Character count of the chunk text.
    #[getter]
    fn char_count(&self) -> usize {
        self.inner.metadata.char_count
    }

    /// Whitespace-separated word count.
    #[getter]
    fn word_count(&self) -> usize {
        self.inner.metadata.word_count
    }

    /// Sentence count (uses the chunker's sentence splitter).
    #[getter]
    fn sentence_count(&self) -> usize {
        self.inner.metadata.sentence_count
    }

    /// Detected language code (ISO 639-3, via `whatlang`); `None` if the
    /// detection is inconclusive.
    #[getter]
    fn language(&self) -> Option<String> {
        self.inner.metadata.language.clone()
    }

    /// Detection confidence in `(0, 1]` for `language`; `None` when no
    /// language was detected.
    #[getter]
    fn language_confidence(&self) -> Option<f32> {
        self.inner.metadata.language_confidence
    }

    /// Whether the language detection is considered reliable; `None` when no
    /// language was detected.
    #[getter]
    fn language_reliable(&self) -> Option<bool> {
        self.inner.metadata.language_reliable
    }

    /// Deterministic, stable identifier for this chunk.
    #[getter]
    fn chunk_id(&self) -> String {
        self.inner.metadata.chunk_id.clone()
    }

    /// Identifier of the previous chunk in the document, if any.
    #[getter]
    fn prev_chunk_id(&self) -> Option<String> {
        self.inner.metadata.prev_chunk_id.clone()
    }

    /// Identifier of the next chunk in the document, if any.
    #[getter]
    fn next_chunk_id(&self) -> Option<String> {
        self.inner.metadata.next_chunk_id.clone()
    }

    /// First and last page the chunk's elements touch (inclusive), or `None`
    /// when the chunk has no positioned elements.
    #[getter]
    fn page_span(&self) -> Option<(u32, u32)> {
        self.inner.metadata.page_span
    }

    /// Per-page citation regions (union bbox of the chunk's elements on each
    /// page), sorted ascending by page.
    #[getter]
    fn page_regions(&self) -> Vec<PyPageRegion> {
        self.inner
            .metadata
            .page_regions
            .iter()
            .map(|r| PyPageRegion { inner: *r })
            .collect()
    }

    /// Row count of the chunk's largest table, or `None` if no table.
    #[getter]
    fn table_rows(&self) -> Option<usize> {
        self.inner.metadata.table_rows
    }

    /// Column count of the same table reported by `table_rows`; `None` when
    /// the chunk has no table.
    #[getter]
    fn table_cols(&self) -> Option<usize> {
        self.inner.metadata.table_cols
    }

    /// Source-document metadata, if the chunk was produced through
    /// :meth:`PdfReader.rag_chunks_with_source` (or the ``_and_config``
    /// variant). ``None`` for chunks from the bare ``rag_chunks()``.
    #[getter]
    fn source(&self) -> Option<PyDocumentSource> {
        self.inner
            .metadata
            .source
            .clone()
            .map(|inner| PyDocumentSource { inner })
    }

    /// Open extension bag for provider-supplied fields, populated by
    /// :class:`oxidize_pdf.experimental.MetadataEnricher` implementations.
    /// Returns an empty dict when no enricher ran.
    #[getter]
    fn extra<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, pyo3::types::PyDict>> {
        crate::json_util::extra_map_to_py_dict(py, &self.inner.metadata.extra)
    }

    fn __repr__(&self) -> String {
        format!(
            "RagChunk(chunk_index={}, pages={:?}, token_estimate={}, chunk_id={:?})",
            self.inner.chunk_index,
            self.inner.page_numbers,
            self.inner.token_estimate,
            self.inner.metadata.chunk_id,
        )
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDetectedLanguage>()?;
    m.add_class::<PyDocumentChunk>()?;
    m.add_class::<PyDocumentChunker>()?;
    m.add_class::<PyMarkdownOptions>()?;
    m.add_class::<PyMarkdownExporter>()?;
    m.add_class::<PyTokenEfficientExporter>()?;
    m.add_class::<PyJsonExporter>()?;
    m.add_class::<PyExtractionProfile>()?;
    m.add_class::<PyReadingOrderStrategy>()?;
    m.add_class::<PyPartitionConfig>()?;
    m.add_class::<PyMergePolicy>()?;
    m.add_class::<PyContextFormat>()?;
    m.add_class::<PyContextMode>()?;
    m.add_class::<PyHybridChunkConfig>()?;
    m.add_class::<PySemanticChunkConfig>()?;
    m.add_class::<PyRichCell>()?;
    m.add_class::<PyTableStructure>()?;
    m.add_class::<PyElement>()?;
    m.add_class::<PyRagChunk>()?;
    m.add_class::<PyElementBBox>()?;
    m.add_class::<PyContentTypeFlags>()?;
    m.add_class::<PyPageRegion>()?;
    m.add_class::<PyDocumentSource>()?;
    Ok(())
}
