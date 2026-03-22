"""Tests for Tier 20 — Annotations Deep (F83): Specific annotation types."""

import pytest
from oxidize_pdf import (
    Annotation,
    AnnotationType,
    BorderEffect,
    BorderEffectStyle,
    CircleAnnotation,
    Color,
    Document,
    FileAttachmentAnnotation,
    FileAttachmentIcon,
    FreeTextAnnotation,
    HighlightAnnotation,
    HighlightMode,
    InkAnnotation,
    LineAnnotation,
    LineEndingStyle,
    LinkAnnotation,
    MarkupAnnotation,
    MarkupType,
    Page,
    Point,
    PolygonAnnotation,
    PolylineAnnotation,
    PopupAnnotation,
    PopupFlags,
    QuadPoints,
    Rectangle,
    SquareAnnotation,
    StampAnnotation,
    StampName,
    TextAnnotation,
)


# ── Cycle 1: Support types ──────────────────────────────────────────────


class TestLineEndingStyle:
    def test_all_variants_exist(self):
        assert LineEndingStyle.NONE is not None
        assert LineEndingStyle.SQUARE is not None
        assert LineEndingStyle.CIRCLE is not None
        assert LineEndingStyle.DIAMOND is not None
        assert LineEndingStyle.OPEN_ARROW is not None
        assert LineEndingStyle.CLOSED_ARROW is not None
        assert LineEndingStyle.BUTT is not None
        assert LineEndingStyle.R_OPEN_ARROW is not None
        assert LineEndingStyle.R_CLOSED_ARROW is not None
        assert LineEndingStyle.SLASH is not None

    def test_repr(self):
        r = repr(LineEndingStyle.OPEN_ARROW)
        assert "OpenArrow" in r


class TestBorderEffectStyle:
    def test_variants(self):
        assert BorderEffectStyle.SOLID is not None
        assert BorderEffectStyle.CLOUDY is not None

    def test_repr(self):
        assert "BorderEffectStyle" in repr(BorderEffectStyle.SOLID)


class TestBorderEffect:
    def test_new_with_style(self):
        be = BorderEffect(BorderEffectStyle.CLOUDY, 1.5)
        assert be is not None

    def test_default(self):
        be = BorderEffect()
        assert be is not None

    def test_repr(self):
        assert "BorderEffect" in repr(BorderEffect())


# ── Cycle 1: CircleAnnotation ────────────────────────────────────────────


class TestCircleAnnotation:
    def test_new(self):
        rect = Rectangle(Point(50.0, 50.0), Point(150.0, 150.0))
        c = CircleAnnotation(rect)
        assert c is not None

    def test_with_interior_color(self):
        rect = Rectangle(Point(50.0, 50.0), Point(150.0, 150.0))
        c = CircleAnnotation(rect).with_interior_color(Color.rgb(1.0, 0.0, 0.0))
        assert c is not None

    def test_with_cloudy_border(self):
        rect = Rectangle(Point(50.0, 50.0), Point(150.0, 150.0))
        c = CircleAnnotation(rect).with_cloudy_border(1.5)
        assert c is not None

    def test_to_annotation(self):
        rect = Rectangle(Point(50.0, 50.0), Point(150.0, 150.0))
        ann = (
            CircleAnnotation(rect)
            .with_interior_color(Color.rgb(0.0, 0.5, 1.0))
            .to_annotation()
        )
        assert isinstance(ann, Annotation)

    def test_builder_chain(self):
        rect = Rectangle(Point(50.0, 50.0), Point(150.0, 150.0))
        ann = (
            CircleAnnotation(rect)
            .with_interior_color(Color.gray(0.5))
            .with_cloudy_border(1.0)
            .with_contents("A circle")
            .to_annotation()
        )
        assert isinstance(ann, Annotation)

    def test_repr(self):
        rect = Rectangle(Point(50.0, 50.0), Point(150.0, 150.0))
        r = repr(CircleAnnotation(rect))
        assert "CircleAnnotation" in r
        assert "50" in r


# ── Cycle 1: SquareAnnotation ────────────────────────────────────────────


class TestSquareAnnotation:
    def test_new(self):
        rect = Rectangle(Point(10.0, 10.0), Point(110.0, 110.0))
        s = SquareAnnotation(rect)
        assert s is not None

    def test_with_interior_color(self):
        rect = Rectangle(Point(10.0, 10.0), Point(110.0, 110.0))
        s = SquareAnnotation(rect).with_interior_color(Color.rgb(0.0, 1.0, 0.0))
        assert s is not None

    def test_with_cloudy_border(self):
        rect = Rectangle(Point(10.0, 10.0), Point(110.0, 110.0))
        s = SquareAnnotation(rect).with_cloudy_border(2.0)
        assert s is not None

    def test_to_annotation(self):
        rect = Rectangle(Point(10.0, 10.0), Point(110.0, 110.0))
        ann = SquareAnnotation(rect).with_interior_color(Color.gray(0.8)).to_annotation()
        assert isinstance(ann, Annotation)

    def test_builder_chain(self):
        rect = Rectangle(Point(10.0, 10.0), Point(110.0, 110.0))
        ann = (
            SquareAnnotation(rect)
            .with_interior_color(Color.rgb(0.0, 0.0, 1.0))
            .with_cloudy_border(1.5)
            .with_contents("A square")
            .to_annotation()
        )
        assert isinstance(ann, Annotation)

    def test_repr(self):
        rect = Rectangle(Point(10.0, 10.0), Point(110.0, 110.0))
        r = repr(SquareAnnotation(rect))
        assert "SquareAnnotation" in r
        assert "10" in r


# ── Cycle 1: LineAnnotation ──────────────────────────────────────────────


class TestLineAnnotation:
    def test_new(self):
        line = LineAnnotation(Point(100.0, 100.0), Point(300.0, 200.0))
        assert line is not None

    def test_with_endings(self):
        line = LineAnnotation(Point(0.0, 0.0), Point(100.0, 100.0))
        line = line.with_endings(LineEndingStyle.OPEN_ARROW, LineEndingStyle.CLOSED_ARROW)
        assert line is not None

    def test_with_interior_color(self):
        line = LineAnnotation(Point(0.0, 0.0), Point(100.0, 100.0))
        line = line.with_interior_color(Color.rgb(1.0, 0.0, 0.0))
        assert line is not None

    def test_to_annotation(self):
        ann = (
            LineAnnotation(Point(50.0, 500.0), Point(400.0, 500.0))
            .with_endings(LineEndingStyle.OPEN_ARROW, LineEndingStyle.NONE)
            .with_interior_color(Color.blue())
            .to_annotation()
        )
        assert isinstance(ann, Annotation)

    def test_with_contents(self):
        ann = (
            LineAnnotation(Point(0.0, 0.0), Point(200.0, 200.0))
            .with_contents("A line")
            .to_annotation()
        )
        assert isinstance(ann, Annotation)

    def test_repr(self):
        r = repr(LineAnnotation(Point(0.0, 0.0), Point(100.0, 100.0)))
        assert "LineAnnotation" in r
        assert "100" in r


# ── Cycle 2: StampAnnotation ─────────────────────────────────────────────


class TestStampName:
    def test_standard_constants(self):
        assert StampName.APPROVED is not None
        assert StampName.EXPERIMENTAL is not None
        assert StampName.NOT_APPROVED is not None
        assert StampName.AS_IS is not None
        assert StampName.EXPIRED is not None
        assert StampName.NOT_FOR_PUBLIC_RELEASE is not None
        assert StampName.CONFIDENTIAL is not None
        assert StampName.FINAL is not None
        assert StampName.SOLD is not None
        assert StampName.DEPARTMENTAL is not None
        assert StampName.FOR_COMMENT is not None
        assert StampName.TOP_SECRET is not None
        assert StampName.DRAFT is not None
        assert StampName.FOR_PUBLIC_RELEASE is not None

    def test_custom(self):
        custom = StampName.custom("MyCompanyStamp")
        assert custom is not None

    def test_repr(self):
        assert "Approved" in repr(StampName.APPROVED)


class TestStampAnnotation:
    def test_new(self):
        rect = Rectangle(Point(100.0, 700.0), Point(300.0, 750.0))
        sa = StampAnnotation(rect, StampName.DRAFT)
        assert sa is not None

    def test_to_annotation(self):
        rect = Rectangle(Point(100.0, 700.0), Point(300.0, 750.0))
        ann = StampAnnotation(rect, StampName.APPROVED).to_annotation()
        assert isinstance(ann, Annotation)

    def test_custom_stamp(self):
        rect = Rectangle(Point(100.0, 700.0), Point(300.0, 750.0))
        ann = StampAnnotation(rect, StampName.custom("MyStamp")).to_annotation()
        assert isinstance(ann, Annotation)

    def test_repr(self):
        rect = Rectangle(Point(100.0, 700.0), Point(300.0, 750.0))
        r = repr(StampAnnotation(rect, StampName.DRAFT))
        assert "StampAnnotation" in r
        assert "Draft" in r


# ── Cycle 2: FileAttachmentAnnotation ────────────────────────────────────


class TestFileAttachmentIcon:
    def test_all_variants(self):
        assert FileAttachmentIcon.GRAPH is not None
        assert FileAttachmentIcon.PAPERCLIP is not None
        assert FileAttachmentIcon.PUSH_PIN is not None
        assert FileAttachmentIcon.TAG is not None

    def test_repr(self):
        assert "FileAttachmentIcon" in repr(FileAttachmentIcon.PAPERCLIP)


class TestFileAttachmentAnnotation:
    def test_new(self):
        rect = Rectangle(Point(100.0, 700.0), Point(120.0, 720.0))
        fa = FileAttachmentAnnotation(rect, "report.txt", b"file content")
        assert fa is not None

    def test_with_mime_type(self):
        rect = Rectangle(Point(100.0, 700.0), Point(120.0, 720.0))
        fa = FileAttachmentAnnotation(rect, "data.csv", b"a,b\n1,2").with_mime_type("text/csv")
        assert fa is not None

    def test_with_icon(self):
        rect = Rectangle(Point(100.0, 700.0), Point(120.0, 720.0))
        fa = FileAttachmentAnnotation(rect, "note.txt", b"hello").with_icon(FileAttachmentIcon.TAG)
        assert fa is not None

    def test_to_annotation(self):
        rect = Rectangle(Point(100.0, 700.0), Point(120.0, 720.0))
        ann = FileAttachmentAnnotation(rect, "doc.pdf", b"%PDF-").to_annotation()
        assert isinstance(ann, Annotation)

    def test_repr(self):
        rect = Rectangle(Point(100.0, 700.0), Point(120.0, 720.0))
        r = repr(FileAttachmentAnnotation(rect, "test.txt", b"data"))
        assert "FileAttachmentAnnotation" in r
        assert "test.txt" in r


# ── Cycle 2: FreeTextAnnotation ──────────────────────────────────────────


class TestFreeTextAnnotation:
    def test_new(self):
        rect = Rectangle(Point(100.0, 600.0), Point(300.0, 650.0))
        ft = FreeTextAnnotation(rect, "Hello, world!")
        assert ft is not None

    def test_with_justification(self):
        rect = Rectangle(Point(100.0, 600.0), Point(300.0, 650.0))
        ft = FreeTextAnnotation(rect, "Centered").with_justification(1)
        assert ft is not None

    def test_to_annotation(self):
        rect = Rectangle(Point(100.0, 600.0), Point(300.0, 650.0))
        ann = FreeTextAnnotation(rect, "Note text").to_annotation()
        assert isinstance(ann, Annotation)

    def test_builder_chain(self):
        rect = Rectangle(Point(100.0, 600.0), Point(300.0, 650.0))
        ann = (
            FreeTextAnnotation(rect, "Aligned text")
            .with_justification(2)
            .to_annotation()
        )
        assert isinstance(ann, Annotation)

    def test_repr(self):
        rect = Rectangle(Point(100.0, 600.0), Point(300.0, 650.0))
        r = repr(FreeTextAnnotation(rect, "text"))
        assert "FreeTextAnnotation" in r
        assert "100" in r


# ── Cycle 2: InkAnnotation ───────────────────────────────────────────────


class TestInkAnnotation:
    def test_new(self):
        ink = InkAnnotation()
        assert ink is not None

    def test_add_stroke(self):
        ink = InkAnnotation().add_stroke([Point(10.0, 10.0), Point(50.0, 80.0), Point(90.0, 10.0)])
        assert ink is not None

    def test_multiple_strokes(self):
        ink = (
            InkAnnotation()
            .add_stroke([Point(0.0, 0.0), Point(100.0, 100.0)])
            .add_stroke([Point(100.0, 0.0), Point(0.0, 100.0)])
        )
        assert ink is not None

    def test_to_annotation(self):
        ann = (
            InkAnnotation()
            .add_stroke([Point(10.0, 10.0), Point(200.0, 200.0)])
            .to_annotation()
        )
        assert isinstance(ann, Annotation)

    def test_repr(self):
        assert "InkAnnotation" in repr(InkAnnotation())


# ── Cycle 3: PolygonAnnotation ───────────────────────────────────────────


class TestPolygonAnnotation:
    def test_new(self):
        verts = [Point(100.0, 100.0), Point(200.0, 200.0), Point(100.0, 200.0)]
        p = PolygonAnnotation(verts)
        assert p is not None

    def test_with_line_color(self):
        verts = [Point(0.0, 0.0), Point(100.0, 0.0), Point(50.0, 100.0)]
        p = PolygonAnnotation(verts).with_line_color(Color.red())
        assert p is not None

    def test_with_fill_color(self):
        verts = [Point(0.0, 0.0), Point(100.0, 0.0), Point(50.0, 100.0)]
        p = PolygonAnnotation(verts).with_fill_color(Color.blue())
        assert p is not None

    def test_with_opacity(self):
        verts = [Point(0.0, 0.0), Point(100.0, 0.0), Point(50.0, 100.0)]
        p = PolygonAnnotation(verts).with_opacity(0.5)
        assert p is not None

    def test_to_annotation(self):
        verts = [Point(0.0, 0.0), Point(200.0, 0.0), Point(200.0, 150.0), Point(0.0, 150.0)]
        ann = (
            PolygonAnnotation(verts)
            .with_line_color(Color.black())
            .with_fill_color(Color.rgb(0.9, 0.9, 0.0))
            .with_opacity(0.8)
            .to_annotation()
        )
        assert isinstance(ann, Annotation)

    def test_repr(self):
        verts = [Point(0.0, 0.0), Point(100.0, 0.0), Point(50.0, 100.0)]
        assert "PolygonAnnotation" in repr(PolygonAnnotation(verts))


# ── Cycle 3: PolylineAnnotation ──────────────────────────────────────────


class TestPolylineAnnotation:
    def test_new(self):
        verts = [Point(0.0, 0.0), Point(100.0, 100.0), Point(200.0, 0.0)]
        pl = PolylineAnnotation(verts)
        assert pl is not None

    def test_with_line_color(self):
        verts = [Point(0.0, 0.0), Point(100.0, 100.0)]
        pl = PolylineAnnotation(verts).with_line_color(Color.green())
        assert pl is not None

    def test_with_opacity(self):
        verts = [Point(0.0, 100.0), Point(200.0, 100.0)]
        pl = PolylineAnnotation(verts).with_opacity(0.7)
        assert pl is not None

    def test_to_annotation(self):
        verts = [Point(50.0, 400.0), Point(150.0, 500.0), Point(250.0, 400.0)]
        ann = (
            PolylineAnnotation(verts)
            .with_line_color(Color.rgb(0.2, 0.4, 0.8))
            .with_line_width(2.0)
            .to_annotation()
        )
        assert isinstance(ann, Annotation)

    def test_repr(self):
        verts = [Point(0.0, 0.0), Point(100.0, 100.0)]
        assert "PolylineAnnotation" in repr(PolylineAnnotation(verts))


# ── Cycle 3: QuadPoints + HighlightAnnotation ───────────────────────────


class TestQuadPoints:
    def test_from_rect(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 515.0))
        qp = QuadPoints.from_rect(rect)
        assert qp is not None

    def test_new_with_points(self):
        qp = QuadPoints([100.0, 500.0, 300.0, 500.0, 300.0, 515.0, 100.0, 515.0])
        assert qp is not None

    def test_repr(self):
        assert "QuadPoints" in repr(QuadPoints([0.0] * 8))


class TestHighlightAnnotationDeep:
    def test_new(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 515.0))
        ha = HighlightAnnotation(rect)
        assert ha is not None

    def test_to_annotation(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 515.0))
        ann = HighlightAnnotation(rect).to_annotation()
        assert isinstance(ann, Annotation)

    def test_with_custom_quad_points(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 515.0))
        qp = QuadPoints([100.0, 500.0, 300.0, 500.0, 300.0, 515.0, 100.0, 515.0])
        ann = HighlightAnnotation.with_quad_points(rect, qp).to_annotation()
        assert isinstance(ann, Annotation)

    def test_repr(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 515.0))
        r = repr(HighlightAnnotation(rect))
        assert "HighlightAnnotation" in r
        assert "100" in r


# ── Cycle 3: PopupAnnotation + PopupFlags ────────────────────────────────


class TestPopupFlags:
    def test_new(self):
        pf = PopupFlags(no_rotate=True, no_zoom=False)
        assert pf is not None

    def test_default(self):
        pf = PopupFlags()
        assert pf is not None

    def test_repr(self):
        assert "PopupFlags" in repr(PopupFlags())


class TestPopupAnnotation:
    def test_new(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 600.0))
        popup = PopupAnnotation(rect)
        assert popup is not None

    def test_with_open(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 600.0))
        popup = PopupAnnotation(rect).with_open(True)
        assert popup is not None

    def test_with_contents(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 600.0))
        popup = PopupAnnotation(rect).with_contents("Popup text")
        assert popup is not None

    def test_with_color(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 600.0))
        popup = PopupAnnotation(rect).with_color(Color.rgb(1.0, 1.0, 0.8))
        assert popup is not None

    def test_with_flags(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 600.0))
        flags = PopupFlags(no_rotate=True, no_zoom=True)
        ann = PopupAnnotation(rect).with_flags(flags).to_annotation()
        assert isinstance(ann, Annotation)

    def test_with_flags_default(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 600.0))
        ann = PopupAnnotation(rect).with_flags(PopupFlags()).to_annotation()
        assert isinstance(ann, Annotation)

    def test_to_annotation(self):
        rect = Rectangle(Point(200.0, 500.0), Point(400.0, 600.0))
        ann = (
            PopupAnnotation(rect)
            .with_open(True)
            .with_contents("Review comment")
            .with_color(Color.rgb(1.0, 1.0, 0.9))
            .to_annotation()
        )
        assert isinstance(ann, Annotation)

    def test_repr(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 600.0))
        r = repr(PopupAnnotation(rect))
        assert "PopupAnnotation" in r
        assert "100" in r


# ── Cycle 4: HighlightMode + LinkAnnotation ──────────────────────────────


class TestHighlightMode:
    def test_variants(self):
        assert HighlightMode.NONE is not None
        assert HighlightMode.INVERT is not None
        assert HighlightMode.OUTLINE is not None
        assert HighlightMode.PUSH is not None

    def test_repr(self):
        assert "HighlightMode" in repr(HighlightMode.INVERT)


class TestLinkAnnotation:
    def test_to_uri(self):
        rect = Rectangle(Point(100.0, 700.0), Point(300.0, 720.0))
        link = LinkAnnotation.to_uri(rect, "https://example.com")
        assert link is not None

    def test_to_uri_to_annotation(self):
        rect = Rectangle(Point(100.0, 700.0), Point(300.0, 720.0))
        ann = LinkAnnotation.to_uri(rect, "https://example.com").to_annotation()
        assert isinstance(ann, Annotation)

    def test_with_highlight_mode(self):
        rect = Rectangle(Point(100.0, 700.0), Point(300.0, 720.0))
        ann = (
            LinkAnnotation.to_uri(rect, "https://example.com")
            .with_highlight_mode(HighlightMode.OUTLINE)
            .to_annotation()
        )
        assert isinstance(ann, Annotation)

    def test_named_action(self):
        rect = Rectangle(Point(100.0, 700.0), Point(300.0, 720.0))
        ann = LinkAnnotation.named_action(rect, "NextPage").to_annotation()
        assert isinstance(ann, Annotation)

    def test_repr(self):
        rect = Rectangle(Point(100.0, 700.0), Point(300.0, 720.0))
        r = repr(LinkAnnotation.to_uri(rect, "https://example.com"))
        assert "LinkAnnotation" in r
        assert "100" in r


# ── Integration tests: annotations on documents ─────────────────────────


class TestAnnotationsDeepOnDocument:
    def test_circle_on_page(self):
        page = Page(612.0, 792.0)
        ann = (
            CircleAnnotation(Rectangle(Point(100.0, 500.0), Point(200.0, 600.0)))
            .with_interior_color(Color.rgb(1.0, 0.8, 0.0))
            .to_annotation()
        )
        page.add_annotation(ann)
        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_line_annotation_on_page(self):
        page = Page(612.0, 792.0)
        ann = (
            LineAnnotation(Point(100.0, 700.0), Point(400.0, 700.0))
            .with_endings(LineEndingStyle.OPEN_ARROW, LineEndingStyle.OPEN_ARROW)
            .to_annotation()
        )
        page.add_annotation(ann)
        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_stamp_on_page(self):
        page = Page(612.0, 792.0)
        ann = StampAnnotation(
            Rectangle(Point(400.0, 650.0), Point(550.0, 700.0)), StampName.CONFIDENTIAL
        ).to_annotation()
        page.add_annotation(ann)
        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_polygon_on_page(self):
        page = Page(612.0, 792.0)
        ann = (
            PolygonAnnotation([Point(100.0, 100.0), Point(200.0, 200.0), Point(100.0, 200.0)])
            .with_line_color(Color.red())
            .to_annotation()
        )
        page.add_annotation(ann)
        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_link_on_page(self):
        page = Page(612.0, 792.0)
        ann = LinkAnnotation.to_uri(
            Rectangle(Point(100.0, 700.0), Point(300.0, 720.0)),
            "https://example.com",
        ).to_annotation()
        page.add_annotation(ann)
        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"

    def test_ink_on_page(self):
        page = Page(612.0, 792.0)
        ann = (
            InkAnnotation()
            .add_stroke([Point(100.0, 100.0), Point(200.0, 300.0), Point(300.0, 100.0)])
            .to_annotation()
        )
        page.add_annotation(ann)
        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"


# ── Quality fixes: Validation tests (R2 + R3) ───────────────────────────


class TestFreeTextJustificationValidation:
    def test_valid_justification_0(self):
        rect = Rectangle(Point(0.0, 0.0), Point(100.0, 50.0))
        ft = FreeTextAnnotation(rect, "text").with_justification(0)
        assert ft is not None

    def test_valid_justification_2(self):
        rect = Rectangle(Point(0.0, 0.0), Point(100.0, 50.0))
        ft = FreeTextAnnotation(rect, "text").with_justification(2)
        assert ft is not None

    def test_invalid_justification_negative(self):
        rect = Rectangle(Point(0.0, 0.0), Point(100.0, 50.0))
        with pytest.raises(ValueError, match="justification"):
            FreeTextAnnotation(rect, "text").with_justification(-1)

    def test_invalid_justification_too_large(self):
        rect = Rectangle(Point(0.0, 0.0), Point(100.0, 50.0))
        with pytest.raises(ValueError, match="justification"):
            FreeTextAnnotation(rect, "text").with_justification(3)


class TestQuadPointsValidation:
    def test_valid_8_floats(self):
        qp = QuadPoints([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        assert qp is not None

    def test_valid_16_floats(self):
        qp = QuadPoints([0.0] * 16)
        assert qp is not None

    def test_invalid_7_floats(self):
        with pytest.raises(ValueError, match="multiple of 8"):
            QuadPoints([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])

    def test_invalid_empty(self):
        with pytest.raises(ValueError, match="multiple of 8"):
            QuadPoints([])

    def test_invalid_9_floats(self):
        with pytest.raises(ValueError, match="multiple of 8"):
            QuadPoints([0.0] * 9)


# ── Quality fixes: Negative/edge case tests (R5) ────────────────────────


class TestNegativeEdgeCases:
    def test_stamp_name_custom_empty_string(self):
        """Custom stamp name with empty string — core accepts it."""
        sn = StampName.custom("")
        assert sn is not None

    def test_file_attachment_empty_data(self):
        """FileAttachmentAnnotation with empty file_data — core accepts it."""
        rect = Rectangle(Point(0.0, 0.0), Point(20.0, 20.0))
        ann = FileAttachmentAnnotation(rect, "empty.txt", b"").to_annotation()
        assert isinstance(ann, Annotation)

    def test_ink_annotation_empty_stroke(self):
        """add_stroke([]) does not raise — see docstring for rationale."""
        ann = InkAnnotation().add_stroke([]).to_annotation()
        assert isinstance(ann, Annotation)

    def test_polygon_opacity_clamped_above_1(self):
        """Opacity > 1.0 is clamped to 1.0 by the core — no error raised."""
        verts = [Point(0.0, 0.0), Point(100.0, 0.0), Point(50.0, 100.0)]
        p = PolygonAnnotation(verts).with_opacity(2.5)
        assert p is not None

    def test_polygon_opacity_clamped_below_0(self):
        """Opacity < 0.0 is clamped to 0.0 by the core — no error raised."""
        verts = [Point(0.0, 0.0), Point(100.0, 0.0), Point(50.0, 100.0)]
        p = PolygonAnnotation(verts).with_opacity(-0.5)
        assert p is not None

    def test_polyline_opacity_clamped(self):
        """Polyline opacity is also clamped by the core."""
        verts = [Point(0.0, 0.0), Point(100.0, 100.0)]
        p = PolylineAnnotation(verts).with_opacity(5.0)
        assert p is not None


# ── Re-review findings: R-NEW-1, R-NEW-2, O-NEW-1/2/3 ──────────────────


class TestPolygonVertexValidation:
    def test_empty_vertices_raises(self):
        with pytest.raises(ValueError, match="vertices"):
            PolygonAnnotation([])

    def test_one_vertex_raises(self):
        with pytest.raises(ValueError, match="vertices"):
            PolygonAnnotation([Point(0.0, 0.0)])

    def test_two_vertices_raises(self):
        with pytest.raises(ValueError, match="vertices"):
            PolygonAnnotation([Point(0.0, 0.0), Point(10.0, 0.0)])

    def test_three_vertices_accepted(self):
        p = PolygonAnnotation([Point(0.0, 0.0), Point(10.0, 0.0), Point(5.0, 10.0)])
        assert p is not None


class TestPolylineVertexValidation:
    def test_empty_vertices_raises(self):
        with pytest.raises(ValueError, match="vertices"):
            PolylineAnnotation([])

    def test_one_vertex_raises(self):
        with pytest.raises(ValueError, match="vertices"):
            PolylineAnnotation([Point(0.0, 0.0)])

    def test_two_vertices_accepted(self):
        pl = PolylineAnnotation([Point(0.0, 0.0), Point(100.0, 100.0)])
        assert pl is not None


class TestStampAnnotationWithContents:
    def test_with_contents(self):
        rect = Rectangle(Point(50.0, 50.0), Point(200.0, 100.0))
        sa = StampAnnotation(rect, StampName.DRAFT).with_contents("For review only")
        assert sa is not None

    def test_with_contents_to_annotation(self):
        rect = Rectangle(Point(50.0, 50.0), Point(200.0, 100.0))
        ann = StampAnnotation(rect, StampName.APPROVED).with_contents("Approved by QA").to_annotation()
        assert isinstance(ann, Annotation)

    def test_with_contents_repr(self):
        rect = Rectangle(Point(50.0, 50.0), Point(200.0, 100.0))
        sa = StampAnnotation(rect, StampName.DRAFT).with_contents("text")
        assert "StampAnnotation" in repr(sa)


class TestMarkupAnnotationReprImproved:
    def test_repr_highlight(self):
        rect = Rectangle(Point(100.0, 500.0), Point(300.0, 515.0))
        assert "Highlight" in repr(MarkupAnnotation.highlight(rect))

    def test_repr_underline(self):
        rect = Rectangle(Point(0.0, 0.0), Point(100.0, 10.0))
        assert "Underline" in repr(MarkupAnnotation.underline(rect))

    def test_repr_strikeout(self):
        rect = Rectangle(Point(0.0, 0.0), Point(100.0, 10.0))
        assert "StrikeOut" in repr(MarkupAnnotation.strikeout(rect))

    def test_repr_squiggly(self):
        rect = Rectangle(Point(0.0, 0.0), Point(100.0, 10.0))
        assert "Squiggly" in repr(MarkupAnnotation.squiggly(rect))


class TestTextAnnotationReprImproved:
    def test_repr_includes_position(self):
        ta = TextAnnotation(Point(10.0, 20.0))
        r = repr(ta)
        assert "TextAnnotation" in r
        assert "10" in r
        assert "20" in r


class TestInkAnnotationReprWithPoints:
    def test_repr_with_strokes_and_points(self):
        ink = (
            InkAnnotation()
            .add_stroke([Point(0.0, 0.0), Point(10.0, 10.0)])
            .add_stroke([Point(20.0, 20.0), Point(30.0, 30.0), Point(40.0, 40.0)])
        )
        r = repr(ink)
        assert "strokes=2" in r
        assert "points=5" in r

    def test_repr_zero_strokes(self):
        r = repr(InkAnnotation())
        assert "strokes=0" in r
        assert "points=0" in r


class TestBorderEffectGetters:
    def test_is_cloudy_false(self):
        be = BorderEffect(BorderEffectStyle.SOLID, 1.0)
        assert be.is_cloudy is False

    def test_is_cloudy_true(self):
        be = BorderEffect(BorderEffectStyle.CLOUDY, 2.0)
        assert be.is_cloudy is True

    def test_intensity_getter(self):
        be = BorderEffect(BorderEffectStyle.SOLID, 1.5)
        assert be.intensity == 1.5

    def test_intensity_default(self):
        be = BorderEffect()
        assert be.intensity == 1.0


# ── Quality: R1 — Enum eq/hash tests ────────────────────────────────────


class TestEnumEqHash:
    """Verify that frozen enum-like types support == and can be used in sets/dicts."""

    def test_annotation_type_eq(self):
        assert AnnotationType.TEXT == AnnotationType.TEXT
        assert AnnotationType.TEXT != AnnotationType.LINK

    def test_annotation_type_hashable(self):
        s = {AnnotationType.TEXT, AnnotationType.LINK, AnnotationType.TEXT}
        assert len(s) == 2

    def test_markup_type_eq(self):
        assert MarkupType.HIGHLIGHT == MarkupType.HIGHLIGHT
        assert MarkupType.HIGHLIGHT != MarkupType.UNDERLINE

    def test_markup_type_hashable(self):
        d = {MarkupType.HIGHLIGHT: "hl", MarkupType.UNDERLINE: "ul"}
        assert d[MarkupType.HIGHLIGHT] == "hl"

    def test_line_ending_style_eq(self):
        assert LineEndingStyle.OPEN_ARROW == LineEndingStyle.OPEN_ARROW
        assert LineEndingStyle.OPEN_ARROW != LineEndingStyle.CLOSED_ARROW

    def test_line_ending_style_hashable(self):
        s = {LineEndingStyle.NONE, LineEndingStyle.SQUARE, LineEndingStyle.NONE}
        assert len(s) == 2

    def test_border_effect_style_eq(self):
        assert BorderEffectStyle.SOLID == BorderEffectStyle.SOLID
        assert BorderEffectStyle.SOLID != BorderEffectStyle.CLOUDY

    def test_border_effect_style_hashable(self):
        s = {BorderEffectStyle.SOLID, BorderEffectStyle.CLOUDY}
        assert len(s) == 2

    def test_stamp_name_eq(self):
        assert StampName.DRAFT == StampName.DRAFT
        assert StampName.DRAFT != StampName.APPROVED

    def test_stamp_name_hashable(self):
        s = {StampName.DRAFT, StampName.APPROVED, StampName.DRAFT}
        assert len(s) == 2

    def test_highlight_mode_eq(self):
        assert HighlightMode.INVERT == HighlightMode.INVERT
        assert HighlightMode.INVERT != HighlightMode.OUTLINE

    def test_highlight_mode_hashable(self):
        d = {HighlightMode.NONE: 0, HighlightMode.PUSH: 1}
        assert len(d) == 2


# ── Quality: R7 — Docstring presence tests ──────────────────────────────


class TestAnnotationDocstrings:
    """Verify that all public annotation types have non-empty __doc__."""

    def test_all_annotation_classes_have_docstrings(self):
        import oxidize_pdf

        classes = [
            "AnnotationType", "Annotation", "MarkupType", "MarkupAnnotation",
            "AnnotationIcon", "TextAnnotation", "BorderStyleType", "BorderStyle",
            "LineEndingStyle", "BorderEffectStyle", "BorderEffect",
            "CircleAnnotation", "SquareAnnotation", "LineAnnotation",
            "StampName", "StampAnnotation", "FileAttachmentIcon",
            "FileAttachmentAnnotation", "FreeTextAnnotation", "InkAnnotation",
            "PolygonAnnotation", "PolylineAnnotation", "QuadPoints",
            "HighlightAnnotation", "PopupFlags", "PopupAnnotation",
            "HighlightMode", "LinkAnnotation",
        ]
        missing = []
        for name in classes:
            cls = getattr(oxidize_pdf, name)
            if not cls.__doc__:
                missing.append(name)
        assert missing == [], f"Missing docstrings: {missing}"
