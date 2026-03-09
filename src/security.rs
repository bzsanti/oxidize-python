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

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPermissions>()?;
    Ok(())
}
