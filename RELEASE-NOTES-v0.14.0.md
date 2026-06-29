# Release v0.14.0

## Summary

Hardens the built-in MCP server against denial-of-service from a single large
or malicious PDF (issue #115), and bumps the bundled `oxidize-pdf` core from
`=3.0.1` to `=3.0.4`. The core bump makes `PdfDocument` `Send`, which lets the
bridge release the GIL during heavy PDF work — so a multi-client MCP deployment
now runs concurrent operations in parallel instead of serializing on one core.

Also documents first-class use from **GitHub Copilot** and the **OpenAI Agents
SDK**.

No breaking change to the existing Python API. All new limits are configurable
and ship with generous defaults.

## Added — MCP resource caps (issue #115)

Configurable limits, enforced before any heavy work, returning an error with
code `RESOURCE_LIMIT`:

- `OXIDIZE_MAX_PAGES` (default 10000) — documents with more pages are rejected
  before extraction begins.
- `OXIDIZE_MAX_OUTPUT_BYTES` (default 10 MB) — caps the serialized size of a
  tool's JSON response.
- `OXIDIZE_MAX_SESSION_BYTES` (default 10 MB) — bounds the content a single
  stateful PDF-creation session may accumulate.

The page-count gate and output cap apply to `extract_text`, `read_pdf`,
`extract_entities`, and `convert_pdf`. `get_session_store` now honours
`OXIDIZE_MAX_SESSIONS` (previously a hardcoded 100).

## Added — GIL release for concurrent PDF work (issue #115)

Heavy Rust operations now run inside `Python::detach`, releasing the GIL so
concurrent MCP calls execute in parallel:

- Standalone path/bytes ops: `validate_pdf`, `compare_pdfs`,
  `detect_pdf_corruption`, `PdfAValidator.validate_bytes`, `split_pdf`,
  `merge_pdfs`.
- `PdfReader` extract/chunk methods: `extract_text`, `extract_text_from_page`,
  `extract_text_chunks`, `metadata`, `get_page`, `to_markdown`, `to_contextual`,
  `chunk`, `chunk_page`, `partition`, `rag_chunks` (and the `_with_profile` /
  `_with_source` / `_with_source_and_config` variants),
  `extract_text_with_options`, `extract_fragments_with_options`,
  `extract_fragments_from_page`, `extract_plain_text`,
  `extract_plain_text_lines`, `get_page_content_streams`.

`rag_chunks_with_pipeline` is intentionally left GIL-held (it runs a
user-supplied analysis pipeline that may re-enter Python).

## Added — Copilot & OpenAI Agents SDK integration

- README: `.vscode/mcp.json` configuration for GitHub Copilot agent mode and an
  OpenAI Agents SDK (`MCPServerStdio`) snippet.
- `examples/openai_agents_quickstart.py` — runnable example that connects to the
  `oxidize-mcp` server over stdio and exposes the 12 tools to an agent.

## Changed — upstream bump to `oxidize-pdf` 3.0.4

Picks up the core change that makes `PdfDocument` `Send`
(`Rc<ResourceManager>` → `Arc`, `RefCell` → `Mutex`), required to release the
GIL in the reader methods.

## Security

Mitigates MCP DoS (premortem scenario): a crafted PDF (huge page tree,
unbounded extraction output, or session-content flood) is now rejected at the
gate or bounded, and GIL release prevents one heavy request from freezing all
concurrent sessions.
