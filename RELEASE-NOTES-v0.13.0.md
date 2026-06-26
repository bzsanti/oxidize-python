# Release v0.13.0

## Summary

Minor release that bumps the bundled `oxidize-pdf` core from `=2.16.3` to
`=3.0.1` and surfaces the new upstream **CID-keyed positioned-glyph-run** write
path (issue #358) into the Python bridge. This lets callers draw a pre-shaped
glyph run — addressing glyphs directly by id, with per-glyph kerning and offset
— while keeping the result extractable as text.

No breaking change to the existing Python API: the upstream 3.0.0 breaking
changes touch only low-level font modules the bridge never used.

## Added — CID-keyed positioned glyph runs (issue #358)

A pre-shaped glyph run (e.g. produced by a HarfBuzz-style shaper) can now be
embedded as an Identity-H `Type0`/`CIDFontType2` font where the CID equals the
glyph id, drawn as a `TJ` array, and accompanied by a `ToUnicode` CMap so the
text stays searchable/extractable. The embedded font is subset to the used
glyph ids.

New surface:

- `CidMapping(cid_to_gid=..., cid_to_unicode=..., cid_to_unicode_str=...,
  max_cid=...)` — keyword dicts populate the underlying maps; `max_cid` is
  auto-derived as the largest CID across every map when omitted.
  `cid_to_unicode_str` lets a single CID (e.g. an `fi` ligature glyph)
  decompose to several characters in the `ToUnicode` CMap.
- `CidShowElement(cid, adjust)` with `.with_x_offset(offset)` and `cid` /
  `adjust` / `x_offset` accessors. `adjust` is the post-glyph advance kern
  (`TJ` convention); `x_offset` displaces a glyph without consuming advance
  (GPOS mark attachment / diacritics).
- `Document.add_cid_keyed_font(name, data, mapping)` — registers a CID-keyed
  font on a path kept separate from the Unicode-keyed embedding path. Only
  TrueType/SFNT (`CIDFontType2`) fonts are supported.
- `Page.set_custom_font(name, size)` — selects the active custom font for
  subsequent drawing (required before `show_cid_array`).
- `Page.show_cid_array(elements, x, y)` — writes the positioned glyph run.

## Changed — upstream bump to `oxidize-pdf` 3.0.1

- 3.0.0 introduces the CID glyph-run API above and a subset-by-used-GIDs
  embedding path for it.
- 3.0.1 fixes font loss when a merged page's `/Resources` references `/Font`
  indirectly (`/Font 1 0 R`) rather than inline.

The two upstream 3.0.0 breaking changes (removal of the non-functional
`truetype_subsetting` glyph subsetter; `CidMapping` becoming `#[non_exhaustive]`)
do not affect the bridge — neither symbol was used in bridge source.

## Fixed — MCP `convert_pdf` parameter description

The `max_tokens` parameter description claimed it applied to `format='rag'`, but
the `rag` path calls `rag_chunks()` with a fixed internal budget and ignores it.
The description now states `max_tokens` applies to `format='chunks'` only. A
characterization test pins that `rag` output is independent of `max_tokens`.

## Tests

- New `tests/test_issue_358_cid_glyph_run.py`: builds a CID-keyed font with
  CIDs distinct from their GIDs, draws a positioned run (including an `fi`
  ligature CID), and verifies the end-to-end contract on real bytes —
  `Type0`/`CIDFontType2`/`Identity-H` structure, the CID codes in the `TJ`
  content stream, and a text-extraction round-trip yielding `fix` via the
  `ToUnicode` CMap.
- New characterization test in `tests/mcp_tests/test_tool_convert_pdf.py` for
  the `max_tokens`/`rag` contract.
- Full suite green; `mypy` clean; `cargo check`/`cargo fmt` clean.

## Compatibility

- **Python 3.10+**, `cp310-abi3` wheels (unchanged).

## Breaking Changes

None to the Python API.
