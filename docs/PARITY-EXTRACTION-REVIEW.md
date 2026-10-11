# Composed extraction policies — Rust 5.4.2

## Scope

ExtractionOptions now exposes all core fields plus all five public extractor
builder policies. New keyword-only options are reorder_columns, reading_order
and a typed CarriageReturnHandling enum. Existing positional arguments/defaults
are unchanged. The shared extractor constructor is used by whole-document,
page, fragment and bounded recovery methods. Core retains ownership of policy
precedence: reading order applies only to flat text without column reordering;
fragments are returned only with preserve_layout.

## Evidence and corrected test assumptions

2605 tests pass, one preexisting skip. Twelve focused cases (six extraction,
five parity-gate mutations and runtime contract) pass. Strict typed consumer
passes. Clippy passes with warnings denied. A compiled mutation ignoring the
three policies produces five assertion failures; sources/binaries restored and
full regression passes. Full suite uses local MCP IPC outside the sandbox.

Independent handcrafted PDF syntax supplies explicit ToUnicode mappings for CR
and LF. Tests distinguish all three policies in normal and recovered output,
fragments, text budgets including zero, and column/reading-order behavior.
The initial test assumed fragments on the flat path and column clustering across
separate reading regions. Inspection of core corrected those assumptions: use
preserve_layout for fragment assertions and interleaved column rows for the
column-clustering contract. Expected CR semantics are unchanged.

## Test quality and security review

Kripteia Python: 96, 2488 discovered tests / 116 files. Runtime parametrized count
is higher. Rust scanner finds no native tests and no security issues; actual
compiled bridge is exercised through Python. Python security reports only the
preexisting synthetic SECRET fixture in test_security.py.

Manual review verifies exhaustive enum conversion, unchanged defaults, full
ExtractionOptions literal (no silently defaulted field), immutable borrowed
configuration across GIL-detached execution and identical shared constructor
use in normal/recovery paths. No unsafe code or new I/O introduced. Error
mapping remains the existing parser mapping. No unresolved finding in scope.

The public/stub exports, constructor parameters, properties and required tests
are enforced by docs/parity-contract.json. This contract is still partial;
remaining Rust capabilities and parser-result audit stay in #244. No global
parity percentage is asserted. Platform CI pending at commit preparation.
