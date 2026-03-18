use pyo3::prelude::*;

use crate::errors::to_py_err;
use crate::outlines::PyOutlineTree;
use crate::page::PyPage;
use crate::page_labels::PyPageLabelTree;
use crate::security::{PyEncryptionStrength, PyPermissions};

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

    fn __repr__(&self) -> String {
        format!("Document(pages={})", self.inner.page_count())
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDocument>()?;
    Ok(())
}
