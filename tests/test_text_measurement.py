"""Tests for Text Measurement — Feature 5 (Tier 1)."""

import pytest


class TestMeasureText:
    """Test measure_text function."""

    def test_measure_text_returns_positive(self):
        from oxidize_pdf import Font, measure_text

        result = measure_text("Hello", Font.HELVETICA, 12.0)
        assert isinstance(result, float)
        assert result > 0.0

    def test_measure_text_empty_string(self):
        from oxidize_pdf import Font, measure_text

        result = measure_text("", Font.HELVETICA, 12.0)
        assert result == 0.0

    def test_measure_text_scales_with_size(self):
        from oxidize_pdf import Font, measure_text

        w12 = measure_text("Hello", Font.HELVETICA, 12.0)
        w24 = measure_text("Hello", Font.HELVETICA, 24.0)
        assert w24 > w12

    def test_measure_text_longer_is_wider(self):
        from oxidize_pdf import Font, measure_text

        short = measure_text("Hi", Font.HELVETICA, 12.0)
        long = measure_text("Hello World", Font.HELVETICA, 12.0)
        assert long > short

    def test_measure_text_different_fonts(self):
        from oxidize_pdf import Font, measure_text

        w_helv = measure_text("Hello", Font.HELVETICA, 12.0)
        w_courier = measure_text("Hello", Font.COURIER, 12.0)
        # Courier is monospaced so widths differ from proportional Helvetica
        assert w_helv != w_courier


class TestMeasureChar:
    """Test measure_char function."""

    def test_measure_char_returns_positive(self):
        from oxidize_pdf import Font, measure_char

        result = measure_char("A", Font.HELVETICA, 12.0)
        assert isinstance(result, float)
        assert result > 0.0

    def test_measure_char_space(self):
        from oxidize_pdf import Font, measure_char

        result = measure_char(" ", Font.HELVETICA, 12.0)
        assert result > 0.0

    def test_measure_char_empty_raises(self):
        from oxidize_pdf import Font, measure_char

        with pytest.raises(ValueError):
            measure_char("", Font.HELVETICA, 12.0)

    def test_measure_char_multi_char_raises(self):
        from oxidize_pdf import Font, measure_char

        with pytest.raises(ValueError):
            measure_char("AB", Font.HELVETICA, 12.0)
