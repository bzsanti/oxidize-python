"""Behavioral coverage for the extraction integrations from core 5.0–5.1."""

import pytest

import oxidize_pdf as op
from test_core_4_6_bindings import _pdf, _stream
from test_upstream_4_3_0 import _pdf_with_content_stream


@pytest.mark.parametrize("mode,name", enumerate([
    "FILL", "STROKE", "FILL_STROKE", "INVISIBLE", "FILL_CLIP",
    "STROKE_CLIP", "FILL_STROKE_CLIP", "CLIP",
]))
def test_fragment_render_mode(mode, name):
    data = _pdf_with_content_stream(
        f"BT /F1 12 Tf 10 50 Td {mode} Tr (Layer) Tj ET".encode()
    )
    reader = op.PdfReader.from_bytes(data)
    options = op.ExtractionOptions(preserve_layout=True)
    for fragments in (
        reader.extract_fragments_from_page(0, options),
        reader.extract_fragments_with_options(options)[0],
        reader.extract_page_text(0, options).fragments,
    ):
        assert [f.text for f in fragments] == ["Layer"]
        assert repr(fragments[0].render_mode) == f"TextRenderingMode.{name}"
        expected = getattr(op.TextRenderingMode, name)
        assert fragments[0].render_mode == expected
        assert expected == fragments[0].render_mode
        assert fragments[0].render_mode == fragments[0].render_mode
        for other_name in (
            "FILL", "STROKE", "FILL_STROKE", "INVISIBLE", "FILL_CLIP",
            "STROKE_CLIP", "FILL_STROKE_CLIP", "CLIP",
        ):
            assert (fragments[0].render_mode != getattr(op.TextRenderingMode, other_name)) == (
                other_name != name
            )
        assert fragments[0].render_mode != object()


def test_fragment_equality_includes_render_mode():
    fragments = []
    for mode in (0, 3):
        reader = op.PdfReader.from_bytes(_pdf_with_content_stream(
            f"BT /F1 12 Tf 10 50 Td {mode} Tr (Layer) Tj ET".encode()
        ))
        fragments.append(reader.extract_page_text(
            0, op.ExtractionOptions(preserve_layout=True),
        ).fragments[0])
    assert fragments[0] == fragments[0]
    assert fragments[0] != fragments[1]


def _links_pdf():
    return _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] /Annots ["
        b"<< /Subtype /Link /A << /S /URI /URI (mailto:help@example.com) >> >> 4 0 R "
        b"<< /Subtype /Link /A << /S /JavaScript /JS (ignored) >> >>] >>",
        b"<< /Subtype /Link /A << /S /URI /URI (https://example.com) >> >>",
    ])


def test_links_are_opt_in_and_preserve_annotation_order():
    reader = op.PdfReader.from_bytes(_links_pdf())
    assert reader.extract_text_with_options(op.ExtractionOptions()) == [""]
    options = op.ExtractionOptions(include_link_annotations=True)
    expected = "mailto:help@example.com\nhttps://example.com"
    assert options.include_link_annotations
    assert reader.extract_text_with_options(options) == [expected]
    assert reader.extract_page_text(0, options).text == expected


def test_links_respect_extraction_budget():
    reader = op.PdfReader.from_bytes(_links_pdf())
    result = reader.extract_page_text(0, op.ExtractionOptions(
        include_link_annotations=True, max_extracted_bytes=3,
    ))
    assert result.truncated
    assert result.text == ""


@pytest.mark.parametrize("text", ["", "Intro"])
@pytest.mark.parametrize("uri", ["https://example.com", "https://example.com/café"])
@pytest.mark.parametrize("preserve_layout", [False, True])
def test_link_budget_counts_utf8_text_and_separator(text, uri, preserve_layout):
    # PDF Unicode strings use a UTF-16BE BOM; the extraction budget uses UTF-8.
    encoded_uri = (b"\xfe\xff" + uri.encode("utf-16-be")).hex().encode()
    data = _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R "
        b"/Annots [<< /Subtype /Link /A << /S /URI /URI <" + encoded_uri + b"> >> >>] >>",
        _stream("", f"BT /F1 12 Tf 10 50 Td ({text}) Tj ET".encode()),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ])
    reader = op.PdfReader.from_bytes(data)
    expected = f"{text}\n{uri}" if text else uri
    exact_budget = len(expected.encode("utf-8"))
    for budget, expected_text, truncated in (
        (exact_budget, expected, False),
        (exact_budget - 1, text, True),
    ):
        options = op.ExtractionOptions(
            preserve_layout=preserve_layout,
            include_link_annotations=True,
            max_extracted_bytes=budget,
        )
        result = reader.extract_page_text(0, options)
        assert result.text == expected_text
        assert result.truncated is truncated
        assert len(result.text.encode("utf-8")) <= budget
        assert reader.extract_text_with_options(options) == [expected_text]


@pytest.mark.parametrize("preserve_layout", [False, True])
def test_unreliable_figure_text_requires_opt_in(preserve_layout):
    data = _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        _stream("", b"BT /F1 12 Tf 10 70 Td (B) Tj ET "
                b"/Figure BMC BT /F1 12 Tf 10 50 Td (A) Tj ET EMC"),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
        b"/Encoding << /BaseEncoding /WinAnsiEncoding /Differences [65 /B] >> >>",
    ])
    reader = op.PdfReader.from_bytes(data)
    options = op.ExtractionOptions(preserve_layout=preserve_layout)
    assert not options.include_unreliable_figure_text
    assert reader.extract_page_text(0, options).text == "B"
    options = op.ExtractionOptions(
        preserve_layout=preserve_layout, include_unreliable_figure_text=True,
    )
    assert reader.extract_page_text(0, options).text.split() == ["B", "B"]
    assert reader.extract_text_with_options(options)[0].split() == ["B", "B"]
    if preserve_layout:
        assert len(reader.extract_fragments_from_page(0, options)) == 2
        assert len(reader.extract_fragments_with_options(options)[0]) == 2
