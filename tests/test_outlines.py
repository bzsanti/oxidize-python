"""Tests for Bookmarks/Outlines, Destinations, Page Labels — Features 24-26 (Tier 6)."""

import pytest


# ── Feature 24: Bookmarks/Outlines ────────────────────────────────────────


class TestOutlineItem:
    def test_outline_item_create(self):
        from oxidize_pdf import OutlineItem

        item = OutlineItem("Chapter 1")
        assert isinstance(item, OutlineItem)

    def test_outline_item_with_destination(self):
        from oxidize_pdf import Destination, OutlineItem

        item = OutlineItem("Chapter 1").with_destination(Destination.fit(0))
        assert isinstance(item, OutlineItem)

    def test_outline_item_bold_italic(self):
        from oxidize_pdf import OutlineItem

        item = OutlineItem("Important").bold().italic()
        assert isinstance(item, OutlineItem)

    def test_outline_item_with_color(self):
        from oxidize_pdf import Color, OutlineItem

        item = OutlineItem("Red Chapter").with_color(Color.rgb(1.0, 0.0, 0.0))
        assert isinstance(item, OutlineItem)

    def test_outline_item_add_child(self):
        from oxidize_pdf import OutlineItem

        parent = OutlineItem("Part I")
        parent.add_child(OutlineItem("Chapter 1"))
        parent.add_child(OutlineItem("Chapter 2"))


class TestOutlineTree:
    def test_outline_tree_create(self):
        from oxidize_pdf import OutlineTree

        tree = OutlineTree()
        assert isinstance(tree, OutlineTree)

    def test_outline_tree_add_items(self):
        from oxidize_pdf import OutlineItem, OutlineTree

        tree = OutlineTree()
        tree.add_item(OutlineItem("Chapter 1"))
        tree.add_item(OutlineItem("Chapter 2"))


class TestDocumentOutline:
    def test_document_set_outline_renders(self):
        from oxidize_pdf import (
            Destination,
            Document,
            Font,
            OutlineItem,
            OutlineTree,
            Page,
        )

        tree = OutlineTree()
        tree.add_item(OutlineItem("Chapter 1").with_destination(Destination.fit(0)))
        tree.add_item(OutlineItem("Chapter 2").with_destination(Destination.fit(1)))

        doc = Document()
        for i in range(2):
            page = Page.a4()
            page.set_font(Font.HELVETICA, 24.0)
            page.text_at(72.0, 700.0, f"Chapter {i + 1}")
            doc.add_page(page)

        doc.set_outline(tree)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
        assert len(data) > 100


# ── Feature 25: Destinations ──────────────────────────────────────────────


class TestDestination:
    def test_destination_fit(self):
        from oxidize_pdf import Destination

        d = Destination.fit(0)
        assert isinstance(d, Destination)

    def test_destination_xyz(self):
        from oxidize_pdf import Destination

        d = Destination.xyz(0, 100.0, 700.0, 1.5)
        assert isinstance(d, Destination)

    def test_destination_fit_h(self):
        from oxidize_pdf import Destination

        d = Destination.fit_h(0, 700.0)
        assert isinstance(d, Destination)

    def test_destination_fit_v(self):
        from oxidize_pdf import Destination

        d = Destination.fit_v(0, 72.0)
        assert isinstance(d, Destination)

    def test_destination_fit_b(self):
        from oxidize_pdf import Destination

        d = Destination.fit_b(0)
        assert isinstance(d, Destination)


# ── Feature 26: Page Labels ──────────────────────────────────────────────


class TestPageLabelStyle:
    def test_page_label_style_variants(self):
        from oxidize_pdf import PageLabelStyle

        assert PageLabelStyle.DECIMAL is not None
        assert PageLabelStyle.ROMAN_UPPER is not None
        assert PageLabelStyle.ROMAN_LOWER is not None
        assert PageLabelStyle.ALPHA_UPPER is not None
        assert PageLabelStyle.ALPHA_LOWER is not None
        assert PageLabelStyle.NONE is not None


class TestPageLabel:
    def test_page_label_decimal(self):
        from oxidize_pdf import PageLabel

        pl = PageLabel.decimal()
        assert isinstance(pl, PageLabel)

    def test_page_label_roman(self):
        from oxidize_pdf import PageLabel

        pl = PageLabel.roman_uppercase()
        assert isinstance(pl, PageLabel)

    def test_page_label_with_prefix(self):
        from oxidize_pdf import PageLabel

        pl = PageLabel.decimal().with_prefix("Appendix ")
        assert isinstance(pl, PageLabel)

    def test_page_label_starting_at(self):
        from oxidize_pdf import PageLabel

        pl = PageLabel.decimal().starting_at(5)
        assert isinstance(pl, PageLabel)


class TestPageLabelTree:
    def test_page_label_tree_create(self):
        from oxidize_pdf import PageLabelTree

        tree = PageLabelTree()
        assert isinstance(tree, PageLabelTree)

    def test_page_label_tree_add_range(self):
        from oxidize_pdf import PageLabel, PageLabelTree

        tree = PageLabelTree()
        tree.add_range(0, PageLabel.roman_lowercase())
        tree.add_range(4, PageLabel.decimal())


class TestDocumentPageLabels:
    def test_document_set_page_labels(self):
        from oxidize_pdf import Document, Font, Page, PageLabel, PageLabelTree

        tree = PageLabelTree()
        tree.add_range(0, PageLabel.roman_lowercase())
        tree.add_range(3, PageLabel.decimal().with_prefix("Ch ").starting_at(1))

        doc = Document()
        for i in range(5):
            page = Page.a4()
            page.set_font(Font.HELVETICA, 12.0)
            page.text_at(72.0, 700.0, f"Page {i + 1}")
            doc.add_page(page)

        doc.set_page_labels(tree)
        data = doc.save_to_bytes()
        assert data[:5] == b"%PDF-"
