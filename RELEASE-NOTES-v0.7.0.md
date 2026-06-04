# Release v0.7.0

## Summary

Minor release that pulls in upstream `oxidize-pdf` v2.11.0 and exposes its new GFX-019 colour-drawing surface to Python: ICC-based, named-calibrated, and named-Lab fill/stroke colours, plus page-level colour-space resource registration (`Page.add_color_space` + the new `PageColorSpace` type).

This is a non-breaking, additive change. Every previously-callable method preserves its signature; the new capabilities are opt-in. Python is the first oxidize-pdf binding to expose the GFX-019 content-stream drawing side end-to-end (the .NET M3 milestone shipped only the resource-registration half, blocked at the time on the absent upstream `set_fill_color_icc`).

## Upstream

- **`oxidize-pdf` `=2.10.0` → `=2.11.0`.** Pinned exact equality preserved. Feature set unchanged (`compression, signatures, semantic`, `default-features = false`).
- Upstream 2.11.0 adds (a) named ICC / calibrated / Lab colour setters on `GraphicsContext` (GFX-019) and (b) a partitioner heading-classification fix that consumes `TextFragment.struct_tag` (issue #271). The partitioner fix is internal to the core — it improves structured extraction without requiring new bindings, since `TextFragment.struct_tag` is already exposed (since 0.6.0). The full baseline suite passes unchanged against 2.11.0, confirming the fix introduces no regression in this binding.

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

### Type stubs

`PageColorSpace` and the seven new `Page` methods are added to `_oxidize_pdf.pyi`. The previously-undeclared calibrated colour types (`CalGrayColorSpace`, `CalRgbColorSpace`, `LabColorSpace`, `CalibratedColor`, `LabColor`) gained stub entries as well, since the new signatures reference them and `.pyi` files are analysed in isolation. The stub was verified against the runtime API (no drift).

## Tests

`tests/test_page_color_spaces_gfx019.py` — 19 new tests, each asserting against the actual decoded content-stream bytes (or the serialised resource dict), never a return code or byte count:

- ICC fill/stroke emit `/<name> cs` + `<components> sc` (and `CS`/`SC` for stroke) in order, with components rendered to four decimals; the ICC resource survives as an `/ICCBased` family array. CMYK (4-channel) and Gray (1-channel) covered.
- Empty ICC component lists raise `ValueError` (fill and stroke).
- `icc_based` rejects channel counts outside `{1, 3, 4}`; accepts the legal three.
- Two named calibrated spaces coexist and paint in draw order on one page, proving the one-space-per-page limit is removed.
- Named calibrated stroke, Lab fill, and Lab stroke each emit the correct named space and normalised components (`LabColor.values()` maps L/100 and `(x−rmin)/(rmax−rmin)` into `[0,1]`).
- Device-alias registration, the `parameterised` escape hatch (int/float/str/list round-trip; unknown-family and bool-value rejection), and invalid-resource-name rejection (`PdfError`).
- The legacy `set_fill_color_calibrated` still emits `/CalRGB1 cs` after the upstream delegation refactor.

## Compatibility

- **Source-compatible.** No existing signature changed. All new surface is additive.
- **Wire-format unchanged** for any code that does not call the new methods.

## Validation

- `cargo check --all-targets`: clean, no warnings.
- `mypy python/oxidize_pdf`: clean (2 source files).
- `pytest`: **2163 passed** (2144 baseline carried over from 0.6.0 + 19 new GFX-019 tests).
- `maturin develop --release`: clean build against `oxidize-pdf` 2.11.0.
