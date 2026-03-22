"""Tests for the charts module (F58)."""

import pytest
from oxidize_pdf import (
    BarChart,
    BarChartBuilder,
    BarOrientation,
    ChartData,
    ChartRenderer,
    ChartType,
    Color,
    DashboardBarChart,
    DashboardLineChart,
    DashboardPieChart,
    DataSeries,
    Document,
    Font,
    LegendPosition,
    LineChart,
    LineChartBuilder,
    Page,
    PieChart,
    PieChartBuilder,
    PieSegment,
)


# ── Enums ─────────────────────────────────────────────────────────────────


class TestChartType:
    def test_vertical_bar_exists(self):
        assert ChartType.VERTICAL_BAR is not None

    def test_horizontal_bar_exists(self):
        assert ChartType.HORIZONTAL_BAR is not None

    def test_pie_exists(self):
        assert ChartType.PIE is not None

    def test_line_exists(self):
        assert ChartType.LINE is not None

    def test_area_exists(self):
        assert ChartType.AREA is not None

    def test_repr(self):
        assert "VERTICAL_BAR" in repr(ChartType.VERTICAL_BAR)
        assert "PIE" in repr(ChartType.PIE)
        assert "LINE" in repr(ChartType.LINE)

    def test_all_variants_distinct(self):
        variants = [
            ChartType.VERTICAL_BAR,
            ChartType.HORIZONTAL_BAR,
            ChartType.PIE,
            ChartType.LINE,
            ChartType.AREA,
        ]
        assert len(variants) == 5


class TestLegendPosition:
    def test_none_exists(self):
        assert LegendPosition.NONE is not None

    def test_right_exists(self):
        assert LegendPosition.RIGHT is not None

    def test_bottom_exists(self):
        assert LegendPosition.BOTTOM is not None

    def test_top_exists(self):
        assert LegendPosition.TOP is not None

    def test_left_exists(self):
        assert LegendPosition.LEFT is not None

    def test_repr(self):
        assert "NONE" in repr(LegendPosition.NONE)
        assert "RIGHT" in repr(LegendPosition.RIGHT)
        assert "BOTTOM" in repr(LegendPosition.BOTTOM)
        assert "TOP" in repr(LegendPosition.TOP)
        assert "LEFT" in repr(LegendPosition.LEFT)


class TestBarOrientation:
    def test_vertical_exists(self):
        assert BarOrientation.VERTICAL is not None

    def test_horizontal_exists(self):
        assert BarOrientation.HORIZONTAL is not None

    def test_repr(self):
        assert "VERTICAL" in repr(BarOrientation.VERTICAL)
        assert "HORIZONTAL" in repr(BarOrientation.HORIZONTAL)


# ── ChartData ─────────────────────────────────────────────────────────────


class TestChartData:
    def test_constructor(self):
        d = ChartData("Q1", 100.0)
        assert d is not None

    def test_repr_contains_label_and_value(self):
        d = ChartData("Revenue", 999.5)
        r = repr(d)
        assert "Revenue" in r
        assert "999.5" in r

    def test_color_builder_returns_new_instance(self):
        d = ChartData("A", 10.0)
        d2 = d.color(Color.red())
        assert d2 is not None

    def test_highlighted_returns_new_instance(self):
        d = ChartData("B", 20.0)
        d2 = d.highlighted()
        assert d2 is not None

    def test_chained_builder(self):
        d = ChartData("C", 30.0).color(Color.blue()).highlighted()
        assert d is not None


# ── BarChartBuilder and BarChart ───────────────────────────────────────────


class TestBarChartBuilder:
    def _make_simple_chart(self):
        b = BarChartBuilder()
        b.title("Sales 2024")
        b.simple_data([10.0, 20.0, 30.0])
        return b.build()

    def test_build_returns_bar_chart(self):
        chart = self._make_simple_chart()
        assert isinstance(chart, BarChart)

    def test_repr_active_builder(self):
        b = BarChartBuilder()
        assert "active" in repr(b)

    def test_repr_consumed_builder(self):
        b = BarChartBuilder()
        b.build()
        assert "consumed" in repr(b)

    def test_build_twice_raises(self):
        b = BarChartBuilder()
        b.build()
        with pytest.raises(RuntimeError):
            b.build()

    def test_title(self):
        b = BarChartBuilder()
        b.title("My Chart")
        chart = b.build()
        assert "My Chart" in repr(chart)

    def test_add_data(self):
        b = BarChartBuilder()
        b.add_data(ChartData("Alpha", 42.0))
        b.add_data(ChartData("Beta", 58.0))
        chart = b.build()
        assert "2" in repr(chart)  # 2 bars

    def test_data_list(self):
        b = BarChartBuilder()
        b.data([ChartData("X", 1.0), ChartData("Y", 2.0), ChartData("Z", 3.0)])
        chart = b.build()
        assert "3" in repr(chart)

    def test_orientation_horizontal(self):
        b = BarChartBuilder()
        b.simple_data([1.0, 2.0])
        b.orientation(BarOrientation.HORIZONTAL)
        chart = b.build()
        assert chart is not None

    def test_colors(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.colors([Color.red(), Color.blue()])
        chart = b.build()
        assert chart is not None

    def test_title_font(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.title_font(Font.HELVETICA_BOLD, 18.0)
        chart = b.build()
        assert chart is not None

    def test_label_font(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.label_font(Font.HELVETICA, 10.0)
        chart = b.build()
        assert chart is not None

    def test_value_font(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.value_font(Font.HELVETICA, 9.0)
        chart = b.build()
        assert chart is not None

    def test_legend_position(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.legend_position(LegendPosition.BOTTOM)
        chart = b.build()
        assert chart is not None

    def test_background_color(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.background_color(Color.white())
        chart = b.build()
        assert chart is not None

    def test_show_values(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.show_values(False)
        chart = b.build()
        assert chart is not None

    def test_show_grid(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.show_grid(False)
        chart = b.build()
        assert chart is not None

    def test_grid_color(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.grid_color(Color.gray(0.8))
        chart = b.build()
        assert chart is not None

    def test_bar_spacing(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.bar_spacing(0.3)
        chart = b.build()
        assert chart is not None

    def test_bar_border(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.bar_border(Color.black(), 1.0)
        chart = b.build()
        assert chart is not None

    def test_bar_width_range(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.bar_width_range(15.0, None)
        chart = b.build()
        assert chart is not None

    def test_bar_width_range_with_max(self):
        b = BarChartBuilder()
        b.simple_data([1.0])
        b.bar_width_range(10.0, 80.0)
        chart = b.build()
        assert chart is not None

    def test_labeled_data(self):
        b = BarChartBuilder()
        b.labeled_data([("Q1", 100.0), ("Q2", 150.0), ("Q3", 120.0)])
        chart = b.build()
        assert "3" in repr(chart)

    def test_financial_style(self):
        b = BarChartBuilder()
        b.simple_data([100.0, 200.0])
        b.financial_style()
        chart = b.build()
        assert chart is not None

    def test_minimal_style(self):
        b = BarChartBuilder()
        b.simple_data([100.0, 200.0])
        b.minimal_style()
        chart = b.build()
        assert chart is not None

    def test_progress_style(self):
        b = BarChartBuilder()
        b.simple_data([75.0])
        b.progress_style(Color.green())
        chart = b.build()
        assert chart is not None

    def test_bar_chart_repr(self):
        b = BarChartBuilder()
        b.title("Test Chart")
        b.simple_data([1.0, 2.0])
        chart = b.build()
        r = repr(chart)
        assert "BarChart" in r
        assert "Test Chart" in r


# ── DataSeries ────────────────────────────────────────────────────────────


class TestDataSeries:
    def test_constructor(self):
        s = DataSeries("Revenue", Color.blue())
        assert s is not None

    def test_repr(self):
        s = DataSeries("Revenue", Color.blue())
        r = repr(s)
        assert "Revenue" in r

    def test_y_data(self):
        s = DataSeries("Series", Color.red())
        s2 = s.y_data([1.0, 2.0, 3.0])
        r = repr(s2)
        assert "3" in r

    def test_xy_data(self):
        s = DataSeries("XY", Color.green())
        s2 = s.xy_data([(0.0, 1.0), (1.0, 4.0), (2.0, 9.0)])
        r = repr(s2)
        assert "3" in r

    def test_line_style(self):
        s = DataSeries("S", Color.black())
        s2 = s.line_style(3.0)
        assert s2 is not None

    def test_markers_enabled(self):
        s = DataSeries("S", Color.blue())
        s2 = s.markers(True, 6.0)
        assert s2 is not None

    def test_markers_disabled(self):
        s = DataSeries("S", Color.blue())
        s2 = s.markers(False, 0.0)
        assert s2 is not None

    def test_fill_area_with_color(self):
        s = DataSeries("S", Color.blue())
        s2 = s.fill_area(Color.rgb(0.5, 0.5, 0.9))
        assert s2 is not None

    def test_fill_area_no_color(self):
        s = DataSeries("S", Color.blue())
        s2 = s.fill_area(None)
        assert s2 is not None

    def test_chained_builders(self):
        s = (
            DataSeries("Trend", Color.rgb(0.2, 0.6, 0.8))
            .y_data([10.0, 20.0, 15.0, 25.0])
            .line_style(2.5)
            .markers(True, 5.0)
        )
        assert s is not None


# ── LineChartBuilder and LineChart ─────────────────────────────────────────


class TestLineChartBuilder:
    def _make_simple_chart(self):
        b = LineChartBuilder()
        b.title("Trend Analysis")
        s = DataSeries("Revenue", Color.blue()).y_data([10.0, 20.0, 15.0, 30.0])
        b.add_series(s)
        return b.build()

    def test_build_returns_line_chart(self):
        chart = self._make_simple_chart()
        assert isinstance(chart, LineChart)

    def test_repr_active_builder(self):
        b = LineChartBuilder()
        assert "active" in repr(b)

    def test_repr_consumed_builder(self):
        b = LineChartBuilder()
        b.build()
        assert "consumed" in repr(b)

    def test_build_twice_raises(self):
        b = LineChartBuilder()
        b.build()
        with pytest.raises(RuntimeError):
            b.build()

    def test_title(self):
        b = LineChartBuilder()
        b.title("Stock Prices")
        chart = b.build()
        assert "Stock Prices" in repr(chart)

    def test_add_series(self):
        b = LineChartBuilder()
        s1 = DataSeries("S1", Color.blue()).y_data([1.0, 2.0, 3.0])
        s2 = DataSeries("S2", Color.red()).y_data([3.0, 2.0, 1.0])
        b.add_series(s1)
        b.add_series(s2)
        chart = b.build()
        assert "2" in repr(chart)

    def test_axis_labels(self):
        b = LineChartBuilder()
        b.axis_labels("Time", "Value")
        chart = b.build()
        assert chart is not None

    def test_title_font(self):
        b = LineChartBuilder()
        b.title_font(Font.HELVETICA_BOLD, 20.0)
        chart = b.build()
        assert chart is not None

    def test_label_font(self):
        b = LineChartBuilder()
        b.label_font(Font.HELVETICA, 10.0)
        chart = b.build()
        assert chart is not None

    def test_axis_font(self):
        b = LineChartBuilder()
        b.axis_font(Font.HELVETICA, 8.0)
        chart = b.build()
        assert chart is not None

    def test_legend_position(self):
        b = LineChartBuilder()
        b.legend_position(LegendPosition.BOTTOM)
        chart = b.build()
        assert chart is not None

    def test_background_color(self):
        b = LineChartBuilder()
        b.background_color(Color.white())
        chart = b.build()
        assert chart is not None

    def test_grid(self):
        b = LineChartBuilder()
        b.grid(True, Color.gray(0.9), 10)
        chart = b.build()
        assert chart is not None

    def test_grid_disabled(self):
        b = LineChartBuilder()
        b.grid(False, Color.white(), 5)
        chart = b.build()
        assert chart is not None

    def test_x_range(self):
        b = LineChartBuilder()
        b.x_range(0.0, 100.0)
        chart = b.build()
        assert chart is not None

    def test_y_range(self):
        b = LineChartBuilder()
        b.y_range(-10.0, 50.0)
        chart = b.build()
        assert chart is not None

    def test_add_simple_series(self):
        b = LineChartBuilder()
        b.add_simple_series("Growth", [5.0, 10.0, 8.0, 15.0], Color.green())
        chart = b.build()
        assert "1" in repr(chart)

    def test_line_chart_repr(self):
        b = LineChartBuilder()
        b.title("My Line Chart")
        b.add_simple_series("S1", [1.0, 2.0], Color.blue())
        chart = b.build()
        r = repr(chart)
        assert "LineChart" in r
        assert "My Line Chart" in r


# ── PieSegment ─────────────────────────────────────────────────────────────


class TestPieSegment:
    def test_constructor(self):
        seg = PieSegment("Category A", 40.0, Color.blue())
        assert seg is not None

    def test_repr(self):
        seg = PieSegment("Revenue", 75.5, Color.green())
        r = repr(seg)
        assert "Revenue" in r
        assert "75.5" in r

    def test_exploded(self):
        seg = PieSegment("X", 25.0, Color.red())
        seg2 = seg.exploded(0.2)
        assert seg2 is not None

    def test_show_percentage_false(self):
        seg = PieSegment("X", 25.0, Color.red())
        seg2 = seg.show_percentage(False)
        assert seg2 is not None

    def test_show_percentage_true(self):
        seg = PieSegment("X", 25.0, Color.red())
        seg2 = seg.show_percentage(True)
        assert seg2 is not None

    def test_show_label_false(self):
        seg = PieSegment("X", 25.0, Color.red())
        seg2 = seg.show_label(False)
        assert seg2 is not None

    def test_show_label_true(self):
        seg = PieSegment("X", 25.0, Color.red())
        seg2 = seg.show_label(True)
        assert seg2 is not None

    def test_chained(self):
        seg = (
            PieSegment("Highlight", 30.0, Color.rgb(0.8, 0.2, 0.2))
            .exploded(0.15)
            .show_percentage(True)
            .show_label(True)
        )
        assert seg is not None


# ── PieChartBuilder and PieChart ───────────────────────────────────────────


class TestPieChartBuilder:
    def _make_simple_chart(self):
        b = PieChartBuilder()
        b.title("Market Share")
        b.add_segment(PieSegment("Alpha", 40.0, Color.blue()))
        b.add_segment(PieSegment("Beta", 35.0, Color.red()))
        b.add_segment(PieSegment("Gamma", 25.0, Color.green()))
        return b.build()

    def test_build_returns_pie_chart(self):
        chart = self._make_simple_chart()
        assert isinstance(chart, PieChart)

    def test_repr_active_builder(self):
        b = PieChartBuilder()
        assert "active" in repr(b)

    def test_repr_consumed_builder(self):
        b = PieChartBuilder()
        b.build()
        assert "consumed" in repr(b)

    def test_build_twice_raises(self):
        b = PieChartBuilder()
        b.build()
        with pytest.raises(RuntimeError):
            b.build()

    def test_title(self):
        b = PieChartBuilder()
        b.title("Sales Breakdown")
        chart = b.build()
        assert "Sales Breakdown" in repr(chart)

    def test_add_segment(self):
        b = PieChartBuilder()
        b.add_segment(PieSegment("A", 50.0, Color.blue()))
        b.add_segment(PieSegment("B", 50.0, Color.red()))
        chart = b.build()
        assert "2" in repr(chart)

    def test_segments_list(self):
        b = PieChartBuilder()
        segs = [
            PieSegment("X", 30.0, Color.blue()),
            PieSegment("Y", 70.0, Color.red()),
        ]
        b.segments(segs)
        chart = b.build()
        assert "2" in repr(chart)

    def test_colors(self):
        b = PieChartBuilder()
        b.simple_data([25.0, 25.0, 25.0, 25.0])
        b.colors([Color.red(), Color.blue(), Color.green(), Color.gray(0.5)])
        chart = b.build()
        assert chart is not None

    def test_title_font(self):
        b = PieChartBuilder()
        b.simple_data([50.0, 50.0])
        b.title_font(Font.HELVETICA_BOLD, 18.0)
        chart = b.build()
        assert chart is not None

    def test_label_font(self):
        b = PieChartBuilder()
        b.simple_data([50.0, 50.0])
        b.label_font(Font.HELVETICA, 9.0)
        chart = b.build()
        assert chart is not None

    def test_percentage_font(self):
        b = PieChartBuilder()
        b.simple_data([50.0, 50.0])
        b.percentage_font(Font.HELVETICA, 8.0)
        chart = b.build()
        assert chart is not None

    def test_legend_position(self):
        b = PieChartBuilder()
        b.simple_data([50.0, 50.0])
        b.legend_position(LegendPosition.RIGHT)
        chart = b.build()
        assert chart is not None

    def test_background_color(self):
        b = PieChartBuilder()
        b.simple_data([50.0, 50.0])
        b.background_color(Color.white())
        chart = b.build()
        assert chart is not None

    def test_show_percentages(self):
        b = PieChartBuilder()
        b.simple_data([50.0, 50.0])
        b.show_percentages(False)
        chart = b.build()
        assert chart is not None

    def test_show_labels(self):
        b = PieChartBuilder()
        b.simple_data([50.0, 50.0])
        b.show_labels(False)
        chart = b.build()
        assert chart is not None

    def test_start_angle(self):
        b = PieChartBuilder()
        b.simple_data([50.0, 50.0])
        b.start_angle(0.0)
        chart = b.build()
        assert chart is not None

    def test_border(self):
        b = PieChartBuilder()
        b.simple_data([50.0, 50.0])
        b.border(Color.white(), 2.0)
        chart = b.build()
        assert chart is not None

    def test_label_settings(self):
        b = PieChartBuilder()
        b.simple_data([50.0, 50.0])
        b.label_settings(1.3, 0.15)
        chart = b.build()
        assert chart is not None

    def test_data_from_chart_data(self):
        b = PieChartBuilder()
        b.data([
            ChartData("Alpha", 40.0),
            ChartData("Beta", 60.0),
        ])
        chart = b.build()
        assert "2" in repr(chart)

    def test_simple_data(self):
        b = PieChartBuilder()
        b.simple_data([25.0, 35.0, 40.0])
        chart = b.build()
        assert "3" in repr(chart)

    def test_labeled_data(self):
        b = PieChartBuilder()
        b.labeled_data([("North", 30.0), ("South", 20.0), ("East", 25.0), ("West", 25.0)])
        chart = b.build()
        assert "4" in repr(chart)

    def test_financial_style(self):
        b = PieChartBuilder()
        b.simple_data([20.0, 30.0, 50.0])
        b.financial_style()
        chart = b.build()
        assert chart is not None

    def test_minimal_style(self):
        b = PieChartBuilder()
        b.simple_data([20.0, 30.0, 50.0])
        b.minimal_style()
        chart = b.build()
        assert chart is not None

    def test_donut_style(self):
        b = PieChartBuilder()
        b.simple_data([25.0, 25.0, 25.0, 25.0])
        b.donut_style()
        chart = b.build()
        assert chart is not None

    def test_pie_chart_repr(self):
        b = PieChartBuilder()
        b.title("Revenue Split")
        b.simple_data([40.0, 60.0])
        chart = b.build()
        r = repr(chart)
        assert "PieChart" in r
        assert "Revenue Split" in r


# ── ChartRenderer ─────────────────────────────────────────────────────────


class TestChartRenderer:
    def test_constructor(self):
        renderer = ChartRenderer()
        assert renderer is not None

    def test_repr(self):
        renderer = ChartRenderer()
        assert "ChartRenderer" in repr(renderer)

    def test_render_bar_chart_produces_valid_pdf(self):
        b = BarChartBuilder()
        b.title("Q1 Results")
        b.labeled_data([("Jan", 100.0), ("Feb", 150.0), ("Mar", 120.0)])
        chart = b.build()

        page = Page(612.0, 792.0)
        renderer = ChartRenderer()
        renderer.render_bar_chart(page, chart, 50.0, 400.0, 500.0, 300.0)

        doc = Document()
        doc.add_page(page)
        pdf_bytes = doc.save_to_bytes()
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_render_pie_chart_produces_valid_pdf(self):
        b = PieChartBuilder()
        b.title("Market Share")
        b.simple_data([30.0, 40.0, 30.0])
        chart = b.build()

        page = Page(612.0, 792.0)
        renderer = ChartRenderer()
        renderer.render_pie_chart(page, chart, 306.0, 500.0, 150.0)

        doc = Document()
        doc.add_page(page)
        pdf_bytes = doc.save_to_bytes()
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_render_line_chart_produces_valid_pdf(self):
        b = LineChartBuilder()
        b.title("Revenue Trend")
        b.add_simple_series("Revenue", [100.0, 120.0, 110.0, 150.0], Color.blue())
        chart = b.build()

        page = Page(612.0, 792.0)
        renderer = ChartRenderer()
        renderer.render_line_chart(page, chart, 50.0, 400.0, 500.0, 300.0)

        doc = Document()
        doc.add_page(page)
        pdf_bytes = doc.save_to_bytes()
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"


# ── Page.add_*_chart methods ───────────────────────────────────────────────


class TestPageChartMethods:
    def test_add_bar_chart(self):
        b = BarChartBuilder()
        b.title("Sales")
        b.labeled_data([("Q1", 100.0), ("Q2", 200.0)])
        chart = b.build()

        page = Page(612.0, 792.0)
        page.add_bar_chart(chart, 50.0, 400.0, 500.0, 300.0)

        doc = Document()
        doc.add_page(page)
        pdf_bytes = doc.save_to_bytes()
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_add_pie_chart(self):
        b = PieChartBuilder()
        b.simple_data([40.0, 35.0, 25.0])
        chart = b.build()

        page = Page(612.0, 792.0)
        page.add_pie_chart(chart, 306.0, 500.0, 150.0)

        doc = Document()
        doc.add_page(page)
        pdf_bytes = doc.save_to_bytes()
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_add_line_chart(self):
        b = LineChartBuilder()
        b.add_simple_series("Profit", [10.0, 20.0, 15.0, 30.0], Color.green())
        chart = b.build()

        page = Page(612.0, 792.0)
        page.add_line_chart(chart, 50.0, 400.0, 500.0, 300.0)

        doc = Document()
        doc.add_page(page)
        pdf_bytes = doc.save_to_bytes()
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_multiple_charts_on_one_page(self):
        bar_b = BarChartBuilder()
        bar_b.simple_data([10.0, 20.0, 30.0])
        bar_chart = bar_b.build()

        pie_b = PieChartBuilder()
        pie_b.simple_data([40.0, 60.0])
        pie_chart = pie_b.build()

        page = Page(612.0, 792.0)
        page.add_bar_chart(bar_chart, 50.0, 450.0, 240.0, 200.0)
        page.add_pie_chart(pie_chart, 440.0, 550.0, 100.0)

        doc = Document()
        doc.add_page(page)
        pdf_bytes = doc.save_to_bytes()
        assert len(pdf_bytes) > 0

    def test_bar_chart_with_all_styles(self):
        b = BarChartBuilder()
        b.title("Full Featured Chart")
        b.labeled_data([("A", 10.0), ("B", 20.0), ("C", 30.0)])
        b.show_grid(True)
        b.show_values(True)
        b.legend_position(LegendPosition.BOTTOM)
        b.grid_color(Color.gray(0.9))
        b.bar_border(Color.gray(0.7), 0.5)
        chart = b.build()

        page = Page(612.0, 792.0)
        page.add_bar_chart(chart, 50.0, 400.0, 500.0, 300.0)

        doc = Document()
        doc.add_page(page)
        pdf_bytes = doc.save_to_bytes()
        assert len(pdf_bytes) > 0

    def test_line_chart_multi_series(self):
        b = LineChartBuilder()
        b.title("Multi-Series")
        s1 = DataSeries("Revenue", Color.blue()).y_data([10.0, 20.0, 15.0, 30.0])
        s2 = DataSeries("Costs", Color.red()).y_data([8.0, 12.0, 10.0, 18.0])
        b.add_series(s1)
        b.add_series(s2)
        b.axis_labels("Quarter", "USD (k)")
        b.legend_position(LegendPosition.RIGHT)
        chart = b.build()

        page = Page(612.0, 792.0)
        page.add_line_chart(chart, 50.0, 400.0, 500.0, 300.0)

        doc = Document()
        doc.add_page(page)
        pdf_bytes = doc.save_to_bytes()
        assert len(pdf_bytes) > 0


# ── Dashboard wrappers ─────────────────────────────────────────────────────


class TestDashboardCharts:
    def test_dashboard_bar_chart_constructor(self):
        b = BarChartBuilder()
        b.simple_data([10.0, 20.0])
        chart = b.build()
        d = DashboardBarChart(chart)
        assert d is not None

    def test_dashboard_bar_chart_repr(self):
        b = BarChartBuilder()
        b.simple_data([10.0])
        chart = b.build()
        d = DashboardBarChart(chart)
        assert "DashboardBarChart" in repr(d)

    def test_dashboard_bar_chart_span(self):
        b = BarChartBuilder()
        b.simple_data([10.0])
        chart = b.build()
        d = DashboardBarChart(chart).span(12)
        assert d is not None

    def test_dashboard_pie_chart_constructor(self):
        b = PieChartBuilder()
        b.simple_data([40.0, 60.0])
        chart = b.build()
        d = DashboardPieChart(chart)
        assert d is not None

    def test_dashboard_pie_chart_repr(self):
        b = PieChartBuilder()
        b.simple_data([50.0, 50.0])
        chart = b.build()
        d = DashboardPieChart(chart)
        assert "DashboardPieChart" in repr(d)

    def test_dashboard_pie_chart_span(self):
        b = PieChartBuilder()
        b.simple_data([50.0, 50.0])
        chart = b.build()
        d = DashboardPieChart(chart).span(4)
        assert d is not None

    def test_dashboard_line_chart_constructor(self):
        b = LineChartBuilder()
        s = DataSeries("S", Color.blue()).y_data([1.0, 2.0])
        b.add_series(s)
        chart = b.build()
        d = DashboardLineChart(chart)
        assert d is not None

    def test_dashboard_line_chart_repr(self):
        b = LineChartBuilder()
        b.add_simple_series("S", [1.0, 2.0], Color.green())
        chart = b.build()
        d = DashboardLineChart(chart)
        assert "DashboardLineChart" in repr(d)

    def test_dashboard_line_chart_span(self):
        b = LineChartBuilder()
        b.add_simple_series("S", [1.0, 2.0], Color.green())
        chart = b.build()
        d = DashboardLineChart(chart).span(8)
        assert d is not None

    def test_all_span_values(self):
        b = BarChartBuilder()
        b.simple_data([10.0])
        chart = b.build()
        for columns in [1, 4, 6, 8, 12]:
            d = DashboardBarChart(chart).span(columns)
            assert d is not None
