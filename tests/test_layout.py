"""Tests for Layout module — oxidize-pdf 2.5.0 new functionality."""

import pytest


# ── Ciclo 1: PageConfig + utility functions + TextBlockMetrics ─────────────


class TestPageConfig:
    """Test PageConfig construction and geometry calculations."""

    def test_a4_returns_a4_dimensions(self):
        from oxidize_pdf import PageConfig

        cfg = PageConfig.a4()
        assert cfg.width == 595.0
        assert cfg.height == 842.0

    def test_a4_default_margins(self):
        from oxidize_pdf import PageConfig

        cfg = PageConfig.a4()
        assert cfg.margin_left == 72.0
        assert cfg.margin_right == 72.0
        assert cfg.margin_top == 72.0
        assert cfg.margin_bottom == 72.0

    def test_a4_content_width_with_default_margins(self):
        from oxidize_pdf import PageConfig

        cfg = PageConfig.a4()
        # 595 - 72 - 72 = 451
        assert abs(cfg.content_width() - 451.0) < 0.1

    def test_a4_usable_height_with_default_margins(self):
        from oxidize_pdf import PageConfig

        cfg = PageConfig.a4()
        # 842 - 72 - 72 = 698
        assert abs(cfg.usable_height() - 698.0) < 0.1

    def test_a4_with_margins_custom(self):
        from oxidize_pdf import PageConfig

        cfg = PageConfig.a4_with_margins(50.0, 50.0, 50.0, 50.0)
        assert cfg.width == 595.0
        assert cfg.height == 842.0
        assert abs(cfg.content_width() - 495.0) < 0.1
        assert abs(cfg.usable_height() - 742.0) < 0.1

    def test_new_custom_dimensions(self):
        from oxidize_pdf import PageConfig

        cfg = PageConfig(400.0, 600.0, 20.0, 20.0, 30.0, 30.0)
        assert cfg.width == 400.0
        assert cfg.height == 600.0
        assert abs(cfg.content_width() - 360.0) < 0.1
        assert abs(cfg.usable_height() - 540.0) < 0.1


class TestFitImageDimensions:
    """Test fit_image_dimensions preserves aspect ratio."""

    def test_width_constrained(self):
        from oxidize_pdf import fit_image_dimensions

        # 400x200 px into 200x300 pt box → width limits: 200x100
        w, h = fit_image_dimensions(400, 200, 200.0, 300.0)
        assert abs(w - 200.0) < 0.001
        assert abs(h - 100.0) < 0.001

    def test_height_constrained(self):
        from oxidize_pdf import fit_image_dimensions

        # 200x400 px into 300x200 pt box → height limits: 100x200
        w, h = fit_image_dimensions(200, 400, 300.0, 200.0)
        assert abs(w - 100.0) < 0.001
        assert abs(h - 200.0) < 0.001

    def test_zero_width_returns_zero(self):
        from oxidize_pdf import fit_image_dimensions

        w, h = fit_image_dimensions(0, 100, 200.0, 200.0)
        assert w == 0.0
        assert h == 0.0

    def test_zero_height_returns_zero(self):
        from oxidize_pdf import fit_image_dimensions

        w, h = fit_image_dimensions(100, 0, 200.0, 200.0)
        assert w == 0.0
        assert h == 0.0

    def test_square_in_square_box(self):
        from oxidize_pdf import fit_image_dimensions

        w, h = fit_image_dimensions(500, 500, 100.0, 100.0)
        assert abs(w - 100.0) < 0.001
        assert abs(h - 100.0) < 0.001

    def test_exact_fit(self):
        from oxidize_pdf import fit_image_dimensions

        # Image aspect ratio matches box exactly
        w, h = fit_image_dimensions(200, 100, 200.0, 100.0)
        assert abs(w - 200.0) < 0.001
        assert abs(h - 100.0) < 0.001


class TestCenteredImageX:
    """Test centered_image_x centering calculation."""

    def test_centered_image(self):
        from oxidize_pdf import centered_image_x

        # margin_left=50, content_width=400, image_width=200 → 50 + (400-200)/2 = 150
        x = centered_image_x(50.0, 400.0, 200.0)
        assert abs(x - 150.0) < 0.001

    def test_image_fills_content_area(self):
        from oxidize_pdf import centered_image_x

        # image_width == content_width → x = margin_left
        x = centered_image_x(50.0, 200.0, 200.0)
        assert abs(x - 50.0) < 0.001

    def test_image_wider_than_content_clamps_to_margin(self):
        from oxidize_pdf import centered_image_x

        # image > content_width → .max(0.0) makes offset 0 → x = margin_left
        x = centered_image_x(50.0, 100.0, 200.0)
        assert abs(x - 50.0) < 0.001


class TestMeasureTextBlock:
    """Test measure_text_block word-wrapping metrics."""

    def test_single_line_returns_line_count_one(self):
        from oxidize_pdf import Font, measure_text_block

        m = measure_text_block("Hello", Font.HELVETICA, 12.0, 1.2, 500.0)
        assert m.line_count == 1
        assert m.width > 0.0
        assert m.height > 0.0

    def test_empty_text_returns_zero_metrics(self):
        from oxidize_pdf import Font, measure_text_block

        m = measure_text_block("", Font.HELVETICA, 12.0, 1.2, 500.0)
        assert m.line_count == 0
        assert m.width == 0.0
        assert m.height == 0.0

    def test_narrow_width_wraps_into_multiple_lines(self):
        from oxidize_pdf import Font, measure_text_block

        # "Hello World" with very narrow width forces wrapping
        m = measure_text_block("Hello World", Font.HELVETICA, 12.0, 1.2, 40.0)
        assert m.line_count >= 2

    def test_height_equals_line_count_times_font_size_times_line_height(self):
        from oxidize_pdf import Font, measure_text_block

        m = measure_text_block("Hello", Font.HELVETICA, 12.0, 1.5, 500.0)
        expected_height = 1 * 12.0 * 1.5
        assert abs(m.height - expected_height) < 0.001

    def test_width_does_not_exceed_max_width(self):
        from oxidize_pdf import Font, measure_text_block

        m = measure_text_block(
            "A fairly long sentence that should wrap", Font.HELVETICA, 12.0, 1.2, 100.0
        )
        assert m.width <= 100.0 + 0.1  # small tolerance for glyph rounding


# ── Ciclo 2: TextSpan + RichText ───────────────────────────────────────────


class TestTextSpan:
    """Test TextSpan construction and measurement."""

    def test_new_creates_span(self):
        from oxidize_pdf import Color, Font, TextSpan

        span = TextSpan("Hello", Font.HELVETICA, 12.0, Color.black())
        assert isinstance(span, TextSpan)

    def test_measure_width_positive_for_nonempty(self):
        from oxidize_pdf import Color, Font, TextSpan

        span = TextSpan("Hello", Font.HELVETICA, 12.0, Color.black())
        assert span.measure_width() > 0.0

    def test_measure_width_zero_for_empty(self):
        from oxidize_pdf import Color, Font, TextSpan

        span = TextSpan("", Font.HELVETICA, 12.0, Color.black())
        assert span.measure_width() == 0.0

    def test_larger_font_produces_wider_span(self):
        from oxidize_pdf import Color, Font, TextSpan

        small = TextSpan("Test", Font.HELVETICA, 10.0, Color.black())
        large = TextSpan("Test", Font.HELVETICA, 20.0, Color.black())
        assert large.measure_width() > small.measure_width()


class TestRichText:
    """Test RichText composition of multiple spans."""

    def test_new_with_spans(self):
        from oxidize_pdf import Color, Font, RichText, TextSpan

        spans = [
            TextSpan("Total: ", Font.HELVETICA_BOLD, 14.0, Color.black()),
            TextSpan("$100", Font.HELVETICA, 14.0, Color.gray(0.3)),
        ]
        rt = RichText(spans)
        assert isinstance(rt, RichText)

    def test_total_width_is_sum_of_spans(self):
        from oxidize_pdf import Color, Font, RichText, TextSpan

        s1 = TextSpan("A", Font.HELVETICA, 12.0, Color.black())
        s2 = TextSpan("B", Font.HELVETICA, 12.0, Color.black())
        w1 = TextSpan("A", Font.HELVETICA, 12.0, Color.black()).measure_width()
        w2 = TextSpan("B", Font.HELVETICA, 12.0, Color.black()).measure_width()
        rt = RichText([s1, s2])
        assert abs(rt.total_width() - (w1 + w2)) < 0.001

    def test_max_font_size_returns_largest(self):
        from oxidize_pdf import Color, Font, RichText, TextSpan

        spans = [
            TextSpan("small", Font.HELVETICA, 10.0, Color.black()),
            TextSpan("big", Font.HELVETICA, 18.0, Color.black()),
        ]
        rt = RichText(spans)
        assert rt.max_font_size() == 18.0

    def test_empty_rich_text(self):
        from oxidize_pdf import RichText

        rt = RichText([])
        assert rt.total_width() == 0.0
        assert rt.max_font_size() == 0.0


# ── Ciclo 3: FlowLayout ───────────────────────────────────────────────────


class TestFlowLayout:
    """Test FlowLayout automatic page layout with page breaks."""

    def test_build_creates_valid_pdf(self):
        from oxidize_pdf import Document, FlowLayout, Font, PageConfig

        layout = FlowLayout(PageConfig.a4())
        layout.add_text("Hello World", Font.HELVETICA, 12.0)
        doc = Document()
        layout.build_into(doc)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
        assert len(data) > 100

    def test_single_page_for_short_content(self):
        from oxidize_pdf import Document, FlowLayout, Font, PageConfig

        layout = FlowLayout(PageConfig.a4())
        layout.add_text("Short text", Font.HELVETICA, 12.0)
        doc = Document()
        layout.build_into(doc)
        assert doc.page_count == 1

    def test_add_spacer(self):
        from oxidize_pdf import Document, FlowLayout, Font, PageConfig

        layout = FlowLayout(PageConfig.a4())
        layout.add_spacer(20.0)
        layout.add_text("After spacer", Font.HELVETICA, 12.0)
        doc = Document()
        layout.build_into(doc)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_add_table(self):
        from oxidize_pdf import Document, FlowLayout, Font, PageConfig, Table

        layout = FlowLayout(PageConfig.a4())
        table = Table([100.0, 100.0])
        table.add_header_row(["A", "B"])
        table.add_row(["1", "2"])
        layout.add_table(table)
        doc = Document()
        layout.build_into(doc)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_page_break_for_tall_content(self):
        from oxidize_pdf import Document, FlowLayout, Font, PageConfig

        layout = FlowLayout(PageConfig.a4_with_margins(72.0, 72.0, 72.0, 72.0))
        # usable_height ~698pt, each line ~14.4pt → 70 lines should overflow
        for _ in range(70):
            layout.add_text(
                "Line of text that fills the page to force a break",
                Font.HELVETICA,
                12.0,
            )
        doc = Document()
        layout.build_into(doc)
        assert doc.page_count >= 2

    def test_add_rich_text(self):
        from oxidize_pdf import (
            Color, Document, FlowLayout, Font, PageConfig, RichText, TextSpan,
        )

        spans = [TextSpan("Bold", Font.HELVETICA_BOLD, 14.0, Color.black())]
        rt = RichText(spans)
        layout = FlowLayout(PageConfig.a4())
        layout.add_rich_text(rt)
        doc = Document()
        layout.build_into(doc)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_add_text_with_line_height(self):
        from oxidize_pdf import Document, FlowLayout, Font, PageConfig

        layout = FlowLayout(PageConfig.a4())
        layout.add_text_with_line_height("Hello", Font.HELVETICA, 12.0, 1.5)
        doc = Document()
        layout.build_into(doc)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_multiple_elements_combined(self):
        from oxidize_pdf import (
            Color, Document, FlowLayout, Font, PageConfig, RichText, Table, TextSpan,
        )

        layout = FlowLayout(PageConfig.a4())
        layout.add_text("Title", Font.HELVETICA_BOLD, 18.0)
        layout.add_spacer(10.0)
        layout.add_text("Body paragraph", Font.HELVETICA, 12.0)
        layout.add_spacer(10.0)
        table = Table([150.0, 150.0])
        table.add_header_row(["Name", "Value"])
        table.add_row(["A", "1"])
        layout.add_table(table)
        layout.add_spacer(10.0)
        rt = RichText([
            TextSpan("Note: ", Font.HELVETICA_BOLD, 10.0, Color.black()),
            TextSpan("see appendix", Font.HELVETICA, 10.0, Color.gray(0.4)),
        ])
        layout.add_rich_text(rt)
        doc = Document()
        layout.build_into(doc)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
        assert doc.page_count >= 1
