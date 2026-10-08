# oxidize-pdf 0.21.0 — Core 5.4.1 and new Python APIs

- Update the Rust core from 5.1.5 to 5.4.1, retaining Python 3.10+, Rust 1.88,
  optional MCP SDK v2 and the RustCrypto certificate provider.
- Add explicit bounded text recovery on pages/documents with typed diagnostics
  distinguishing unverified, incomplete and omitted Flate content. Resource and
  predictor errors remain errors; ordinary extraction remains strict.
- Add optional non-breaking-space normalization to ExtractionOptions, effective
  PDF version reading and document build-identification controls.
- Add incremental signature-slot creation, listing, reading, drawing, completion
  and removal. Handwritten completion is distinct from cryptographic signing;
  completed slots are immutable and edits retain the original PDF byte prefix.
- Preserve the Python Type3 differences contract despite upstream encoding changes.
- Include native exports, type stubs, strict consumer checks and behavioral tests.

See [API examples and compatibility notes](docs/UPSTREAM-5.4.1.md).
Local validation: 2547 tests passed, one optional legacy-client test skipped;
Clippy, no-SPI compilation, typing, dependency and security checks passed.
