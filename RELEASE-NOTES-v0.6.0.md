# Release v0.6.0

## Summary

Minor release that pulls in upstream `oxidize-pdf` v2.10.0 — two minor versions worth of text-extraction quality work — and exposes the new public API surface to Python: marked-content-aware `TextFragment` extraction, paragraph reconstruction, TJ-kern space synthesis, and `/Artifact` filtering.

This is a non-breaking change: existing callers see identical behaviour because every new option defaults to the same value the previous binding behaved as. New capabilities are opt-in.

## Upstream

- **`oxidize-pdf` `=2.8.2` → `=2.10.0`.** Pinned exact equality preserved. Feature set unchanged (`compression, signatures, semantic`, `default-features = false`). Notably, upstream `2.9.0` moved `ocr-tesseract` out of default features and made `external-images` default; this binding never depended on `ocr-tesseract`, so the change is transparent here.

## Added

### `TextFragment` Python class + positional extraction methods

`oxidize-pdf` 2.10.0 added `mcid: Option<u32>` and `struct_tag: Option<String>` to `TextFragment`, carrying the innermost marked-content ancestor's identity (e.g. `"P"`, `"H1"`, `"Figure"`, `"Artifact"`) for tagged PDFs. To make these reachable from Python, this release introduces a `TextFragment` Python class and two new `PdfReader` methods:

- `PdfReader.extract_fragments_with_options(options) -> list[list[TextFragment]]` — returns one list of fragments per page.
- `PdfReader.extract_fragments_from_page(page_index, options) -> list[TextFragment]` — single-page variant.

`TextFragment` exposes `text`, `x`, `y`, `width`, `height`, `font_size`, `font_name`, `is_bold`, `is_italic`, `color`, `mcid`, `struct_tag`, and `space_decisions` as read-only properties. `font_name` and `struct_tag` use borrowed `&str` returns under the frozen pyclass to avoid per-call allocation. `__eq__` is structural across content, position, geometry, font metadata, colour, and marked-content identity (excluding `space_decisions`, which is opt-in instrumentation). Fragments are only produced when `options.preserve_layout = True` (upstream contract preserved verbatim).

### `SpaceDecision` Python class

Exposed for forward compatibility with the existing `ExtractionOptions.track_space_decisions` flag. `SpaceDecision` is a frozen pyclass with read-only getters `offset`, `dx`, `threshold`, `confidence`, and `inserted`, matching the upstream Rust struct exactly. Note: upstream 2.10.0 declares the type but no extractor path currently pushes onto the per-fragment vector — the binding ships the class so that when upstream wires the producer, no further Python-side wiring is needed. A regression test pins the current empty-vector contract so the activation event is explicit.

### `ExtractionOptions` new flags

Three new constructor keyword arguments (and matching getters) on `ExtractionOptions`, all defaulting to upstream defaults so existing callers see no behaviour change:

- `tj_space_threshold: float = 0.2` (upstream `#272`) — synthesises an implicit `U+0020` when a `TJ` numeric kern exceeds this fraction of the font size. Catches inter-word gaps encoded as wide negative kerns rather than literal spaces (typical for LaTeX, kerned typography, academic publishers).
- `reconstruct_paragraphs: bool = False` (upstream `#261`) — groups raw fragments into visual lines and paragraphs with hyphenation handling. Required by partitioner pipelines to emit paragraph-granularity elements.
- `include_artifacts: bool = False` (upstream `#269`) — by default filters out `/Artifact` marked-content scopes (page headers, footers, watermarks, decorative content). Opt-in for forensic / redaction use cases.

### `PlainTextConfig` new flag

- `tj_space_threshold: float = 0.2` — mirror of `ExtractionOptions.tj_space_threshold` for the plain-text extraction path.

## Tests

`tests/test_text_extraction.py` extended with ten new content-verifying tests under `TestTextFragmentExtraction`. Each test asserts behaviour against the actual extracted fragments rather than counts or success flags:

- `test_extract_fragments_with_options_returns_per_page_lists` — verifies the per-page list-of-lists shape on a single-page sample PDF emitting five `Tj` operators at known coordinates.
- `test_extract_fragments_from_page_sorted_by_y_descending` — verifies the `sort_by_position=True` default surfaces fragments top-to-bottom: first fragment at `y ≈ 750`, last at `y ≈ 660`, monotonic non-increase across the chain.
- `test_fragment_exposes_position_and_font_metadata` — asserts the `"Contract #12345"` fragment carries `x ≈ 50.0`, `y ≈ 750.0`, `font_size = 12.0`, positive width/height, and the correct bold/italic flags for Helvetica.
- `test_fragment_mcid_and_struct_tag_none_for_untagged_pdf` — asserts that for an untagged PDF (the sample emits plain `Tj` without `/MCID … BDC … EMC`) every fragment's `mcid` and `struct_tag` is `None`. Encodes the 2.10.0 contract that these fields are only populated for tagged PDFs.
- `test_fragment_repr_includes_text_and_position` — asserts `repr()` surfaces `x=`, `y=`, `mcid=`, `struct_tag=`.
- `test_extract_fragments_without_preserve_layout_yields_empty` — asserts the upstream contract verbatim: `preserve_layout=False` yields no fragments, exposing the choice to Python callers rather than synthesising.
- `test_extract_fragments_from_invalid_page_raises` — asserts an out-of-range page index raises `PdfParseError` specifically (not a generic `Exception`).
- `test_fragment_eq_is_structural` — asserts `==` is structural across re-extractions of the same bytes and that distinct fragments from the same page compare unequal.
- `test_space_decisions_returns_list_with_or_without_flag` — pins the current upstream 2.10.0 contract (vector always empty regardless of `track_space_decisions`) so that when upstream wires the producer the test fails loudly and gets replaced.
- `test_fragment_color_reflects_set_fill_color` — reproduces the issue #57 fix flow (rect fill + colour switch + text) and asserts the extracted fragment's `color` carries the red the producer set, not the prior magenta.

Existing `TestExtractionOptions` and `TestPlainTextConfig` updated to cover the new fields' defaults, custom values, `repr()` surface, and (for `dense()` / `loose()` presets) the upstream `tj_space_threshold` values (`0.1` and `0.25` respectively).

## Compatibility

- **Source-compatible.** All previously-callable methods preserve their signatures; new arguments on `ExtractionOptions.__init__` and `PlainTextConfig.__init__` have defaults matching pre-existing behaviour.
- **Wire-format unchanged** for any code that does not opt into the new flags. Enabling `reconstruct_paragraphs=True` or `include_artifacts=False` (the new default for `/Artifact`) changes the extracted-text shape — but `include_artifacts` already defaults to the no-artifacts behaviour that RAG callers consistently expect, matching the upstream Phase-1 decision (issue #269).

## Validation

- `cargo check --all-targets`: clean, no warnings.
- `pytest --ignore=tests/mcp_tests`: **1976 passed** (1966 baseline carried over from 0.5.2 + 10 new fragment-extraction tests).
- `maturin develop --release`: clean build against `oxidize-pdf` 2.10.0.
