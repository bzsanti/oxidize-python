// oxidize-wasm/src/lib.rs
// Reference skeleton for the WASM bridge.
//
// Key differences from oxidize-python:
//   1. No file path APIs. All input/output is Uint8Array (bytes in JS).
//   2. Error handling returns JsValue (JS Error objects) not Python exceptions.
//   3. wasm-bindgen replaces pyo3. The macro syntax is similar but not identical.
//   4. No threading — wasm32-unknown-unknown is single-threaded.

use wasm_bindgen::prelude::*;

mod document;
mod operations;
mod page;
mod parser;
mod types;

// Re-export error conversion helper used across modules.
pub(crate) fn to_js_err(err: impl std::fmt::Display) -> JsValue {
    JsValue::from_str(&err.to_string())
}

// Expose the version constant to JS.
#[wasm_bindgen]
pub fn version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}

// Example: how Document is exposed in WASM vs Python
//
// Python (pyo3):
//   #[pyclass(name = "Document")]
//   pub struct PyDocument { pub inner: oxidize_pdf::Document }
//   #[pymethods] impl PyDocument { ... }
//
// WASM (wasm-bindgen):
//   #[wasm_bindgen]
//   pub struct Document { inner: oxidize_pdf::Document }
//   #[wasm_bindgen] impl Document { ... }
//
// The structural pattern is identical. The macros and error types differ.

// Example: how operations differ (bytes-in/bytes-out instead of file paths)
//
// Python bridge:
//   fn merge_pdfs(input_paths: Vec<String>, output_path: &str) -> PyResult<()>
//
// WASM bridge:
//   pub fn merge_pdfs(inputs: Vec<js_sys::Uint8Array>) -> Result<js_sys::Uint8Array, JsValue>
//
// The core's merge operation must accept &[u8] / impl Read, not &str paths.
// If the core only exposes file-path APIs, this is a blocker — see LIFECYCLE_STRATEGY.md.
