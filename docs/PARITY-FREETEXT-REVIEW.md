# Incremental FreeText parity — Rust 5.4.2

## Scope and validation

Expose IncrementalFreeTextEditor and typed identity, result, mutation and alignment
classes. Every core add/update/remove field and result member is represented.
The editor owns an immutable snapshot, releases the GIL for core work and returns
new bytes plus the complete current annotation set. No output file is written.
Previous bytes remain an exact prefix of each nonempty successful revision.
Core validation and its typed error mapping are retained.

Full regression: 2612 pass, one preexisting skip. After adding four invalid-batch
cases, 17 focused tests pass. Strict typing and Clippy pass. The compiled mutation
that replaces submitted batches with empty ones produces six failures (lifecycle,
invalid identity and certification denial); restoration passes. Independent PDF
fixtures test all alignments, appearance strings, geometry, identity preservation,
page and result fields, add/update/remove and immutable error recovery.

Certification tests use the existing signed P2 fixture from oxidize-pdf-dotnet;
P1/P3 variants replace one byte and intentionally invalidate that fixture's
cryptographic signature. These cases test permission interpretation only, not
signature authenticity. Unmodified P2 rejects edits. Signing interoperability is
covered by the separate CMS contract.

## Security finding and boundary

Candidate note/highlight bindings exposed an upstream defect: Rust 5.4.2 omits
DocMDP checks for those two editors. Core issue #712 records reproduction and
correction work. Its policy validator is crate-private, so a direct bridge call
fails compilation. Do not copy the signature-policy parser into each binding.
Those candidate APIs are NOT exported in this increment. FreeText already calls
the core policy validator and rejects P1/P2 while allowing P3. Full parity #244
remains open and notes/highlights depend on the fixed upstream dependency.

## Quality and security review

Kripteia Python: 96, 2491 AST tests / 117 files before the last four parametrized
cases. Rust scanner finds zero Rust unit tests and no security issues; Python
executes the compiled bridge. The only Python security hit is the existing
synthetic SECRET string in test_security.py.

Manual review confirms exhaustive enum conversion, fixed-size geometry parsing,
owned snapshot/mutations across GIL detachment, cloned immutable results, no unsafe
code and errors routed through the shared PdfError conversion (including permission
and parse subclasses). Invalid batches are checked against independently expected
failure, preserve the snapshot and permit a subsequent valid operation. The
per-member parity gate and strict typed consumer protect signatures/results.
No unresolved finding inside the published FreeText scope. Platform CI pending.

Evidence: docs/evidence/parity-freetext. Remaining functionality is tracked by
#244 and coordinated by core #710; no global completeness percentage is asserted.
