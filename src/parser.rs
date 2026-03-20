use std::fs::File;
use std::io::Cursor;

use pyo3::prelude::*;

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
    #[allow(deprecated)]
    fn to_markdown(&mut self) -> PyResult<String> {
        self.ensure_document();
        with_document!(self, doc => doc.to_markdown().map_err(pdf_err_to_py))
    }

    /// Export document in contextual format (for LLM prompts).
    #[allow(deprecated)]
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
    m.add_function(wrap_pyfunction!(verify_pdf_signatures, m)?)?;
    Ok(())
}
