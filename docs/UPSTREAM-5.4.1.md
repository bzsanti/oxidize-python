# Upstream 5.4.1 integration

Base: published Python 0.20.1 (core 5.1.5), incorporated from origin/main.
Registry artifact 5.4.1 verified against the official sparse index SHA-256:
`83753fe3fe16dba14fd86408772934231c60ba9e922a63d2b263b3394616c7de`.

| Requirement | Evidence/status | Blocker / next action |
| --- | --- | --- |
| Pin latest published upstream | Verified artifact; exact manifest/lock pin; default and no-SPI builds pass | Closed |
| Connect new application APIs since 5.1.5 | Recovery, normalization, effective version, build identification and signature slot lifecycle exported and typed | Closed; 19 focused behavioral cases pass |
| Preserve contracts and type information | Type3 compatibility correction; complete suite, typing, Clippy, dependency and security checks pass | Closed |

The earlier backlog in UPSTREAM-5.1.3.md remains separate: existing-document
operations, CMS signing, OCR, annotation/tagged editors and semantic redaction
predate this update. New low-level font internals and writer configuration for
unexposed incremental writers do not introduce Python entry points here. Signature
slots provide preparation and handwriting, not cryptographic signing. No MCP
tool schema change is needed to expose the Python APIs.

## Python APIs

```python
from oxidize_pdf import ExtractionOptions, PdfReader

reader = PdfReader.open("document.pdf")
print(reader.version, reader.effective_version)  # header vs catalog override
options = ExtractionOptions(
    preserve_layout=True,  # retain positional fragments
    normalize_non_breaking_spaces=True,  # U+00A0/U+202F -> U+0020; default False
    max_extracted_bytes=1_000_000,
)
result = reader.extract_page_text_with_recovery(
    0, max_stream_bytes=8_000_000, options=options,
)
print(result.text.text, result.text.truncated)
for diagnostic in result.diagnostics:
    print(diagnostic.location, diagnostic.action, diagnostic.kind, diagnostic.error)
```

`extract_text_with_recovery(max_stream_bytes=..., options=...)` returns one
`RecoveredText` per page. The required bound limits each decoded content/Form
stream, including operators; `max_extracted_bytes` independently bounds emitted
text per page. Limits and predictor errors still raise `PdfParseError`. Ordinary
extraction remains strict even with lenient parse options. Recovery must be
explicit; text may be incomplete, unverified, or empty because a stream was omitted.
Empty diagnostics mean no Flate recovery was needed, not full PDF validation.

`TextRecoveryDiagnostic` retains `location` (`page_contents` or `form_xobject`),
`contents_index`, `form_name`, `object_id`, `action` (`recovered` or `omitted`),
`filter_index`, `kind` (`unverified` or `incomplete`) and the original `error`.
Fields which do not apply are `None`.

```python
from oxidize_pdf import (
    BuildIdentification, Document, create_signature_slot, read_signature_slot,
    draw_signature_slot, complete_signature_slot, list_signature_slots,
    remove_signature_slot,
)

doc = Document()
doc.set_build_identification(BuildIdentification.Disabled)
assert doc.build_identification == BuildIdentification.Disabled

# Each edit returns bytes retaining the complete original prefix.
prepared = create_signature_slot(
    source_bytes, "Signer-1", 0, (50.0, 50.0, 250.0, 150.0), metadata="Participant",
)
reviewed = draw_signature_slot(
    prepared, "Signer-1", [[(0.1, 0.2), (0.9, 0.8)]], label="Reviewed",
)
completed = complete_signature_slot(reviewed, "Signer-1", [[(0.1, 0.2), (0.9, 0.8)]])
slot = read_signature_slot(completed, "Signer-1")
assert slot.completed and not slot.digitally_signed
```

Build identification is enabled by default; disabling it omits the three generated
build/edition/features Info entries while leaving Creator/Producer policies alone.
Signature rectangles use `(left, bottom, right, top)` PDF coordinates; strokes use
normalized coordinates in `[0,1]`. Names allow 1–128 ASCII alphanumeric/hyphen
bytes; metadata is capped at 4096 UTF-8 bytes. The core enforces page bounds,
100 slots, 1000 strokes, 20000 points and certification/field policies. Errors
raise `PdfError`; no files are written. `draw_signature_slot` defaults to
`complete=False`; `complete_signature_slot` defaults to `complete=True`.
Completed slots cannot be redrawn or removed. `digitally_signed` indicates a
non-null signature value, not successful CMS verification. This API does not
supply a private key, CMS signing or cryptographic identity verification.

## Compatibility and scope

The lockfile changes only the core version and checksum; transitive versions
remain unchanged. Existing parser, encoding, xref and incremental-writer fixes
are inherited. New recovery is explicit because lenient flags no longer imply
unverified Flate success. The release's low-level `RecoveredStream` decoder
requires native PDF dictionaries/streams, which this bridge does not expose;
the public recovery integration is at the page/document text boundary.
The new font parser internals and tagged-editor preflight remain with their
unexposed parent APIs in the earlier backlog. No package release was published.

## Compatibility correction and validation (2026-10-08)

The initial regression exposed a Type3 change: core `ResolvedFontResource.differences`
now includes base-encoding names. Python continues to return only explicitly
specified `/Differences`; its decoder retains the complete core mapping. The
existing glyph-program test caught this, and a new test proves that an explicit
override matching its base glyph is preserved too. This is a required compatibility
fix, not a change to the previous Python contract.

Validated on Linux x86_64 / Python 3.12:

- `maturin develop --locked --offline`: built and installed the current bindings.
- `pytest tests/ -q`: **2547 passed, 1 skipped**. The full suite was run outside
  the sandbox for MCP transports. Log: `/tmp/oxidize-python-541-tests.log`.
- Focused new APIs and Type3 compatibility: **23 passed**. Tests distinguish
  verified/unverified/incomplete/omitted recovery, Form locations, stream/text
  limits, strict extraction after recovery, NBSP text/fragments, effective PDF
  version, serialized identification and immutable/completed signature slots.
  Invalid inputs, duplicate names, encrypted inputs and malformed certification
  policies are rejected.
- `cargo clippy --locked --offline --all-targets -- -D warnings`: passed.
- `cargo check --locked --offline --no-default-features`: passed.
- `mypy python/oxidize_pdf/`: passed, 24 source files. Strict consumers for
  extraction, MCP and upstream 5.4 passed, including Python 3.10 for the new API.
  The new consumer is included in CI.
- `scripts/check_parity.py`: passed, 396 exports; `git diff --check`: passed.
- Native-dependency gate: passed with the exact manifest/lock and source copied
  to `/tmp/oxidize-python-541-native-check`; the working checkout contains `.venv`
  and an installed extension, which the scanner otherwise mistakes for product
  sources. All transitive versions are unchanged from the approved 0.20.1 graph.
- Kripteia test quality: 100/100 on both affected test files; security scan of
  `src/`: no findings. JSON evidence: `/tmp/oxidize-python-541-test-quality.json`,
  `/tmp/oxidize-python-541-font-test-quality.json`,
  `/tmp/oxidize-python-541-security.json`. The telemetry database was read-only;
  the analyses themselves completed successfully.
- New Rust module passes rustfmt. Global pre-existing formatting differences
  were not reformatted as part of this update.

The local MCP installation was updated to the declared dependencies (FastMCP
4.0.11 and SDK/types 2.3.0). Reinstalling FastMCP/slim repaired shared files removed
when uninstalling version 3. The unrelated preinstalled `openai-agents 0.17.7`
requires MCP <2 and is incompatible with this project's MCP extra; it is not a
project dependency and was not removed. No product dependency ranges changed.
Cross-platform wheel validation remains for CI; no release/commit/push was made.
Pre-existing MCP tracking documents and untracked handoffs/uv.lock were preserved.

## Release 0.21.0

User authorized publication of the next version. Minor version 0.21.0 includes
new additive Python APIs. Acceptance: coherent package/lock versions; reviewed
changes committed without unrelated local tracking files; green CI on release
PR; main tag; five wheels and sdist on PyPI; GitHub release and MCP registry refresh.
Status: version and notes prepared; remote CI/publication pending.
