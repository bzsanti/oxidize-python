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


# ── Tier 0: Connect forms to Document ─────────────────────────────────────


class TestDocumentEnableForms:
    def test_enable_forms(self):
        from oxidize_pdf import Document

        doc = Document()
        doc.enable_forms()

    def test_add_text_field_renders(self):
        from oxidize_pdf import Document, Font, Page, Point, Rectangle, TextField

        doc = Document()
        doc.enable_forms()

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 720.0, "Name:")
        doc.add_page(page)

        tf = TextField("name_field")
        rect = Rectangle(Point(150.0, 710.0), Point(350.0, 735.0))
        doc.add_text_field(0, tf, rect)

        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
        assert len(data) > 200

    def test_add_checkbox_renders(self):
        from oxidize_pdf import CheckBox, Document, Font, Page, Point, Rectangle

        doc = Document()
        doc.enable_forms()

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 680.0, "Agree:")
        doc.add_page(page)

        cb = CheckBox("agree").checked()
        rect = Rectangle(Point(150.0, 670.0), Point(170.0, 690.0))
        doc.add_checkbox(0, cb, rect)

        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
        assert len(data) > 200

    def test_add_combo_box_renders(self):
        from oxidize_pdf import ComboBox, Document, Font, Page, Point, Rectangle

        doc = Document()
        doc.enable_forms()

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 640.0, "Country:")
        doc.add_page(page)

        combo = ComboBox("country").add_option("US", "United States").add_option("UK", "United Kingdom")
        rect = Rectangle(Point(150.0, 630.0), Point(350.0, 655.0))
        doc.add_combo_box(0, combo, rect)

        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_add_list_box_renders(self):
        from oxidize_pdf import Document, Font, ListBox, Page, Point, Rectangle

        doc = Document()
        doc.enable_forms()

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 600.0, "Fruits:")
        doc.add_page(page)

        lb = ListBox("fruits").add_option("apple", "Apple").add_option("banana", "Banana")
        rect = Rectangle(Point(150.0, 540.0), Point(350.0, 610.0))
        doc.add_list_box(0, lb, rect)

        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_add_radio_button_renders(self):
        from oxidize_pdf import Document, Font, Page, Point, RadioButton, Rectangle

        doc = Document()
        doc.enable_forms()

        page = Page.a4()
        page.set_font(Font.HELVETICA, 12.0)
        page.text_at(72.0, 500.0, "Color:")
        doc.add_page(page)

        rb = RadioButton("color").add_option("R", "Red").add_option("G", "Green")
        rect = Rectangle(Point(150.0, 490.0), Point(170.0, 510.0))
        doc.add_radio_button(0, rb, rect)

        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
