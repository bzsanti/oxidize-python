use pyo3::prelude::*;

/// PDF document permissions.
///
/// Controls what operations are allowed on an encrypted PDF.
///
/// Example::
///
///     perms = Permissions(print=True, copy=False)
///     doc.encrypt("user", "owner", permissions=perms)
#[pyclass(name = "Permissions", from_py_object)]
#[derive(Clone)]
pub struct PyPermissions {
    pub inner: oxidize_pdf::encryption::Permissions,
}

#[pymethods]
impl PyPermissions {
    #[new]
    #[pyo3(signature = (
        print = false,
        copy = false,
        modify_contents = false,
        modify_annotations = false,
        fill_forms = false,
        accessibility = true,
        assemble = false,
        print_high_quality = false,
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        print: bool,
        copy: bool,
        modify_contents: bool,
        modify_annotations: bool,
        fill_forms: bool,
        accessibility: bool,
        assemble: bool,
        print_high_quality: bool,
    ) -> Self {
        let mut perms = oxidize_pdf::encryption::Permissions::new();
        perms.set_print(print);
        perms.set_copy(copy);
        perms.set_modify_contents(modify_contents);
        perms.set_modify_annotations(modify_annotations);
        perms.set_fill_forms(fill_forms);
        perms.set_accessibility(accessibility);
        perms.set_assemble(assemble);
        perms.set_print_high_quality(print_high_quality);
        Self { inner: perms }
    }

    /// Create permissions with everything allowed.
    #[staticmethod]
    fn all() -> Self {
        Self {
            inner: oxidize_pdf::encryption::Permissions::all(),
        }
    }

    /// Create permissions with everything denied (except accessibility).
    #[staticmethod]
    fn none() -> Self {
        Self {
            inner: oxidize_pdf::encryption::Permissions::new(),
        }
    }

    #[getter]
    fn can_print(&self) -> bool {
        self.inner.can_print()
    }

    #[getter]
    fn can_copy(&self) -> bool {
        self.inner.can_copy()
    }

    #[getter]
    fn can_modify_contents(&self) -> bool {
        self.inner.can_modify_contents()
    }

    #[getter]
    fn can_modify_annotations(&self) -> bool {
        self.inner.can_modify_annotations()
    }

    #[getter]
    fn can_fill_forms(&self) -> bool {
        self.inner.can_fill_forms()
    }

    #[getter]
    fn can_assemble(&self) -> bool {
        self.inner.can_assemble()
    }

    #[getter]
    fn can_print_high_quality(&self) -> bool {
        self.inner.can_print_high_quality()
    }

    fn __repr__(&self) -> String {
        let flags: Vec<&str> = [
            (self.inner.can_print(), "print"),
            (self.inner.can_copy(), "copy"),
            (self.inner.can_modify_contents(), "modify_contents"),
            (self.inner.can_modify_annotations(), "modify_annotations"),
            (self.inner.can_fill_forms(), "fill_forms"),
            (self.inner.can_assemble(), "assemble"),
            (self.inner.can_print_high_quality(), "print_high_quality"),
        ]
        .into_iter()
        .filter(|(allowed, _)| *allowed)
        .map(|(_, name)| name)
        .collect();

        if flags.is_empty() {
            "Permissions(none)".to_string()
        } else {
            format!("Permissions({})", flags.join(", "))
        }
    }
}

// ── EncryptionStrength ─────────────────────────────────────────────────────

#[pyclass(name = "EncryptionStrength", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyEncryptionStrength {
    pub inner: oxidize_pdf::document::EncryptionStrength,
}

#[pymethods]
impl PyEncryptionStrength {
    #[classattr]
    const RC4_40: PyEncryptionStrength = PyEncryptionStrength {
        inner: oxidize_pdf::document::EncryptionStrength::Rc4_40bit,
    };
    #[classattr]
    const RC4_128: PyEncryptionStrength = PyEncryptionStrength {
        inner: oxidize_pdf::document::EncryptionStrength::Rc4_128bit,
    };
    #[classattr]
    const AES_128: PyEncryptionStrength = PyEncryptionStrength {
        inner: oxidize_pdf::document::EncryptionStrength::Aes128,
    };
    #[classattr]
    const AES_256: PyEncryptionStrength = PyEncryptionStrength {
        inner: oxidize_pdf::document::EncryptionStrength::Aes256,
    };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            oxidize_pdf::document::EncryptionStrength::Rc4_40bit => "RC4_40",
            oxidize_pdf::document::EncryptionStrength::Rc4_128bit => "RC4_128",
            oxidize_pdf::document::EncryptionStrength::Aes128 => "AES_128",
            oxidize_pdf::document::EncryptionStrength::Aes256 => "AES_256",
        };
        format!("EncryptionStrength.{name}")
    }
}

// ── Recipient (Feature 29) ────────────────────────────────────────────────

#[pyclass(name = "Recipient", from_py_object)]
#[derive(Clone)]
pub struct PyRecipient {
    pub inner: oxidize_pdf::encryption::Recipient,
}

#[pymethods]
impl PyRecipient {
    #[staticmethod]
    fn from_certificate(cert_data: &[u8]) -> PyResult<Self> {
        const MIN_CERT_LEN: usize = 64;
        if cert_data.len() < MIN_CERT_LEN {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Invalid certificate data: too short ({} bytes, minimum {MIN_CERT_LEN})",
                cert_data.len()
            )));
        }
        if cert_data[0] != 0x30 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid certificate data: not a valid DER-encoded X.509 certificate",
            ));
        }
        Ok(Self {
            inner: oxidize_pdf::encryption::Recipient {
                certificate: cert_data.to_vec(),
                permissions: oxidize_pdf::encryption::Permissions::all(),
                encrypted_seed: Vec::new(),
            },
        })
    }

    fn __repr__(&self) -> String {
        format!("Recipient(cert_len={})", self.inner.certificate.len())
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPermissions>()?;
    m.add_class::<PyEncryptionStrength>()?;
    m.add_class::<PyRecipient>()?;
    Ok(())
}
