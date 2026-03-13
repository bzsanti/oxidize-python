"""oxidize-pdf: Python bindings for the oxidize-pdf Rust library."""

from oxidize_pdf._oxidize_pdf import __version__

# Errors
from oxidize_pdf._oxidize_pdf import (
    PdfError,
    PdfEncryptionError,
    PdfIoError,
    PdfParseError,
    PdfPermissionError,
)

# Types
from oxidize_pdf._oxidize_pdf import (
    Color,
    Margins,
    Point,
    Rectangle,
)

# Document & Page
from oxidize_pdf._oxidize_pdf import (
    Document,
    Page,
)

# Text
from oxidize_pdf._oxidize_pdf import (
    Font,
    TextAlign,
)

# Parser
from oxidize_pdf._oxidize_pdf import (
    PdfReader,
)

# Operations
from oxidize_pdf._oxidize_pdf import (
    split_pdf,
    merge_pdfs,
    rotate_pdf,
    extract_pages,
)

# Security
from oxidize_pdf._oxidize_pdf import (
    Permissions,
)

__all__ = [
    "__version__",
    # Errors
    "PdfError",
    "PdfEncryptionError",
    "PdfIoError",
    "PdfParseError",
    "PdfPermissionError",
    # Types
    "Color",
    "Margins",
    "Point",
    "Rectangle",
    # Document & Page
    "Document",
    "Page",
    # Text
    "Font",
    "TextAlign",
    # Parser
    "PdfReader",
    # Operations
    "split_pdf",
    "merge_pdfs",
    "rotate_pdf",
    "extract_pages",
    # Security
    "Permissions",
]
