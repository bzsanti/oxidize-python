# TDD Plan — oxidize-python Feature Parity

**Última actualización**: 2026-03-21
**Estado**: ~89/113 features completadas (79%)
**Tests**: 1554 pasando, 0 warnings
**Tiers 0-19 completados**: incluye Charts, Tables, Transitions, AI/ML, Graphics Adv, Text Extract, Batch/Recovery/Streaming, Forms Deep, Signatures Deep, ContentParser, XMP Metadata
**Core**: oxidize-pdf v2.3.2 (features: compression, signatures)

**Nota sobre métricas**: El plan anterior reportaba 57/64 (89%). Eso medía features de alto nivel.
Tras gap analysis profundo contra la API completa del core (674 structs, 243 enums, 31 módulos),
se identificaron **49 features adicionales** no contempladas. La cobertura real de la superficie
de API es ~18% de structs y ~16% de enums. Este plan actualizado refleja el gap completo.

---

## Features Completadas (57)

### Tier 0 — Fixes Críticos
- [x] F3 fix: Page.set_header() / set_footer()
- [x] F22 fix: Document.enable_forms() + add_text_field/checkbox/combo_box/list_box/radio_button
- [x] F25 fix: NamedDestinations + Document.set_named_destinations()

### Tier 1 — Alto Impacto
- [x] F1: Image embedding (Image, Page.add_image/draw_image)
- [x] F2: Tables (Table, TableOptions, TableCell, TableStyle)
- [x] F3: Headers/Footers (HeaderFooter, HeaderFooterOptions)
- [x] F4: Lists (OrderedList, UnorderedList, BulletStyle)
- [x] F5: Text measurement (measure_text, measure_char)

### Tier 1.5 — Parser Fundamentals
- [x] F42: ParseOptions (strict/tolerant/lenient/skip_errors + custom)
- [x] F43: DocumentMetadata + PdfReader.metadata()

### Tier 2 — Document Operations
- [x] F6: reorder/swap/move/reverse_pdf_pages
- [x] F7: OverlayPosition + OverlayOptions + overlay_pdf
- [x] F8: ExtractImagesOptions + extract_images_from_pdf
- [x] F9: Page rotation (getter/setter)
- [x] F10: merge/rotate/extract/split _to_bytes

### Tier 2 — Operations Additions
- [x] F49: PageRange + SplitMode + split_pdf_with_mode
- [x] F50: MergeOptions + merge_pdfs_with_options
- [x] F51: RotationAngle + RotateOptions + rotate_pdf_with_options
- [x] F52: extract_page_range_to_bytes/to_file
- [x] F53: PageType + ContentAnalysis + analyze_page/document_content

### Tier 2.5 — Document Configuration
- [x] F44: ViewerPreferences (PageLayout, PageMode, PrintScaling, Duplex, 4 presets)
- [x] F45: Document.set_open_action_goto/uri (with is_map param)
- [x] F46: Document.add_font/add_font_from_bytes/has_custom_font/custom_font_names
- [x] F47: WriterConfig (modern/legacy/incremental + custom kwargs) + set_compress + enable_xref_streams
- [x] F48: FontEncoding + Document.set_default_font_encoding

### Tier 3 — Graphics
- [x] F11: LineCap + LineJoin + set_miter_limit
- [x] F12: LineDashPattern + set_dash_pattern
- [x] F13: save/restore_graphics_state
- [x] F14: ClippingPath + set_clipping_path/clear_clipping
- [x] F15: BlendMode + set_blend_mode
- [x] F54: CalGrayColorSpace, CalRgbColorSpace, CalibratedColor, LabColor + 4 Page methods

### Tier 4-5 — Text + Metadata
- [x] F16: set_horizontal_scaling
- [x] F17: set_text_rise
- [x] F18: TextRenderingMode + set_rendering_mode
- [x] F19: Document.set_producer
- [x] F20: Document.set_creation_date/set_modification_date

### Tier 6 — Annotations, Forms, Actions
- [x] F21: AnnotationType (17 types) + Annotation
- [x] F22: TextField, CheckBox, RadioButton, ComboBox, ListBox
- [x] F23: UriAction, GoToAction, JavaScriptAction, ResetFormAction
- [x] F24: OutlineItem + OutlineTree + Document.set_outline
- [x] F25: Destination (fit/xyz/fit_h/fit_v/fit_b)
- [x] F26: PageLabel + PageLabelTree + Document.set_page_labels
- [x] F55: MarkupAnnotation, TextAnnotation, AnnotationIcon, BorderStyle
- [x] F56: LaunchAction, StandardNamedAction, NamedAction, SubmitFormAction, HideAction
- [x] F57: FieldValue, ValidationRule, FieldValidator, FormValidationSystem

### Tier 7 — Security
- [x] F27: EncryptionStrength + Document.encrypt with strength param
- [x] F28: detect_signatures + verify_pdf_signatures (standalone function)
- [x] F29: Recipient.from_certificate

### Tier 8 — Enterprise (Parcial)
- [x] F30: StandardStructureType + StructureElement + StructTree
- [x] F31: CoordinateSystem + Page.set_coordinate_system
- [x] F32: LabColorSpace (d50/d65)
- [x] F33: TemplateContext + TemplateRenderer
- [x] F34: OcrEngine + MockOcrProvider
- [x] F35: BatchOptions (solo constructor, sin BatchProcessor)
- [x] F36: StreamingOptions + LazyDocument (solo open + page_count)
- [x] F37: validate_pdf (solo is_valid/error_count/warning_count)
- [x] F38: PdfALevel + PdfAValidator (solo constructor)
- [x] F39: compare_pdfs (solo similarity_score/difference_count)
- [x] F40: EntityType (**STUB** — sin implementación real, solo `_private: ()`)
- [x] F41: DashboardBuilder + DashboardTheme + KpiCard (solo constructors)

---

## Features Pendientes (56) — Organizadas por Tier

### Tier 9 — Charts & Visualización (F58, ~15 ciclos TDD) ✅ COMPLETADO

APIs confirmadas en core: módulo `charts` completo. **129 tests.**

- [x] F58a: ChartData + ChartType + LegendPosition
  - Enums: `ChartType` (VerticalBar, HorizontalBar, Pie, Line, Area), `LegendPosition` (None, Right, Bottom, Top, Left)
  - Struct: `ChartData` (label, value, color, highlighted)
  - ~2 ciclos TDD

- [x] F58b: BarChart + BarChartBuilder
  - Enum: `BarOrientation` (Vertical, Horizontal)
  - Struct: `BarChart` con 20 campos configurables
  - Builder: `BarChartBuilder` con 22 métodos (title, data, orientation, colors, fonts, spacing, styles presets: financial_style, minimal_style, progress_style)
  - ~3 ciclos TDD

- [x] F58c: LineChart + LineChartBuilder + DataSeries
  - Struct: `DataSeries` (name, data points, color, line_width, markers, fill_area)
  - Struct: `LineChart` con ejes, series, grid, ranges
  - Builder: `LineChartBuilder` con 14 métodos
  - ~3 ciclos TDD

- [x] F58d: PieChart + PieChartBuilder + PieSegment
  - Struct: `PieSegment` (label, value, color, exploded, percentage)
  - Struct: `PieChart` con segmentos, labels, borders, start_angle
  - Builder: `PieChartBuilder` con 21 métodos (incluye donut_style)
  - ~3 ciclos TDD

- [x] F58e: ChartRenderer + ChartExt (Page integration)
  - Struct: `ChartRenderer` (margin, grid_opacity, coordinate_system)
  - Métodos: render_chart, render_bar_chart, render_pie_chart, render_line_chart
  - Page extension: `Page.add_chart()`, `Page.add_bar_chart()`, `Page.add_pie_chart()`, `Page.add_line_chart()`
  - Dashboard integration: `DashboardBarChart`, `DashboardPieChart`, `DashboardLineChart`
  - ~4 ciclos TDD

### Tier 10 — Advanced Tables (F61, ~12 ciclos TDD) ✅ COMPLETADO

APIs confirmadas en core: módulo `advanced_tables` completo. **82 tests.**
Nota: CellData, RowData, ZebraConfig no re-exportados en crate 2.3.2 — omitidos.

- [x] F61a: CellStyle + CellAlignment + Padding
  - Enum: `CellAlignment` (Left, Center, Right, Justify)
  - Struct: `Padding` (top, right, bottom, left) + uniform/symmetric constructors
  - Struct: `CellStyle` con 12 campos + builders (header, data, numeric, alternating presets)
  - ~2 ciclos TDD

- [x] F61b: BorderEdge + BorderConfiguration + BorderStyle (advanced)
  - Enum: `BorderStyle` (None, Solid, Dashed, Dotted, Double)
  - Struct: `BorderEdge` (style, width, color) + solid/dashed/dotted/none factories
  - Struct: `BorderConfiguration` (top, right, bottom, left) + uniform/edges/none factories
  - ~2 ciclos TDD

- [x] F61c: HeaderCell + HeaderBuilder
  - Struct: `HeaderCell` (text, colspan, rowspan, style, start_col, row_level)
  - Struct: `HeaderBuilder` con multi-level headers, add_group, add_complex_header
  - Presets: financial_report, product_comparison
  - ~3 ciclos TDD

- [x] F61d: CellData + RowData + Column + ZebraConfig
  - Struct: `CellData` (content, style, colspan, rowspan)
  - Struct: `RowData` (from_strings, from_cells, min_height)
  - Struct: `Column` (header, width, style, auto_resize)
  - Struct: `ZebraConfig` (odd/even colors)
  - ~2 ciclos TDD

- [x] F61e: AdvancedTable + AdvancedTableBuilder + TableRenderer + AdvancedTableExt
  - Struct: `AdvancedTable` con title, columns, rows, header, zebra, borders, cell_styles
  - Builder: `AdvancedTableBuilder` con 28+ métodos (incluye financial_table, minimal_table presets)
  - Struct: `TableRenderer` (calculate_height, render_table)
  - Trait: `AdvancedTableExt` → Page.add_advanced_table(table, x, y), Page.add_advanced_table_auto(table)
  - Enum: `TableError` (7 variantes: NoColumns, ColumnMismatch, HeaderOverlap, etc.)
  - ~3 ciclos TDD

### Tier 11 — Page Transitions (F60, ~4 ciclos TDD) ✅ COMPLETADO

APIs confirmadas en core: módulo `page_transitions` completo. **63 tests.**

- [x] F60a: TransitionStyle + TransitionDimension + TransitionMotion + TransitionDirection
  - Enum: `TransitionStyle` (12 variantes: Split, Blinds, Box, Wipe, Dissolve, Glitter, Replace, Fly, Push, Cover, Uncover, Fade)
  - Enum: `TransitionDimension` (Horizontal, Vertical)
  - Enum: `TransitionMotion` (Inward, Outward)
  - Enum: `TransitionDirection` (LeftToRight, BottomToTop, RightToLeft, TopToBottom, TopLeftToBottomRight, Custom)
  - ~1 ciclo TDD

- [x] F60b: PageTransition + Page integration
  - Struct: `PageTransition` (style, duration, dimension, motion, direction, scale, area)
  - Builder: with_duration, with_dimension, with_motion, with_direction, with_scale, with_area
  - 11 convenience constructors: split, blinds, box_transition, wipe, dissolve, glitter, replace, fly, push, cover, uncover, fade
  - Page integration: Page.set_transition(transition)
  - ~3 ciclos TDD

### Tier 12 — AI/ML & Pipeline (F59, ~14 ciclos TDD) ✅ COMPLETADO

APIs confirmadas en core: módulos `ai` + `pipeline` completos. **77 tests.**
PdfReader métodos: to_markdown, to_contextual, chunk, partition, rag_chunks, rag_chunks_with_profile.

- [x] F59a: DocumentChunker + DocumentChunk + ChunkMetadata + ChunkPosition
  - Struct: `DocumentChunker` (chunk_size, overlap) + new/default
  - Métodos: chunk_document, chunk_text, chunk_text_with_pages, estimate_tokens
  - Struct: `DocumentChunk` (id, content, tokens, page_numbers, chunk_index, metadata)
  - Struct: `ChunkMetadata` (position, confidence, sentence_boundary_respected)
  - Struct: `ChunkPosition` (start_char, end_char, first_page, last_page)
  - ~3 ciclos TDD

- [x] F59b: MarkdownExporter + MarkdownOptions + ContextualFormat
  - Struct: `MarkdownOptions` (include_metadata, include_page_numbers)
  - Struct: `MarkdownExporter` (export, export_text, export_with_metadata, export_with_pages)
  - Struct: `ContextualFormat` (export_simple, export_with_metadata, export_with_pages)
  - Funciones PdfReader: to_markdown(), to_contextual()
  - ~2 ciclos TDD

- [x] F59c: Partitioner + PartitionConfig + Element + ExtractionProfile
  - Enum: `Element` (Title, Paragraph, Table, Header, Footer, ListItem, Image, CodeBlock, KeyValue) con 12 métodos
  - Struct: `PartitionConfig` (detect_tables, detect_headers_footers, title_min_font_ratio, reading_order)
  - Struct: `Partitioner` (partition_fragments)
  - Enum: `ExtractionProfile` (Standard, Academic, Form, Government, Dense, Presentation, Rag)
  - Enum: `ReadingOrderStrategy` (Simple, XYCut, None)
  - ~3 ciclos TDD

- [x] F59d: HybridChunker + SemanticChunker + ElementGraph
  - Struct: `HybridChunkConfig` (max_tokens, overlap_tokens, merge_adjacent, propagate_headings, merge_policy)
  - Struct: `HybridChunker` (chunk, chunk_with_graph)
  - Struct: `HybridChunk` (elements, heading_context, text, full_text, token_estimate, is_oversized)
  - Struct: `SemanticChunkConfig` (max_tokens, overlap_tokens, respect_element_boundaries)
  - Struct: `SemanticChunker` (chunk)
  - Struct: `SemanticChunk` (elements, text, token_estimate, page_numbers, is_oversized)
  - Struct: `ElementGraph` (build, parent_of, children_of, next_of, prev_of, elements_in_section, top_level_sections)
  - Enum: `MergePolicy` (SameTypeOnly, AnyInlineContent)
  - ~3 ciclos TDD

- [x] F59e: RagChunk + ElementMarkdownExporter + ExportConfig
  - Struct: `RagChunk` (chunk_index, text, full_text, page_numbers, bounding_boxes, element_types, heading_context, token_estimate, is_oversized)
  - Struct: `ExportConfig` (include_headers_footers)
  - Struct: `ElementMarkdownExporter` (export)
  - Struct: `ElementBBox` (x, y, width, height, right, top)
  - Struct: `ElementMetadata` (page, bbox, confidence, font_name, font_size, is_bold, is_italic, parent_heading)
  - PdfReader integration: rag_chunks(), rag_chunks_with_profile()
  - ~3 ciclos TDD

### Tier 13 — Graphics Avanzado (F65-F70, ~20 ciclos TDD) ✅ COMPLETADO

APIs confirmadas en core: submódulos de `graphics`. **125 tests.**

- [x] F65: Shadings (gradientes)
  - Struct: `ColorStop` (position, color)
  - Struct: `AxialShading` (linear gradient) + linear_gradient factory + with_extend
  - Struct: `RadialShading` (radial gradient) + radial_gradient factory + with_extend
  - Enum: `ShadingDefinition` (Axial, Radial, FunctionBased)
  - Struct: `ShadingManager` (add_shading, create_linear_gradient, create_radial_gradient)
  - Page integration: draw con shading fill
  - ~4 ciclos TDD

- [x] F66: Patterns (tiling)
  - Enum: `PaintType` (Colored, Uncolored), `TilingType` (3 variantes)
  - Struct: `PatternMatrix` (identity, translation, scale, rotation, multiply)
  - Struct: `TilingPattern` (add_rectangle, add_line, add_circle, stroke, fill)
  - Struct: `PatternManager` (add_pattern, create_checkerboard_pattern, create_stripe_pattern, create_dots_pattern)
  - Trait: `PatternGraphicsContext` → Page.set_fill_pattern, Page.set_stroke_pattern
  - ~4 ciclos TDD

- [x] F67: FormXObject (reusable content)
  - Struct: `FormXObject` (bbox, matrix, resources, content, transparency_group)
  - Builder: `FormXObjectBuilder` (15 métodos: rectangle, move_to, line_to, fill_color, stroke_color, etc.)
  - Struct: `FormTemplates` (checkmark, cross, circle, star, logo_placeholder) — factories estáticas
  - Struct: `FormXObjectManager` (add_form, get_form, remove_form)
  - Page integration existente: Page.add_form_xobject
  - ~3 ciclos TDD

- [x] F68: ExtGState (graphics state parameters)
  - Struct: `ExtGState` con 27 campos opcionales (line_width, line_cap, blend_mode, alpha, soft_mask, halftone, transfer_function, etc.)
  - 25+ métodos builder: with_line_width, with_blend_mode, with_alpha, with_gamma_correction, etc.
  - Struct: `ExtGStateManager` (add_state, get_state, to_resource_dictionary)
  - Enum: `RenderingIntent` (4 variantes)
  - Nota: ExtGState es el mecanismo subyacente para muchas features ya expuestas (blend_mode, opacity). Este feature expone el control granular completo.
  - ~3 ciclos TDD

- [x] F69: SoftMask + TransparencyGroup
  - Struct: `SoftMask` (alpha, luminosity, with_background_color, with_bbox)
  - Struct: `SoftMaskState` (set_mask, push_mask, pop_mask)
  - Struct: `TransparencyGroup` (isolated, knockout, blend_mode, opacity, color_space)
  - Enum: `SoftMaskType` (Alpha, Luminosity)
  - ~3 ciclos TDD

- [x] F70: Advanced Color Spaces (ICC, Separation, DeviceN, Indexed)
  - Struct: `IccProfile` (from_standard, validate) + `IccProfileManager` + `StandardIccProfile` enum (7 perfiles)
  - Struct: `SeparationColorSpace` (rgb_separation, cmyk_separation) + `SeparationColor` + `SpotColors` (Pantone presets)
  - Struct: `DeviceNColorSpace` (cmyk_plus_spots) + `ColorantDefinition` + `DeviceNAttributes`
  - Struct: `IndexedColorSpace` (from_palette, web_safe_palette, grayscale_palette) + `IndexedColorManager`
  - Enum: `IccColorSpace` (Rgb, Cmyk, Lab, Gray)
  - ~3 ciclos TDD

### Tier 14 — Text Extraction & Analysis (F71-F74, ~10 ciclos TDD) ✅ COMPLETADO

APIs confirmadas en core: submódulos de `text`. **66 tests.**

- [x] F71: TextExtractor + ExtractionOptions
  - Struct: `TextExtractor` (extract_from_document, extract_from_page)
  - Struct: `ExtractionOptions` (preserve_layout, space_threshold, detect_columns, merge_hyphenated, sort_by_position)
  - Integración: PdfReader.extract_text_advanced(options)
  - ~2 ciclos TDD

- [x] F72: PlainTextExtractor + PlainTextConfig
  - Struct: `PlainTextExtractor` (extract, extract_lines)
  - Struct: `PlainTextConfig` (space_threshold, newline_threshold, preserve_layout, line_break_mode)
  - Presets: dense(), loose(), preserve_layout()
  - Enum: `LineBreakMode` (Auto, PreserveAll, Normalize)
  - Struct: `PlainTextResult` (text, line_count, char_count)
  - ~2 ciclos TDD

- [x] F73: ColumnLayout
  - Struct: `ColumnLayout` (new, with_custom_widths, column_count, column_width, column_x_position)
  - Struct: `ColumnOptions` (font, font_size, line_height, text_color, text_align, balance_columns, show_separators)
  - Struct: `ColumnContent` (text, formatting)
  - Integración: Page.render_columns(layout, content, x, y, height)
  - ~3 ciclos TDD

- [x] F74: TextValidator + InvoiceExtractor + StructuredDataDetector
  - Struct: `TextValidator` (search_for_target, validate_contract_text)
  - Struct: `TextValidationResult` (found, matches, confidence)
  - Struct: `InvoiceExtractor` (builder pattern, extract from text_fragments)
  - Struct: `StructuredDataDetector` (detect from fragments)
  - Enum: `MatchType` (Date, ContractNumber, PartyName, MonetaryAmount, Location, Custom)
  - Enum: `Language` (Spanish, English, German, Italian)
  - ~3 ciclos TDD

### Tier 15 — Batch, Recovery, Streaming Full (F62-F64, ~15 ciclos TDD) ✅ COMPLETADO

APIs confirmadas en core. **58 tests.**

- [x] F62: Batch Processing Full
  - Struct: `BatchProcessor` (add_job, add_jobs, execute, cancel, get_progress)
  - Enum: `BatchJob` (Custom, Split, Merge, Rotate, Extract, Compress)
  - Enum: `JobResult` (Success, Failed, Cancelled)
  - Struct: `BatchSummary` (total_jobs, successful, failed, duration, results)
  - Struct: `BatchProgress` (add_job, start_job, complete_job, get_info)
  - Struct: `ProgressInfo` (percentage, is_complete, elapsed, format_progress)
  - Funciones: batch_process_files, batch_split_pdfs, batch_merge_pdfs
  - **Nota FFI**: BatchJob::Custom usa `Box<dyn Fn()>` — requiere wrapper para Python callbacks. progress_callback usa `Arc<dyn ProgressCallback>` — requiere adapter.
  - ~5 ciclos TDD

- [x] F63: Recovery Full
  - Struct: `PdfRecovery` (recover_document, recover_partial, warnings)
  - Struct: `RecoveryOptions` (aggressive_recovery, partial_content, max_errors, rebuild_xref, memory_limit)
  - Struct: `PartialRecovery` (recovered_pages, total_objects, recovered_objects)
  - Struct: `RecoveredPage` (page_number, content, has_text, has_images)
  - Struct: `ObjectScanner` (scan_file → ScanResult)
  - Struct: `CorruptionReport` (corruption_type, severity, errors, recoverable_sections)
  - Enum: `CorruptionType` (8 variantes: InvalidHeader, CorruptXRef, MissingEOF, etc.)
  - Enum: `RepairStrategy` + Struct: `RepairResult`
  - Funciones: quick_recover, analyze_corruption, detect_corruption, repair_document
  - ~5 ciclos TDD

- [x] F64: Streaming Full
  - Struct: `StreamingDocument<File>` (next_page, process_pages, memory_usage, clear_cache)
  - Struct: `StreamingPage` (number, width, height, extract_text_streaming, media_box)
  - Struct: `PageStreamer<File>` (next, seek_to_page, total_pages)
  - Struct: `IncrementalParser` (feed, take_events, is_complete)
  - Enum: `ParseEvent` (Header, ObjectStart, ObjectEnd, StreamData, XRef, Trailer, EndOfFile)
  - Struct: `TextStreamer` (process_chunk, extract_text)
  - Struct: `TextStreamOptions` (min_font_size, max_buffer_size, preserve_formatting)
  - Struct: `ChunkProcessor` + Struct: `ContentChunk` + Struct: `ChunkOptions`
  - **Nota FFI**: `<R: Read + Seek>` genérico — wrappear con `File` concreto y `Cursor<Vec<u8>>` para bytes.
  - ~5 ciclos TDD

### Tier 16 — Signatures & Forms Deep (F75-F76, ~8 ciclos TDD) ✅ COMPLETADO

APIs confirmadas en core. **183 tests (140 F76 + 43 F75).**

- [x] F75: Signatures Deep
  - Struct: `ParsedSignature` (digest_algorithm, signature_algorithm, signer_certificate_der, signature_value)
  - Struct: `SignatureVerificationResult` (hash_valid, signature_valid, details) + is_valid()
  - Struct: `TrustStore` (mozilla_roots, empty, root_count, is_mozilla_bundle)
  - Struct: `ByteRange` (from_array, ranges, total_bytes, validate)
  - Struct: `CertificateValidationResult` (subject, issuer, valid_from, valid_to, is_time_valid, is_trusted, warnings)
  - Función: `FullSignatureValidationResult.validate_certificate(cert_der, trust_store)`
  - Enum: `DigestAlgorithm`, `SignatureAlgorithm`
  - **Nota**: Requiere feature `signatures` en Cargo.toml — actualmente solo tiene `compression`.
  - ~4 ciclos TDD

- [x] F76: Forms Deep
  - Struct: `FormManager` (add_text_field, add_combo_box con Widget + FieldOptions)
  - Struct: `AcroForm` (fields, need_appearances, sig_flags, add_field, to_dict)
  - Struct: `FormData` (values HashMap, set_value, get_value)
  - Struct: `CalculationEngine` (evaluate, set_field_value)
  - Enum: `FieldAction` (11 variantes: JavaScript, Format, Calculate, SubmitForm, ShowHide, etc.)
  - Struct: `FieldActions` (10 event handlers: on_focus, on_blur, on_format, on_calculate, etc.)
  - Struct: `AppearanceDictionary` (set_appearance, get_appearance)
  - ~4 ciclos TDD

### Tier 17 — Parser Low-Level & XMP Metadata (F77-F78, ~8 ciclos TDD) ✅ COMPLETADO

APIs confirmadas en core. **77 tests (47 F77 + 30 F78).**

- [x] F77: ContentParser + ContentOperation
  - Función: `ContentParser.parse_content(content: bytes) → Vec<ContentOperation>`
  - Enum: `ContentOperation` (70+ variantes organizadas en categorías):
    - Text: BeginText, EndText, ShowText, SetFont, etc.
    - Graphics State: SaveGraphicsState, RestoreGraphicsState, SetLineWidth, etc.
    - Path: MoveTo, LineTo, CurveTo, ClosePath, Rectangle
    - Painting: Stroke, Fill, FillStroke, EndPath
    - Color: SetStrokingRGB, SetNonStrokingRGB, SetStrokingCMYK, etc.
    - Clipping: Clip, ClipEvenOdd
    - Marked Content: BeginMarkedContent, EndMarkedContent
    - XObjects: PaintXObject
  - Struct: `XRefTable` (entries, parse) — acceso low-level a tabla de referencias
  - **Nota**: ContentOperation requiere wrapping cuidadoso — 70+ variantes como Python enum/dataclass.
  - ~5 ciclos TDD

- [x] F78: XMP Metadata
  - Struct: `XmpMetadata` (set_text, set_date, set_array, set_bag, set_struct, add_property)
  - Struct: `XmpProperty` (namespace, name, value)
  - Enum: `XmpNamespace` (DublinCore, XmpBasic, XmpRights, XmpMediaManagement, Pdf, Photoshop, Custom)
  - Enum: `XmpValue` (Text, Date, Array, Bag, Alt, Struct, ArrayStruct)
  - Document integration: Document.set_xmp_metadata(metadata)
  - ~3 ciclos TDD

### Tier 18 — Verification & Compliance (F79-F80, ~6 ciclos TDD) ✅ COMPLETADO

APIs confirmadas en core: módulo `verification`. **28 tests.**

- [x] F79: Compliance System
  - Struct: `ComplianceSystem` (ISO matrix compliance verification)
  - Struct: `IsoMatrix`, `ComplianceReport`, `ComplianceStats`
  - Struct: `IsoRequirement`, `RequirementInfo`, `RequirementStatus`
  - Función: verify_iso_requirement()
  - ~3 ciclos TDD

- [x] F80: PDF Comparison Deep
  - Struct: `ComparisonResult` (detailed differences)
  - Struct: `PdfDifference` (structured diffs)
  - Función: extract_pdf_differences()
  - Función: pdfs_structurally_equivalent()
  - Enum: `DifferenceSeverity`
  - Nota: compare_pdfs (F39) ya existe como wrapper básico. Este feature lo profundiza.
  - ~3 ciclos TDD

### Tier 19 — Semantic & Graphics Extraction (F81-F82, ~6 ciclos TDD) ✅ COMPLETADO

APIs confirmadas en core. **68 tests (44 F81 + 24 F82).** Feature `semantic` activada.

- [x] F81: Semantic Marking (reemplaza F40 stub)
  - Struct: `SemanticEntity` (type, text, bbox, metadata, relations)
  - Struct: `SemanticMarker` (mark_entity, build_entity_map)
  - Struct: `EntityBuilder` (set_type, set_text, set_bbox, add_relation)
  - Struct: `EntityMap` (entities, find_by_type, find_related)
  - Enum: `EntityType` (**reimplementar** — actual es stub sin funcionalidad)
  - Enum: `RelationType`
  - Enum: `ExportFormat`
  - ~3 ciclos TDD

- [x] F82: Graphics Extraction
  - Struct: `GraphicsExtractor` (extract_from_page → ExtractedGraphics)
  - Struct: `ExtractedGraphics` (lines, horizontal_count, vertical_count, has_table_structure)
  - Struct: `VectorLine` (x1, y1, x2, y2, orientation, stroke_width, color, length, midpoint)
  - Struct: `ExtractionConfig` (min_line_length, extract_diagonals, stroked_only)
  - Enum: `LineOrientation` (Horizontal, Vertical, Diagonal)
  - ~3 ciclos TDD

### Tier 20 — Annotations Deep (F83, ~4 ciclos TDD)

APIs confirmadas en core: tipos específicos en módulo `annotations`.

- [ ] F83: Specific Annotation Types
  - Structs con APIs ricas (vs Annotation genérica actual):
    - `CircleAnnotation`, `SquareAnnotation` (GeometricAppearance: fill_color, stroke_color, border_width)
    - `LineAnnotation` (start/end points, LineEndingStyle enum: None, Square, Circle, Diamond, OpenArrow, ClosedArrow, Butt, Slash)
    - `FreeTextAnnotation` (default_appearance, intent, callout_line)
    - `InkAnnotation` (ink_list: Vec<Vec<Point>>)
    - `StampAnnotation` (StampName enum: Approved, Experimental, NotApproved, Draft, Final, etc.)
    - `FileAttachmentAnnotation` (FileAttachmentIcon enum: Graph, Paperclip, PushPin, Tag)
    - `PolygonAnnotation`, `PolylineAnnotation` (vertices)
    - `HighlightAnnotation` (QuadPoints)
    - `LinkAnnotation` (LinkAction, LinkDestination, HighlightMode)
    - `PopupAnnotation` (parent, PopupFlags)
  - ~4 ciclos TDD

### Tier 21 — Deepen Existing Minimal Wrappers (F84-F86, ~6 ciclos TDD)

Estos features profundizan wrappers existentes que solo exponen constructors.

- [ ] F84: Templates Deep
  - Struct: `TemplateParser` (parse template string → analysis)
  - Struct: `TemplateAnalysis` (placeholders found, warnings)
  - Struct: `Placeholder` (name, position, default_value)
  - Enum: `TemplateError` (detailed error types)
  - Enum: `TemplateValue` (String, Number, Boolean, List, Map)
  - Profundizar TemplateRenderer con error handling y multi-value types
  - ~2 ciclos TDD

- [ ] F85: PdfA Validation Deep
  - Profundizar PdfAValidator: validate(data) → ValidationResult detallado
  - Struct: `ValidationResult` (errors, warnings, conformance level achieved)
  - Enum: `PdfAConformance` (variantes más allá de A1B/A2B/A3B)
  - Enum: `ValidationError`, `ValidationWarning`
  - Struct: `XmpPdfAIdentifier`
  - ~2 ciclos TDD

- [ ] F86: Dashboard Deep
  - Profundizar DashboardBuilder: add_component, add_kpi_card, set_theme, build → Document
  - Integración con Charts (F58): DashboardBarChart, DashboardPieChart, DashboardLineChart
  - Dashboard layout: grid system, ComponentSpan
  - ~2 ciclos TDD

---

## Resumen Cuantitativo

| Tier | Features | Ciclos TDD est. | Prioridad | Impacto |
|------|----------|----------------|-----------|---------|
| 9 — Charts | F58a-e | ~15 | Alta | Generación visual para reportes |
| 10 — Advanced Tables | F61a-e | ~12 | Alta | Tablas profesionales (finance, reports) |
| 11 — Page Transitions | F60a-b | ~4 | Media | Presentaciones PDF |
| 12 — AI/ML Pipeline | F59a-e | ~14 | Alta | RAG, chunking, extraction para LLMs |
| 13 — Graphics Avanzado | F65-F70 | ~20 | Media | Gradientes, patterns, ICC, spot colors |
| 14 — Text Extraction | F71-F74 | ~10 | Alta | Extraction avanzado, columnas, facturas |
| 15 — Batch/Recovery/Streaming | F62-F64 | ~15 | Media | Procesamiento enterprise |
| 16 — Signatures/Forms Deep | F75-F76 | ~8 | Media-Baja | Firmas verificables, formularios avanzados |
| 17 — Parser/XMP | F77-F78 | ~8 | Baja | Low-level access, XMP metadata |
| 18 — Verification | F79-F80 | ~6 | Baja | ISO compliance |
| 19 — Semantic/GraphicsExtract | F81-F82 | ~6 | Media | AI marking, vector extraction |
| 20 — Annotations Deep | F83 | ~4 | Media | Tipos específicos con APIs ricas |
| 21 — Deepen Existing | F84-F86 | ~6 | Baja | Completar wrappers mínimos |
| **TOTAL** | **56 features** | **~128 ciclos** | | |

---

## Notas Técnicas de FFI

### Genéricos `<R: Read + Seek>`
Módulos streaming, recovery, graphics extraction usan genéricos. Estrategia:
- Wrappear con tipos concretos: `File` para paths, `Cursor<Vec<u8>>` para bytes
- Ofrecer `from_path()` y `from_bytes()` como constructores Python

### Callbacks (`Box<dyn Fn>`, `Arc<dyn Trait>`)
BatchProcessor y StreamingDocument usan callbacks. Opciones:
- PyO3 `Py<PyAny>` como callback wrapper
- Polling API alternativa (get_progress en lugar de callback)

### Feature flags
- `signatures`: Requerido para F75 (SignatureVerificationResult detallado). Hay que activarlo en Cargo.toml.
- `semantic`: Requerido para JsonExporter y RagChunk.to_json(). Verificar disponibilidad.

### EntityType (F40 actual)
Es un **stub** sin funcionalidad (`_private: ()`). F81 lo reemplaza completamente.

---

## Quality Review Anterior (2026-03-18)

10 hallazgos corregidos:
1. ✅ Memory leak Box::leak → String return
2. ✅ page_index eliminado de form methods (BREAKING)
3. ⏭️ detect_signatures post-promoción — descartado (promoción automática lo impide)
4. ✅ pdf_err_to_py preserva jerarquía
5. ⏭️ Catch-all arms — mantenidos (enums tienen Custom variant)
6. ✅ is_map parameter en set_open_action_uri
7. ✅ WriterConfig constructor con kwargs
8. ✅ ParsedPage/TextChunk exportados
9. ✅ Certificado DER valida longitud mínima
10. ✅ set_rotation valida 0/90/180/270
11. ✅ Opacity valida rango [0.0, 1.0]
