//! Unstable Analysis SPI bindings — Python callbacks over the upstream
//! `unstable-spi` traits (`ChunkingStrategy`, `ElementClassifier`,
//! `MetadataEnricher`) and the [`AnalysisPipeline`] builder.
//!
//! The SPI is exempt from semver upstream while experimental, so we expose it
//! through the `oxidize_pdf.experimental` submodule on the Python side to
//! signal that the surface may change between releases.
//!
//! Error-propagation strategy: a Python callback that raises stores the
//! `PyErr` in a `Mutex` slot held by the adapter. The trait's
//! return-without-Result signature is honoured (the adapter yields an empty
//! `Vec`); the binding caller checks the slot after the upstream pipeline
//! returns and surfaces the error instead of the (now-empty) chunk list.

use std::collections::BTreeMap;
use std::sync::{Arc, Mutex};

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use oxidize_pdf::pipeline::{
    AnalysisPipeline, ChunkGroup, ChunkMetadata, ChunkingStrategy, ClassLabel, ClassifyContext,
    Element, ElementClassifier, EnrichContext, HybridChunkConfig, MetadataEnricher,
};

use crate::ai_pipeline::{PyDocumentSource, PyElement};

// ── PyChunkGroup ───────────────────────────────────────────────────────────

/// A grouping of pipeline elements destined to become one chunk.
///
/// A custom :class:`ChunkingStrategy` returns a list of these; the pipeline
/// owns everything downstream (``chunk_id``, prev/next links, metadata).
#[pyclass(name = "ChunkGroup", skip_from_py_object)]
#[derive(Clone)]
pub struct PyChunkGroup {
    pub inner: ChunkGroup,
}

#[pymethods]
impl PyChunkGroup {
    #[new]
    #[pyo3(signature = (elements, heading_context = None))]
    fn new(elements: Vec<PyRef<PyElement>>, heading_context: Option<String>) -> Self {
        let inner_elems: Vec<Element> = elements.iter().map(|e| e.inner.clone()).collect();
        Self {
            inner: ChunkGroup::new(inner_elems, heading_context),
        }
    }

    /// The elements that form this chunk, in order.
    #[getter]
    fn elements(&self) -> Vec<PyElement> {
        self.inner
            .elements
            .iter()
            .map(|e| PyElement { inner: e.clone() })
            .collect()
    }

    /// Optional heading context to prepend for embedding.
    #[getter]
    fn heading_context(&self) -> Option<String> {
        self.inner.heading_context.clone()
    }

    fn __repr__(&self) -> String {
        format!(
            "ChunkGroup(elements=[{} items], heading_context={:?})",
            self.inner.elements.len(),
            self.inner.heading_context,
        )
    }
}

// ── PyChunkingStrategyAdapter ──────────────────────────────────────────────

/// Wraps a Python object exposing ``chunk(self, elements) -> list[ChunkGroup]``
/// in a Rust `impl ChunkingStrategy` so it can be plugged into the upstream
/// pipeline.
///
/// `Send + Sync`: `Py<PyAny>` is itself `Send + Sync` (every dereference
/// requires the GIL); `Arc<Mutex<…>>` covers the error slot.
pub(crate) struct PyChunkingStrategyAdapter {
    callable: Py<PyAny>,
    err: Arc<Mutex<Option<PyErr>>>,
}

impl ChunkingStrategy for PyChunkingStrategyAdapter {
    fn chunk(&self, elements: &[Element]) -> Vec<ChunkGroup> {
        let result: PyResult<Vec<ChunkGroup>> = Python::attach(|py| {
            // Wrap each `Element` in `PyElement` so user code can read
            // type/text/page without owning the borrow.
            let py_elements: Vec<Py<PyElement>> = elements
                .iter()
                .map(|e| Py::new(py, PyElement { inner: e.clone() }))
                .collect::<PyResult<_>>()?;
            let py_list = PyList::new(py, py_elements)?;
            let py_groups = self
                .callable
                .bind(py)
                .call_method1("chunk", (py_list,))?;
            let groups: Vec<PyRef<PyChunkGroup>> = py_groups.extract()?;
            Ok(groups.iter().map(|g| g.inner.clone()).collect())
        });
        match result {
            Ok(groups) => groups,
            Err(e) => {
                // Surface the error after the upstream call returns. Store
                // unless a previous call already populated the slot (we keep
                // the first error for clarity).
                let mut slot = self.err.lock().unwrap();
                if slot.is_none() {
                    *slot = Some(e);
                }
                Vec::new()
            }
        }
    }
}

// ── PyClassLabel ───────────────────────────────────────────────────────────

/// An open class label assigned to an element by an :class:`ElementClassifier`.
///
/// The label is an opaque string — semantics live entirely in the provider.
#[pyclass(name = "ClassLabel", frozen, skip_from_py_object)]
#[derive(Clone)]
pub struct PyClassLabel {
    pub inner: ClassLabel,
}

#[pymethods]
impl PyClassLabel {
    #[new]
    fn new(label: String) -> Self {
        Self {
            inner: ClassLabel::new(label),
        }
    }

    /// The label as a string.
    fn as_str(&self) -> &str {
        self.inner.as_str()
    }

    fn __str__(&self) -> &str {
        self.inner.as_str()
    }

    fn __repr__(&self) -> String {
        format!("ClassLabel({:?})", self.inner.as_str())
    }

    fn __eq__(&self, other: &Bound<'_, PyAny>) -> PyResult<bool> {
        if let Ok(other_label) = other.extract::<PyRef<PyClassLabel>>() {
            return Ok(self.inner == other_label.inner);
        }
        if let Ok(other_str) = other.extract::<String>() {
            return Ok(self.inner.as_str() == other_str);
        }
        Ok(false)
    }

    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        let mut hasher = DefaultHasher::new();
        self.inner.as_str().hash(&mut hasher);
        hasher.finish()
    }
}

// ── PyClassifyContext ──────────────────────────────────────────────────────

/// Read-only context handed to an :class:`ElementClassifier`.
///
/// ``elements`` is the full ordered element slice for the document;
/// ``index`` is the position of the element currently being classified.
/// Implementations should look only at a small constant window of neighbours
/// so the overall classification pass stays O(N).
#[pyclass(name = "ClassifyContext", frozen, skip_from_py_object)]
pub struct PyClassifyContext {
    /// The Python list[Element] — shared (refcount-cloned) across classify calls.
    elements: Py<pyo3::types::PyList>,
    index: usize,
}

#[pymethods]
impl PyClassifyContext {
    /// All elements of the document, in order.
    #[getter]
    fn elements<'py>(&self, py: Python<'py>) -> Bound<'py, pyo3::types::PyList> {
        self.elements.bind(py).clone()
    }

    /// Index of the element currently being classified.
    #[getter]
    fn index(&self) -> usize {
        self.index
    }

    fn __repr__(&self) -> String {
        format!("ClassifyContext(index={})", self.index)
    }
}

// ── PyElementClassifierAdapter ─────────────────────────────────────────────

/// Wraps a Python object exposing
/// ``classify(self, element, ctx) -> ClassLabel | None`` in a Rust
/// `impl ElementClassifier`. Builds the Python ``ctx.elements`` list lazily on
/// first call and caches it for the rest of the document so the classify pass
/// stays O(N) rather than degenerating to O(N²).
pub(crate) struct PyElementClassifierAdapter {
    callable: Py<PyAny>,
    err: Arc<Mutex<Option<PyErr>>>,
    cached_elements_list: Mutex<Option<Py<pyo3::types::PyList>>>,
}

impl ElementClassifier for PyElementClassifierAdapter {
    fn classify(&self, element: &Element, ctx: &ClassifyContext) -> Option<ClassLabel> {
        let result: PyResult<Option<ClassLabel>> = Python::attach(|py| {
            // Build the elements list lazily and reuse it across calls.
            let elements_list = {
                let mut cache = self.cached_elements_list.lock().unwrap();
                if cache.is_none() {
                    let py_elements: Vec<Py<PyElement>> = ctx
                        .elements
                        .iter()
                        .map(|e| Py::new(py, PyElement { inner: e.clone() }))
                        .collect::<PyResult<_>>()?;
                    let list = PyList::new(py, py_elements)?;
                    *cache = Some(list.unbind());
                }
                cache.as_ref().unwrap().clone_ref(py)
            };
            let py_ctx = Py::new(
                py,
                PyClassifyContext {
                    elements: elements_list,
                    index: ctx.index,
                },
            )?;
            let py_element = Py::new(py, PyElement { inner: element.clone() })?;
            let result = self
                .callable
                .bind(py)
                .call_method1("classify", (py_element, py_ctx))?;
            if result.is_none() {
                return Ok(None);
            }
            let label: PyRef<PyClassLabel> = result.extract()?;
            Ok(Some(label.inner.clone()))
        });
        match result {
            Ok(label) => label,
            Err(e) => {
                let mut slot = self.err.lock().unwrap();
                if slot.is_none() {
                    *slot = Some(e);
                }
                None
            }
        }
    }
}

// ── JSON value ↔ Python conversion ─────────────────────────────────────────

/// Convert a `serde_json::Value` into a Python object.
///
/// Surfaces JSON primitives as their Python equivalents (None, bool, int,
/// float, str, list, dict). Used to expose the open ``extra`` bag on a chunk.
pub(crate) fn json_value_to_py<'py>(
    py: Python<'py>,
    value: &serde_json::Value,
) -> PyResult<Bound<'py, PyAny>> {
    match value {
        serde_json::Value::Null => Ok(py.None().into_bound(py)),
        serde_json::Value::Bool(b) => Ok(b.into_pyobject(py)?.to_owned().into_any()),
        serde_json::Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.into_pyobject(py)?.into_any())
            } else if let Some(u) = n.as_u64() {
                Ok(u.into_pyobject(py)?.into_any())
            } else {
                let f = n.as_f64().unwrap_or(0.0);
                Ok(f.into_pyobject(py)?.into_any())
            }
        }
        serde_json::Value::String(s) => Ok(s.as_str().into_pyobject(py)?.into_any()),
        serde_json::Value::Array(items) => {
            let py_items: Vec<Bound<PyAny>> = items
                .iter()
                .map(|v| json_value_to_py(py, v))
                .collect::<PyResult<_>>()?;
            Ok(PyList::new(py, py_items)?.into_any())
        }
        serde_json::Value::Object(map) => {
            let dict = PyDict::new(py);
            for (k, v) in map {
                dict.set_item(k, json_value_to_py(py, v)?)?;
            }
            Ok(dict.into_any())
        }
    }
}

/// Convert a Python object into a `serde_json::Value`.
///
/// Accepts None / bool / int / float / str / list / dict; everything else
/// raises `TypeError`. ``bool`` is checked before ``int`` because Python
/// booleans inherit from int.
fn py_to_json_value(value: &Bound<'_, PyAny>) -> PyResult<serde_json::Value> {
    use serde_json::Value;

    if value.is_none() {
        return Ok(Value::Null);
    }
    if let Ok(b) = value.extract::<bool>() {
        return Ok(Value::Bool(b));
    }
    if let Ok(i) = value.extract::<i64>() {
        return Ok(Value::Number(i.into()));
    }
    if let Ok(f) = value.extract::<f64>() {
        return Ok(serde_json::Number::from_f64(f)
            .map(Value::Number)
            .unwrap_or(Value::Null));
    }
    if let Ok(s) = value.extract::<String>() {
        return Ok(Value::String(s));
    }
    if let Ok(list) = value.cast::<PyList>() {
        let mut arr = Vec::with_capacity(list.len());
        for item in list.iter() {
            arr.push(py_to_json_value(&item)?);
        }
        return Ok(Value::Array(arr));
    }
    if let Ok(dict) = value.cast::<PyDict>() {
        let mut obj = serde_json::Map::with_capacity(dict.len());
        for (k, v) in dict.iter() {
            let key: String = k.extract()?;
            obj.insert(key, py_to_json_value(&v)?);
        }
        return Ok(Value::Object(obj));
    }
    Err(pyo3::exceptions::PyTypeError::new_err(
        "extra values must be None/bool/int/float/str/list/dict",
    ))
}

/// Materialize a `BTreeMap<String, JsonValue>` as a Python ``dict``.
pub(crate) fn extra_map_to_py_dict<'py>(
    py: Python<'py>,
    extra: &BTreeMap<String, serde_json::Value>,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    for (k, v) in extra {
        dict.set_item(k, json_value_to_py(py, v)?)?;
    }
    Ok(dict)
}

/// Replace `extra` from a Python dict, validating every value.
fn py_dict_to_extra_map(
    dict: &Bound<'_, PyDict>,
) -> PyResult<BTreeMap<String, serde_json::Value>> {
    let mut out = BTreeMap::new();
    for (k, v) in dict.iter() {
        let key: String = k.extract()?;
        out.insert(key, py_to_json_value(&v)?);
    }
    Ok(out)
}

// ── PyEnrichContext ────────────────────────────────────────────────────────

/// Read-only context handed to a :class:`MetadataEnricher`.
#[pyclass(name = "EnrichContext", frozen, skip_from_py_object)]
pub struct PyEnrichContext {
    text: String,
    elements: Py<PyList>,
    heading_path: Vec<String>,
}

#[pymethods]
impl PyEnrichContext {
    /// The chunk's text (elements joined by newlines).
    #[getter]
    fn text(&self) -> &str {
        &self.text
    }

    /// The elements that compose this chunk, in order.
    #[getter]
    fn elements<'py>(&self, py: Python<'py>) -> Bound<'py, PyList> {
        self.elements.bind(py).clone()
    }

    /// The chunk's heading breadcrumb, root → leaf.
    #[getter]
    fn heading_path(&self) -> Vec<String> {
        self.heading_path.clone()
    }

    fn __repr__(&self) -> String {
        format!(
            "EnrichContext(text_len={}, heading_path={:?})",
            self.text.len(),
            self.heading_path,
        )
    }
}

// ── PyMetadataEnricherAdapter ──────────────────────────────────────────────

/// Wraps a Python object exposing
/// ``enrich(self, ctx: EnrichContext, extra: dict) -> None`` in a Rust
/// `impl MetadataEnricher`. The Python enricher mutates ``extra`` in place;
/// the adapter merges the (possibly updated) dict back into ``meta.extra``.
pub(crate) struct PyMetadataEnricherAdapter {
    callable: Py<PyAny>,
    err: Arc<Mutex<Option<PyErr>>>,
}

impl MetadataEnricher for PyMetadataEnricherAdapter {
    fn enrich(&self, ctx: &EnrichContext, meta: &mut ChunkMetadata) {
        let result: PyResult<BTreeMap<String, serde_json::Value>> = Python::attach(|py| {
            // Materialize the elements list once per enrich call. Enrich runs
            // O(chunks) — not O(elements²) — so the cost is bounded.
            let py_elements: Vec<Py<PyElement>> = ctx
                .elements
                .iter()
                .map(|e| Py::new(py, PyElement { inner: e.clone() }))
                .collect::<PyResult<_>>()?;
            let py_elements_list = PyList::new(py, py_elements)?;
            let py_ctx = Py::new(
                py,
                PyEnrichContext {
                    text: ctx.text.to_string(),
                    elements: py_elements_list.unbind(),
                    heading_path: ctx.heading_path.to_vec(),
                },
            )?;
            let extra_dict = extra_map_to_py_dict(py, &meta.extra)?;
            self.callable
                .bind(py)
                .call_method1("enrich", (py_ctx, &extra_dict))?;
            py_dict_to_extra_map(&extra_dict)
        });
        match result {
            Ok(new_extra) => {
                meta.extra = new_extra;
            }
            Err(e) => {
                let mut slot = self.err.lock().unwrap();
                if slot.is_none() {
                    *slot = Some(e);
                }
            }
        }
    }
}

// ── PyAnalysisPipeline ─────────────────────────────────────────────────────

/// Configures the analysis pipeline: which chunking strategy to run and the
/// token budget used to flag oversized chunks.
///
/// ``AnalysisPipeline()`` reproduces :meth:`PdfReader.rag_chunks` exactly when
/// passed to :meth:`PdfReader.rag_chunks_with_pipeline`.
#[pyclass(name = "AnalysisPipeline")]
pub struct PyAnalysisPipeline {
    /// User-supplied Python object implementing ``chunk(elements)``.
    pub(crate) chunking: Option<Py<PyAny>>,
    /// Token budget used to flag oversized chunks; defaults to the
    /// upstream `HybridChunkConfig::default().max_tokens`.
    pub(crate) max_tokens: usize,
    /// User-supplied Python object implementing ``classify(element, ctx)``.
    pub(crate) classifier: Option<Py<PyAny>>,
    /// User-supplied Python objects implementing ``enrich(ctx, extra)``,
    /// in registration order.
    pub(crate) enrichers: Vec<Py<PyAny>>,
    /// Optional source-document metadata to stamp on every chunk.
    pub(crate) source: Option<PyDocumentSource>,
}

#[pymethods]
impl PyAnalysisPipeline {
    #[new]
    fn new() -> Self {
        Self {
            chunking: None,
            max_tokens: HybridChunkConfig::default().max_tokens,
            classifier: None,
            enrichers: Vec::new(),
            source: None,
        }
    }

    /// Replace the chunking strategy.
    ///
    /// ``strategy`` must expose ``chunk(self, elements: list[Element]) ->
    /// list[ChunkGroup]``.
    fn with_chunking(&self, py: Python, strategy: Py<PyAny>) -> Self {
        let mut next = self.shallow_clone(py);
        next.chunking = Some(strategy);
        next
    }

    /// Set the token budget used to flag oversized chunks.
    fn with_max_tokens(&self, py: Python, max_tokens: usize) -> Self {
        let mut next = self.shallow_clone(py);
        next.max_tokens = max_tokens;
        next
    }

    /// Register a classifier that labels elements before chunking.
    ///
    /// ``classifier`` must expose
    /// ``classify(self, element: Element, ctx: ClassifyContext) -> ClassLabel | None``.
    /// The label is stored on :attr:`Element.class_label` and may be read by
    /// a custom chunking strategy to decide chunk boundaries.
    fn with_classifier(&self, py: Python, classifier: Py<PyAny>) -> Self {
        let mut next = self.shallow_clone(py);
        next.classifier = Some(classifier);
        next
    }

    /// Register an enricher that writes provider-specific fields into each
    /// chunk's ``extra`` bag after metadata is derived.
    ///
    /// ``enricher`` must expose
    /// ``enrich(self, ctx: EnrichContext, extra: dict[str, Any]) -> None``.
    /// Enrichers run in registration order; mutate ``extra`` in place.
    fn with_enricher(&self, py: Python, enricher: Py<PyAny>) -> Self {
        let mut next = self.shallow_clone(py);
        next.enrichers.push(enricher);
        next
    }

    /// Stamp source-document metadata on every chunk produced by the
    /// pipeline (same effect as :meth:`PdfReader.rag_chunks_with_source`).
    fn with_source(&self, py: Python, source: PyRef<'_, PyDocumentSource>) -> Self {
        let mut next = self.shallow_clone(py);
        next.source = Some(source.clone());
        next
    }

    fn __repr__(&self) -> String {
        format!(
            "AnalysisPipeline(custom_chunking={}, custom_classifier={}, enrichers={}, source={}, max_tokens={})",
            self.chunking.is_some(),
            self.classifier.is_some(),
            self.enrichers.len(),
            self.source.is_some(),
            self.max_tokens,
        )
    }
}

impl PyAnalysisPipeline {
    /// Shallow clone that respects the GIL for the `Py<PyAny>` field.
    fn shallow_clone(&self, py: Python) -> Self {
        Self {
            chunking: self.chunking.as_ref().map(|c| c.clone_ref(py)),
            max_tokens: self.max_tokens,
            classifier: self.classifier.as_ref().map(|c| c.clone_ref(py)),
            enrichers: self.enrichers.iter().map(|e| e.clone_ref(py)).collect(),
            source: self.source.clone(),
        }
    }

    /// Build the upstream `AnalysisPipeline` from the current Python-side
    /// state. Returns the pipeline and the error slot the caller must check
    /// after running — the chunking, classifier and enricher adapters all
    /// share the same slot so the first failure wins.
    pub(crate) fn build(&self, py: Python) -> (AnalysisPipeline, Arc<Mutex<Option<PyErr>>>) {
        let err = Arc::new(Mutex::new(None));
        let mut pipeline = AnalysisPipeline::new().with_max_tokens(self.max_tokens);
        if let Some(callable) = self.chunking.as_ref() {
            let adapter = PyChunkingStrategyAdapter {
                callable: callable.clone_ref(py),
                err: err.clone(),
            };
            pipeline = pipeline.with_chunking(Box::new(adapter));
        }
        if let Some(callable) = self.classifier.as_ref() {
            let adapter = PyElementClassifierAdapter {
                callable: callable.clone_ref(py),
                err: err.clone(),
                cached_elements_list: Mutex::new(None),
            };
            pipeline = pipeline.with_classifier(Box::new(adapter));
        }
        for callable in &self.enrichers {
            let adapter = PyMetadataEnricherAdapter {
                callable: callable.clone_ref(py),
                err: err.clone(),
            };
            pipeline = pipeline.with_enricher(Box::new(adapter));
        }
        if let Some(source) = self.source.as_ref() {
            pipeline = pipeline.with_source(source.inner.clone());
        }
        (pipeline, err)
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyChunkGroup>()?;
    m.add_class::<PyAnalysisPipeline>()?;
    m.add_class::<PyClassLabel>()?;
    m.add_class::<PyClassifyContext>()?;
    m.add_class::<PyEnrichContext>()?;
    Ok(())
}
