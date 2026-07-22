"""Advanced shading surface (oxidize-pdf 4.1.0, issue #407).

``Page.add_mesh_shading`` registers a Type 4 free-form Gouraud triangle mesh
(emitted as an uncompressed stream: shading dictionary + packed vertex bytes)
and ``Page.add_conic_shading`` registers an exact conic gradient as a Type 1
function-based shading whose ``/Function`` is a Type 4 PostScript calculator.
Both are painted with the pre-existing ``paint_shading`` (``/name sh``).

Every assertion reads the raw serialized PDF or the decoded content stream,
never a return code. The packed-vertex byte assertion mirrors core's
``test_gouraud_vertex_pack_byte_aligned`` fixture: vertex ``flag=0, x=10.0,
y=20.0, rgb(1,0,0)`` with ``decode=[0,100,0,100,0,1,0,1,0,1]`` and default
bit widths (16/8/8) packs to ``00 19 9A 33 33 FF 00 00``.
"""

import pytest

import oxidize_pdf
from oxidize_pdf import (
    AxialShading,
    Color,
    ColorStop,
    ConicShading,
    Document,
    FreeFormGouraudShading,
    GouraudVertex,
    Page,
    PdfError,
    PdfReader,
    ShadingPoint,
)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _content(doc: Document) -> bytes:
    """Serialize ``doc`` and return its first page's decoded content stream(s)."""
    reader = PdfReader.from_bytes(doc.save_to_bytes())
    return b"".join(reader.get_page_content_streams(0))


_RGB_MESH_DECODE = [0.0, 100.0, 0.0, 100.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0]


def _sample_rgb_mesh(name: str = "Mesh1") -> FreeFormGouraudShading:
    """Mirror of core's ``sample_rgb_mesh``: 3 vertices, flags 0/1/1."""
    return FreeFormGouraudShading(
        name,
        "DeviceRGB",
        _RGB_MESH_DECODE,
        [
            GouraudVertex(0, 10.0, 20.0, Color.rgb(1.0, 0.0, 0.0)),
            GouraudVertex(1, 30.0, 40.0, Color.rgb(0.0, 1.0, 0.0)),
            GouraudVertex(1, 50.0, 60.0, Color.rgb(0.0, 0.0, 1.0)),
        ],
    )


def _conic(name: str = "Cone1") -> ConicShading:
    return ConicShading(
        name,
        ShadingPoint(50.0, 50.0),
        [0.0, 100.0, 0.0, 100.0],
        [ColorStop(0.0, Color.red()), ColorStop(1.0, Color.blue())],
    )


def _saved(page: Page) -> bytes:
    doc = Document()
    doc.add_page(page)
    return doc.save_to_bytes()


# ── Page.add_mesh_shading: PDF bytes ─────────────────────────────────────────


class TestAddMeshShading:
    def test_registers_shading_type_4(self):
        page = Page.a4()
        page.add_mesh_shading("Mesh1", _sample_rgb_mesh())
        raw = _saved(page)
        assert b"/ShadingType 4" in raw
        assert b"/BitsPerCoordinate 16" in raw
        assert b"/BitsPerComponent 8" in raw
        assert b"/BitsPerFlag 8" in raw
        assert b"/ColorSpace /DeviceRGB" in raw

    def test_packs_first_vertex_bytes_exactly(self):
        # Cross-checked against core's test_gouraud_vertex_pack_byte_aligned:
        # flag=0 (8 bits), x=10/100 -> 0x1999 (~0x199A rounded), y=20/100,
        # rgb(1,0,0) -> FF 00 00. The Type 4 stream is written uncompressed.
        page = Page.a4()
        page.add_mesh_shading("Mesh1", _sample_rgb_mesh())
        raw = _saved(page)
        assert bytes([0x00, 0x19, 0x9A, 0x33, 0x33, 0xFF, 0x00, 0x00]) in raw

    def test_registers_under_given_name(self):
        page = Page.a4()
        page.add_mesh_shading("Mesh1", _sample_rgb_mesh())
        assert b"/Mesh1" in _saved(page)

    def test_invalid_resource_name_raises(self):
        page = Page.a4()
        with pytest.raises(PdfError):
            page.add_mesh_shading("bad name", _sample_rgb_mesh())

    def test_invalid_mesh_propagates_validation_error(self):
        page = Page.a4()
        bad = _sample_rgb_mesh().with_bits(5, 8, 8)
        with pytest.raises(PdfError, match="BitsPerCoordinate"):
            page.add_mesh_shading("Mesh1", bad)


# ── Page.add_conic_shading: PDF bytes ────────────────────────────────────────


class TestAddConicShading:
    def test_registers_shading_type_1_with_postscript_function(self):
        page = Page.a4()
        page.add_conic_shading("Cone1", _conic())
        raw = _saved(page)
        assert b"/ShadingType 1" in raw
        assert b"/FunctionType 4" in raw
        # Deterministic angle prologue for center (50, 50).
        assert b"50 sub exch 50 sub atan 360 div" in raw

    def test_domain_present(self):
        page = Page.a4()
        page.add_conic_shading("Cone1", _conic())
        assert b"/Domain" in _saved(page)

    def test_with_matrix_writes_matrix_key(self):
        page = Page.a4()
        page.add_conic_shading(
            "Cone1", _conic().with_matrix([1.0, 0.0, 0.0, 1.0, 10.0, 10.0])
        )
        assert b"/Matrix" in _saved(page)

    def test_invalid_resource_name_raises(self):
        page = Page.a4()
        with pytest.raises(PdfError):
            page.add_conic_shading("bad name", _conic())

    def test_empty_stops_propagates_validation_error(self):
        page = Page.a4()
        empty = ConicShading(
            "Cone1", ShadingPoint(50.0, 50.0), [0.0, 100.0, 0.0, 100.0], []
        )
        with pytest.raises(PdfError, match="color stop"):
            page.add_conic_shading("Cone1", empty)


# ── paint_shading integration ────────────────────────────────────────────────


class TestPaintAdvancedShadings:
    def test_paint_mesh_shading_emits_sh_operator(self):
        doc = Document()
        page = Page.a4()
        page.add_mesh_shading("Mesh1", _sample_rgb_mesh())
        page.paint_shading("Mesh1")
        doc.add_page(page)
        assert b"/Mesh1 sh\n" in _content(doc)

    def test_paint_conic_shading_emits_sh_operator(self):
        doc = Document()
        page = Page.a4()
        page.add_conic_shading("Cone1", _conic())
        page.paint_shading("Cone1")
        doc.add_page(page)
        assert b"/Cone1 sh\n" in _content(doc)

    def test_mesh_axial_and_conic_coexist_on_same_page(self):
        # Core keeps classic and advanced shadings in two maps merged into the
        # same /Shading resource dictionary; none may clobber another.
        doc = Document()
        page = Page.a4()
        page.add_shading(
            "Ax1",
            AxialShading.linear_gradient(
                "Ax1",
                ShadingPoint(0.0, 0.0),
                ShadingPoint(100.0, 0.0),
                Color.red(),
                Color.blue(),
            ),
        )
        page.add_mesh_shading("Mesh1", _sample_rgb_mesh())
        page.add_conic_shading("Cone1", _conic())
        page.paint_shading("Ax1")
        page.paint_shading("Mesh1")
        page.paint_shading("Cone1")
        doc.add_page(page)
        raw = doc.save_to_bytes()
        assert b"/ShadingType 2" in raw
        assert b"/ShadingType 4" in raw
        assert b"/ShadingType 1" in raw
        content = _content(doc)
        assert b"/Ax1 sh\n" in content
        assert b"/Mesh1 sh\n" in content
        assert b"/Cone1 sh\n" in content


# ── Exports ──────────────────────────────────────────────────────────────────


class TestExports:
    def test_new_shading_types_in_all(self):
        assert {
            "GouraudVertex",
            "FreeFormGouraudShading",
            "ConicShading",
        } <= set(oxidize_pdf.__all__)
