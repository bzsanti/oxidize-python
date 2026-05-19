"""Regression for issue #57 — `set_fill_color()` applied before `text_at()`
must actually colour the text.

Bug in oxidize-pdf 2.8.0: after drawing and filling a shape, a subsequent
`page.set_fill_color(new_color)` followed by `page.text_at(...)` did not
emit a fresh non-stroking colour (`rg`) before the text block, so the
text inherited the previous shape's fill colour. Upstream fix landed in
oxidize-pdf #239 (released as 2.8.2).

The tests assert the actual PDF operator sequence emitted into the
page's Contents stream — not a smoke test on `len(bytes) > 0`.
"""

import re

import pytest


# Match any non-stroking RGB colour operator: ``r g b rg`` with integer or
# float operands. The writer in oxidize-pdf 2.8.2 emits three-decimal
# floats (e.g. ``1.000 1.000 1.000 rg``), but older / future versions may
# choose ``1 1 1 rg``. Both are valid PDF and must satisfy the test.
_RG_OP_RE = re.compile(rb"(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+rg")


def _rg_operands_in(stream: bytes) -> list[tuple[float, float, float]]:
    """Return every ``r g b rg`` operand triple as floats, in stream order."""
    return [
        (float(m.group(1)), float(m.group(2)), float(m.group(3)))
        for m in _RG_OP_RE.finditer(stream)
    ]


def _approx_eq(a: float, b: float, tol: float = 1e-3) -> bool:
    return abs(a - b) <= tol


# ── Helpers ──────────────────────────────────────────────────────────────────


def _build_filled_rect_then_text() -> bytes:
    """Reproducer from issue #57: magenta filled band, then white text on top.

    Both the rect fill colour and the text fill colour are set with
    ``set_fill_color``. The text must render in white, not magenta.
    """
    from oxidize_pdf import Color, Document, Font, Page

    doc = Document()
    page = Page.a4()

    page.set_fill_color(Color.rgb(0.851, 0.275, 0.937))  # magenta band
    page.draw_rect(0.0, 600.0, 595.0, 200.0)
    page.fill()

    page.set_fill_color(Color.rgb(1.0, 1.0, 1.0))  # white text colour
    page.set_font(Font.HELVETICA_BOLD, 32.0)
    page.text_at(50.0, 700.0, "Hello white")

    doc.add_page(page)
    return doc.save_to_bytes()


def _page_content_stream(pdf_bytes: bytes, page_index: int = 0) -> bytes:
    """Return the page's decoded Contents stream concatenated as bytes."""
    from oxidize_pdf import PdfReader

    reader = PdfReader.from_bytes(pdf_bytes)
    return b"\n".join(reader.get_page_content_streams(page_index))


# ── Assertions ────────────────────────────────────────────────────────────────


def test_white_fill_color_is_emitted_before_text():
    """After ``set_fill_color(white)`` and a ``text_at`` call, a white
    non-stroking-colour operator (``r g b rg`` with r=g=b=1) must appear
    in the Contents stream — otherwise the text inherits the prior
    magenta fill.
    """
    stream = _page_content_stream(_build_filled_rect_then_text())
    rgs = _rg_operands_in(stream)
    has_white = any(
        _approx_eq(r, 1.0) and _approx_eq(g, 1.0) and _approx_eq(b, 1.0)
        for (r, g, b) in rgs
    )
    assert has_white, (
        "Expected a white non-stroking-colour operator "
        "(`1 1 1 rg` or `1.000 1.000 1.000 rg`) after "
        "`set_fill_color(white)`. None was emitted; the text would "
        "inherit the prior fill colour (issue #57). "
        f"Operands seen: {rgs!r}"
    )


def test_white_fill_color_appears_after_magenta_rect_fill():
    """The white ``rg`` must be emitted AFTER the magenta ``rg`` used
    for the rectangle, so the graphics-state ordering matches the
    user's source order.
    """
    stream = _page_content_stream(_build_filled_rect_then_text())
    rgs = _rg_operands_in(stream)

    magenta_pos = next(
        (
            i
            for i, (r, g, b) in enumerate(rgs)
            if _approx_eq(r, 0.851) and _approx_eq(g, 0.275) and _approx_eq(b, 0.937)
        ),
        -1,
    )
    white_pos = next(
        (
            i
            for i, (r, g, b) in enumerate(rgs)
            if _approx_eq(r, 1.0) and _approx_eq(g, 1.0) and _approx_eq(b, 1.0)
        ),
        -1,
    )

    assert magenta_pos != -1, f"Magenta fill colour not found. Operands: {rgs!r}"
    assert white_pos != -1, f"White fill colour not found (issue #57). Operands: {rgs!r}"
    assert white_pos > magenta_pos, (
        f"White rg (pos={white_pos}) must appear after magenta rg "
        f"(pos={magenta_pos}); operator order is wrong. Operands: {rgs!r}"
    )


def test_two_distinct_rg_operators_emitted():
    """Sanity check: at least one ``rg`` per ``set_fill_color`` call.
    If the bug is present, only the magenta ``rg`` is in the stream.
    """
    stream = _page_content_stream(_build_filled_rect_then_text())
    rgs = _rg_operands_in(stream)
    assert len(rgs) >= 2, (
        f"Expected at least 2 non-stroking-colour operators (`rg`), "
        f"found {len(rgs)}. Issue #57 likely regressed. Operands: {rgs!r}"
    )


def test_text_block_carries_white_rg_inside_bt_et():
    """Stronger check: the text-rendering block (between ``BT`` and the
    next ``ET``) must itself carry the white ``rg`` — placing the white
    operator outside the text object would not affect glyph fill in
    every PDF viewer.
    """
    stream = _page_content_stream(_build_filled_rect_then_text())
    bt_idx = stream.find(b"BT")
    et_idx = stream.find(b"ET", bt_idx + 2) if bt_idx != -1 else -1
    assert bt_idx != -1 and et_idx != -1, "BT/ET text block not found in stream."

    inside = stream[bt_idx:et_idx]
    rgs_inside = _rg_operands_in(inside)
    has_white_inside = any(
        _approx_eq(r, 1.0) and _approx_eq(g, 1.0) and _approx_eq(b, 1.0)
        for (r, g, b) in rgs_inside
    )
    assert has_white_inside, (
        "Expected white `rg` inside the BT/ET text object (issue #57). "
        f"Operands inside text block: {rgs_inside!r}"
    )
