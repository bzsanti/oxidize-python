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

# Signatures Deep (F75)
from oxidize_pdf._oxidize_pdf import (
    DigestAlgorithm,
    SignatureAlgorithm,
    ByteRange,
    SignatureField,
    TrustStore,
    ParsedSignature,
    HashVerificationResult,
    SignatureVerificationResult,
    CertificateValidationResult,
    FullSignatureValidationResult,
    compute_pdf_hash_py as compute_pdf_hash,
    parse_pkcs7_signature_py as parse_pkcs7_signature,
    verify_pdf_signature_py as verify_pdf_signature,
    validate_pdf_certificate_py as validate_pdf_certificate,
    has_incremental_update_py as has_incremental_update,
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

# Batch/Recovery/Streaming Full (Tier 15 — F62-F64)
from oxidize_pdf._oxidize_pdf import (
    # F62: Batch Processing
    BatchJob,
    JobResult,
    BatchSummary,
    ProgressInfo,
    BatchProcessor,
    batch_split_pdfs,
    batch_merge_pdfs,
    # F63: Recovery Full
    RepairStrategy,
    CorruptionType,
    CorruptionReport,
    RepairResult,
    ScanResult,
    ObjectScanner,
    quick_recover,
    detect_pdf_corruption,
    analyze_pdf_corruption,
    repair_pdf,
    # F64: Streaming Full
    StreamingPage,
    PageStreamer,
    IncrementalParser,
)

# Content Parser (Tier 17 — F77)
from oxidize_pdf._oxidize_pdf import (
    ContentParser,
    ContentOperation,
    TextElement,
    XRefEntry,
    XRefTable,
)

# XMP Metadata (Tier 17 — F78)
from oxidize_pdf._oxidize_pdf import (
    XmpNamespace,
    XmpValue,
    XmpProperty,
    XmpMetadata,
)

# Compliance + Comparison Deep (Tier 18 — F79 + F80)
from oxidize_pdf._oxidize_pdf import (
    # F79: Compliance System
    VerificationLevel,
    ComplianceStats,
    IsoRequirement,
    RequirementInfo,
    ComplianceSystem,
    # F80: PDF Comparison Deep
    DifferenceSeverity,
    PdfDifference,
    ComparisonResult,
    compare_pdfs_deep_py as compare_pdfs_deep,
    extract_pdf_differences_py as extract_pdf_differences,
    pdfs_structurally_equivalent_py as pdfs_structurally_equivalent,
)

# Forms Deep (Tier 16 — F76)
from oxidize_pdf._oxidize_pdf import (
    # Group A: Form Management
    FormData,
    Widget,
    FieldOptions,
    PushButton,
    AcroForm,
    FormManager,
    # Group B: Field Actions
    SpecialFormatType,
    FieldAction,
    FieldActions,
    ActionSettings,
    FieldActionSystem,
    # Group C: Calculations
    SimpleOperation,
    PercentMode,
    SeparatorStyle,
    NegativeStyle,
    SpecialFormat,
    FieldFormat,
    JavaScriptCalculation,
    CalculationSettings,
    CalculationEngine,
    FormCalculationSystem,
    # Group D: Appearance
    AppearanceState,
    AppearanceStream,
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
    # Signatures Deep (F75)
    "DigestAlgorithm",
    "SignatureAlgorithm",
    "ByteRange",
    "SignatureField",
    "TrustStore",
    "ParsedSignature",
    "HashVerificationResult",
    "SignatureVerificationResult",
    "CertificateValidationResult",
    "FullSignatureValidationResult",
    "compute_pdf_hash",
    "parse_pkcs7_signature",
    "verify_pdf_signature",
    "validate_pdf_certificate",
    "has_incremental_update",
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
    # Batch/Recovery/Streaming (Tier 15 — F62-F64)
    # F62
    "BatchJob",
    "JobResult",
    "BatchSummary",
    "ProgressInfo",
    "BatchProcessor",
    "batch_split_pdfs",
    "batch_merge_pdfs",
    # F63
    "RepairStrategy",
    "CorruptionType",
    "CorruptionReport",
    "RepairResult",
    "ScanResult",
    "ObjectScanner",
    "quick_recover",
    "detect_pdf_corruption",
    "analyze_pdf_corruption",
    "repair_pdf",
    # F64
    "StreamingPage",
    "PageStreamer",
    "IncrementalParser",
    # Content Parser (Tier 17 — F77)
    "ContentParser",
    "ContentOperation",
    "TextElement",
    "XRefEntry",
    "XRefTable",
    # XMP Metadata (Tier 17 — F78)
    "XmpNamespace",
    "XmpValue",
    "XmpProperty",
    "XmpMetadata",
    # Forms Deep (Tier 16 — F76)
    # Group A
    "FormData",
    "Widget",
    "FieldOptions",
    "PushButton",
    "AcroForm",
    "FormManager",
    # Group B
    "SpecialFormatType",
    "FieldAction",
    "FieldActions",
    "ActionSettings",
    "FieldActionSystem",
    # Group C
    "SimpleOperation",
    "PercentMode",
    "SeparatorStyle",
    "NegativeStyle",
    "SpecialFormat",
    "FieldFormat",
    "JavaScriptCalculation",
    "CalculationSettings",
    "CalculationEngine",
    "FormCalculationSystem",
    # Group D
    "AppearanceState",
    "AppearanceStream",
    # Compliance + Comparison Deep (Tier 18 — F79 + F80)
    # F79: Compliance System
    "VerificationLevel",
    "ComplianceStats",
    "IsoRequirement",
    "RequirementInfo",
    "ComplianceSystem",
    # F80: PDF Comparison Deep
    "DifferenceSeverity",
    "PdfDifference",
    "ComparisonResult",
    "compare_pdfs_deep",
    "extract_pdf_differences",
    "pdfs_structurally_equivalent",
]
