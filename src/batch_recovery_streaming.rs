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
use std::path::PathBuf;

use pyo3::prelude::*;
use pyo3::types::PyDict;

use oxidize_pdf::batch::{
    BatchJob, BatchOptions, BatchProcessor, BatchSummary, JobResult, ProgressInfo,
};
use oxidize_pdf::recovery::{
    analyze_corruption, detect_corruption, repair_document, CorruptionReport, CorruptionType,
    ObjectScanner, RepairResult, RepairStrategy, ScanResult,
};
use oxidize_pdf::streaming::{IncrementalParser, PageStreamer, StreamingPage};

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
}

#[pymethods]
impl PyBatchProcessor {
    #[new]
    fn new(options: &crate::tier8::PyBatchOptions) -> Self {
        Self {
            inner: Some(BatchProcessor::new(options.inner.clone())),
        }
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
    fn execute(&mut self) -> PyResult<PyBatchSummary> {
        let processor = self.inner.take().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err(
                "BatchProcessor already consumed by a previous execute() call",
            )
        })?;
        let summary = processor.execute().map_err(to_py_err)?;
        Ok(PyBatchSummary { inner: summary })
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
        processor.add_job(BatchJob::Split {
            input: PathBuf::from(&file),
            output_pattern: format!(
                "{}_page_%d.pdf",
                PathBuf::from(&file)
                    .file_stem()
                    .and_then(|s| s.to_str())
                    .unwrap_or("output")
            ),
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
fn detect_pdf_corruption(path: &str) -> PyResult<PyCorruptionReport> {
    let report = detect_corruption(path).map_err(to_py_err)?;
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

/// A page obtained from streaming — read-only.
///
/// Provides access to page number, dimensions, and streaming text extraction.
#[pyclass(name = "StreamingPage", frozen)]
pub struct PyStreamingPage {
    inner: StreamingPage,
}

#[pymethods]
impl PyStreamingPage {
    #[getter]
    fn number(&self) -> u32 {
        self.inner.number()
    }

    #[getter]
    fn width(&self) -> f64 {
        self.inner.width()
    }

    #[getter]
    fn height(&self) -> f64 {
        self.inner.height()
    }

    fn extract_text_streaming(&self) -> PyResult<String> {
        self.inner.extract_text_streaming().map_err(to_py_err)
    }

    fn media_box(&self) -> [f64; 4] {
        self.inner.media_box()
    }

    fn __repr__(&self) -> String {
        format!(
            "StreamingPage(number={}, {}x{})",
            self.inner.number(),
            self.inner.width(),
            self.inner.height()
        )
    }
}

// ── PageStreamer ───────────────────────────────────────────────────────────

/// Streams pages from a PDF file without loading the whole document.
///
/// Example::
///
///     streamer = PageStreamer.open("large.pdf")
///     while True:
///         page = streamer.next()
///         if page is None:
///             break
///         print(f"Page {page.number}: {page.width}x{page.height}")
#[pyclass(name = "PageStreamer", unsendable)]
pub struct PyPageStreamer {
    inner: PageStreamer<File>,
}

#[pymethods]
impl PyPageStreamer {
    #[staticmethod]
    fn open(path: &str) -> PyResult<Self> {
        let file = File::open(path).map_err(|e| crate::errors::PdfIoError::new_err(e.to_string()))?;
        Ok(Self {
            inner: PageStreamer::new(file),
        })
    }

    fn next(&mut self) -> PyResult<Option<PyStreamingPage>> {
        let page = self.inner.next().map_err(to_py_err)?;
        Ok(page.map(|p| PyStreamingPage { inner: p }))
    }

    fn seek_to_page(&mut self, page_num: u32) -> PyResult<()> {
        self.inner.seek_to_page(page_num).map_err(to_py_err)
    }

    fn total_pages(&self) -> Option<u32> {
        self.inner.total_pages()
    }

    fn __repr__(&self) -> String {
        "PageStreamer(file)".to_string()
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

    /// Feed a chunk of PDF bytes to the parser.
    fn feed(&mut self, data: &[u8]) -> PyResult<()> {
        self.inner.feed(data).map_err(to_py_err)
    }

    /// Return and clear all pending parse events as dicts.
    ///
    /// Each dict has a ``type`` key and event-specific fields.
    fn take_events<'py>(&mut self, py: Python<'py>) -> PyResult<Vec<Bound<'py, PyDict>>> {
        let events = self.inner.take_events();
        let mut result = Vec::with_capacity(events.len());

        for event in events {
            let dict = PyDict::new(py);
            match event {
                oxidize_pdf::streaming::ParseEvent::Header { version } => {
                    dict.set_item("type", "header")?;
                    dict.set_item("version", version)?;
                }
                oxidize_pdf::streaming::ParseEvent::ObjectStart { id, generation } => {
                    dict.set_item("type", "object_start")?;
                    dict.set_item("id", id)?;
                    dict.set_item("generation", generation)?;
                }
                oxidize_pdf::streaming::ParseEvent::ObjectEnd { id, generation, .. } => {
                    dict.set_item("type", "object_end")?;
                    dict.set_item("id", id)?;
                    dict.set_item("generation", generation)?;
                }
                oxidize_pdf::streaming::ParseEvent::StreamData { object_id, data } => {
                    dict.set_item("type", "stream_data")?;
                    dict.set_item("object_id", object_id)?;
                    dict.set_item("data_len", data.len())?;
                }
                oxidize_pdf::streaming::ParseEvent::XRef { entries } => {
                    dict.set_item("type", "xref")?;
                    dict.set_item("entry_count", entries.len())?;
                }
                oxidize_pdf::streaming::ParseEvent::Trailer { .. } => {
                    dict.set_item("type", "trailer")?;
                }
                oxidize_pdf::streaming::ParseEvent::EndOfFile => {
                    dict.set_item("type", "end_of_file")?;
                }
            }
            result.push(dict);
        }

        Ok(result)
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
