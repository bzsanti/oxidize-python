//! Stable document-analysis adapters, independent of the experimental SPI.
use std::sync::Mutex;

use oxidize_pdf::pipeline::{ElementGraph, TokenCounter};
use pyo3::exceptions::{PyIndexError, PyTypeError};
use pyo3::prelude::*;
use pyo3::types::PyBool;

/// Owns the graph; its indices refer to the elements returned alongside it.
#[pyclass(name = "ElementGraph", frozen)]
pub struct PyElementGraph {
    pub inner: ElementGraph,
}

impl PyElementGraph {
    fn checked(&self, index: usize) -> PyResult<usize> {
        if index >= self.inner.len() {
            Err(PyIndexError::new_err("element index out of range"))
        } else {
            Ok(index)
        }
    }
}

#[pymethods]
impl PyElementGraph {
    fn __len__(&self) -> usize {
        self.inner.len()
    }
    fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }
    fn parent_of(&self, index: usize) -> PyResult<Option<usize>> {
        Ok(self.inner.parent_of(self.checked(index)?))
    }
    fn children_of(&self, index: usize) -> PyResult<Vec<usize>> {
        Ok(self.inner.children_of(self.checked(index)?).to_vec())
    }
    fn next_of(&self, index: usize) -> PyResult<Option<usize>> {
        Ok(self.inner.next_of(self.checked(index)?))
    }
    fn prev_of(&self, index: usize) -> PyResult<Option<usize>> {
        Ok(self.inner.prev_of(self.checked(index)?))
    }
    fn elements_in_section(&self, index: usize) -> PyResult<Vec<usize>> {
        Ok(self.inner.elements_in_section(self.checked(index)?))
    }
    fn top_level_sections(&self) -> Vec<usize> {
        self.inner.top_level_sections()
    }
}

/// Core's counter trait is infallible. Keep the first Python error and stop
/// calling user code after failure; the reader discards the result and raises
/// that same error. A zero count only lets the finite core loop unwind.
/// No mutex is held while running Python code. The default non-additive policy
/// measures whole joined strings, avoiding incorrect budgets for BPE counters.
pub(crate) struct CallbackCounter {
    callback: Py<PyAny>,
    error: Mutex<Option<PyErr>>,
}

impl CallbackCounter {
    pub fn new(callback: Py<PyAny>) -> Self {
        Self {
            callback,
            error: Mutex::new(None),
        }
    }
    pub fn take_error(&self) -> Option<PyErr> {
        self.error.lock().unwrap_or_else(|e| e.into_inner()).take()
    }
}

impl TokenCounter for CallbackCounter {
    fn count(&self, text: &str) -> usize {
        if self
            .error
            .lock()
            .unwrap_or_else(|e| e.into_inner())
            .is_some()
        {
            return 0;
        }
        let result = Python::attach(|py| {
            let value = self.callback.bind(py).call1((text,))?;
            if value.is_instance_of::<PyBool>() {
                return Err(PyTypeError::new_err(
                    "token counter must return an integer, not bool",
                ));
            }
            value.extract::<usize>()
        });
        match result {
            Ok(count) => count,
            Err(error) => {
                let mut slot = self.error.lock().unwrap_or_else(|e| e.into_inner());
                if slot.is_none() {
                    *slot = Some(error);
                }
                0
            }
        }
    }
    fn name(&self) -> &'static str {
        "python-callback"
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyElementGraph>()
}
