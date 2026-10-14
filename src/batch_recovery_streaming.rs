//! Batch, Recovery, and Streaming bindings — Features F62, F63, F64
//!
//! Wraps `oxidize_pdf::batch`, `oxidize_pdf::recovery`, and
//! `oxidize_pdf::streaming` for Python.
//!
//! # Naming Convention Note
//!
//! Functions in this module use clean names without a `_py` suffix (e.g.
//! `batch_split_pdfs`, `quick_recover`), while `security.rs` and
//! `verification.rs` use `_py` suffixed names (e.g. `compute_pdf_hash_py`).
//! Both conventions expose the same clean names via `__init__.py` aliases.
//! Renaming these functions would break the existing public API.

use std::fs::File;
use std::io::{Seek, SeekFrom};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

use pyo3::prelude::*;
use pyo3::types::PyDict;

use oxidize_pdf::batch::{
    BatchJob, BatchOptions, BatchProcessor, BatchSummary, JobResult, ProgressInfo,
};
use oxidize_pdf::recovery::{
    analyze_corruption, detect_corruption, repair_document, CorruptionReport, CorruptionType,
    ObjectScanner, RepairResult, RepairStrategy, ScanResult,
};
use oxidize_pdf::streaming::IncrementalParser;
use oxidize_pdf::{PdfDocument, PdfReader};
use crate::parser::parse_err_to_py;

use crate::errors::to_py_err;

// ── F62: Batch Processing ─────────────────────────────────────────────────

// ── BatchJob ──────────────────────────────────────────────────────────────

/// A job for batch processing.
///
/// Use the static factory methods to create jobs::
///
///     job = BatchJob.split("input.pdf", "output_%d.pdf", 5)
///     job = BatchJob.merge(["a.pdf", "b.pdf"], "merged.pdf")
///     job = BatchJob.rotate("in.pdf", "out.pdf", 90, [0, 1, 2])
///     job = BatchJob.extract("in.pdf", "out.pdf", [0, 2, 4])
///     job = BatchJob.compress("in.pdf", "out.pdf", 80)
#[pyclass(name = "BatchJob", unsendable)]
pub struct PyBatchJob {
    inner: Option<BatchJob>,
    display: String,
}

#[pymethods]
impl PyBatchJob {
    #[staticmethod]
    fn split(input: &str, output_pattern: &str, pages_per_file: usize) -> Self {
        let display = format!("Split({input}, {output_pattern}, {pages_per_file})");
        Self {
            inner: Some(BatchJob::Split {
                input: PathBuf::from(input),
                output_pattern: output_pattern.to_string(),
                pages_per_file,
            }),
            display,
        }
    }

    #[staticmethod]
    fn merge(inputs: Vec<String>, output: &str) -> Self {
        let display = format!("Merge({} files -> {output})", inputs.len());
        Self {
            inner: Some(BatchJob::Merge {
                inputs: inputs.iter().map(PathBuf::from).collect(),
                output: PathBuf::from(output),
            }),
            display,
        }
    }

    #[staticmethod]
    fn rotate(input: &str, output: &str, rotation: i32, pages: Option<Vec<usize>>) -> Self {
        let display = format!("Rotate({input}, {rotation}°)");
        Self {
            inner: Some(BatchJob::Rotate {
                input: PathBuf::from(input),
                output: PathBuf::from(output),
                rotation,
                pages,
            }),
            display,
        }
    }

    #[staticmethod]
    fn extract(input: &str, output: &str, pages: Vec<usize>) -> Self {
        let display = format!("Extract({} pages from {input})", pages.len());
        Self {
            inner: Some(BatchJob::Extract {
                input: PathBuf::from(input),
                output: PathBuf::from(output),
                pages,
            }),
            display,
        }
    }

    #[staticmethod]
    fn compress(input: &str, output: &str, quality: u8) -> Self {
        let display = format!("Compress({input}, quality={quality})");
        Self {
            inner: Some(BatchJob::Compress {
                input: PathBuf::from(input),
                output: PathBuf::from(output),
                quality,
            }),
            display,
        }
    }

    fn __repr__(&self) -> String {
        format!("BatchJob({})", self.display)
    }
}

// ── JobResult ─────────────────────────────────────────────────────────────

/// Result of a single batch job — read-only.
///
/// Properties: ``status`` (str), ``job_name`` (str), ``duration_secs``
/// (float or None), ``error`` (str or None), ``output_files`` (list[str]).
#[pyclass(name = "JobResult", frozen)]
pub struct PyJobResult {
    inner: JobResult,
}

#[pymethods]
impl PyJobResult {
    #[getter]
    fn status(&self) -> &str {
        match &self.inner {
            JobResult::Success { .. } => "success",
            JobResult::Failed { .. } => "failed",
            JobResult::Cancelled { .. } => "cancelled",
        }
    }

    #[getter]
    fn job_name(&self) -> &str {
        self.inner.job_name()
    }

    #[getter]
    fn duration_secs(&self) -> Option<f64> {
        self.inner.duration().map(|d| d.as_secs_f64())
    }

    #[getter]
    fn error(&self) -> Option<&str> {
        self.inner.error()
    }

    #[getter]
    fn output_files(&self) -> Vec<String> {
        self.inner
            .output_files()
            .unwrap_or(&[])
            .iter()
            .map(|p| p.to_string_lossy().into_owned())
            .collect()
    }

    fn __repr__(&self) -> String {
        format!(
            "JobResult(status={:?}, job_name={:?})",
            self.status(),
            self.job_name()
        )
    }
}

// ── BatchSummary ──────────────────────────────────────────────────────────

/// Summary of a completed batch operation — read-only.
///
/// Properties: ``total_jobs``, ``successful``, ``failed``, ``cancelled``
/// (bool), ``duration_secs`` (float), ``results`` (list[JobResult]).
#[pyclass(name = "BatchSummary", frozen)]
pub struct PyBatchSummary {
    inner: BatchSummary,
}

#[pymethods]
impl PyBatchSummary {
    #[getter]
    fn total_jobs(&self) -> usize {
        self.inner.total_jobs
    }

    #[getter]
    fn successful(&self) -> usize {
        self.inner.successful
    }

    #[getter]
    fn failed(&self) -> usize {
        self.inner.failed
    }

    #[getter]
    fn cancelled(&self) -> bool {
        self.inner.cancelled
    }

    #[getter]
    fn duration_secs(&self) -> f64 {
        self.inner.duration.as_secs_f64()
    }

    #[getter]
    fn results(&self) -> Vec<PyJobResult> {
        self.inner
            .results
            .iter()
            .map(|r| PyJobResult { inner: r.clone() })
            .collect()
    }

    fn success_rate(&self) -> f64 {
        self.inner.success_rate()
    }

    fn __repr__(&self) -> String {
        format!(
            "BatchSummary(total={}, successful={}, failed={})",
            self.inner.total_jobs, self.inner.successful, self.inner.failed
        )
    }
}

// ── ProgressInfo ──────────────────────────────────────────────────────────

/// Progress information for a running batch operation — read-only.
#[pyclass(name = "ProgressInfo", frozen)]
pub struct PyProgressInfo {
    inner: ProgressInfo,
}

#[pymethods]
impl PyProgressInfo {
    #[getter]
    fn total_jobs(&self) -> usize {
        self.inner.total_jobs
    }

    #[getter]
    fn completed_jobs(&self) -> usize {
        self.inner.completed_jobs
    }

    #[getter]
    fn failed_jobs(&self) -> usize {
        self.inner.failed_jobs
    }

    #[getter]
    fn running_jobs(&self) -> usize {
        self.inner.running_jobs
    }

    fn percentage(&self) -> f64 {
        self.inner.percentage()
    }

    fn is_complete(&self) -> bool {
        self.inner.is_complete()
    }

    fn elapsed_secs(&self) -> f64 {
        self.inner.elapsed().as_secs_f64()
    }

    fn __repr__(&self) -> String {
        format!(
            "ProgressInfo({}/{}, {:.1}%)",
            self.inner.completed_jobs,
            self.inner.total_jobs,
            self.inner.percentage()
        )
    }
}

// ── BatchProcessor ────────────────────────────────────────────────────────

// One adapter per processor: reusing options must not share callback failures.
struct PythonProgressCallback {
    callback: Py<PyAny>,
    error: Mutex<Option<PyErr>>,
}

impl oxidize_pdf::batch::ProgressCallback for PythonProgressCallback {
    fn on_progress(&self, info: &ProgressInfo) {
        if self.error.lock().unwrap_or_else(|e| e.into_inner()).is_some() {
            return;
        }
        Python::attach(|py| {
            // Never hold the error mutex while invoking user Python code.
            if let Err(error) = self.callback.call1(py, (PyProgressInfo { inner: info.clone() },)) {
                *self.error.lock().unwrap_or_else(|e| e.into_inner()) = Some(error);
            }
        });
    }
}

/// Batch processor for executing multiple PDF jobs in parallel.
///
/// Example::
///
///     opts = BatchOptions(parallelism=4)
///     processor = BatchProcessor(opts)
///     processor.add_job(BatchJob.split("in.pdf", "out_%d.pdf", 5))
///     summary = processor.execute()
///     print(f"Successful: {summary.successful}")
#[pyclass(name = "BatchProcessor", unsendable)]
pub struct PyBatchProcessor {
    inner: Option<BatchProcessor>,
    callback: Option<Arc<PythonProgressCallback>>,
}

#[pymethods]
impl PyBatchProcessor {
    fn __traverse__(&self, visit: pyo3::gc::PyVisit<'_>) -> Result<(), pyo3::gc::PyTraverseError> {
        if let Some(callback) = &self.callback { visit.call(&callback.callback)?; }
        Ok(())
    }
    fn __clear__(&mut self) {
        self.inner = None;
        self.callback = None;
    }
    #[new]
    fn new(options: &crate::tier8::PyBatchOptions, py: Python<'_>) -> Self {
        let mut native = options.inner.clone();
        let callback = options.callback.as_ref().map(|callback| Arc::new(PythonProgressCallback {
            callback: callback.clone_ref(py),
            error: Mutex::new(None),
        }));
        native.progress_callback = callback.as_ref().map(|cb| {
            Arc::clone(cb) as Arc<dyn oxidize_pdf::batch::ProgressCallback>
        });
        Self { inner: Some(BatchProcessor::new(native)), callback }
    }

    fn add_job(&mut self, job: &mut PyBatchJob) -> PyResult<()> {
        let batch_job = job.inner.take().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("BatchJob already consumed")
        })?;
        let processor = self.inner.as_mut().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("BatchProcessor already consumed by execute()")
        })?;
        processor.add_job(batch_job);
        Ok(())
    }

    fn get_progress(&self) -> PyResult<PyProgressInfo> {
        let processor = self.inner.as_ref().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("BatchProcessor already consumed")
        })?;
        Ok(PyProgressInfo {
            inner: processor.get_progress(),
        })
    }

    fn cancel(&self) -> PyResult<()> {
        let processor = self.inner.as_ref().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("BatchProcessor already consumed")
        })?;
        processor.cancel();
        Ok(())
    }

    fn is_cancelled(&self) -> PyResult<bool> {
        let processor = self.inner.as_ref().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("BatchProcessor already consumed")
        })?;
        Ok(processor.is_cancelled())
    }

    /// Execute all queued jobs. Consumes the processor — cannot call again.
    fn execute(&mut self, py: Python<'_>) -> PyResult<PyBatchSummary> {
        let processor = self.inner.take().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err(
                "BatchProcessor already consumed by a previous execute() call",
            )
        })?;
        let result = py.detach(move || processor.execute());
        if let Some(callback) = self.callback.take() {
            if let Some(error) = callback.error.lock().unwrap_or_else(|e| e.into_inner()).take() {
                return Err(error);
            }
        }
        Ok(PyBatchSummary { inner: result.map_err(to_py_err)? })
    }

    fn __repr__(&self) -> String {
        if self.inner.is_some() {
            "BatchProcessor(active)".to_string()
        } else {
            "BatchProcessor(consumed)".to_string()
        }
    }
}

// ── Standalone batch functions ────────────────────────────────────────────

/// Split multiple PDF files in batch, one ``pages_per_file`` pages per output file.
#[pyfunction]
fn batch_split_pdfs(
    files: Vec<String>,
    pages_per_file: usize,
    parallelism: usize,
) -> PyResult<PyBatchSummary> {
    let options = BatchOptions::default().with_parallelism(parallelism);
    let mut processor = BatchProcessor::new(options);
    for file in files {
        let input_path = PathBuf::from(&file);
        // Upstream substitutes `{n}` (1-based chunk index) — `%d` is NOT a
        // placeholder and was emitted literally, collapsing every chunk onto
        // one filename. Write beside the input (not the process CWD) so the
        // output is discoverable; `JobResult.output_files` is empty upstream.
        // Reject non-UTF-8 paths loudly rather than degrading silently
        // (`to_string_lossy` would inject U+FFFD and yield an unusable pattern,
        // surfacing only as an opaque job failure).
        let stem = input_path
            .file_stem()
            .and_then(|s| s.to_str())
            .ok_or_else(|| {
                pyo3::exceptions::PyValueError::new_err(format!(
                    "input path has no valid UTF-8 file stem: {file:?}"
                ))
            })?;
        let file_name = format!("{stem}_page_{{n}}.pdf");
        let output_pattern = match input_path.parent() {
            Some(dir) if !dir.as_os_str().is_empty() => dir
                .join(&file_name)
                .to_str()
                .ok_or_else(|| {
                    pyo3::exceptions::PyValueError::new_err(format!(
                        "input path contains non-UTF-8 characters: {file:?}"
                    ))
                })?
                .to_owned(),
            _ => file_name,
        };
        processor.add_job(BatchJob::Split {
            input: input_path,
            output_pattern,
            pages_per_file,
        });
    }
    let summary = processor.execute().map_err(to_py_err)?;
    Ok(PyBatchSummary { inner: summary })
}

/// Merge groups of PDFs in batch.
///
/// ``merge_groups`` is a list of ``(input_files, output_path)`` tuples.
#[pyfunction]
fn batch_merge_pdfs(
    merge_groups: Vec<(Vec<String>, String)>,
    parallelism: usize,
) -> PyResult<PyBatchSummary> {
    let options = BatchOptions::default().with_parallelism(parallelism);
    let mut processor = BatchProcessor::new(options);
    for (inputs, output) in merge_groups {
        processor.add_job(BatchJob::Merge {
            inputs: inputs.iter().map(PathBuf::from).collect(),
            output: PathBuf::from(output),
        });
    }
    let summary = processor.execute().map_err(to_py_err)?;
    Ok(PyBatchSummary { inner: summary })
}

// ── F63: Recovery Full ────────────────────────────────────────────────────

// ── RepairStrategy ────────────────────────────────────────────────────────

/// Strategy for repairing a corrupted PDF.
#[pyclass(name = "RepairStrategy", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyRepairStrategy {
    pub inner: RepairStrategy,
}

#[pymethods]
impl PyRepairStrategy {
    #[classattr]
    const REBUILD_XREF: Self = Self { inner: RepairStrategy::RebuildXRef };
    #[classattr]
    const FIX_STRUCTURE: Self = Self { inner: RepairStrategy::FixStructure };
    #[classattr]
    const EXTRACT_CONTENT: Self = Self { inner: RepairStrategy::ExtractContent };
    #[classattr]
    const RECONSTRUCT_FRAGMENTS: Self = Self { inner: RepairStrategy::ReconstructFragments };
    #[classattr]
    const MINIMAL_REPAIR: Self = Self { inner: RepairStrategy::MinimalRepair };
    #[classattr]
    const AGGRESSIVE_REPAIR: Self = Self { inner: RepairStrategy::AggressiveRepair };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            RepairStrategy::RebuildXRef => "REBUILD_XREF",
            RepairStrategy::FixStructure => "FIX_STRUCTURE",
            RepairStrategy::ExtractContent => "EXTRACT_CONTENT",
            RepairStrategy::ReconstructFragments => "RECONSTRUCT_FRAGMENTS",
            RepairStrategy::MinimalRepair => "MINIMAL_REPAIR",
            RepairStrategy::AggressiveRepair => "AGGRESSIVE_REPAIR",
        };
        format!("RepairStrategy.{}", name)
    }
}

// ── CorruptionType ────────────────────────────────────────────────────────

/// Type of corruption detected in a PDF file.
#[pyclass(name = "CorruptionType", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyCorruptionType {
    pub inner: CorruptionType,
}

impl PyCorruptionType {
    fn type_name(t: &CorruptionType) -> &'static str {
        match t {
            CorruptionType::InvalidHeader => "INVALID_HEADER",
            CorruptionType::CorruptXRef => "CORRUPT_XREF",
            CorruptionType::MissingEOF => "MISSING_EOF",
            CorruptionType::BrokenReferences => "BROKEN_REFERENCES",
            CorruptionType::CorruptStreams => "CORRUPT_STREAMS",
            CorruptionType::InvalidPageTree => "INVALID_PAGE_TREE",
            CorruptionType::TruncatedFile => "TRUNCATED_FILE",
            CorruptionType::Multiple(_) => "MULTIPLE",
            CorruptionType::Unknown => "UNKNOWN",
        }
    }
}

#[pymethods]
impl PyCorruptionType {
    #[classattr]
    const INVALID_HEADER: Self = Self { inner: CorruptionType::InvalidHeader };
    #[classattr]
    const CORRUPT_XREF: Self = Self { inner: CorruptionType::CorruptXRef };
    #[classattr]
    const MISSING_EOF: Self = Self { inner: CorruptionType::MissingEOF };
    #[classattr]
    const BROKEN_REFERENCES: Self = Self { inner: CorruptionType::BrokenReferences };
    #[classattr]
    const CORRUPT_STREAMS: Self = Self { inner: CorruptionType::CorruptStreams };
    #[classattr]
    const INVALID_PAGE_TREE: Self = Self { inner: CorruptionType::InvalidPageTree };
    #[classattr]
    const TRUNCATED_FILE: Self = Self { inner: CorruptionType::TruncatedFile };
    #[classattr]
    const UNKNOWN: Self = Self { inner: CorruptionType::Unknown };

    fn __repr__(&self) -> String {
        format!("CorruptionType.{}", Self::type_name(&self.inner))
    }
}

// ── CorruptionReport ──────────────────────────────────────────────────────

/// Report describing the corruption state of a PDF file — read-only.
///
/// Properties: ``corruption_type`` (CorruptionType), ``severity`` (int),
/// ``errors`` (list[str]), ``file_size`` (int), ``estimated_objects`` (int),
/// ``found_pages`` (int).
#[pyclass(name = "CorruptionReport", frozen)]
pub struct PyCorruptionReport {
    inner: CorruptionReport,
}

#[pymethods]
impl PyCorruptionReport {
    #[getter]
    fn corruption_type(&self) -> PyCorruptionType {
        PyCorruptionType {
            inner: self.inner.corruption_type.clone(),
        }
    }

    #[getter]
    fn severity(&self) -> u8 {
        self.inner.severity
    }

    #[getter]
    fn errors(&self) -> Vec<String> {
        self.inner.errors.clone()
    }

    #[getter]
    fn file_size(&self) -> u64 {
        self.inner.file_stats.file_size
    }

    #[getter]
    fn estimated_objects(&self) -> usize {
        self.inner.file_stats.estimated_objects
    }

    #[getter]
    fn found_pages(&self) -> usize {
        self.inner.file_stats.found_pages
    }

    fn __repr__(&self) -> String {
        format!(
            "CorruptionReport(type={}, severity={})",
            PyCorruptionType::type_name(&self.inner.corruption_type),
            self.inner.severity
        )
    }
}

// ── RepairResult ──────────────────────────────────────────────────────────

/// Result of a PDF repair operation — read-only.
///
/// Properties: ``success`` (bool), ``pages_recovered`` (int),
/// ``objects_recovered`` (int), ``warnings`` (list[str]),
/// ``is_partial`` (bool), ``repaired_bytes`` (bytes or None).
#[pyclass(name = "RepairResult", frozen)]
pub struct PyRepairResult {
    success: bool,
    pages_recovered: usize,
    objects_recovered: usize,
    warnings: Vec<String>,
    is_partial: bool,
    /// Pre-serialized bytes of the recovered document (if any).
    repaired_bytes_cache: Option<Vec<u8>>,
}

impl PyRepairResult {
    fn from_repair_result(mut result: RepairResult) -> PyResult<Self> {
        let success = result.recovered_document.is_some();
        let repaired_bytes_cache = if let Some(mut doc) = result.recovered_document.take() {
            Some(doc.to_bytes().map_err(to_py_err)?)
        } else {
            None
        };
        Ok(Self {
            success,
            pages_recovered: result.pages_recovered,
            objects_recovered: result.objects_recovered,
            warnings: result.warnings,
            is_partial: result.is_partial,
            repaired_bytes_cache,
        })
    }
}

#[pymethods]
impl PyRepairResult {
    #[getter]
    fn success(&self) -> bool {
        self.success
    }

    #[getter]
    fn pages_recovered(&self) -> usize {
        self.pages_recovered
    }

    #[getter]
    fn objects_recovered(&self) -> usize {
        self.objects_recovered
    }

    #[getter]
    fn warnings(&self) -> Vec<String> {
        self.warnings.clone()
    }

    #[getter]
    fn is_partial(&self) -> bool {
        self.is_partial
    }

    /// The repaired document as bytes, or ``None`` if repair failed.
    #[getter]
    fn repaired_bytes(&self) -> Option<Vec<u8>> {
        self.repaired_bytes_cache.clone()
    }

    fn __repr__(&self) -> String {
        format!(
            "RepairResult(success={}, pages={})",
            self.success, self.pages_recovered
        )
    }
}

// ── ScanResult ────────────────────────────────────────────────────────────

/// Result of scanning a PDF for valid objects — read-only.
#[pyclass(name = "ScanResult", frozen)]
pub struct PyScanResult {
    inner: ScanResult,
}

#[pymethods]
impl PyScanResult {
    #[getter]
    fn total_objects(&self) -> usize {
        self.inner.total_objects
    }

    #[getter]
    fn valid_objects(&self) -> usize {
        self.inner.valid_objects
    }

    #[getter]
    fn estimated_pages(&self) -> u32 {
        self.inner.estimated_pages
    }

    fn __repr__(&self) -> String {
        format!(
            "ScanResult(total={}, valid={}, pages={})",
            self.inner.total_objects, self.inner.valid_objects, self.inner.estimated_pages
        )
    }
}

// ── ObjectScanner ─────────────────────────────────────────────────────────

/// Scanner for locating valid PDF objects in a possibly-corrupted file.
#[pyclass(name = "ObjectScanner")]
pub struct PyObjectScanner {
    inner: ObjectScanner,
}

#[pymethods]
impl PyObjectScanner {
    #[new]
    fn new() -> Self {
        Self { inner: ObjectScanner::new() }
    }

    fn scan_file(&mut self, path: &str) -> PyResult<PyScanResult> {
        let result = self.inner.scan_file(path).map_err(to_py_err)?;
        Ok(PyScanResult { inner: result })
    }

    fn __repr__(&self) -> String {
        "ObjectScanner()".to_string()
    }
}

// ── Standalone recovery functions ─────────────────────────────────────────

/// Quickly recover a corrupted PDF, returning the repaired document bytes.
#[pyfunction]
fn quick_recover(path: &str) -> PyResult<Vec<u8>> {
    let mut doc = oxidize_pdf::recovery::quick_recover(path).map_err(to_py_err)?;
    doc.to_bytes().map_err(to_py_err)
}

/// Detect corruption in a PDF file.
#[pyfunction]
fn detect_pdf_corruption(py: Python<'_>, path: String) -> PyResult<PyCorruptionReport> {
    // #115 Capa C: scan for corruption without holding the GIL.
    let report = py
        .detach(move || detect_corruption(&path))
        .map_err(to_py_err)?;
    Ok(PyCorruptionReport { inner: report })
}

/// Analyze a PDF file for corruption (alias for detect_pdf_corruption).
#[pyfunction]
fn analyze_pdf_corruption(path: &str) -> PyResult<PyCorruptionReport> {
    let report = analyze_corruption(path).map_err(to_py_err)?;
    Ok(PyCorruptionReport { inner: report })
}

/// Repair a corrupted PDF using the given strategy.
#[pyfunction]
fn repair_pdf(path: &str, strategy: &PyRepairStrategy) -> PyResult<PyRepairResult> {
    let options = oxidize_pdf::recovery::RecoveryOptions::default();
    let result = repair_document(path, strategy.inner.clone(), &options).map_err(to_py_err)?;
    PyRepairResult::from_repair_result(result)
}

// ── F64: Streaming Full ───────────────────────────────────────────────────

// ── StreamingPage ─────────────────────────────────────────────────────────

/// An owned snapshot of one parsed page, independent of the source file.
#[pyclass(name = "StreamingPage", frozen)]
pub struct PyStreamingPage {
    number: u32,
    width: f64,
    height: f64,
    media_box: [f64; 4],
    text: String,
}

#[pymethods]
impl PyStreamingPage {
    #[getter]
    fn number(&self) -> u32 {
        self.number
    }
    #[getter]
    fn width(&self) -> f64 {
        self.width
    }
    #[getter]
    fn height(&self) -> f64 {
        self.height
    }
    fn extract_text_streaming(&self) -> &str {
        &self.text
    }
    fn media_box(&self) -> [f64; 4] {
        self.media_box
    }
    fn __repr__(&self) -> String {
        format!(
            "StreamingPage(number={}, {}x{})",
            self.number, self.width, self.height
        )
    }
}

/// Iterate real PDF pages using a fresh core parser for each page.
///
/// Keeps one source file open. Each next() reparses the PDF index and extracts
/// only the selected page, then drops all parser caches. Memory depends on the
/// index, page resources and decoded page content; it is not constant or capped.
/// Returned pages own their text and geometry. Do not modify the source file
/// while it is open. Use close() or a with statement to release the descriptor.
#[pyclass(name = "PageStreamer", unsendable)]
pub struct PyPageStreamer {
    file: Option<File>,
    current_page: u32,
    total_pages: u32,
}

impl PyPageStreamer {
    fn file(&self) -> PyResult<&File> {
        self.file
            .as_ref()
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("PageStreamer is closed"))
    }

    // Duplicated descriptors share a cursor; all access is serialized by the
    // mutable PyO3 borrow. No parser/BufReader survives this operation.
    fn document(file: &File) -> PyResult<PdfDocument<File>> {
        let mut input = file
            .try_clone()
            .map_err(|e| crate::errors::PdfIoError::new_err(e.to_string()))?;
        input
            .seek(SeekFrom::Start(0))
            .map_err(|e| crate::errors::PdfIoError::new_err(e.to_string()))?;
        let reader = PdfReader::new(input).map_err(parse_err_to_py)?;
        if reader.is_encrypted() {
            return Err(crate::errors::PdfEncryptionError::new_err(
                "PageStreamer does not support encrypted PDFs; use PdfReader.unlock",
            ));
        }
        Ok(PdfDocument::new(reader))
    }
}

#[pymethods]
impl PyPageStreamer {
    #[staticmethod]
    fn open(py: Python<'_>, path: String) -> PyResult<Self> {
        py.detach(move || {
            let file =
                File::open(path).map_err(|e| crate::errors::PdfIoError::new_err(e.to_string()))?;
            let total_pages = Self::document(&file)?
                .page_count()
                .map_err(parse_err_to_py)?;
            Ok(Self {
                file: Some(file),
                current_page: 0,
                total_pages,
            })
        })
    }

    fn next(&mut self, py: Python<'_>) -> PyResult<Option<PyStreamingPage>> {
        let file = self.file()?;
        if self.current_page >= self.total_pages {
            return Ok(None);
        }
        let number = self.current_page;
        let page = py.detach(|| {
            let document = Self::document(file)?;
            let page = document.get_page(number).map_err(parse_err_to_py)?;
            let text = document
                .extract_text_from_page(number)
                .map_err(parse_err_to_py)?
                .text;
            Ok::<_, PyErr>(PyStreamingPage {
                number,
                width: page.width(),
                height: page.height(),
                media_box: page.media_box,
                text,
            })
        })?;
        // Failed reads leave the cursor unchanged, permitting explicit retry/seek.
        self.current_page += 1;
        Ok(Some(page))
    }

    /// Position the next read. total_pages is the valid EOF position.
    fn seek_to_page(&mut self, page_num: u32) -> PyResult<()> {
        self.file()?;
        if page_num > self.total_pages {
            return Err(pyo3::exceptions::PyIndexError::new_err(
                "page index out of range",
            ));
        }
        self.current_page = page_num;
        Ok(())
    }
    fn total_pages(&self) -> u32 {
        self.total_pages
    }
    fn close(&mut self) {
        self.file = None;
    }
    fn __enter__(slf: PyRef<'_, Self>) -> PyResult<PyRef<'_, Self>> {
        slf.file()?;
        Ok(slf)
    }
    fn __exit__(
        &mut self,
        _exc_type: &Bound<'_, PyAny>,
        _exc_value: &Bound<'_, PyAny>,
        _traceback: &Bound<'_, PyAny>,
    ) {
        self.close();
    }
    fn __repr__(&self) -> String {
        format!(
            "PageStreamer(pages={}, closed={})",
            self.total_pages,
            self.file.is_none()
        )
    }
}

// ── IncrementalParser ─────────────────────────────────────────────────────

/// Parses PDF content incrementally, emitting events as they are detected.
///
/// Example::
///
///     parser = IncrementalParser()
///     with open("document.pdf", "rb") as f:
///         while chunk := f.read(4096):
///             parser.feed(chunk)
///             for event in parser.take_events():
///                 print(event)
///     print(f"Complete: {parser.is_complete()}")
#[pyclass(name = "IncrementalParser")]
pub struct PyIncrementalParser {
    inner: IncrementalParser,
}

#[pymethods]
impl PyIncrementalParser {
    #[new]
    fn new() -> Self {
        Self { inner: IncrementalParser::new() }
    }

    /// Feed the core's line-oriented parser. Core 5.4.2 normalizes UTF-8 and
    /// whitespace; this is not a binary-safe PDF stream parser.
    fn feed(&mut self, data: &[u8]) -> PyResult<()> {
        self.inner.feed(data).map_err(to_py_err)
    }

    /// Return and clear all pending parse events as dicts.
    ///
    /// Each dict has a ``type`` key and retains the complete core event payload.
    /// Core 5.4.2 supplies placeholder Null objects and does not yet emit xref
    /// or trailer events. Stream bytes reflect core normalization, not raw input.
    fn take_events<'py>(&mut self, py: Python<'py>) -> PyResult<Vec<Bound<'py, PyDict>>> {
        self.inner.take_events().into_iter()
            .map(|event| crate::parse_events::event_to_dict(py, event))
            .collect()
    }

    fn is_complete(&self) -> bool {
        self.inner.is_complete()
    }

    fn __repr__(&self) -> String {
        format!("IncrementalParser(complete={})", self.inner.is_complete())
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // F62: Batch
    m.add_class::<PyBatchJob>()?;
    m.add_class::<PyJobResult>()?;
    m.add_class::<PyBatchSummary>()?;
    m.add_class::<PyProgressInfo>()?;
    m.add_class::<PyBatchProcessor>()?;
    m.add_function(wrap_pyfunction!(batch_split_pdfs, m)?)?;
    m.add_function(wrap_pyfunction!(batch_merge_pdfs, m)?)?;

    // F63: Recovery
    m.add_class::<PyRepairStrategy>()?;
    m.add_class::<PyCorruptionType>()?;
    m.add_class::<PyCorruptionReport>()?;
    m.add_class::<PyRepairResult>()?;
    m.add_class::<PyScanResult>()?;
    m.add_class::<PyObjectScanner>()?;
    m.add_function(wrap_pyfunction!(quick_recover, m)?)?;
    m.add_function(wrap_pyfunction!(detect_pdf_corruption, m)?)?;
    m.add_function(wrap_pyfunction!(analyze_pdf_corruption, m)?)?;
    m.add_function(wrap_pyfunction!(repair_pdf, m)?)?;

    // F64: Streaming
    m.add_class::<PyStreamingPage>()?;
    m.add_class::<PyPageStreamer>()?;
    m.add_class::<PyIncrementalParser>()?;

    Ok(())
}
