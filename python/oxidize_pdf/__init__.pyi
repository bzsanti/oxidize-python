"""Type stubs for oxidize-pdf."""

from oxidize_pdf._oxidize_pdf import (
    Color as Color,
    Document as Document,
    Font as Font,
    Margins as Margins,
    Page as Page,
    ParsedPage as ParsedPage,
    PdfEncryptionError as PdfEncryptionError,
    PdfError as PdfError,
    PdfIoError as PdfIoError,
    PdfParseError as PdfParseError,
    PdfPermissionError as PdfPermissionError,
    PdfReader as PdfReader,
    Permissions as Permissions,
    Point as Point,
    Rectangle as Rectangle,
    TextAlign as TextAlign,
    __version__ as __version__,
    extract_pages as extract_pages,
    merge_pdfs as merge_pdfs,
    rotate_pdf as rotate_pdf,
    split_pdf as split_pdf,
)

__all__: list[str]
