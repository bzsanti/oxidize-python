use std::fs::File;

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

/// Internal state of PyPdfReader.
///
/// When first opened on an encrypted file, we hold a raw `PdfReader` so
/// that `unlock` can work. Once the reader is ready (not encrypted or
/// successfully unlocked), we promote it to a `PdfDocument`.
enum ReaderState {
    /// Raw reader — encrypted, not yet unlocked.
    Raw(oxidize_pdf::PdfReader<File>),
    /// High-level document wrapper (ready for queries).
    Document(oxidize_pdf::PdfDocument<File>),
    /// Transient state during promotion (never visible to callers).
    Transitioning,
}

// ── PdfReader ─────────────────────────────────────────────────────────────────

/// High-level PDF reader for parsing existing PDF files.
///
/// Example::
///
///     reader = PdfReader.open("document.pdf")
///     if reader.is_encrypted:
///         reader.unlock("password")
///     print(f"Pages: {len(reader)}")
///     text = reader.extract_text_from_page(0)
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
            ReaderState::Raw(reader) => {
                ReaderState::Document(oxidize_pdf::PdfDocument::new(reader))
            }
            other => other,
        };
    }

    /// Get a reference to the inner PdfDocument, promoting from Raw if needed.
    fn document(&mut self) -> PyResult<&oxidize_pdf::PdfDocument<File>> {
        if matches!(self.state, ReaderState::Raw(_)) {
            self.promote();
        }
        match &self.state {
            ReaderState::Document(doc) => Ok(doc),
            _ => unreachable!("promote() guarantees Document state"),
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
            // Keep as Raw so user can call unlock().
            Ok(Self {
                state: ReaderState::Raw(reader),
                encrypted,
            })
        } else {
            // Promote immediately.
            Ok(Self {
                state: ReaderState::Document(oxidize_pdf::PdfDocument::new(reader)),
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
        if let ReaderState::Raw(ref mut reader) = self.state {
            reader.unlock(password).map_err(parse_err_to_py)?;
            self.promote();
        }
        // Already a Document — nothing to do.
        Ok(())
    }

    /// Number of pages in the document.
    #[getter]
    fn page_count(&mut self) -> PyResult<u32> {
        self.document()?.page_count().map_err(parse_err_to_py)
    }

    /// PDF version string (e.g. ``"1.4"``).
    #[getter]
    fn version(&mut self) -> PyResult<String> {
        self.document()?.version().map_err(parse_err_to_py)
    }

    /// Return the parsed page at the given 0-based index.
    fn get_page(&mut self, index: u32) -> PyResult<PyParsedPage> {
        let page = self.document()?.get_page(index).map_err(parse_err_to_py)?;
        Ok(PyParsedPage { inner: page })
    }

    /// Extract text from a single page (0-based index).
    fn extract_text_from_page(&mut self, index: u32) -> PyResult<String> {
        let extracted = self
            .document()?
            .extract_text_from_page(index)
            .map_err(parse_err_to_py)?;
        Ok(extracted.text)
    }

    /// Extract text from all pages, returning a list of strings.
    fn extract_text(&mut self) -> PyResult<Vec<String>> {
        let texts = self.document()?.extract_text().map_err(parse_err_to_py)?;
        Ok(texts.into_iter().map(|t| t.text).collect())
    }

    fn __len__(&mut self) -> PyResult<usize> {
        let count = self.document()?.page_count().map_err(parse_err_to_py)?;
        Ok(count as usize)
    }

    fn __repr__(&mut self) -> PyResult<String> {
        let count = self.document()?.page_count().map_err(parse_err_to_py)?;
        Ok(format!("PdfReader(pages={count})"))
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
    Ok(())
}
