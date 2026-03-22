"""Tests for Lists — Feature 4 (Tier 1)."""

import pytest


class TestOrderedList:
    """Test OrderedList construction and usage."""

    def test_ordered_list_create(self):
        from oxidize_pdf import OrderedList, OrderedListStyle

        ol = OrderedList(OrderedListStyle.DECIMAL)
        assert isinstance(ol, OrderedList)

    def test_ordered_list_add_items(self):
        from oxidize_pdf import OrderedList, OrderedListStyle

        ol = OrderedList(OrderedListStyle.DECIMAL)
        ol.add_item("First item")
        ol.add_item("Second item")
        ol.add_item("Third item")

    def test_ordered_list_styles(self):
        from oxidize_pdf import OrderedListStyle

        assert OrderedListStyle.DECIMAL is not None
        assert OrderedListStyle.LOWER_ALPHA is not None
        assert OrderedListStyle.UPPER_ALPHA is not None
        assert OrderedListStyle.LOWER_ROMAN is not None
        assert OrderedListStyle.UPPER_ROMAN is not None


class TestUnorderedList:
    """Test UnorderedList construction and usage."""

    def test_unordered_list_create(self):
        from oxidize_pdf import BulletStyle, UnorderedList

        ul = UnorderedList(BulletStyle.DISC)
        assert isinstance(ul, UnorderedList)

    def test_unordered_list_add_items(self):
        from oxidize_pdf import BulletStyle, UnorderedList

        ul = UnorderedList(BulletStyle.DISC)
        ul.add_item("Item A")
        ul.add_item("Item B")

    def test_bullet_styles(self):
        from oxidize_pdf import BulletStyle

        assert BulletStyle.DISC is not None
        assert BulletStyle.CIRCLE is not None
        assert BulletStyle.SQUARE is not None
        assert BulletStyle.DASH is not None


class TestListOnPage:
    """Test rendering lists on pages."""

    def test_page_add_ordered_list(self):
        from oxidize_pdf import Document, OrderedList, OrderedListStyle, Page

        ol = OrderedList(OrderedListStyle.DECIMAL)
        ol.add_item("First")
        ol.add_item("Second")
        ol.add_item("Third")

        page = Page.a4()
        page.add_ordered_list(ol, 72.0, 700.0)

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()

        assert data[:5] == b"%PDF-"

    def test_page_add_unordered_list(self):
        from oxidize_pdf import BulletStyle, Document, Page, UnorderedList

        ul = UnorderedList(BulletStyle.DISC)
        ul.add_item("Alpha")
        ul.add_item("Beta")

        page = Page.a4()
        page.add_unordered_list(ul, 72.0, 700.0)

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()

        assert data[:5] == b"%PDF-"

    def test_page_add_quick_ordered_list(self):
        from oxidize_pdf import Document, OrderedListStyle, Page

        items = ["One", "Two", "Three"]
        page = Page.a4()
        page.add_quick_ordered_list(items, 72.0, 700.0, OrderedListStyle.DECIMAL)

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()

        assert data[:5] == b"%PDF-"

    def test_page_add_quick_unordered_list(self):
        from oxidize_pdf import BulletStyle, Document, Page

        items = ["Item A", "Item B"]
        page = Page.a4()
        page.add_quick_unordered_list(items, 72.0, 700.0, BulletStyle.CIRCLE)

        doc = Document()
        doc.add_page(page)
        data = doc.save_to_bytes()

        assert data[:5] == b"%PDF-"
