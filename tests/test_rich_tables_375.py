"""F3 (#375): rich table structure — TableStructure / RichCell with merged
cells and header rows, surfaced through Element.table_structure.

Upstream oxidize-pdf 4.0.0 populates a rich TableStructure (merged cells via
drawn-grid dividers, header rows via structure tags) on detected tables. The
bridge surfaces it on Element for tables where a hard signal revealed it;
borderless tables keep structure None and expose only the flat view.

The fixture mirrors the upstream #375 detection fixture: a ruled 2x2 grid whose
top row omits the middle vertical divider (one spanning header cell) while the
bottom row keeps it (two cells).
"""

import pytest
import oxidize_pdf as op


def _hline(page, x1, x2, y):
    page.move_to(x1, y)
    page.line_to(x2, y)
    page.stroke()


def _vline(page, x, y1, y2):
    page.move_to(x, y1)
    page.line_to(x, y2)
    page.stroke()


def _build_merged_header_table_pdf() -> bytes:
    doc = op.Document()
    page = op.Page.a4()
    for y in (100.0, 150.0, 200.0):
        _hline(page, 100.0, 300.0, y)
    _vline(page, 100.0, 100.0, 200.0)  # left border (full height)
    _vline(page, 300.0, 100.0, 200.0)  # right border (full height)
    _vline(page, 200.0, 100.0, 150.0)  # middle divider only in the bottom row
    page.set_font(op.Font.HELVETICA, 10.0)
    page.text_at(150.0, 170.0, "Header")
    page.text_at(130.0, 120.0, "A")
    page.text_at(230.0, 120.0, "B")
    doc.add_page(page)
    return doc.save_to_bytes()


@pytest.fixture
def table_elem():
    reader = op.PdfReader.from_bytes(_build_merged_header_table_pdf())
    tables = [e for e in reader.partition() if e.type_name == "table"]
    assert tables, "no table element detected in the ruled-grid fixture"
    return tables[0]


class TestTableStructure:
    def test_structure_present(self, table_elem):
        assert table_elem.table_structure is not None

    def test_grid_dimensions(self, table_elem):
        st = table_elem.table_structure
        assert st.num_rows == 2
        assert st.num_cols == 2

    def test_merged_header_cell_spans_two_columns(self, table_elem):
        st = table_elem.table_structure
        top_left = [c for c in st.cells if c.row == 0 and c.col == 0]
        assert top_left, "no cell at (0,0)"
        assert top_left[0].col_span == 2
        assert top_left[0].row_span == 1

    def test_merged_cell_omits_interior_position(self, table_elem):
        st = table_elem.table_structure
        assert not [c for c in st.cells if c.row == 0 and c.col == 1]

    def test_bottom_row_has_two_single_cells(self, table_elem):
        st = table_elem.table_structure
        singles = [
            c for c in st.cells if c.row == 1 and c.col_span == 1 and c.row_span == 1
        ]
        assert len(singles) >= 2

    def test_header_rows_counted(self, table_elem):
        assert table_elem.table_structure.header_rows >= 1

    def test_richcell_exposes_text(self, table_elem):
        st = table_elem.table_structure
        assert any("Header" in c.text for c in st.cells)


class TestNonTableElement:
    def test_paragraph_has_no_structure(self):
        doc = op.Document()
        page = op.Page.a4()
        page.set_font(op.Font.HELVETICA, 12.0)
        page.text_at(50.0, 700.0, "Just a paragraph of ordinary prose text.")
        doc.add_page(page)
        reader = op.PdfReader.from_bytes(doc.save_to_bytes())
        for e in reader.partition():
            assert e.table_structure is None
