use pyo3::prelude::*;

mod actions;
mod advanced_tables;
mod ai_pipeline;
mod annotations;
mod batch_recovery_streaming;
mod charts;
mod content_parser;
mod document;
mod errors;
mod forms;
mod graphics;
mod graphics_advanced;
mod graphics_extraction;
mod image;
mod list;
mod operations;
mod outlines;
mod page;
mod page_labels;
mod page_transitions;
mod parser;
mod security;
mod semantic;
mod table;
mod text;
mod text_extraction;
mod tier8;
mod types;
mod verification;
mod viewer_preferences;
mod xmp_metadata;

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
    graphics_advanced::register(m)?;
    page_transitions::register(m)?;
    ai_pipeline::register(m)?;
    text_extraction::register(m)?;
    batch_recovery_streaming::register(m)?;
    content_parser::register(m)?;
    xmp_metadata::register(m)?;
    verification::register(m)?;
    semantic::register(m)?;
    graphics_extraction::register(m)?;

    Ok(())
}
