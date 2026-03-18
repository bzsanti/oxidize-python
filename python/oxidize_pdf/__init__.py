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
    HeaderFooter,
    HeaderFooterOptions,
    TextAlign,
    TextRenderingMode,
    measure_text,
    measure_char,
)

# Lists
from oxidize_pdf._oxidize_pdf import (
    BulletStyle,
    OrderedList,
    OrderedListStyle,
    UnorderedList,
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
    # Feature 6
    reorder_pdf_pages,
    swap_pdf_pages,
    move_pdf_page,
    reverse_pdf_pages,
    # Feature 7
    OverlayPosition,
    OverlayOptions,
    overlay_pdf,
    # Feature 8
    ExtractImagesOptions,
    extract_images_from_pdf,
    # Feature 10
    merge_pdfs_to_bytes,
    rotate_pdf_to_bytes,
    extract_pages_to_bytes,
    split_pdf_to_bytes,
)

# Image
from oxidize_pdf._oxidize_pdf import (
    Image,
)

# Tables
from oxidize_pdf._oxidize_pdf import (
    GridStyle,
    HeaderStyle,
    Table,
    TableCell,
    TableOptions,
    TableStyle,
)

# Graphics (Tier 3)
from oxidize_pdf._oxidize_pdf import (
    BlendMode,
    ClippingPath,
    LineCap,
    LineDashPattern,
    LineJoin,
)

# Annotations (Tier 6)
from oxidize_pdf._oxidize_pdf import (
    Annotation,
    AnnotationType,
)

# Actions (Tier 6)
from oxidize_pdf._oxidize_pdf import (
    Destination,
    GoToAction,
    JavaScriptAction,
    ResetFormAction,
    UriAction,
)

# Forms (Tier 6)
from oxidize_pdf._oxidize_pdf import (
    CheckBox,
    ComboBox,
    ListBox,
    RadioButton,
    TextField,
)

# Outlines (Tier 6)
from oxidize_pdf._oxidize_pdf import (
    OutlineItem,
    OutlineTree,
)

# Page Labels (Tier 6)
from oxidize_pdf._oxidize_pdf import (
    PageLabel,
    PageLabelStyle,
    PageLabelTree,
)

# Tier 8 — Enterprise
from oxidize_pdf._oxidize_pdf import (
    # Feature 30: Tagged PDF
    StandardStructureType,
    StructTree,
    StructureElement,
    # Feature 31: Coordinate Systems
    CoordinateSystem,
    # Feature 32: Calibrated Colors
    LabColorSpace,
    # Feature 33: Templates
    TemplateContext,
    TemplateRenderer,
    # Feature 34: OCR
    MockOcrProvider,
    OcrEngine,
    # Feature 35: Batch Processing
    BatchOptions,
    # Feature 36: Streaming/Lazy
    LazyDocument,
    StreamingOptions,
    # Feature 37: PDF Recovery
    validate_pdf,
    # Feature 38: PDF/A Validation
    PdfALevel,
    PdfAValidator,
    # Feature 39: PDF Comparison
    compare_pdfs,
    # Feature 40: Semantic Marking
    EntityType,
    # Feature 41: Dashboards
    DashboardBuilder,
    DashboardTheme,
    KpiCard,
)

# Security
from oxidize_pdf._oxidize_pdf import (
    EncryptionStrength,
    Permissions,
    Recipient,
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
    "HeaderFooter",
    "HeaderFooterOptions",
    "TextAlign",
    "TextRenderingMode",
    "measure_text",
    "measure_char",
    # Lists
    "BulletStyle",
    "OrderedList",
    "OrderedListStyle",
    "UnorderedList",
    # Parser
    "PdfReader",
    # Operations
    "split_pdf",
    "merge_pdfs",
    "rotate_pdf",
    "extract_pages",
    "reorder_pdf_pages",
    "swap_pdf_pages",
    "move_pdf_page",
    "reverse_pdf_pages",
    "OverlayPosition",
    "OverlayOptions",
    "overlay_pdf",
    "ExtractImagesOptions",
    "extract_images_from_pdf",
    "merge_pdfs_to_bytes",
    "rotate_pdf_to_bytes",
    "extract_pages_to_bytes",
    "split_pdf_to_bytes",
    # Image
    "Image",
    # Tables
    "GridStyle",
    "HeaderStyle",
    "Table",
    "TableCell",
    "TableOptions",
    "TableStyle",
    # Graphics (Tier 3)
    "BlendMode",
    "ClippingPath",
    "LineCap",
    "LineDashPattern",
    "LineJoin",
    # Annotations
    "Annotation",
    "AnnotationType",
    # Actions
    "Destination",
    "GoToAction",
    "JavaScriptAction",
    "ResetFormAction",
    "UriAction",
    # Forms
    "CheckBox",
    "ComboBox",
    "ListBox",
    "RadioButton",
    "TextField",
    # Outlines
    "OutlineItem",
    "OutlineTree",
    # Page Labels
    "PageLabel",
    "PageLabelStyle",
    "PageLabelTree",
    # Tier 8
    "StandardStructureType",
    "StructTree",
    "StructureElement",
    "CoordinateSystem",
    "LabColorSpace",
    "TemplateContext",
    "TemplateRenderer",
    "MockOcrProvider",
    "OcrEngine",
    "BatchOptions",
    "LazyDocument",
    "StreamingOptions",
    "validate_pdf",
    "PdfALevel",
    "PdfAValidator",
    "compare_pdfs",
    "EntityType",
    "DashboardBuilder",
    "DashboardTheme",
    "KpiCard",
    # Security
    "EncryptionStrength",
    "Permissions",
    "Recipient",
]
