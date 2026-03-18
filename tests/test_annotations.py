"""Tests for Annotations and Actions — Features 21, 23 (Tier 6)."""

import pytest


class TestAnnotationType:
    def test_annotation_type_variants(self):
        from oxidize_pdf import AnnotationType

        assert AnnotationType.TEXT is not None
        assert AnnotationType.LINK is not None
        assert AnnotationType.FREE_TEXT is not None
        assert AnnotationType.LINE is not None
        assert AnnotationType.SQUARE is not None
        assert AnnotationType.CIRCLE is not None
        assert AnnotationType.HIGHLIGHT is not None
        assert AnnotationType.UNDERLINE is not None
        assert AnnotationType.STRIKE_OUT is not None
        assert AnnotationType.STAMP is not None
        assert AnnotationType.INK is not None
        assert AnnotationType.POPUP is not None
        assert AnnotationType.FILE_ATTACHMENT is not None


class TestAnnotation:
    def test_annotation_create(self):
        from oxidize_pdf import Annotation, AnnotationType, Point, Rectangle

        a = Annotation(AnnotationType.TEXT, Rectangle(Point(100.0, 700.0), Point(200.0, 750.0)))
        assert isinstance(a, Annotation)

    def test_annotation_with_contents(self):
        from oxidize_pdf import Annotation, AnnotationType, Point, Rectangle

        a = Annotation(AnnotationType.TEXT, Rectangle(Point(100.0, 700.0), Point(200.0, 750.0)))
        a = a.with_contents("A note")
        assert isinstance(a, Annotation)

    def test_annotation_with_subject(self):
        from oxidize_pdf import Annotation, AnnotationType, Point, Rectangle

        a = Annotation(AnnotationType.TEXT, Rectangle(Point(100.0, 700.0), Point(200.0, 750.0)))
        a = a.with_subject("Review")
        assert isinstance(a, Annotation)

    def test_annotation_with_color(self):
        from oxidize_pdf import Annotation, AnnotationType, Color, Point, Rectangle

        a = Annotation(AnnotationType.HIGHLIGHT, Rectangle(Point(100.0, 700.0), Point(300.0, 720.0)))
        a = a.with_color(Color.rgb(1.0, 1.0, 0.0))
        assert isinstance(a, Annotation)

    def test_annotation_builder_chain(self):
        from oxidize_pdf import Annotation, AnnotationType, Color, Point, Rectangle

        a = (
            Annotation(AnnotationType.TEXT, Rectangle(Point(100.0, 700.0), Point(200.0, 750.0)))
            .with_contents("Note text")
            .with_subject("Subject")
            .with_name("MyAnnot")
            .with_color(Color.rgb(0.0, 0.5, 1.0))
        )
        assert isinstance(a, Annotation)


class TestActions:
    def test_uri_action_create(self):
        from oxidize_pdf import UriAction

        a = UriAction("https://example.com")
        assert isinstance(a, UriAction)

    def test_uri_action_email(self):
        from oxidize_pdf import UriAction

        a = UriAction.email("user@example.com")
        assert isinstance(a, UriAction)

    def test_goto_action_create(self):
        from oxidize_pdf import GoToAction

        a = GoToAction.to_page(0)
        assert isinstance(a, GoToAction)

    def test_goto_action_xyz(self):
        from oxidize_pdf import GoToAction

        a = GoToAction.to_page_xyz(0, 100.0, 700.0)
        assert isinstance(a, GoToAction)

    def test_javascript_action(self):
        from oxidize_pdf import JavaScriptAction

        a = JavaScriptAction("app.alert('Hello');")
        assert isinstance(a, JavaScriptAction)

    def test_reset_form_action(self):
        from oxidize_pdf import ResetFormAction

        a = ResetFormAction()
        assert isinstance(a, ResetFormAction)


class TestAnnotationOnPage:
    def test_text_annotation_renders(self):
        from oxidize_pdf import Annotation, AnnotationType, Document, Page, Point, Rectangle

        page = Page.a4()
        ann = Annotation(AnnotationType.TEXT, Rectangle(Point(100.0, 700.0), Point(130.0, 730.0)))
        ann = ann.with_contents("A sticky note")
        page.add_annotation(ann)

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
