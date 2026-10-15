"""Issue #265: concrete public results and discriminating invalid uses.

Unused ignores are errors under --strict: each negative control must continue
producing its specified error. --disallow-any-expr rejects erased result types.
"""
from oxidize_pdf import (
    Annotation, AnnotationType, AxialShading, ByteRange, Color, ColorStop,
    DigestAlgorithm, Document, Element, EncryptionStrength, FieldValue,
    HashVerificationResult, Image, LazyDocument, Page, PageStreamer, PdfReader,
    merge_pdfs_to_bytes, split_pdf_to_bytes, extract_pages_to_bytes, rotate_pdf_to_bytes,
    PlainTextConfig, PlainTextResult, Rectangle, ShadingPoint, StreamingOptions,
    StreamingPage, compute_pdf_hash,
)


def reproduce(reader: PdfReader) -> tuple[list[Element], str]:
    elements: list[Element] = reader.partition()
    contextual: str = reader.to_contextual()
    reader.partition("invalid")  # type: ignore[call-arg]
    reader.to_contextual(123)  # type: ignore[call-arg]
    invalid_elements: list[str] = reader.partition()  # type: ignore[assignment]
    invalid_context: bytes = reader.to_contextual()  # type: ignore[assignment]
    reader.partition_with("invalid")  # type: ignore[arg-type]
    return elements, contextual


def streaming(path: str) -> tuple[int, list[str]]:
    lazy: LazyDocument = LazyDocument.open(path)
    options: StreamingOptions = StreamingOptions.minimal_memory()
    options = StreamingOptions.fast_processing()
    texts: list[str] = []
    with PageStreamer.open(path) as stream:
        page: StreamingPage | None = stream.next()
        if page is not None:
            texts.append(page.extract_text_streaming())
            invalid: bytes = page.extract_text_streaming()  # type: ignore[assignment]
        stream.next(1)  # type: ignore[call-arg]
        stream.seek_to_page("one")  # type: ignore[arg-type]
    LazyDocument.open(42)  # type: ignore[arg-type]
    return lazy.page_count, texts


def other_public_apis(reader: PdfReader, data: bytes) -> None:
    result: PlainTextResult = reader.extract_plain_text(0, PlainTextConfig())
    lines: list[str] = reader.extract_plain_text_lines(0)
    signatures: list[dict[str, str | None]] = reader.detect_signatures()
    document = Document()
    document.encrypt("user", "owner", strength=EncryptionStrength.RC4_128)
    document.set_producer("typed consumer")
    page = Page.a4()
    page.add_image("sample", Image.from_png_data(data))
    page.add_image("sample", data)  # type: ignore[arg-type]
    image_width: int = Image.from_png_data(data).width
    field: FieldValue = FieldValue.text(s="hello")
    annotation: Annotation = Annotation(AnnotationType.TEXT, Rectangle.from_xywh(0, 0, 10, 10))
    shade = AxialShading("gradient", ShadingPoint(0, 0), ShadingPoint(10, 10),
                        [ColorStop(0, Color.black()), ColorStop(1, Color.white())])
    shade.validate()
    hashed: HashVerificationResult = compute_pdf_hash(data, ByteRange([(0, 1), (2, 3)]), DigestAlgorithm.SHA256)
    compute_pdf_hash("invalid", ByteRange([(0, 1), (2, 3)]), DigestAlgorithm.SHA256)  # type: ignore[arg-type]


def binary_results(path: str) -> list[bytes]:
    merged: bytes = merge_pdfs_to_bytes([path])
    extracted: bytes = extract_pages_to_bytes(path, [0])
    rotated: bytes = rotate_pdf_to_bytes(path, 90)
    pages: list[bytes] = split_pdf_to_bytes(path)
    invalid: list[int] = merge_pdfs_to_bytes([path])  # type: ignore[assignment]
    return [merged, extracted, rotated, *pages]
