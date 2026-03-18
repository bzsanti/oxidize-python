use pyo3::prelude::*;
use pyo3::types::PyDict;

use oxidize_pdf::forms;
use oxidize_pdf::forms::calculations::FieldValue;
use oxidize_pdf::forms::validation::{FieldValidator, FormValidationSystem, ValidationRule};


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

// ── FieldValue ────────────────────────────────────────────────────────────

#[pyclass(name = "FieldValue", from_py_object)]
#[derive(Clone)]
pub struct PyFieldValue {
    pub inner: FieldValue,
}

#[pymethods]
impl PyFieldValue {
    #[staticmethod]
    fn number(n: f64) -> Self {
        Self { inner: FieldValue::Number(n) }
    }

    #[staticmethod]
    fn text(s: &str) -> Self {
        Self { inner: FieldValue::Text(s.to_string()) }
    }

    #[staticmethod]
    fn boolean(b: bool) -> Self {
        Self { inner: FieldValue::Boolean(b) }
    }

    #[staticmethod]
    fn empty() -> Self {
        Self { inner: FieldValue::Empty }
    }

    fn to_number(&self) -> f64 {
        self.inner.to_number()
    }

    fn to_text(&self) -> String {
        self.inner.to_string()
    }

    fn __repr__(&self) -> String {
        format!("FieldValue({:?})", self.inner.to_string())
    }
}

// ── ValidationRule ────────────────────────────────────────────────────────

#[pyclass(name = "ValidationRule", from_py_object)]
#[derive(Clone)]
pub struct PyValidationRule {
    pub inner: ValidationRule,
}

#[pymethods]
impl PyValidationRule {
    #[staticmethod]
    fn required() -> Self {
        Self { inner: ValidationRule::Required }
    }

    #[staticmethod]
    #[pyo3(signature = (min=None, max=None))]
    fn range(min: Option<f64>, max: Option<f64>) -> Self {
        Self { inner: ValidationRule::Range { min, max } }
    }

    #[staticmethod]
    #[pyo3(signature = (min=None, max=None))]
    fn length(min: Option<usize>, max: Option<usize>) -> Self {
        Self { inner: ValidationRule::Length { min, max } }
    }

    #[staticmethod]
    fn pattern(regex: &str) -> Self {
        Self { inner: ValidationRule::Pattern(regex.to_string()) }
    }

    #[staticmethod]
    fn email() -> Self {
        Self { inner: ValidationRule::Email }
    }

    #[staticmethod]
    fn url() -> Self {
        Self { inner: ValidationRule::Url }
    }

    fn __repr__(&self) -> String {
        "ValidationRule(...)".to_string()
    }
}

// ── FieldValidator ────────────────────────────────────────────────────────

#[pyclass(name = "FieldValidator")]
pub struct PyFieldValidator {
    pub inner: FieldValidator,
}

#[pymethods]
impl PyFieldValidator {
    #[new]
    fn new(field_name: &str) -> Self {
        Self {
            inner: FieldValidator {
                field_name: field_name.to_string(),
                rules: Vec::new(),
                format_mask: None,
                error_message: None,
            },
        }
    }

    fn add_rule(&mut self, rule: &PyValidationRule) {
        self.inner.rules.push(rule.inner.clone());
    }

    fn __repr__(&self) -> String {
        format!("FieldValidator(field={:?})", self.inner.field_name)
    }
}

// ── FormValidationSystem ──────────────────────────────────────────────────

#[pyclass(name = "FormValidationSystem")]
pub struct PyFormValidationSystem {
    pub inner: FormValidationSystem,
}

#[pymethods]
impl PyFormValidationSystem {
    #[new]
    fn new() -> Self {
        Self { inner: FormValidationSystem::new() }
    }

    fn add_validator(&mut self, validator: &mut PyFieldValidator) {
        self.inner.add_validator(validator.inner.clone());
    }

    fn validate_field<'py>(
        &mut self,
        py: Python<'py>,
        name: &str,
        value: &PyFieldValue,
    ) -> PyResult<Bound<'py, PyDict>> {
        let result = self.inner.validate_field(name, &value.inner);
        let dict = PyDict::new(py);
        dict.set_item("field_name", &result.field_name)?;
        dict.set_item("is_valid", result.is_valid)?;
        let errors: Vec<String> = result.errors.iter().map(|e| e.message.clone()).collect();
        dict.set_item("errors", errors)?;
        if let Some(formatted) = result.formatted_value {
            dict.set_item("formatted_value", formatted)?;
        }
        Ok(dict)
    }

    fn __repr__(&self) -> String {
        "FormValidationSystem(...)".to_string()
    }
}

// ── Registration ──────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTextField>()?;
    m.add_class::<PyCheckBox>()?;
    m.add_class::<PyRadioButton>()?;
    m.add_class::<PyComboBox>()?;
    m.add_class::<PyListBox>()?;
    m.add_class::<PyFieldValue>()?;
    m.add_class::<PyValidationRule>()?;
    m.add_class::<PyFieldValidator>()?;
    m.add_class::<PyFormValidationSystem>()?;
    Ok(())
}
