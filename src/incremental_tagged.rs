//! Owned, atomic tagged-structure editing over the published core.
use crate::errors::to_py_err;
use crate::signing::PyPdfValue;
use crate::tagged_validation::{
    PyTaggedPdfObjectRef, PyTaggedPdfValidationOptions, PyTaggedPdfValidationReport,
};
use oxidize_pdf::parser::objects::PdfDictionary;
use oxidize_pdf::verification::tagged_pdf::TaggedPdfValidationOptions;
use oxidize_pdf::writer as core;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::collections::HashMap;

#[pyclass(name = "TaggedPdfMutation", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTaggedPdfMutation {
    inner: core::TaggedPdfMutation,
}
#[pymethods]
impl PyTaggedPdfMutation {
    #[staticmethod]
    #[pyo3(signature=(parent, structure_type, attributes=None, index=None))]
    fn create_element(
        parent: PyTaggedPdfObjectRef,
        structure_type: String,
        attributes: Option<HashMap<String, PyPdfValue>>,
        index: Option<usize>,
    ) -> Self {
        let mut dict = PdfDictionary::new();
        for (k, v) in attributes.unwrap_or_default() {
            dict.insert(k, v.inner);
        }
        Self {
            inner: core::TaggedPdfMutation::CreateElement {
                parent: parent.inner,
                structure_type,
                attributes: dict,
                index,
            },
        }
    }
    #[staticmethod]
    #[pyo3(signature=(element,key,value=None))]
    fn set_element_attribute(
        element: PyTaggedPdfObjectRef,
        key: String,
        value: Option<PyPdfValue>,
    ) -> Self {
        Self {
            inner: core::TaggedPdfMutation::SetElementAttribute {
                element: element.inner,
                key,
                value: value.map(|v| v.inner),
            },
        }
    }
    #[staticmethod]
    #[pyo3(signature=(element,new_parent,index=None))]
    fn reparent_element(
        element: PyTaggedPdfObjectRef,
        new_parent: PyTaggedPdfObjectRef,
        index: Option<usize>,
    ) -> Self {
        Self {
            inner: core::TaggedPdfMutation::ReparentElement {
                element: element.inner,
                new_parent: new_parent.inner,
                index,
            },
        }
    }
    #[staticmethod]
    fn associate_mcid(
        element: PyTaggedPdfObjectRef,
        page: PyTaggedPdfObjectRef,
        mcid: u32,
    ) -> Self {
        Self {
            inner: core::TaggedPdfMutation::AssociateMcid {
                element: element.inner,
                page: page.inner,
                mcid,
            },
        }
    }
    #[staticmethod]
    #[pyo3(signature=(key,value=None))]
    fn set_parent_tree_entry(key: i64, value: Option<PyPdfValue>) -> Self {
        Self {
            inner: core::TaggedPdfMutation::SetParentTreeEntry {
                key,
                value: value.map(|v| v.inner),
            },
        }
    }
    #[getter]
    fn parent(&self) -> Option<PyTaggedPdfObjectRef> {
        match &self.inner {
            core::TaggedPdfMutation::CreateElement { parent: value, .. } => {
                Some(PyTaggedPdfObjectRef { inner: *value })
            }
            _ => None,
        }
    }
    #[getter]
    fn element(&self) -> Option<PyTaggedPdfObjectRef> {
        match &self.inner {
            core::TaggedPdfMutation::SetElementAttribute { element: value, .. }
            | core::TaggedPdfMutation::ReparentElement { element: value, .. }
            | core::TaggedPdfMutation::AssociateMcid { element: value, .. } => {
                Some(PyTaggedPdfObjectRef { inner: *value })
            }
            _ => None,
        }
    }
    #[getter]
    fn new_parent(&self) -> Option<PyTaggedPdfObjectRef> {
        match &self.inner {
            core::TaggedPdfMutation::ReparentElement {
                new_parent: value, ..
            } => Some(PyTaggedPdfObjectRef { inner: *value }),
            _ => None,
        }
    }
    #[getter]
    fn page(&self) -> Option<PyTaggedPdfObjectRef> {
        match &self.inner {
            core::TaggedPdfMutation::AssociateMcid { page: value, .. } => {
                Some(PyTaggedPdfObjectRef { inner: *value })
            }
            _ => None,
        }
    }
    #[getter]
    fn structure_type(&self) -> Option<String> {
        match &self.inner {
            core::TaggedPdfMutation::CreateElement {
                structure_type: value,
                ..
            } => Some(value.clone()),
            _ => None,
        }
    }
    #[getter]
    fn index(&self) -> Option<usize> {
        match &self.inner {
            core::TaggedPdfMutation::CreateElement { index: value, .. }
            | core::TaggedPdfMutation::ReparentElement { index: value, .. } => *value,
            _ => None,
        }
    }
    #[getter]
    fn mcid(&self) -> Option<u32> {
        match &self.inner {
            core::TaggedPdfMutation::AssociateMcid { mcid: value, .. } => Some(*value),
            _ => None,
        }
    }
    #[getter]
    fn attribute_key(&self) -> Option<String> {
        match &self.inner {
            core::TaggedPdfMutation::SetElementAttribute { key: value, .. } => Some(value.clone()),
            _ => None,
        }
    }
    #[getter]
    fn parent_tree_key(&self) -> Option<i64> {
        match &self.inner {
            core::TaggedPdfMutation::SetParentTreeEntry { key: value, .. } => Some(*value),
            _ => None,
        }
    }
    #[getter]
    fn value(&self) -> Option<PyPdfValue> {
        match &self.inner {
            core::TaggedPdfMutation::SetElementAttribute { value, .. }
            | core::TaggedPdfMutation::SetParentTreeEntry { value, .. } => {
                value.clone().map(|inner| PyPdfValue { inner })
            }
            _ => None,
        }
    }
    #[getter]
    fn attributes(&self) -> Option<HashMap<String, PyPdfValue>> {
        match &self.inner {
            core::TaggedPdfMutation::CreateElement {
                attributes: value, ..
            } => Some(crate::signing::dictionary_values(value)),
            _ => None,
        }
    }
    #[getter]
    fn kind(&self) -> &'static str {
        match self.inner {
            core::TaggedPdfMutation::CreateElement { .. } => "create_element",
            core::TaggedPdfMutation::SetElementAttribute { .. } => "set_element_attribute",
            core::TaggedPdfMutation::ReparentElement { .. } => "reparent_element",
            core::TaggedPdfMutation::AssociateMcid { .. } => "associate_mcid",
            core::TaggedPdfMutation::SetParentTreeEntry { .. } => "set_parent_tree_entry",
        }
    }
}
#[pyclass(
    name = "TaggedPdfChangedObjectKind",
    frozen,
    eq,
    eq_int,
    from_py_object
)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyTaggedPdfChangedObjectKind {
    StructureElement,
    StructureTreeRoot,
    ParentTree,
    CrossReference,
}
#[pyclass(name = "TaggedPdfChangedObject", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTaggedPdfChangedObject {
    inner: core::TaggedPdfChangedObject,
}
#[pymethods]
impl PyTaggedPdfChangedObject {
    #[getter]
    fn object(&self) -> PyTaggedPdfObjectRef {
        PyTaggedPdfObjectRef {
            inner: self.inner.object,
        }
    }
    #[getter]
    fn kind(&self) -> PyTaggedPdfChangedObjectKind {
        match self.inner.kind {
            core::TaggedPdfChangedObjectKind::StructureElement => {
                PyTaggedPdfChangedObjectKind::StructureElement
            }
            core::TaggedPdfChangedObjectKind::StructureTreeRoot => {
                PyTaggedPdfChangedObjectKind::StructureTreeRoot
            }
            core::TaggedPdfChangedObjectKind::ParentTree => {
                PyTaggedPdfChangedObjectKind::ParentTree
            }
            core::TaggedPdfChangedObjectKind::CrossReference => {
                PyTaggedPdfChangedObjectKind::CrossReference
            }
        }
    }
}
#[pyclass(name = "TaggedPdfEditPlan", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTaggedPdfEditPlan {
    inner: core::TaggedPdfEditPlan,
}
#[pymethods]
impl PyTaggedPdfEditPlan {
    #[getter]
    fn changed_objects(&self) -> Vec<PyTaggedPdfChangedObject> {
        self.inner
            .changed_objects
            .iter()
            .map(|v| PyTaggedPdfChangedObject { inner: *v })
            .collect()
    }
    #[getter]
    fn mutations(&self) -> Vec<PyTaggedPdfMutation> {
        self.inner
            .mutations
            .iter()
            .map(|v| PyTaggedPdfMutation { inner: v.clone() })
            .collect()
    }
}
#[pyclass(name = "TaggedPdfMutationReport", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyTaggedPdfMutationReport {
    inner: core::TaggedPdfMutationReport,
}
#[pymethods]
impl PyTaggedPdfMutationReport {
    #[getter]
    fn pdf_bytes<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.inner.pdf_bytes)
    }
    #[getter]
    fn plan(&self) -> PyTaggedPdfEditPlan {
        PyTaggedPdfEditPlan {
            inner: self.inner.plan.clone(),
        }
    }
    #[getter]
    fn validation_before(&self) -> PyTaggedPdfValidationReport {
        PyTaggedPdfValidationReport {
            inner: self.inner.validation_before.clone(),
        }
    }
    #[getter]
    fn validation_after(&self) -> PyTaggedPdfValidationReport {
        PyTaggedPdfValidationReport {
            inner: self.inner.validation_after.clone(),
        }
    }
}
#[derive(Clone)]
enum Preparation {
    Recover,
    Language(String),
}
/// Immutable source and ordered preparation recipe; each call independently
/// rebuilds the core baseline. Failed operations cannot change this snapshot.
#[pyclass(name = "IncrementalTaggedPdfEditor", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyIncrementalTaggedPdfEditor {
    base: Vec<u8>,
    options: TaggedPdfValidationOptions,
    preparation: Vec<Preparation>,
}
impl PyIncrementalTaggedPdfEditor {
    fn editor(&self) -> oxidize_pdf::Result<core::IncrementalTaggedPdfEditor<'_>> {
        let mut editor = core::IncrementalTaggedPdfEditor::new(&self.base)
            .with_validation_options(self.options.clone());
        for step in &self.preparation {
            editor = match step {
                Preparation::Recover => editor.with_recovered_indexes()?,
                Preparation::Language(s) => editor.with_document_language(s)?,
            };
        }
        Ok(editor)
    }
}
#[pymethods]
impl PyIncrementalTaggedPdfEditor {
    #[new]
    fn new(pdf: &[u8]) -> Self {
        Self {
            base: pdf.to_vec(),
            options: TaggedPdfValidationOptions::default(),
            preparation: Vec::new(),
        }
    }
    fn with_validation_options(&self, options: PyTaggedPdfValidationOptions) -> Self {
        Self {
            options: options.inner,
            ..self.clone()
        }
    }
    fn with_recovered_indexes(&self, py: Python<'_>) -> PyResult<Self> {
        let mut next = self.clone();
        next.preparation.push(Preparation::Recover);
        py.detach(|| next.editor().map(|_| ())).map_err(to_py_err)?;
        Ok(next)
    }
    fn with_document_language(&self, py: Python<'_>, language: String) -> PyResult<Self> {
        let mut next = self.clone();
        next.preparation.push(Preparation::Language(language));
        py.detach(|| next.editor().map(|_| ())).map_err(to_py_err)?;
        Ok(next)
    }
    fn preparation_objects(&self, py: Python<'_>) -> PyResult<Vec<PyTaggedPdfObjectRef>> {
        py.detach(|| {
            self.editor().map(|editor| {
                editor
                    .preparation_objects()
                    .iter()
                    .map(|v| PyTaggedPdfObjectRef { inner: *v })
                    .collect()
            })
        })
        .map_err(to_py_err)
    }
    fn preflight(&self, py: Python<'_>) -> PyResult<PyTaggedPdfValidationReport> {
        let inner = py
            .detach(|| self.editor()?.preflight())
            .map_err(to_py_err)?;
        Ok(PyTaggedPdfValidationReport { inner })
    }
    fn plan(
        &self,
        py: Python<'_>,
        mutations: Vec<PyTaggedPdfMutation>,
    ) -> PyResult<PyTaggedPdfEditPlan> {
        let mutations: Vec<_> = mutations.into_iter().map(|m| m.inner).collect();
        let inner = py
            .detach(|| self.editor()?.plan(&mutations))
            .map_err(to_py_err)?;
        Ok(PyTaggedPdfEditPlan { inner })
    }
    fn apply(
        &self,
        py: Python<'_>,
        mutations: Vec<PyTaggedPdfMutation>,
    ) -> PyResult<PyTaggedPdfMutationReport> {
        let mutations: Vec<_> = mutations.into_iter().map(|m| m.inner).collect();
        let inner = py
            .detach(|| self.editor()?.apply(&mutations))
            .map_err(to_py_err)?;
        Ok(PyTaggedPdfMutationReport { inner })
    }
}
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTaggedPdfMutation>()?;
    m.add_class::<PyTaggedPdfChangedObjectKind>()?;
    m.add_class::<PyTaggedPdfChangedObject>()?;
    m.add_class::<PyTaggedPdfEditPlan>()?;
    m.add_class::<PyTaggedPdfMutationReport>()?;
    m.add_class::<PyIncrementalTaggedPdfEditor>()?;
    Ok(())
}
