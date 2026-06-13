"""Tests for IncrementalFormFiller (oxidize-pdf 2.15.0, issue #318).

Fills AcroForm fields on an already-serialized PDF via an ISO 32000-1 §7.5.6
incremental update: the original bytes are preserved verbatim and the modified
field objects are appended in a new revision.

These tests validate the real wire output (verbatim-preservation contract and
the field /V actually written into the appended revision), never just that a
call returns bytes.
"""

import pytest

from oxidize_pdf import (
    Document,
    Font,
    IncrementalFormFiller,
    Page,
    Point,
    Rectangle,
    TextField,
)


def _base_form_pdf(field_name="name_field", *extra_fields):
    """Build a single-page PDF carrying one or more AcroForm text fields."""
    doc = Document()
    doc.enable_forms()

    page = Page.a4()
    page.set_font(Font.HELVETICA, 12.0)
    page.text_at(72.0, 720.0, "Name:")
    doc.add_page(page)

    doc.add_text_field(TextField(field_name), Rectangle(Point(150.0, 710.0), Point(350.0, 735.0)))
    y = 670.0
    for name in extra_fields:
        doc.add_text_field(TextField(name), Rectangle(Point(150.0, y), Point(350.0, y + 25.0)))
        y -= 40.0

    return doc.save_to_bytes()


class TestFillSingleField:
    def test_original_bytes_preserved_verbatim(self):
        base = _base_form_pdf()
        filled = IncrementalFormFiller(base).fill("name_field", "Ada Lovelace")

        # ISO 32000-1 §7.5.6 incremental update: the base prefix is untouched.
        assert filled[: len(base)] == base
        assert len(filled) > len(base)

    def test_value_written_into_appended_revision(self):
        base = _base_form_pdf()
        filled = IncrementalFormFiller(base).fill("name_field", "Ada Lovelace")

        appended = filled[len(base):]
        # The rewritten field object carries /V set to the supplied value.
        # write_dict emits `/V (value)` (name, space, literal string), so the
        # exact pairing proves recovery rather than the value merely appearing
        # inside a synthesized /AP appearance stream.
        assert b"/V (Ada Lovelace)" in appended

    def test_incremental_revision_has_its_own_xref(self):
        base = _base_form_pdf()
        filled = IncrementalFormFiller(base).fill("name_field", "Ada Lovelace")

        # An incremental update appends a second cross-reference section, so the
        # filled document carries more than one `startxref` marker.
        assert filled.count(b"startxref") == base.count(b"startxref") + 1


class TestFillMany:
    def test_writes_every_supplied_field(self):
        base = _base_form_pdf("first", "second")
        filled = IncrementalFormFiller(base).fill_many(
            [("first", "Grace Hopper"), ("second", "Margaret Hamilton")]
        )

        assert filled[: len(base)] == base
        appended = filled[len(base):]
        assert b"/V (Grace Hopper)" in appended
        assert b"/V (Margaret Hamilton)" in appended

    def test_fill_many_single_appended_revision(self):
        base = _base_form_pdf("first", "second")
        filled = IncrementalFormFiller(base).fill_many(
            [("first", "Grace Hopper"), ("second", "Margaret Hamilton")]
        )

        # Two fields, one incremental update -> exactly one extra xref section.
        assert filled.count(b"startxref") == base.count(b"startxref") + 1


class TestErrors:
    def test_unknown_field_name_raises(self):
        base = _base_form_pdf()
        with pytest.raises(Exception) as exc:
            IncrementalFormFiller(base).fill("does_not_exist", "x")
        # FieldNotFound surfaces the offending name.
        assert "does_not_exist" in str(exc.value)

    def test_malformed_base_bytes_raise(self):
        with pytest.raises(Exception):
            IncrementalFormFiller(b"not a pdf at all").fill("name_field", "x")
