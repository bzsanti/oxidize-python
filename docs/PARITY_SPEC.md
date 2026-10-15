# Bridge Parity Spec — Python + .NET

**Reconciled:** 2026-10-15, Python issue [#266](https://github.com/bzsanti/oxidize-python/issues/266).
**Source checkpoints (not package-release claims):** Python 0.22.0, `55c3528843ec2bbe6d4fc413879f6936fd35d000`;
.NET managed package 0.19.0, `0b8905e6624d02b80bd6c18c409879dedcb916e6` (native FFI crate 0.14.0).
These are repository snapshots; features added after a release are not promised by
the published package with the same manifest version. Both Cargo manifests pin
core **=5.4.2**. Equal core versions do not establish
bridge parity, identical output, or complete security/standards guarantees.

This document is a synchronized **partial capability inventory and work contract**,
not a certificate that either bridge implements all Rust functionality. It replaces
the mixed May 2026 status table. The historical Python and .NET versions remain
available in the [Python checkpoint](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/docs/PARITY_SPEC.md) and
[.NET checkpoint](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/docs/PARITY_SPEC.md); their old checkmarks and TODOs are
historical assertions, not current evidence. All 107 existing IDs are retained.
No global coverage percentage is published: a complete inventory of core
capabilities and behavioral evidence per capability is still missing.

## Evidence and status semantics

- **API**: the named binding exists in the inspected source (and, for Python,
  the installed runtime). It does not assert all options work or certify equivalence.
- **Partial**: a concrete limitation or asymmetry is stated; the action remains open.
- **Absent**: no equivalent public binding found in the inspected bridge snapshot.
- **Unreviewed/external**: current availability or behavior has not been established;
  it must not be interpreted as absent, complete, or a stale release claim.
- **Tests present/configured**: source or CI wiring exists, not a new execution result.
- **N/A**: an ecosystem-specific capability, with the reason stated.

RAG/AI remains the scheduling priority. Tier 0 cannot be promoted to semantic
parity without fixtures that assert meaningful content/results in both bridges.
Python [#244](https://github.com/bzsanti/oxidize-python/issues/244), .NET
[#81](https://github.com/bzsanti/oxidize-pdf-dotnet/issues/81), and core
[#710](https://github.com/bzsanti/oxidizePdf/issues/710) track the larger work.
This documentation reconciliation does not authorize API renaming or migrations.

### Audited sources and behavioral anchors

Python sources: [reader](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/src/parser.rs), [RAG/config models](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/src/ai_pipeline.rs),
[writer](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/src/document.rs), [operations](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/src/operations.rs),
[forms](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/src/forms.rs), [outline reader](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/src/outline_read.rs),
[public stubs](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/python/oxidize_pdf/_oxidize_pdf.pyi).
.NET sources: [extractor and native call sites](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET/PdfExtractor.cs),
[writer](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET/PdfDocument.cs),
[operations](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET/PdfOperations.cs),
[managed models](https://github.com/bzsanti/oxidize-pdf-dotnet/tree/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET/Models),
[hybrid config](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET/Pipeline/HybridChunkConfig.cs),
[native implementation](https://github.com/bzsanti/oxidize-pdf-dotnet/tree/0b8905e6624d02b80bd6c18c409879dedcb916e6/native/src).

Behavioral anchors for the corrected RAG/outline claims:
[Python RAG](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/tests/test_rag_reader_parity.py),
[Python outlines](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/tests/test_outline_read.py),
[.NET hybrid config](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET.Tests/Pipeline/PdfExtractorHybridChunksTests.cs),
[.NET disjointness](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET.Tests/Pipeline/RagChunksDisjointnessTests.cs),
[.NET bookmarks](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET.Tests/BookmarkReadingTests.cs).
Python's bounded, audited contract and prior execution evidence are in
[parity-contract.json](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/docs/parity-contract.json) and
[FEATURE_PARITY.md](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/docs/FEATURE_PARITY.md). Tests and native call paths were
inspected for this source review; .NET tests were not rerun for this docs-only edit.
The issue-266 evidence in the Python repository records the row-to-symbol/source
inventory; it is presence evidence, not a full behavioral audit.

## RAG capabilities

| ID | Capability | Python | .NET | Action for parity / limitation |
| --- | --- | --- | --- | --- |
| RAG-001 | Partition document → semantic elements | API `PdfReader.partition` | API `PartitionAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| RAG-002 | RAG chunks (default config) | API `PdfReader.rag_chunks` | API `RagChunksAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| RAG-003 | RAG chunks with `ExtractionProfile` | API `PdfReader.rag_chunks_with_profile` | API `RagChunksAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| RAG-004 | `ExtractionProfile` enum (7 values: `STANDARD`, `RAG`, `ACADEMIC`, `FORM`, `GOVERNMENT`, `DENSE`, `PRESENTATION`) | API `ExtractionProfile` | API `ExtractionProfile` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| RAG-005 | Granular HybridChunkConfig and partition options | API `PdfReader.rag_chunks_with` | API `RagChunksAsync` | Python config and custom token counter are exposed (#260). .NET exposes partition + hybrid configs; compare context/token policies before claiming equivalence. |
| RAG-006 | `MergePolicy` enum (`AnyInlineContent`, `SameTypeOnly`) | API `MergePolicy` | API `MergePolicy` | Both expose two policies; the old spurious Python None TODO is obsolete. |
| RAG-007 | `ReadingOrderStrategy` (`Simple`, `None`, `XyCut(min_gap)`) | API `ReadingOrderStrategy` | API `ReadingOrderStrategy` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| RAG-008 | Chunk arbitrary text | API `DocumentChunker.chunk_text` | API `ChunkText` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| RAG-009 | Token estimation utility | API `DocumentChunker.estimate_tokens` | API `EstimateTokens` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| RAG-010 | Per-page chunking | API `PdfReader.chunk_page` | API `ExtractChunksFromPageAsync` | Python: chunk_page(page_index, chunk_size=512, overlap=50). .NET: see ExtractChunksFromPageAsync options; do not copy Python arguments. |
| RAG-011 | Markdown export | API `PdfReader.to_markdown` | API `ToMarkdownAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| RAG-012 | Markdown export with configurable `MarkdownOptions` | API `MarkdownExporter.export` | API `ToMarkdownAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| RAG-013 | Contextual export (LLM context windows) | API `PdfReader.to_contextual` | API `ToContextualAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| RAG-014 | Structured JSON export | API `PdfReader.to_json` | API `ToJsonAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| RAG-015 | RagChunk result schema | API `RagChunk` | API `RagChunk` | Both: compare schema, source metadata, ordering and serialization; matching model names do not prove semantic equivalence. |
| RAG-016 | Element result schema | API `Element` | API `PdfElement` | Element/PdfElement are idiomatic public names; no rename or migration is authorized by this matrix. |
| RAG-017 | `DocumentChunk` schema | API `DocumentChunk` | API `DocumentChunk` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| RAG-018 | Page content analysis (text/scanned/mixed) | API `analyze_page_content` | API `AnalyzePageContentAsync` | Python: analyze_page_content(input_path, page_number). Classification is not image recognition. |
| RAG-019 | OCR for scanned PDFs (Tesseract) | Absent — no real Tesseract recognition binding | Absent — no real Tesseract recognition binding | Both: expose and validate recognition. Python #262; supplied OCR text layers are a separate capability. |
| RAG-020 | Semantic disjointness regression evidence | Tests present: test_rag_chunks_disjoint.py and test_rag_reader_parity.py | Tests present: Pipeline/RagChunksDisjointnessTests.cs | Both: retain semantic fixtures. No cross-bridge execution or identical-output result is claimed here. |
| RAG-021 | First-class adapter for ecosystem RAG framework | External integration — publication not revalidated | API/project: OxidizePdf.NET.KernelMemory | Consult INT-001/002; a project in source does not prove current package publication. |

## READ capabilities

| ID | Capability | Python | .NET | Action for parity / limitation |
| --- | --- | --- | --- | --- |
| READ-001 | Open PDF from file path | API `PdfReader.open` | Partial — PdfExtractor methods consume byte[] | .NET: caller loads bytes; a stateful file-path reader equivalent to Python is not established. |
| READ-002 | Open PDF from bytes | API `PdfReader.from_bytes` | API `ExtractTextAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| READ-003 | Read a file-like or network input | Partial — from_stream reads the input into memory | Partial — caller supplies byte[] | Both: do not describe buffered input as bounded network streaming. Python PageStreamer is a separate file iterator (#254/#255); options/lazy work remains #258. |
| READ-004 | Page count | API `PdfReader.page_count` | API `GetPageCountAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| READ-005 | PDF version | API `PdfReader.version` | API `GetPdfVersionAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| READ-006 | Extract text (single page) | API `PdfReader.extract_text_from_page` | API `ExtractTextFromPageAsync` | Python reader indexes are zero-based; legacy .NET extraction uses one-based pageNumber. New .NET bookmarks/operations may use zero-based page_index. Follow each API; no blanket migration. |
| READ-007 | Extract text (all pages) | API `PdfReader.extract_text` | API `ExtractTextAsync` | Python returns list[str]; legacy .NET ExtractTextAsync returns concatenated string. .NET per-page alternatives require explicit consumer choice. |
| READ-008 | Extract text with `ExtractionOptions` | API `PdfReader.extract_text_with_options` | API `ExtractTextWithResultAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| READ-009 | Document metadata | API `PdfReader.metadata` | API `ExtractMetadataAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| READ-010 | Page dimensions | API `PdfReader.get_page` | API `GetPageGeometryAsync` | .NET GetPageDimensionsAsync still returns width/height; use GetPageGeometryAsync for rotation and boxes. |
| READ-011 | Page resources (fonts, images) | API `PdfReader.get_page_resources` | API `GetPageResourcesAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| READ-012 | Decoded page content streams | API `PdfReader.get_page_content_streams` | API `GetPageContentStreamAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| READ-013 | Lenient/tolerant parsing | Partial — ParseOptions accepted by open/from_bytes/from_stream | API ParseOptions (inspect each consuming overload) | Python #259 documents inert core options; neither a tolerant constructor nor memory_limit proves a parser resource bound. |
| READ-014 | Extract embedded font program bytes | API `PdfReader.resolve_font` | API `GetResolvedFontResourceAsync` | Both: resolved font APIs expose embedded font data; inspect subtype/optional-result behavior. Old blanket absent status is obsolete. |
| READ-015 | Extract single image XObject by name | Absent — no equivalent public reader API | API `PdfImages` | Python: add named-image selection to public API. |
| READ-016 | Distinguish direct vs inherited resources | Absent — no equivalent public reader API | API `GetPageResourceProvenanceAsync` | Python: expose direct/inherited resource provenance. |
| READ-017 | Raw undecoded content streams + filter chain metadata | Absent — no equivalent public reader API | API `PdfStreams` | Python: expose raw streams and filter-chain metadata; current content-stream method returns decoded bytes. |

## WRITE capabilities

| ID | Capability | Python | .NET | Action for parity / limitation |
| --- | --- | --- | --- | --- |
| WRITE-001 | Create empty document | API `Document` | API `PdfDocument` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-002 | Set metadata (title, author, subject, keywords, creator, producer, dates) | API `Document.set_producer` | API `SetProducer` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-003 | Add pages | API `Document.add_page` | API `AddPage` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-004 | Save to bytes | API `Document.save_to_bytes` | API `SaveToBytes` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-005 | Save to file | API `Document.save` | API `SaveToFile` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-006 | Writer configuration and save methods | API `WriterConfig` | API `PdfSaveOptions` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-007 | Encrypt RC4-128 | API `Document.encrypt` | API `Encrypt` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-008 | Encrypt AES-128 | Partial — AES enum and encrypt binding | Partial — explicit AES methods | Both inherit pinned core 5.4.2. Python #253 tracks fallible cryptographically secure IV generation; API presence is not a security approval. |
| WRITE-009 | Encrypt AES-256 | Partial — AES enum and encrypt binding | Partial — explicit AES methods | Both inherit pinned core 5.4.2. Python #253 tracks fallible cryptographically secure IV generation; API presence is not a security approval. |
| WRITE-010 | Permissions | API `Permissions` | API `PdfPermissions` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-011 | Embed font from bytes | API `Document.add_font_from_bytes` | API `AddFont` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-012 | Embed font from file path | API `Document.add_font` | API `AddFontFromFile` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-013 | Open action (GoTo page, URI) | API `Document.set_open_action_goto` | API `SetOpenAction` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-014 | Viewer preferences | API `Document.set_viewer_preferences` | API `SetViewerPreferences` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-015 | Outlines/bookmarks: separate reading and writing | API OutlineTree/OutlineItem write; PdfReader.outline()/outline_with_options() read | API SetOutline write; GetBookmarksAsync read | Both have bounded reading. Python returns ReadOutline/items; .NET returns preorder PdfBookmark list. Named/GoTo destinations resolve; other actions are not executed. |
| WRITE-016 | Named destinations | API `NamedDestinations` | API `AddNamedDestination` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-017 | Page labels (custom numbering) | API `PageLabelTree` | API `SetPageLabels` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-018 | Tagged PDF (Structure tree) | API `Document.set_struct_tree` | API `SetStructureTree` | Creation is exposed in both bridges. Existing-document tagged editors/preparation are separate contracts; Python #262 remains open. |
| WRITE-019 | Semantic entities (AI-ready markup) | API `EntityMap` | API `SetEntityContent` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-020 | `WriterConfig.pdf_version` / `PdfSaveOptions.PdfVersion` explicit version kwarg | API `WriterConfig.pdf_version` | API `PdfVersion` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| WRITE-021 | In-memory save with config (no file roundtrip) | API `Document.save_to_bytes_with_config` | API `SaveToBytes` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |

## ANN capabilities

| ID | Capability | Python | .NET | Action for parity / limitation |
| --- | --- | --- | --- | --- |
| ANN-001 | Read annotations from existing PDF | Partial — IncrementalFreeTextEditor/IncrementalInkEditor read their annotation types | API `GetAnnotationsAsync` | Python: no general PdfReader.get_annotations API established; do not infer arbitrary annotation reading from creation classes. |
| ANN-002 | Write link annotations (URI + GoTo) | API `LinkAnnotation` | API `AddLinkUri` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| ANN-003 | Write text markup (highlight, underline, strikeout) | API `MarkupAnnotation` | API `AddHighlight` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| ANN-004 | Write text note + stamp + geometric annotations | API `TextAnnotation` | API `AddTextNote` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| ANN-005 | FileAttachment annotation | API `FileAttachmentAnnotation` | Absent — no public FileAttachment creation API found | .NET: expose/validate FileAttachment creation; Python type presence does not certify all embedded-file semantics. |
| ANN-006 | FreeText annotation | API `FreeTextAnnotation` | API `EditFreeTextAnnotationsAsync` | Python has creation and IncrementalFreeTextEditor; .NET EditFreeTextAnnotationsAsync targets existing PDFs. Keep creation and incremental editing distinct. |

## FORM capabilities

| ID | Capability | Python | .NET | Action for parity / limitation |
| --- | --- | --- | --- | --- |
| FORM-001 | Read form fields (text, checkbox, radio, dropdown, listbox, button) | Unreviewed — general existing-field inventory not established | API `GetFormFieldsAsync` | Python: verify actual existing-PDF reading separately from FormManager in-memory state; .NET has GetFormFieldsAsync. |
| FORM-002 | Create form fields | API `Document.add_checkbox` | API `AddTextField` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| FORM-003 | Fill form fields programmatically | API `IncrementalFormFiller` | API `FillFormFieldsAsync` | Distinguish new-document FillField from existing-document incremental updates; neither implies arbitrary form preservation. |
| FORM-004 | Form calculation engine | API `FormCalculationSystem` | Absent — no equivalent general engine found | .NET: scope and expose a calculation/field-validation engine; TextValidation is text analysis, not form validation. |
| FORM-005 | Field validation | API `FieldValidator` | Absent — no equivalent general engine found | .NET: scope and expose a calculation/field-validation engine; TextValidation is text analysis, not form validation. |

## OPS capabilities

| ID | Capability | Python | .NET | Action for parity / limitation |
| --- | --- | --- | --- | --- |
| OPS-001 | Split to individual pages | API `split_pdf` | API `SplitAsync` | Both: these legacy operations may reconstruct documents. Use explicit existing-document preservation policies for audited structural guarantees. |
| OPS-002 | Split by size/range | API `split_pdf_with_options` | API `SplitAsync` | Both: these legacy operations may reconstruct documents. Use explicit existing-document preservation policies for audited structural guarantees. |
| OPS-003 | Merge documents | API `merge_pdfs` | API `MergeAsync` | Both: these legacy operations may reconstruct documents. Use explicit existing-document preservation policies for audited structural guarantees. |
| OPS-004 | Merge with selective page ranges | API `merge_pdfs_with_inputs` | API `MergeAsync` | Both: these legacy operations may reconstruct documents. Use explicit existing-document preservation policies for audited structural guarantees. |
| OPS-005 | Rotate all pages | API `rotate_pdf` | API `RotateAsync` | Both: these legacy operations may reconstruct documents. Use explicit existing-document preservation policies for audited structural guarantees. |
| OPS-006 | Rotate selective pages | API `rotate_pdf_with_options` | API `RotatePagesAsync` | Both: these legacy operations may reconstruct documents. Use explicit existing-document preservation policies for audited structural guarantees. |
| OPS-007 | Extract pages | API `extract_pages` | API `ExtractPagesAsync` | Both: these legacy operations may reconstruct documents. Use explicit existing-document preservation policies for audited structural guarantees. |
| OPS-008 | Overlay/watermark | API `overlay_pdf` | API `OverlayAsync` | Both: these legacy operations may reconstruct documents. Use explicit existing-document preservation policies for audited structural guarantees. |
| OPS-009 | Reorder/swap/move/reverse pages | API `reorder_pdf_pages` | API `ReorderPagesAsync` | Both: these legacy operations may reconstruct documents. Use explicit existing-document preservation policies for audited structural guarantees. |
| OPS-010 | Extract images | API `extract_images_in_memory` | API `ExtractImagesAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| OPS-011 | Split using explicit page ranges | API `SplitMode.ranges` | API `PdfSplitMode` | .NET PdfSplitMode.Ranges is exposed; old missing-constructor TODO is obsolete. |
| OPS-012 | Split pattern, metadata and optimization options | Partial — SplitOptions(mode, output_pattern, preserve_metadata, optimize) | Partial — PdfSplitOptions and SplitNamedAsync | Core 5.4.2 ignores Optimize. .NET copies four Info fields, names are suggestions; Python filesystem-pattern behavior is different. No optimization/full metadata-preservation claim. |
| OPS-013 | Expose `MetadataMode` in merge | Absent — no MetadataMode selector on merge bindings | API PdfMergeMetadataOptions / MergeWithMetadataAsync | Python: expose metadata selection; .NET contract covers Title/Author/Subject/Keywords, not XMP or structural preservation. |

## SIG capabilities

| ID | Capability | Python | .NET | Action for parity / limitation |
| --- | --- | --- | --- | --- |
| SIG-001 | Detect signatures | API `PdfReader.detect_signatures` | API `HasDigitalSignaturesAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| SIG-002 | Parse signatures (PKCS#7/CMS) | API `parse_pkcs7_signature` | API `GetDigitalSignaturesAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |
| SIG-003 | Verify signatures | API `verify_pdf_signature` | API `VerifySignaturesAsync` | Both: retain API contract; cross-bridge semantic equivalence remains unverified. |

## PDFA capabilities

| ID | Capability | Python | .NET | Action for parity / limitation |
| --- | --- | --- | --- | --- |
| PDFA-001 | PDF/A validation | API `PdfAValidator` | Absent — no public PDF/A validator found | Python validator does not certify all ISO conformance; .NET: expose validation with explicit rule coverage. |
| PDFA-002 | XMP metadata read/write | Partial — XmpMetadata and Document.create_xmp_metadata/get_xmp_packet | Absent — no general public XMP editor found | Python: distinguish new-document XMP from existing-PDF read/write; .NET: scope/expose XMP support. |

## INT capabilities

| ID | Capability | Python | .NET | Action for parity / limitation |
| --- | --- | --- | --- | --- |
| INT-001 | LlamaIndex reader (PyPI) | External/unreviewed — no release state inferred | N/A or external integration, outside native bridge inventory | Integration maintainers: verify package/repository and published version before claiming availability. Historical release numbers are not current evidence. |
| INT-002 | Microsoft Kernel Memory adapter (NuGet) | N/A — .NET ecosystem | Project present: dotnet/OxidizePdf.NET.KernelMemory | The old sample-only claim is obsolete. NuGet publication/version is not revalidated in this source review. |
| INT-003 | LangChain document loader | External/unreviewed — no release state inferred | N/A or external integration, outside native bridge inventory | Integration maintainers: verify package/repository and published version before claiming availability. Historical release numbers are not current evidence. |
| INT-004 | Haystack converter | External/unreviewed — no release state inferred | N/A or external integration, outside native bridge inventory | Integration maintainers: verify package/repository and published version before claiming availability. Historical release numbers are not current evidence. |
| INT-005 | Semantic Kernel plugin | N/A — .NET ecosystem | Unreviewed — KernelMemory is not automatically a Semantic Kernel plugin | Integration maintainers: verify the specific adapter before claiming support. |
| INT-006 | Claude Code plugin | External/unreviewed — no release state inferred | N/A or external integration, outside native bridge inventory | Integration maintainers: verify package/repository and published version before claiming availability. Historical release numbers are not current evidence. |

## MCP capabilities

| ID | Capability | Python | .NET | Action for parity / limitation |
| --- | --- | --- | --- | --- |
| MCP-001 | MCP server (Anthropic protocol) | API FastMCP server: 12 tools, 5 static resources + session template, 5 prompts | Absent — no MCP server in this snapshot | Python: see MCP catalog/interop CI. These are selected tools, not full Rust API exposure; no .NET server implementation is authorized here. |
| MCP-002 | Official MCP registry submission | Unreviewed — live registry not queried | N/A — no server in snapshot | Registry owners: verify current publication separately. No registry update is requested by this document correction. |

## QA capabilities

| ID | Capability | Python | .NET | Action for parity / limitation |
| --- | --- | --- | --- | --- |
| QA-001 | `FEATURE_PARITY.md` up to date with current bridge version | Current partial status above historical FEATURE_PARITY matrix | Current increment tracking in FEATURE_PARITY | Both: preserve dated evidence; update current status without relabeling historical tests as fresh runs. |
| QA-002 | Semantic disjointness tests for RAG | Tests present; see RAG-020 | Tests present; see RAG-020 | Old .NET absent-test claim is obsolete. No fixed historical test count is a coverage guarantee. |
| QA-003 | Cross-platform build/test configuration | Configured: 3 OS families × Python 3.10–3.14 | Configured: net8.0/net9.0/net10.0 project; Linux x64/arm64, Windows x64, macOS arm64 test jobs | Distinguish target frameworks, native build matrix and actual test commands. See pinned workflow sources; not five Python OS families. |
| QA-004 | Empirical audit script for RAG correctness | Unreviewed/private process artifact | Unreviewed/private process artifact | Both: private notes are not a public capability contract or reproducible evidence. Use versioned tests, contract and CI; no naming migration required. |
| QA-005 | Cross-session error log | Unreviewed/private process artifact | Unreviewed/private process artifact | Both: private notes are not a public capability contract or reproducible evidence. Use versioned tests, contract and CI; no naming migration required. |
| QA-006 | TDD plan visible | Unreviewed/private process artifact | Unreviewed/private process artifact | Both: private notes are not a public capability contract or reproducible evidence. Use versioned tests, contract and CI; no naming migration required. |

## OCR capabilities

| ID | Capability | Python | .NET | Action for parity / limitation |
| --- | --- | --- | --- | --- |
| OCR-001 | `TesseractOcrProvider` real provider | Absent — no real Tesseract recognition binding | Absent — no real Tesseract recognition binding | Both: expose and validate recognition. Python #262; supplied OCR text layers are a separate capability. |
| OCR-002 | `OcrOptions.preprocessing` (deskew, denoise, enhance_contrast) | Absent — no real recognition/provider contract | Absent — no real recognition/provider contract | Both: expose recognition options/provider results with behavioral evidence. OcrEngine enum or MockOcrProvider is not recognition. |
| OCR-003 | `OcrProcessingResult.fragments` with per-word confidence | Absent — no real recognition/provider contract | Absent — no real recognition/provider contract | Both: expose recognition options/provider results with behavioral evidence. OcrEngine enum or MockOcrProvider is not recognition. |
| OCR-004 | Searchable PDF / OCR text layer | Absent — no existing-PDF OCR text-layer editor binding | Partial — PdfOcrLayer.PlanAsync/ApplyAsync consumes supplied recognition data | Python #262: expose layer editing. .NET does not recognize images; callers supply fragments/confidence. This is not a Tesseract-backed searchable-PDF pipeline. |
| OCR-005 | `OcrProvider` protocol (Python ABC / C# interface) | Absent — no real recognition/provider contract | Absent — no real recognition/provider contract | Both: expose recognition options/provider results with behavioral evidence. OcrEngine enum or MockOcrProvider is not recognition. |

## Core guarantees and current work boundaries

API presence must be separated from effectiveness. In pinned 5.4.2, Python parser
and recovery options include inert fields; RecoveryOptions.memory_limit is not a
memory bound and a successful repair can produce empty pages. Batch timeout and
memory options are not enforced by core. StreamingOptions/LazyDocument presence
is not evidence of a bounded streaming implementation (Python #258/#259/#257).
AES IV generation remains tracked by Python #253; do not infer cryptographic
security from AES enum availability or round-trip success.

Legacy split/merge/mutation methods may reconstruct content. Both bridges have
separate policy-driven existing-document APIs; preservation can reject unsupported
structures. These guarantees cannot be attached to every operation with a similar
name. New incremental editing, signing, revision comparison and irreversible
redaction require their own contracts, beyond this historical ID set. Python
#262/#263 remain open. .NET has separate tagged/OCR-layer/redaction/comparison
surfaces; that does not mean Python inherits their bindings.

For recent .NET differences see [split options](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET/PdfSplitOptions.cs),
[split results](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET/PdfSplitResult.cs),
[merge metadata](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET/PdfMergeMetadata.cs),
[OCR layer](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET/PdfOcrLayer.cs),
[named images](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET/PdfImages.cs),
[raw streams](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET/PdfStreams.cs),
[FreeText editing](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET/PdfOperations.FreeText.cs),
[KernelMemory project](https://github.com/bzsanti/oxidize-pdf-dotnet/tree/0b8905e6624d02b80bd6c18c409879dedcb916e6/dotnet/OxidizePdf.NET.KernelMemory), and
[CI](https://github.com/bzsanti/oxidize-pdf-dotnet/blob/0b8905e6624d02b80bd6c18c409879dedcb916e6/.github/workflows/ci.yml). Python CI is
[here](https://github.com/bzsanti/oxidize-python/blob/55c3528843ec2bbe6d4fc413879f6936fd35d000/.github/workflows/test.yml). Package registry state is intentionally
not inferred from these source files.

## Maintenance rules

1. `docs/PARITY_SPEC.md` in both repositories is a byte-identical mirror. Propagate
   changes in the same PR cycle and compare both copies before acceptance.
2. Preserve IDs. Update both status cells and the action together, with a source
   checkpoint and behavioral evidence for any stronger guarantee. Do not replace
   uncertainty with an unqualified checkmark or a count of passing tests.
3. New core capabilities need new IDs and evidence; the retained legacy rows are
   not the denominator for a global coverage percentage.
4. Keep dated release notes and validation logs historical. Current source/package
   versions, build matrices and open work belong in the current sections.
5. Review each bridge independently. Equal method names, schema shapes, a core pin,
   or successful smoke tests do not establish semantic equivalence.
