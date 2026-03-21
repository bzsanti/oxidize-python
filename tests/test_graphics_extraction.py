"""Tests for F82 — Graphics Extraction: VectorLine, ExtractedGraphics, GraphicsExtractor."""

import pytest
from oxidize_pdf import (
    LineOrientation,
    VectorLine,
    ExtractedGraphics,
    ExtractionConfig,
    GraphicsExtractor,
    Document,
    Page,
)


# ═══════════════════════════════════════════════════════════════════════════════
# LineOrientation
# ═══════════════════════════════════════════════════════════════════════════════


class TestLineOrientation:
    def test_variants(self):
        assert LineOrientation.HORIZONTAL is not None
        assert LineOrientation.VERTICAL is not None
        assert LineOrientation.DIAGONAL is not None

    def test_equality(self):
        assert LineOrientation.HORIZONTAL == LineOrientation.HORIZONTAL
        assert LineOrientation.HORIZONTAL != LineOrientation.VERTICAL

    def test_repr(self):
        assert "LineOrientation" in repr(LineOrientation.HORIZONTAL)


# ═══════════════════════════════════════════════════════════════════════════════
# VectorLine
# ═══════════════════════════════════════════════════════════════════════════════


class TestVectorLine:
    def test_create_horizontal(self):
        line = VectorLine(0.0, 100.0, 200.0, 100.0, 1.0, True)
        assert line is not None
        assert line.orientation == LineOrientation.HORIZONTAL

    def test_create_vertical(self):
        line = VectorLine(100.0, 0.0, 100.0, 200.0, 1.0, True)
        assert line.orientation == LineOrientation.VERTICAL

    def test_create_diagonal(self):
        line = VectorLine(0.0, 0.0, 100.0, 200.0, 1.0, True)
        assert line.orientation == LineOrientation.DIAGONAL

    def test_getters(self):
        line = VectorLine(10.0, 20.0, 30.0, 40.0, 2.5, True)
        assert line.x1 == 10.0
        assert line.y1 == 20.0
        assert line.x2 == 30.0
        assert line.y2 == 40.0
        assert line.stroke_width == 2.5
        assert line.is_stroked is True

    def test_length(self):
        line = VectorLine(0.0, 0.0, 3.0, 4.0, 1.0, True)
        assert abs(line.length - 5.0) < 0.001

    def test_midpoint(self):
        line = VectorLine(0.0, 0.0, 100.0, 200.0, 1.0, True)
        mx, my = line.midpoint
        assert mx == 50.0
        assert my == 100.0

    def test_repr(self):
        line = VectorLine(0.0, 0.0, 100.0, 0.0, 1.0, True)
        assert "VectorLine" in repr(line)

    # Cycle 16 (O7): stroke_color getter
    def test_stroke_color_default_none(self):
        line = VectorLine(0.0, 0.0, 100.0, 0.0, 1.0, True)
        assert line.stroke_color is None


# ═══════════════════════════════════════════════════════════════════════════════
# ExtractedGraphics
# ═══════════════════════════════════════════════════════════════════════════════


class TestExtractedGraphics:
    def test_create_empty(self):
        eg = ExtractedGraphics()
        assert eg is not None
        assert eg.horizontal_count == 0
        assert eg.vertical_count == 0
        assert eg.lines == []

    def test_add_line(self):
        eg = ExtractedGraphics()
        eg.add_line(VectorLine(0.0, 100.0, 200.0, 100.0, 1.0, True))
        assert len(eg.lines) == 1
        assert eg.horizontal_count == 1

    def test_has_table_structure(self):
        eg = ExtractedGraphics()
        # Need at least 2 horizontal + 2 vertical
        eg.add_line(VectorLine(0.0, 0.0, 100.0, 0.0, 1.0, True))
        eg.add_line(VectorLine(0.0, 50.0, 100.0, 50.0, 1.0, True))
        assert eg.has_table_structure is False  # no verticals yet
        eg.add_line(VectorLine(0.0, 0.0, 0.0, 50.0, 1.0, True))
        eg.add_line(VectorLine(100.0, 0.0, 100.0, 50.0, 1.0, True))
        assert eg.has_table_structure is True

    def test_horizontal_lines(self):
        eg = ExtractedGraphics()
        eg.add_line(VectorLine(0.0, 100.0, 200.0, 100.0, 1.0, True))
        eg.add_line(VectorLine(100.0, 0.0, 100.0, 200.0, 1.0, True))
        h_lines = eg.horizontal_lines
        assert len(h_lines) == 1

    def test_vertical_lines(self):
        eg = ExtractedGraphics()
        eg.add_line(VectorLine(0.0, 100.0, 200.0, 100.0, 1.0, True))
        eg.add_line(VectorLine(100.0, 0.0, 100.0, 200.0, 1.0, True))
        v_lines = eg.vertical_lines
        assert len(v_lines) == 1

    def test_repr(self):
        eg = ExtractedGraphics()
        assert "ExtractedGraphics" in repr(eg)

    # Cycle 15 (O6): test non-stroked lines
    def test_add_non_stroked_line(self):
        eg = ExtractedGraphics()
        # Non-stroked lines can be added to the container directly
        eg.add_line(VectorLine(0.0, 0.0, 100.0, 0.0, 1.0, False))
        assert len(eg.lines) == 1
        assert eg.lines[0].is_stroked is False

    def test_stroked_only_config(self):
        # With stroked_only=True (default), non-stroked lines from PDF are filtered
        # With stroked_only=False, fill-based lines are also captured
        config_default = ExtractionConfig(stroked_only=True)
        config_all = ExtractionConfig(stroked_only=False)
        assert config_default.stroked_only is True
        assert config_all.stroked_only is False


# ═══════════════════════════════════════════════════════════════════════════════
# ExtractionConfig
# ═══════════════════════════════════════════════════════════════════════════════


class TestExtractionConfig:
    def test_default(self):
        config = ExtractionConfig()
        assert config.min_line_length == 1.0
        assert config.extract_diagonals is False
        assert config.stroked_only is True

    def test_custom(self):
        config = ExtractionConfig(
            min_line_length=5.0,
            extract_diagonals=True,
            stroked_only=False,
        )
        assert config.min_line_length == 5.0
        assert config.extract_diagonals is True
        assert config.stroked_only is False

    def test_repr(self):
        config = ExtractionConfig()
        assert "ExtractionConfig" in repr(config)

    # Cycle 3 (R3): reject negative min_line_length
    def test_negative_min_line_length_raises(self):
        with pytest.raises(ValueError):
            ExtractionConfig(min_line_length=-1.0)

    def test_zero_min_line_length_allowed(self):
        config = ExtractionConfig(min_line_length=0.0)
        assert config.min_line_length == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# GraphicsExtractor
# ═══════════════════════════════════════════════════════════════════════════════


class TestGraphicsExtractor:
    def test_create_default(self):
        ge = GraphicsExtractor()
        assert ge is not None

    def test_create_with_config(self):
        config = ExtractionConfig(min_line_length=10.0)
        ge = GraphicsExtractor(config=config)
        assert ge is not None

    def test_extract_from_bytes(self):
        """Extract graphics from a PDF with drawn lines."""
        doc = Document()
        page = Page(612.0, 792.0)
        doc.add_page(page)
        pdf_bytes = doc.save_to_bytes()

        ge = GraphicsExtractor()
        result = ge.extract_from_bytes(pdf_bytes, 0)
        assert isinstance(result, ExtractedGraphics)

    def test_extract_from_empty_page(self):
        doc = Document()
        doc.add_page(Page(612.0, 792.0))
        pdf_bytes = doc.save_to_bytes()

        ge = GraphicsExtractor()
        result = ge.extract_from_bytes(pdf_bytes, 0)
        assert isinstance(result, ExtractedGraphics)
        assert len(result.lines) == 0

    def test_repr(self):
        ge = GraphicsExtractor()
        assert "GraphicsExtractor" in repr(ge)

    # Cycle 10 (R5): repr with config values
    def test_repr_shows_config(self):
        config = ExtractionConfig(min_line_length=5.0, extract_diagonals=True, stroked_only=False)
        ge = GraphicsExtractor(config=config)
        r = repr(ge)
        assert "5.0" in r
        assert "GraphicsExtractor" in r

    def test_repr_default(self):
        ge = GraphicsExtractor()
        r = repr(ge)
        assert "GraphicsExtractor" in r
        assert "1.0" in r  # default min_line_length

    # Cycle 14 (O5): out-of-range page raises
    def test_extract_from_bytes_out_of_range_page(self):
        doc = Document()
        doc.add_page(Page(612.0, 792.0))
        pdf_bytes = doc.save_to_bytes()

        ge = GraphicsExtractor()
        with pytest.raises(ValueError):
            ge.extract_from_bytes(pdf_bytes, 999)
