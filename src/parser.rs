use std::fs::File;
use std::io::Cursor;

use pyo3::prelude::*;

use crate::errors;

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
    errors::PdfError::new_err(err.to_string())
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
    fn open(path: &str) -> PyResult<Self> {
        let reader = oxidize_pdf::PdfReader::open(path).map_err(parse_err_to_py)?;
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
    fn from_bytes(data: &[u8]) -> PyResult<Self> {
        let cursor = Cursor::new(data.to_vec());
        let reader = oxidize_pdf::PdfReader::new(cursor).map_err(parse_err_to_py)?;
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
            // For promoted documents, re-open the file to get a fresh reader
            ReaderState::FileDocument(_) | ReaderState::CursorDocument(_) => {
                // No signatures detected after promotion — return empty
                // (detect_signature_fields requires raw PdfReader access)
                Ok(Vec::new())
            }
            ReaderState::Transitioning => unreachable!(),
        }
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

// ── Registration ──────────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPdfReader>()?;
    m.add_class::<PyParsedPage>()?;
    m.add_class::<PyTextChunk>()?;
    Ok(())
}
