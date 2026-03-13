"""Tests for graphics drawing operations on pages."""

import pytest


class TestGraphicsPrimitives:
    """Test basic shape drawing."""

    def test_draw_rect_and_fill(self):
        from oxidize_pdf import Color, Document, Page

        page = Page.a4()
        page.set_fill_color(Color.red())
        page.draw_rect(100.0, 100.0, 200.0, 150.0)
        page.fill()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_draw_circle_and_stroke(self):
        from oxidize_pdf import Color, Document, Page

        page = Page.a4()
        page.set_stroke_color(Color.blue())
        page.draw_circle(300.0, 400.0, 50.0)
        page.stroke()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_draw_line(self):
        from oxidize_pdf import Document, Page

        page = Page.a4()
        page.set_line_width(2.0)
        page.move_to(50.0, 50.0)
        page.line_to(500.0, 700.0)
        page.stroke()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0


class TestGraphicsPath:
    """Test path construction operations."""

    def test_triangle_path(self):
        from oxidize_pdf import Color, Document, Page

        page = Page.a4()
        page.set_fill_color(Color.green())
        page.move_to(300.0, 700.0)
        page.line_to(200.0, 500.0)
        page.line_to(400.0, 500.0)
        page.close_path()
        page.fill()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_curve_to(self):
        from oxidize_pdf import Document, Page

        page = Page.a4()
        page.move_to(100.0, 400.0)
        page.curve_to(150.0, 500.0, 250.0, 500.0, 300.0, 400.0)
        page.stroke()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_fill_and_stroke(self):
        from oxidize_pdf import Color, Document, Page

        page = Page.a4()
        page.set_fill_color(Color.rgb(0.9, 0.9, 0.0))
        page.set_stroke_color(Color.black())
        page.set_line_width(3.0)
        page.draw_rect(100.0, 100.0, 200.0, 200.0)
        page.fill_and_stroke()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0


class TestGraphicsState:
    """Test graphics state operations."""

    def test_fill_opacity(self):
        from oxidize_pdf import Color, Document, Page

        page = Page.a4()
        page.set_fill_color(Color.red())
        page.set_fill_opacity(0.5)
        page.draw_rect(100.0, 100.0, 200.0, 200.0)
        page.fill()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_stroke_opacity(self):
        from oxidize_pdf import Color, Document, Page

        page = Page.a4()
        page.set_stroke_color(Color.blue())
        page.set_stroke_opacity(0.3)
        page.draw_circle(300.0, 400.0, 100.0)
        page.stroke()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert len(data) > 0

    def test_combined_text_and_graphics(self):
        """Verify text and graphics coexist on the same page."""
        from oxidize_pdf import Color, Document, Font, Page

        page = Page.a4()

        # Draw background
        page.set_fill_color(Color.rgb(0.95, 0.95, 1.0))
        page.draw_rect(50.0, 50.0, 495.0, 742.0)
        page.fill()

        # Draw border
        page.set_stroke_color(Color.black())
        page.set_line_width(1.0)
        page.draw_rect(50.0, 50.0, 495.0, 742.0)
        page.stroke()

        # Write text
        page.set_font(Font.HELVETICA_BOLD, 24.0)
        page.set_text_color(Color.black())
        page.text_at(100.0, 750.0, "Title")

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
        assert len(data) > 200
