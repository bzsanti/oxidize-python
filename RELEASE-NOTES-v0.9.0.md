# Release v0.9.0

## Summary

Minor release that pulls in upstream `oxidize-pdf` v2.14.0 and exposes its new
gradient-rendering capability in the Python bridge.

Upstream 2.14.0 makes axial and radial shadings **actually render**: a shading
now emits a real PDF `/Function` (Type 2 exponential for two colour stops, Type
3 stitching for more) together with the required `/ColorSpace`, instead of the
previous placeholder `/Function 1` integer with no paint operator (upstream
#297). The bridge already exposed the shading *definition* types
(`AxialShading`, `RadialShading`, `ShadingManager`), but they were a dead end:
there was no way to attach a shading to a page nor to paint it. This release
adds the missing paint path.

This is a non-breaking, additive change at the API level. Every previously
callable method preserves its signature; the new methods are purely additive.
The text-extraction quality fixes from upstream (word scramble in dense and
multi-column documents #302/#305, the `chunk_text` infinite-loop guard #308, and
the non-ASCII WinAnsi glyph measurement corrections #309/#313) are inherited
transparently through the version bump with no bridge API change.

## Upstream

- **`oxidize-pdf` `=2.13.0` → `=2.14.0`.** Pinned exact equality preserved; the
  feature set is unchanged (`compression, signatures, semantic,
  language-detection`, `default-features = false`).
- Upstream 2.14.0 added real gradient rendering (#297) and fixed: word scramble
  from unresolved indirect `/Font` dictionaries and overlapping font-switched
  runs (#302, #305), a `DocumentChunker::chunk_text` infinite loop (#308), and
  `measure_text`/`get_string_width` over-measuring non-ASCII WinAnsi glyphs
  (#309, #313).

## Added

### Gradient rendering (`Page`)

The canonical bounded-gradient idiom is: register a shading, then bound it with
a clip and paint it —
`add_shading` → `save_graphics_state` → build a path → `clip` → `end_path` →
`paint_shading` → `restore_graphics_state` (the PDF `q … W n /Sh sh … Q`
sequence).

- `Page.add_shading(name, shading)` — registers an `AxialShading` or
  `RadialShading` under `/Resources/Shading/<name>`. `name` must be a valid PDF
  resource name; an invalid name raises `PdfError` and a non-shading object
  raises `TypeError`.
- `Page.paint_shading(name)` — emits the `sh` operator, painting the named
  shading into the current clip region. If `name` was never registered the
  operator is still emitted but references an undefined resource (no `/Shading`
  dict is written); conforming viewers skip the paint.
- `Page.clip()` / `Page.clip_even_odd()` — emit the `W` / `W*` clip-path
  operators, intersecting the clipping region with the current path using the
  non-zero winding or even-odd rule. Bound an arbitrary-shaped gradient region.
- `Page.end_path()` — emits the `n` operator, terminating a clip path
  (`W n` / `W* n`) without filling or stroking.

Rectangular gradient regions can also be bounded with the existing
`Page.set_clipping_path`; the new `clip` / `end_path` pair covers
arbitrary-shaped clips.

## Compatibility

Fully backward compatible. All 2038 pre-existing tests pass unchanged; 12 new
tests cover the added surface: exact content-stream operators in document order
(`W` → `n` → `/Sh sh`), resource registration (`/ShadingType 2` axial,
`/ShadingType 3` radial), a real `/FunctionType 2` exponential function for a
two-stop axial gradient (the #297 proof), two shadings coexisting on one page,
the unregistered-name contract, and the invalid-name / non-shading-object error
paths. `mypy` and `cargo clippy -D warnings` are clean; the full suite is 2050
passing.
