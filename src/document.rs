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
use crate::text::{PyFont, PyFontEncoding};
use crate::types::PyRectangle;
use crate::viewer_preferences::PyViewerPreferences;
use crate::xmp_metadata::PyXmpMetadata;

#[pyclass(name = "Document")]
pub struct PyDocument {
    pub inner: oxidize_pdf::Document,
    /// Pages added via :meth:`add_page`, held as live handles to the Python
    /// ``Page`` objects rather than eager clones. This is what lets draws
    /// issued *after* ``add_page`` reach the saved page (issue #80): the
    /// page's current content is materialised into ``inner`` only at save
    /// time. ``Document::add_page`` consumes a ``Page`` by value, so each
    /// handle is materialised exactly once — tracked by ``flushed_pages`` —
    /// to support saving the same document more than once.
    pending_pages: Vec<Py<PyPage>>,
    /// Count of ``pending_pages`` already materialised into ``inner``.
    flushed_pages: usize,
}

#[pymethods]
impl PyDocument {
    #[new]
    fn new() -> Self {
        Self {
            inner: oxidize_pdf::Document::new(),
            pending_pages: Vec::new(),
            flushed_pages: 0,
        }
    }

    /// Number of pages in the document.
    ///
    /// Read-only property. Access as ``doc.page_count`` (an integer), not
    /// ``doc.page_count()`` — calling a property raises ``TypeError``.
    #[getter]
    fn page_count(&self) -> usize {
        // Pages already flushed live in `inner`; pending-but-unflushed pages
        // are counted directly so the property is accurate before save.
        self.inner.page_count() + (self.pending_pages.len() - self.flushed_pages)
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

    /// Add a page to the document.
    ///
    /// The page is held by reference, not snapshotted: any draw issued on the
    /// ``Page`` object after ``add_page`` still appears in the saved document
    /// (issue #80). The page's content is materialised at save time.
    fn add_page(&mut self, page: Py<PyPage>) {
        self.pending_pages.push(page);
    }

    /// Create a new A4 page already bound to this Document's font
    /// metrics store. Recommended over :meth:`Page.a4` for code that
    /// uses custom fonts: the returned page measures ``Font.custom(...)``
    /// against this Document's per-instance metrics, avoiding the
    /// deprecated process-wide registry. Mirrors upstream
    /// ``Document::new_page_a4``.
    fn new_page_a4(&self) -> PyPage {
        PyPage {
            inner: self.inner.new_page_a4(),
        }
    }

    /// Create a new US Letter page bound to this Document's font
    /// metrics store. Mirrors upstream ``Document::new_page_letter``.
    fn new_page_letter(&self) -> PyPage {
        PyPage {
            inner: self.inner.new_page_letter(),
        }
    }

    /// Create a new page of arbitrary dimensions bound to this
    /// Document's font metrics store. Mirrors upstream
    /// ``Document::new_page``.
    fn new_page(&self, width: f64, height: f64) -> PyPage {
        PyPage {
            inner: self.inner.new_page(width, height),
        }
    }

    /// Save the document to a file.
    fn save(&mut self, py: Python<'_>, path: &str) -> PyResult<()> {
        self.flush_pending_pages(py);
        self.inner.save(path).map_err(to_py_err)
    }

    /// Save the document to bytes and return them.
    fn save_to_bytes(&mut self, py: Python<'_>) -> PyResult<Vec<u8>> {
        self.flush_pending_pages(py);
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

    /// Add a text field to the document.
    fn add_text_field(
        &mut self,
        field: &PyTextField,
        rect: &PyRectangle,
    ) -> PyResult<()> {
        let widget = Widget::new(rect.inner);
        self.inner
            .enable_forms()
            .add_text_field(field.inner.clone(), widget, None)
            .map_err(to_py_err)?;
        Ok(())
    }

    /// Add a checkbox to the document.
    fn add_checkbox(
        &mut self,
        field: &PyCheckBox,
        rect: &PyRectangle,
    ) -> PyResult<()> {
        let widget = Widget::new(rect.inner);
        self.inner
            .enable_forms()
            .add_checkbox(field.inner.clone(), widget, None)
            .map_err(to_py_err)?;
        Ok(())
    }

    /// Add a combo box to the document.
    fn add_combo_box(
        &mut self,
        field: &PyComboBox,
        rect: &PyRectangle,
    ) -> PyResult<()> {
        let widget = Widget::new(rect.inner);
        self.inner
            .enable_forms()
            .add_combo_box(field.inner.clone(), widget, None)
            .map_err(to_py_err)?;
        Ok(())
    }

    /// Add a list box to the document.
    fn add_list_box(
        &mut self,
        field: &PyListBox,
        rect: &PyRectangle,
    ) -> PyResult<()> {
        let widget = Widget::new(rect.inner);
        self.inner
            .enable_forms()
            .add_list_box(field.inner.clone(), widget, None)
            .map_err(to_py_err)?;
        Ok(())
    }

    /// Add a radio button group to the document.
    fn add_radio_button(
        &mut self,
        field: &PyRadioButton,
        rect: &PyRectangle,
    ) -> PyResult<()> {
        let widget = Widget::new(rect.inner);
        self.inner
            .enable_forms()
            .add_radio_button(field.inner.clone(), Some(vec![widget]), None)
            .map_err(to_py_err)?;
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

    #[pyo3(signature = (action, is_map = false))]
    fn set_open_action_uri(&mut self, action: &PyUriAction, is_map: bool) {
        use oxidize_pdf::actions::Action;
        self.inner.set_open_action(Action::URI {
            uri: action.inner.uri.clone(),
            is_map,
        });
    }

    // ── Font Management (F46) ────────────────────────────────────────────

    /// Embed a custom TrueType/OpenType font from a file path.
    ///
    /// Reads the file and delegates to the byte-loading path so the font's
    /// embedded glyph widths are registered in this Document's font metrics
    /// store. This makes :meth:`measure_text` / :meth:`measure_char` return
    /// the real per-glyph widths for ``Font.custom(name)`` instead of a
    /// fallback (issue #78). Upstream's path-only ``add_font`` does not
    /// register metrics; routing through bytes closes that gap.
    fn add_font(&mut self, name: &str, path: &str) -> PyResult<()> {
        let data = std::fs::read(path).map_err(|e| to_py_err(e.into()))?;
        self.inner
            .add_font_from_bytes(name, data)
            .map_err(to_py_err)
    }

    fn add_font_from_bytes(&mut self, name: &str, data: &[u8]) -> PyResult<()> {
        self.inner
            .add_font_from_bytes(name, data.to_vec())
            .map_err(to_py_err)
    }

    /// Measure the rendered width of ``text`` in ``font`` at ``size`` points,
    /// scoped to this Document's embedded fonts.
    ///
    /// Unlike the module-level :func:`oxidize_pdf.measure_text`, this resolves
    /// ``Font.custom(name)`` against the fonts embedded on *this* Document via
    /// :meth:`add_font` / :meth:`add_font_from_bytes`, returning the embedded
    /// glyph widths rather than a fallback (issue #78). Built-in fonts measure
    /// identically to the free function.
    fn measure_text(&self, text: &str, font: &PyFont, size: f64) -> f64 {
        oxidize_pdf::text::metrics::measure_text_with(
            text,
            &font.inner,
            size,
            Some(self.inner.font_metrics()),
        )
    }

    /// Measure the rendered width of a single character in ``font`` at
    /// ``size`` points, scoped to this Document's embedded fonts.
    ///
    /// Document-bound counterpart of :func:`oxidize_pdf.measure_char`; see
    /// :meth:`measure_text` for why the scope matters (issue #78).
    fn measure_char(&self, ch: &str, font: &PyFont, size: f64) -> PyResult<f64> {
        let mut chars = ch.chars();
        let c = chars.next().ok_or_else(|| {
            pyo3::exceptions::PyValueError::new_err(
                "Expected a single character, got empty string",
            )
        })?;
        if chars.next().is_some() {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Expected a single character, got string of length {}",
                ch.len()
            )));
        }
        Ok(oxidize_pdf::text::metrics::measure_char_with(
            c,
            font.inner.clone(),
            size,
            Some(self.inner.font_metrics()),
        ))
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

    fn save_with_config(
        &mut self,
        py: Python<'_>,
        path: &str,
        config: &PyWriterConfig,
    ) -> PyResult<()> {
        self.flush_pending_pages(py);
        self.inner
            .save_with_config(path, config.inner.clone())
            .map_err(to_py_err)
    }

    /// Save the document to bytes using the supplied WriterConfig.
    ///
    /// In-memory counterpart of :py:meth:`save_with_config` — honors the
    /// config's ``pdf_version``, xref/object stream toggles, compression
    /// flag, and incremental-update mode.
    fn save_to_bytes_with_config(
        &mut self,
        py: Python<'_>,
        config: &PyWriterConfig,
    ) -> PyResult<Vec<u8>> {
        self.flush_pending_pages(py);
        self.inner
            .to_bytes_with_config(config.inner.clone())
            .map_err(to_py_err)
    }

    // ── Font Encoding (F48) ──────────────────────────────────────────────

    fn set_default_font_encoding(&mut self, encoding: &PyFontEncoding) {
        self.inner
            .set_default_font_encoding(Some(encoding.inner));
    }

    // ── XMP Metadata (F78) ───────────────────────────────────────────────

    /// Create an XmpMetadata object populated with this document's metadata.
    fn create_xmp_metadata(&self) -> PyXmpMetadata {
        PyXmpMetadata {
            inner: self.inner.create_xmp_metadata(),
        }
    }

    /// Return the XMP packet XML string for this document's metadata.
    fn get_xmp_packet(&self) -> String {
        self.inner.get_xmp_packet()
    }

    fn __repr__(&self) -> String {
        format!("Document(pages={})", self.page_count())
    }
}

impl PyDocument {
    /// Materialise any pages added via :meth:`add_page` that have not yet been
    /// pushed into the underlying document, capturing each page's *current*
    /// content (issue #80). Idempotent across repeated saves: each page handle
    /// is materialised exactly once, tracked by ``flushed_pages``.
    fn flush_pending_pages(&mut self, py: Python<'_>) {
        for i in self.flushed_pages..self.pending_pages.len() {
            let page_inner = self.pending_pages[i].borrow(py).inner.clone();
            self.inner.add_page(page_inner);
        }
        self.flushed_pages = self.pending_pages.len();
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
    #[pyo3(signature = (
        compress_streams=None,
        use_xref_streams=None,
        use_object_streams=None,
        pdf_version=None,
        incremental_update=None,
    ))]
    fn new(
        compress_streams: Option<bool>,
        use_xref_streams: Option<bool>,
        use_object_streams: Option<bool>,
        pdf_version: Option<String>,
        incremental_update: Option<bool>,
    ) -> Self {
        let mut cfg = WriterConfig::default();
        if let Some(v) = compress_streams {
            cfg.compress_streams = v;
        }
        if let Some(v) = use_xref_streams {
            cfg.use_xref_streams = v;
        }
        if let Some(v) = use_object_streams {
            cfg.use_object_streams = v;
        }
        if let Some(v) = pdf_version {
            cfg.pdf_version = v;
        }
        if let Some(v) = incremental_update {
            cfg.incremental_update = v;
        }
        Self { inner: cfg }
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

    #[getter]
    fn pdf_version(&self) -> String {
        self.inner.pdf_version.clone()
    }

    #[getter]
    fn incremental_update(&self) -> bool {
        self.inner.incremental_update
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
            "WriterConfig(pdf_version={:?}, compress={}, xref_streams={}, object_streams={}, incremental_update={})",
            self.inner.pdf_version,
            self.inner.compress_streams,
            self.inner.use_xref_streams,
            self.inner.use_object_streams,
            self.inner.incremental_update,
        )
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDocument>()?;
    m.add_class::<PyWriterConfig>()?;
    Ok(())
}
