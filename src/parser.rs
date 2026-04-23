use std::fs::File;
use std::io::Cursor;

use pyo3::prelude::*;

use oxidize_pdf::ai::DocumentChunker;

use crate::ai_pipeline::{PyDocumentChunk, PyElement, PyExtractionProfile, PyRagChunk};
use crate::errors;
use crate::text_extraction::{PyExtractionOptions, PyPlainTextConfig, PyPlainTextResult};

/// Convert a parser `ParseError` into the appropriate Python exception.
///
/// We map directly instead of going through `PdfError` because the
/// `From<ParseError> for PdfError` conversion loses variant information
/// (e.g. `ParseError::Io` becomes `PdfError::ParseError(String)`).
fn parse_err_to_py(err: oxidize_pdf::parser::ParseError) -> PyErr {
    use oxidize_pdf::parser::ParseError as PE;

    match err {
        PE::Io(io_err) => errors::PdfIoError::new_err(format!("IO error: {io_err}")),
        PE::EncryptionNotSupported | PE::WrongPassword | PE::PdfLocked => {
            errors::PdfEncryptionError::new_err(err.to_string())
        }
        _ => errors::PdfParseError::new_err(err.to_string()),
    }
}

fn pdf_err_to_py(err: oxidize_pdf::PdfError) -> PyErr {
    errors::to_py_err(err)
}

// ── ParseOptions ──────────────────────────────────────────────────────────────

#[pyclass(name = "ParseOptions", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyParseOptions {
    pub inner: oxidize_pdf::parser::ParseOptions,
}

#[pymethods]
impl PyParseOptions {
    #[new]
    #[pyo3(signature = (
        strict_mode = true,
        recover_from_stream_errors = false,
        ignore_corrupt_streams = false,
        partial_content_allowed = false,
        lenient_streams = false,
        lenient_encoding = true,
        lenient_syntax = false,
        max_recovery_attempts = 3,
        max_recovery_bytes = 1000,
        collect_warnings = false,
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        strict_mode: bool,
        recover_from_stream_errors: bool,
        ignore_corrupt_streams: bool,
        partial_content_allowed: bool,
        lenient_streams: bool,
        lenient_encoding: bool,
        lenient_syntax: bool,
        max_recovery_attempts: usize,
        max_recovery_bytes: usize,
        collect_warnings: bool,
    ) -> Self {
        Self {
            inner: oxidize_pdf::parser::ParseOptions {
                strict_mode,
                recover_from_stream_errors,
                ignore_corrupt_streams,
                partial_content_allowed,
                lenient_streams,
                lenient_encoding,
                lenient_syntax,
                max_recovery_attempts,
                max_recovery_bytes,
                collect_warnings,
                ..Default::default()
            },
        }
    }

    #[staticmethod]
    fn strict() -> Self {
        Self {
            inner: oxidize_pdf::parser::ParseOptions::strict(),
        }
    }

    #[staticmethod]
    fn tolerant() -> Self {
        Self {
            inner: oxidize_pdf::parser::ParseOptions::tolerant(),
        }
    }

    #[staticmethod]
    fn lenient() -> Self {
        Self {
            inner: oxidize_pdf::parser::ParseOptions::lenient(),
        }
    }

    #[staticmethod]
    fn skip_errors() -> Self {
        Self {
            inner: oxidize_pdf::parser::ParseOptions::skip_errors(),
        }
    }

    #[getter]
    fn strict_mode(&self) -> bool {
        self.inner.strict_mode
    }

    #[getter]
    fn recover_from_stream_errors(&self) -> bool {
        self.inner.recover_from_stream_errors
    }

    #[getter]
    fn ignore_corrupt_streams(&self) -> bool {
        self.inner.ignore_corrupt_streams
    }

    #[getter]
    fn partial_content_allowed(&self) -> bool {
        self.inner.partial_content_allowed
    }

    #[getter]
    fn lenient_streams(&self) -> bool {
        self.inner.lenient_streams
    }

    #[getter]
    fn lenient_encoding(&self) -> bool {
        self.inner.lenient_encoding
    }

    #[getter]
    fn lenient_syntax(&self) -> bool {
        self.inner.lenient_syntax
    }

    #[getter]
    fn max_recovery_attempts(&self) -> usize {
        self.inner.max_recovery_attempts
    }

    #[getter]
    fn max_recovery_bytes(&self) -> usize {
        self.inner.max_recovery_bytes
    }

    #[getter]
    fn collect_warnings(&self) -> bool {
        self.inner.collect_warnings
    }

    fn __repr__(&self) -> String {
        format!(
            "ParseOptions(strict_mode={}, lenient_streams={})",
            self.inner.strict_mode, self.inner.lenient_streams,
        )
    }
}

// ── DocumentMetadata ──────────────────────────────────────────────────────────

#[pyclass(name = "DocumentMetadata", frozen)]
pub struct PyDocumentMetadata {
    #[pyo3(get)]
    pub title: Option<String>,
    #[pyo3(get)]
    pub author: Option<String>,
    #[pyo3(get)]
    pub subject: Option<String>,
    #[pyo3(get)]
    pub keywords: Option<String>,
    #[pyo3(get)]
    pub creator: Option<String>,
    #[pyo3(get)]
    pub producer: Option<String>,
    #[pyo3(get)]
    pub creation_date: Option<String>,
    #[pyo3(get)]
    pub modification_date: Option<String>,
    #[pyo3(get)]
    pub version: String,
    #[pyo3(get)]
    pub page_count: Option<u32>,
}

#[pymethods]
impl PyDocumentMetadata {
    fn __repr__(&self) -> String {
        format!(
            "DocumentMetadata(title={:?}, author={:?}, version={:?})",
            self.title, self.author, self.version,
        )
    }
}

/// Internal state of PyPdfReader.
///
/// When first opened on an encrypted file, we hold a raw `PdfReader` so
/// that `unlock` can work. Once the reader is ready (not encrypted or
/// successfully unlocked), we promote it to a `PdfDocument`.
///
/// Supports both file-backed and in-memory (bytes) readers.
enum ReaderState {
    /// Raw reader from file — encrypted, not yet unlocked.
    RawFile(oxidize_pdf::PdfReader<File>),
    /// Raw reader from bytes — encrypted, not yet unlocked.
    RawCursor(oxidize_pdf::PdfReader<Cursor<Vec<u8>>>),
    /// High-level document wrapper from file (ready for queries).
    FileDocument(oxidize_pdf::PdfDocument<File>),
    /// High-level document wrapper from bytes (ready for queries).
    CursorDocument(oxidize_pdf::PdfDocument<Cursor<Vec<u8>>>),
    /// Transient state during promotion (never visible to callers).
    Transitioning,
}

/// Dispatch a method call on the inner `PdfDocument` regardless of backend.
///
/// Since `PdfDocument<File>` and `PdfDocument<Cursor<Vec<u8>>>` are distinct
/// types with identical APIs, this macro expands to a match on both variants.
macro_rules! with_document {
    ($self:expr, $doc:ident => $body:expr) => {
        match &$self.state {
            ReaderState::FileDocument($doc) => $body,
            ReaderState::CursorDocument($doc) => $body,
            _ => unreachable!("promote() guarantees Document state"),
        }
    };
}

// ── PdfReader ─────────────────────────────────────────────────────────────────

/// High-level PDF reader for parsing existing PDF files or byte buffers.
///
/// Example::
///
///     reader = PdfReader.open("document.pdf")
///     if reader.is_encrypted:
///         reader.unlock("password")
///     print(f"Pages: {len(reader)}")
///     text = reader.extract_text_from_page(0)
///
///     # Or from bytes:
///     reader = PdfReader.from_bytes(pdf_bytes)
#[pyclass(name = "PdfReader", unsendable)]
struct PyPdfReader {
    state: ReaderState,
    /// Cached flag — True if the file was encrypted on open.
    encrypted: bool,
}

impl PyPdfReader {
    /// Promote to PdfDocument if still in Raw state.
    fn promote(&mut self) {
        let old = std::mem::replace(&mut self.state, ReaderState::Transitioning);
        self.state = match old {
            ReaderState::RawFile(reader) => {
                ReaderState::FileDocument(oxidize_pdf::PdfDocument::new(reader))
            }
            ReaderState::RawCursor(reader) => {
                ReaderState::CursorDocument(oxidize_pdf::PdfDocument::new(reader))
            }
            other => other,
        };
    }

    /// Ensure the reader is in a Document state.
    fn ensure_document(&mut self) {
        if matches!(
            self.state,
            ReaderState::RawFile(_) | ReaderState::RawCursor(_)
        ) {
            self.promote();
        }
    }
}

#[pymethods]
impl PyPdfReader {
    /// Open a PDF file for reading.
    #[staticmethod]
    #[pyo3(signature = (path, options = None))]
    fn open(path: &str, options: Option<&PyParseOptions>) -> PyResult<Self> {
        let reader = if let Some(opts) = options {
            oxidize_pdf::PdfReader::open_with_options(path, opts.inner.clone())
        } else {
            oxidize_pdf::PdfReader::open(path)
        }
        .map_err(parse_err_to_py)?;
        let encrypted = reader.is_encrypted();

        if encrypted {
            Ok(Self {
                state: ReaderState::RawFile(reader),
                encrypted,
            })
        } else {
            Ok(Self {
                state: ReaderState::FileDocument(oxidize_pdf::PdfDocument::new(reader)),
                encrypted,
            })
        }
    }

    /// Open a PDF from an in-memory byte buffer.
    #[staticmethod]
    #[pyo3(signature = (data, options = None))]
    fn from_bytes(data: &[u8], options: Option<&PyParseOptions>) -> PyResult<Self> {
        let cursor = Cursor::new(data.to_vec());
        let reader = if let Some(opts) = options {
            oxidize_pdf::PdfReader::new_with_options(cursor, opts.inner.clone())
        } else {
            oxidize_pdf::PdfReader::new(cursor)
        }
        .map_err(parse_err_to_py)?;
        let encrypted = reader.is_encrypted();

        if encrypted {
            Ok(Self {
                state: ReaderState::RawCursor(reader),
                encrypted,
            })
        } else {
            Ok(Self {
                state: ReaderState::CursorDocument(oxidize_pdf::PdfDocument::new(reader)),
                encrypted,
            })
        }
    }

    /// Open a PDF from any binary stream (io.BinaryIO-compatible).
    ///
    /// The stream is read fully from its **current cursor position** into
    /// memory via `stream.read()`. The stream is NOT rewound — if you need
    /// to read from position 0, call `stream.seek(0)` yourself first.
    /// After this call, the stream cursor will be at end-of-stream.
    ///
    /// Any object with a `.read() -> bytes` method is accepted (e.g.
    /// `io.BytesIO`, `open(path, "rb")`, `urllib` responses read fully).
    /// Passing an object without `.read()` raises `AttributeError`; a
    /// `.read()` that returns text (str) raises `TypeError`.
    #[staticmethod]
    #[pyo3(signature = (stream, options = None))]
    fn from_stream(
        stream: &Bound<'_, PyAny>,
        options: Option<&PyParseOptions>,
    ) -> PyResult<Self> {
        let read_result = stream.call_method0("read")?;
        let data: Vec<u8> = read_result.extract()?;
        let cursor = Cursor::new(data);
        let reader = if let Some(opts) = options {
            oxidize_pdf::PdfReader::new_with_options(cursor, opts.inner.clone())
        } else {
            oxidize_pdf::PdfReader::new(cursor)
        }
        .map_err(parse_err_to_py)?;
        let encrypted = reader.is_encrypted();

        if encrypted {
            Ok(Self {
                state: ReaderState::RawCursor(reader),
                encrypted,
            })
        } else {
            Ok(Self {
                state: ReaderState::CursorDocument(oxidize_pdf::PdfDocument::new(reader)),
                encrypted,
            })
        }
    }

    /// Whether the PDF file is encrypted.
    #[getter]
    fn is_encrypted(&self) -> bool {
        self.encrypted
    }

    /// Unlock an encrypted PDF with the given password.
    ///
    /// The password is tried as both user and owner password.
    ///
    /// Raises:
    ///     PdfEncryptionError: If the password is incorrect.
    fn unlock(&mut self, password: &str) -> PyResult<()> {
        match &mut self.state {
            ReaderState::RawFile(ref mut reader) => {
                reader.unlock(password).map_err(parse_err_to_py)?;
            }
            ReaderState::RawCursor(ref mut reader) => {
                reader.unlock(password).map_err(parse_err_to_py)?;
            }
            _ => return Ok(()), // Already a Document — nothing to do.
        }
        self.promote();
        Ok(())
    }

    /// Number of pages in the document.
    #[getter]
    fn page_count(&mut self) -> PyResult<u32> {
        self.ensure_document();
        with_document!(self, doc => doc.page_count().map_err(parse_err_to_py))
    }

    /// PDF version string (e.g. ``"1.4"``).
    #[getter]
    fn version(&mut self) -> PyResult<String> {
        self.ensure_document();
        with_document!(self, doc => doc.version().map_err(parse_err_to_py))
    }

    /// Return the parsed page at the given 0-based index.
    fn get_page(&mut self, index: u32) -> PyResult<PyParsedPage> {
        self.ensure_document();
        let page = with_document!(self, doc => doc.get_page(index).map_err(parse_err_to_py))?;
        Ok(PyParsedPage { inner: page })
    }

    /// Extract text from a single page (0-based index).
    fn extract_text_from_page(&mut self, index: u32) -> PyResult<String> {
        self.ensure_document();
        let extracted =
            with_document!(self, doc => doc.extract_text_from_page(index).map_err(parse_err_to_py))?;
        Ok(extracted.text)
    }

    /// Extract text from all pages, returning a list of strings.
    fn extract_text(&mut self) -> PyResult<Vec<String>> {
        self.ensure_document();
        let texts = with_document!(self, doc => doc.extract_text().map_err(parse_err_to_py))?;
        Ok(texts.into_iter().map(|t| t.text).collect())
    }

    /// Extract text chunks with positional information from a page.
    ///
    /// Returns a list of ``TextChunk`` objects, each with ``text``, ``x``,
    /// ``y``, ``font_size``, and ``font_name`` attributes.
    fn extract_text_chunks(&mut self, index: u32) -> PyResult<Vec<PyTextChunk>> {
        self.ensure_document();

        // Get the parsed page and its content streams.
        let page = with_document!(self, doc => doc.get_page(index).map_err(parse_err_to_py))?;
        let streams =
            with_document!(self, doc => doc.get_page_content_streams(&page).map_err(parse_err_to_py))?;

        let mut streamer =
            oxidize_pdf::TextStreamer::new(oxidize_pdf::TextStreamOptions::default());

        let mut chunks = Vec::new();
        for stream_data in &streams {
            let mut page_chunks = streamer.process_chunk(stream_data).map_err(pdf_err_to_py)?;
            chunks.append(&mut page_chunks);
        }

        Ok(chunks
            .into_iter()
            .map(|c| PyTextChunk {
                text: c.text,
                x: c.x,
                y: c.y,
                font_size: c.font_size,
                font_name: c.font_name,
            })
            .collect())
    }

    /// Get document metadata (title, author, subject, etc.).
    fn metadata(&mut self) -> PyResult<PyDocumentMetadata> {
        self.ensure_document();
        let meta = with_document!(self, doc => doc.metadata().map_err(parse_err_to_py))?;
        Ok(PyDocumentMetadata {
            title: meta.title,
            author: meta.author,
            subject: meta.subject,
            keywords: meta.keywords,
            creator: meta.creator,
            producer: meta.producer,
            creation_date: meta.creation_date,
            modification_date: meta.modification_date,
            version: meta.version,
            page_count: meta.page_count,
        })
    }

    fn __len__(&mut self) -> PyResult<usize> {
        self.ensure_document();
        let count = with_document!(self, doc => doc.page_count().map_err(parse_err_to_py))?;
        Ok(count as usize)
    }

    /// Detect signature fields in the PDF.
    ///
    /// Returns a list of dicts with ``name``, ``filter``, and ``sub_filter`` keys.
    /// An unsigned PDF returns an empty list.
    fn detect_signatures<'py>(&mut self, py: Python<'py>) -> PyResult<Vec<Bound<'py, pyo3::types::PyDict>>> {
        use pyo3::types::PyDict;

        macro_rules! detect_on_reader {
            ($reader:expr) => {{
                let sigs = oxidize_pdf::signatures::detect_signature_fields($reader)
                    .map_err(|e| errors::PdfError::new_err(e.to_string()))?;
                let mut results = Vec::new();
                for sig in sigs {
                    let dict = PyDict::new(py);
                    dict.set_item("name", sig.name.clone().unwrap_or_default())?;
                    dict.set_item("filter", &sig.filter)?;
                    dict.set_item("sub_filter", &sig.sub_filter)?;
                    results.push(dict);
                }
                Ok(results)
            }};
        }

        match &mut self.state {
            ReaderState::RawFile(ref mut reader) => detect_on_reader!(reader),
            ReaderState::RawCursor(ref mut reader) => detect_on_reader!(reader),
            ReaderState::FileDocument(_) | ReaderState::CursorDocument(_) => {
                // detect_signature_fields requires raw PdfReader access.
                // After promotion, the reader is consumed — return empty list.
                Ok(Vec::new())
            }
            ReaderState::Transitioning => unreachable!(),
        }
    }

    /// Export document as Markdown.
    #[allow(deprecated, clippy::wrong_self_convention)]
    fn to_markdown(&mut self) -> PyResult<String> {
        self.ensure_document();
        with_document!(self, doc => doc.to_markdown().map_err(pdf_err_to_py))
    }

    /// Export document in contextual format (for LLM prompts).
    #[allow(deprecated, clippy::wrong_self_convention)]
    fn to_contextual(&mut self) -> PyResult<String> {
        self.ensure_document();
        with_document!(self, doc => doc.to_contextual().map_err(pdf_err_to_py))
    }

    /// Chunk document text for RAG pipeline (deprecated — prefer rag_chunks).
    #[allow(deprecated)]
    fn chunk(&mut self, chunk_size: usize, overlap: usize) -> PyResult<Vec<PyDocumentChunk>> {
        self.ensure_document();
        let chunks =
            with_document!(self, doc => doc.chunk_with(chunk_size, overlap).map_err(pdf_err_to_py))?;
        Ok(chunks.into_iter().map(|c| PyDocumentChunk { inner: c }).collect())
    }

    /// Chunk a single page (0-based index) into LLM-friendly pieces.
    ///
    /// Cross-bridge counterpart of .NET's `PdfExtractor.ExtractChunksFromPageAsync`
    /// (RAG-010 in `docs/PARITY_SPEC.md`). Each returned `DocumentChunk`
    /// carries `page_numbers = [page_index + 1]` so consumers can later
    /// merge per-page results into a single corpus and still know which
    /// page each chunk belongs to.
    ///
    /// Defaults match `DocumentChunker.default()` (512 tokens, 50 overlap).
    #[pyo3(signature = (page_index, chunk_size = 512, overlap = 50))]
    fn chunk_page(
        &mut self,
        page_index: u32,
        chunk_size: usize,
        overlap: usize,
    ) -> PyResult<Vec<PyDocumentChunk>> {
        // Bridge-level input validation. The underlying `DocumentChunker`
        // does not bounds-check `chunk_size` and enters an infinite loop
        // when it is 0 (slice never advances). Reject at the boundary
        // rather than hanging the worker thread.
        if chunk_size == 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "chunk_size must be > 0",
            ));
        }
        if overlap >= chunk_size {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "overlap ({overlap}) must be < chunk_size ({chunk_size})"
            )));
        }
        self.ensure_document();
        let extracted = with_document!(self, doc =>
            doc.extract_text_from_page(page_index).map_err(parse_err_to_py)
        )?;
        let chunker = DocumentChunker::new(chunk_size, overlap);
        let mut chunks = chunker.chunk_text(&extracted.text).map_err(pdf_err_to_py)?;
        // Stamp the source page on every chunk. The core's `chunk_text`
        // does not know which page the string came from, so without this
        // injection `page_numbers` would be empty and consumers would lose
        // the ability to filter/group by page after merging multiple
        // `chunk_page` calls.
        let page_number = (page_index as usize) + 1;
        for chunk in chunks.iter_mut() {
            chunk.page_numbers = vec![page_number];
        }
        Ok(chunks.into_iter().map(|c| PyDocumentChunk { inner: c }).collect())
    }

    /// Partition document into semantic elements.
    fn partition(&mut self) -> PyResult<Vec<PyElement>> {
        self.ensure_document();
        let elements =
            with_document!(self, doc => doc.partition().map_err(parse_err_to_py))?;
        Ok(elements.into_iter().map(|e| PyElement { inner: e }).collect())
    }

    /// Get RAG-ready chunks with default configuration.
    fn rag_chunks(&mut self) -> PyResult<Vec<PyRagChunk>> {
        self.ensure_document();
        let chunks =
            with_document!(self, doc => doc.rag_chunks().map_err(parse_err_to_py))?;
        Ok(chunks.into_iter().map(|c| PyRagChunk { inner: c }).collect())
    }

    /// Get RAG chunks with an extraction profile.
    fn rag_chunks_with_profile(
        &mut self,
        profile: &PyExtractionProfile,
    ) -> PyResult<Vec<PyRagChunk>> {
        self.ensure_document();
        let chunks = with_document!(self, doc =>
            doc.rag_chunks_with_profile(profile.inner.clone()).map_err(parse_err_to_py)
        )?;
        Ok(chunks.into_iter().map(|c| PyRagChunk { inner: c }).collect())
    }

    /// Extract text from all pages using advanced options.
    ///
    /// Returns a list of strings, one per page.
    fn extract_text_with_options(&mut self, options: &PyExtractionOptions) -> PyResult<Vec<String>> {
        self.ensure_document();
        let texts = with_document!(self, doc =>
            doc.extract_text_with_options(options.inner.clone()).map_err(parse_err_to_py)
        )?;
        Ok(texts.into_iter().map(|t| t.text).collect())
    }

    /// Extract plain text from a single page using PlainTextExtractor.
    ///
    /// Returns a ``PlainTextResult`` with text, line_count, and char_count.
    #[pyo3(signature = (page_index, config = None))]
    fn extract_plain_text(
        &mut self,
        page_index: u32,
        config: Option<&PyPlainTextConfig>,
    ) -> PyResult<PyPlainTextResult> {
        self.ensure_document();
        let mut extractor = if let Some(cfg) = config {
            oxidize_pdf::text::PlainTextExtractor::with_config(cfg.inner.clone())
        } else {
            oxidize_pdf::text::PlainTextExtractor::new()
        };
        let result = with_document!(self, doc =>
            extractor.extract(doc, page_index).map_err(parse_err_to_py)
        )?;
        Ok(PyPlainTextResult { inner: result })
    }

    /// Extract plain text lines from a single page.
    ///
    /// Returns a list of strings, one per detected line.
    #[pyo3(signature = (page_index, config = None))]
    fn extract_plain_text_lines(
        &mut self,
        page_index: u32,
        config: Option<&PyPlainTextConfig>,
    ) -> PyResult<Vec<String>> {
        self.ensure_document();
        let mut extractor = if let Some(cfg) = config {
            oxidize_pdf::text::PlainTextExtractor::with_config(cfg.inner.clone())
        } else {
            oxidize_pdf::text::PlainTextExtractor::new()
        };
        with_document!(self, doc =>
            extractor.extract_lines(doc, page_index).map_err(parse_err_to_py)
        )
    }

    /// Return the decoded content streams of the page at ``index``.
    ///
    /// The PDF ``/Contents`` entry may be a single stream or an array of
    /// streams; the bridge flattens both forms into a list of ``bytes``
    /// in writer-emission order. Each entry is the decoded (filters
    /// applied, e.g. FlateDecode removed) operator sequence — callers
    /// parse the PostScript-like content stream directly.
    ///
    /// Pages without a ``/Contents`` entry return an empty list. An out
    /// of range ``index`` raises ``PdfError``.
    fn get_page_content_streams(&mut self, index: u32) -> PyResult<Vec<Vec<u8>>> {
        self.ensure_document();
        with_document!(self, doc => {
            let page = doc.get_page(index).map_err(parse_err_to_py)?;
            doc.get_page_content_streams(&page).map_err(parse_err_to_py)
        })
    }

    /// Return the structured ``/Resources`` view of the page at ``index``.
    ///
    /// Returns ``None`` when the page has neither a direct ``/Resources``
    /// entry nor an inherited one. Raises ``PdfError`` if ``index`` is out
    /// of bounds.
    fn get_page_resources(
        &mut self,
        py: Python<'_>,
        index: u32,
    ) -> PyResult<Option<PyPageResources>> {
        self.ensure_document();
        with_document!(self, doc => {
            let page = doc.get_page(index).map_err(parse_err_to_py)?;
            let Some(resources) = page.get_resources() else {
                return Ok(None);
            };
            let resources = resources.clone();
            let built = build_page_resources(py, &resources, doc)?;
            Ok(Some(built))
        })
    }

    fn __repr__(&mut self) -> PyResult<String> {
        self.ensure_document();
        let count = with_document!(self, doc => doc.page_count().map_err(parse_err_to_py))?;
        Ok(format!("PdfReader(pages={count})"))
    }
}

// ── TextChunk ─────────────────────────────────────────────────────────────────

/// A chunk of extracted text with positional information.
#[pyclass(name = "TextChunk", frozen)]
struct PyTextChunk {
    #[pyo3(get)]
    text: String,
    #[pyo3(get)]
    x: f64,
    #[pyo3(get)]
    y: f64,
    #[pyo3(get)]
    font_size: f64,
    #[pyo3(get)]
    font_name: Option<String>,
}

#[pymethods]
impl PyTextChunk {
    fn __repr__(&self) -> String {
        format!(
            "TextChunk(text={:?}, x={}, y={}, font_size={})",
            self.text, self.x, self.y, self.font_size
        )
    }
}

// ── ParsedPage ────────────────────────────────────────────────────────────────

/// A page obtained from parsing an existing PDF.
///
/// Provides read-only access to page dimensions and rotation.
#[pyclass(name = "ParsedPage")]
struct PyParsedPage {
    inner: oxidize_pdf::ParsedPage,
}

#[pymethods]
impl PyParsedPage {
    /// Effective page width in points (accounts for rotation).
    #[getter]
    fn width(&self) -> f64 {
        self.inner.width()
    }

    /// Effective page height in points (accounts for rotation).
    #[getter]
    fn height(&self) -> f64 {
        self.inner.height()
    }

    /// Page rotation in degrees (0, 90, 180, or 270).
    #[getter]
    fn rotation(&self) -> i32 {
        self.inner.rotation
    }

    fn __repr__(&self) -> String {
        format!(
            "ParsedPage({}x{}, rotation={})",
            self.inner.width(),
            self.inner.height(),
            self.inner.rotation
        )
    }
}

// ── PageResources / FontResource / ImageResource / FormXObjectResource ───────

/// A font referenced by a page's ``/Resources /Font`` sub-dictionary.
#[pyclass(name = "FontResource", frozen)]
pub struct PyFontResource {
    /// Font subtype (``Type1``, ``TrueType``, ``Type0``, etc.).
    #[pyo3(get)]
    pub subtype: String,
    /// Value of ``/BaseFont`` (e.g. ``"Helvetica-Bold"`` or ``"ABCDEF+Arial"``).
    #[pyo3(get)]
    pub base_font: String,
    /// Name of the encoding dictionary or predefined encoding, if present.
    #[pyo3(get)]
    pub encoding: Option<String>,
    /// ``True`` if the font descriptor carries embedded font program data
    /// (``/FontFile``, ``/FontFile2`` or ``/FontFile3``).
    #[pyo3(get)]
    pub is_embedded: bool,
    /// ``True`` if ``base_font`` begins with a 6-letter subset tag like ``ABCDEF+``.
    #[pyo3(get)]
    pub is_subset: bool,
}

#[pymethods]
impl PyFontResource {
    fn __repr__(&self) -> String {
        format!(
            "FontResource(base_font={:?}, subtype={:?}, embedded={}, subset={})",
            self.base_font, self.subtype, self.is_embedded, self.is_subset,
        )
    }
}

/// An image (``/Subtype /Image`` XObject) referenced by a page's Resources.
#[pyclass(name = "ImageResource", frozen)]
pub struct PyImageResource {
    #[pyo3(get)]
    pub width: u32,
    #[pyo3(get)]
    pub height: u32,
    #[pyo3(get)]
    pub bits_per_component: u32,
    /// Filter chain, in application order (outermost last per PDF spec).
    #[pyo3(get)]
    pub filter: Vec<String>,
    /// Color-space name (``DeviceGray``, ``DeviceRGB``, ``ICCBased``, …).
    #[pyo3(get)]
    pub color_space: String,
}

#[pymethods]
impl PyImageResource {
    fn __repr__(&self) -> String {
        format!(
            "ImageResource({}x{}, bpc={}, color_space={:?}, filter={:?})",
            self.width, self.height, self.bits_per_component, self.color_space, self.filter,
        )
    }
}

/// A Form XObject (``/Subtype /Form``) referenced by a page's Resources.
///
/// Minimal shape for the current pass — extended as callers consume it.
#[pyclass(name = "FormXObjectResource", frozen)]
pub struct PyFormXObjectResource {
    /// Form bounding box ``(llx, lly, urx, ury)`` if declared.
    #[pyo3(get)]
    pub bbox: Option<(f64, f64, f64, f64)>,
}

#[pymethods]
impl PyFormXObjectResource {
    fn __repr__(&self) -> String {
        format!("FormXObjectResource(bbox={:?})", self.bbox)
    }
}

/// Structured view of a page's ``/Resources`` dictionary.
///
/// Unlike .NET's flat ``(fonts, images)`` shape — dictated by its JSON
/// boundary — Python uses a hierarchical form: each category is a dict
/// keyed by the resource name used in the page's content stream.
#[pyclass(name = "PageResources")]
pub struct PyPageResources {
    fonts: Py<pyo3::types::PyDict>,
    images: Py<pyo3::types::PyDict>,
    forms: Py<pyo3::types::PyDict>,
    ext_g_states: Py<pyo3::types::PyDict>,
    proc_sets: Vec<String>,
    resource_keys: Vec<String>,
}

#[pymethods]
impl PyPageResources {
    #[getter]
    fn fonts<'py>(&self, py: Python<'py>) -> Bound<'py, pyo3::types::PyDict> {
        self.fonts.bind(py).clone()
    }

    #[getter]
    fn images<'py>(&self, py: Python<'py>) -> Bound<'py, pyo3::types::PyDict> {
        self.images.bind(py).clone()
    }

    #[getter]
    fn forms<'py>(&self, py: Python<'py>) -> Bound<'py, pyo3::types::PyDict> {
        self.forms.bind(py).clone()
    }

    #[getter]
    fn ext_g_states<'py>(&self, py: Python<'py>) -> Bound<'py, pyo3::types::PyDict> {
        self.ext_g_states.bind(py).clone()
    }

    #[getter]
    fn proc_sets(&self) -> Vec<String> {
        self.proc_sets.clone()
    }

    #[getter]
    fn resource_keys(&self) -> Vec<String> {
        self.resource_keys.clone()
    }

    fn __repr__(&self) -> String {
        format!(
            "PageResources(keys={:?}, proc_sets={:?})",
            self.resource_keys, self.proc_sets,
        )
    }
}

/// Resolve an indirect reference to a dictionary-bearing object, returning
/// an owned `PdfDictionary`. For streams, returns the stream's dictionary.
fn resolve_to_dict<R: std::io::Read + std::io::Seek>(
    obj: &oxidize_pdf::parser::objects::PdfObject,
    doc: &oxidize_pdf::PdfDocument<R>,
) -> Option<oxidize_pdf::parser::objects::PdfDictionary> {
    use oxidize_pdf::parser::objects::PdfObject;
    let resolved = doc.resolve(obj).ok()?;
    match resolved {
        PdfObject::Dictionary(d) => Some(d),
        PdfObject::Stream(s) => Some(s.dict),
        _ => None,
    }
}

/// Look up a sub-dictionary by key inside a page's Resources, transparently
/// following an indirect reference if present. Returns None when the key is
/// absent or the target is not a dictionary.
fn get_sub_dict<R: std::io::Read + std::io::Seek>(
    parent: &oxidize_pdf::parser::objects::PdfDictionary,
    key: &str,
    doc: &oxidize_pdf::PdfDocument<R>,
) -> Option<oxidize_pdf::parser::objects::PdfDictionary> {
    use oxidize_pdf::parser::objects::PdfObject;
    match parent.get(key)? {
        PdfObject::Dictionary(d) => Some(d.clone()),
        obj @ PdfObject::Reference(_, _) => resolve_to_dict(obj, doc),
        _ => None,
    }
}

fn is_subset_font_name(name: &str) -> bool {
    let bytes = name.as_bytes();
    if bytes.len() < 8 {
        return false;
    }
    if bytes[6] != b'+' {
        return false;
    }
    bytes[..6].iter().all(|b| b.is_ascii_uppercase())
}

fn font_descriptor_has_font_file(fd_dict: &oxidize_pdf::parser::objects::PdfDictionary) -> bool {
    fd_dict.contains_key("FontFile")
        || fd_dict.contains_key("FontFile2")
        || fd_dict.contains_key("FontFile3")
}

/// Check whether a font carries embedded program data.
///
/// For simple fonts (``/Type1``, ``/TrueType``, ``/Type3``) we walk directly
/// into ``/FontDescriptor``. For composite fonts (``/Type0``) the descriptor
/// lives inside the CIDFont referenced by ``/DescendantFonts`` — the top-level
/// Type0 dictionary has no descriptor of its own. Without this second path
/// any embedded CJK / emoji font would be misreported as non-embedded.
fn has_embedded_font_data<R: std::io::Read + std::io::Seek>(
    font_dict: &oxidize_pdf::parser::objects::PdfDictionary,
    doc: &oxidize_pdf::PdfDocument<R>,
) -> bool {
    use oxidize_pdf::parser::objects::PdfObject;

    if let Some(fd_obj) = font_dict.get("FontDescriptor") {
        if let Some(fd_dict) = resolve_to_dict(fd_obj, doc) {
            if font_descriptor_has_font_file(&fd_dict) {
                return true;
            }
        }
    }

    // Composite fonts: descend into /DescendantFonts.
    let Some(desc_obj) = font_dict.get("DescendantFonts") else {
        return false;
    };
    let resolved = match desc_obj {
        PdfObject::Reference(_, _) => match doc.resolve(desc_obj).ok() {
            Some(o) => o,
            None => return false,
        },
        other => other.clone(),
    };
    let PdfObject::Array(arr) = resolved else {
        return false;
    };
    for entry in &arr.0 {
        let Some(cid_dict) = resolve_to_dict(entry, doc) else {
            continue;
        };
        if let Some(fd_obj) = cid_dict.get("FontDescriptor") {
            if let Some(fd_dict) = resolve_to_dict(fd_obj, doc) {
                if font_descriptor_has_font_file(&fd_dict) {
                    return true;
                }
            }
        }
    }
    false
}

fn build_font_resource<R: std::io::Read + std::io::Seek>(
    font_obj: &oxidize_pdf::parser::objects::PdfObject,
    doc: &oxidize_pdf::PdfDocument<R>,
) -> Option<PyFontResource> {
    use oxidize_pdf::parser::objects::PdfObject;

    let font_dict = resolve_to_dict(font_obj, doc)?;

    let subtype = font_dict
        .get("Subtype")
        .and_then(|o| o.as_name())
        .map(|n| n.0.clone())
        .unwrap_or_default();

    let base_font = font_dict
        .get("BaseFont")
        .and_then(|o| o.as_name())
        .map(|n| n.0.clone())
        .unwrap_or_default();

    let encoding = font_dict.get("Encoding").and_then(|o| {
        let resolved = match o {
            PdfObject::Reference(_, _) => doc.resolve(o).ok()?,
            other => other.clone(),
        };
        match resolved {
            PdfObject::Name(n) => Some(n.0),
            PdfObject::Dictionary(d) => d
                .get("BaseEncoding")
                .and_then(|be| be.as_name())
                .map(|n| n.0.clone()),
            _ => None,
        }
    });

    let is_subset = is_subset_font_name(&base_font);
    let is_embedded = has_embedded_font_data(&font_dict, doc);

    Some(PyFontResource {
        subtype,
        base_font,
        encoding,
        is_embedded,
        is_subset,
    })
}

fn build_image_resource<R: std::io::Read + std::io::Seek>(
    xobj: &oxidize_pdf::parser::objects::PdfObject,
    doc: &oxidize_pdf::PdfDocument<R>,
) -> Option<PyImageResource> {
    use oxidize_pdf::parser::objects::PdfObject;

    let dict = resolve_to_dict(xobj, doc)?;

    let to_u32 = |key: &str| -> u32 {
        dict.get(key)
            .and_then(|o| o.as_integer())
            .and_then(|i| u32::try_from(i).ok())
            .unwrap_or(0)
    };
    let width = to_u32("Width");
    let height = to_u32("Height");
    let bits_per_component = to_u32("BitsPerComponent");

    let filter = match dict.get("Filter") {
        Some(PdfObject::Name(n)) => vec![n.0.clone()],
        Some(PdfObject::Array(arr)) => arr
            .0
            .iter()
            .filter_map(|o| o.as_name().map(|n| n.0.clone()))
            .collect(),
        _ => Vec::new(),
    };

    let color_space_obj = dict.get("ColorSpace").and_then(|o| match o {
        PdfObject::Reference(_, _) => doc.resolve(o).ok(),
        other => Some(other.clone()),
    });
    let color_space = match color_space_obj {
        Some(PdfObject::Name(n)) => n.0,
        Some(PdfObject::Array(arr)) => arr
            .0
            .first()
            .and_then(|o| o.as_name())
            .map(|n| n.0.clone())
            .unwrap_or_default(),
        _ => String::new(),
    };

    Some(PyImageResource {
        width,
        height,
        bits_per_component,
        filter,
        color_space,
    })
}

fn build_form_resource<R: std::io::Read + std::io::Seek>(
    xobj: &oxidize_pdf::parser::objects::PdfObject,
    doc: &oxidize_pdf::PdfDocument<R>,
) -> Option<PyFormXObjectResource> {
    use oxidize_pdf::parser::objects::PdfObject;

    let dict = resolve_to_dict(xobj, doc)?;
    let bbox = match dict.get("BBox") {
        Some(PdfObject::Array(arr)) if arr.0.len() == 4 => {
            let vals: Vec<f64> = arr
                .0
                .iter()
                .map(|o| {
                    o.as_real()
                        .or_else(|| o.as_integer().map(|i| i as f64))
                        .unwrap_or(0.0)
                })
                .collect();
            Some((vals[0], vals[1], vals[2], vals[3]))
        }
        _ => None,
    };
    Some(PyFormXObjectResource { bbox })
}

/// Maximum recursion depth when converting nested PDF objects to Python.
/// Beyond this the converter collapses to ``None`` instead of risking a
/// stack overflow on adversarial or circular-resolved input.
const PDF_TO_PY_MAX_DEPTH: u8 = 64;

/// Convert a `PdfObject` into a Python primitive. Streams and unresolved
/// references collapse to ``None`` — callers that need those branches should
/// drop to the core layer directly. Recursion is bounded by
/// [`PDF_TO_PY_MAX_DEPTH`].
fn pdf_object_to_py(
    py: Python<'_>,
    obj: &oxidize_pdf::parser::objects::PdfObject,
    depth: u8,
) -> PyResult<Py<PyAny>> {
    use oxidize_pdf::parser::objects::PdfObject;
    use pyo3::types::{PyBool, PyBytes, PyDict, PyFloat, PyInt, PyList, PyString};

    if depth >= PDF_TO_PY_MAX_DEPTH {
        return Ok(py.None());
    }

    match obj {
        PdfObject::Null => Ok(py.None()),
        PdfObject::Boolean(b) => Ok(PyBool::new(py, *b).to_owned().into_any().unbind()),
        PdfObject::Integer(i) => Ok(PyInt::new(py, *i).into_any().unbind()),
        PdfObject::Real(f) => Ok(PyFloat::new(py, *f).into_any().unbind()),
        PdfObject::Name(n) => Ok(PyString::new(py, &n.0).into_any().unbind()),
        PdfObject::String(s) => match s.as_str() {
            Ok(text) => Ok(PyString::new(py, text).into_any().unbind()),
            Err(_) => Ok(PyBytes::new(py, s.as_bytes()).into_any().unbind()),
        },
        PdfObject::Array(arr) => {
            let list = PyList::empty(py);
            for item in &arr.0 {
                list.append(pdf_object_to_py(py, item, depth + 1)?)?;
            }
            Ok(list.into_any().unbind())
        }
        PdfObject::Dictionary(d) => {
            let dict = PyDict::new(py);
            for (k, v) in &d.0 {
                dict.set_item(&k.0, pdf_object_to_py(py, v, depth + 1)?)?;
            }
            Ok(dict.into_any().unbind())
        }
        PdfObject::Reference(_, _) | PdfObject::Stream(_) => Ok(py.None()),
    }
}

fn build_page_resources<R: std::io::Read + std::io::Seek>(
    py: Python<'_>,
    resources: &oxidize_pdf::parser::objects::PdfDictionary,
    doc: &oxidize_pdf::PdfDocument<R>,
) -> PyResult<PyPageResources> {
    use oxidize_pdf::parser::objects::PdfObject;
    use pyo3::types::PyDict;

    let fonts = PyDict::new(py);
    let images = PyDict::new(py);
    let forms = PyDict::new(py);
    let ext_g_states = PyDict::new(py);
    let mut proc_sets: Vec<String> = Vec::new();

    if let Some(font_dict) = get_sub_dict(resources, "Font", doc) {
        for (name, font_obj) in &font_dict.0 {
            if let Some(font) = build_font_resource(font_obj, doc) {
                fonts.set_item(&name.0, Py::new(py, font)?)?;
            }
        }
    }

    if let Some(xo_dict) = get_sub_dict(resources, "XObject", doc) {
        for (name, xo_obj) in &xo_dict.0 {
            let Some(xo_dict_resolved) = resolve_to_dict(xo_obj, doc) else {
                continue;
            };
            let subtype = xo_dict_resolved
                .get("Subtype")
                .and_then(|o| o.as_name())
                .map(|n| n.0.as_str())
                .unwrap_or_default();
            match subtype {
                "Image" => {
                    if let Some(img) = build_image_resource(xo_obj, doc) {
                        images.set_item(&name.0, Py::new(py, img)?)?;
                    }
                }
                "Form" => {
                    if let Some(form) = build_form_resource(xo_obj, doc) {
                        forms.set_item(&name.0, Py::new(py, form)?)?;
                    }
                }
                _ => {}
            }
        }
    }

    if let Some(gs_dict) = get_sub_dict(resources, "ExtGState", doc) {
        for (name, gs_obj) in &gs_dict.0 {
            let Some(gs_entry) = resolve_to_dict(gs_obj, doc) else {
                continue;
            };
            let entry_dict = PyDict::new(py);
            for (k, v) in &gs_entry.0 {
                entry_dict.set_item(&k.0, pdf_object_to_py(py, v, 0)?)?;
            }
            ext_g_states.set_item(&name.0, entry_dict)?;
        }
    }

    if let Some(ps_obj) = resources.get("ProcSet") {
        let resolved = match ps_obj {
            PdfObject::Reference(_, _) => doc.resolve(ps_obj).ok(),
            other => Some(other.clone()),
        };
        if let Some(PdfObject::Array(arr)) = resolved {
            for item in &arr.0 {
                if let Some(n) = item.as_name() {
                    proc_sets.push(n.0.clone());
                }
            }
        }
    }

    let resource_keys: Vec<String> = resources.0.keys().map(|n| n.0.clone()).collect();

    Ok(PyPageResources {
        fonts: fonts.unbind(),
        images: images.unbind(),
        forms: forms.unbind(),
        ext_g_states: ext_g_states.unbind(),
        proc_sets,
        resource_keys,
    })
}

// ── verify_pdf_signatures ─────────────────────────────────────────────────────

/// Verify digital signatures in a PDF byte buffer.
///
/// Returns a list of dicts, one per signature field, with keys:
/// ``name``, ``filter``, ``sub_filter``, ``valid`` (bool), ``error`` (str or None).
///
/// NOTE: The "signatures" feature is not compiled in by default. When absent the
/// parse_pkcs7_signature call returns Err immediately, so ``valid`` will be false
/// and ``error`` will describe why verification was skipped.
#[pyfunction]
fn verify_pdf_signatures<'py>(
    pdf_bytes: &[u8],
    py: Python<'py>,
) -> PyResult<Vec<Bound<'py, pyo3::types::PyDict>>> {
    use pyo3::types::PyDict;
    use std::io::Cursor;

    let cursor = Cursor::new(pdf_bytes.to_vec());
    let mut reader = oxidize_pdf::PdfReader::new(cursor)
        .map_err(|e| errors::PdfParseError::new_err(e.to_string()))?;

    let sig_fields = oxidize_pdf::signatures::detect_signature_fields(&mut reader)
        .map_err(|e| errors::PdfError::new_err(e.to_string()))?;

    let mut results = Vec::new();
    for field in sig_fields {
        let dict = PyDict::new(py);
        dict.set_item("name", field.name.clone().unwrap_or_default())?;
        dict.set_item("filter", &field.filter)?;
        dict.set_item("sub_filter", &field.sub_filter)?;

        match oxidize_pdf::signatures::parse_pkcs7_signature(&field.contents) {
            Ok(parsed) => {
                let verify_ok =
                    oxidize_pdf::signatures::verify_signature(pdf_bytes, &parsed, &field.byte_range)
                        .is_ok();
                dict.set_item("valid", verify_ok)?;
                dict.set_item("error", py.None())?;
            }
            Err(e) => {
                dict.set_item("valid", false)?;
                dict.set_item("error", e.to_string())?;
            }
        }
        results.push(dict);
    }

    Ok(results)
}

// ── Registration ──────────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyParseOptions>()?;
    m.add_class::<PyDocumentMetadata>()?;
    m.add_class::<PyPdfReader>()?;
    m.add_class::<PyParsedPage>()?;
    m.add_class::<PyTextChunk>()?;
    m.add_class::<PyFontResource>()?;
    m.add_class::<PyImageResource>()?;
    m.add_class::<PyFormXObjectResource>()?;
    m.add_class::<PyPageResources>()?;
    m.add_function(wrap_pyfunction!(verify_pdf_signatures, m)?)?;
    Ok(())
}
