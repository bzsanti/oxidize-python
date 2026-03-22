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
