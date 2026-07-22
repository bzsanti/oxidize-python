# Release v0.16.0

## Summary

Exposes the advanced shading surface added in `oxidize-pdf` core 4.1.0
(upstream #407) and bumps the bundled core from `=4.1.0` to `=4.2.0`. Three
new classes — `GouraudVertex`, `FreeFormGouraudShading`, `ConicShading` — and
two new `Page` methods — `add_mesh_shading`, `add_conic_shading` — bring
Type 4 free-form Gouraud triangle meshes and exact conic (angular) gradients
to Python. The core bump additionally ships text-extraction and RAG-chunking
correctness fixes that reach existing callers with no code change.

## Added — Type 4 free-form Gouraud mesh shadings (core 4.1.0, #407)

`FreeFormGouraudShading` emits a Type 4 mesh as a PDF stream per
ISO 32000-1 §8.7.4.5.5: the shading dictionary plus byte-aligned packed
vertex data.

```python
from oxidize_pdf import Color, Document, FreeFormGouraudShading, GouraudVertex, Page

mesh = FreeFormGouraudShading(
    "Mesh1",
    "DeviceRGB",
    [0.0, 100.0, 0.0, 100.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0],  # Decode
    [
        GouraudVertex(0, 10.0, 20.0, Color.rgb(1.0, 0.0, 0.0)),
        GouraudVertex(1, 30.0, 40.0, Color.rgb(0.0, 1.0, 0.0)),
        GouraudVertex(1, 50.0, 60.0, Color.rgb(0.0, 0.0, 1.0)),
    ],
)
page = Page.a4()
page.add_mesh_shading("Mesh1", mesh)
page.paint_shading("Mesh1")
```

- `GouraudVertex(flag, x, y, color)` — edge flag 0 starts a new triangle;
  1/2 share an edge with the previous one. Out-of-range flags raise
  `OverflowError` at construction (u8) or `PdfError` at validation (>2).
- Default bit widths are 16-bit coordinates, 8-bit components, 8-bit flags;
  override with `with_bits(bits_per_coordinate, bits_per_component,
  bits_per_flag)`.
- `validate()` enforces the Type 4 constraints (permitted bit widths,
  `Decode` length/ordering for the colour space, edge flags, DeviceGray
  meshes requiring gray vertex colours). `Page.add_mesh_shading` validates
  both the resource name and the mesh before registering.

## Added — exact conic (angular) gradients (core 4.1.0, #407)

`ConicShading` emits a Type 1 function-based shading whose `/Function` is a
real Type 4 PostScript calculator (angle around a centre → colour ramp), so
conic gradients are resolution-independent rather than a mesh approximation.

```python
from oxidize_pdf import Color, ColorStop, ConicShading, Page, ShadingPoint

conic = ConicShading(
    "Cone1",
    ShadingPoint(50.0, 50.0),
    [0.0, 100.0, 0.0, 100.0],  # domain
    [ColorStop(0.0, Color.red()), ColorStop(1.0, Color.blue())],
)
page = Page.a4()
page.add_conic_shading("Cone1", conic)
page.paint_shading("Cone1")
```

- Stops must be strictly ascending and (with 2+ stops) span [0.0, 1.0];
  `validate()` and `Page.add_conic_shading` enforce this.
- `with_matrix([a, b, c, d, e, f])` sets the shading-to-target transform.

Both shading kinds coexist with the existing axial/radial gradients in the
same `/Resources/Shading` dictionary and are painted with the pre-existing
`paint_shading(name)`. The resource key is the `name` argument of the
`add_*_shading` call; the shading's internal `name` is descriptive metadata
and never reaches the emitted PDF.

## Changed — core bumped to 4.2.0

Correctness fixes from core 4.2.0 that reach Python callers directly:

- **A lone space decoded from `/ToUnicode` was discarded as garbage**
  (core #438). The extractor fell back to the raw code and emitted the byte
  as a literal ASCII character, corrupting word boundaries in subsetted-font
  documents. Whitespace-only decodes are now accepted; the shared predicate
  also stops the CID path accepting C1 control codes as genuine text.
- **Chunk budgets were decided on a sum of per-element token counts**
  (core #435). Under a BPE counter a chunk could be approved on a cost that
  was never measured and exceed `max_tokens`. Every budget decision now
  measures the text it is about to emit; oversize fragments are flagged
  rather than passed off as within budget.
- **Paragraphs ran together across a font change in extraction**
  (core #436). A change of font size or weight now ends the paragraph, so a
  heading set in the same block as its body no longer merges into one run.

## Compatibility

- No breaking changes. All additions are new classes/methods.
- Wheels remain `cp310-abi3` (Python 3.10+).
- MSRV unchanged (1.88).

## Verification

- 38 new tests asserting real PDF bytes: `/ShadingType 4` dictionaries with
  packed vertex bytes cross-checked against core's byte-aligned pack fixture,
  `/ShadingType 1` with the deterministic PostScript `atan` prologue, `sh`
  operators in the decoded content stream, resource-key/internal-name
  separation, and every core `validate()` precondition as an error path.
- Full suite: 2210 passed. `mypy` clean. `cargo clippy --all-targets
  -- -D warnings` clean.
