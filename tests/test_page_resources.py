"""Tests for PdfReader.get_page_resources — READ-011.

Semantic tests against fixture PDFs with known resource content. No smoke
tests; every assertion validates real behavior against a known input.
"""

import pytest

from helpers import _minimal_jpeg


# ── Fixture builders ──────────────────────────────────────────────────────────


def _build_font_page() -> bytes:
    """PDF with a single page using Helvetica-Bold standard Type1 font.

    The writer pre-registers all 12 standard Type1 fonts with their base
    names as resource keys (``/Helvetica-Bold``, ``/Times-Roman``, etc.).
    None of the standard fonts are embedded; none are subset.
    """
    from oxidize_pdf import Document, Font, Page

    doc = Document()
    page = Page.a4()
    page.set_font(Font.HELVETICA_BOLD, 14.0)
    page.text_at(50.0, 700.0, "Fixture content for READ-011")
    doc.add_page(page)
    return doc.save_to_bytes()


def _build_image_page() -> bytes:
    """PDF with a page containing one JPEG XObject (1x1 grayscale pixel).

    Produces ``/XObject/Im1`` with ``Subtype=Image``, ``Filter=DCTDecode``,
    ``Width=1``, ``Height=1``, ``BitsPerComponent=8``, ``ColorSpace=DeviceGray``.
    The XObject is stored as an indirect reference in the page Resources,
    so the bridge must resolve it to inspect the image dictionary.
    """
    from oxidize_pdf import Document, Image, Page

    doc = Document()
    page = Page.a4()
    img = Image.from_jpeg_data(_minimal_jpeg())
    page.add_image("Im1", img)
    page.draw_image("Im1", 100.0, 100.0, 50.0, 50.0)
    doc.add_page(page)
    return doc.save_to_bytes()


def _build_extgstate_page() -> bytes:
    """PDF with a page that sets fill opacity to 0.5.

    The writer auto-names the state ``/GS1`` and emits ``/ca 0.5`` as a
    direct float value inside the ExtGState sub-dictionary.
    """
    from oxidize_pdf import Document, Page

    doc = Document()
    page = Page.a4()
    page.set_fill_opacity(0.5)
    page.draw_rect(50.0, 500.0, 100.0, 50.0)
    page.fill()
    doc.add_page(page)
    return doc.save_to_bytes()


def _assemble_raw_pdf(objects: list[bytes]) -> bytes:
    """Serialize a list of object bodies (object #1 first) into a valid PDF.

    Each entry is the ``<< ... >>`` or ``<< ... >>\\nstream\\n...\\nendstream``
    blob; the helper writes the ``N 0 obj`` / ``endobj`` wrappers, xref, and
    trailer. Root is always object #1.
    """
    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    body = bytearray(header)
    offsets: list[int] = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body.extend(f"{i} 0 obj\n".encode())
        body.extend(obj)
        body.extend(b"\nendobj\n")

    xref_offset = len(body)
    body.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    body.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        body.extend(f"{off:010d} 00000 n \n".encode())
    body.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode())
    body.extend(f"startxref\n{xref_offset}\n%%EOF\n".encode())
    return bytes(body)


def _build_no_resources_page() -> bytes:
    """Raw-bytes minimal PDF whose single page has no ``/Resources`` entry.

    Tests the ``None`` return path of ``get_page_resources`` — the core
    returns ``Option<&PdfDictionary>`` and the bridge surfaces ``None``
    when the page has neither a direct nor an inherited Resources dict.
    """
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>",
    ]
    return _assemble_raw_pdf(objects)


def _build_inherited_resources_page() -> bytes:
    """Raw-bytes PDF where ``/Resources`` sits on the ``/Pages`` parent.

    The leaf ``/Page`` (obj 3) deliberately omits ``/Resources``; the parent
    ``/Pages`` node (obj 2) owns a Resources dict carrying one Type1 font.
    A conforming reader must surface the inherited resources when the leaf
    has none of its own.
    """
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        (
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 "
            b"/Resources << /Font << /F1 4 0 R >> /ProcSet [/PDF /Text] >> >>"
        ),
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>",
        (
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
            b"/Encoding /WinAnsiEncoding >>"
        ),
    ]
    return _assemble_raw_pdf(objects)


def _build_type0_font_page() -> bytes:
    """Raw-bytes PDF with a ``/Type0`` composite font whose CIDFont descendant
    carries an embedded ``/FontFile2`` stream.

    Verifies that ``FontResource.is_embedded`` navigates through
    ``/DescendantFonts`` when the top-level ``/Type0`` dictionary has no
    ``/FontDescriptor`` of its own — the canonical shape of every embedded
    CJK, emoji, or Unicode-complete font in real-world PDFs.
    """
    fontfile_stream = b"<< /Length 0 >>\nstream\n\nendstream"
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> >>"
        ),
        (
            b"<< /Type /Font /Subtype /Type0 /BaseFont /ABCDEF+CustomCID "
            b"/Encoding /Identity-H /DescendantFonts [5 0 R] >>"
        ),
        (
            b"<< /Type /Font /Subtype /CIDFontType2 /BaseFont /ABCDEF+CustomCID "
            b"/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> "
            b"/FontDescriptor 6 0 R >>"
        ),
        (
            b"<< /Type /FontDescriptor /FontName /ABCDEF+CustomCID /Flags 4 "
            b"/FontBBox [0 0 1000 1000] /ItalicAngle 0 /Ascent 800 /Descent -200 "
            b"/CapHeight 700 /StemV 80 /FontFile2 7 0 R >>"
        ),
        fontfile_stream,
    ]
    return _assemble_raw_pdf(objects)


def _build_encrypted_page() -> bytes:
    """PDF encrypted with a user password — the bridge must refuse resource
    access on a reader that has not been unlocked."""
    from oxidize_pdf import Document, Font, Page

    doc = Document()
    page = Page.a4()
    page.set_font(Font.HELVETICA, 12.0)
    page.text_at(72.0, 700.0, "secret")
    doc.add_page(page)
    doc.encrypt("user-pw", "owner-pw")
    return doc.save_to_bytes()


# ── T5: High-level PageResources contract ─────────────────────────────────────


class TestPageResourcesContract:
    def test_returns_none_when_page_has_no_resources(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_no_resources_page())
        assert reader.get_page_resources(0) is None

    def test_returns_object_with_fonts_dict_when_fonts_present(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert isinstance(resources.fonts, dict)
        assert len(resources.fonts) >= 1

    def test_resource_keys_contains_font_for_fonts_fixture(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert isinstance(resources.resource_keys, list)
        assert "Font" in resources.resource_keys

    def test_proc_sets_is_list(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert isinstance(resources.proc_sets, list)

    def test_empty_categories_return_empty_dicts_not_none(self):
        """Categories absent from the page still exist as empty dicts."""
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        # The font fixture has no images or forms — both must be empty dicts
        # with no resource entries, not None.
        assert resources.images == {}
        assert resources.forms == {}


# ── T6: FontResource semantic checks ──────────────────────────────────────────


class TestFontResource:
    def test_fonts_dict_keys_are_base_font_names(self):
        """The writer registers Helvetica-Bold as key 'Helvetica-Bold'."""
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert "Helvetica-Bold" in resources.fonts

    def test_helvetica_bold_subtype_is_type1(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        font = resources.fonts["Helvetica-Bold"]
        assert font.subtype == "Type1"

    def test_helvetica_bold_base_font_field(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        font = resources.fonts["Helvetica-Bold"]
        assert font.base_font == "Helvetica-Bold"

    def test_helvetica_bold_encoding_is_winansi(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        font = resources.fonts["Helvetica-Bold"]
        assert font.encoding == "WinAnsiEncoding"

    def test_standard_font_is_not_embedded(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        font = resources.fonts["Helvetica-Bold"]
        assert font.is_embedded is False

    def test_standard_font_is_not_subset(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        font = resources.fonts["Helvetica-Bold"]
        assert font.is_subset is False


# ── T7: ImageResource semantic checks ─────────────────────────────────────────


class TestImageResource:
    def test_images_dict_contains_im1(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_image_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert "Im1" in resources.images

    def test_image_dimensions_are_1x1(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_image_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        image = resources.images["Im1"]
        assert image.width == 1
        assert image.height == 1

    def test_image_bits_per_component_is_8(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_image_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        image = resources.images["Im1"]
        assert image.bits_per_component == 8

    def test_jpeg_filter_is_dctdecode(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_image_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        image = resources.images["Im1"]
        assert "DCTDecode" in image.filter

    def test_image_color_space_is_device_rgb_or_gray(self):
        """The 1-component minimal JPEG maps to DeviceGray."""
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_image_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        image = resources.images["Im1"]
        assert image.color_space in ("DeviceGray", "DeviceRGB")


# ── T8a: ExtGStateResource ────────────────────────────────────────────────────


class TestExtGStateResource:
    def test_extgstate_dict_contains_gs1(self):
        """The writer auto-names the opacity state '/GS1'."""
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_extgstate_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert "GS1" in resources.ext_g_states

    def test_extgstate_entry_has_ca_key(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_extgstate_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        gs1 = resources.ext_g_states["GS1"]
        assert "ca" in gs1

    def test_extgstate_ca_value_is_half(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_extgstate_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        gs1 = resources.ext_g_states["GS1"]
        assert gs1["ca"] == pytest.approx(0.5)


# ── T8b: Bounds and indexing ──────────────────────────────────────────────────


class TestBoundsAndIndexing:
    def test_zero_index_works_on_single_page_doc(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_font_page())
        # Should not raise; return value must be non-None given the fixture.
        resources = reader.get_page_resources(0)
        assert resources is not None

    def test_index_out_of_bounds_raises(self):
        from oxidize_pdf import PdfError, PdfReader

        reader = PdfReader.from_bytes(_build_font_page())
        with pytest.raises((IndexError, PdfError)):
            reader.get_page_resources(9999)


# ── Inherited resources (B3 — carried from quality review) ────────────────────


class TestInheritedResources:
    """A page that omits ``/Resources`` must still surface the dict inherited
    from a ``/Pages`` ancestor. This is the canonical shape of many
    real-world PDFs and was absent from the original fixture set."""

    def test_inherited_resources_are_returned(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_inherited_resources_page())
        resources = reader.get_page_resources(0)
        assert resources is not None

    def test_inherited_font_is_surfaced(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_inherited_resources_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert "F1" in resources.fonts
        assert resources.fonts["F1"].base_font == "Helvetica"

    def test_inherited_proc_set_is_surfaced(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_inherited_resources_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert "PDF" in resources.proc_sets
        assert "Text" in resources.proc_sets


# ── Composite Type0 fonts (B3 — carried from quality review) ──────────────────


class TestType0CompositeFont:
    """Embedded Type0 fonts hold the ``/FontDescriptor`` inside their
    ``/DescendantFonts`` CIDFont, not at the top level. Without descending
    into that array, ``is_embedded`` is a false negative for every modern
    CJK / emoji font."""

    def test_type0_is_surfaced_as_font(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_type0_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert "F1" in resources.fonts

    def test_type0_subtype_is_reported(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_type0_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert resources.fonts["F1"].subtype == "Type0"

    def test_type0_base_font_preserves_subset_tag(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_type0_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert resources.fonts["F1"].base_font == "ABCDEF+CustomCID"

    def test_type0_subset_flag_detected_from_basefont(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_type0_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert resources.fonts["F1"].is_subset is True

    def test_type0_is_embedded_via_descendant_font_descriptor(self):
        from oxidize_pdf import PdfReader

        reader = PdfReader.from_bytes(_build_type0_font_page())
        resources = reader.get_page_resources(0)
        assert resources is not None
        assert resources.fonts["F1"].is_embedded is True


# ── Encrypted documents (M3 — contract under lock) ────────────────────────────


class TestEncryptedDocument:
    """Calling ``get_page_resources`` on an encrypted reader that has not
    been unlocked must not silently succeed with empty dicts. The current
    contract is to raise — this test locks that behavior in."""

    def test_locked_reader_raises_on_resource_access(self):
        from oxidize_pdf import PdfError, PdfReader

        reader = PdfReader.from_bytes(_build_encrypted_page())
        assert reader.is_encrypted is True
        with pytest.raises(PdfError):
            reader.get_page_resources(0)


# ── Recursion guard (M2) ──────────────────────────────────────────────────────


class TestExtGStateRecursionGuard:
    """``pdf_object_to_py`` walks ``/ExtGState`` entries recursively. A
    pathological PDF with deep dict nesting must not crash the thread via
    stack overflow — it should collapse oversized branches to ``None``."""

    def test_deeply_nested_extgstate_does_not_overflow(self):
        from oxidize_pdf import PdfReader

        # Build /GS1 with 256 levels of nested dictionaries under /Custom.
        # 256 comfortably exceeds the 64-deep guard in the bridge.
        nested = b"<< /Leaf true >>"
        for _ in range(256):
            nested = b"<< /Inner " + nested + b" >>"

        objects: list[bytes] = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            (
                b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                b"/Resources << /ExtGState << /GS1 4 0 R >> >> >>"
            ),
            b"<< /ca 0.5 /Custom " + nested + b" >>",
        ]
        pdf_bytes = _assemble_raw_pdf(objects)

        # The call must return without raising or crashing the interpreter.
        reader = PdfReader.from_bytes(pdf_bytes)
        resources = reader.get_page_resources(0)
        assert resources is not None
        gs1 = resources.ext_g_states["GS1"]
        # Shallow entries survive the depth guard.
        assert gs1["ca"] == pytest.approx(0.5)
        # The deep branch collapses to None at the guard.
        deep = gs1["Custom"]
        for _ in range(80):
            if deep is None:
                break
            if isinstance(deep, dict):
                deep = deep.get("Inner")
            else:
                break
        assert deep is None
