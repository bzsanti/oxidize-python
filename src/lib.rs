use pyo3::prelude::*;

mod document;
mod errors;
mod graphics;
mod operations;
mod page;
mod parser;
mod security;
mod text;
mod types;

/// oxidize-pdf Python bindings
#[pymodule]
fn _oxidize_pdf(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    // Register submodules
    errors::register(m)?;
    types::register(m)?;
    document::register(m)?;
    page::register(m)?;
    text::register(m)?;
    graphics::register(m)?;
    parser::register(m)?;
    operations::register(m)?;
    security::register(m)?;

    Ok(())
}
