use pyo3::prelude::*;

use crate::errors;

/// Convert an `OperationError` into the appropriate Python exception.
fn op_err_to_py(err: oxidize_pdf::operations::OperationError) -> PyErr {
    use oxidize_pdf::operations::OperationError as OE;

    match err {
        OE::Io(io_err) => errors::PdfIoError::new_err(format!("IO error: {io_err}")),
        OE::PdfError(pdf_err) => crate::errors::to_py_err(pdf_err),
        OE::PageIndexOutOfBounds(idx, total) => errors::PdfError::new_err(format!(
            "Page index {idx} out of bounds (document has {total} pages)"
        )),
        OE::InvalidPageRange(msg) => {
            errors::PdfError::new_err(format!("Invalid page range: {msg}"))
        }
        OE::NoPagesToProcess => errors::PdfError::new_err("No pages to process"),
        OE::InvalidRotation(deg) => {
            errors::PdfError::new_err(format!("Invalid rotation angle: {deg}"))
        }
        _ => errors::PdfError::new_err(err.to_string()),
    }
}

// ── split_pdf ─────────────────────────────────────────────────────────────────

/// Split a PDF into individual single-page files.
///
/// Args:
///     input_path: Path to the input PDF file.
///     output_dir: Directory where split pages will be written.
///         Files are named ``page_1.pdf``, ``page_2.pdf``, etc.
///
/// Returns:
///     A list of paths to the created files.
///
/// Raises:
///     PdfError: If the input file cannot be read or split.
///     PdfIoError: If there is an I/O error.
#[pyfunction]
fn split_pdf(input_path: &str, output_dir: &str) -> PyResult<Vec<String>> {
    let pattern = format!("{}/page_{{}}.pdf", output_dir);
    let result = oxidize_pdf::operations::split_into_pages(input_path, &pattern)
        .map_err(op_err_to_py)?;
    Ok(result.into_iter().map(|p| p.to_string_lossy().into_owned()).collect())
}

// ── merge_pdfs ────────────────────────────────────────────────────────────────

/// Merge multiple PDF files into a single output file.
///
/// Args:
///     input_paths: List of paths to PDF files to merge (in order).
///     output_path: Path where the merged PDF will be written.
///
/// Raises:
///     PdfError: If any input file cannot be read or the merge fails.
///     PdfIoError: If there is an I/O error.
///     ValueError: If the input list is empty.
#[pyfunction]
fn merge_pdfs(input_paths: Vec<String>, output_path: &str) -> PyResult<()> {
    if input_paths.is_empty() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "At least one input file is required",
        ));
    }

    let inputs: Vec<oxidize_pdf::operations::MergeInput> = input_paths
        .iter()
        .map(|p| oxidize_pdf::operations::MergeInput::new(p))
        .collect();

    oxidize_pdf::operations::merge_pdfs(
        inputs,
        output_path,
        oxidize_pdf::operations::MergeOptions::default(),
    )
    .map_err(op_err_to_py)
}

// ── rotate_pdf ────────────────────────────────────────────────────────────────

/// Rotate all pages of a PDF by the given angle.
///
/// Args:
///     input_path: Path to the input PDF file.
///     output_path: Path where the rotated PDF will be written.
///     degrees: Rotation angle in degrees. Must be 0, 90, 180, or 270.
///
/// Raises:
///     PdfError: If the rotation angle is invalid or the file cannot be processed.
///     PdfIoError: If there is an I/O error.
#[pyfunction]
fn rotate_pdf(input_path: &str, output_path: &str, degrees: i32) -> PyResult<()> {
    let angle = oxidize_pdf::operations::RotationAngle::from_degrees(degrees)
        .map_err(op_err_to_py)?;

    oxidize_pdf::operations::rotate_all_pages(input_path, output_path, angle)
        .map_err(op_err_to_py)
}

// ── extract_pages ─────────────────────────────────────────────────────────────

/// Extract specific pages from a PDF into a new file.
///
/// Args:
///     input_path: Path to the input PDF file.
///     output_path: Path where the extracted pages will be written.
///     page_indices: List of 0-based page indices to extract.
///
/// Raises:
///     PdfError: If a page index is out of bounds or the file cannot be processed.
///     PdfIoError: If there is an I/O error.
///     ValueError: If the page list is empty.
#[pyfunction]
fn extract_pages(input_path: &str, output_path: &str, page_indices: Vec<usize>) -> PyResult<()> {
    if page_indices.is_empty() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "At least one page index is required",
        ));
    }

    oxidize_pdf::operations::extract_pages_to_file(input_path, &page_indices, output_path)
        .map_err(op_err_to_py)
}

// ── Registration ──────────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(split_pdf, m)?)?;
    m.add_function(wrap_pyfunction!(merge_pdfs, m)?)?;
    m.add_function(wrap_pyfunction!(rotate_pdf, m)?)?;
    m.add_function(wrap_pyfunction!(extract_pages, m)?)?;
    Ok(())
}
