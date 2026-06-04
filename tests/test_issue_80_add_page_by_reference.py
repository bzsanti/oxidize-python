"""Regression for issue #80 — draws issued *after* ``Document.add_page`` must
appear in the saved page.

Bug in oxidize-pdf 0.7.0 (Python bridge): ``add_page(page)`` cloned the page's
content at call time (``page.inner.clone()``), so any draw operation performed
on the Python page object after ``add_page`` was lost — the saved page was
blank. ``new_page_a4()`` does not register the page itself, so the natural
"create page, add it, then draw" order silently produced an empty page.

The fix makes the bridge hold a reference to the live Python page object and
materialise its *current* content into the document at ``save`` time, so the
draw order no longer matters.

These tests assert the actual text show operator inside the page's decoded
Contents stream — not a smoke test on ``len(bytes) > 0``.
"""

import oxidize_pdf as ox


def _page0_content(pdf_bytes: bytes) -> bytes:
    """Return page 0's decoded (decompressed) Contents stream."""
    reader = ox.PdfReader.from_bytes(pdf_bytes)
    return b"\n".join(reader.get_page_content_streams(0))


def test_draw_after_add_page_appears_in_output():
    """The exact repro from issue #80: add the page first, draw afterwards."""
    d = ox.Document()
    p = d.new_page_a4()
    d.add_page(p)  # added first
    p.set_font(ox.Font.HELVETICA, 20)
    p.text_at(60, 700, "AFTER add_page")  # drawn after add_page

    stream = _page0_content(d.save_to_bytes())
    assert b"AFTER add_page" in stream


def test_draw_before_add_page_still_works():
    """The previously-working order must keep working (no regression)."""
    d = ox.Document()
    p = d.new_page_a4()
    p.set_font(ox.Font.HELVETICA, 20)
    p.text_at(60, 700, "BEFORE add_page")  # drawn before
    d.add_page(p)

    stream = _page0_content(d.save_to_bytes())
    assert b"BEFORE add_page" in stream


def test_draws_both_before_and_after_add_page():
    """Content drawn before and after add_page must both survive."""
    d = ox.Document()
    p = d.new_page_a4()
    p.set_font(ox.Font.HELVETICA, 18)
    p.text_at(60, 720, "FIRST line")  # before add_page
    d.add_page(p)
    p.text_at(60, 680, "SECOND line")  # after add_page

    stream = _page0_content(d.save_to_bytes())
    assert b"FIRST line" in stream
    assert b"SECOND line" in stream


def test_page_count_reflects_added_pages_before_save():
    """``page_count`` must count pages added but not yet saved."""
    d = ox.Document()
    assert d.page_count == 0
    d.add_page(d.new_page_a4())
    assert d.page_count == 1
    d.add_page(d.new_page_a4())
    assert d.page_count == 2


def test_saving_twice_does_not_duplicate_pages():
    """Re-saving the same document must not re-materialise pages (no dupes)."""
    d = ox.Document()
    p = d.new_page_a4()
    d.add_page(p)
    p.set_font(ox.Font.HELVETICA, 20)
    p.text_at(60, 700, "ONCE")

    first = d.save_to_bytes()
    second = d.save_to_bytes()
    assert ox.PdfReader.from_bytes(first).page_count == 1
    assert ox.PdfReader.from_bytes(second).page_count == 1
    assert b"ONCE" in _page0_content(second)


def test_save_with_config_captures_post_add_draws():
    """The WriterConfig save path must also materialise post-add draws."""
    d = ox.Document()
    p = d.new_page_a4()
    d.add_page(p)
    p.set_font(ox.Font.HELVETICA, 20)
    p.text_at(60, 700, "CONFIG path")

    cfg = ox.WriterConfig()
    stream = _page0_content(d.save_to_bytes_with_config(cfg))
    assert b"CONFIG path" in stream


def test_pages_added_between_saves_are_all_present():
    """A page added after a first save must appear in a later save alongside
    the earlier page (incremental materialisation)."""
    d = ox.Document()
    p1 = d.new_page_a4()
    d.add_page(p1)
    p1.set_font(ox.Font.HELVETICA, 16)
    p1.text_at(50, 700, "EARLY page")
    d.save_to_bytes()  # flushes p1

    p2 = d.new_page_a4()
    d.add_page(p2)
    p2.set_font(ox.Font.HELVETICA, 16)
    p2.text_at(50, 700, "LATE page")

    pdf = d.save_to_bytes()
    reader = ox.PdfReader.from_bytes(pdf)
    assert reader.page_count == 2
    assert b"EARLY page" in b"\n".join(reader.get_page_content_streams(0))
    assert b"LATE page" in b"\n".join(reader.get_page_content_streams(1))


def test_multiple_pages_each_keep_their_own_post_add_draws():
    """Two pages, each drawn on after being added, keep their own content."""
    d = ox.Document()
    p1 = d.new_page_a4()
    p2 = d.new_page_a4()
    d.add_page(p1)
    d.add_page(p2)
    p1.set_font(ox.Font.HELVETICA, 16)
    p1.text_at(50, 700, "PAGE ONE content")
    p2.set_font(ox.Font.HELVETICA, 16)
    p2.text_at(50, 700, "PAGE TWO content")

    pdf = d.save_to_bytes()
    reader = ox.PdfReader.from_bytes(pdf)
    s0 = b"\n".join(reader.get_page_content_streams(0))
    s1 = b"\n".join(reader.get_page_content_streams(1))
    assert b"PAGE ONE content" in s0
    assert b"PAGE TWO content" not in s0
    assert b"PAGE TWO content" in s1
    assert b"PAGE ONE content" not in s1
