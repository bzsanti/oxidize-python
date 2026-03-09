use pyo3::prelude::*;

use crate::errors::to_py_err;
use crate::page::PyPage;
use crate::security::PyPermissions;

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
    #[pyo3(signature = (user_password, owner_password, permissions = None))]
    fn encrypt(
        &mut self,
        user_password: &str,
        owner_password: &str,
        permissions: Option<&PyPermissions>,
    ) {
        match permissions {
            Some(perms) => {
                let enc = oxidize_pdf::document::DocumentEncryption::new(
                    user_password,
                    owner_password,
                    perms.inner,
                    oxidize_pdf::document::EncryptionStrength::Rc4_128bit,
                );
                self.inner.set_encryption(enc);
            }
            None => {
                self.inner
                    .encrypt_with_passwords(user_password, owner_password);
            }
        }
    }

    /// Whether the document has encryption set.
    #[getter]
    fn is_encrypted(&self) -> bool {
        self.inner.is_encrypted()
    }

    fn __repr__(&self) -> String {
        format!("Document(pages={})", self.inner.page_count())
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDocument>()?;
    Ok(())
}
