"""Tests for Table support — Feature 2 (Tier 1)."""

import pytest


class TestTableConstruction:
    """Test Table, TableOptions, HeaderStyle construction."""

    def test_table_create_with_columns(self):
        from oxidize_pdf import Table

        t = Table([100.0, 150.0, 100.0])
        assert isinstance(t, Table)

    def test_table_with_equal_columns(self):
        from oxidize_pdf import Table

        t = Table.with_equal_columns(4, 400.0)
        assert isinstance(t, Table)

    def test_table_options_defaults(self):
        from oxidize_pdf import TableOptions

        opts = TableOptions()
        assert isinstance(opts, TableOptions)

    def test_table_options_custom(self):
        from oxidize_pdf import Color, Font, TableOptions

        opts = TableOptions(
            border_width=2.0,
            cell_padding=8.0,
            font_size=12.0,
        )
        assert isinstance(opts, TableOptions)

    def test_header_style(self):
        from oxidize_pdf import Color, Font, HeaderStyle

        hs = HeaderStyle(
            background_color=Color.rgb(0.2, 0.2, 0.8),
            text_color=Color.rgb(1.0, 1.0, 1.0),
            font=Font.HELVETICA_BOLD,
            bold=True,
        )
        assert isinstance(hs, HeaderStyle)

    def test_grid_style_variants(self):
        from oxidize_pdf import GridStyle

        assert GridStyle.NONE is not None
        assert GridStyle.HORIZONTAL is not None
        assert GridStyle.VERTICAL is not None
        assert GridStyle.FULL is not None
        assert GridStyle.OUTLINE is not None


class TestTableRows:
    """Test adding rows to tables."""

    def test_add_row(self):
        from oxidize_pdf import Table

        t = Table([100.0, 100.0, 100.0])
        t.add_row(["A", "B", "C"])

    def test_add_header_row(self):
        from oxidize_pdf import Table

        t = Table([100.0, 100.0, 100.0])
        t.add_header_row(["Col1", "Col2", "Col3"])

    def test_add_row_wrong_column_count_raises(self):
        from oxidize_pdf import PdfError, Table

        t = Table([100.0, 100.0])
        with pytest.raises(PdfError):
            t.add_row(["A", "B", "C"])  # 3 cells for 2 columns

    def test_table_dimensions(self):
        from oxidize_pdf import Table

        t = Table([100.0, 150.0, 100.0])
        assert t.width == 350.0
        assert t.height >= 0.0


class TestTableCell:
    """Test TableCell construction."""

    def test_cell_simple(self):
        from oxidize_pdf import TableCell

        cell = TableCell("Hello")
        assert isinstance(cell, TableCell)

    def test_cell_with_colspan(self):
        from oxidize_pdf import TableCell

        cell = TableCell.with_colspan("Merged", 2)
        assert isinstance(cell, TableCell)

    def test_cell_with_background(self):
        from oxidize_pdf import Color, TableCell

        cell = TableCell("Colored")
        cell.set_background_color(Color.rgb(0.9, 0.9, 0.9))

    def test_add_custom_row(self):
        from oxidize_pdf import Table, TableCell

        t = Table([100.0, 100.0])
        cells = [TableCell("A"), TableCell("B")]
        t.add_custom_row(cells)


class TestTableOnPage:
    """Test rendering tables on pages."""

    def test_page_add_simple_table(self):
        from oxidize_pdf import Document, Page, Table

        t = Table([150.0, 150.0])
        t.add_header_row(["Name", "Value"])
        t.add_row(["Alpha", "1"])
        t.add_row(["Beta", "2"])

        page = Page.a4()
        page.add_simple_table(t, 50.0, 700.0)

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()

        assert data[:5] == b"%PDF-"
        assert len(data) > 0

    def test_page_add_quick_table(self):
        from oxidize_pdf import Document, Page

        data_rows = [
            ["Name", "Age", "City"],
            ["Alice", "30", "London"],
            ["Bob", "25", "Paris"],
        ]
        page = Page.a4()
        page.add_quick_table(data_rows, 50.0, 700.0, 450.0)

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()

        assert data[:5] == b"%PDF-"

    def test_page_add_styled_table(self):
        from oxidize_pdf import Document, Page, TableStyle

        headers = ["ID", "Product", "Price"]
        rows = [["1", "Widget", "9.99"], ["2", "Gadget", "19.99"]]
        style = TableStyle.professional()

        page = Page.a4()
        page.add_styled_table(headers, rows, 50.0, 700.0, 450.0, style)

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()

        assert data[:5] == b"%PDF-"

    def test_table_with_options(self):
        from oxidize_pdf import (
            Color,
            Document,
            Font,
            GridStyle,
            HeaderStyle,
            Page,
            Table,
            TableOptions,
        )

        opts = TableOptions(
            border_width=0.5,
            cell_padding=6.0,
            font_size=11.0,
            grid_style=GridStyle.FULL,
            header_style=HeaderStyle(
                background_color=Color.rgb(0.1, 0.1, 0.5),
                text_color=Color.rgb(1.0, 1.0, 1.0),
                font=Font.HELVETICA_BOLD,
                bold=True,
            ),
        )

        t = Table([120.0, 120.0])
        t.set_options(opts)
        t.add_header_row(["Key", "Value"])
        t.add_row(["foo", "bar"])

        page = Page.a4()
        page.add_simple_table(t, 50.0, 700.0)

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()

        assert data[:5] == b"%PDF-"


class TestTableStyle:
    """Test predefined table styles."""

    def test_style_minimal(self):
        from oxidize_pdf import TableStyle

        s = TableStyle.minimal()
        assert isinstance(s, TableStyle)

    def test_style_simple(self):
        from oxidize_pdf import TableStyle

        s = TableStyle.simple()
        assert isinstance(s, TableStyle)

    def test_style_professional(self):
        from oxidize_pdf import TableStyle

        s = TableStyle.professional()
        assert isinstance(s, TableStyle)

    def test_style_colorful(self):
        from oxidize_pdf import TableStyle

        s = TableStyle.colorful()
        assert isinstance(s, TableStyle)
