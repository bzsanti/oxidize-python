"""Gradient rendering surface (oxidize-pdf 2.14.0, issue #297).

Mirrors the upstream paint path on the Python side: shadings registered with
``Page.add_shading`` are emitted at ``/Resources/Shading/<name>`` and painted
with the ``sh`` operator, bounded by a ``W n`` clip. Every assertion reads the
*decoded content stream bytes* or the *raw serialized PDF*, never a return code
or byte count.

Operator serialization (verified): the writer emits one operator per line,
``\\n``-separated — e.g. ``re\\n``, ``W\\n``, ``n\\n``, ``/Sh1 sh\\n``.
"""

import pytest

from oxidize_pdf import (
    AxialShading,
    Color,
    Document,
    Page,
    PdfError,
    PdfReader,
    RadialShading,
    ShadingPoint,
)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _content(doc: Document) -> bytes:
    """Serialize ``doc`` and return its first page's decoded content stream(s)."""
    reader = PdfReader.from_bytes(doc.save_to_bytes())
    return b"".join(reader.get_page_content_streams(0))


def _pos(content: bytes, needle: bytes) -> int:
    idx = content.find(needle)
    assert idx != -1, f"{needle!r} not found in content stream:\n{content!r}"
    return idx


def _axial(name: str = "Sh1") -> AxialShading:
    return AxialShading.linear_gradient(
        name,
        ShadingPoint(50.0, 700.0),
        ShadingPoint(250.0, 700.0),
        Color.red(),
        Color.blue(),
    )


def _radial(name: str = "Sh2") -> RadialShading:
    return RadialShading.radial_gradient(
        name,
        ShadingPoint(150.0, 700.0),
        0.0,
        80.0,
        Color.white(),
        Color.black(),
    )


# ── end_path (`n`) ────────────────────────────────────────────────────────────


def test_end_path_emits_n_operator():
    doc = Document()
    page = Page.a4()
    page.move_to(0.0, 0.0)
    page.line_to(100.0, 0.0)
    page.end_path()
    doc.add_page(page)

    content = _content(doc)
    assert b"\nn\n" in content, content


# ── clip (`W`) / clip_even_odd (`W*`) ──────────────────────────────────────────


def test_clip_emits_W_operator():
    doc = Document()
    page = Page.a4()
    page.draw_rect(50.0, 50.0, 200.0, 200.0)
    page.clip()
    page.end_path()
    doc.add_page(page)

    content = _content(doc)
    assert b"\nW\n" in content, content


def test_clip_even_odd_emits_W_star_operator():
    doc = Document()
    page = Page.a4()
    page.draw_rect(50.0, 50.0, 200.0, 200.0)
    page.clip_even_odd()
    page.end_path()
    doc.add_page(page)

    content = _content(doc)
    assert b"\nW*\n" in content, content


# ── paint_shading (`sh`) ───────────────────────────────────────────────────────


def test_paint_shading_emits_sh_operator():
    """`sh` is a content-stream operator, independent of resource registration."""
    doc = Document()
    page = Page.a4()
    page.paint_shading("Sh1")
    doc.add_page(page)

    content = _content(doc)
    assert b"/Sh1 sh\n" in content, content


def test_paint_shading_without_registration_writes_no_shading_resource():
    """Unregistered name: the `sh` operator is emitted but no /Shading dict
    is written — the documented "undefined resource" contract (#297)."""
    doc = Document()
    page = Page.a4()
    page.paint_shading("Ghost")
    doc.add_page(page)

    pdf_bytes = doc.save_to_bytes()
    content = b"".join(PdfReader.from_bytes(pdf_bytes).get_page_content_streams(0))

    assert b"/Ghost sh\n" in content, content
    assert b"/Shading" not in pdf_bytes, (
        "no shading was registered, so no /Shading resource must be written"
    )


# ── add_shading: resource registration ─────────────────────────────────────────


def test_add_axial_shading_registers_shading_type_2():
    doc = Document()
    page = Page.a4()
    page.add_shading("GradA", _axial("GradA"))
    doc.add_page(page)

    raw = doc.save_to_bytes()
    assert b"/GradA" in raw, "axial shading name not registered"
    assert b"/Shading" in raw, "/Shading resource dictionary missing"
    assert b"/ShadingType 2" in raw, "axial shading must be ShadingType 2"


def test_add_radial_shading_registers_shading_type_3():
    doc = Document()
    page = Page.a4()
    page.add_shading("GradR", _radial("GradR"))
    doc.add_page(page)

    raw = doc.save_to_bytes()
    assert b"/GradR" in raw, "radial shading name not registered"
    assert b"/ShadingType 3" in raw, "radial shading must be ShadingType 3"


def test_add_shading_invalid_name_raises():
    page = Page.a4()
    with pytest.raises(PdfError):
        page.add_shading("bad name with spaces", _axial("bad name with spaces"))


def test_add_shading_rejects_non_shading_object():
    page = Page.a4()
    with pytest.raises(TypeError):
        page.add_shading("X", object())  # type: ignore[arg-type]


# ── Full canonical workflow: q <path> W n /Sh sh Q ─────────────────────────────


def test_axial_gradient_full_workflow_stream_and_resources():
    """Canonical bounded-gradient sequence with a real `/Function` (issue #297)."""
    doc = Document()
    page = Page.a4()

    page.add_shading("Sh1", _axial("Sh1"))
    page.save_graphics_state()
    page.draw_rect(50.0, 680.0, 200.0, 40.0)
    page.clip()
    page.end_path()
    page.paint_shading("Sh1")
    page.restore_graphics_state()
    doc.add_page(page)

    pdf_bytes = doc.save_to_bytes()
    content = b"".join(PdfReader.from_bytes(pdf_bytes).get_page_content_streams(0))

    # Operators in document order: W → n → /Sh1 sh
    w_pos = _pos(content, b"\nW\n")
    n_pos = content.find(b"\nn\n", w_pos)
    assert n_pos != -1, f"`n` must follow `W`:\n{content!r}"
    sh_pos = content.find(b"/Sh1 sh\n", n_pos)
    assert sh_pos != -1, f"`/Sh1 sh` must follow `W n`:\n{content!r}"

    # Resource side: real gradient function, not a placeholder
    assert b"/Shading" in pdf_bytes, "/Shading resource dict missing"
    assert b"/ShadingType 2" in pdf_bytes, "axial ShadingType 2 missing"
    assert b"/Function" in pdf_bytes, "/Function missing — gradient not real (#297)"
    # Two colour stops → a type-2 (exponential) function, not a placeholder int
    assert b"/FunctionType 2" in pdf_bytes, (
        "2-stop axial gradient must emit a Type 2 exponential function (#297)"
    )


def test_radial_gradient_full_workflow_registers_shading_type_3():
    doc = Document()
    page = Page.a4()

    page.add_shading("Sh2", _radial("Sh2"))
    page.save_graphics_state()
    page.draw_circle(150.0, 700.0, 80.0)
    page.clip()
    page.end_path()
    page.paint_shading("Sh2")
    page.restore_graphics_state()
    doc.add_page(page)

    pdf_bytes = doc.save_to_bytes()
    content = b"".join(PdfReader.from_bytes(pdf_bytes).get_page_content_streams(0))
    assert b"/Sh2 sh\n" in content, content
    assert b"/ShadingType 3" in pdf_bytes, "radial ShadingType 3 missing"
    assert b"/Function" in pdf_bytes, "/Function missing — gradient not real (#297)"


def test_two_shadings_on_same_page_coexist():
    """Distinct shadings registered under different names must both survive in
    the page resource dict and both be paintable."""
    doc = Document()
    page = Page.a4()

    page.add_shading("Sh1", _axial("Sh1"))
    page.add_shading("Sh2", _radial("Sh2"))
    page.paint_shading("Sh1")
    page.paint_shading("Sh2")
    doc.add_page(page)

    pdf_bytes = doc.save_to_bytes()
    content = b"".join(PdfReader.from_bytes(pdf_bytes).get_page_content_streams(0))

    # Both operators present, in registration order
    sh1 = _pos(content, b"/Sh1 sh\n")
    sh2 = content.find(b"/Sh2 sh\n", sh1)
    assert sh2 != -1, f"second shading paint missing:\n{content!r}"

    # Both shading types coexist in resources (axial + radial, not overwritten)
    assert b"/ShadingType 2" in pdf_bytes, "axial entry overwritten or missing"
    assert b"/ShadingType 3" in pdf_bytes, "radial entry overwritten or missing"
