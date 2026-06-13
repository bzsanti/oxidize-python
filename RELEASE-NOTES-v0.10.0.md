# Release v0.10.0

## Summary

Minor release that pulls in upstream `oxidize-pdf` v2.15.0 and exposes its new
incremental form-filling capability in the Python bridge.

Upstream 2.15.0 adds `IncrementalFormFiller`: it fills AcroForm fields on an
**already-serialized** PDF by appending an ISO 32000-1 §7.5.6 incremental update.
The original bytes are preserved verbatim — only the modified field objects and
the `/AcroForm` dictionary are rewritten in a new revision (partial cross-
reference section, chained `/Prev`, regenerated `/ID`), and a form reader
recovers each field's `/V` after re-parsing (upstream #318). The bridge already
filled fields at document-*construction* time (`Document.add_text_field` and the
form-builder surface), but had no way to fill an existing template PDF read from
disk. This release adds that path.

This is a non-breaking, additive change at the API level. Every previously
callable method preserves its signature; the new class is purely additive. The
two upstream text-extraction fixes (#319) are inherited transparently through the
version bump with no bridge API change: a single malformed content-stream
operator no longer discards a whole page (best-effort recovery), and text drawn
inside a Form XObject invoked with `Do` is now extracted — 277 files in the
upstream 9051-PDF corpus recover previously-dropped text.

## Upstream

- **`oxidize-pdf` `=2.14.0` → `=2.15.0`.** Pinned exact equality preserved; the
  feature set is unchanged (`compression, signatures, semantic,
  language-detection`, `default-features = false`).
- Upstream 2.15.0 added `IncrementalFormFiller` and a `PdfReader::trailer()`
  accessor (#318), and fixed text extraction to be best-effort on malformed
  operators and to recurse into Form XObjects (#319).

## Added

### Incremental form filling (`IncrementalFormFiller`)

Fill AcroForm fields on an existing PDF without rewriting it:

- `IncrementalFormFiller(base_bytes: bytes)` — wrap the bytes of an
  already-serialized PDF (e.g. a form template).
- `.fill(field_name: str, value: str) -> bytes` — set one field's `/V` and
  return the updated PDF (base bytes + appended incremental revision).
- `.fill_many(fields: list[tuple[str, str]]) -> bytes` — set several fields in a
  single appended revision. Field names are fully qualified
  (e.g. `"address.street"`); duplicate names collapse to the last value.

Unknown field names raise (`FieldNotFound` surfaces the offending name);
malformed base bytes and encrypted documents raise as well.

## Behavior change inherited from upstream (#319)

Content-stream parsing is now best-effort. `ContentParser.parse` and
`ContentParser.parse_strict` (which share the same tokenizer) no longer raise on
unparseable bytes: they return the operators recovered before the first
unrecoverable byte. Pure garbage yields an empty list; a valid prefix followed by
garbage preserves the valid operators. `parse_strict` is retained as a
compatible alias of `parse` — upstream exposes no separate strict mode.

## Compatibility

Fully backward compatible. The full suite is **2058 passing** (single run,
`mcp_tests` excluded). New coverage: 7 tests for `IncrementalFormFiller` (the
verbatim-preservation contract, `/V (value)` written into the appended revision,
the second cross-reference section, multi-field fill in one revision, and the
unknown-field / malformed-bytes error paths); the content-parser suite was
updated to the best-effort contract (empty list on garbage, valid prefix
preserved before an unrecoverable tail). `mypy` and
`cargo clippy --all-targets -D warnings` are clean.
