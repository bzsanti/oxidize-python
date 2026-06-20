# Release v0.11.0

## Summary

Minor release that pulls in upstream `oxidize-pdf` v2.16.3 and wires its new
**experimental Analysis SPI** into the Python bridge, enriches `RagChunk`
metadata, adds document-source stamping, and switches the native extension to a
single **abi3 (stable ABI)** wheel.

Upstream 2.16.x exposes a Service Provider Interface (SPI) that lets a consumer
plug in custom chunking, classification, and metadata-enrichment logic without
forking the MIT core. This release surfaces that surface in
`oxidize_pdf.experimental` (semver-exempt, matching the upstream contract), plus
the always-on metadata that the new pipeline produces. It is a non-breaking,
additive change at the stable API level — every previously callable method
preserves its signature.

## Upstream

- **`oxidize-pdf` `=2.15.0` → `=2.16.3`.** Pinned exact equality preserved.
  Added the `unstable-spi` feature alongside the existing set (`compression,
  signatures, semantic, language-detection`, `default-features = false`).
- 2.16.0 introduced the experimental Analysis SPI and the enriched `RagChunk`
  metadata. 2.16.1–2.16.3 are bug fixes only (xref-stream double-decode #341,
  bounded-memory lenient parse #339, deterministic extraction/XMP #329/#331/#334)
  inherited transparently with no bridge API change.

## Added

### Experimental Analysis SPI (`oxidize_pdf.experimental`, semver-exempt)

Plug custom analysis logic into RAG chunk generation:

- `AnalysisPipeline` builder: `with_chunking`, `with_classifier`, `with_enricher`,
  `with_source`, `with_max_tokens`.
- `PdfReader.rag_chunks_with_pipeline(pipeline)` runs the configured pipeline.
- Support types: `ChunkGroup`, `ClassLabel` (compares against `str`),
  `ClassifyContext`, `EnrichContext`, `Element` (with a `class_label` getter so a
  strategy can read classifier labels), `DocumentSource`.
- `runtime_checkable` Protocols `ChunkingStrategy`, `ElementClassifier`,
  `MetadataEnricher` document the callback shapes a provider must implement.

The module name signals that this surface may change between releases (same
semver-exempt contract as the upstream `unstable-spi` feature).

### Enriched `RagChunk` metadata (always on, not SPI)

21 new getters on `RagChunk`: `heading_path`, `dominant_font[_size]`,
`is_bold`/`is_italic`, `min_confidence`, `content_types` (`ContentTypeFlags`),
`char`/`word`/`sentence_count`, `language`/`language_confidence`/`language_reliable`
(ISO 639-3), `chunk_id` chain, `page_span`, `page_regions` (`PageRegion` with
`ElementBBox`), `table_rows`/`table_cols`, `source` (`DocumentSource`), `extra`.

### Document-source stamping

- `DocumentSource(filename=..., doc_hash=...)`.
- `PdfReader.rag_chunks_with_source[_and_config]` — auto-fills
  title/author/creation_date/total_pages from the document info dict.

## Build & Packaging

### Single abi3 wheel (stable ABI)

The native extension now builds against PyO3's `abi3-py310` (Python limited API):

- One `cp310-abi3` wheel per platform covers Python **≥ 3.10** instead of a wheel
  per minor version.
- **Fixes the Windows / Python 3.13 link failure** (`LNK1181: cannot open input
  file 'python313.lib'`) seen after `windows-latest` rotated to the VS 18 / MSVC
  14.51 image whose Python 3.13.13 toolcache omits the version-specific import
  library. abi3 links against the always-present `python3.lib` forwarder instead.
- Verified: full CI matrix (3.10–3.13 × ubuntu/macos/windows) green; 2281 tests pass.

## Breaking Changes

None. All stable-API method signatures are preserved. The `experimental` module is
explicitly semver-exempt.
