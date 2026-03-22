"""Tests for Tier 3 — Advanced Graphics (Features 11-15)."""

import pytest


# ── Feature 11: Line Cap, Join, Miter ─────────────────────────────────────


class TestLineCap:
    def test_line_cap_variants(self):
        from oxidize_pdf import LineCap

        assert LineCap.BUTT is not None
        assert LineCap.ROUND is not None
        assert LineCap.SQUARE is not None

    def test_set_line_cap_renders(self):
        from oxidize_pdf import Document, LineCap, Page

        page = Page.a4()
        page.set_line_cap(LineCap.ROUND)
        page.set_line_width(3.0)
        page.move_to(100.0, 700.0)
        page.line_to(300.0, 700.0)
        page.stroke()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


class TestLineJoin:
    def test_line_join_variants(self):
        from oxidize_pdf import LineJoin

        assert LineJoin.MITER is not None
        assert LineJoin.ROUND is not None
        assert LineJoin.BEVEL is not None

    def test_set_line_join_renders(self):
        from oxidize_pdf import Document, LineJoin, Page

        page = Page.a4()
        page.set_line_join(LineJoin.BEVEL)
        page.set_line_width(3.0)
        page.move_to(100.0, 700.0)
        page.line_to(200.0, 750.0)
        page.line_to(300.0, 700.0)
        page.stroke()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


class TestMiterLimit:
    def test_set_miter_limit(self):
        from oxidize_pdf import Document, Page

        page = Page.a4()
        page.set_miter_limit(4.0)
        page.move_to(100.0, 700.0)
        page.line_to(200.0, 750.0)
        page.stroke()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


# ── Feature 12: Dash Patterns ─────────────────────────────────────────────


class TestDashPattern:
    def test_dash_pattern_custom(self):
        from oxidize_pdf import LineDashPattern

        p = LineDashPattern([5.0, 3.0], 0.0)
        assert isinstance(p, LineDashPattern)

    def test_dash_pattern_solid(self):
        from oxidize_pdf import LineDashPattern

        p = LineDashPattern.solid()
        assert isinstance(p, LineDashPattern)

    def test_set_dash_pattern_renders(self):
        from oxidize_pdf import Document, LineDashPattern, Page

        page = Page.a4()
        page.set_dash_pattern(LineDashPattern([5.0, 3.0], 0.0))
        page.set_line_width(1.0)
        page.move_to(100.0, 700.0)
        page.line_to(400.0, 700.0)
        page.stroke()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


# ── Feature 13: Graphics Save/Restore ─────────────────────────────────────


class TestGraphicsSaveRestore:
    def test_save_restore_state(self):
        from oxidize_pdf import Color, Document, Page

        page = Page.a4()
        page.save_graphics_state()
        page.set_fill_color(Color.rgb(1.0, 0.0, 0.0))
        page.draw_rect(100.0, 700.0, 100.0, 50.0)
        page.fill()
        page.restore_graphics_state()

        page.draw_rect(100.0, 600.0, 100.0, 50.0)
        page.fill()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


# ── Feature 14: Clipping Paths ────────────────────────────────────────────


class TestClippingPath:
    def test_clipping_path_rect(self):
        from oxidize_pdf import ClippingPath

        cp = ClippingPath.rect(50.0, 50.0, 200.0, 200.0)
        assert isinstance(cp, ClippingPath)

    def test_clipping_path_circle(self):
        from oxidize_pdf import ClippingPath

        cp = ClippingPath.circle(150.0, 150.0, 100.0)
        assert isinstance(cp, ClippingPath)

    def test_set_clipping_path_renders(self):
        from oxidize_pdf import ClippingPath, Color, Document, Page

        page = Page.a4()
        page.set_clipping_path(ClippingPath.rect(100.0, 600.0, 200.0, 200.0))
        page.set_fill_color(Color.rgb(0.0, 0.0, 1.0))
        page.draw_rect(0.0, 0.0, 595.0, 842.0)
        page.fill()
        page.clear_clipping()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


# ── Feature 15: Blend Modes ──────────────────────────────────────────────


class TestBlendMode:
    def test_blend_mode_variants(self):
        from oxidize_pdf import BlendMode

        assert BlendMode.NORMAL is not None
        assert BlendMode.MULTIPLY is not None
        assert BlendMode.SCREEN is not None
        assert BlendMode.OVERLAY is not None
        assert BlendMode.SOFT_LIGHT is not None
        assert BlendMode.HARD_LIGHT is not None
        assert BlendMode.COLOR_DODGE is not None
        assert BlendMode.COLOR_BURN is not None
        assert BlendMode.DARKEN is not None
        assert BlendMode.LIGHTEN is not None

    def test_set_blend_mode_renders(self):
        from oxidize_pdf import BlendMode, Color, Document, Page

        page = Page.a4()
        page.set_blend_mode(BlendMode.MULTIPLY)
        page.set_fill_color(Color.rgb(1.0, 0.0, 0.0))
        page.draw_rect(100.0, 700.0, 100.0, 100.0)
        page.fill()

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
