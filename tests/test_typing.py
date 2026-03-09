"""Type-checking validation script.

This file is checked by mypy to verify that the .pyi stubs are correct
and complete. It exercises every public type, function, and property.
"""

from oxidize_pdf import (
    Color,
    Document,
    Font,
    Margins,
    Page,
    PdfEncryptionError,
    PdfError,
    PdfIoError,
    PdfParseError,
    PdfPermissionError,
    PdfReader,
    Permissions,
    Point,
    Rectangle,
    TextAlign,
    __version__,
    extract_pages,
    merge_pdfs,
    rotate_pdf,
    split_pdf,
)


def check_version() -> str:
    return __version__


def check_color() -> None:
    c1: Color = Color.rgb(1.0, 0.0, 0.0)
    c2: Color = Color.gray(0.5)
    c3: Color = Color.cmyk(0.0, 1.0, 1.0, 0.0)
    c4: Color = Color.hex("#FF0000")
    c5: Color = Color.black()
    c6: Color = Color.white()
    c7: Color = Color.red()
    c8: Color = Color.green()
    c9: Color = Color.blue()

    r: float = c1.r
    g: float = c1.g
    b: float = c1.b
    gv: float = c2.gray_value
    cc: float = c3.c
    cm: float = c3.m
    cy: float = c3.y
    ck: float = c3.k
    cs: str = c1.color_space
    s: str = repr(c1)


def check_point() -> None:
    p1: Point = Point(1.0, 2.0)
    p2: Point = Point.origin()

    x: float = p1.x
    y: float = p1.y
    eq: bool = p1 == p2
    s: str = repr(p1)


def check_rectangle() -> None:
    r1: Rectangle = Rectangle(Point(0.0, 0.0), Point(100.0, 200.0))
    r2: Rectangle = Rectangle.from_xywh(0.0, 0.0, 100.0, 200.0)

    ll: Point = r1.lower_left
    ur: Point = r1.upper_right
    w: float = r1.width
    h: float = r1.height
    c: Point = r1.center
    s: str = repr(r1)


def check_margins() -> None:
    m1: Margins = Margins(top=10.0, right=20.0, bottom=10.0, left=20.0)
    m2: Margins = Margins.uniform(15.0)
    m3: Margins = Margins()

    t: float = m1.top
    r: float = m1.right
    b: float = m1.bottom
    l: float = m1.left
    s: str = repr(m1)


def check_font() -> None:
    f: Font = Font.HELVETICA
    _: Font = Font.HELVETICA_BOLD
    _2: Font = Font.COURIER
    _3: Font = Font.TIMES_ROMAN
    _4: Font = Font.SYMBOL
    _5: Font = Font.ZAPF_DINGBATS
    s: str = repr(f)


def check_text_align() -> None:
    a: TextAlign = TextAlign.LEFT
    _: TextAlign = TextAlign.RIGHT
    _2: TextAlign = TextAlign.CENTER
    _3: TextAlign = TextAlign.JUSTIFIED
    s: str = repr(a)


def check_page() -> None:
    p: Page = Page(595.0, 842.0)
    p1: Page = Page.a4()
    p2: Page = Page.a4_landscape()
    p3: Page = Page.letter()
    p4: Page = Page.letter_landscape()
    p5: Page = Page.legal()
    p6: Page = Page.legal_landscape()

    w: float = p.width
    h: float = p.height
    m: Margins = p.margins
    p.set_margins(Margins.uniform(25.0))

    # Text operations
    p.set_font(Font.HELVETICA, 12.0)
    p.set_text_color(Color.black())
    p.set_character_spacing(1.0)
    p.set_word_spacing(2.0)
    p.set_leading(14.0)
    p.text_at(100.0, 700.0, "Hello")

    # Graphics operations
    p.set_fill_color(Color.red())
    p.set_stroke_color(Color.blue())
    p.set_line_width(2.0)
    p.set_fill_opacity(0.5)
    p.set_stroke_opacity(0.8)
    p.draw_rect(10.0, 10.0, 100.0, 50.0)
    p.draw_circle(200.0, 200.0, 50.0)
    p.move_to(0.0, 0.0)
    p.line_to(100.0, 100.0)
    p.curve_to(10.0, 20.0, 30.0, 40.0, 50.0, 60.0)
    p.close_path()
    p.fill()
    p.stroke()
    p.fill_and_stroke()

    s: str = repr(p)


def check_document() -> None:
    doc: Document = Document()
    count: int = doc.page_count
    encrypted: bool = doc.is_encrypted

    doc.set_title("Title")
    doc.set_author("Author")
    doc.set_subject("Subject")
    doc.set_keywords("kw1, kw2")
    doc.set_creator("Creator")
    doc.add_page(Page.a4())
    doc.save("/tmp/test.pdf")
    data: bytes = doc.save_to_bytes()
    doc.encrypt("user", "owner")
    doc.encrypt("user", "owner", permissions=Permissions.all())

    s: str = repr(doc)


def check_permissions() -> None:
    p1: Permissions = Permissions()
    p2: Permissions = Permissions(print=True, copy=True)
    p3: Permissions = Permissions.all()
    p4: Permissions = Permissions.none()

    cp: bool = p1.can_print
    cc: bool = p1.can_copy
    cm: bool = p1.can_modify_contents
    ca: bool = p1.can_modify_annotations
    cf: bool = p1.can_fill_forms
    cas: bool = p1.can_assemble
    chq: bool = p1.can_print_high_quality

    s: str = repr(p1)


def check_reader() -> None:
    reader: PdfReader = PdfReader.open("test.pdf")
    enc: bool = reader.is_encrypted
    count: int = reader.page_count
    ver: str = reader.version

    reader.unlock("password")

    from oxidize_pdf import ParsedPage

    page: ParsedPage = reader.get_page(0)
    w: float = page.width
    h: float = page.height
    rot: int = page.rotation
    ps: str = repr(page)

    text: str = reader.extract_text_from_page(0)
    texts: list[str] = reader.extract_text()
    length: int = len(reader)
    rs: str = repr(reader)


def check_operations() -> None:
    paths: list[str] = split_pdf("input.pdf", "/output")
    merge_pdfs(["a.pdf", "b.pdf"], "merged.pdf")
    rotate_pdf("input.pdf", "output.pdf", 90)
    extract_pages("input.pdf", "output.pdf", [0, 1, 2])


def check_exceptions() -> None:
    _: type[Exception] = PdfError
    _2: type[PdfError] = PdfParseError
    _3: type[PdfError] = PdfIoError
    _4: type[PdfError] = PdfEncryptionError
    _5: type[PdfError] = PdfPermissionError
