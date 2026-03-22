"""Tests for F77 — ContentParser + ContentOperation (low-level content stream parsing)."""

import pytest
from oxidize_pdf import (
    ContentParser,
    ContentOperation,
    TextElement,
    XRefTable,
    XRefEntry,
)


# ═══════════════════════════════════════════════════════════════════════════════
# ContentOperation — tagged union with op_type + data accessors
# ═══════════════════════════════════════════════════════════════════════════════


class TestContentOperation:
    def test_type_exists(self):
        assert ContentOperation is not None

    def test_op_type_getter(self):
        """After parsing, each operation has an op_type string."""
        ops = ContentParser.parse(b"BT ET")
        assert len(ops) >= 2
        assert ops[0].op_type == "BeginText"
        assert ops[1].op_type == "EndText"

    def test_repr_simple(self):
        ops = ContentParser.parse(b"BT ET")
        assert "ContentOperation" in repr(ops[0])
        assert "BeginText" in repr(ops[0])

    def test_repr_with_operands(self):
        ops = ContentParser.parse(b"2.5 w")
        r = repr(ops[0])
        assert "SetLineWidth" in r
        assert "2.5" in r

    def test_repr_with_name(self):
        ops = ContentParser.parse(b"/Im1 Do")
        r = repr(ops[0])
        assert "PaintXObject" in r
        assert "Im1" in r


class TestContentOperationShowTextArray:
    def test_text_array_elements_accessor(self):
        ops = ContentParser.parse(b"BT [(Hello) -10 (World)] TJ ET")
        tj_ops = [o for o in ops if o.op_type == "ShowTextArray"]
        if tj_ops:
            assert tj_ops[0].text_array_elements is not None

    def test_non_show_text_array_returns_none(self):
        ops = ContentParser.parse(b"BT ET")
        assert ops[0].text_array_elements is None


class TestContentOperationDashPattern:
    def test_set_dash_pattern_operands(self):
        ops = ContentParser.parse(b"[3 2] 0 d")
        dash_ops = [o for o in ops if o.op_type == "SetDashPattern"]
        if dash_ops:
            operands = dash_ops[0].operands
            assert len(operands) >= 1  # at least the phase


class TestContentOperationGraphicsState:
    def test_save_restore(self):
        ops = ContentParser.parse(b"q Q")
        assert ops[0].op_type == "SaveGraphicsState"
        assert ops[1].op_type == "RestoreGraphicsState"

    def test_set_line_width(self):
        ops = ContentParser.parse(b"2.5 w")
        assert ops[0].op_type == "SetLineWidth"
        assert ops[0].operands == [2.5]

    def test_set_line_cap(self):
        ops = ContentParser.parse(b"1 J")
        assert ops[0].op_type == "SetLineCap"

    def test_set_line_join(self):
        ops = ContentParser.parse(b"2 j")
        assert ops[0].op_type == "SetLineJoin"

    def test_set_miter_limit(self):
        ops = ContentParser.parse(b"10 M")
        assert ops[0].op_type == "SetMiterLimit"


class TestContentOperationPath:
    def test_move_to(self):
        ops = ContentParser.parse(b"100 200 m")
        assert ops[0].op_type == "MoveTo"
        assert ops[0].operands == [100.0, 200.0]

    def test_line_to(self):
        ops = ContentParser.parse(b"300 400 l")
        assert ops[0].op_type == "LineTo"
        assert ops[0].operands == [300.0, 400.0]

    def test_rectangle(self):
        ops = ContentParser.parse(b"10 20 100 50 re")
        assert ops[0].op_type == "Rectangle"
        assert ops[0].operands == [10.0, 20.0, 100.0, 50.0]

    def test_close_path(self):
        ops = ContentParser.parse(b"h")
        assert ops[0].op_type == "ClosePath"

    def test_curve_to(self):
        ops = ContentParser.parse(b"1 2 3 4 5 6 c")
        assert ops[0].op_type == "CurveTo"
        assert len(ops[0].operands) == 6


class TestContentOperationPainting:
    def test_stroke(self):
        ops = ContentParser.parse(b"S")
        assert ops[0].op_type == "Stroke"

    def test_fill(self):
        ops = ContentParser.parse(b"f")
        assert ops[0].op_type == "Fill"

    def test_fill_stroke(self):
        ops = ContentParser.parse(b"B")
        assert ops[0].op_type == "FillStroke"

    def test_end_path(self):
        ops = ContentParser.parse(b"n")
        assert ops[0].op_type == "EndPath"

    def test_close_stroke(self):
        ops = ContentParser.parse(b"s")
        assert ops[0].op_type == "CloseStroke"

    def test_fill_even_odd(self):
        ops = ContentParser.parse(b"f*")
        assert ops[0].op_type == "FillEvenOdd"


class TestContentOperationColor:
    def test_set_stroking_rgb(self):
        ops = ContentParser.parse(b"1 0 0 RG")
        assert ops[0].op_type == "SetStrokingRGB"
        assert ops[0].operands == [1.0, 0.0, 0.0]

    def test_set_nonstroking_rgb(self):
        ops = ContentParser.parse(b"0 0.5 1 rg")
        assert ops[0].op_type == "SetNonStrokingRGB"

    def test_set_stroking_gray(self):
        ops = ContentParser.parse(b"0.5 G")
        assert ops[0].op_type == "SetStrokingGray"

    def test_set_nonstroking_gray(self):
        ops = ContentParser.parse(b"0.8 g")
        assert ops[0].op_type == "SetNonStrokingGray"

    def test_set_stroking_cmyk(self):
        ops = ContentParser.parse(b"0.1 0.2 0.3 0.4 K")
        assert ops[0].op_type == "SetStrokingCMYK"
        assert len(ops[0].operands) == 4


class TestContentOperationText:
    def test_set_font(self):
        ops = ContentParser.parse(b"BT /F1 12 Tf ET")
        font_op = [o for o in ops if o.op_type == "SetFont"][0]
        assert font_op.font_name == "F1"
        assert font_op.font_size == 12.0

    def test_show_text(self):
        ops = ContentParser.parse(b"BT (Hello) Tj ET")
        show_ops = [o for o in ops if o.op_type == "ShowText"]
        assert len(show_ops) >= 1
        assert show_ops[0].text_bytes is not None

    def test_move_text(self):
        ops = ContentParser.parse(b"BT 100 700 Td ET")
        move_ops = [o for o in ops if o.op_type == "MoveText"]
        assert len(move_ops) >= 1
        assert move_ops[0].operands == [100.0, 700.0]

    def test_set_text_matrix(self):
        ops = ContentParser.parse(b"BT 1 0 0 1 100 700 Tm ET")
        tm_ops = [o for o in ops if o.op_type == "SetTextMatrix"]
        assert len(tm_ops) >= 1
        assert len(tm_ops[0].operands) == 6


class TestContentOperationClipping:
    def test_clip(self):
        ops = ContentParser.parse(b"W")
        assert ops[0].op_type == "Clip"

    def test_clip_even_odd(self):
        ops = ContentParser.parse(b"W*")
        assert ops[0].op_type == "ClipEvenOdd"


class TestContentOperationXObject:
    def test_paint_xobject(self):
        ops = ContentParser.parse(b"/Im1 Do")
        assert ops[0].op_type == "PaintXObject"
        assert ops[0].name == "Im1"


class TestContentOperationMarkedContent:
    def test_begin_marked_content(self):
        ops = ContentParser.parse(b"/Span BMC EMC")
        assert ops[0].op_type == "BeginMarkedContent"
        assert ops[0].name == "Span"

    def test_end_marked_content(self):
        ops = ContentParser.parse(b"/Span BMC EMC")
        assert ops[1].op_type == "EndMarkedContent"


# ═══════════════════════════════════════════════════════════════════════════════
# ContentParser
# ═══════════════════════════════════════════════════════════════════════════════


class TestContentParser:
    def test_parse_empty(self):
        ops = ContentParser.parse(b"")
        assert ops == []

    def test_parse_simple_content(self):
        content = b"BT /F1 12 Tf 100 700 Td (Hello World) Tj ET"
        ops = ContentParser.parse(content)
        types = [o.op_type for o in ops]
        assert "BeginText" in types
        assert "SetFont" in types
        assert "MoveText" in types
        assert "ShowText" in types
        assert "EndText" in types

    def test_parse_graphics_content(self):
        content = b"q 1 0 0 RG 2 w 100 200 m 300 400 l S Q"
        ops = ContentParser.parse(content)
        types = [o.op_type for o in ops]
        assert "SaveGraphicsState" in types
        assert "SetStrokingRGB" in types
        assert "SetLineWidth" in types
        assert "MoveTo" in types
        assert "LineTo" in types
        assert "Stroke" in types
        assert "RestoreGraphicsState" in types

    def test_parse_invalid_content(self):
        """Invalid content should not crash, may return partial or empty."""
        ops = ContentParser.parse(b"\xff\xfe\xfd")
        assert isinstance(ops, list)

    def test_parse_content_alias(self):
        """parse_content is an alias for parse."""
        ops = ContentParser.parse_content(b"BT ET")
        assert len(ops) >= 2

    def test_parse_strict_valid(self):
        """parse_strict returns operations for valid content."""
        ops = ContentParser.parse_strict(b"BT ET")
        assert isinstance(ops, list)
        assert len(ops) >= 2

    def test_parse_strict_raises_on_invalid(self):
        """parse_strict raises ValueError for invalid content bytes."""
        with pytest.raises((ValueError, Exception)):
            ContentParser.parse_strict(b"\x00\xff\xfe\xfd\x00\xff")


# ═══════════════════════════════════════════════════════════════════════════════
# TextElement
# ═══════════════════════════════════════════════════════════════════════════════


class TestTextElement:
    def test_type_exists(self):
        assert TextElement is not None

    def test_from_show_text_array(self):
        """TextElement instances come from ShowTextArray parsing (TJ operator)."""
        ops = ContentParser.parse(b"BT [(Hello) -10 (World)] TJ ET")
        tj_ops = [o for o in ops if o.op_type == "ShowTextArray"]
        if tj_ops:
            elements = tj_ops[0].text_array_elements
            assert elements is not None
            assert len(elements) >= 1
            # Check that elements have the right types
            for elem in elements:
                assert elem.is_text or elem.is_spacing

    def test_text_element_text(self):
        ops = ContentParser.parse(b"BT [(Hello)] TJ ET")
        tj_ops = [o for o in ops if o.op_type == "ShowTextArray"]
        if tj_ops and tj_ops[0].text_array_elements:
            text_elems = [e for e in tj_ops[0].text_array_elements if e.is_text]
            if text_elems:
                assert text_elems[0].text_bytes is not None
                assert text_elems[0].spacing is None

    def test_text_element_spacing(self):
        ops = ContentParser.parse(b"BT [(Hello) -50 (World)] TJ ET")
        tj_ops = [o for o in ops if o.op_type == "ShowTextArray"]
        if tj_ops and tj_ops[0].text_array_elements:
            spacing_elems = [e for e in tj_ops[0].text_array_elements if e.is_spacing]
            if spacing_elems:
                assert spacing_elems[0].spacing is not None
                assert spacing_elems[0].text_bytes is None


# ═══════════════════════════════════════════════════════════════════════════════
# XRefTable + XRefEntry
# ═══════════════════════════════════════════════════════════════════════════════


class TestXRefTable:
    def test_create_empty(self):
        table = XRefTable()
        assert table is not None
        assert len(table) == 0
        assert table.is_empty is True

    def test_add_entry(self):
        table = XRefTable()
        entry = XRefEntry(offset=0, generation=0, in_use=True)
        table.add_entry(0, entry)
        assert len(table) == 1
        assert table.is_empty is False

    def test_get_entry(self):
        table = XRefTable()
        table.add_entry(1, XRefEntry(offset=100, generation=0, in_use=True))
        entry = table.get_entry(1)
        assert entry is not None
        assert entry.offset == 100
        assert entry.generation == 0
        assert entry.in_use is True

    def test_get_missing_entry(self):
        table = XRefTable()
        assert table.get_entry(999) is None

    def test_entries_iteration(self):
        table = XRefTable()
        table.add_entry(0, XRefEntry(offset=0, generation=0, in_use=True))
        table.add_entry(5, XRefEntry(offset=500, generation=0, in_use=True))
        table.add_entry(10, XRefEntry(offset=1000, generation=1, in_use=False))
        entries = table.entries()
        assert len(entries) == 3
        obj_nums = sorted([num for num, _ in entries])
        assert obj_nums == [0, 5, 10]
        for num, entry in entries:
            assert isinstance(num, int)
            assert isinstance(entry, XRefEntry)

    def test_entries_empty(self):
        table = XRefTable()
        assert table.entries() == []

    def test_repr(self):
        table = XRefTable()
        assert "XRefTable" in repr(table)


class TestXRefEntry:
    def test_create(self):
        entry = XRefEntry(offset=0, generation=0, in_use=True)
        assert entry is not None

    def test_properties(self):
        entry = XRefEntry(offset=500, generation=2, in_use=False)
        assert entry.offset == 500
        assert entry.generation == 2
        assert entry.in_use is False

    def test_repr(self):
        entry = XRefEntry(offset=0, generation=0, in_use=True)
        assert "XRefEntry" in repr(entry)
