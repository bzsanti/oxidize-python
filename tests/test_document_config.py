import pytest


# ── Feature 45: Open Action ───────────────────────────────────────────────


def test_set_open_action_goto_renders_pdf():
    from oxidize_pdf import Document, GoToAction, Page

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)

    action = GoToAction.to_page(0)
    doc.set_open_action_goto(action)

    data = doc.save_to_bytes()
    assert len(data) > 0
    assert data[:4] == b"%PDF"


def test_set_open_action_uri_renders_pdf():
    from oxidize_pdf import Document, Page, UriAction

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)

    action = UriAction("https://example.com")
    doc.set_open_action_uri(action)

    data = doc.save_to_bytes()
    assert len(data) > 0
    assert data[:4] == b"%PDF"


def test_set_open_action_goto_xyz():
    from oxidize_pdf import Document, GoToAction, Page

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)

    action = GoToAction.to_page_xyz(0, 0.0, 792.0, 1.0)
    doc.set_open_action_goto(action)

    data = doc.save_to_bytes()
    assert len(data) > 0


def test_set_open_action_uri_web():
    from oxidize_pdf import Document, Page, UriAction

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)

    action = UriAction.web("https://example.com")
    doc.set_open_action_uri(action)

    data = doc.save_to_bytes()
    assert len(data) > 0


# ── Feature 46: Font Management ───────────────────────────────────────────


def test_has_custom_font_on_fresh_document():
    from oxidize_pdf import Document

    doc = Document()
    assert doc.has_custom_font("NonExistent") is False


def test_custom_font_names_on_fresh_document():
    from oxidize_pdf import Document

    doc = Document()
    names = doc.custom_font_names()
    assert isinstance(names, list)
    assert len(names) == 0


def test_add_font_method_exists():
    from oxidize_pdf import Document

    doc = Document()
    assert hasattr(doc, "add_font")


def test_add_font_from_bytes_method_exists():
    from oxidize_pdf import Document

    doc = Document()
    assert hasattr(doc, "add_font_from_bytes")


def test_add_font_invalid_path_raises():
    from oxidize_pdf import Document, PdfError

    doc = Document()
    with pytest.raises(PdfError):
        doc.add_font("Test", "/nonexistent/path/to/font.ttf")


def test_add_font_from_bytes_invalid_data_raises():
    from oxidize_pdf import Document, PdfError

    doc = Document()
    with pytest.raises(PdfError):
        doc.add_font_from_bytes("Test", b"not a font")


# ── Feature 47: WriterConfig + Compression ────────────────────────────────


def test_writer_config_default():
    from oxidize_pdf import WriterConfig

    config = WriterConfig()
    assert config.compress_streams is True
    assert config.use_xref_streams is False
    assert config.use_object_streams is False


def test_writer_config_modern():
    from oxidize_pdf import WriterConfig

    config = WriterConfig.modern()
    assert config.compress_streams is True
    assert config.use_xref_streams is True
    assert config.use_object_streams is True


def test_writer_config_legacy():
    from oxidize_pdf import WriterConfig

    config = WriterConfig.legacy()
    assert config.compress_streams is True
    assert config.use_xref_streams is False
    assert config.use_object_streams is False


def test_writer_config_incremental():
    from oxidize_pdf import WriterConfig

    config = WriterConfig.incremental()
    assert config.compress_streams is True
    assert config.use_xref_streams is False


def test_writer_config_repr():
    from oxidize_pdf import WriterConfig

    config = WriterConfig()
    r = repr(config)
    assert "WriterConfig" in r


def test_set_compress_true():
    from oxidize_pdf import Document, Page

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)
    doc.set_compress(True)
    data = doc.save_to_bytes()
    assert len(data) > 0


def test_set_compress_false():
    from oxidize_pdf import Document, Page

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)
    doc.set_compress(False)
    data = doc.save_to_bytes()
    assert len(data) > 0


def test_enable_xref_streams():
    from oxidize_pdf import Document, Page

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)
    doc.enable_xref_streams(True)
    data = doc.save_to_bytes()
    assert len(data) > 0


def test_save_with_config(tmp_path):
    from oxidize_pdf import Document, Page, WriterConfig

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)

    config = WriterConfig.modern()
    path = str(tmp_path / "output.pdf")
    doc.save_with_config(path, config)

    import os

    assert os.path.exists(path)
    assert os.path.getsize(path) > 0


def test_save_with_config_legacy(tmp_path):
    from oxidize_pdf import Document, Page, WriterConfig

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)

    config = WriterConfig.legacy()
    path = str(tmp_path / "output_legacy.pdf")
    doc.save_with_config(path, config)

    import os

    assert os.path.exists(path)


# ── WRITE-006 completion: pdf_version + save_to_bytes_with_config ─────────
#
# The preset factories already carry the right pdf_version in the core
# config, but the Python bridge neither exposes a getter nor accepts a
# kwarg — so callers can build a "modern" config without being able to
# read or override the version string. The in-memory variant
# `save_to_bytes_with_config` is also missing, forcing every roundtrip
# through tmpfiles even when bytes are what the caller actually wants.


def test_writer_config_default_pdf_version_is_1_7():
    from oxidize_pdf import WriterConfig

    assert WriterConfig().pdf_version == "1.7"


def test_writer_config_modern_pdf_version_is_1_5():
    from oxidize_pdf import WriterConfig

    assert WriterConfig.modern().pdf_version == "1.5"


def test_writer_config_legacy_pdf_version_is_1_4():
    from oxidize_pdf import WriterConfig

    assert WriterConfig.legacy().pdf_version == "1.4"


def test_writer_config_incremental_pdf_version_is_1_4():
    from oxidize_pdf import WriterConfig

    assert WriterConfig.incremental().pdf_version == "1.4"


def test_writer_config_accepts_custom_pdf_version_kwarg():
    from oxidize_pdf import WriterConfig

    assert WriterConfig(pdf_version="1.6").pdf_version == "1.6"


def test_writer_config_incremental_update_default_is_false():
    from oxidize_pdf import WriterConfig

    assert WriterConfig().incremental_update is False


def test_writer_config_incremental_preset_sets_incremental_update():
    from oxidize_pdf import WriterConfig

    assert WriterConfig.incremental().incremental_update is True


def test_writer_config_modern_does_not_use_incremental_update():
    from oxidize_pdf import WriterConfig

    assert WriterConfig.modern().incremental_update is False


def test_save_to_bytes_with_config_returns_non_empty_bytes():
    from oxidize_pdf import Document, Page, WriterConfig

    doc = Document()
    doc.add_page(Page.a4())
    data = doc.save_to_bytes_with_config(WriterConfig.modern())
    assert isinstance(data, bytes)
    assert len(data) > 0


def test_save_to_bytes_with_config_writes_requested_pdf_version_header():
    from oxidize_pdf import Document, Page, WriterConfig

    doc = Document()
    doc.add_page(Page.a4())
    data = doc.save_to_bytes_with_config(WriterConfig(pdf_version="1.6"))
    assert data.startswith(b"%PDF-1.6")


def test_save_to_bytes_with_config_modern_header_matches_preset_version():
    from oxidize_pdf import Document, Page, WriterConfig

    doc = Document()
    doc.add_page(Page.a4())
    data = doc.save_to_bytes_with_config(WriterConfig.modern())
    assert data.startswith(b"%PDF-1.5")


def test_save_to_bytes_with_config_legacy_header_matches_preset_version():
    from oxidize_pdf import Document, Page, WriterConfig

    doc = Document()
    doc.add_page(Page.a4())
    data = doc.save_to_bytes_with_config(WriterConfig.legacy())
    assert data.startswith(b"%PDF-1.4")


def test_save_to_bytes_with_config_modern_differs_from_legacy():
    """Modern (xref streams + object streams) produces a structurally
    different container than Legacy. If both outputs were identical the
    config would effectively be a no-op."""
    from oxidize_pdf import Document, Page, WriterConfig

    doc_modern = Document()
    doc_modern.add_page(Page.a4())
    modern_bytes = doc_modern.save_to_bytes_with_config(WriterConfig.modern())

    doc_legacy = Document()
    doc_legacy.add_page(Page.a4())
    legacy_bytes = doc_legacy.save_to_bytes_with_config(WriterConfig.legacy())

    assert modern_bytes != legacy_bytes
    # Modern uses XRef streams (binary), legacy uses the classic xref table.
    assert b"\nxref\n" in legacy_bytes
    assert b"\nxref\n" not in modern_bytes


# ── Feature 48: FontEncoding ──────────────────────────────────────────────


def test_font_encoding_variants():
    from oxidize_pdf import FontEncoding

    assert FontEncoding.WIN_ANSI is not None
    assert FontEncoding.MAC_ROMAN is not None
    assert FontEncoding.STANDARD is not None
    assert FontEncoding.MAC_EXPERT is not None


def test_font_encoding_repr():
    from oxidize_pdf import FontEncoding

    assert repr(FontEncoding.WIN_ANSI) == "FontEncoding.WIN_ANSI"
    assert repr(FontEncoding.MAC_ROMAN) == "FontEncoding.MAC_ROMAN"
    assert repr(FontEncoding.STANDARD) == "FontEncoding.STANDARD"
    assert repr(FontEncoding.MAC_EXPERT) == "FontEncoding.MAC_EXPERT"


def test_set_default_font_encoding():
    from oxidize_pdf import Document, FontEncoding, Page

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)
    doc.set_default_font_encoding(FontEncoding.WIN_ANSI)
    data = doc.save_to_bytes()
    assert len(data) > 0


def test_set_default_font_encoding_mac_roman():
    from oxidize_pdf import Document, FontEncoding, Page

    doc = Document()
    page = Page(612.0, 792.0)
    doc.add_page(page)
    doc.set_default_font_encoding(FontEncoding.MAC_ROMAN)
    data = doc.save_to_bytes()
    assert len(data) > 0
