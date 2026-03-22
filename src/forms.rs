use std::collections::HashMap;
use pyo3::prelude::*;

use oxidize_pdf::forms;
use oxidize_pdf::forms::calculations::FieldValue;
use oxidize_pdf::forms::validation::{
    FieldValidator, FormValidationSystem, ValidationResult, ValidationRule,
};
use oxidize_pdf::forms::{
    FormManager, AcroForm, FormData, Widget, FieldOptions, FieldFlags, PushButton,
    AppearanceState, AppearanceStream,
};
use oxidize_pdf::forms::calculations::CalculationEngine;
use oxidize_pdf::forms::calculation_system::{
    FormCalculationSystem, JavaScriptCalculation, SimpleOperation, PercentMode,
    SeparatorStyle, FieldFormat, NegativeStyle, SpecialFormat, CalculationSettings,
};
use oxidize_pdf::{
    FieldAction, FieldActions, FieldActionSystem,
    FormatActionType, ValidateActionType, SpecialFormatType, ActionSettings,
};
use crate::types::PyRectangle;
use crate::errors::to_py_err as pdf_err_to_py;


// ── TextField ─────────────────────────────────────────────────────────────

/// Single-line or multiline text input form field.
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

/// Boolean checkbox form field.
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

/// Mutually exclusive radio button group form field.
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

/// Drop-down combo box form field, optionally editable.
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

/// Scrollable list box form field, optionally multi-select.
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

/// Typed value for a form field (number, text, boolean, or empty).
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

/// A single validation rule for a form field (required, range, length, pattern, email, URL).
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
        match &self.inner {
            ValidationRule::Required => "ValidationRule.required()".to_string(),
            ValidationRule::Range { min, max } => format!("ValidationRule.range(min={min:?}, max={max:?})"),
            ValidationRule::Length { min, max } => format!("ValidationRule.length(min={min:?}, max={max:?})"),
            ValidationRule::Pattern(p) => format!("ValidationRule.pattern({p:?})"),
            ValidationRule::Email => "ValidationRule.email()".to_string(),
            ValidationRule::Url => "ValidationRule.url()".to_string(),
            ValidationRule::PhoneNumber { .. } => "ValidationRule.phone_number(...)".to_string(),
            ValidationRule::Date { .. } => "ValidationRule.date(...)".to_string(),
            ValidationRule::Time { .. } => "ValidationRule.time(...)".to_string(),
            ValidationRule::CreditCard => "ValidationRule.credit_card()".to_string(),
            ValidationRule::Custom { name, .. } => format!("ValidationRule.custom({name:?})"),
        }
    }
}

// ── FieldValidator ────────────────────────────────────────────────────────

/// Validator that applies a set of rules to a named form field.
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

/// Result of validating a form field.
#[pyclass(name = "ValidationResult", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyValidationResult {
    pub inner: ValidationResult,
}

#[pymethods]
impl PyValidationResult {
    #[getter]
    fn field_name(&self) -> &str { &self.inner.field_name }

    #[getter]
    fn is_valid(&self) -> bool { self.inner.is_valid }

    #[getter]
    fn errors(&self) -> Vec<String> {
        self.inner.errors.iter().map(|e| e.message.clone()).collect()
    }

    #[getter]
    fn warnings(&self) -> Vec<String> { self.inner.warnings.clone() }

    #[getter]
    fn formatted_value(&self) -> Option<&str> { self.inner.formatted_value.as_deref() }

    fn __repr__(&self) -> String {
        format!("ValidationResult(field={:?}, valid={}, errors={})",
            self.inner.field_name, self.inner.is_valid, self.inner.errors.len())
    }
}

/// System for validating form field values against registered rules.
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

    /// Validate a field value. Returns a ValidationResult with field_name, is_valid, errors, warnings, formatted_value.
    fn validate_field(
        &mut self,
        name: &str,
        value: &PyFieldValue,
    ) -> PyValidationResult {
        let result = self.inner.validate_field(name, &value.inner);
        PyValidationResult { inner: result }
    }

    fn __repr__(&self) -> String {
        "FormValidationSystem(...)".to_string()
    }
}

// ── Group A — Form Management ──────────────────────────────────────────────

/// Key-value form data container.
#[pyclass(name = "FormData", from_py_object)]
#[derive(Clone)]
pub struct PyFormData {
    pub inner: FormData,
}

#[pymethods]
impl PyFormData {
    #[new]
    fn new() -> Self { Self { inner: FormData::new() } }

    fn set_value(&mut self, name: &str, value: &str) {
        self.inner.set_value(name, value);
    }

    fn get_value(&self, name: &str) -> Option<String> {
        self.inner.get_value(name).map(|s| s.to_string())
    }

    fn __repr__(&self) -> String {
        format!("FormData(entries={})", self.inner.values.len())
    }
}

// ── Widget ────────────────────────────────────────────────────────────────

/// Widget positioning for form fields.
#[pyclass(name = "Widget", from_py_object)]
#[derive(Clone)]
pub struct PyWidget {
    pub inner: Widget,
}

#[pymethods]
impl PyWidget {
    #[new]
    fn new(rect: &PyRectangle) -> Self {
        Self { inner: Widget::new(rect.inner.clone()) }
    }

    fn __repr__(&self) -> String {
        let r = &self.inner.rect;
        format!("Widget(rect=[{:.1}, {:.1}, {:.1}, {:.1}])",
            r.lower_left.x, r.lower_left.y, r.upper_right.x, r.upper_right.y)
    }
}

// ── FieldOptions ──────────────────────────────────────────────────────────

/// Options controlling form field behavior (read-only, required, no-export).
#[pyclass(name = "FieldOptions", from_py_object)]
#[derive(Clone)]
pub struct PyFieldOptions {
    pub inner: FieldOptions,
}

#[pymethods]
impl PyFieldOptions {
    #[new]
    #[pyo3(signature = (read_only=false, required=false, no_export=false))]
    fn new(read_only: bool, required: bool, no_export: bool) -> Self {
        Self {
            inner: FieldOptions {
                flags: FieldFlags { read_only, required, no_export },
                default_appearance: None,
                quadding: None,
            },
        }
    }

    #[getter]
    fn read_only(&self) -> bool { self.inner.flags.read_only }
    #[getter]
    fn required(&self) -> bool { self.inner.flags.required }
    #[getter]
    fn no_export(&self) -> bool { self.inner.flags.no_export }

    fn __repr__(&self) -> String {
        format!("FieldOptions(read_only={}, required={}, no_export={})",
            self.inner.flags.read_only, self.inner.flags.required, self.inner.flags.no_export)
    }
}

// ── PushButton ────────────────────────────────────────────────────────────

/// Push button form field.
#[pyclass(name = "PushButton", from_py_object)]
#[derive(Clone)]
pub struct PyPushButton {
    pub inner: PushButton,
}

#[pymethods]
impl PyPushButton {
    #[new]
    fn new(name: &str) -> Self { Self { inner: PushButton::new(name) } }

    fn with_caption(self_: PyRef<'_, Self>, caption: &str) -> Self {
        Self { inner: self_.inner.clone().with_caption(caption) }
    }

    fn __repr__(&self) -> String {
        format!("PushButton(name={:?})", self.inner.name)
    }
}

// ── AcroForm ──────────────────────────────────────────────────────────────

/// PDF interactive form dictionary (AcroForm).
#[pyclass(name = "AcroForm", from_py_object)]
#[derive(Clone)]
pub struct PyAcroForm {
    pub inner: AcroForm,
}

#[pymethods]
impl PyAcroForm {
    #[new]
    fn new() -> Self { Self { inner: AcroForm::new() } }

    #[getter]
    fn need_appearances(&self) -> bool { self.inner.need_appearances }

    #[getter]
    fn sig_flags(&self) -> Option<i32> { self.inner.sig_flags }

    #[getter]
    fn field_count(&self) -> usize { self.inner.fields.len() }

    fn __repr__(&self) -> String {
        format!("AcroForm(fields={})", self.inner.fields.len())
    }
}

// ── FormManager ───────────────────────────────────────────────────────────

/// Manages form fields and their widgets within a PDF document.
#[pyclass(name = "FormManager")]
pub struct PyFormManager {
    pub inner: FormManager,
}

#[pymethods]
impl PyFormManager {
    #[new]
    fn new() -> Self { Self { inner: FormManager::new() } }

    #[pyo3(signature = (field, widget, options=None))]
    fn add_text_field(&mut self, field: &PyTextField, widget: &PyWidget, options: Option<&PyFieldOptions>) -> PyResult<()> {
        self.inner.add_text_field(
            field.inner.clone(),
            widget.inner.clone(),
            options.map(|o| o.inner.clone()),
        ).map_err(pdf_err_to_py)?;
        Ok(())
    }

    #[pyo3(signature = (field, widget, options=None))]
    fn add_combo_box(&mut self, field: &PyComboBox, widget: &PyWidget, options: Option<&PyFieldOptions>) -> PyResult<()> {
        self.inner.add_combo_box(
            field.inner.clone(),
            widget.inner.clone(),
            options.map(|o| o.inner.clone()),
        ).map_err(pdf_err_to_py)?;
        Ok(())
    }

    #[pyo3(signature = (field, widget, options=None))]
    fn add_list_box(&mut self, field: &PyListBox, widget: &PyWidget, options: Option<&PyFieldOptions>) -> PyResult<()> {
        self.inner.add_list_box(
            field.inner.clone(),
            widget.inner.clone(),
            options.map(|o| o.inner.clone()),
        ).map_err(pdf_err_to_py)?;
        Ok(())
    }

    #[pyo3(signature = (field, widget, options=None))]
    fn add_checkbox(&mut self, field: &PyCheckBox, widget: &PyWidget, options: Option<&PyFieldOptions>) -> PyResult<()> {
        self.inner.add_checkbox(
            field.inner.clone(),
            widget.inner.clone(),
            options.map(|o| o.inner.clone()),
        ).map_err(pdf_err_to_py)?;
        Ok(())
    }

    #[pyo3(signature = (field, widget, options=None))]
    fn add_push_button(&mut self, field: &PyPushButton, widget: &PyWidget, options: Option<&PyFieldOptions>) -> PyResult<()> {
        self.inner.add_push_button(
            field.inner.clone(),
            widget.inner.clone(),
            options.map(|o| o.inner.clone()),
        ).map_err(pdf_err_to_py)?;
        Ok(())
    }

    #[pyo3(signature = (field, widgets, options=None))]
    fn add_radio_button(&mut self, field: &PyRadioButton, widgets: Vec<PyRef<'_, PyWidget>>, options: Option<&PyFieldOptions>) -> PyResult<()> {
        let rust_widgets: Vec<Widget> = widgets.iter().map(|w| w.inner.clone()).collect();
        self.inner.add_radio_buttons(
            field.inner.clone(),
            rust_widgets,
            options.map(|o| o.inner.clone()),
        ).map_err(pdf_err_to_py)?;
        Ok(())
    }

    #[getter]
    fn field_count(&self) -> usize { self.inner.field_count() }

    fn get_acro_form(&self) -> PyAcroForm {
        PyAcroForm { inner: self.inner.get_acro_form().clone() }
    }

    fn __repr__(&self) -> String {
        format!("FormManager(fields={})", self.inner.field_count())
    }
}

// ── Group B — Field Actions ───────────────────────────────────────────────

/// Special format type for phone, ZIP code, and SSN fields.
#[pyclass(name = "SpecialFormatType", frozen, from_py_object)]
#[derive(Clone, Copy)]
pub struct PySpecialFormatType {
    pub inner: SpecialFormatType,
}

#[pymethods]
impl PySpecialFormatType {
    #[classattr]
    const ZIP_CODE: Self = Self { inner: SpecialFormatType::ZipCode };
    #[classattr]
    const ZIP_PLUS_4: Self = Self { inner: SpecialFormatType::ZipPlus4 };
    #[classattr]
    const PHONE: Self = Self { inner: SpecialFormatType::Phone };
    #[classattr]
    const SSN: Self = Self { inner: SpecialFormatType::SSN };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            SpecialFormatType::ZipCode => "ZIP_CODE",
            SpecialFormatType::ZipPlus4 => "ZIP_PLUS_4",
            SpecialFormatType::Phone => "PHONE",
            SpecialFormatType::SSN => "SSN",
        };
        format!("SpecialFormatType.{name}")
    }
}

// ── FieldAction ───────────────────────────────────────────────────────────

/// A single form field action (JavaScript, format, validate, calculate, etc.).
#[pyclass(name = "FieldAction", from_py_object)]
#[derive(Clone)]
pub struct PyFieldAction {
    pub inner: FieldAction,
}

#[pymethods]
impl PyFieldAction {
    #[staticmethod]
    #[pyo3(signature = (script, async_exec=false))]
    fn javascript(script: &str, async_exec: bool) -> Self {
        Self { inner: FieldAction::JavaScript { script: script.to_string(), async_exec } }
    }

    #[staticmethod]
    #[pyo3(signature = (decimals, currency=None))]
    fn format_number(decimals: usize, currency: Option<String>) -> Self {
        Self { inner: FieldAction::Format { format_type: FormatActionType::Number { decimals, currency } } }
    }

    #[staticmethod]
    fn format_percent(decimals: usize) -> Self {
        Self { inner: FieldAction::Format { format_type: FormatActionType::Percent { decimals } } }
    }

    #[staticmethod]
    fn format_date(format: &str) -> Self {
        Self { inner: FieldAction::Format { format_type: FormatActionType::Date { format: format.to_string() } } }
    }

    #[staticmethod]
    fn format_time(format: &str) -> Self {
        Self { inner: FieldAction::Format { format_type: FormatActionType::Time { format: format.to_string() } } }
    }

    #[staticmethod]
    fn format_special(special: &PySpecialFormatType) -> Self {
        Self { inner: FieldAction::Format { format_type: FormatActionType::Special { format: special.inner } } }
    }

    #[staticmethod]
    fn format_custom(script: &str) -> Self {
        Self { inner: FieldAction::Format { format_type: FormatActionType::Custom { script: script.to_string() } } }
    }

    #[staticmethod]
    #[pyo3(signature = (min=None, max=None))]
    fn validate_range(min: Option<f64>, max: Option<f64>) -> Self {
        Self { inner: FieldAction::Validate { validation_type: ValidateActionType::Range { min, max } } }
    }

    #[staticmethod]
    fn validate_custom(script: &str) -> Self {
        Self { inner: FieldAction::Validate { validation_type: ValidateActionType::Custom { script: script.to_string() } } }
    }

    #[staticmethod]
    fn calculate(expression: &str) -> Self {
        Self { inner: FieldAction::Calculate { expression: expression.to_string() } }
    }

    #[staticmethod]
    fn submit_form(url: &str, fields: Vec<String>, include_empty: bool) -> Self {
        Self { inner: FieldAction::SubmitForm { url: url.to_string(), fields, include_empty } }
    }

    #[staticmethod]
    fn reset_form(fields: Vec<String>, exclude: bool) -> Self {
        Self { inner: FieldAction::ResetForm { fields, exclude } }
    }

    #[staticmethod]
    fn import_data(file_path: &str) -> Self {
        Self { inner: FieldAction::ImportData { file_path: file_path.to_string() } }
    }

    #[staticmethod]
    fn set_field(target_field: &str, value: &PyFieldValue) -> Self {
        Self { inner: FieldAction::SetField { target_field: target_field.to_string(), value: value.inner.clone() } }
    }

    #[staticmethod]
    fn show_hide(fields: Vec<String>, show: bool) -> Self {
        Self { inner: FieldAction::ShowHide { fields, show } }
    }

    #[staticmethod]
    fn play_sound(sound_name: &str, volume: f32) -> Self {
        Self { inner: FieldAction::PlaySound { sound_name: sound_name.to_string(), volume } }
    }

    #[staticmethod]
    fn custom(action_type: &str, parameters: HashMap<String, String>) -> Self {
        Self { inner: FieldAction::Custom { action_type: action_type.to_string(), parameters } }
    }

    fn __repr__(&self) -> String {
        let variant = match &self.inner {
            FieldAction::JavaScript { script, .. } => format!("javascript({:?})", script),
            FieldAction::Format { .. } => "format(...)".to_string(),
            FieldAction::Validate { .. } => "validate(...)".to_string(),
            FieldAction::Calculate { expression } => format!("calculate({:?})", expression),
            FieldAction::SubmitForm { url, .. } => format!("submit_form({:?})", url),
            FieldAction::ResetForm { .. } => "reset_form(...)".to_string(),
            FieldAction::ImportData { file_path } => format!("import_data({:?})", file_path),
            FieldAction::SetField { target_field, .. } => format!("set_field({:?})", target_field),
            FieldAction::ShowHide { fields, show } => format!("show_hide({:?}, {})", fields, show),
            FieldAction::PlaySound { sound_name, volume } => format!("play_sound({:?}, {})", sound_name, volume),
            FieldAction::Custom { action_type, .. } => format!("custom({:?})", action_type),
        };
        format!("FieldAction.{variant}")
    }
}

// ── FieldActions ──────────────────────────────────────────────────────────

/// Collection of actions attached to a form field (focus, blur, format, validate, calculate, etc.).
#[pyclass(name = "FieldActions", from_py_object)]
#[derive(Clone)]
pub struct PyFieldActions {
    pub inner: FieldActions,
}

#[pymethods]
impl PyFieldActions {
    #[new]
    #[pyo3(signature = (on_focus=None, on_blur=None, on_format=None, on_keystroke=None, on_calculate=None, on_validate=None, on_mouse_enter=None, on_mouse_exit=None, on_mouse_down=None, on_mouse_up=None))]
    fn new(
        on_focus: Option<PyFieldAction>,
        on_blur: Option<PyFieldAction>,
        on_format: Option<PyFieldAction>,
        on_keystroke: Option<PyFieldAction>,
        on_calculate: Option<PyFieldAction>,
        on_validate: Option<PyFieldAction>,
        on_mouse_enter: Option<PyFieldAction>,
        on_mouse_exit: Option<PyFieldAction>,
        on_mouse_down: Option<PyFieldAction>,
        on_mouse_up: Option<PyFieldAction>,
    ) -> Self {
        Self {
            inner: FieldActions {
                on_focus: on_focus.map(|a| a.inner),
                on_blur: on_blur.map(|a| a.inner),
                on_format: on_format.map(|a| a.inner),
                on_keystroke: on_keystroke.map(|a| a.inner),
                on_calculate: on_calculate.map(|a| a.inner),
                on_validate: on_validate.map(|a| a.inner),
                on_mouse_enter: on_mouse_enter.map(|a| a.inner),
                on_mouse_exit: on_mouse_exit.map(|a| a.inner),
                on_mouse_down: on_mouse_down.map(|a| a.inner),
                on_mouse_up: on_mouse_up.map(|a| a.inner),
            },
        }
    }

    #[getter]
    fn on_focus(&self) -> Option<PyFieldAction> {
        self.inner.on_focus.as_ref().map(|a| PyFieldAction { inner: a.clone() })
    }
    #[getter]
    fn on_blur(&self) -> Option<PyFieldAction> {
        self.inner.on_blur.as_ref().map(|a| PyFieldAction { inner: a.clone() })
    }
    #[getter]
    fn on_format(&self) -> Option<PyFieldAction> {
        self.inner.on_format.as_ref().map(|a| PyFieldAction { inner: a.clone() })
    }
    #[getter]
    fn on_keystroke(&self) -> Option<PyFieldAction> {
        self.inner.on_keystroke.as_ref().map(|a| PyFieldAction { inner: a.clone() })
    }
    #[getter]
    fn on_calculate(&self) -> Option<PyFieldAction> {
        self.inner.on_calculate.as_ref().map(|a| PyFieldAction { inner: a.clone() })
    }
    #[getter]
    fn on_validate(&self) -> Option<PyFieldAction> {
        self.inner.on_validate.as_ref().map(|a| PyFieldAction { inner: a.clone() })
    }
    #[getter]
    fn on_mouse_enter(&self) -> Option<PyFieldAction> {
        self.inner.on_mouse_enter.as_ref().map(|a| PyFieldAction { inner: a.clone() })
    }
    #[getter]
    fn on_mouse_exit(&self) -> Option<PyFieldAction> {
        self.inner.on_mouse_exit.as_ref().map(|a| PyFieldAction { inner: a.clone() })
    }
    #[getter]
    fn on_mouse_down(&self) -> Option<PyFieldAction> {
        self.inner.on_mouse_down.as_ref().map(|a| PyFieldAction { inner: a.clone() })
    }
    #[getter]
    fn on_mouse_up(&self) -> Option<PyFieldAction> {
        self.inner.on_mouse_up.as_ref().map(|a| PyFieldAction { inner: a.clone() })
    }

    fn __repr__(&self) -> String {
        let count = [
            &self.inner.on_focus, &self.inner.on_blur, &self.inner.on_format,
            &self.inner.on_keystroke, &self.inner.on_calculate, &self.inner.on_validate,
            &self.inner.on_mouse_enter, &self.inner.on_mouse_exit,
            &self.inner.on_mouse_down, &self.inner.on_mouse_up,
        ].iter().filter(|a| a.is_some()).count();
        format!("FieldActions(actions_set={count})")
    }
}

// ── ActionSettings ────────────────────────────────────────────────────────

/// Settings controlling which action types are enabled and how events are logged.
#[pyclass(name = "ActionSettings", from_py_object)]
#[derive(Clone)]
pub struct PyActionSettings {
    pub inner: ActionSettings,
}

#[pymethods]
impl PyActionSettings {
    #[new]
    #[pyo3(signature = (enable_javascript=true, enable_form_submit=false, enable_sound=true, log_events=true, max_event_history=1000))]
    fn new(
        enable_javascript: bool,
        enable_form_submit: bool,
        enable_sound: bool,
        log_events: bool,
        max_event_history: usize,
    ) -> Self {
        Self {
            inner: ActionSettings {
                enable_javascript,
                enable_form_submit,
                enable_sound,
                log_events,
                max_event_history,
            },
        }
    }

    fn __repr__(&self) -> String {
        format!("ActionSettings(js={}, log={})",
            self.inner.enable_javascript, self.inner.log_events)
    }
}

// ── FieldActionSystem ─────────────────────────────────────────────────────

/// Processes and dispatches form field events through registered actions.
#[pyclass(name = "FieldActionSystem")]
pub struct PyFieldActionSystem {
    pub inner: FieldActionSystem,
}

#[pymethods]
impl PyFieldActionSystem {
    #[new]
    #[pyo3(signature = (settings=None))]
    fn new(settings: Option<&PyActionSettings>) -> Self {
        match settings {
            Some(s) => Self { inner: FieldActionSystem::with_settings(s.inner.clone()) },
            None => Self { inner: FieldActionSystem::new() },
        }
    }

    fn register_field_actions(&mut self, field_name: &str, actions: &PyFieldActions) {
        self.inner.register_field_actions(field_name, actions.inner.clone());
    }

    fn handle_focus(&mut self, field_name: &str) -> PyResult<()> {
        self.inner.handle_focus(field_name).map_err(pdf_err_to_py)
    }

    fn handle_blur(&mut self, field_name: &str) -> PyResult<()> {
        self.inner.handle_blur(field_name).map_err(pdf_err_to_py)
    }

    fn handle_validate(&mut self, field_name: &str, value: &PyFieldValue) -> PyResult<bool> {
        self.inner.handle_validate(field_name, &value.inner).map_err(pdf_err_to_py)
    }

    fn handle_keystroke(&mut self, field_name: &str, key: char, current_value: &str) -> PyResult<bool> {
        self.inner.handle_keystroke(field_name, key, current_value).map_err(pdf_err_to_py)
    }

    fn get_focused_field(&self) -> Option<String> {
        self.inner.get_focused_field().cloned()
    }

    #[getter]
    fn event_history_count(&self) -> usize {
        self.inner.get_event_history().len()
    }

    fn clear_event_history(&mut self) {
        self.inner.clear_event_history();
    }

    fn __repr__(&self) -> String { "FieldActionSystem(...)".to_string() }
}

// ── Group C — Calculations ────────────────────────────────────────────────

/// Aggregate operation for a simple calculation (sum, product, average, min, max).
#[pyclass(name = "SimpleOperation", frozen, from_py_object)]
#[derive(Clone, Copy)]
pub struct PySimpleOperation {
    pub inner: SimpleOperation,
}

#[pymethods]
impl PySimpleOperation {
    #[classattr]
    const SUM: Self = Self { inner: SimpleOperation::Sum };
    #[classattr]
    const PRODUCT: Self = Self { inner: SimpleOperation::Product };
    #[classattr]
    const AVERAGE: Self = Self { inner: SimpleOperation::Average };
    #[classattr]
    const MINIMUM: Self = Self { inner: SimpleOperation::Minimum };
    #[classattr]
    const MAXIMUM: Self = Self { inner: SimpleOperation::Maximum };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            SimpleOperation::Sum => "SUM",
            SimpleOperation::Product => "PRODUCT",
            SimpleOperation::Average => "AVERAGE",
            SimpleOperation::Minimum => "MINIMUM",
            SimpleOperation::Maximum => "MAXIMUM",
        };
        format!("SimpleOperation.{name}")
    }
}

/// Percentage calculation mode.
#[pyclass(name = "PercentMode", frozen, from_py_object)]
#[derive(Clone, Copy)]
pub struct PyPercentMode {
    pub inner: PercentMode,
}

#[pymethods]
impl PyPercentMode {
    #[classattr]
    const PERCENT_OF: Self = Self { inner: PercentMode::PercentOf };
    #[classattr]
    const PERCENTAGE_OF: Self = Self { inner: PercentMode::PercentageOf };
    #[classattr]
    const ADD_PERCENT: Self = Self { inner: PercentMode::AddPercent };
    #[classattr]
    const SUBTRACT_PERCENT: Self = Self { inner: PercentMode::SubtractPercent };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            PercentMode::PercentOf => "PERCENT_OF",
            PercentMode::PercentageOf => "PERCENTAGE_OF",
            PercentMode::AddPercent => "ADD_PERCENT",
            PercentMode::SubtractPercent => "SUBTRACT_PERCENT",
        };
        format!("PercentMode.{name}")
    }
}

/// Thousands/decimal separator style for numeric fields.
#[pyclass(name = "SeparatorStyle", frozen, from_py_object)]
#[derive(Clone, Copy)]
pub struct PySeparatorStyle {
    pub inner: SeparatorStyle,
}

#[pymethods]
impl PySeparatorStyle {
    #[classattr]
    const COMMA_PERIOD: Self = Self { inner: SeparatorStyle::CommaPeriod };
    #[classattr]
    const PERIOD_COMMA: Self = Self { inner: SeparatorStyle::PeriodComma };
    #[classattr]
    const SPACE_PERIOD: Self = Self { inner: SeparatorStyle::SpacePeriod };
    #[classattr]
    const APOSTROPHE_PERIOD: Self = Self { inner: SeparatorStyle::ApostrophePeriod };
    #[classattr]
    const NONE: Self = Self { inner: SeparatorStyle::None };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            SeparatorStyle::CommaPeriod => "COMMA_PERIOD",
            SeparatorStyle::PeriodComma => "PERIOD_COMMA",
            SeparatorStyle::SpacePeriod => "SPACE_PERIOD",
            SeparatorStyle::ApostrophePeriod => "APOSTROPHE_PERIOD",
            SeparatorStyle::None => "NONE",
        };
        format!("SeparatorStyle.{name}")
    }
}

/// Display style for negative numbers (minus sign, red, parentheses).
#[pyclass(name = "NegativeStyle", frozen, from_py_object)]
#[derive(Clone, Copy)]
pub struct PyNegativeStyle {
    pub inner: NegativeStyle,
}

#[pymethods]
impl PyNegativeStyle {
    #[classattr]
    const MINUS_BLACK: Self = Self { inner: NegativeStyle::MinusBlack };
    #[classattr]
    const RED_PARENTHESES: Self = Self { inner: NegativeStyle::RedParentheses };
    #[classattr]
    const BLACK_PARENTHESES: Self = Self { inner: NegativeStyle::BlackParentheses };
    #[classattr]
    const MINUS_RED: Self = Self { inner: NegativeStyle::MinusRed };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            NegativeStyle::MinusBlack => "MINUS_BLACK",
            NegativeStyle::RedParentheses => "RED_PARENTHESES",
            NegativeStyle::BlackParentheses => "BLACK_PARENTHESES",
            NegativeStyle::MinusRed => "MINUS_RED",
        };
        format!("NegativeStyle.{name}")
    }
}

/// Special numeric format for structured strings (ZIP, phone, SSN).
#[pyclass(name = "SpecialFormat", frozen, from_py_object)]
#[derive(Clone, Copy)]
pub struct PySpecialFormat {
    pub inner: SpecialFormat,
}

#[pymethods]
impl PySpecialFormat {
    #[classattr]
    const ZIP_CODE: Self = Self { inner: SpecialFormat::ZipCode };
    #[classattr]
    const ZIP_CODE_PLUS_4: Self = Self { inner: SpecialFormat::ZipCodePlus4 };
    #[classattr]
    const PHONE_NUMBER: Self = Self { inner: SpecialFormat::PhoneNumber };
    #[classattr]
    const SSN: Self = Self { inner: SpecialFormat::SSN };

    fn __repr__(&self) -> String {
        let name = match self.inner {
            SpecialFormat::ZipCode => "ZIP_CODE",
            SpecialFormat::ZipCodePlus4 => "ZIP_CODE_PLUS_4",
            SpecialFormat::PhoneNumber => "PHONE_NUMBER",
            SpecialFormat::SSN => "SSN",
        };
        format!("SpecialFormat.{name}")
    }
}

// ── FieldFormat ───────────────────────────────────────────────────────────

/// Display format applied to a form field value (number, percent, date, time, special, custom).
#[pyclass(name = "FieldFormat", from_py_object)]
#[derive(Clone)]
pub struct PyFieldFormat {
    pub inner: FieldFormat,
}

#[pymethods]
impl PyFieldFormat {
    #[staticmethod]
    #[pyo3(signature = (decimals, separator, negative_style, currency=None))]
    fn number(decimals: usize, separator: &PySeparatorStyle, negative_style: &PyNegativeStyle, currency: Option<String>) -> Self {
        Self { inner: FieldFormat::Number { decimals, separator: separator.inner, negative_style: negative_style.inner, currency } }
    }

    #[staticmethod]
    fn percent(decimals: usize) -> Self {
        Self { inner: FieldFormat::Percent { decimals } }
    }

    #[staticmethod]
    fn date(format: &str) -> Self {
        Self { inner: FieldFormat::Date { format: format.to_string() } }
    }

    #[staticmethod]
    fn time(format: &str) -> Self {
        Self { inner: FieldFormat::Time { format: format.to_string() } }
    }

    #[staticmethod]
    fn special(format_type: &PySpecialFormat) -> Self {
        Self { inner: FieldFormat::Special { format_type: format_type.inner } }
    }

    #[staticmethod]
    fn custom(format_string: &str) -> Self {
        Self { inner: FieldFormat::Custom { format_string: format_string.to_string() } }
    }

    fn __repr__(&self) -> String { format!("FieldFormat({:?})", self.inner) }
}

// ── JavaScriptCalculation ─────────────────────────────────────────────────

/// JavaScript-based calculation definition for a form field.
#[pyclass(name = "JavaScriptCalculation", from_py_object)]
#[derive(Clone)]
pub struct PyJavaScriptCalculation {
    pub inner: JavaScriptCalculation,
}

#[pymethods]
impl PyJavaScriptCalculation {
    #[staticmethod]
    fn simple(operation: &PySimpleOperation, fields: Vec<String>) -> Self {
        Self { inner: JavaScriptCalculation::SimpleCalculate { operation: operation.inner, fields } }
    }

    #[staticmethod]
    fn percent(base_field: &str, percent_field: &str, mode: &PyPercentMode) -> Self {
        Self { inner: JavaScriptCalculation::PercentCalculate {
            base_field: base_field.to_string(),
            percent_field: percent_field.to_string(),
            mode: mode.inner,
        }}
    }

    #[staticmethod]
    #[pyo3(signature = (start_date_field, format, days_field=None))]
    fn date(start_date_field: &str, format: &str, days_field: Option<String>) -> Self {
        Self { inner: JavaScriptCalculation::DateCalculate {
            start_date_field: start_date_field.to_string(),
            days_field,
            format: format.to_string(),
        }}
    }

    #[staticmethod]
    #[pyo3(signature = (field, min=None, max=None))]
    fn range(field: &str, min: Option<f64>, max: Option<f64>) -> Self {
        Self { inner: JavaScriptCalculation::RangeCalculate {
            field: field.to_string(), min, max,
        }}
    }

    #[staticmethod]
    #[pyo3(signature = (field, decimals, sep_style, currency=None))]
    fn number(field: &str, decimals: usize, sep_style: &PySeparatorStyle, currency: Option<String>) -> Self {
        Self { inner: JavaScriptCalculation::NumberCalculate {
            field: field.to_string(), decimals, sep_style: sep_style.inner, currency,
        }}
    }

    #[staticmethod]
    fn custom(script: &str, dependencies: Vec<String>) -> Self {
        Self { inner: JavaScriptCalculation::Custom {
            script: script.to_string(), dependencies,
        }}
    }

    fn __repr__(&self) -> String { format!("JavaScriptCalculation({:?})", self.inner) }
}

// ── CalculationSettings ───────────────────────────────────────────────────

/// Settings for the form calculation engine (recalculation depth, precision, logging).
#[pyclass(name = "CalculationSettings", from_py_object)]
#[derive(Clone)]
pub struct PyCalculationSettings {
    pub inner: CalculationSettings,
}

#[pymethods]
impl PyCalculationSettings {
    #[new]
    #[pyo3(signature = (auto_recalculate=true, max_depth=10, log_events=false, decimal_precision=2))]
    fn new(auto_recalculate: bool, max_depth: usize, log_events: bool, decimal_precision: usize) -> Self {
        Self { inner: CalculationSettings { auto_recalculate, max_depth, log_events, decimal_precision } }
    }

    fn __repr__(&self) -> String {
        format!("CalculationSettings(auto_recalc={}, precision={})",
            self.inner.auto_recalculate, self.inner.decimal_precision)
    }
}

// ── CalculationSummary ────────────────────────────────────────────────────

/// Summary of form field calculations from ``CalculationEngine``.
#[pyclass(name = "CalculationSummary", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyCalculationSummary {
    pub inner: oxidize_pdf::forms::calculations::CalculationSummary,
}

#[pymethods]
impl PyCalculationSummary {
    /// Total number of form fields tracked.
    #[getter]
    fn total_fields(&self) -> usize { self.inner.total_fields }

    /// Number of fields with calculated values.
    #[getter]
    fn calculated_fields(&self) -> usize { self.inner.calculated_fields }

    /// Number of dependency relationships between fields.
    #[getter]
    fn dependencies(&self) -> usize { self.inner.dependencies }

    /// Ordered list of field names in calculation order.
    #[getter]
    fn calculation_order(&self) -> Vec<String> { self.inner.calculation_order.clone() }

    fn __repr__(&self) -> String {
        format!(
            "CalculationSummary(total={}, calculated={}, deps={})",
            self.inner.total_fields, self.inner.calculated_fields, self.inner.dependencies,
        )
    }
}

// ── CalculationSystemSummary ──────────────────────────────────────────────

/// Summary of a ``FormCalculationSystem`` combining calculations, formats, and events.
#[pyclass(name = "CalculationSystemSummary", frozen, from_py_object)]
#[derive(Clone)]
pub struct PyCalculationSystemSummary {
    pub inner: oxidize_pdf::forms::calculation_system::CalculationSystemSummary,
}

#[pymethods]
impl PyCalculationSystemSummary {
    /// Total number of fields in the system.
    #[getter]
    fn total_fields(&self) -> usize { self.inner.total_fields }

    /// Number of fields with JavaScript calculations.
    #[getter]
    fn js_calculations(&self) -> usize { self.inner.js_calculations }

    /// Number of fields with formatting rules.
    #[getter]
    fn formatted_fields(&self) -> usize { self.inner.formatted_fields }

    /// Number of calculation events that have been logged.
    #[getter]
    fn events_logged(&self) -> usize { self.inner.events_logged }

    fn __repr__(&self) -> String {
        format!(
            "CalculationSystemSummary(total={}, js_calcs={}, formats={}, events={})",
            self.inner.total_fields,
            self.inner.js_calculations,
            self.inner.formatted_fields,
            self.inner.events_logged,
        )
    }
}

// ── CalculationEngine ─────────────────────────────────────────────────────

/// Evaluates field dependencies and recalculates form field values.
#[pyclass(name = "CalculationEngine")]
pub struct PyCalculationEngine {
    pub inner: CalculationEngine,
}

#[pymethods]
impl PyCalculationEngine {
    #[new]
    fn new() -> Self { Self { inner: CalculationEngine::new() } }

    fn set_field_value(&mut self, name: &str, value: &PyFieldValue) {
        self.inner.set_field_value(name, value.inner.clone());
    }

    fn get_field_value(&self, name: &str) -> Option<PyFieldValue> {
        self.inner.get_field_value(name).map(|v| PyFieldValue { inner: v.clone() })
    }

    fn recalculate_all(&mut self) -> PyResult<()> {
        self.inner.recalculate_all().map_err(pdf_err_to_py)
    }

    fn get_summary(&self) -> PyCalculationSummary {
        PyCalculationSummary { inner: self.inner.get_summary() }
    }

    fn __repr__(&self) -> String { "CalculationEngine(...)".to_string() }
}

// ── FormCalculationSystem ─────────────────────────────────────────────────

/// High-level system combining calculation engine with field formats and JavaScript calculations.
#[pyclass(name = "FormCalculationSystem")]
pub struct PyFormCalculationSystem {
    pub inner: FormCalculationSystem,
}

#[pymethods]
impl PyFormCalculationSystem {
    #[new]
    #[pyo3(signature = (settings=None))]
    fn new(settings: Option<&PyCalculationSettings>) -> Self {
        match settings {
            Some(s) => Self { inner: FormCalculationSystem::with_settings(s.inner.clone()) },
            None => Self { inner: FormCalculationSystem::new() },
        }
    }

    fn set_field_value(&mut self, name: &str, value: &PyFieldValue) -> PyResult<()> {
        self.inner.set_field_value(name, value.inner.clone()).map_err(pdf_err_to_py)
    }

    fn add_js_calculation(&mut self, field_name: &str, calculation: &PyJavaScriptCalculation) -> PyResult<()> {
        self.inner.add_js_calculation(field_name, calculation.inner.clone()).map_err(pdf_err_to_py)
    }

    fn set_field_format(&mut self, field_name: &str, format: &PyFieldFormat) {
        self.inner.set_field_format(field_name, format.inner.clone());
    }

    fn get_summary(&self) -> PyCalculationSystemSummary {
        PyCalculationSystemSummary { inner: self.inner.get_summary() }
    }

    fn __repr__(&self) -> String { "FormCalculationSystem(...)".to_string() }
}

// ── Group D — Appearance ──────────────────────────────────────────────────

/// Visual state of a widget appearance stream (normal, rollover, down).
#[pyclass(name = "AppearanceState", frozen, from_py_object)]
#[derive(Clone, Copy)]
pub struct PyAppearanceState {
    pub inner: AppearanceState,
}

#[pymethods]
impl PyAppearanceState {
    #[classattr]
    const NORMAL: Self = Self { inner: AppearanceState::Normal };
    #[classattr]
    const ROLLOVER: Self = Self { inner: AppearanceState::Rollover };
    #[classattr]
    const DOWN: Self = Self { inner: AppearanceState::Down };

    #[getter]
    fn pdf_name(&self) -> &str { self.inner.pdf_name() }
}

// ── AppearanceStream ──────────────────────────────────────────────────────

/// Raw content stream for a widget appearance, with bounding box.
#[pyclass(name = "AppearanceStream", from_py_object)]
#[derive(Clone)]
pub struct PyAppearanceStream {
    pub inner: AppearanceStream,
}

#[pymethods]
impl PyAppearanceStream {
    #[new]
    fn new(content: Vec<u8>, bbox: [f64; 4]) -> Self {
        Self { inner: AppearanceStream::new(content, bbox) }
    }

    #[getter]
    fn content(&self) -> &[u8] { &self.inner.content }

    #[getter]
    fn bbox(&self) -> Vec<f64> { self.inner.bbox.to_vec() }

    fn __repr__(&self) -> String {
        format!("AppearanceStream(bbox={:?})", self.inner.bbox)
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
    m.add_class::<PyValidationResult>()?;
    m.add_class::<PyFormValidationSystem>()?;
    // Group A
    m.add_class::<PyFormData>()?;
    m.add_class::<PyWidget>()?;
    m.add_class::<PyFieldOptions>()?;
    m.add_class::<PyPushButton>()?;
    m.add_class::<PyAcroForm>()?;
    m.add_class::<PyFormManager>()?;
    // Group B
    m.add_class::<PySpecialFormatType>()?;
    m.add_class::<PyFieldAction>()?;
    m.add_class::<PyFieldActions>()?;
    m.add_class::<PyActionSettings>()?;
    m.add_class::<PyFieldActionSystem>()?;
    // Group C
    m.add_class::<PySimpleOperation>()?;
    m.add_class::<PyPercentMode>()?;
    m.add_class::<PySeparatorStyle>()?;
    m.add_class::<PyNegativeStyle>()?;
    m.add_class::<PySpecialFormat>()?;
    m.add_class::<PyFieldFormat>()?;
    m.add_class::<PyJavaScriptCalculation>()?;
    m.add_class::<PyCalculationSettings>()?;
    m.add_class::<PyCalculationSummary>()?;
    m.add_class::<PyCalculationSystemSummary>()?;
    m.add_class::<PyCalculationEngine>()?;
    m.add_class::<PyFormCalculationSystem>()?;
    // Group D
    m.add_class::<PyAppearanceState>()?;
    m.add_class::<PyAppearanceStream>()?;
    Ok(())
}
