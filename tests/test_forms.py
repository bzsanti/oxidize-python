"""Tests for Forms — Feature 22 (Tier 6)."""

import pytest


class TestTextField:
    def test_text_field_create(self):
        from oxidize_pdf import TextField

        tf = TextField("name_field")
        assert isinstance(tf, TextField)

    def test_text_field_with_value(self):
        from oxidize_pdf import TextField

        tf = TextField("email").with_default_value("user@example.com")
        assert isinstance(tf, TextField)

    def test_text_field_multiline(self):
        from oxidize_pdf import TextField

        tf = TextField("comments").multiline()
        assert isinstance(tf, TextField)

    def test_text_field_password(self):
        from oxidize_pdf import TextField

        tf = TextField("password").password()
        assert isinstance(tf, TextField)


class TestCheckBox:
    def test_checkbox_create(self):
        from oxidize_pdf import CheckBox

        cb = CheckBox("agree_terms")
        assert isinstance(cb, CheckBox)

    def test_checkbox_checked(self):
        from oxidize_pdf import CheckBox

        cb = CheckBox("agree_terms").checked()
        assert isinstance(cb, CheckBox)


class TestRadioButton:
    def test_radio_create(self):
        from oxidize_pdf import RadioButton

        rb = RadioButton("gender")
        rb = rb.add_option("M", "Male").add_option("F", "Female")
        assert isinstance(rb, RadioButton)

    def test_radio_with_selected(self):
        from oxidize_pdf import RadioButton

        rb = (
            RadioButton("color")
            .add_option("R", "Red")
            .add_option("G", "Green")
            .with_selected(0)
        )
        assert isinstance(rb, RadioButton)


class TestComboBox:
    def test_combo_create(self):
        from oxidize_pdf import ComboBox

        cb = ComboBox("country")
        cb = cb.add_option("US", "United States").add_option("UK", "United Kingdom")
        assert isinstance(cb, ComboBox)

    def test_combo_editable(self):
        from oxidize_pdf import ComboBox

        cb = ComboBox("city").editable()
        assert isinstance(cb, ComboBox)


class TestListBox:
    def test_listbox_create(self):
        from oxidize_pdf import ListBox

        lb = ListBox("fruits")
        lb = lb.add_option("apple", "Apple").add_option("banana", "Banana")
        assert isinstance(lb, ListBox)

    def test_listbox_multi_select(self):
        from oxidize_pdf import ListBox

        lb = ListBox("colors").multi_select()
        assert isinstance(lb, ListBox)
