# Release v0.8.0

## Summary

Minor release that pulls in upstream `oxidize-pdf` v2.13.0 and surfaces its new
RAG/AI-pipeline capabilities in the Python bridge:

1. **Per-chunk and document-level language detection** (upstream #293) — opt-in
   ISO 639-3 detection for chunked text, exposed through
   `DocumentChunker.with_language_detection(True)`, the new `DetectedLanguage`
   type on `DocumentChunk.language`, and the `DocumentChunker.document_language`
   aggregator.
2. **Token-efficient chunk serialization** (upstream #291) — the new
   `TokenEfficientExporter`, a compact, fully round-trippable tabular format for
   RAG chunks that roughly halves the serialized-token count versus JSON.
3. **`JsonExporter`** — structured JSON export for documents and RAG chunks,
   completing the chunk-export surface alongside the token-efficient format.
4. **Ruling-based table detection control** (upstream #292) —
   `PartitionConfig.prefer_ruling_tables` getter plus
   `PartitionConfig.without_ruling_tables()` to opt out of vector-grid table
   reconstruction in the partition pipeline.

This is a non-breaking, additive change at the API level. Every previously
callable method preserves its signature; the new capabilities are opt-in. The
image-extraction fixes from upstream (#286: `/SMask` alpha compositing and the
flate compression-ratio false-positive) are inherited transparently through the
version bump with no bridge API change.

## Upstream

- **`oxidize-pdf` `=2.12.0` → `=2.13.0`.** Pinned exact equality preserved. The
  `language-detection` feature was added to the dependency's feature set
  (`compression, signatures, semantic, language-detection`,
  `default-features = false`) to pull in the pure-Rust `whatlang` detector that
  backs the new language APIs.
- Upstream 2.13.0 added: ruling-based (vector-grid) table detection wired into
  the partition pipeline (#292), per-chunk/document language detection (#293),
  `/SMask` soft-mask compositing into RGBA on image extraction plus a flate
  compression-ratio guard fix (#286), and the token-efficient chunk serializer
  with the unifying `ChunkExporter` trait (#291).

## Toolchain

- **MSRV raised to Rust 1.88** (from 1.77), tracking upstream 2.13.0's own MSRV
  bump. The 2025 ecosystem migration to edition 2024 plus `let`-chains made the
  previously declared 1.77 unbuildable through the dependency tree.

## Added

### Language detection (RAG chunks)

- `DocumentChunker.with_language_detection(enabled: bool)` — builder that turns
  on per-chunk language detection. Disabled by default; when off,
  `DocumentChunk.language` stays `None`.
- `DocumentChunk.language` — `DetectedLanguage | None`. Populated during
  `chunk_text` only when detection is enabled.
- `DocumentChunker.document_language(chunks)` — static method returning the
  dominant `DetectedLanguage` across chunks, weighted by chunk content length.
  Returns `None` when no chunk carries a detected language (including the empty
  list).
- `DetectedLanguage` — frozen type with `code` (ISO 639-3, e.g. `"eng"`,
  `"spa"`), `confidence` (`float` in `[0.0, 1.0]`), and `reliable` (`bool`).
  Short or ambiguous text can yield an unreliable detection with an
  effectively-random code; gate routing on `reliable`.

### Chunk exporters

- `TokenEfficientExporter` — `export_chunks(chunks)` serializes RAG chunks to the
  `#oxct/1` tabular format (header declared once, one tab-separated row per
  chunk); the static `TokenEfficientExporter.parse_chunks(serialized)` is its
  exact inverse, reconstructing the `DocumentChunk` list. Parsing raises on a
  wrong version marker, wrong header, or a row whose column count does not match
  the header.
- `JsonExporter` — `export(text)` for a simple document object and
  `export_chunks(chunks)` for a structured `chunked_document` object
  (`type`, `chunk_count`, `chunks[]`). Constructor takes
  `pretty_print` (default `True`) and `include_chunks` (default `False`);
  `JsonExporter.default()` mirrors the upstream defaults.

### Partition configuration

- `PartitionConfig.prefer_ruling_tables` — read-only getter; `True` by default,
  matching upstream. When enabled, bordered tables are reconstructed from the
  PDF's drawn grid (primary path) and per-page graphics are extracted only for
  pages that have a drawn grid, so table-free documents pay no extra cost.
- `PartitionConfig.without_ruling_tables()` — builder that disables the
  ruling-based detector; only the spatial detector runs and no page graphics are
  extracted. Chains with the existing `without_tables` / `with_*` builders.

## Compatibility

Fully backward compatible. All 2038 existing tests pass unchanged; 20 new tests
cover the added surface (language detection round-trips against real
English/Spanish corpora, token-efficient export/parse round-trip,
`chunked_document` JSON shape, and the ruling-tables flag). `mypy` and
`cargo clippy -D warnings` are clean.
