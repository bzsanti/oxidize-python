"""Tests for oxidize_pdf base types: Color, Point, Rectangle, Margins."""

import pytest


class TestColor:
    """Test the Color type."""

    def test_rgb_constructor(self):
        from oxidize_pdf import Color

        c = Color.rgb(1.0, 0.0, 0.0)
        assert c.r == 1.0
        assert c.g == 0.0
        assert c.b == 0.0

    def test_gray_constructor(self):
        from oxidize_pdf import Color

        c = Color.gray(0.5)
        assert c.gray_value == 0.5

    def test_cmyk_constructor(self):
        from oxidize_pdf import Color

        c = Color.cmyk(1.0, 0.0, 0.5, 0.2)
        assert c.c == 1.0
        assert c.m == 0.0
        assert c.y == 0.5
        assert c.k == 0.2

    def test_hex_constructor(self):
        from oxidize_pdf import Color

        c = Color.hex("#FF0000")
        assert abs(c.r - 1.0) < 0.01
        assert abs(c.g - 0.0) < 0.01
        assert abs(c.b - 0.0) < 0.01

    def test_named_colors(self):
        from oxidize_pdf import Color

        black = Color.black()
        white = Color.white()
        red = Color.red()
        green = Color.green()
        blue = Color.blue()

        assert black.gray_value == 0.0
        assert white.gray_value == 1.0
        assert red.r == 1.0 and red.g == 0.0 and red.b == 0.0
        assert green.r == 0.0 and green.g == 1.0 and green.b == 0.0
        assert blue.r == 0.0 and blue.g == 0.0 and blue.b == 1.0

    def test_values_are_clamped(self):
        from oxidize_pdf import Color

        c = Color.rgb(2.0, -1.0, 0.5)
        assert c.r == 1.0
        assert c.g == 0.0
        assert c.b == 0.5

    def test_repr_contains_color(self):
        from oxidize_pdf import Color

        c = Color.rgb(1.0, 0.0, 0.0)
        assert "Color" in repr(c)

    def test_color_space_property(self):
        from oxidize_pdf import Color

        assert Color.rgb(1.0, 0.0, 0.0).color_space == "RGB"
        assert Color.gray(0.5).color_space == "Gray"
        assert Color.cmyk(0.0, 0.0, 0.0, 1.0).color_space == "CMYK"


class TestPoint:
    """Test the Point type."""

    def test_constructor(self):
        from oxidize_pdf import Point

        p = Point(10.0, 20.0)
        assert p.x == 10.0
        assert p.y == 20.0

    def test_origin(self):
        from oxidize_pdf import Point

        p = Point.origin()
        assert p.x == 0.0
        assert p.y == 0.0

    def test_negative_coordinates(self):
        from oxidize_pdf import Point

        p = Point(-5.0, -10.0)
        assert p.x == -5.0
        assert p.y == -10.0

    def test_repr(self):
        from oxidize_pdf import Point

        p = Point(1.0, 2.0)
        r = repr(p)
        assert "Point" in r
        assert "1" in r
        assert "2" in r

    def test_equality(self):
        from oxidize_pdf import Point

        p1 = Point(1.0, 2.0)
        p2 = Point(1.0, 2.0)
        p3 = Point(3.0, 4.0)
        assert p1 == p2
        assert p1 != p3


class TestRectangle:
    """Test the Rectangle type."""

    def test_constructor(self):
        from oxidize_pdf import Point, Rectangle

        r = Rectangle(Point(0.0, 0.0), Point(10.0, 20.0))
        assert r.width == 10.0
        assert r.height == 20.0

    def test_from_xywh(self):
        from oxidize_pdf import Rectangle

        r = Rectangle.from_xywh(5.0, 10.0, 100.0, 200.0)
        assert r.width == 100.0
        assert r.height == 200.0

    def test_lower_left_upper_right(self):
        from oxidize_pdf import Point, Rectangle

        r = Rectangle(Point(5.0, 10.0), Point(15.0, 30.0))
        assert r.lower_left.x == 5.0
        assert r.lower_left.y == 10.0
        assert r.upper_right.x == 15.0
        assert r.upper_right.y == 30.0

    def test_center(self):
        from oxidize_pdf import Point, Rectangle

        r = Rectangle(Point(0.0, 0.0), Point(10.0, 20.0))
        c = r.center
        assert c.x == 5.0
        assert c.y == 10.0

    def test_repr(self):
        from oxidize_pdf import Point, Rectangle

        r = Rectangle(Point(0.0, 0.0), Point(10.0, 20.0))
        assert "Rectangle" in repr(r)


class TestMargins:
    """Test the Margins type."""

    def test_constructor_kwargs(self):
        from oxidize_pdf import Margins

        m = Margins(top=72.0, right=54.0, bottom=72.0, left=54.0)
        assert m.top == 72.0
        assert m.right == 54.0
        assert m.bottom == 72.0
        assert m.left == 54.0

    def test_uniform(self):
        from oxidize_pdf import Margins

        m = Margins.uniform(72.0)
        assert m.top == 72.0
        assert m.right == 72.0
        assert m.bottom == 72.0
        assert m.left == 72.0

    def test_repr(self):
        from oxidize_pdf import Margins

        m = Margins.uniform(72.0)
        assert "Margins" in repr(m)
