# Incremental Ink parity — Rust 5.4.2

## Scope and evidence

Typed InkColorSpace, InkColor, InkStroke, InkId, Ink, InkMutation, InkUpdate and
IncrementalInkEditor expose all read/add/update/remove inputs and outputs. Core
constructors validate color, strokes, width and opacity; core apply validates
page bounds, batch consistency and certification permissions. Original Gray,
RGB or CMYK is retained, rather than converting every color to RGB. Single-point
strokes are valid in Rust and remain supported. The editor owns an immutable
snapshot and returns complete current annotations plus new bytes.

2634 tests pass, one existing skip. Twenty-four focused cases pass. Strict typed
consumer, Clippy with warnings denied and new-module rustfmt pass. A compiled
mutation replacing caller width with 1.0 is rejected by eight tests, including
invalid-width rejection and update semantics; restored regression passes.

Fixtures use hand-authored PDF syntax and assert prefix/revision preservation,
independent expected geometry, page count, stable identity, every style/color
component, nullable opacity, add/update/remove, invalid atomic batches and
subsequent successful retry. The signed P2 fixture rejects changes unmodified;
P1/P3 variants intentionally change a byte to test policy interpretation, not
cryptographic authenticity. P3 remains allowed and no-op returns identical bytes.

## Quality and security review

Kripteia Python: 96, 2497 AST tests / 118 files. Rust scanner finds no native tests
and no security issues; behavioral tests execute the compiled binding. Python's
only secret hit remains the preexisting synthetic SECRET test string.

Manual review traces exhaustive three-color conversion, validated constructor
paths, fixed integer bounds, cloned input points and immutable owned data across
GIL detachment, output copying and shared typed error mapping. No new unsafe,
private-key handling, file I/O or publication path. Core's existing Ink permission
gate remains in force and is exercised for all three certification levels.

No unresolved finding in this increment. Notes/highlights remain separately
blocked on core #712. The per-member contract and strict consumer are in CI;
platform CI pending at preparation. Full Rust parity remains tracked by #244.
Evidence: docs/evidence/parity-ink.
