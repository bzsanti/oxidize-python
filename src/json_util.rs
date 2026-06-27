//! `serde_json::Value` ⇄ Python conversion helpers.
//!
//! Lives outside `experimental_spi` so it stays available when the
//! `unstable-spi` feature is disabled: the always-on `RagChunk.extra` getter
//! (`ai_pipeline`) needs `extra_map_to_py_dict`, while the gated SPI surface
//! also uses the full pair.

use std::collections::BTreeMap;

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

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
///
/// Only the gated SPI surface ingests Python-authored `extra` bags, so this
/// (and `py_dict_to_extra_map`) compile only with `unstable-spi`.
#[cfg(feature = "unstable-spi")]
pub(crate) fn py_to_json_value(value: &Bound<'_, PyAny>) -> PyResult<serde_json::Value> {
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
#[cfg(feature = "unstable-spi")]
pub(crate) fn py_dict_to_extra_map(
    dict: &Bound<'_, PyDict>,
) -> PyResult<BTreeMap<String, serde_json::Value>> {
    let mut out = BTreeMap::new();
    for (k, v) in dict.iter() {
        let key: String = k.extract()?;
        out.insert(key, py_to_json_value(&v)?);
    }
    Ok(out)
}
