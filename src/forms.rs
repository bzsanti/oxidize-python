use pyo3::prelude::*;

use oxidize_pdf::forms;

// ── TextField ─────────────────────────────────────────────────────────────

#[pyclass(name = "TextField", from_py_object)]
#[derive(Clone)]
pub struct PyTextField {
    pub inner: forms::TextField,
}

#[pymethods]
impl PyTextField {
    #[new]
    fn new(name: &str) -> Self {
        Self {
            inner: forms::TextField::new(name),
        }
    }

    fn with_default_value(self_: PyRef<'_, Self>, value: &str) -> Self {
        Self {
            inner: self_.inner.clone().with_default_value(value),
        }
    }

    fn with_value(self_: PyRef<'_, Self>, value: &str) -> Self {
        Self {
            inner: self_.inner.clone().with_value(value),
        }
    }

    fn with_max_length(self_: PyRef<'_, Self>, length: i32) -> Self {
        Self {
            inner: self_.inner.clone().with_max_length(length),
        }
    }

    fn multiline(self_: PyRef<'_, Self>) -> Self {
        Self {
            inner: self_.inner.clone().multiline(),
        }
    }

    fn password(self_: PyRef<'_, Self>) -> Self {
        Self {
            inner: self_.inner.clone().password(),
        }
    }

    fn __repr__(&self) -> String {
        format!("TextField(name={:?})", self.inner.name)
    }
}

// ── CheckBox ──────────────────────────────────────────────────────────────

#[pyclass(name = "CheckBox", from_py_object)]
#[derive(Clone)]
pub struct PyCheckBox {
    pub inner: forms::CheckBox,
}

#[pymethods]
impl PyCheckBox {
    #[new]
    fn new(name: &str) -> Self {
        Self {
            inner: forms::CheckBox::new(name),
        }
    }

    fn checked(self_: PyRef<'_, Self>) -> Self {
        Self {
            inner: self_.inner.clone().checked(),
        }
    }

    fn with_export_value(self_: PyRef<'_, Self>, value: &str) -> Self {
        Self {
            inner: self_.inner.clone().with_export_value(value),
        }
    }

    fn __repr__(&self) -> String {
        format!("CheckBox(name={:?})", self.inner.name)
    }
}

// ── RadioButton ───────────────────────────────────────────────────────────

#[pyclass(name = "RadioButton", from_py_object)]
#[derive(Clone)]
pub struct PyRadioButton {
    pub inner: forms::RadioButton,
}

#[pymethods]
impl PyRadioButton {
    #[new]
    fn new(name: &str) -> Self {
        Self {
            inner: forms::RadioButton::new(name),
        }
    }

    fn add_option(self_: PyRef<'_, Self>, export_value: &str, label: &str) -> Self {
        Self {
            inner: self_.inner.clone().add_option(export_value, label),
        }
    }

    fn with_selected(self_: PyRef<'_, Self>, index: usize) -> Self {
        Self {
            inner: self_.inner.clone().with_selected(index),
        }
    }

    fn __repr__(&self) -> String {
        format!("RadioButton(name={:?})", self.inner.name)
    }
}

// ── ComboBox ──────────────────────────────────────────────────────────────

#[pyclass(name = "ComboBox", from_py_object)]
#[derive(Clone)]
pub struct PyComboBox {
    pub inner: forms::ComboBox,
}

#[pymethods]
impl PyComboBox {
    #[new]
    fn new(name: &str) -> Self {
        Self {
            inner: forms::ComboBox::new(name),
        }
    }

    fn add_option(self_: PyRef<'_, Self>, export_value: &str, display: &str) -> Self {
        Self {
            inner: self_.inner.clone().add_option(export_value, display),
        }
    }

    fn editable(self_: PyRef<'_, Self>) -> Self {
        Self {
            inner: self_.inner.clone().editable(),
        }
    }

    fn with_value(self_: PyRef<'_, Self>, value: &str) -> Self {
        Self {
            inner: self_.inner.clone().with_value(value),
        }
    }

    fn __repr__(&self) -> String {
        format!("ComboBox(name={:?})", self.inner.name)
    }
}

// ── ListBox ───────────────────────────────────────────────────────────────

#[pyclass(name = "ListBox", from_py_object)]
#[derive(Clone)]
pub struct PyListBox {
    pub inner: forms::ListBox,
}

#[pymethods]
impl PyListBox {
    #[new]
    fn new(name: &str) -> Self {
        Self {
            inner: forms::ListBox::new(name),
        }
    }

    fn add_option(self_: PyRef<'_, Self>, export_value: &str, display: &str) -> Self {
        Self {
            inner: self_.inner.clone().add_option(export_value, display),
        }
    }

    fn multi_select(self_: PyRef<'_, Self>) -> Self {
        Self {
            inner: self_.inner.clone().multi_select(),
        }
    }

    fn __repr__(&self) -> String {
        format!("ListBox(name={:?})", self.inner.name)
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTextField>()?;
    m.add_class::<PyCheckBox>()?;
    m.add_class::<PyRadioButton>()?;
    m.add_class::<PyComboBox>()?;
    m.add_class::<PyListBox>()?;
    Ok(())
}
