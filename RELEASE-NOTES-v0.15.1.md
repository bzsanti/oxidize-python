# Release v0.15.1

## Summary

Bumps the bundled `oxidize-pdf` core from `=4.0.0` to `=4.1.0`. This is a
core-only release: no Python API changes, no new bindings. It ships three
correctness fixes and one security patch that reach existing Python callers
without any code change on their side.

Two of the fixes are silent-failure bugs — they returned plausible-looking
wrong output rather than raising — so upgrading is recommended for anyone
extracting text from third-party PDFs.

## Fixed — page trees with indirect `/Kids` or `/Count` (core #415)

A `/Pages` node storing `/Kids` or `/Count` as an indirect reference
(`N G R`) instead of inline is spec-legal per ISO 32000-1 §7.3.10 and is
emitted by iText. On those documents `PdfReader.page_count` returned `0` and
`PdfReader.extract_text()` returned empty text — with no error raised. One
level of indirection now resolves consistently across the page-tree flat
index, `page_count()`, and PDF/A page-walk validation.

## Fixed — LZW `EarlyChange` code-width boundary (core #415)

The LZW decoder widened the code one entry too late (`2^width` instead of
`2^width - 1` under the default `EarlyChange=1`), desyncing streams that grew
past 511/1023/2047 dictionary entries and failing with `invalid code`.
Corrected per ISO 32000-1 §7.4.4.2.

## Fixed — column detection no longer shreds tokens (core #422, #417)

Affects the opt-in `ExtractionOptions(detect_columns=True)` path only; the
default extraction path was never affected.

- Column blocks now require their wide gaps to align horizontally across rows.
  Previously, normal-leading lines that each happened to contain a wide gap at
  a *different* X were merged into a false column block and reordered
  column-major, which split tokens apart — CNPJ identifiers in label/value
  forms were a reported case (#422).
- Line grouping is now head-anchored, and a multi-line column block only forms
  when its rows are at least one line height apart. Previously a fixed
  `newline_threshold` band keyed to the previous fragment merged tight-leading
  prose into one pseudo-line and then reordered it as a table (#417).

Real tables and genuine multi-column layouts are unaffected.

## Security — quick-xml DoS advisories (core #416)

The core bumped `quick-xml` 0.39 → 0.41, clearing **RUSTSEC-2026-0194** and
**RUSTSEC-2026-0195**: a quadratic duplicate-attribute check and an unbounded
namespace-declaration allocation, both reachable through untrusted XMP
metadata in a PDF. The unused `serialize` (serde) feature was dropped; XMP
parsing uses only the streaming pull-parser.

## Not included

Core 4.1.0 also added `ConicShading` and `FreeFormGouraudShading` /
`GouraudVertex` with `Page::add_mesh_shading` / `add_conic_shading`. These are
**not** exposed in the Python bridge yet — it still binds `AxialShading` and
`RadialShading` only. Wrapping the new shading types is deferred to a future
minor release.

## Compatibility

No breaking changes. No Python API additions or removals. Wheels remain
`cp310-abi3` (Python 3.10+).
