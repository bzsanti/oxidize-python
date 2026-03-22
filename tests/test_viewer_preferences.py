import pytest


def test_page_layout_variants():
    from oxidize_pdf import PageLayout

    assert PageLayout.SINGLE_PAGE is not None
    assert PageLayout.ONE_COLUMN is not None
    assert PageLayout.TWO_COLUMN_LEFT is not None
    assert PageLayout.TWO_COLUMN_RIGHT is not None
    assert PageLayout.TWO_PAGE_LEFT is not None
    assert PageLayout.TWO_PAGE_RIGHT is not None


def test_page_layout_repr():
    from oxidize_pdf import PageLayout

    assert repr(PageLayout.SINGLE_PAGE) == "PageLayout.SINGLE_PAGE"
    assert repr(PageLayout.ONE_COLUMN) == "PageLayout.ONE_COLUMN"
    assert repr(PageLayout.TWO_COLUMN_LEFT) == "PageLayout.TWO_COLUMN_LEFT"
    assert repr(PageLayout.TWO_COLUMN_RIGHT) == "PageLayout.TWO_COLUMN_RIGHT"
    assert repr(PageLayout.TWO_PAGE_LEFT) == "PageLayout.TWO_PAGE_LEFT"
    assert repr(PageLayout.TWO_PAGE_RIGHT) == "PageLayout.TWO_PAGE_RIGHT"


def test_page_mode_variants():
    from oxidize_pdf import PageMode

    assert PageMode.USE_NONE is not None
    assert PageMode.USE_OUTLINES is not None
    assert PageMode.USE_THUMBS is not None
    assert PageMode.FULL_SCREEN is not None
    assert PageMode.USE_OC is not None
    assert PageMode.USE_ATTACHMENTS is not None


def test_page_mode_repr():
    from oxidize_pdf import PageMode

    assert repr(PageMode.USE_NONE) == "PageMode.USE_NONE"
    assert repr(PageMode.USE_OUTLINES) == "PageMode.USE_OUTLINES"
    assert repr(PageMode.USE_THUMBS) == "PageMode.USE_THUMBS"
    assert repr(PageMode.FULL_SCREEN) == "PageMode.FULL_SCREEN"
    assert repr(PageMode.USE_OC) == "PageMode.USE_OC"
    assert repr(PageMode.USE_ATTACHMENTS) == "PageMode.USE_ATTACHMENTS"


def test_print_scaling_variants():
    from oxidize_pdf import PrintScaling

    assert PrintScaling.NONE is not None
    assert PrintScaling.APP_DEFAULT is not None


def test_print_scaling_repr():
    from oxidize_pdf import PrintScaling

    assert repr(PrintScaling.NONE) == "PrintScaling.NONE"
    assert repr(PrintScaling.APP_DEFAULT) == "PrintScaling.APP_DEFAULT"


def test_duplex_variants():
    from oxidize_pdf import Duplex

    assert Duplex.SIMPLEX is not None
    assert Duplex.FLIP_SHORT_EDGE is not None
    assert Duplex.FLIP_LONG_EDGE is not None


def test_duplex_repr():
    from oxidize_pdf import Duplex

    assert repr(Duplex.SIMPLEX) == "Duplex.SIMPLEX"
    assert repr(Duplex.FLIP_SHORT_EDGE) == "Duplex.FLIP_SHORT_EDGE"
    assert repr(Duplex.FLIP_LONG_EDGE) == "Duplex.FLIP_LONG_EDGE"


def test_viewer_preferences_construction():
    from oxidize_pdf import ViewerPreferences

    prefs = ViewerPreferences()
    assert prefs is not None


def test_viewer_preferences_builder_hide_toolbar():
    from oxidize_pdf import ViewerPreferences

    prefs = ViewerPreferences().hide_toolbar(True)
    assert prefs is not None


def test_viewer_preferences_builder_hide_menubar():
    from oxidize_pdf import ViewerPreferences

    prefs = ViewerPreferences().hide_menubar(True)
    assert prefs is not None


def test_viewer_preferences_builder_hide_window_ui():
    from oxidize_pdf import ViewerPreferences

    prefs = ViewerPreferences().hide_window_ui(True)
    assert prefs is not None


def test_viewer_preferences_builder_fit_window():
    from oxidize_pdf import ViewerPreferences

    prefs = ViewerPreferences().fit_window(True)
    assert prefs is not None


def test_viewer_preferences_builder_center_window():
    from oxidize_pdf import ViewerPreferences

    prefs = ViewerPreferences().center_window(True)
    assert prefs is not None


def test_viewer_preferences_builder_display_doc_title():
    from oxidize_pdf import ViewerPreferences

    prefs = ViewerPreferences().display_doc_title(True)
    assert prefs is not None


def test_viewer_preferences_builder_page_layout():
    from oxidize_pdf import PageLayout, ViewerPreferences

    prefs = ViewerPreferences().page_layout(PageLayout.TWO_COLUMN_LEFT)
    assert prefs is not None


def test_viewer_preferences_builder_page_mode():
    from oxidize_pdf import PageMode, ViewerPreferences

    prefs = ViewerPreferences().page_mode(PageMode.FULL_SCREEN)
    assert prefs is not None


def test_viewer_preferences_builder_print_scaling():
    from oxidize_pdf import PrintScaling, ViewerPreferences

    prefs = ViewerPreferences().print_scaling(PrintScaling.NONE)
    assert prefs is not None


def test_viewer_preferences_builder_duplex():
    from oxidize_pdf import Duplex, ViewerPreferences

    prefs = ViewerPreferences().duplex(Duplex.FLIP_LONG_EDGE)
    assert prefs is not None


def test_viewer_preferences_builder_num_copies():
    from oxidize_pdf import ViewerPreferences

    prefs = ViewerPreferences().num_copies(3)
    assert prefs is not None


def test_viewer_preferences_chaining():
    from oxidize_pdf import Duplex, PageLayout, PageMode, PrintScaling, ViewerPreferences

    prefs = (
        ViewerPreferences()
        .hide_toolbar(True)
        .hide_menubar(True)
        .fit_window(True)
        .center_window(True)
        .display_doc_title(True)
        .page_layout(PageLayout.ONE_COLUMN)
        .page_mode(PageMode.USE_OUTLINES)
        .print_scaling(PrintScaling.APP_DEFAULT)
        .duplex(Duplex.SIMPLEX)
        .num_copies(2)
    )
    assert prefs is not None


def test_viewer_preferences_preset_presentation():
    from oxidize_pdf import ViewerPreferences

    prefs = ViewerPreferences.presentation()
    assert prefs is not None


def test_viewer_preferences_preset_reading():
    from oxidize_pdf import ViewerPreferences

    prefs = ViewerPreferences.reading()
    assert prefs is not None


def test_viewer_preferences_preset_printing():
    from oxidize_pdf import ViewerPreferences

    prefs = ViewerPreferences.printing()
    assert prefs is not None


def test_viewer_preferences_preset_minimal_ui():
    from oxidize_pdf import ViewerPreferences

    prefs = ViewerPreferences.minimal_ui()
    assert prefs is not None


def test_viewer_preferences_set_on_document():
    from oxidize_pdf import Document, Page, ViewerPreferences

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)

    prefs = ViewerPreferences.presentation()
    doc.set_viewer_preferences(prefs)

    data = doc.save_to_bytes()
    assert len(data) > 0
    assert data[:4] == b"%PDF"


def test_viewer_preferences_presentation_renders_pdf():
    from oxidize_pdf import Document, Font, Page, ViewerPreferences

    doc = Document()
    page = Page(612.0, 792.0)
    page.set_font(Font.HELVETICA, 12.0)
    page.text_at(72.0, 700.0, "Test")
    doc.add_page(page)

    doc.set_viewer_preferences(ViewerPreferences.minimal_ui())
    data = doc.save_to_bytes()
    assert len(data) > 0
    assert data[:4] == b"%PDF"
