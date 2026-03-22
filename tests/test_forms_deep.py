"""Tests for F76 — Forms Deep: AcroForm, FormManager, FieldActions, Calculations, Appearance."""

import pytest
from oxidize_pdf import (
    # Existing types
    FieldValue,
    TextField,
    CheckBox,
    RadioButton,
    ComboBox,
    ListBox,
    Point,
    Rectangle,
    FieldValidator,
    ValidationRule,
    FormValidationSystem,
)

# New F76 types — Group A: Form Management
from oxidize_pdf import (
    FormData,
    Widget,
    FieldOptions,
    PushButton,
    AcroForm,
    FormManager,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Group A — Form Management
# ═══════════════════════════════════════════════════════════════════════════════


class TestFormData:
    def test_create(self):
        fd = FormData()
        assert fd is not None

    def test_set_and_get_value(self):
        fd = FormData()
        fd.set_value("name", "John")
        assert fd.get_value("name") == "John"

    def test_get_missing_returns_none(self):
        fd = FormData()
        assert fd.get_value("missing") is None

    def test_overwrite_value(self):
        fd = FormData()
        fd.set_value("name", "John")
        fd.set_value("name", "Jane")
        assert fd.get_value("name") == "Jane"

    def test_multiple_values(self):
        fd = FormData()
        fd.set_value("first", "A")
        fd.set_value("second", "B")
        assert fd.get_value("first") == "A"
        assert fd.get_value("second") == "B"

    def test_repr(self):
        fd = FormData()
        assert "FormData" in repr(fd)


class TestWidget:
    def test_create(self):
        rect = Rectangle(Point(0.0, 0.0), Point(100.0, 20.0))
        w = Widget(rect)
        assert w is not None

    def test_repr(self):
        rect = Rectangle(Point(0.0, 0.0), Point(100.0, 20.0))
        w = Widget(rect)
        assert "Widget" in repr(w)


class TestFieldOptions:
    def test_default(self):
        fo = FieldOptions()
        assert fo.read_only is False
        assert fo.required is False
        assert fo.no_export is False

    def test_read_only(self):
        fo = FieldOptions(read_only=True)
        assert fo.read_only is True

    def test_required(self):
        fo = FieldOptions(required=True)
        assert fo.required is True

    def test_no_export(self):
        fo = FieldOptions(no_export=True)
        assert fo.no_export is True

    def test_combined(self):
        fo = FieldOptions(read_only=True, required=True)
        assert fo.read_only is True
        assert fo.required is True
        assert fo.no_export is False

    def test_repr(self):
        fo = FieldOptions()
        assert "FieldOptions" in repr(fo)


class TestPushButton:
    def test_create(self):
        pb = PushButton("submit")
        assert pb is not None

    def test_with_caption(self):
        pb = PushButton("submit").with_caption("Submit Form")
        assert pb is not None

    def test_repr(self):
        pb = PushButton("submit")
        r = repr(pb)
        assert "PushButton" in r
        assert "submit" in r


class TestAcroForm:
    def test_create(self):
        af = AcroForm()
        assert af is not None

    def test_need_appearances_default(self):
        af = AcroForm()
        assert af.need_appearances is True

    def test_sig_flags_default(self):
        af = AcroForm()
        assert af.sig_flags is None

    def test_field_count_default(self):
        af = AcroForm()
        assert af.field_count == 0

    def test_repr(self):
        af = AcroForm()
        assert "AcroForm" in repr(af)


class TestFormManager:
    def _make_widget(self):
        return Widget(Rectangle(Point(0.0, 0.0), Point(200.0, 20.0)))

    def test_create(self):
        fm = FormManager()
        assert fm is not None
        assert fm.field_count == 0

    def test_add_text_field(self):
        fm = FormManager()
        fm.add_text_field(TextField("name"), self._make_widget())
        assert fm.field_count == 1

    def test_add_text_field_with_options(self):
        fm = FormManager()
        opts = FieldOptions(required=True)
        fm.add_text_field(TextField("name"), self._make_widget(), opts)
        assert fm.field_count == 1

    def test_add_combo_box(self):
        fm = FormManager()
        combo = ComboBox("color").add_option("r", "Red").add_option("g", "Green")
        fm.add_combo_box(combo, self._make_widget())
        assert fm.field_count == 1

    def test_add_list_box(self):
        fm = FormManager()
        lb = ListBox("items").add_option("a", "Alpha").add_option("b", "Beta")
        fm.add_list_box(lb, self._make_widget())
        assert fm.field_count == 1

    def test_add_checkbox(self):
        fm = FormManager()
        fm.add_checkbox(CheckBox("agree"), self._make_widget())
        assert fm.field_count == 1

    def test_add_push_button(self):
        fm = FormManager()
        fm.add_push_button(PushButton("submit").with_caption("Go"), self._make_widget())
        assert fm.field_count == 1

    def test_add_radio_button(self):
        fm = FormManager()
        radio = RadioButton("choice").add_option("a", "Option A").add_option("b", "Option B")
        widgets = [self._make_widget(), self._make_widget()]
        fm.add_radio_button(radio, widgets)
        assert fm.field_count == 1

    def test_multiple_fields(self):
        fm = FormManager()
        fm.add_text_field(TextField("first"), self._make_widget())
        fm.add_text_field(TextField("last"), self._make_widget())
        fm.add_checkbox(CheckBox("agree"), self._make_widget())
        assert fm.field_count == 3

    def test_get_acro_form(self):
        fm = FormManager()
        fm.add_text_field(TextField("name"), self._make_widget())
        af = fm.get_acro_form()
        assert isinstance(af, AcroForm)
        assert af.field_count == 1

    def test_repr(self):
        fm = FormManager()
        assert "FormManager" in repr(fm)

    def test_add_duplicate_field_names(self):
        """FormManager replaces fields with same name — core behavior."""
        fm = FormManager()
        fm.add_text_field(TextField("name"), self._make_widget())
        fm.add_text_field(TextField("name"), self._make_widget())
        # Core replaces fields with same name, not duplicates
        assert fm.field_count == 1


class TestValidationResultType:
    def test_validate_returns_dedicated_type(self):
        from oxidize_pdf import ValidationResult
        fvs = FormValidationSystem()
        validator = FieldValidator("score")
        validator.add_rule(ValidationRule.range(0.0, 100.0))
        fvs.add_validator(validator)
        result = fvs.validate_field("score", FieldValue.number(50.0))
        assert isinstance(result, ValidationResult)
        assert result.field_name == "score"
        assert result.is_valid is True
        assert result.errors == []
        assert "ValidationResult" in repr(result)

    def test_validation_result_with_errors(self):
        from oxidize_pdf import ValidationResult
        fvs = FormValidationSystem()
        validator = FieldValidator("score")
        validator.add_rule(ValidationRule.range(0.0, 100.0))
        fvs.add_validator(validator)
        result = fvs.validate_field("score", FieldValue.number(999.0))
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.errors) > 0


class TestValidationRuleRepr:
    def test_required_repr(self):
        r = repr(ValidationRule.required())
        assert "required" in r.lower()

    def test_range_repr(self):
        r = repr(ValidationRule.range(0.0, 100.0))
        assert "range" in r.lower()
        assert "0" in r

    def test_length_repr(self):
        r = repr(ValidationRule.length(1, 50))
        assert "length" in r.lower()

    def test_pattern_repr(self):
        r = repr(ValidationRule.pattern(r"\d+"))
        assert "pattern" in r.lower()

    def test_email_repr(self):
        r = repr(ValidationRule.email())
        assert "email" in r.lower()

    def test_url_repr(self):
        r = repr(ValidationRule.url())
        assert "url" in r.lower()


class TestFormDataRepr:
    def test_repr_shows_count(self):
        fd = FormData()
        assert "entries=0" in repr(fd)
        fd.set_value("a", "1")
        assert "entries=1" in repr(fd)


class TestWidgetRepr:
    def test_repr_shows_rect(self):
        rect = Rectangle(Point(10.0, 20.0), Point(200.0, 50.0))
        w = Widget(rect)
        r = repr(w)
        assert "Widget" in r
        assert "10.0" in r
        assert "200.0" in r


class TestFieldOptionsRepr:
    def test_repr_shows_flags(self):
        fo = FieldOptions(read_only=True, required=True)
        r = repr(fo)
        assert "read_only=true" in r
        assert "required=true" in r


# ═══════════════════════════════════════════════════════════════════════════════
# Group B — Field Actions
# ═══════════════════════════════════════════════════════════════════════════════


from oxidize_pdf import (
    FieldAction,
    FieldActions,
    SpecialFormatType,
    ActionSettings,
    FieldActionSystem,
)


class TestSpecialFormatType:
    def test_zip_code(self):
        assert SpecialFormatType.ZIP_CODE is not None

    def test_zip_plus_4(self):
        assert SpecialFormatType.ZIP_PLUS_4 is not None

    def test_phone(self):
        assert SpecialFormatType.PHONE is not None

    def test_ssn(self):
        assert SpecialFormatType.SSN is not None


class TestFieldAction:
    def test_javascript(self):
        a = FieldAction.javascript("alert('hi');")
        assert a is not None

    def test_javascript_async(self):
        a = FieldAction.javascript("fetch()", async_exec=True)
        assert a is not None

    def test_format_number(self):
        a = FieldAction.format_number(2, "USD")
        assert a is not None

    def test_format_number_no_currency(self):
        a = FieldAction.format_number(2)
        assert a is not None

    def test_format_percent(self):
        a = FieldAction.format_percent(1)
        assert a is not None

    def test_format_date(self):
        a = FieldAction.format_date("mm/dd/yyyy")
        assert a is not None

    def test_format_time(self):
        a = FieldAction.format_time("HH:mm")
        assert a is not None

    def test_format_special(self):
        a = FieldAction.format_special(SpecialFormatType.ZIP_CODE)
        assert a is not None

    def test_format_custom(self):
        a = FieldAction.format_custom("AFSpecial_Format(0);")
        assert a is not None

    def test_validate_range(self):
        a = FieldAction.validate_range(0.0, 100.0)
        assert a is not None

    def test_validate_range_partial(self):
        a = FieldAction.validate_range(min=0.0)
        assert a is not None

    def test_validate_custom(self):
        a = FieldAction.validate_custom("script")
        assert a is not None

    def test_calculate(self):
        a = FieldAction.calculate("a + b")
        assert a is not None

    def test_submit_form(self):
        a = FieldAction.submit_form("https://example.com", ["f1", "f2"], False)
        assert a is not None

    def test_reset_form(self):
        a = FieldAction.reset_form(["f1"], False)
        assert a is not None

    def test_import_data(self):
        a = FieldAction.import_data("/path/to/data.fdf")
        assert a is not None

    def test_set_field(self):
        a = FieldAction.set_field("target", FieldValue.number(42.0))
        assert a is not None

    def test_show_hide(self):
        a = FieldAction.show_hide(["field1", "field2"], True)
        assert a is not None

    def test_play_sound(self):
        a = FieldAction.play_sound("beep", 0.5)
        assert a is not None

    def test_custom(self):
        a = FieldAction.custom("myAction", {"key": "value"})
        assert a is not None

    def test_repr(self):
        a = FieldAction.javascript("x")
        assert "FieldAction" in repr(a)


class TestFieldActions:
    def test_default(self):
        fa = FieldActions()
        assert fa is not None

    def test_with_on_focus(self):
        action = FieldAction.javascript("onFocus();")
        fa = FieldActions(on_focus=action)
        assert fa is not None

    def test_with_multiple_slots(self):
        fa = FieldActions(
            on_focus=FieldAction.javascript("focus();"),
            on_blur=FieldAction.javascript("blur();"),
            on_validate=FieldAction.validate_range(0.0, 100.0),
        )
        assert fa is not None

    def test_getter_on_focus(self):
        action = FieldAction.javascript("onFocus();")
        fa = FieldActions(on_focus=action)
        assert fa.on_focus is not None
        assert fa.on_blur is None

    def test_getter_all_none(self):
        fa = FieldActions()
        assert fa.on_focus is None
        assert fa.on_blur is None
        assert fa.on_format is None
        assert fa.on_keystroke is None
        assert fa.on_calculate is None
        assert fa.on_validate is None
        assert fa.on_mouse_enter is None
        assert fa.on_mouse_exit is None
        assert fa.on_mouse_down is None
        assert fa.on_mouse_up is None

    def test_getter_all_set(self):
        js = FieldAction.javascript("x;")
        fa = FieldActions(
            on_focus=js, on_blur=js, on_format=js, on_keystroke=js,
            on_calculate=js, on_validate=js, on_mouse_enter=js,
            on_mouse_exit=js, on_mouse_down=js, on_mouse_up=js,
        )
        assert fa.on_focus is not None
        assert fa.on_mouse_up is not None

    def test_repr_count(self):
        fa = FieldActions()
        assert "actions_set=0" in repr(fa)
        fa2 = FieldActions(
            on_focus=FieldAction.javascript("x;"),
            on_blur=FieldAction.javascript("y;"),
        )
        assert "actions_set=2" in repr(fa2)


class TestActionSettings:
    def test_default(self):
        s = ActionSettings()
        assert s is not None

    def test_custom(self):
        s = ActionSettings(enable_javascript=False, log_events=True)
        assert s is not None

    def test_repr_shows_state(self):
        s = ActionSettings()
        r = repr(s)
        assert "ActionSettings" in r
        assert "js=" in r
        assert "log=" in r


class TestFieldActionSystem:
    def test_create(self):
        fas = FieldActionSystem()
        assert fas is not None

    def test_create_with_settings(self):
        settings = ActionSettings(log_events=True)
        fas = FieldActionSystem(settings=settings)
        assert fas is not None

    def test_register_and_focus(self):
        fas = FieldActionSystem()
        actions = FieldActions(on_focus=FieldAction.javascript("focused();"))
        fas.register_field_actions("name", actions)
        fas.handle_focus("name")
        assert fas.get_focused_field() == "name"

    def test_blur(self):
        fas = FieldActionSystem()
        actions = FieldActions(on_blur=FieldAction.javascript("blurred();"))
        fas.register_field_actions("name", actions)
        fas.handle_focus("name")
        fas.handle_blur("name")
        assert fas.get_focused_field() is None

    def test_handle_validate(self):
        fas = FieldActionSystem()
        actions = FieldActions(on_validate=FieldAction.validate_range(0.0, 100.0))
        fas.register_field_actions("score", actions)
        result = fas.handle_validate("score", FieldValue.number(50.0))
        assert isinstance(result, bool)

    def test_handle_keystroke(self):
        fas = FieldActionSystem()
        actions = FieldActions(on_keystroke=FieldAction.javascript("true;"))
        fas.register_field_actions("input", actions)
        result = fas.handle_keystroke("input", "a", "")
        assert isinstance(result, bool)

    def test_event_history(self):
        fas = FieldActionSystem()
        actions = FieldActions(on_focus=FieldAction.javascript("x;"))
        fas.register_field_actions("f1", actions)
        fas.handle_focus("f1")
        assert fas.event_history_count >= 0

    def test_clear_event_history(self):
        fas = FieldActionSystem()
        fas.clear_event_history()
        assert fas.event_history_count == 0

    def test_focus_unregistered_field(self):
        """Focusing an unregistered field should not raise (no action to execute)."""
        fas = FieldActionSystem()
        fas.handle_focus("nonexistent")
        assert fas.get_focused_field() == "nonexistent"

    def test_blur_without_focus(self):
        """Blurring without prior focus should not raise."""
        fas = FieldActionSystem()
        fas.handle_blur("nonexistent")
        assert fas.get_focused_field() is None

    def test_validate_unregistered_field(self):
        """Validating an unregistered field should succeed (no validation rules)."""
        fas = FieldActionSystem()
        result = fas.handle_validate("unknown", FieldValue.number(50.0))
        assert isinstance(result, bool)

    def test_keystroke_unregistered_field(self):
        """Keystroke on an unregistered field should succeed."""
        fas = FieldActionSystem()
        result = fas.handle_keystroke("unknown", "x", "current")
        assert isinstance(result, bool)

    def test_repr(self):
        fas = FieldActionSystem()
        assert "FieldActionSystem" in repr(fas)


# ═══════════════════════════════════════════════════════════════════════════════
# Group C — Calculations
# ═══════════════════════════════════════════════════════════════════════════════


from oxidize_pdf import (
    SimpleOperation,
    CalculationEngine,
    FormCalculationSystem,
    JavaScriptCalculation,
    PercentMode,
    SeparatorStyle,
    NegativeStyle,
    SpecialFormat,
    FieldFormat,
    CalculationSettings,
    CalculationSummary,
    CalculationSystemSummary,
)


class TestSimpleOperation:
    def test_sum(self):
        assert SimpleOperation.SUM is not None

    def test_product(self):
        assert SimpleOperation.PRODUCT is not None

    def test_average(self):
        assert SimpleOperation.AVERAGE is not None

    def test_minimum(self):
        assert SimpleOperation.MINIMUM is not None

    def test_maximum(self):
        assert SimpleOperation.MAXIMUM is not None


class TestPercentMode:
    def test_percent_of(self):
        assert PercentMode.PERCENT_OF is not None

    def test_percentage_of(self):
        assert PercentMode.PERCENTAGE_OF is not None

    def test_add_percent(self):
        assert PercentMode.ADD_PERCENT is not None

    def test_subtract_percent(self):
        assert PercentMode.SUBTRACT_PERCENT is not None


class TestSeparatorStyle:
    def test_comma_period(self):
        assert SeparatorStyle.COMMA_PERIOD is not None

    def test_period_comma(self):
        assert SeparatorStyle.PERIOD_COMMA is not None

    def test_space_period(self):
        assert SeparatorStyle.SPACE_PERIOD is not None

    def test_apostrophe_period(self):
        assert SeparatorStyle.APOSTROPHE_PERIOD is not None

    def test_none(self):
        assert SeparatorStyle.NONE is not None


class TestNegativeStyle:
    def test_minus_black(self):
        assert NegativeStyle.MINUS_BLACK is not None

    def test_red_parentheses(self):
        assert NegativeStyle.RED_PARENTHESES is not None

    def test_black_parentheses(self):
        assert NegativeStyle.BLACK_PARENTHESES is not None

    def test_minus_red(self):
        assert NegativeStyle.MINUS_RED is not None


class TestSpecialFormat:
    def test_zip_code(self):
        assert SpecialFormat.ZIP_CODE is not None

    def test_zip_code_plus_4(self):
        assert SpecialFormat.ZIP_CODE_PLUS_4 is not None

    def test_phone_number(self):
        assert SpecialFormat.PHONE_NUMBER is not None

    def test_ssn(self):
        assert SpecialFormat.SSN is not None


class TestEnumReprs:
    """Verify all frozen enum types have informative __repr__."""

    def test_special_format_type_repr(self):
        assert repr(SpecialFormatType.ZIP_CODE) == "SpecialFormatType.ZIP_CODE"

    def test_simple_operation_repr(self):
        assert repr(SimpleOperation.SUM) == "SimpleOperation.SUM"

    def test_percent_mode_repr(self):
        assert repr(PercentMode.PERCENT_OF) == "PercentMode.PERCENT_OF"

    def test_separator_style_repr(self):
        assert repr(SeparatorStyle.COMMA_PERIOD) == "SeparatorStyle.COMMA_PERIOD"

    def test_negative_style_repr(self):
        assert repr(NegativeStyle.MINUS_BLACK) == "NegativeStyle.MINUS_BLACK"

    def test_special_format_repr(self):
        assert repr(SpecialFormat.ZIP_CODE) == "SpecialFormat.ZIP_CODE"


class TestFieldFormat:
    def test_number(self):
        f = FieldFormat.number(2, SeparatorStyle.COMMA_PERIOD, NegativeStyle.MINUS_BLACK)
        assert f is not None

    def test_number_with_currency(self):
        f = FieldFormat.number(2, SeparatorStyle.COMMA_PERIOD, NegativeStyle.MINUS_BLACK, "USD")
        assert f is not None

    def test_percent(self):
        f = FieldFormat.percent(1)
        assert f is not None

    def test_date(self):
        f = FieldFormat.date("mm/dd/yyyy")
        assert f is not None

    def test_time(self):
        f = FieldFormat.time("HH:mm")
        assert f is not None

    def test_special(self):
        f = FieldFormat.special(SpecialFormat.PHONE_NUMBER)
        assert f is not None

    def test_custom(self):
        f = FieldFormat.custom("###-####")
        assert f is not None

    def test_repr(self):
        f = FieldFormat.number(2, SeparatorStyle.COMMA_PERIOD, NegativeStyle.MINUS_BLACK)
        assert "FieldFormat" in repr(f)


class TestJavaScriptCalculation:
    def test_simple_sum(self):
        c = JavaScriptCalculation.simple(SimpleOperation.SUM, ["a", "b"])
        assert c is not None

    def test_simple_average(self):
        c = JavaScriptCalculation.simple(SimpleOperation.AVERAGE, ["x", "y", "z"])
        assert c is not None

    def test_percent(self):
        c = JavaScriptCalculation.percent("base", "pct", PercentMode.PERCENT_OF)
        assert c is not None

    def test_date(self):
        c = JavaScriptCalculation.date("start", "mm/dd/yyyy")
        assert c is not None

    def test_date_with_days_field(self):
        c = JavaScriptCalculation.date("start", "mm/dd/yyyy", days_field="days")
        assert c is not None

    def test_range(self):
        c = JavaScriptCalculation.range("value", 0.0, 100.0)
        assert c is not None

    def test_number(self):
        c = JavaScriptCalculation.number("price", 2, SeparatorStyle.COMMA_PERIOD)
        assert c is not None

    def test_number_with_currency(self):
        c = JavaScriptCalculation.number("price", 2, SeparatorStyle.COMMA_PERIOD, "EUR")
        assert c is not None

    def test_custom(self):
        c = JavaScriptCalculation.custom("event.value = 42;", ["dep1"])
        assert c is not None

    def test_repr(self):
        c = JavaScriptCalculation.simple(SimpleOperation.SUM, ["a"])
        assert "JavaScriptCalculation" in repr(c)


class TestCalculationSettings:
    def test_default(self):
        cs = CalculationSettings()
        assert cs is not None

    def test_custom(self):
        cs = CalculationSettings(
            auto_recalculate=False,
            max_depth=5,
            log_events=True,
            decimal_precision=4,
        )
        assert cs is not None

    def test_repr_shows_state(self):
        cs = CalculationSettings()
        r = repr(cs)
        assert "CalculationSettings" in r
        assert "auto_recalc=" in r
        assert "precision=" in r


class TestCalculationEngine:
    def test_create(self):
        ce = CalculationEngine()
        assert ce is not None

    def test_set_and_get_field_value(self):
        ce = CalculationEngine()
        ce.set_field_value("a", FieldValue.number(10.0))
        val = ce.get_field_value("a")
        assert val is not None
        assert val.to_number() == 10.0

    def test_get_missing_value(self):
        ce = CalculationEngine()
        assert ce.get_field_value("missing") is None

    def test_recalculate_all(self):
        ce = CalculationEngine()
        ce.set_field_value("a", FieldValue.number(5.0))
        ce.recalculate_all()

    def test_get_summary(self):
        ce = CalculationEngine()
        summary = ce.get_summary()
        assert isinstance(summary, CalculationSummary)
        assert isinstance(summary.total_fields, int)
        assert isinstance(summary.calculated_fields, int)
        assert isinstance(summary.dependencies, int)
        assert isinstance(summary.calculation_order, list)

    def test_get_summary_repr(self):
        ce = CalculationEngine()
        summary = ce.get_summary()
        assert "CalculationSummary" in repr(summary)

    def test_repr(self):
        ce = CalculationEngine()
        assert "CalculationEngine" in repr(ce)


class TestFormCalculationSystem:
    def test_create(self):
        fcs = FormCalculationSystem()
        assert fcs is not None

    def test_create_with_settings(self):
        settings = CalculationSettings(auto_recalculate=True)
        fcs = FormCalculationSystem(settings=settings)
        assert fcs is not None

    def test_set_field_value(self):
        fcs = FormCalculationSystem()
        fcs.set_field_value("price", FieldValue.number(19.99))

    def test_add_js_calculation(self):
        fcs = FormCalculationSystem()
        fcs.set_field_value("a", FieldValue.number(10.0))
        fcs.set_field_value("b", FieldValue.number(20.0))
        calc = JavaScriptCalculation.simple(SimpleOperation.SUM, ["a", "b"])
        fcs.add_js_calculation("total", calc)

    def test_set_field_format(self):
        fcs = FormCalculationSystem()
        fmt = FieldFormat.number(2, SeparatorStyle.COMMA_PERIOD, NegativeStyle.MINUS_BLACK)
        fcs.set_field_format("price", fmt)

    def test_get_summary(self):
        fcs = FormCalculationSystem()
        summary = fcs.get_summary()
        assert isinstance(summary, CalculationSystemSummary)
        assert isinstance(summary.total_fields, int)
        assert isinstance(summary.js_calculations, int)
        assert isinstance(summary.formatted_fields, int)
        assert isinstance(summary.events_logged, int)

    def test_get_summary_repr(self):
        fcs = FormCalculationSystem()
        summary = fcs.get_summary()
        assert "CalculationSystemSummary" in repr(summary)

    def test_repr(self):
        fcs = FormCalculationSystem()
        assert "FormCalculationSystem" in repr(fcs)


# ═══════════════════════════════════════════════════════════════════════════════
# Group D — Appearance
# ═══════════════════════════════════════════════════════════════════════════════


from oxidize_pdf import (
    AppearanceState,
    AppearanceStream,
)


class TestAppearanceState:
    def test_normal(self):
        assert AppearanceState.NORMAL is not None

    def test_rollover(self):
        assert AppearanceState.ROLLOVER is not None

    def test_down(self):
        assert AppearanceState.DOWN is not None

    def test_pdf_name_normal(self):
        assert AppearanceState.NORMAL.pdf_name == "N"

    def test_pdf_name_rollover(self):
        assert AppearanceState.ROLLOVER.pdf_name == "R"

    def test_pdf_name_down(self):
        assert AppearanceState.DOWN.pdf_name == "D"


class TestAppearanceStream:
    def test_create(self):
        s = AppearanceStream(b"BT /F1 12 Tf (Hello) Tj ET", [0.0, 0.0, 100.0, 20.0])
        assert s is not None

    def test_content_property(self):
        content = b"BT /F1 12 Tf ET"
        s = AppearanceStream(content, [0.0, 0.0, 100.0, 20.0])
        assert s.content == content

    def test_bbox_property(self):
        s = AppearanceStream(b"data", [10.0, 20.0, 200.0, 50.0])
        bbox = s.bbox
        assert len(bbox) == 4
        assert bbox[0] == 10.0
        assert bbox[3] == 50.0

    def test_repr(self):
        s = AppearanceStream(b"x", [0.0, 0.0, 1.0, 1.0])
        assert "AppearanceStream" in repr(s)
