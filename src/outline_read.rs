//! Owned, read-only snapshots from the core's bounded outline reader.
use oxidize_pdf::parser::OutlineReadOptions;
use oxidize_pdf::structure::{
    Destination, DestinationType, OutlineItem, OutlineTree, PageDestination,
};
use pyo3::prelude::*;

/// Traversal budgets. Zero is valid; root outline depth is zero.
/// These are item/depth budgets, not a cap on total parser memory or PDF size.
#[pyclass(name = "OutlineReadOptions", frozen)]
pub struct PyOutlineReadOptions {
    pub(crate) inner: OutlineReadOptions,
}

#[pymethods]
impl PyOutlineReadOptions {
    #[new]
    #[pyo3(signature = (*, max_items=100000, max_depth=256, max_named_destinations=100000, max_name_tree_nodes=100000))]
    fn new(
        max_items: usize,
        max_depth: usize,
        max_named_destinations: usize,
        max_name_tree_nodes: usize,
    ) -> Self {
        Self {
            inner: OutlineReadOptions {
                max_items,
                max_depth,
                max_named_destinations,
                max_name_tree_nodes,
            },
        }
    }
    #[getter]
    fn max_items(&self) -> usize {
        self.inner.max_items
    }
    #[getter]
    fn max_depth(&self) -> usize {
        self.inner.max_depth
    }
    #[getter]
    fn max_named_destinations(&self) -> usize {
        self.inner.max_named_destinations
    }
    #[getter]
    fn max_name_tree_nodes(&self) -> usize {
        self.inner.max_name_tree_nodes
    }
}

/// Snapshot of an existing document's outline, independent of the reader.
#[pyclass(name = "ReadOutline", frozen)]
pub struct PyReadOutline {
    pub(crate) inner: OutlineTree,
}
#[pymethods]
impl PyReadOutline {
    #[getter]
    fn items(&self) -> Vec<PyReadOutlineItem> {
        self.inner
            .items
            .iter()
            .cloned()
            .map(|inner| PyReadOutlineItem { inner })
            .collect()
    }
}

/// Read-only item. Children are owned copies, not mutation handles into a PDF.
#[pyclass(name = "ReadOutlineItem", frozen)]
pub struct PyReadOutlineItem {
    inner: OutlineItem,
}
#[pymethods]
impl PyReadOutlineItem {
    #[getter]
    fn title(&self) -> &str {
        &self.inner.title
    }
    #[getter]
    fn destination(&self) -> Option<PyReadOutlineDestination> {
        self.inner
            .destination
            .clone()
            .map(|inner| PyReadOutlineDestination { inner })
    }
    #[getter]
    fn children(&self) -> Vec<PyReadOutlineItem> {
        self.inner
            .children
            .iter()
            .cloned()
            .map(|inner| Self { inner })
            .collect()
    }
    #[getter]
    fn color(&self) -> Option<(f64, f64, f64)> {
        self.inner
            .color
            .map(|color| (color.r(), color.g(), color.b()))
    }
    #[getter]
    fn is_bold(&self) -> bool {
        self.inner.flags.bold
    }
    #[getter]
    fn is_italic(&self) -> bool {
        self.inner.flags.italic
    }
    #[getter]
    fn is_open(&self) -> bool {
        self.inner.open
    }
}

/// Resolved internal page destination. Page indices are zero-based.
/// Parameters follow PDF order: XYZ(left,top,zoom), FitR(left,bottom,right,top),
/// FitH/FitBH(top), FitV/FitBV(left), Fit/FitB(). Null is preserved as None.
#[pyclass(name = "ReadOutlineDestination", frozen)]
pub struct PyReadOutlineDestination {
    inner: Destination,
}
#[pymethods]
impl PyReadOutlineDestination {
    #[getter]
    fn page_index(&self) -> PyResult<u32> {
        match self.inner.page {
            PageDestination::PageNumber(number) => Ok(number),
            PageDestination::PageRef(_) => Err(crate::errors::PdfParseError::new_err(
                "outline destination was not resolved to a page index",
            )),
        }
    }
    #[getter]
    fn kind(&self) -> &'static str {
        match self.inner.dest_type {
            DestinationType::XYZ { .. } => "XYZ",
            DestinationType::Fit => "Fit",
            DestinationType::FitH { .. } => "FitH",
            DestinationType::FitV { .. } => "FitV",
            DestinationType::FitR { .. } => "FitR",
            DestinationType::FitB => "FitB",
            DestinationType::FitBH { .. } => "FitBH",
            DestinationType::FitBV { .. } => "FitBV",
        }
    }
    #[getter]
    fn parameters(&self) -> Vec<Option<f64>> {
        match self.inner.dest_type {
            DestinationType::XYZ { left, top, zoom } => vec![left, top, zoom],
            DestinationType::Fit | DestinationType::FitB => vec![],
            DestinationType::FitH { top } | DestinationType::FitBH { top } => vec![top],
            DestinationType::FitV { left } | DestinationType::FitBV { left } => vec![left],
            DestinationType::FitR { rect } => vec![
                Some(rect.lower_left.x),
                Some(rect.lower_left.y),
                Some(rect.upper_right.x),
                Some(rect.upper_right.y),
            ],
        }
    }
}

pub(crate) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyOutlineReadOptions>()?;
    m.add_class::<PyReadOutline>()?;
    m.add_class::<PyReadOutlineItem>()?;
    m.add_class::<PyReadOutlineDestination>()?;
    Ok(())
}
