//! AI/ML Pipeline bindings — Feature 59
//!
//! Wraps `oxidize_pdf::ai` and `oxidize_pdf::pipeline` for Python:
//! document chunking, markdown export, element partitioning, and RAG chunks.

use pyo3::prelude::*;

use oxidize_pdf::ai::{DocumentChunk, DocumentChunker, MarkdownExporter, MarkdownOptions};
use oxidize_pdf::pipeline::{
    ExtractionProfile, HybridChunkConfig, MergePolicy, PartitionConfig, RagChunk,
    ReadingOrderStrategy, SemanticChunkConfig,
};

use crate::errors::to_py_err;

fn pdf_err_to_py(err: oxidize_pdf::PdfError) -> PyErr {
    to_py_err(err)
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

    fn __repr__(&self) -> String {
        format!(
            "PartitionConfig(detect_tables={}, detect_headers_footers={})",
            self.inner.detect_tables, self.inner.detect_headers_footers,
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
    #[pyo3(signature = (max_tokens = 512, overlap_tokens = 50))]
    fn new(max_tokens: usize, overlap_tokens: usize) -> Self {
        Self {
            inner: HybridChunkConfig {
                max_tokens,
                overlap_tokens,
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

    fn __repr__(&self) -> String {
        format!(
            "HybridChunkConfig(max_tokens={}, overlap_tokens={})",
            self.inner.max_tokens, self.inner.overlap_tokens,
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

    fn __repr__(&self) -> String {
        format!(
            "Element(type={:?}, page={})",
            self.inner.type_name(),
            self.inner.page(),
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

    fn __repr__(&self) -> String {
        format!(
            "RagChunk(chunk_index={}, pages={:?}, token_estimate={})",
            self.inner.chunk_index, self.inner.page_numbers, self.inner.token_estimate,
        )
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDocumentChunk>()?;
    m.add_class::<PyDocumentChunker>()?;
    m.add_class::<PyMarkdownOptions>()?;
    m.add_class::<PyMarkdownExporter>()?;
    m.add_class::<PyExtractionProfile>()?;
    m.add_class::<PyReadingOrderStrategy>()?;
    m.add_class::<PyPartitionConfig>()?;
    m.add_class::<PyMergePolicy>()?;
    m.add_class::<PyHybridChunkConfig>()?;
    m.add_class::<PySemanticChunkConfig>()?;
    m.add_class::<PyElement>()?;
    m.add_class::<PyRagChunk>()?;
    Ok(())
}
