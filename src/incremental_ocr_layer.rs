//! Incremental invisible text layers from caller-supplied OCR results.
use crate::errors::to_py_err;
use oxidize_pdf::writer as core;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

/// An owned word and region [x, y, width, height] in PDF user-space coordinates.
/// Semantic validation occurs in plan/apply, as in the core API.
#[pyclass(name = "OcrLayerFragment", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyOcrLayerFragment {
    inner: core::OcrLayerFragment,
}
#[pymethods]
impl PyOcrLayerFragment {
    #[new]
    fn new(text: String, region: [f64; 4], confidence: f64, reading_order: u32) -> Self {
        Self {
            inner: core::OcrLayerFragment {
                text,
                region,
                confidence,
                reading_order,
            },
        }
    }
    #[getter]
    fn text(&self) -> &str {
        &self.inner.text
    }
    #[getter]
    fn region(&self) -> [f64; 4] {
        self.inner.region
    }
    #[getter]
    fn confidence(&self) -> f64 {
        self.inner.confidence
    }
    #[getter]
    fn reading_order(&self) -> u32 {
        self.inner.reading_order
    }
}
/// Caller-supplied fragments for one page; no recognition is performed.
#[pyclass(name = "OcrLayerPage", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyOcrLayerPage {
    inner: core::OcrLayerPage,
}
#[pymethods]
impl PyOcrLayerPage {
    #[new]
    fn new(page_index: u32, language: String, fragments: Vec<PyOcrLayerFragment>) -> Self {
        Self {
            inner: core::OcrLayerPage {
                page_index,
                language,
                fragments: fragments.into_iter().map(|f| f.inner).collect(),
            },
        }
    }
    #[getter]
    fn page_index(&self) -> u32 {
        self.inner.page_index
    }
    #[getter]
    fn language(&self) -> &str {
        &self.inner.language
    }
    #[getter]
    fn fragments(&self) -> Vec<PyOcrLayerFragment> {
        self.inner
            .fragments
            .iter()
            .cloned()
            .map(|inner| PyOcrLayerFragment { inner })
            .collect()
    }
}
#[pyclass(name = "OcrLayerPlan", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyOcrLayerPlan {
    inner: core::OcrLayerPlan,
}
#[pymethods]
impl PyOcrLayerPlan {
    #[getter]
    fn pages(&self) -> Vec<u32> {
        self.inner.pages.clone()
    }
    #[getter]
    fn streams_added(&self) -> usize {
        self.inner.streams_added
    }
    #[getter]
    fn resources_added(&self) -> usize {
        self.inner.resources_added
    }
    #[getter]
    fn pages_skipped_existing_ocr(&self) -> Vec<u32> {
        self.inner.pages_skipped_existing_ocr.clone()
    }
}
#[pyclass(name = "OcrLayerUpdate", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyOcrLayerUpdate {
    inner: core::OcrLayerUpdate,
}
#[pymethods]
impl PyOcrLayerUpdate {
    #[getter]
    fn pdf_bytes<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.inner.pdf_bytes)
    }
    #[getter]
    fn plan(&self) -> PyOcrLayerPlan {
        PyOcrLayerPlan {
            inner: self.inner.plan.clone(),
        }
    }
}
/// Owns an immutable PDF snapshot. Each apply returns an independent revision.
/// Both plan and apply enforce core permissions, even for an empty request.
#[pyclass(name = "IncrementalOcrLayerEditor", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyIncrementalOcrLayerEditor {
    base: Vec<u8>,
}
#[pymethods]
impl PyIncrementalOcrLayerEditor {
    #[new]
    fn new(pdf: &[u8]) -> Self {
        Self { base: pdf.to_vec() }
    }
    fn plan(&self, py: Python<'_>, pages: Vec<PyOcrLayerPage>) -> PyResult<PyOcrLayerPlan> {
        let pages: Vec<_> = pages.into_iter().map(|p| p.inner).collect();
        let inner = py
            .detach(|| core::IncrementalOcrLayerEditor::new(&self.base).plan(&pages))
            .map_err(to_py_err)?;
        Ok(PyOcrLayerPlan { inner })
    }
    fn apply(&self, py: Python<'_>, pages: Vec<PyOcrLayerPage>) -> PyResult<PyOcrLayerUpdate> {
        let pages: Vec<_> = pages.into_iter().map(|p| p.inner).collect();
        let inner = py
            .detach(|| core::IncrementalOcrLayerEditor::new(&self.base).apply(&pages))
            .map_err(to_py_err)?;
        Ok(PyOcrLayerUpdate { inner })
    }
}
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyOcrLayerFragment>()?;
    m.add_class::<PyOcrLayerPage>()?;
    m.add_class::<PyOcrLayerPlan>()?;
    m.add_class::<PyOcrLayerUpdate>()?;
    m.add_class::<PyIncrementalOcrLayerEditor>()?;
    Ok(())
}
