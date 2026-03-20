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
    DocumentMetadata,
    ParsedPage,
    ParseOptions,
    PdfReader,
    TextChunk,
    # Feature 28 fix
    verify_pdf_signatures,
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
    # Feature 49: SplitMode
    PageRange,
    SplitMode,
    split_pdf_with_mode,
    # Feature 50: MergeOptions
    MergeOptions,
    merge_pdfs_with_options,
    # Feature 51: RotateOptions
    RotationAngle,
    RotateOptions,
    rotate_pdf_with_options,
    # Feature 52: extract_page_range
    extract_page_range_to_bytes,
    extract_page_range_to_file,
    # Feature 53: PageContentAnalyzer
    PageType,
    ContentAnalysis,
    analyze_page_content,
    analyze_document_content,
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
    # Feature 54: Calibrated Colors
    CalGrayColorSpace,
    CalRgbColorSpace,
    CalibratedColor,
    LabColor,
)

# Annotations (Tier 6)
from oxidize_pdf._oxidize_pdf import (
    Annotation,
    AnnotationType,
    # Feature 55: Rich Annotations
    MarkupType,
    MarkupAnnotation,
    AnnotationIcon,
    TextAnnotation,
    BorderStyleType,
    BorderStyle,
)

# Actions (Tier 6)
from oxidize_pdf._oxidize_pdf import (
    Destination,
    GoToAction,
    JavaScriptAction,
    NamedDestinations,
    ResetFormAction,
    UriAction,
    # Feature 56: Actions Extension
    LaunchAction,
    StandardNamedAction,
    NamedAction,
    SubmitFormAction,
    HideAction,
)

# Forms (Tier 6)
from oxidize_pdf._oxidize_pdf import (
    CheckBox,
    ComboBox,
    ListBox,
    RadioButton,
    TextField,
    # Feature 57: Form Validation
    FieldValue,
    ValidationRule,
    FieldValidator,
    FormValidationSystem,
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

# Viewer Preferences (F44)
from oxidize_pdf._oxidize_pdf import (
    Duplex,
    PageLayout,
    PageMode,
    PrintScaling,
    ViewerPreferences,
)

# Writer Config (F47)
from oxidize_pdf._oxidize_pdf import (
    WriterConfig,
)

# Font Encoding (F48)
from oxidize_pdf._oxidize_pdf import (
    FontEncoding,
)

# Charts (Tier 9 — F58)
from oxidize_pdf._oxidize_pdf import (
    ChartType,
    LegendPosition,
    BarOrientation,
    ChartData,
    BarChart,
    BarChartBuilder,
    DataSeries,
    LineChart,
    LineChartBuilder,
    PieSegment,
    PieChart,
    PieChartBuilder,
    ChartRenderer,
    DashboardBarChart,
    DashboardPieChart,
    DashboardLineChart,
)

# Page Transitions (F60)
from oxidize_pdf._oxidize_pdf import (
    TransitionStyle,
    TransitionDimension,
    TransitionMotion,
    TransitionDirection,
    PageTransition,
)

# Advanced Tables (F61)
from oxidize_pdf._oxidize_pdf import (
    CellAlignment,
    CellBorderStyle,
    CellPadding,
    CellStyle,
    HeaderCell,
    HeaderBuilder,
    AdvColumn,
    AdvancedTable,
    AdvancedTableBuilder,
    AdvTableRenderer,
)

# AI/ML Pipeline (F59)
from oxidize_pdf._oxidize_pdf import (
    DocumentChunk,
    DocumentChunker,
    MarkdownOptions,
    MarkdownExporter,
    ExtractionProfile,
    ReadingOrderStrategy,
    PartitionConfig,
    MergePolicy,
    HybridChunkConfig,
    SemanticChunkConfig,
    Element,
    RagChunk,
)

# Advanced Graphics (Tier 13 — F65-F70)
from oxidize_pdf._oxidize_pdf import (
    # F65: Shadings (enums + types)
    ShadingType,
    ShadingPoint,
    ColorStop,
    AxialShading,
    RadialShading,
    ShadingManager,
    # F66: Patterns
    PaintType,
    TilingType,
    PatternMatrix,
    TilingPattern,
    PatternManager,
    # F67: FormXObject
    FormXObject,
    FormXObjectBuilder,
    FormTemplates,
    FormXObjectManager,
    # F68: ExtGState
    RenderingIntent,
    ExtGState,
    ExtGStateManager,
    # F69: SoftMask + TransparencyGroup
    SoftMaskType,
    SoftMask,
    SoftMaskState,
    TransparencyGroup,
    # F70: Advanced Color Spaces
    IccColorSpace,
    StandardIccProfile,
    IccProfile,
    IccProfileManager,
    SeparationColorSpace,
    SeparationColor,
    SpotColors,
)

# Text Extraction Deep (Tier 14 — F71-F74)
from oxidize_pdf._oxidize_pdf import (
    # F71: ExtractionOptions
    ExtractionOptions,
    # F72: LineBreakMode, PlainTextConfig, PlainTextResult
    LineBreakMode,
    PlainTextConfig,
    PlainTextResult,
    # F73: ColumnLayout, ColumnOptions, ColumnContent
    ColumnLayout,
    ColumnOptions,
    ColumnContent,
    # F74: MatchType, TextMatch, TextValidationResult, TextValidator
    MatchType,
    TextMatch,
    TextValidationResult,
    TextValidator,
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
    "DocumentMetadata",
    "ParsedPage",
    "ParseOptions",
    "PdfReader",
    "TextChunk",
    "verify_pdf_signatures",
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
    # Feature 49
    "PageRange",
    "SplitMode",
    "split_pdf_with_mode",
    # Feature 50
    "MergeOptions",
    "merge_pdfs_with_options",
    # Feature 51
    "RotationAngle",
    "RotateOptions",
    "rotate_pdf_with_options",
    # Feature 52
    "extract_page_range_to_bytes",
    "extract_page_range_to_file",
    # Feature 53
    "PageType",
    "ContentAnalysis",
    "analyze_page_content",
    "analyze_document_content",
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
    # Feature 54
    "CalGrayColorSpace",
    "CalRgbColorSpace",
    "CalibratedColor",
    "LabColor",
    # Annotations
    "Annotation",
    "AnnotationType",
    # Feature 55
    "MarkupType",
    "MarkupAnnotation",
    "AnnotationIcon",
    "TextAnnotation",
    "BorderStyleType",
    "BorderStyle",
    # Actions
    "Destination",
    "GoToAction",
    "JavaScriptAction",
    "NamedDestinations",
    "ResetFormAction",
    "UriAction",
    # Feature 56
    "LaunchAction",
    "StandardNamedAction",
    "NamedAction",
    "SubmitFormAction",
    "HideAction",
    # Forms
    "CheckBox",
    "ComboBox",
    "ListBox",
    "RadioButton",
    "TextField",
    # Feature 57
    "FieldValue",
    "ValidationRule",
    "FieldValidator",
    "FormValidationSystem",
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
    # Viewer Preferences (F44)
    "Duplex",
    "PageLayout",
    "PageMode",
    "PrintScaling",
    "ViewerPreferences",
    # Writer Config (F47)
    "WriterConfig",
    # Font Encoding (F48)
    "FontEncoding",
    # Charts (F58)
    "ChartType",
    "LegendPosition",
    "BarOrientation",
    "ChartData",
    "BarChart",
    "BarChartBuilder",
    "DataSeries",
    "LineChart",
    "LineChartBuilder",
    "PieSegment",
    "PieChart",
    "PieChartBuilder",
    "ChartRenderer",
    "DashboardBarChart",
    "DashboardPieChart",
    "DashboardLineChart",
    # Page Transitions (F60)
    "TransitionStyle",
    "TransitionDimension",
    "TransitionMotion",
    "TransitionDirection",
    "PageTransition",
    # Advanced Tables (F61)
    "CellAlignment",
    "CellBorderStyle",
    "CellPadding",
    "CellStyle",
    "HeaderCell",
    "HeaderBuilder",
    "AdvColumn",
    "AdvancedTable",
    "AdvancedTableBuilder",
    "AdvTableRenderer",
    # AI/ML Pipeline (F59)
    "DocumentChunk",
    "DocumentChunker",
    "MarkdownOptions",
    "MarkdownExporter",
    "ExtractionProfile",
    "ReadingOrderStrategy",
    "PartitionConfig",
    "MergePolicy",
    "HybridChunkConfig",
    "SemanticChunkConfig",
    "Element",
    "RagChunk",
    # Advanced Graphics (Tier 13 — F65-F70)
    # F65: Shadings
    "ShadingType",
    "ShadingPoint",
    "ColorStop",
    "AxialShading",
    "RadialShading",
    "ShadingManager",
    # F66: Patterns
    "PaintType",
    "TilingType",
    "PatternMatrix",
    "TilingPattern",
    "PatternManager",
    # F67: FormXObject
    "FormXObject",
    "FormXObjectBuilder",
    "FormTemplates",
    "FormXObjectManager",
    # F68: ExtGState
    "RenderingIntent",
    "ExtGState",
    "ExtGStateManager",
    # F69: SoftMask + TransparencyGroup
    "SoftMaskType",
    "SoftMask",
    "SoftMaskState",
    "TransparencyGroup",
    # F70: Advanced Color Spaces
    "IccColorSpace",
    "StandardIccProfile",
    "IccProfile",
    "IccProfileManager",
    "SeparationColorSpace",
    "SeparationColor",
    "SpotColors",
    # Text Extraction Deep (Tier 14 — F71-F74)
    # F71
    "ExtractionOptions",
    # F72
    "LineBreakMode",
    "PlainTextConfig",
    "PlainTextResult",
    # F73
    "ColumnLayout",
    "ColumnOptions",
    "ColumnContent",
    # F74
    "MatchType",
    "TextMatch",
    "TextValidationResult",
    "TextValidator",
]
