use pyo3::exceptions::PyException;
use pyo3::prelude::*;

// Base exception for all oxidize-pdf errors
pyo3::create_exception!(oxidize_pdf, PdfError, PyException, "Base exception for all oxidize-pdf errors.");

// Specialized subclasses
pyo3::create_exception!(oxidize_pdf, PdfParseError, PdfError, "Raised when PDF parsing fails.");
pyo3::create_exception!(oxidize_pdf, PdfIoError, PdfError, "Raised on I/O errors (file not found, permission denied, etc.).");
pyo3::create_exception!(oxidize_pdf, PdfEncryptionError, PdfError, "Raised on encryption/decryption errors.");
pyo3::create_exception!(oxidize_pdf, PdfPermissionError, PdfError, "Raised when an operation is denied by document permissions.");

/// Convert a Rust `oxidize_pdf::PdfError` into the appropriate Python exception.
pub fn to_py_err(err: oxidize_pdf::PdfError) -> PyErr {
    use oxidize_pdf::PdfError as E;

    match &err {
        E::Io(_) => PdfIoError::new_err(err.to_string()),
        E::ParseError(_) | E::InvalidStructure(_) | E::InvalidReference(_)
        | E::InvalidObjectReference(_, _) | E::InvalidHeader | E::InvalidFormat(_) => {
            PdfParseError::new_err(err.to_string())
        }
        E::EncryptionError(_) => PdfEncryptionError::new_err(err.to_string()),
        E::PermissionDenied(_) => PdfPermissionError::new_err(err.to_string()),
        _ => PdfError::new_err(err.to_string()),
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("PdfError", m.py().get_type::<PdfError>())?;
    m.add("PdfParseError", m.py().get_type::<PdfParseError>())?;
    m.add("PdfIoError", m.py().get_type::<PdfIoError>())?;
    m.add("PdfEncryptionError", m.py().get_type::<PdfEncryptionError>())?;
    m.add("PdfPermissionError", m.py().get_type::<PdfPermissionError>())?;
    Ok(())
}
