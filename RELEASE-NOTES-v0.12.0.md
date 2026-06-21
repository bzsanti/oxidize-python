# Release v0.12.0

## Summary

Minor release focused entirely on the bundled **MCP server**: it raises the
Tool Definition Quality of all 12 tools so AI agents (and Glama's Tool
Definition Quality Score) get precise, self-describing tool definitions. No
change to the PDF library API and no upstream bump (`oxidize-pdf` stays at
`=2.16.3`).

Every MCP tool now ships per-parameter descriptions, behavioural annotations,
and a description that states its purpose, when to use it (and the alternative
tool when not), its side effects, and its JSON return shape. Free-form mode
parameters are now typed enums.

## Changed — MCP tool definitions

Reworked the definition of every tool (`read_pdf`, `extract_text`,
`extract_entities`, `convert_pdf`, `analyze_pdf`, `manipulate_pdf`,
`annotate_pdf`, `manage_forms`, `secure_pdf`, `create_pdf`, `add_pdf_content`,
`save_pdf`) along six quality dimensions:

- **Parameter semantics** — every parameter carries an `Annotated[..., Field(
  description=...)]` description: units (PDF points), 0-based page indices,
  bottom-left coordinate origin, defaults, and which parameters apply to which
  mode. Previously the generated schema had no parameter descriptions.
- **Behavioural transparency** — each tool declares MCP `ToolAnnotations`
  (`title`, `readOnlyHint`, `destructiveHint`, `idempotentHint`,
  `openWorldHint=False`), and descriptions now disclose file writes/overwrites,
  session mutation, and the JSON shape returned.
- **Purpose & usage** — descriptions distinguish overlapping tools
  (`extract_text` vs `convert_pdf` vs `extract_entities`; `read_pdf` vs
  `analyze_pdf`) and name the alternative tool for excluded cases.
- **Contextual completeness** — valid modes are enumerated, the
  create→add→save session workflow is documented, and honest limitations are
  stated (`manage_forms` `read` returns text runs rather than AcroForm widgets,
  `validate` enforces a required-only rule, `fill` overlays values; `secure_pdf`
  `encrypt` may drop non-text elements).

### Typed mode parameters (minor behaviour change)

`operation`, `check`, `content_type`, `compliance_level`, `page_size`, and
`annotation_type` are now `Literal` types, surfaced as JSON-schema enums. An
unknown value is now rejected by schema validation (an MCP `ToolError`) before
the tool body runs, instead of returning an `INVALID_*` JSON error body. Valid
inputs are unaffected.

## Tests

- New `tests/mcp_tests/test_tool_definition_quality.py` asserts the wire-level
  schema contract for every tool (non-tautological parameter descriptions,
  annotations with read-only flags, enum-typed mode parameters, sibling
  cross-references).
- The three existing invalid-mode-value tests were migrated to the
  `pytest.raises(ToolError)` pattern to match the new enum validation.
- Full suite green; mypy clean.

## Compatibility

- **Python 3.10+** — tool parameter annotations use `typing.Optional[...]`
  (not PEP 604 `X | None`) inside `Annotated` so that
  `get_type_hints(include_extras=True)` preserves the `Field` metadata on
  Python 3.10 (CPython gh-90353, fixed in 3.11). Verified across the
  3.10–3.13 × ubuntu/macos/windows matrix.

## Breaking Changes

None to the PDF library API. The only behavioural change is stricter,
schema-level validation of MCP tool mode parameters (described above), which
affects only previously-invalid inputs.
