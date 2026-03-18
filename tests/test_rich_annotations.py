"""Tests for Feature 55: Rich Annotations."""
import pytest


def test_markup_type_constants():
    from oxidize_pdf import MarkupType

    assert MarkupType.HIGHLIGHT is not None
    assert MarkupType.UNDERLINE is not None
    assert MarkupType.STRIKE_OUT is not None
    assert MarkupType.SQUIGGLY is not None


def test_markup_annotation_highlight():
    from oxidize_pdf import MarkupAnnotation, Point, Rectangle

    rect = Rectangle(Point(100.0, 500.0), Point(300.0, 515.0))
    ma = MarkupAnnotation.highlight(rect)
    assert ma is not None


def test_markup_annotation_underline():
    from oxidize_pdf import MarkupAnnotation, Point, Rectangle

    rect = Rectangle(Point(100.0, 500.0), Point(300.0, 515.0))
    ma = MarkupAnnotation.underline(rect)
    assert ma is not None


def test_markup_annotation_strikeout():
    from oxidize_pdf import MarkupAnnotation, Point, Rectangle

    rect = Rectangle(Point(100.0, 500.0), Point(300.0, 515.0))
    ma = MarkupAnnotation.strikeout(rect)
    assert ma is not None


def test_markup_annotation_squiggly():
    from oxidize_pdf import MarkupAnnotation, Point, Rectangle

    rect = Rectangle(Point(100.0, 500.0), Point(300.0, 515.0))
    ma = MarkupAnnotation.squiggly(rect)
    assert ma is not None


def test_markup_annotation_builders():
    from oxidize_pdf import Color, MarkupAnnotation, Point, Rectangle

    rect = Rectangle(Point(100.0, 500.0), Point(300.0, 515.0))
    ma = (
        MarkupAnnotation.highlight(rect)
        .with_author("Test Author")
        .with_contents("Test content")
        .with_color(Color.rgb(1.0, 0.8, 0.0))
    )
    assert ma is not None


def test_markup_annotation_to_annotation():
    from oxidize_pdf import Annotation, MarkupAnnotation, Point, Rectangle

    rect = Rectangle(Point(100.0, 500.0), Point(300.0, 515.0))
    ma = MarkupAnnotation.highlight(rect).with_author("Reviewer").with_contents("Important!")
    ann = ma.to_annotation()
    assert isinstance(ann, Annotation)


def test_annotation_icon_constants():
    from oxidize_pdf import AnnotationIcon

    assert AnnotationIcon.COMMENT is not None
    assert AnnotationIcon.NOTE is not None
    assert AnnotationIcon.KEY is not None
    assert AnnotationIcon.HELP is not None
    assert AnnotationIcon.NEW_PARAGRAPH is not None
    assert AnnotationIcon.PARAGRAPH is not None
    assert AnnotationIcon.INSERT is not None


def test_text_annotation_new():
    from oxidize_pdf import Point, TextAnnotation

    pos = Point(100.0, 700.0)
    ta = TextAnnotation(pos)
    assert ta is not None


def test_text_annotation_builders():
    from oxidize_pdf import AnnotationIcon, Point, TextAnnotation

    pos = Point(100.0, 700.0)
    ta = (
        TextAnnotation(pos)
        .with_icon(AnnotationIcon.COMMENT)
        .with_contents("This is a note")
        .open()
    )
    assert ta is not None


def test_text_annotation_to_annotation():
    from oxidize_pdf import Annotation, Point, TextAnnotation

    pos = Point(100.0, 700.0)
    ta = TextAnnotation(pos).with_contents("Test note")
    ann = ta.to_annotation()
    assert isinstance(ann, Annotation)


def test_border_style_type_constants():
    from oxidize_pdf import BorderStyleType

    assert BorderStyleType.SOLID is not None
    assert BorderStyleType.DASHED is not None
    assert BorderStyleType.BEVELED is not None
    assert BorderStyleType.INSET is not None
    assert BorderStyleType.UNDERLINE is not None


def test_border_style_new():
    from oxidize_pdf import BorderStyle, BorderStyleType

    bs = BorderStyle(2.0, BorderStyleType.DASHED)
    assert bs is not None


def test_border_style_default():
    from oxidize_pdf import BorderStyle

    bs = BorderStyle()
    assert bs is not None


def test_annotation_with_border():
    from oxidize_pdf import Annotation, AnnotationType, BorderStyle, BorderStyleType, Point, Rectangle

    rect = Rectangle(Point(100.0, 500.0), Point(300.0, 600.0))
    ann = (
        Annotation(AnnotationType.SQUARE, rect)
        .with_border(BorderStyle(2.0, BorderStyleType.SOLID))
    )
    assert ann is not None
