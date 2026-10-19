//! Typed configuration of the native streaming and lazy-document adapters.
use crate::batch_recovery_streaming::PyStreamingPage;
use crate::errors::to_py_err;
use crate::parser::PyParsedPage;
use crate::signing::PyPdfValue;
use oxidize_pdf::{memory, streaming};
use pyo3::prelude::*;
use std::fs::File;

#[pyclass(name = "StreamingOptions", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyStreamingOptions {
    inner: streaming::StreamingOptions,
}
#[pymethods]
impl PyStreamingOptions {
    #[new]
    #[pyo3(signature = (*, buffer_size=262144, page_cache_size=3, max_content_stream_size=10485760, progressive_hints=true, memory_limit=104857600))]
    fn new(
        buffer_size: usize,
        page_cache_size: usize,
        max_content_stream_size: usize,
        progressive_hints: bool,
        memory_limit: usize,
    ) -> Self {
        Self {
            inner: streaming::StreamingOptions {
                buffer_size,
                page_cache_size,
                max_content_stream_size,
                progressive_hints,
                memory_limit,
            },
        }
    }
    #[getter]
    fn buffer_size(&self) -> usize {
        self.inner.buffer_size
    }
    #[getter]
    fn page_cache_size(&self) -> usize {
        self.inner.page_cache_size
    }
    #[getter]
    fn max_content_stream_size(&self) -> usize {
        self.inner.max_content_stream_size
    }
    #[getter]
    fn progressive_hints(&self) -> bool {
        self.inner.progressive_hints
    }
    #[getter]
    fn memory_limit(&self) -> usize {
        self.inner.memory_limit
    }
    #[staticmethod]
    fn minimal_memory() -> Self {
        Self {
            inner: streaming::StreamingOptions::minimal_memory(),
        }
    }
    #[staticmethod]
    fn fast_processing() -> Self {
        Self {
            inner: streaming::StreamingOptions::fast_processing(),
        }
    }
    fn with_buffer_size(&self, value: usize) -> Self {
        Self {
            inner: self.inner.clone().with_buffer_size(value),
        }
    }
    fn with_page_cache_size(&self, value: usize) -> Self {
        Self {
            inner: self.inner.clone().with_page_cache_size(value),
        }
    }
    fn with_memory_limit(&self, value: usize) -> Self {
        Self {
            inner: self.inner.clone().with_memory_limit(value),
        }
    }
}

#[pyclass(name = "MemoryOptions", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyMemoryOptions {
    inner: memory::MemoryOptions,
}
#[pymethods]
impl PyMemoryOptions {
    #[new]
    #[pyo3(signature = (*, lazy_loading=true, memory_mapping=true, cache_size=1000, streaming=true, buffer_size=65536, mmap_threshold=10485760))]
    fn new(
        lazy_loading: bool,
        memory_mapping: bool,
        cache_size: usize,
        streaming: bool,
        buffer_size: usize,
        mmap_threshold: usize,
    ) -> Self {
        Self {
            inner: memory::MemoryOptions {
                lazy_loading,
                memory_mapping,
                cache_size,
                streaming,
                buffer_size,
                mmap_threshold,
            },
        }
    }
    #[getter]
    fn lazy_loading(&self) -> bool {
        self.inner.lazy_loading
    }
    #[getter]
    fn memory_mapping(&self) -> bool {
        self.inner.memory_mapping
    }
    #[getter]
    fn cache_size(&self) -> usize {
        self.inner.cache_size
    }
    #[getter]
    fn streaming(&self) -> bool {
        self.inner.streaming
    }
    #[getter]
    fn buffer_size(&self) -> usize {
        self.inner.buffer_size
    }
    #[getter]
    fn mmap_threshold(&self) -> usize {
        self.inner.mmap_threshold
    }
    #[staticmethod]
    fn small_file() -> Self {
        Self {
            inner: memory::MemoryOptions::small_file(),
        }
    }
    #[staticmethod]
    fn large_file() -> Self {
        Self {
            inner: memory::MemoryOptions::large_file(),
        }
    }
    fn with_lazy_loading(&self, value: bool) -> Self {
        Self {
            inner: self.inner.clone().with_lazy_loading(value),
        }
    }
    fn with_memory_mapping(&self, value: bool) -> Self {
        Self {
            inner: self.inner.clone().with_memory_mapping(value),
        }
    }
    fn with_cache_size(&self, value: usize) -> Self {
        Self {
            inner: self.inner.clone().with_cache_size(value),
        }
    }
    fn with_streaming(&self, value: bool) -> Self {
        Self {
            inner: self.inner.clone().with_streaming(value),
        }
    }
}

#[pyclass(name = "UnsupportedMemoryOption", frozen, eq, eq_int, from_py_object)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyUnsupportedMemoryOption {
    MemoryMapping,
    Streaming,
}

#[pyclass(name = "MemoryConfiguration", frozen)]
pub struct PyMemoryConfiguration {
    inner: memory::MemoryConfiguration,
}
#[pymethods]
impl PyMemoryConfiguration {
    #[getter]
    fn requested(&self) -> PyMemoryOptions {
        PyMemoryOptions {
            inner: self.inner.requested.clone(),
        }
    }
    #[getter]
    fn effective(&self) -> PyMemoryOptions {
        PyMemoryOptions {
            inner: self.inner.effective.clone(),
        }
    }
    #[getter]
    fn unsupported(&self) -> Vec<PyUnsupportedMemoryOption> {
        self.inner
            .unsupported
            .iter()
            .map(|v| match v {
                memory::UnsupportedMemoryOption::MemoryMapping => {
                    PyUnsupportedMemoryOption::MemoryMapping
                }
                memory::UnsupportedMemoryOption::Streaming => PyUnsupportedMemoryOption::Streaming,
            })
            .collect()
    }
}

#[pyclass(name = "StreamingConfiguration", frozen)]
pub struct PyStreamingConfiguration {
    inner: streaming::StreamingConfiguration,
}
#[pymethods]
impl PyStreamingConfiguration {
    #[getter]
    fn requested(&self) -> PyStreamingOptions {
        PyStreamingOptions {
            inner: self.inner.requested.clone(),
        }
    }
    #[getter]
    fn effective(&self) -> PyStreamingOptions {
        PyStreamingOptions {
            inner: self.inner.effective.clone(),
        }
    }
    #[getter]
    fn progressive_hints_unsupported(&self) -> bool {
        self.inner.progressive_hints_unsupported
    }
}

/// Adapter counters only; allocated_bytes/lazy_loads/mapped_regions are not
/// measurements of underlying parser allocations or OS mappings.
#[pyclass(name = "MemoryStats", frozen)]
pub struct PyMemoryStats {
    inner: memory::MemoryStats,
}
#[pymethods]
impl PyMemoryStats {
    #[getter]
    fn allocated_bytes(&self) -> usize {
        self.inner.allocated_bytes
    }
    #[getter]
    fn cached_objects(&self) -> usize {
        self.inner.cached_objects
    }
    #[getter]
    fn cache_hits(&self) -> usize {
        self.inner.cache_hits
    }
    #[getter]
    fn cache_misses(&self) -> usize {
        self.inner.cache_misses
    }
    #[getter]
    fn lazy_loads(&self) -> usize {
        self.inner.lazy_loads
    }
    #[getter]
    fn mapped_regions(&self) -> usize {
        self.inner.mapped_regions
    }
}

/// Native page-at-a-time adapter with retained-payload cache budgets.
/// Reader caches, extraction working memory and caller-owned pages are excluded.
#[pyclass(name = "StreamingDocument", unsendable)]
pub struct PyStreamingDocument {
    inner: Option<streaming::StreamingDocument<File>>,
}
impl PyStreamingDocument {
    fn doc(&self) -> PyResult<&streaming::StreamingDocument<File>> {
        self.inner
            .as_ref()
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("StreamingDocument is closed"))
    }
    fn doc_mut(&mut self) -> PyResult<&mut streaming::StreamingDocument<File>> {
        self.inner
            .as_mut()
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("StreamingDocument is closed"))
    }
}
#[pymethods]
impl PyStreamingDocument {
    #[staticmethod]
    #[pyo3(signature = (path, options=None))]
    fn open(py: Python<'_>, path: String, options: Option<&PyStreamingOptions>) -> PyResult<Self> {
        let options = options.map(|o| o.inner.clone()).unwrap_or_default();
        let inner = py.detach(move || {
            let file =
                File::open(path).map_err(|e| crate::errors::PdfIoError::new_err(e.to_string()))?;
            streaming::StreamingDocument::new(file, options).map_err(to_py_err)
        })?;
        Ok(Self { inner: Some(inner) })
    }
    fn configuration(&self) -> PyResult<PyStreamingConfiguration> {
        Ok(PyStreamingConfiguration {
            inner: self.doc()?.configuration().clone(),
        })
    }
    fn next_page(&mut self, py: Python<'_>) -> PyResult<Option<PyStreamingPage>> {
        let doc = self.doc_mut()?;
        py.detach(|| doc.next_page())
            .map_err(to_py_err)?
            .map(PyStreamingPage::from_core)
            .transpose()
    }
    fn cached_pages(&self) -> PyResult<usize> {
        Ok(self.doc()?.cached_pages())
    }
    fn memory_usage(&self) -> PyResult<usize> {
        Ok(self.doc()?.memory_usage())
    }
    fn clear_cache(&mut self) -> PyResult<()> {
        self.doc_mut()?.clear_cache();
        Ok(())
    }
    fn close(&mut self) {
        self.inner = None;
    }
    fn __enter__(slf: PyRef<'_, Self>) -> PyResult<PyRef<'_, Self>> {
        slf.doc()?;
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
}

/// Native lazy object loading. Cache capacity counts adapter objects and does
/// not cap parser caches, eager loading or total process memory.
#[pyclass(name = "LazyDocument", unsendable)]
pub struct PyLazyDocument {
    inner: Option<memory::LazyDocument<File>>,
    page_count: u32,
}
impl PyLazyDocument {
    fn doc(&self) -> PyResult<&memory::LazyDocument<File>> {
        self.inner
            .as_ref()
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("LazyDocument is closed"))
    }
}
#[pymethods]
impl PyLazyDocument {
    #[staticmethod]
    #[pyo3(signature = (path, options=None))]
    fn open(py: Python<'_>, path: String, options: Option<&PyMemoryOptions>) -> PyResult<Self> {
        let options = options.map(|o| o.inner.clone()).unwrap_or_default();
        let inner = py
            .detach(move || memory::LazyDocument::open(path, options))
            .map_err(to_py_err)?;
        let page_count = inner.page_count();
        Ok(Self {
            inner: Some(inner),
            page_count,
        })
    }
    /// Number of pages (read-only property).
    #[getter]
    fn page_count(&self) -> u32 {
        self.page_count
    }
    fn configuration(&self) -> PyResult<PyMemoryConfiguration> {
        Ok(PyMemoryConfiguration {
            inner: self.doc()?.configuration().clone(),
        })
    }
    fn get_page(&self, py: Python<'_>, index: u32) -> PyResult<PyParsedPage> {
        let doc = self.doc()?;
        Ok(PyParsedPage {
            inner: py.detach(|| doc.get_page(index)).map_err(to_py_err)?,
        })
    }
    #[pyo3(signature = (number, generation=0))]
    fn get_object(&self, py: Python<'_>, number: u32, generation: u16) -> PyResult<PyPdfValue> {
        let doc = self.doc()?;
        let id = oxidize_pdf::objects::ObjectId::new(number, generation);
        let object = py.detach(|| doc.get_object(&id)).map_err(to_py_err)?;
        Ok(PyPdfValue {
            inner: object.as_ref().clone(),
        })
    }
    fn preload_page(&self, py: Python<'_>, index: u32) -> PyResult<()> {
        let doc = self.doc()?;
        py.detach(|| doc.preload_page(index)).map_err(to_py_err)
    }
    fn memory_stats(&self) -> PyResult<PyMemoryStats> {
        Ok(PyMemoryStats {
            inner: self.doc()?.memory_stats(),
        })
    }
    fn clear_cache(&self) -> PyResult<()> {
        self.doc()?.clear_cache();
        Ok(())
    }
    fn close(&mut self) {
        self.inner = None;
    }
    fn __enter__(slf: PyRef<'_, Self>) -> PyResult<PyRef<'_, Self>> {
        slf.doc()?;
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
        format!("LazyDocument(pages={})", self.page_count)
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyStreamingOptions>()?;
    m.add_class::<PyMemoryOptions>()?;
    m.add_class::<PyUnsupportedMemoryOption>()?;
    m.add_class::<PyMemoryConfiguration>()?;
    m.add_class::<PyStreamingConfiguration>()?;
    m.add_class::<PyMemoryStats>()?;
    m.add_class::<PyStreamingDocument>()?;
    m.add_class::<PyLazyDocument>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::{Cursor, Read, Seek, SeekFrom};
    use std::sync::{Arc, Mutex};

    struct Observed {
        bytes: Cursor<Vec<u8>>,
        requests: Arc<Mutex<Vec<usize>>>,
    }
    impl Read for Observed {
        fn read(&mut self, buffer: &mut [u8]) -> std::io::Result<usize> {
            self.requests.lock().unwrap().push(buffer.len());
            self.bytes.read(buffer)
        }
    }
    impl Seek for Observed {
        fn seek(&mut self, pos: SeekFrom) -> std::io::Result<u64> {
            self.bytes.seek(pos)
        }
    }
    // No PDF writer under test produces this fixture. The unrelated string is
    // large enough that one-byte and 64-KiB buffers require different I/O.
    fn fixture() -> Vec<u8> {
        let objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>".to_vec(),
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>".to_vec(),
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 321 456] >>".to_vec(),
            format!("({})", "payload ".repeat(10000)).into_bytes(),
        ];
        let mut pdf = b"%PDF-1.7\n".to_vec();
        let mut offsets = Vec::new();
        for (i, object) in objects.iter().enumerate() {
            offsets.push(pdf.len());
            pdf.extend_from_slice(format!("{} 0 obj\n", i + 1).as_bytes());
            pdf.extend_from_slice(object);
            pdf.extend_from_slice(b"\nendobj\n");
        }
        let xref = pdf.len();
        pdf.extend_from_slice(b"xref\n0 5\n0000000000 65535 f \n");
        for offset in offsets {
            pdf.extend_from_slice(format!("{offset:010} 00000 n \n").as_bytes());
        }
        pdf.extend_from_slice(
            format!("trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n").as_bytes(),
        );
        pdf
    }

    #[test]
    fn configured_buffers_and_eager_loading_change_real_io() {
        let mut read_counts = Vec::new();
        for (lazy, buffer) in [(true, 1), (true, 65536), (false, 65536)] {
            let requests = Arc::new(Mutex::new(Vec::new()));
            let reader = oxidize_pdf::PdfReader::new(Observed {
                bytes: Cursor::new(fixture()),
                requests: requests.clone(),
            })
            .unwrap();
            let options = PyMemoryOptions::new(lazy, false, 0, false, buffer, 0);
            let doc = memory::LazyDocument::new(reader, options.inner).unwrap();
            requests.lock().unwrap().clear();
            let value = doc
                .get_object(&oxidize_pdf::objects::ObjectId::new(4, 0))
                .unwrap();
            assert!(
                matches!(&*value, oxidize_pdf::parser::PdfObject::String(s) if s.as_bytes().len() == 80000)
            );
            read_counts.push(requests.lock().unwrap().len());
        }
        assert!(
            read_counts[0] > read_counts[1],
            "small buffer must require more reads: {read_counts:?}"
        );
        assert!(read_counts[1] > 0, "lazy load must perform I/O");
        assert_eq!(
            read_counts[2], 0,
            "eager load must already contain the object"
        );

        for buffer in [1, 65536] {
            let requests = Arc::new(Mutex::new(Vec::new()));
            let options = PyStreamingOptions::new(buffer, 0, 0, false, 0);
            let mut doc = streaming::StreamingDocument::new(
                Observed {
                    bytes: Cursor::new(fixture()),
                    requests: requests.clone(),
                },
                options.inner,
            )
            .unwrap();
            assert_eq!(doc.next_page().unwrap().unwrap().width(), 321.0);
            assert_eq!(
                requests.lock().unwrap().contains(&65536),
                buffer == 65536,
                "requested buffer must reach the underlying reader"
            );
        }
    }
}
