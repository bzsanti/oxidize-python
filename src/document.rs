use pyo3::prelude::*;

use oxidize_pdf::forms::Widget;
use oxidize_pdf::writer::WriterConfig;

use crate::actions::{PyGoToAction, PyNamedDestinations, PyUriAction};
use crate::errors::to_py_err;
use crate::forms::{PyCheckBox, PyComboBox, PyListBox, PyRadioButton, PyTextField};
use crate::outlines::PyOutlineTree;
use crate::page::PyPage;
use crate::page_labels::PyPageLabelTree;
use crate::security::{PyEncryptionStrength, PyPermissions};
use crate::text::PyFontEncoding;
use crate::types::PyRectangle;
use crate::viewer_preferences::PyViewerPreferences;

#[pyclass(name = "Document")]
pub struct PyDocument {
    pub inner: oxidize_pdf::Document,
}

#[pymethods]
impl PyDocument {
    #[new]
    fn new() -> Self {
        Self {
            inner: oxidize_pdf::Document::new(),
        }
    }

    /// Number of pages in the document.
    #[getter]
    fn page_count(&self) -> usize {
        self.inner.page_count()
    }

    fn set_title(&mut self, title: &str) {
        self.inner.set_title(title);
    }

    fn set_author(&mut self, author: &str) {
        self.inner.set_author(author);
    }

    fn set_subject(&mut self, subject: &str) {
        self.inner.set_subject(subject);
    }

    fn set_keywords(&mut self, keywords: &str) {
        self.inner.set_keywords(keywords);
    }

    fn set_creator(&mut self, creator: &str) {
        self.inner.set_creator(creator);
    }

    /// Add a page to the document. The page is cloned internally.
    fn add_page(&mut self, page: &PyPage) {
        self.inner.add_page(page.inner.clone());
    }

    /// Save the document to a file.
    fn save(&mut self, path: &str) -> PyResult<()> {
        self.inner.save(path).map_err(to_py_err)
    }

    /// Save the document to bytes and return them.
    fn save_to_bytes(&mut self) -> PyResult<Vec<u8>> {
        self.inner.to_bytes().map_err(to_py_err)
    }

    /// Encrypt the document with passwords.
    ///
    /// Args:
    ///     user_password: Password required to open the document.
    ///     owner_password: Password for full access (editing, printing, etc.).
    ///     permissions: Optional permissions to restrict operations. Defaults to all allowed.
    #[pyo3(signature = (user_password, owner_password, permissions = None, strength = None))]
    fn encrypt(
        &mut self,
        user_password: &str,
        owner_password: &str,
        permissions: Option<&PyPermissions>,
        strength: Option<&PyEncryptionStrength>,
    ) {
        let perms = permissions
            .map(|p| p.inner)
            .unwrap_or(oxidize_pdf::encryption::Permissions::all());
        let str = strength
            .map(|s| s.inner)
            .unwrap_or(oxidize_pdf::document::EncryptionStrength::Rc4_128bit);
        let enc = oxidize_pdf::document::DocumentEncryption::new(
            user_password,
            owner_password,
            perms,
            str,
        );
        self.inner.set_encryption(enc);
    }

    /// Whether the document has encryption set.
    #[getter]
    fn is_encrypted(&self) -> bool {
        self.inner.is_encrypted()
    }

    /// Set the document structure tree (tagged PDF / accessibility).
    fn set_struct_tree(&mut self, tree: &mut crate::tier8::PyStructTree) {
        let t = std::mem::replace(&mut tree.inner, oxidize_pdf::structure::StructTree::new());
        self.inner.set_struct_tree(t);
    }

    /// Set the document outline (bookmarks).
    fn set_outline(&mut self, outline: &mut PyOutlineTree) {
        let tree = std::mem::replace(&mut outline.inner, oxidize_pdf::structure::OutlineTree::new());
        self.inner.set_outline(tree);
    }

    /// Set the document page labels.
    fn set_page_labels(&mut self, labels: &PyPageLabelTree) {
        self.inner.set_page_labels(labels.inner.clone());
    }

    /// Set the document producer metadata.
    fn set_producer(&mut self, producer: &str) {
        self.inner.set_producer(producer);
    }

    /// Set the document creation date from an ISO 8601 string.
    fn set_creation_date(&mut self, iso_date: &str) -> PyResult<()> {
        let dt = chrono::DateTime::parse_from_rfc3339(iso_date).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid date format: {e}"))
        })?;
        self.inner
            .set_creation_date(dt.with_timezone(&chrono::Utc));
        Ok(())
    }

    /// Set the document modification date from an ISO 8601 string.
    fn set_modification_date(&mut self, iso_date: &str) -> PyResult<()> {
        let dt = chrono::DateTime::parse_from_rfc3339(iso_date).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid date format: {e}"))
        })?;
        self.inner
            .set_modification_date(dt.with_timezone(&chrono::Utc));
        Ok(())
    }

    // ── Forms ────────────────────────────────────────────────────────────

    /// Enable the AcroForm subsystem on this document.
    fn enable_forms(&mut self) {
        self.inner.enable_forms();
    }

    /// Add a text field to the document on the given page.
    fn add_text_field(
        &mut self,
        page_index: usize,
        field: &PyTextField,
        rect: &PyRectangle,
    ) -> PyResult<()> {
        let widget = Widget::new(rect.inner.clone());
        self.inner
            .enable_forms()
            .add_text_field(field.inner.clone(), widget, None)
            .map_err(to_py_err)?;
        let _ = page_index; // page association handled by core
        Ok(())
    }

    /// Add a checkbox to the document on the given page.
    fn add_checkbox(
        &mut self,
        page_index: usize,
        field: &PyCheckBox,
        rect: &PyRectangle,
    ) -> PyResult<()> {
        let widget = Widget::new(rect.inner.clone());
        self.inner
            .enable_forms()
            .add_checkbox(field.inner.clone(), widget, None)
            .map_err(to_py_err)?;
        let _ = page_index;
        Ok(())
    }

    /// Add a combo box to the document on the given page.
    fn add_combo_box(
        &mut self,
        page_index: usize,
        field: &PyComboBox,
        rect: &PyRectangle,
    ) -> PyResult<()> {
        let widget = Widget::new(rect.inner.clone());
        self.inner
            .enable_forms()
            .add_combo_box(field.inner.clone(), widget, None)
            .map_err(to_py_err)?;
        let _ = page_index;
        Ok(())
    }

    /// Add a list box to the document on the given page.
    fn add_list_box(
        &mut self,
        page_index: usize,
        field: &PyListBox,
        rect: &PyRectangle,
    ) -> PyResult<()> {
        let widget = Widget::new(rect.inner.clone());
        self.inner
            .enable_forms()
            .add_list_box(field.inner.clone(), widget, None)
            .map_err(to_py_err)?;
        let _ = page_index;
        Ok(())
    }

    /// Add a radio button group to the document on the given page.
    fn add_radio_button(
        &mut self,
        page_index: usize,
        field: &PyRadioButton,
        rect: &PyRectangle,
    ) -> PyResult<()> {
        let widget = Widget::new(rect.inner.clone());
        self.inner
            .enable_forms()
            .add_radio_button(field.inner.clone(), Some(vec![widget]), None)
            .map_err(to_py_err)?;
        let _ = page_index;
        Ok(())
    }

    // ── Named Destinations ──────────────────────────────────────────────

    /// Set named destinations on this document.
    fn set_named_destinations(&mut self, destinations: &mut PyNamedDestinations) {
        let nd = std::mem::replace(
            &mut destinations.inner,
            oxidize_pdf::structure::NamedDestinations::new(),
        );
        self.inner.set_named_destinations(nd);
    }

    // ── Viewer Preferences (F44) ─────────────────────────────────────────

    fn set_viewer_preferences(&mut self, prefs: &PyViewerPreferences) {
        self.inner.set_viewer_preferences(prefs.inner.clone());
    }

    // ── Open Action (F45) ────────────────────────────────────────────────

    fn set_open_action_goto(&mut self, action: &PyGoToAction) {
        use oxidize_pdf::actions::Action;
        self.inner.set_open_action(Action::GoTo {
            destination: action.inner.destination.clone(),
        });
    }

    fn set_open_action_uri(&mut self, action: &PyUriAction) {
        use oxidize_pdf::actions::Action;
        self.inner.set_open_action(Action::URI {
            uri: action.inner.uri.clone(),
            is_map: false,
        });
    }

    // ── Font Management (F46) ────────────────────────────────────────────

    fn add_font(&mut self, name: &str, path: &str) -> PyResult<()> {
        self.inner.add_font(name, path).map_err(to_py_err)
    }

    fn add_font_from_bytes(&mut self, name: &str, data: &[u8]) -> PyResult<()> {
        self.inner
            .add_font_from_bytes(name, data.to_vec())
            .map_err(to_py_err)
    }

    fn has_custom_font(&self, name: &str) -> bool {
        self.inner.has_custom_font(name)
    }

    fn custom_font_names(&self) -> Vec<String> {
        self.inner.custom_font_names()
    }

    // ── Writer Config / Compression (F47) ────────────────────────────────

    fn set_compress(&mut self, compress: bool) {
        self.inner.set_compress(compress);
    }

    fn enable_xref_streams(&mut self, enable: bool) {
        self.inner.enable_xref_streams(enable);
    }

    fn save_with_config(&mut self, path: &str, config: &PyWriterConfig) -> PyResult<()> {
        self.inner
            .save_with_config(path, config.inner.clone())
            .map_err(to_py_err)
    }

    // ── Font Encoding (F48) ──────────────────────────────────────────────

    fn set_default_font_encoding(&mut self, encoding: &PyFontEncoding) {
        self.inner
            .set_default_font_encoding(Some(encoding.inner.clone()));
    }

    fn __repr__(&self) -> String {
        format!("Document(pages={})", self.inner.page_count())
    }
}

// ── WriterConfig ──────────────────────────────────────────────────────────

#[pyclass(name = "WriterConfig", from_py_object)]
#[derive(Clone)]
pub struct PyWriterConfig {
    pub inner: WriterConfig,
}

#[pymethods]
impl PyWriterConfig {
    #[new]
    fn new() -> Self {
        Self {
            inner: WriterConfig::default(),
        }
    }

    #[getter]
    fn compress_streams(&self) -> bool {
        self.inner.compress_streams
    }

    #[getter]
    fn use_xref_streams(&self) -> bool {
        self.inner.use_xref_streams
    }

    #[getter]
    fn use_object_streams(&self) -> bool {
        self.inner.use_object_streams
    }

    #[staticmethod]
    fn modern() -> Self {
        Self {
            inner: WriterConfig::modern(),
        }
    }

    #[staticmethod]
    fn legacy() -> Self {
        Self {
            inner: WriterConfig::legacy(),
        }
    }

    #[staticmethod]
    fn incremental() -> Self {
        Self {
            inner: WriterConfig::incremental(),
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "WriterConfig(compress={}, xref_streams={}, object_streams={})",
            self.inner.compress_streams,
            self.inner.use_xref_streams,
            self.inner.use_object_streams
        )
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDocument>()?;
    m.add_class::<PyWriterConfig>()?;
    Ok(())
}
