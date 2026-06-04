# Release v0.7.0

## Summary

Minor release that pulls in upstream `oxidize-pdf` v2.12.0 and bundles three things:

1. **GFX-019 colour-drawing surface** (from upstream 2.11.0): ICC-based, named-calibrated, and named-Lab fill/stroke colours, plus page-level colour-space resource registration (`Page.add_color_space` + the new `PageColorSpace` type).
2. **Two Python-bridge bug fixes** — #78 (text measurement ignored embedded custom-font metrics) and #80 (draws after `add_page` were lost), with a Document-bound text-measurement API.
3. **Glyph-coverage diagnostics** for embedded custom fonts (upstream #287): the new `EmbeddedFont` type plus `Document.embedded_font` / `Document.font_missing_glyphs`.

This is a non-breaking, additive change at the API level. Every previously-callable method preserves its signature; the new capabilities are opt-in. The one behavioural change is itself a bug fix: drawing after `add_page` now reaches the saved page instead of being silently dropped. Python is the first oxidize-pdf binding to expose the GFX-019 content-stream drawing side end-to-end (the .NET M3 milestone shipped only the resource-registration half, blocked at the time on the absent upstream `set_fill_color_icc`).

## Upstream

- **`oxidize-pdf` `=2.10.0` → `=2.12.0`.** Pinned exact equality preserved. Feature set unchanged (`compression, signatures, semantic`, `default-features = false`).
- Upstream 2.11.0 added (a) named ICC / calibrated / Lab colour setters on `GraphicsContext` (GFX-019) and (b) a partitioner heading-classification fix that consumes `TextFragment.struct_tag` (issue #271).
- Upstream 2.12.0 added ICC colour spaces as conformant `/ICCBased` streams (#282/#283), indexed-image extraction fixes (#286), and glyph-coverage diagnostics for embedded fonts (#287). The bridge surfaces #287; the others are internal core improvements. Note that the bridge bugs #78/#80 were diagnosed as bridge-level — upstream 2.12.0 does not fix them — and are resolved here in the binding.

## Bug Fixes

### #78 — `measure_text` / `measure_char` ignored embedded custom-font metrics

Two compounding causes, both fixed in the bridge:

- The module-level `measure_text` / `measure_char` call the free upstream functions with no `FontMetricsStore`, so `Font.custom(name)` could never resolve a document's embedded font and fell back to default (Helvetica-shaped) widths. There was no Document-bound measurement API.
- `Document.add_font(name, path)` delegated to upstream's path-variant which — unlike `add_font_from_bytes` — does **not** register text metrics, so even a Document-bound measurement would have seen an empty store.

The fix routes `add_font(path)` through the byte-loading path (registering the embedded glyph widths) and adds `Document.measure_text` / `Document.measure_char`, which measure against this Document's font store via upstream `measure_text_with` / `measure_char_with`. Built-in fonts measure identically to the free functions.

### #80 — draws after `add_page` produced a blank page

`add_page(page)` cloned the page's content at call time, so any draw issued on the Python page object afterwards was lost. Because `new_page_a4()` does not register the page itself, the natural "create page, add it, then draw" order silently produced an empty page.

The fix makes `Document` hold live handles (`Py<Page>`) to the same Python page objects rather than eager clones, and materialise each page's *current* content into the underlying document at save time — across all four save paths (`save`, `save_to_bytes`, and the `_with_config` variants). Materialisation is idempotent across repeated saves, and `page_count` counts pages added but not yet saved.

## Added

### `PageColorSpace` Python class

A typed wrapper for page-level colour-space resources (ISO 32000-1 §8.6), emitted at `/Resources/ColorSpace/<name>`. Construct via static factories:

- `PageColorSpace.device(name)` — a device-space alias (`DeviceGray`, `DeviceRGB`, `DeviceCMYK`, `Pattern`). Raises `ValueError` for any other name.
- `PageColorSpace.icc_based(n, alternate)` — an ICCBased space with `n` channels (must be 1, 3, or 4 per §8.6.5.5; other values raise `ValueError`) and a device `alternate` (e.g. `"DeviceRGB"`).
- `PageColorSpace.cal_gray(CalGrayColorSpace)`, `.cal_rgb(CalRgbColorSpace)`, `.lab(LabColorSpace)` — calibrated/Lab spaces built from the existing colour-space types; the parameter dictionary is derived from the source object, not hand-written.
- `PageColorSpace.parameterised(family, params)` — generic escape hatch for the `#[non_exhaustive]` family set. `family` is one of `CalGray`, `CalRGB`, `Lab`, `ICCBased`; `params` is a `dict[str, object]` mapping PDF parameter names to int / float / str (a PDF name) / list-of-those. A Python `bool` in `params` raises `ValueError` rather than being silently coerced to `1`/`0` (Python `bool` subclasses `int`, but PDF has no boolean parameter type here).

### `Page` colour-drawing methods (GFX-019)

- `Page.add_color_space(name, PageColorSpace)` — registers the space on the page. Raises `PdfError` if `name` is not a valid PDF resource name (ISO 32000-1 §7.3.5).
- `Page.set_fill_color_icc(name, components)` / `Page.set_stroke_color_icc(name, components)` — paint with a registered ICC space. `components` must be non-empty: an empty list would emit a bare `sc`/`SC` operator with no operands (invalid per §8.6.8). Upstream only guards this with a `debug_assert!` (compiled out in release builds), so this binding enforces it in all builds, raising `ValueError`.
- `Page.set_fill_color_calibrated_named(name, CalibratedColor)` / stroke variant — paint with a calibrated space registered under a caller-supplied name. Lets multiple calibrated spaces coexist on one page, removing the prior one-calibrated-space-per-page limitation.
- `Page.set_fill_color_lab_named(name, LabColor)` / stroke variant — same, for Lab spaces.

The legacy `set_fill_color_calibrated` / `set_fill_color_lab` methods are unchanged; they continue to emit the default `CalRGB1` / `Lab1` resource slots (upstream now delegates them to the `_named` variants with the default names).

### Document-bound text measurement (#78)

- `Document.measure_text(text, font, size) -> float` and `Document.measure_char(ch, font, size) -> float` — measure scoped to this Document's embedded fonts, so `Font.custom(name)` resolves to the embedded font's real per-glyph widths. The module-level free functions cannot resolve per-Document fonts (they hold no Document handle); these methods are the correct API for custom-font layout maths.

### Glyph-coverage diagnostics (#287)

- `EmbeddedFont` — a handle to a custom font embedded on a Document. Exposes `name`, `has_glyph(ch) -> bool`, and `missing_glyphs(text) -> list[str]` (deduplicated, first-seen order). Characters with no glyph render as `.notdef` (an empty box); these let callers detect coverage gaps before rendering. An empty `missing_glyphs` result means every character is covered *or* coverage could not be determined (upstream `coverage_known()` is `pub(crate)`, so it is not surfaced; fonts loaded via `add_font` parse their cmap, so coverage is determinable for them).
- `Document.embedded_font(name) -> EmbeddedFont | None` and `Document.font_missing_glyphs(name, text) -> list[str]` (a one-off convenience over the handle).

### Type stubs

`PageColorSpace` and the seven new `Page` methods are added to `_oxidize_pdf.pyi`. `EmbeddedFont`, the two `Document.measure_*` methods, `Document.embedded_font`, `Document.font_missing_glyphs`, and `Document.add_font` / `add_font_from_bytes` were added too, with `EmbeddedFont` re-exported from `__init__`. The previously-undeclared calibrated colour types (`CalGrayColorSpace`, `CalRgbColorSpace`, `LabColorSpace`, `CalibratedColor`, `LabColor`) gained stub entries as well, since the new signatures reference them and `.pyi` files are analysed in isolation. The stub was verified against the runtime API (no drift).

## Tests

`tests/test_page_color_spaces_gfx019.py` — 19 new tests, each asserting against the actual decoded content-stream bytes (or the serialised resource dict), never a return code or byte count:

- ICC fill/stroke emit `/<name> cs` + `<components> sc` (and `CS`/`SC` for stroke) in order, with components rendered to four decimals; the ICC resource survives as an `/ICCBased` family array. CMYK (4-channel) and Gray (1-channel) covered.
- Empty ICC component lists raise `ValueError` (fill and stroke).
- `icc_based` rejects channel counts outside `{1, 3, 4}`; accepts the legal three.
- Two named calibrated spaces coexist and paint in draw order on one page, proving the one-space-per-page limit is removed.
- Named calibrated stroke, Lab fill, and Lab stroke each emit the correct named space and normalised components (`LabColor.values()` maps L/100 and `(x−rmin)/(rmax−rmin)` into `[0,1]`).
- Device-alias registration, the `parameterised` escape hatch (int/float/str/list round-trip; unknown-family and bool-value rejection), and invalid-resource-name rejection (`PdfError`).
- The legacy `set_fill_color_calibrated` still emits `/CalRGB1 cs` after the upstream delegation refactor.

### Bug-fix and diagnostics tests

- `tests/test_issue_78_custom_font_metrics.py` — 5 tests. `add_font(path)` registers the same embedded metrics as `add_font_from_bytes`; Document-bound measurement of a custom font differs from the Helvetica-shaped fallback; per-character widths reflect the font's proportions (`W` wider than `i`); measurement scales linearly with size; built-in fonts match the free function.
- `tests/test_issue_80_add_page_by_reference.py` — 8 tests, asserting the actual decoded Contents stream. Draws after `add_page` appear; draws before still work; both survive together; `page_count` reflects unsaved pages; saving twice does not duplicate pages; the `_with_config` save path captures post-add draws; pages added between saves are all present; each of multiple pages keeps its own post-add content.
- `tests/test_issue_287_glyph_diagnostics.py` — 10 tests against the Roboto fixture (a CJK ideograph as the uncovered probe): handle lookup and `None` for unknown fonts; `has_glyph` true/false; `missing_glyphs` listing, empty-when-covered, and dedup; the `Document.font_missing_glyphs` convenience and its empty-on-unknown-font contract; single-character validation.

## Compatibility

- **Source-compatible.** No existing signature changed. All new surface is additive.
- **Wire-format unchanged** for any code that does not call the new methods.

## Validation

- `cargo check --all-targets` and `cargo build --release`: clean, no warnings.
- `mypy python/oxidize_pdf`: clean (2 source files).
- `pytest`: **2186 passed** (2163 from the GFX-019 work + 23 new: #78 ×5, #80 ×8, #287 ×10).
- `maturin develop --release`: clean build against `oxidize-pdf` 2.12.0.
- CI on the develop PR: green across Python 3.10–3.13 on ubuntu / macOS / windows.
