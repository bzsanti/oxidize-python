"""Tests for the advanced_tables module (Feature 61)."""

import pytest

import oxidize_pdf as op


# ── CellAlignment ────────────────────────────────────────────────────────────


def test_cell_alignment_variants():
    assert repr(op.CellAlignment.LEFT) == "CellAlignment.LEFT"
    assert repr(op.CellAlignment.CENTER) == "CellAlignment.CENTER"
    assert repr(op.CellAlignment.RIGHT) == "CellAlignment.RIGHT"
    assert repr(op.CellAlignment.JUSTIFY) == "CellAlignment.JUSTIFY"


def test_cell_alignment_distinct():
    """All four alignment variants should be distinct objects."""
    variants = [op.CellAlignment.LEFT, op.CellAlignment.CENTER,
                op.CellAlignment.RIGHT, op.CellAlignment.JUSTIFY]
    reprs = [repr(v) for v in variants]
    assert len(set(reprs)) == 4


# ── CellBorderStyle ──────────────────────────────────────────────────────────


def test_cell_border_style_variants():
    assert repr(op.CellBorderStyle.NONE) == "CellBorderStyle.NONE"
    assert repr(op.CellBorderStyle.SOLID) == "CellBorderStyle.SOLID"
    assert repr(op.CellBorderStyle.DASHED) == "CellBorderStyle.DASHED"
    assert repr(op.CellBorderStyle.DOTTED) == "CellBorderStyle.DOTTED"
    assert repr(op.CellBorderStyle.DOUBLE) == "CellBorderStyle.DOUBLE"


def test_cell_border_style_distinct():
    variants = [
        op.CellBorderStyle.NONE, op.CellBorderStyle.SOLID,
        op.CellBorderStyle.DASHED, op.CellBorderStyle.DOTTED,
        op.CellBorderStyle.DOUBLE,
    ]
    reprs = [repr(v) for v in variants]
    assert len(set(reprs)) == 5


# ── CellPadding ──────────────────────────────────────────────────────────────


def test_cell_padding_new():
    p = op.CellPadding(1.0, 2.0, 3.0, 4.0)
    assert p.top == 1.0
    assert p.right == 2.0
    assert p.bottom == 3.0
    assert p.left == 4.0


def test_cell_padding_uniform():
    p = op.CellPadding.uniform(10.0)
    assert p.top == 10.0
    assert p.right == 10.0
    assert p.bottom == 10.0
    assert p.left == 10.0


def test_cell_padding_symmetric():
    p = op.CellPadding.symmetric(5.0, 8.0)
    assert p.top == 8.0
    assert p.right == 5.0
    assert p.bottom == 8.0
    assert p.left == 5.0


def test_cell_padding_repr():
    p = op.CellPadding(1.0, 2.0, 3.0, 4.0)
    r = repr(p)
    assert "CellPadding" in r
    assert "top=1" in r


# ── CellStyle ────────────────────────────────────────────────────────────────


def test_cell_style_new():
    s = op.CellStyle()
    assert "CellStyle" in repr(s)


def test_cell_style_background_color():
    s = op.CellStyle().background_color(op.Color.rgb(0.5, 0.5, 0.5))
    assert "CellStyle" in repr(s)


def test_cell_style_text_color():
    s = op.CellStyle().text_color(op.Color.black())
    assert "CellStyle" in repr(s)


def test_cell_style_font():
    s = op.CellStyle().font(op.Font.HELVETICA_BOLD)
    assert "CellStyle" in repr(s)


def test_cell_style_font_size():
    s = op.CellStyle().font_size(14.0)
    assert "14" in repr(s)


def test_cell_style_padding():
    p = op.CellPadding.uniform(8.0)
    s = op.CellStyle().padding(p)
    assert "CellStyle" in repr(s)


def test_cell_style_alignment():
    s = op.CellStyle().alignment(op.CellAlignment.CENTER)
    assert "CellStyle" in repr(s)


def test_cell_style_border():
    s = op.CellStyle().border(op.CellBorderStyle.DASHED, 2.0, op.Color.black())
    assert "CellStyle" in repr(s)


def test_cell_style_text_wrap():
    s = op.CellStyle().text_wrap(False)
    assert "CellStyle" in repr(s)


def test_cell_style_min_height():
    s = op.CellStyle().min_height(30.0)
    assert "CellStyle" in repr(s)


def test_cell_style_max_height():
    s = op.CellStyle().max_height(100.0)
    assert "CellStyle" in repr(s)


def test_cell_style_chaining():
    s = (op.CellStyle()
         .font_size(12.0)
         .alignment(op.CellAlignment.RIGHT)
         .text_wrap(True)
         .min_height(20.0))
    assert "12" in repr(s)


def test_cell_style_preset_header():
    s = op.CellStyle.header()
    assert "CellStyle" in repr(s)
    assert "14" in repr(s)


def test_cell_style_preset_data():
    s = op.CellStyle.data()
    assert "CellStyle" in repr(s)
    assert "12" in repr(s)


def test_cell_style_preset_numeric():
    s = op.CellStyle.numeric()
    assert "CellStyle" in repr(s)
    assert "11" in repr(s)


def test_cell_style_preset_alternating():
    s = op.CellStyle.alternating()
    assert "CellStyle" in repr(s)


# ── HeaderCell ───────────────────────────────────────────────────────────────


def test_header_cell_new():
    c = op.HeaderCell("Name")
    assert c.text == "Name"
    assert c.span_cols == 1
    assert c.span_rows == 1


def test_header_cell_colspan():
    c = op.HeaderCell("Wide").colspan(3)
    assert c.span_cols == 3


def test_header_cell_rowspan():
    c = op.HeaderCell("Tall").rowspan(2)
    assert c.span_rows == 2


def test_header_cell_style():
    style = op.CellStyle.header()
    c = op.HeaderCell("Styled").style(style)
    assert "HeaderCell" in repr(c)


def test_header_cell_repr():
    c = op.HeaderCell("Test").colspan(2).rowspan(1)
    r = repr(c)
    assert "Test" in r
    assert "colspan=2" in r


def test_header_cell_chaining():
    c = op.HeaderCell("Complex").colspan(3).rowspan(2)
    assert c.span_cols == 3
    assert c.span_rows == 2


# ── HeaderBuilder ────────────────────────────────────────────────────────────


def test_header_builder_new():
    hb = op.HeaderBuilder(3)
    assert hb.row_count() == 0


def test_header_builder_auto():
    hb = op.HeaderBuilder.auto()
    assert hb.row_count() == 0


def test_header_builder_add_simple_row():
    hb = op.HeaderBuilder(3)
    hb.add_simple_row(["Name", "Age", "Dept"])
    assert hb.row_count() == 1


def test_header_builder_add_level():
    hb = op.HeaderBuilder.auto()
    hb.add_level([("Sales", 2), ("Costs", 2)])
    assert hb.row_count() == 1


def test_header_builder_add_group():
    hb = op.HeaderBuilder(3)
    hb.add_group("Sales Data", ["Q1", "Q2", "Q3"])
    assert hb.row_count() == 2


def test_header_builder_default_style():
    hb = op.HeaderBuilder(3)
    style = op.CellStyle.header()
    hb.default_style(style)
    assert "HeaderBuilder" in repr(hb)


def test_header_builder_add_custom_row():
    hb = op.HeaderBuilder(2)
    cells = [op.HeaderCell("A").colspan(1), op.HeaderCell("B").colspan(1)]
    hb.add_custom_row(cells)
    assert hb.row_count() == 1


def test_header_builder_financial_report():
    hb = op.HeaderBuilder.financial_report()
    assert hb.row_count() > 0


def test_header_builder_product_comparison():
    hb = op.HeaderBuilder.product_comparison(["Product A", "Product B"])
    assert hb.row_count() > 0


def test_header_builder_repr():
    hb = op.HeaderBuilder(5)
    r = repr(hb)
    assert "HeaderBuilder" in r


# ── AdvColumn ────────────────────────────────────────────────────────────────


def test_adv_column_new():
    col = op.AdvColumn("Header", 100.0)
    assert col.header == "Header"
    assert col.width == 100.0


def test_adv_column_with_style():
    col = op.AdvColumn("Header", 100.0).with_style(op.CellStyle.data())
    assert col.header == "Header"


def test_adv_column_auto_resize():
    col = op.AdvColumn("Header", 100.0).auto_resize(50.0, 200.0)
    assert col.width == 100.0


def test_adv_column_repr():
    col = op.AdvColumn("Name", 150.0)
    r = repr(col)
    assert "Name" in r
    assert "150" in r


# ── AdvancedTableBuilder ─────────────────────────────────────────────────────


def test_builder_new():
    b = op.AdvancedTableBuilder()
    assert "active" in repr(b)


def test_builder_add_column_and_build():
    b = op.AdvancedTableBuilder()
    b.add_column("Name", 150.0)
    b.add_column("Age", 80.0)
    table = b.build()
    assert table.column_count() == 2
    assert table.row_count() == 0


def test_builder_add_styled_column():
    b = op.AdvancedTableBuilder()
    b.add_styled_column("Header", 100.0, op.CellStyle.header())
    table = b.build()
    assert table.column_count() == 1


def test_builder_columns_equal_width():
    b = op.AdvancedTableBuilder()
    b.columns_equal_width(["A", "B", "C", "D"], 400.0)
    table = b.build()
    assert table.column_count() == 4
    assert table.calculate_width() == 400.0


def test_builder_add_row():
    b = op.AdvancedTableBuilder()
    b.add_column("Name", 100.0)
    b.add_row(["Alice"])
    b.add_row(["Bob"])
    table = b.build()
    assert table.row_count() == 2


def test_builder_add_styled_row():
    b = op.AdvancedTableBuilder()
    b.add_column("Name", 100.0)
    b.add_styled_row(["Alice"], op.CellStyle.header())
    table = b.build()
    assert table.row_count() == 1


def test_builder_add_data():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 50.0)
    b.add_column("B", 50.0)
    b.add_data([["A1", "B1"], ["A2", "B2"], ["A3", "B3"]])
    table = b.build()
    assert table.row_count() == 3


def test_builder_default_style():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.default_style(op.CellStyle.data())
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_data_style():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.data_style(op.CellStyle.data())
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_header_style():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.header_style(op.CellStyle.header())
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_show_header():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.show_header(False)
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_title():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.title("Sales Report")
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_position():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.position(50.0, 700.0)
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_zebra_stripes_enabled():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.zebra_stripes(True, op.Color.rgb(0.95, 0.95, 0.95))
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_zebra_stripes_disabled():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.zebra_stripes(False, op.Color.rgb(0.95, 0.95, 0.95))
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_zebra_striping():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.zebra_striping(op.Color.rgb(0.9, 0.9, 0.9))
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_table_border():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.table_border(False)
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_cell_spacing():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.cell_spacing(3.0)
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_total_width():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.total_width(500.0)
    table = b.build()
    assert table.calculate_width() == 500.0


def test_builder_repeat_headers():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.repeat_headers(True)
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_set_cell_style():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.add_row(["Value"])
    b.set_cell_style(0, 0, op.CellStyle.header())
    table = b.build()
    assert table.row_count() == 1


def test_builder_complex_header():
    hb = op.HeaderBuilder(3)
    hb.add_simple_row(["Name", "Age", "Dept"])
    b = op.AdvancedTableBuilder()
    b.add_column("Name", 150.0)
    b.add_column("Age", 80.0)
    b.add_column("Dept", 120.0)
    b.complex_header(hb)
    table = b.build()
    assert table.column_count() == 3


def test_builder_financial_table():
    b = op.AdvancedTableBuilder()
    b.add_column("Item", 150.0)
    b.add_column("Amount", 100.0)
    b.financial_table()
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_minimal_table():
    b = op.AdvancedTableBuilder()
    b.add_column("Item", 150.0)
    b.add_column("Value", 100.0)
    b.minimal_table()
    table = b.build()
    assert "AdvancedTable" in repr(table)


def test_builder_build_error_no_columns():
    b = op.AdvancedTableBuilder()
    with pytest.raises(Exception, match="[Cc]olumn"):
        b.build()


def test_builder_consumed_repr():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.build()
    assert "consumed" in repr(b)


# ── AdvancedTable ────────────────────────────────────────────────────────────


def test_advanced_table_column_count():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 50.0)
    b.add_column("B", 75.0)
    b.add_column("C", 100.0)
    table = b.build()
    assert table.column_count() == 3


def test_advanced_table_row_count():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.add_row(["1"])
    b.add_row(["2"])
    table = b.build()
    assert table.row_count() == 2


def test_advanced_table_calculate_width():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.add_column("B", 150.0)
    table = b.build()
    assert table.calculate_width() == 250.0


def test_advanced_table_repr():
    b = op.AdvancedTableBuilder()
    b.add_column("A", 100.0)
    b.add_row(["Value"])
    table = b.build()
    r = repr(table)
    assert "AdvancedTable" in r
    assert "cols=1" in r
    assert "rows=1" in r


# ── AdvTableRenderer ─────────────────────────────────────────────────────────


def test_adv_table_renderer_new():
    renderer = op.AdvTableRenderer()
    assert "AdvTableRenderer" in repr(renderer)


def test_adv_table_renderer_render():
    page = op.Page.a4()
    b = op.AdvancedTableBuilder()
    b.add_column("Name", 150.0)
    b.add_column("Value", 100.0)
    b.add_row(["Alice", "42"])
    b.add_row(["Bob", "37"])
    table = b.build()
    renderer = op.AdvTableRenderer()
    result = renderer.render_table(page, table, 50.0, 700.0)
    assert isinstance(result, float)
    assert result < 700.0  # Y decreases as content is drawn


# ── Page integration ─────────────────────────────────────────────────────────


def _build_simple_table():
    b = op.AdvancedTableBuilder()
    b.add_column("Name", 150.0)
    b.add_column("Dept", 120.0)
    b.add_column("Salary", 100.0)
    b.add_row(["Alice", "Engineering", "90000"])
    b.add_row(["Bob", "Marketing", "75000"])
    b.zebra_striping(op.Color.rgb(0.95, 0.95, 0.95))
    return b.build()


def test_page_add_advanced_table():
    page = op.Page.a4()
    table = _build_simple_table()
    result = page.add_advanced_table(table, 50.0, 700.0)
    assert isinstance(result, float)
    assert result < 700.0


def test_page_add_advanced_table_produces_valid_pdf():
    doc = op.Document()
    page = op.Page.a4()
    page.set_font(op.Font.HELVETICA, 12.0)
    table = _build_simple_table()
    page.add_advanced_table(table, 50.0, 700.0)
    doc.add_page(page)
    pdf_bytes = doc.save_to_bytes()
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 100


def test_page_add_advanced_table_auto():
    page = op.Page.a4()
    table = _build_simple_table()
    result = page.add_advanced_table_auto(table)
    assert isinstance(result, float)


def test_page_add_advanced_table_auto_produces_valid_pdf():
    doc = op.Document()
    page = op.Page.a4()
    table = _build_simple_table()
    page.add_advanced_table_auto(table)
    doc.add_page(page)
    pdf_bytes = doc.save_to_bytes()
    assert pdf_bytes[:4] == b"%PDF"


def test_page_add_advanced_table_with_header_style():
    doc = op.Document()
    page = op.Page.a4()
    b = op.AdvancedTableBuilder()
    b.add_column("Product", 150.0)
    b.add_column("Q1", 80.0)
    b.add_column("Q2", 80.0)
    b.header_style(
        op.CellStyle.header()
        .background_color(op.Color.rgb(0.2, 0.4, 0.8))
        .text_color(op.Color.rgb(1.0, 1.0, 1.0))
    )
    b.add_row(["Widget A", "1200", "1350"])
    b.add_row(["Widget B", "980", "1100"])
    b.financial_table()
    table = b.build()
    page.add_advanced_table(table, 50.0, 700.0)
    doc.add_page(page)
    pdf_bytes = doc.save_to_bytes()
    assert pdf_bytes[:4] == b"%PDF"


def test_page_add_advanced_table_with_complex_header():
    doc = op.Document()
    page = op.Page.a4()
    hb = op.HeaderBuilder.financial_report()
    b = op.AdvancedTableBuilder()
    b.add_column("Q1 Revenue", 80.0)
    b.add_column("Q1 Expenses", 80.0)
    b.add_column("Q2 Revenue", 80.0)
    b.add_column("Q2 Expenses", 80.0)
    b.add_column("Total Revenue", 80.0)
    b.add_column("Total Expenses", 80.0)
    b.complex_header(hb)
    b.add_row(["100", "80", "120", "90", "220", "170"])
    table = b.build()
    page.add_advanced_table(table, 50.0, 700.0)
    doc.add_page(page)
    pdf_bytes = doc.save_to_bytes()
    assert pdf_bytes[:4] == b"%PDF"
