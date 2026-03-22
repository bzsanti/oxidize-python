"""Tests for Feature 57: Form Validation."""
import pytest


def test_field_value_number():
    from oxidize_pdf import FieldValue

    fv = FieldValue.number(42.5)
    assert fv is not None
    assert fv.to_number() == pytest.approx(42.5)


def test_field_value_text():
    from oxidize_pdf import FieldValue

    fv = FieldValue.text("hello")
    assert fv.to_text() == "hello"


def test_field_value_boolean_true():
    from oxidize_pdf import FieldValue

    fv = FieldValue.boolean(True)
    assert fv.to_number() == pytest.approx(1.0)


def test_field_value_boolean_false():
    from oxidize_pdf import FieldValue

    fv = FieldValue.boolean(False)
    assert fv.to_number() == pytest.approx(0.0)


def test_field_value_empty():
    from oxidize_pdf import FieldValue

    fv = FieldValue.empty()
    assert fv.to_number() == pytest.approx(0.0)
    assert fv.to_text() == ""


def test_validation_rule_required():
    from oxidize_pdf import ValidationRule

    rule = ValidationRule.required()
    assert rule is not None


def test_validation_rule_range():
    from oxidize_pdf import ValidationRule

    rule = ValidationRule.range(0.0, 100.0)
    assert rule is not None


def test_validation_rule_range_open():
    from oxidize_pdf import ValidationRule

    rule = ValidationRule.range(min=0.0)
    assert rule is not None

    rule2 = ValidationRule.range(max=100.0)
    assert rule2 is not None


def test_validation_rule_length():
    from oxidize_pdf import ValidationRule

    rule = ValidationRule.length(1, 50)
    assert rule is not None


def test_validation_rule_pattern():
    from oxidize_pdf import ValidationRule

    rule = ValidationRule.pattern(r"^\d{5}$")
    assert rule is not None


def test_validation_rule_email():
    from oxidize_pdf import ValidationRule

    rule = ValidationRule.email()
    assert rule is not None


def test_validation_rule_url():
    from oxidize_pdf import ValidationRule

    rule = ValidationRule.url()
    assert rule is not None


def test_field_validator_new():
    from oxidize_pdf import FieldValidator

    fv = FieldValidator("myField")
    assert fv is not None


def test_field_validator_add_rule():
    from oxidize_pdf import FieldValidator, ValidationRule

    fv = FieldValidator("myField")
    fv.add_rule(ValidationRule.required())
    fv.add_rule(ValidationRule.length(1, 100))


def test_form_validation_system_new():
    from oxidize_pdf import FormValidationSystem

    fvs = FormValidationSystem()
    assert fvs is not None


def test_form_validation_system_add_validator():
    from oxidize_pdf import FieldValidator, FormValidationSystem, ValidationRule

    fvs = FormValidationSystem()
    validator = FieldValidator("name")
    validator.add_rule(ValidationRule.required())
    fvs.add_validator(validator)


def test_form_validation_system_validate_field_valid():
    from oxidize_pdf import FieldValidator, FieldValue, FormValidationSystem, ValidationResult, ValidationRule

    fvs = FormValidationSystem()
    validator = FieldValidator("age")
    validator.add_rule(ValidationRule.range(0.0, 120.0))
    fvs.add_validator(validator)

    result = fvs.validate_field("age", FieldValue.number(25.0))
    assert isinstance(result, ValidationResult)
    assert result.field_name == "age"
    assert result.is_valid is True
    assert result.errors == []


def test_form_validation_system_validate_field_invalid():
    from oxidize_pdf import FieldValidator, FieldValue, FormValidationSystem, ValidationResult, ValidationRule

    fvs = FormValidationSystem()
    validator = FieldValidator("age")
    validator.add_rule(ValidationRule.range(0.0, 120.0))
    fvs.add_validator(validator)

    result = fvs.validate_field("age", FieldValue.number(200.0))
    assert isinstance(result, ValidationResult)
    assert result.field_name == "age"
    assert result.is_valid is False
    assert len(result.errors) > 0


def test_form_validation_system_unknown_field_is_valid():
    from oxidize_pdf import FieldValue, FormValidationSystem

    fvs = FormValidationSystem()
    result = fvs.validate_field("unknown_field", FieldValue.text("anything"))
    assert result.is_valid is True
