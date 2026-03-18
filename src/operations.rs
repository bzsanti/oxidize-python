use pyo3::prelude::*;
use pyo3::types::PyDict;

use oxidize_pdf::operations::{
    self, ExtractImagesOptions, MergeInput, MergeOptions, OperationError, OverlayOptions,
    OverlayPosition, RotationAngle,
};

use crate::errors;

/// Convert an `OperationError` into the appropriate Python exception.
fn op_err_to_py(err: OperationError) -> PyErr {
    match err {
        OperationError::Io(io_err) => errors::PdfIoError::new_err(format!("IO error: {io_err}")),
        OperationError::PdfError(pdf_err) => errors::to_py_err(pdf_err),
        OperationError::PageIndexOutOfBounds(idx, total) => errors::PdfError::new_err(format!(
            "Page index {idx} out of bounds (document has {total} pages)"
        )),
        OperationError::InvalidPageRange(msg) => {
            errors::PdfError::new_err(format!("Invalid page range: {msg}"))
        }
        OperationError::NoPagesToProcess => errors::PdfError::new_err("No pages to process"),
        OperationError::InvalidRotation(deg) => {
            errors::PdfError::new_err(format!("Invalid rotation angle: {deg}"))
        }
        _ => errors::PdfError::new_err(err.to_string()),
    }
}

// ── split_pdf ─────────────────────────────────────────────────────────────────

#[pyfunction]
fn split_pdf(input_path: &str, output_dir: &str) -> PyResult<Vec<String>> {
    let pattern = format!("{}/page_{{}}.pdf", output_dir);
    let result = operations::split_into_pages(input_path, &pattern).map_err(op_err_to_py)?;
    Ok(result
        .into_iter()
        .map(|p| p.to_string_lossy().into_owned())
        .collect())
}

// ── merge_pdfs ────────────────────────────────────────────────────────────────

#[pyfunction]
fn merge_pdfs(input_paths: Vec<String>, output_path: &str) -> PyResult<()> {
    if input_paths.is_empty() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "At least one input file is required",
        ));
    }
    let inputs: Vec<MergeInput> = input_paths.iter().map(|p| MergeInput::new(p)).collect();
    operations::merge_pdfs(inputs, output_path, MergeOptions::default()).map_err(op_err_to_py)
}

// ── rotate_pdf ────────────────────────────────────────────────────────────────

#[pyfunction]
fn rotate_pdf(input_path: &str, output_path: &str, degrees: i32) -> PyResult<()> {
    let angle = RotationAngle::from_degrees(degrees).map_err(op_err_to_py)?;
    operations::rotate_all_pages(input_path, output_path, angle).map_err(op_err_to_py)
}

// ── extract_pages ─────────────────────────────────────────────────────────────

#[pyfunction]
fn extract_pages(input_path: &str, output_path: &str, page_indices: Vec<usize>) -> PyResult<()> {
    if page_indices.is_empty() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "At least one page index is required",
        ));
    }
    operations::extract_pages_to_file(input_path, &page_indices, output_path)
        .map_err(op_err_to_py)
}

// ── Feature 6: Page Reorder/Swap/Move/Reverse ────────────────────────────────

#[pyfunction]
fn reorder_pdf_pages(input: &str, output: &str, page_order: Vec<usize>) -> PyResult<()> {
    operations::reorder_pdf_pages(input, output, page_order).map_err(op_err_to_py)
}

#[pyfunction]
fn swap_pdf_pages(input: &str, output: &str, page_a: usize, page_b: usize) -> PyResult<()> {
    operations::swap_pdf_pages(input, output, page_a, page_b).map_err(op_err_to_py)
}

#[pyfunction]
fn move_pdf_page(
    input: &str,
    output: &str,
    from_index: usize,
    to_index: usize,
) -> PyResult<()> {
    operations::move_pdf_page(input, output, from_index, to_index).map_err(op_err_to_py)
}

#[pyfunction]
fn reverse_pdf_pages(input: &str, output: &str) -> PyResult<()> {
    operations::reverse_pdf_pages(input, output).map_err(op_err_to_py)
}

// ── Feature 7: Overlay PDF ───────────────────────────────────────────────────

#[pyclass(name = "OverlayPosition", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyOverlayPosition {
    pub inner: OverlayPosition,
}

#[pymethods]
impl PyOverlayPosition {
    #[classattr]
    const CENTER: PyOverlayPosition = PyOverlayPosition {
        inner: OverlayPosition::Center,
    };
    #[classattr]
    const TOP_LEFT: PyOverlayPosition = PyOverlayPosition {
        inner: OverlayPosition::TopLeft,
    };
    #[classattr]
    const TOP_RIGHT: PyOverlayPosition = PyOverlayPosition {
        inner: OverlayPosition::TopRight,
    };
    #[classattr]
    const BOTTOM_LEFT: PyOverlayPosition = PyOverlayPosition {
        inner: OverlayPosition::BottomLeft,
    };
    #[classattr]
    const BOTTOM_RIGHT: PyOverlayPosition = PyOverlayPosition {
        inner: OverlayPosition::BottomRight,
    };

    fn __repr__(&self) -> String {
        let name = match &self.inner {
            OverlayPosition::Center => "CENTER",
            OverlayPosition::TopLeft => "TOP_LEFT",
            OverlayPosition::TopRight => "TOP_RIGHT",
            OverlayPosition::BottomLeft => "BOTTOM_LEFT",
            OverlayPosition::BottomRight => "BOTTOM_RIGHT",
            _ => "CUSTOM",
        };
        format!("OverlayPosition.{name}")
    }
}

#[pyclass(name = "OverlayOptions", from_py_object)]
#[derive(Clone)]
pub struct PyOverlayOptions {
    pub inner: OverlayOptions,
}

#[pymethods]
impl PyOverlayOptions {
    #[new]
    #[pyo3(signature = (position=None, opacity=None, scale=None, repeat=None))]
    fn new(
        position: Option<&PyOverlayPosition>,
        opacity: Option<f64>,
        scale: Option<f64>,
        repeat: Option<bool>,
    ) -> Self {
        let mut opts = OverlayOptions::default();
        if let Some(p) = position {
            opts.position = p.inner.clone();
        }
        if let Some(o) = opacity {
            opts.opacity = o;
        }
        if let Some(s) = scale {
            opts.scale = s;
        }
        if let Some(r) = repeat {
            opts.repeat = r;
        }
        Self { inner: opts }
    }

    fn __repr__(&self) -> String {
        format!(
            "OverlayOptions(opacity={}, scale={})",
            self.inner.opacity, self.inner.scale
        )
    }
}

#[pyfunction]
fn overlay_pdf(
    base: &str,
    overlay: &str,
    output: &str,
    options: &PyOverlayOptions,
) -> PyResult<()> {
    operations::overlay_pdf(base, overlay, output, options.inner.clone()).map_err(op_err_to_py)
}

// ── Feature 8: Extract Images ────────────────────────────────────────────────

#[pyclass(name = "ExtractImagesOptions", from_py_object)]
#[derive(Clone)]
pub struct PyExtractImagesOptions {
    pub inner: ExtractImagesOptions,
}

#[pymethods]
impl PyExtractImagesOptions {
    #[new]
    #[pyo3(signature = (output_dir, extract_inline=None, min_size=None))]
    fn new(output_dir: &str, extract_inline: Option<bool>, min_size: Option<u32>) -> Self {
        let mut opts = ExtractImagesOptions::default();
        opts.output_dir = std::path::PathBuf::from(output_dir);
        if let Some(ei) = extract_inline {
            opts.extract_inline = ei;
        }
        if let Some(ms) = min_size {
            opts.min_size = Some(ms);
        }
        Self { inner: opts }
    }

    fn __repr__(&self) -> String {
        format!(
            "ExtractImagesOptions(output_dir={:?})",
            self.inner.output_dir
        )
    }
}

#[pyfunction]
fn extract_images_from_pdf<'py>(
    input: &str,
    options: &PyExtractImagesOptions,
    py: Python<'py>,
) -> PyResult<Vec<Bound<'py, PyDict>>> {
    let results =
        operations::extract_images_from_pdf(input, options.inner.clone()).map_err(op_err_to_py)?;
    let mut py_results = Vec::new();
    for img in results {
        let dict = PyDict::new(py);
        dict.set_item("page_number", img.page_number)?;
        dict.set_item("image_index", img.image_index)?;
        dict.set_item("file_path", img.file_path.to_string_lossy().to_string())?;
        dict.set_item("width", img.width)?;
        dict.set_item("height", img.height)?;
        py_results.push(dict);
    }
    Ok(py_results)
}

// ── Feature 10: Save-to-bytes variants ───────────────────────────────────────

#[pyfunction]
fn merge_pdfs_to_bytes(input_paths: Vec<String>) -> PyResult<Vec<u8>> {
    if input_paths.is_empty() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "At least one input file is required",
        ));
    }
    let inputs: Vec<MergeInput> = input_paths.iter().map(|p| MergeInput::new(p)).collect();

    // Merge to temp file, then read bytes
    let tmpdir =
        tempfile::tempdir().map_err(|e| errors::PdfIoError::new_err(e.to_string()))?;
    let tmp_output = tmpdir.path().join("merged.pdf");

    operations::merge_pdfs(inputs, &tmp_output, MergeOptions::default()).map_err(op_err_to_py)?;

    std::fs::read(&tmp_output).map_err(|e| errors::PdfIoError::new_err(e.to_string()))
}

#[pyfunction]
fn rotate_pdf_to_bytes(input: &str, degrees: i32) -> PyResult<Vec<u8>> {
    let angle = RotationAngle::from_degrees(degrees).map_err(op_err_to_py)?;

    let tmpdir =
        tempfile::tempdir().map_err(|e| errors::PdfIoError::new_err(e.to_string()))?;
    let tmp_output = tmpdir.path().join("rotated.pdf");

    operations::rotate_all_pages(input, &tmp_output, angle).map_err(op_err_to_py)?;

    std::fs::read(&tmp_output).map_err(|e| errors::PdfIoError::new_err(e.to_string()))
}

#[pyfunction]
fn extract_pages_to_bytes(input: &str, page_indices: Vec<usize>) -> PyResult<Vec<u8>> {
    if page_indices.is_empty() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "At least one page index is required",
        ));
    }

    let tmpdir =
        tempfile::tempdir().map_err(|e| errors::PdfIoError::new_err(e.to_string()))?;
    let tmp_output = tmpdir.path().join("extracted.pdf");

    operations::extract_pages_to_file(input, &page_indices, &tmp_output).map_err(op_err_to_py)?;

    std::fs::read(&tmp_output).map_err(|e| errors::PdfIoError::new_err(e.to_string()))
}

#[pyfunction]
fn split_pdf_to_bytes(input: &str) -> PyResult<Vec<Vec<u8>>> {
    let tmpdir =
        tempfile::tempdir().map_err(|e| errors::PdfIoError::new_err(e.to_string()))?;
    let pattern = format!("{}/page_{{}}.pdf", tmpdir.path().display());

    let paths = operations::split_into_pages(input, &pattern).map_err(op_err_to_py)?;

    let mut results = Vec::new();
    for path in paths {
        let data =
            std::fs::read(&path).map_err(|e| errors::PdfIoError::new_err(e.to_string()))?;
        results.push(data);
    }
    Ok(results)
}

// ── Registration ──────────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(split_pdf, m)?)?;
    m.add_function(wrap_pyfunction!(merge_pdfs, m)?)?;
    m.add_function(wrap_pyfunction!(rotate_pdf, m)?)?;
    m.add_function(wrap_pyfunction!(extract_pages, m)?)?;
    // Feature 6
    m.add_function(wrap_pyfunction!(reorder_pdf_pages, m)?)?;
    m.add_function(wrap_pyfunction!(swap_pdf_pages, m)?)?;
    m.add_function(wrap_pyfunction!(move_pdf_page, m)?)?;
    m.add_function(wrap_pyfunction!(reverse_pdf_pages, m)?)?;
    // Feature 7
    m.add_class::<PyOverlayPosition>()?;
    m.add_class::<PyOverlayOptions>()?;
    m.add_function(wrap_pyfunction!(overlay_pdf, m)?)?;
    // Feature 8
    m.add_class::<PyExtractImagesOptions>()?;
    m.add_function(wrap_pyfunction!(extract_images_from_pdf, m)?)?;
    // Feature 10
    m.add_function(wrap_pyfunction!(merge_pdfs_to_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(rotate_pdf_to_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(extract_pages_to_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(split_pdf_to_bytes, m)?)?;
    Ok(())
}
