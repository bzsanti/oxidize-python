use pyo3::prelude::*;

use oxidize_pdf::metadata::xmp::{XmpMetadata, XmpNamespace, XmpProperty, XmpValue};

// ── PyXmpNamespace ─────────────────────────────────────────────────────────

/// XMP namespace identifier.
///
/// Standard namespaces: ``DUBLIN_CORE``, ``XMP_BASIC``, ``XMP_RIGHTS``,
/// ``XMP_MEDIA_MANAGEMENT``, ``PDF``, ``PHOTOSHOP``.
/// Custom namespaces: ``XmpNamespace.custom("prefix", "uri")``.
#[pyclass(name = "XmpNamespace", frozen, from_py_object, eq, hash)]
#[derive(Clone, PartialEq, Eq, Hash)]
pub struct PyXmpNamespace {
    pub inner: XmpNamespace,
}

#[pymethods]
impl PyXmpNamespace {
    #[staticmethod]
    fn custom(prefix: &str, uri: &str) -> Self {
        Self {
            inner: XmpNamespace::Custom(prefix.to_string(), uri.to_string()),
        }
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn DUBLIN_CORE() -> Self {
        Self {
            inner: XmpNamespace::DublinCore,
        }
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn XMP_BASIC() -> Self {
        Self {
            inner: XmpNamespace::XmpBasic,
        }
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn XMP_RIGHTS() -> Self {
        Self {
            inner: XmpNamespace::XmpRights,
        }
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn XMP_MEDIA_MANAGEMENT() -> Self {
        Self {
            inner: XmpNamespace::XmpMediaManagement,
        }
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn PDF() -> Self {
        Self {
            inner: XmpNamespace::Pdf,
        }
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn PHOTOSHOP() -> Self {
        Self {
            inner: XmpNamespace::Photoshop,
        }
    }

    #[getter]
    fn prefix(&self) -> &str {
        self.inner.prefix()
    }

    #[getter]
    fn uri(&self) -> &str {
        self.inner.uri()
    }

    fn __repr__(&self) -> String {
        format!("XmpNamespace({:?})", self.inner.prefix())
    }
}

// ── PyXmpValue ─────────────────────────────────────────────────────────────

/// XMP property value.
///
/// Constructors: ``text()``, ``date()``, ``array()``, ``bag()``, ``alt()``,
/// ``struct_value()``, ``array_struct()``.
/// Use ``value_type`` to inspect the variant.
#[pyclass(name = "XmpValue", frozen, from_py_object, eq)]
#[derive(Clone, PartialEq)]
pub struct PyXmpValue {
    pub inner: XmpValue,
}

#[pymethods]
impl PyXmpValue {
    #[staticmethod]
    fn text(value: &str) -> Self {
        Self {
            inner: XmpValue::Text(value.to_string()),
        }
    }

    #[staticmethod]
    fn date(value: &str) -> Self {
        Self {
            inner: XmpValue::Date(value.to_string()),
        }
    }

    #[staticmethod]
    fn array(values: Vec<String>) -> Self {
        Self {
            inner: XmpValue::Array(values),
        }
    }

    #[staticmethod]
    fn bag(values: Vec<String>) -> Self {
        Self {
            inner: XmpValue::Bag(values),
        }
    }

    #[staticmethod]
    fn alt(values: Vec<(String, String)>) -> Self {
        Self {
            inner: XmpValue::Alt(values),
        }
    }

    /// Create a structured value (nested key-value pairs).
    #[staticmethod]
    fn struct_value(fields: std::collections::HashMap<String, PyXmpValue>) -> Self {
        let inner_fields = fields
            .into_iter()
            .map(|(k, v)| (k, Box::new(v.inner)))
            .collect();
        Self {
            inner: XmpValue::Struct(inner_fields),
        }
    }

    /// Create an array of structured values.
    #[staticmethod]
    fn array_struct(items: Vec<std::collections::HashMap<String, PyXmpValue>>) -> Self {
        let inner_items = items
            .into_iter()
            .map(|item| {
                item.into_iter()
                    .map(|(k, v)| (k, Box::new(v.inner)))
                    .collect()
            })
            .collect();
        Self {
            inner: XmpValue::ArrayStruct(inner_items),
        }
    }

    #[getter]
    fn value_type(&self) -> &str {
        match &self.inner {
            XmpValue::Text(_) => "Text",
            XmpValue::Date(_) => "Date",
            XmpValue::Array(_) => "Array",
            XmpValue::Bag(_) => "Bag",
            XmpValue::Alt(_) => "Alt",
            XmpValue::Struct(_) => "Struct",
            XmpValue::ArrayStruct(_) => "ArrayStruct",
        }
    }

    fn __repr__(&self) -> String {
        format!("XmpValue({})", self.value_type())
    }
}

// ── PyXmpProperty ──────────────────────────────────────────────────────────

/// A single XMP metadata property with namespace, name, and value.
#[pyclass(name = "XmpProperty", from_py_object)]
#[derive(Clone)]
pub struct PyXmpProperty {
    pub inner: XmpProperty,
}

#[pymethods]
impl PyXmpProperty {
    #[new]
    fn new(namespace: &PyXmpNamespace, name: &str, value: &PyXmpValue) -> Self {
        Self {
            inner: XmpProperty {
                namespace: namespace.inner.clone(),
                name: name.to_string(),
                value: value.inner.clone(),
            },
        }
    }

    #[getter]
    fn name(&self) -> &str {
        &self.inner.name
    }

    #[getter]
    fn namespace(&self) -> PyXmpNamespace {
        PyXmpNamespace {
            inner: self.inner.namespace.clone(),
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "XmpProperty(ns={:?}, name={:?})",
            self.inner.namespace.prefix(),
            self.inner.name
        )
    }
}

// ── PyXmpMetadata ──────────────────────────────────────────────────────────

/// XMP metadata container (ISO 16684-1).
///
/// Note: ``set_*`` methods append properties — calling ``set_text()`` twice
/// with the same name creates two entries. Use ``add_property()`` for the
/// same append semantics explicitly.
#[pyclass(name = "XmpMetadata", from_py_object)]
#[derive(Clone)]
pub struct PyXmpMetadata {
    pub inner: XmpMetadata,
}

#[pymethods]
impl PyXmpMetadata {
    #[new]
    fn new() -> Self {
        Self {
            inner: XmpMetadata::new(),
        }
    }

    fn set_text(&mut self, namespace: &PyXmpNamespace, name: &str, value: &str) {
        self.inner.set_text(namespace.inner.clone(), name, value);
    }

    fn set_date(&mut self, namespace: &PyXmpNamespace, name: &str, value: &str) {
        self.inner.set_date(namespace.inner.clone(), name, value);
    }

    fn set_array(&mut self, namespace: &PyXmpNamespace, name: &str, values: Vec<String>) {
        self.inner.set_array(namespace.inner.clone(), name, values);
    }

    fn set_bag(&mut self, namespace: &PyXmpNamespace, name: &str, values: Vec<String>) {
        self.inner.set_bag(namespace.inner.clone(), name, values);
    }

    fn set_alt(&mut self, namespace: &PyXmpNamespace, name: &str, values: Vec<(String, String)>) {
        self.inner.set_alt(namespace.inner.clone(), name, values);
    }

    fn add_property(&mut self, property: &PyXmpProperty) {
        self.inner.add_property(property.inner.clone());
    }

    fn register_namespace(&mut self, prefix: &str, uri: &str) {
        self.inner
            .register_namespace(prefix.to_string(), uri.to_string());
    }

    #[getter]
    fn property_count(&self) -> usize {
        self.inner.properties().len()
    }

    /// Reset all properties, creating a fresh empty metadata container.
    fn clear(&mut self) {
        self.inner = XmpMetadata::new();
    }

    fn to_xmp_packet(&self) -> String {
        self.inner.to_xmp_packet()
    }

    fn __repr__(&self) -> String {
        format!("XmpMetadata(properties={})", self.inner.properties().len())
    }
}

// ── Register ───────────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyXmpNamespace>()?;
    m.add_class::<PyXmpValue>()?;
    m.add_class::<PyXmpProperty>()?;
    m.add_class::<PyXmpMetadata>()?;
    Ok(())
}
