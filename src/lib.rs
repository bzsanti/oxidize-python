use pyo3::prelude::*;

mod actions;
mod advanced_tables;
mod annotations;
mod charts;
mod document;
mod errors;
mod forms;
mod graphics;
mod image;
mod list;
mod operations;
mod outlines;
mod page;
mod page_labels;
mod parser;
mod security;
mod table;
mod text;
mod tier8;
mod types;
mod viewer_preferences;

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
    image::register(m)?;
    table::register(m)?;
    list::register(m)?;
    annotations::register(m)?;
    actions::register(m)?;
    forms::register(m)?;
    outlines::register(m)?;
    page_labels::register(m)?;
    tier8::register(m)?;
    viewer_preferences::register(m)?;
    charts::register(m)?;
    advanced_tables::register(m)?;

    Ok(())
}
