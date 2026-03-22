use pyo3::prelude::*;

use oxidize_pdf::structure::{OutlineItem, OutlineTree};

use crate::actions::PyDestination;
use crate::types::PyColor;

// ── OutlineItem ───────────────────────────────────────────────────────────

#[pyclass(name = "OutlineItem", from_py_object)]
#[derive(Clone)]
pub struct PyOutlineItem {
    pub inner: OutlineItem,
}

#[pymethods]
impl PyOutlineItem {
    #[new]
    fn new(title: &str) -> Self {
        Self {
            inner: OutlineItem::new(title),
        }
    }

    fn with_destination(self_: PyRef<'_, Self>, dest: &PyDestination) -> Self {
        Self {
            inner: self_.inner.clone().with_destination(dest.inner.clone()),
        }
    }

    fn with_color(self_: PyRef<'_, Self>, color: &PyColor) -> Self {
        Self {
            inner: self_.inner.clone().with_color(color.inner),
        }
    }

    fn bold(self_: PyRef<'_, Self>) -> Self {
        Self {
            inner: self_.inner.clone().bold(),
        }
    }

    fn italic(self_: PyRef<'_, Self>) -> Self {
        Self {
            inner: self_.inner.clone().italic(),
        }
    }

    fn closed(self_: PyRef<'_, Self>) -> Self {
        Self {
            inner: self_.inner.clone().closed(),
        }
    }

    fn add_child(&mut self, child: &PyOutlineItem) {
        self.inner.add_child(child.inner.clone());
    }

    fn __repr__(&self) -> String {
        format!("OutlineItem(title={:?})", self.inner.title)
    }
}

// ── OutlineTree ───────────────────────────────────────────────────────────

#[pyclass(name = "OutlineTree")]
pub struct PyOutlineTree {
    pub inner: OutlineTree,
}

#[pymethods]
impl PyOutlineTree {
    #[new]
    fn new() -> Self {
        Self {
            inner: OutlineTree::new(),
        }
    }

    fn add_item(&mut self, item: &PyOutlineItem) {
        self.inner.add_item(item.inner.clone());
    }

    fn __repr__(&self) -> String {
        format!("OutlineTree(items={})", self.inner.items.len())
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyOutlineItem>()?;
    m.add_class::<PyOutlineTree>()?;
    Ok(())
}
