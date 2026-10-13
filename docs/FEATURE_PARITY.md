# Current parity target — Rust 5.4.2

The bridge target is **all functional capabilities of Rust**, including options,
results and errors. Pinning the same core version is not proof of API parity.
Tracking: [#244](https://github.com/bzsanti/oxidize-python/issues/244), coordinated
by [core #710](https://github.com/bzsanti/oxidizePdf/issues/710).

| Capability | Current status |
| --- | --- |
| Existing-document merge/extract/split with explicit preservation policies and complete plans | Integrated in develop via #245; 26 CI checks passed |
| Atomic lossless page mutations (move/rotate/delete/duplicate/insert) | Integrated in develop via #245; 26 CI checks passed |
| CMS preparation and completion | Integrated in develop via #246; 26 CI checks passed |
| Composed extraction policies (CR, reading order, column reordering) | Integrated in develop via #248; 26 CI checks passed |
| Incremental FreeText editor (read/add/update/remove, all fields) | Integrated via #249; 26 CI checks passed |
| Incremental Ink editor (read/add/update/remove, all fields) | Implemented and locally validated; CI pending |
| Incremental notes/highlights | Candidate bindings blocked on upstream DocMDP fix [core #712](https://github.com/bzsanti/oxidizePdf/issues/712); not exported |
| Other incremental annotation/tagged/OCR editors, security redaction, revision-aware comparison | Missing bindings; required for full parity |
| Recovery diagnostics, NBSP normalization, signature slots, batch/streaming, experimental SPI | Bindings exist; complete option/result audit pending |
| Generation, parsing, graphics, forms, layout, AI and remaining public Rust API | Bindings exist in part; complete functional audit pending |
| Tesseract recognition and optional production features | Full exposure pending |

`docs/parity-contract.json` records the first audited API contract. CI tests each
callable parameter and result property and runs the named behavioral tests. Its
scope is explicitly partial. No global coverage percentage is currently valid.
A Rust limitation remains a Rust limitation: preserving edits that require
remapping the base document's page labels are rejected by core 5.4.2.

## Historical matrix (not a current completeness claim)

# Feature Parity — oxidize-python

Bridge version: 0.19.0
Core dependency: =5.1.3
Last upstream review: 2026-09-24

The original feature inventory below is not a complete inventory of core 5.x.
See the [5.1.3 integration review](UPSTREAM-5.1.3.md) for newly integrated
extraction APIs and prioritized gaps in preservation, editing and signing.

Reference: [API Surface definition](lifecycle/API_SURFACE.md)

Status values:
- `yes` — fully implemented and tested
- `partial` — implemented but with known gaps (see Notes)
- `no` — not yet implemented
- `n/a` — not applicable to this runtime

---

## DOC — Document creation

| Feature ID | Feature Name | Python |
|---|---|---|
| DOC-001 | Create empty document | yes |
| DOC-002 | Set document metadata | yes |
| DOC-003 | Add pages | yes |
| DOC-004 | Save to file | yes |
| DOC-005 | Save to bytes | yes |
| DOC-006 | Encrypt (RC4-128) | yes |
| DOC-007 | Permissions | yes |

## PAGE — Page creation

| Feature ID | Feature Name | Python |
|---|---|---|
| PAGE-001 | Arbitrary dimensions | yes |
| PAGE-002 | Standard presets | yes |
| PAGE-003 | Margins | yes |

## TXT — Text operations

| Feature ID | Feature Name | Python |
|---|---|---|
| TXT-001 | Standard fonts | yes |
| TXT-002 | Custom/embedded fonts | yes |
| TXT-003 | Text color | yes |
| TXT-004 | Character spacing | yes |
| TXT-005 | Word spacing | yes |
| TXT-006 | Line leading | yes |
| TXT-007 | Text at position | yes |
| TXT-008 | Text alignment | yes |

## GFX — Graphics operations

| Feature ID | Feature Name | Python |
|---|---|---|
| GFX-001 | Color spaces | yes |
| GFX-002 | Fill color | yes |
| GFX-003 | Stroke color | yes |
| GFX-004 | Line width | yes |
| GFX-005 | Fill opacity | yes |
| GFX-006 | Stroke opacity | yes |
| GFX-007 | Rectangle | yes |
| GFX-008 | Circle | yes |
| GFX-009 | Arbitrary paths | yes |
| GFX-010 | Fill | yes |
| GFX-011 | Stroke | yes |
| GFX-012 | Fill-and-stroke | yes |
| GFX-013 | Image embedding | yes |

## PARSE — PDF parsing

| Feature ID | Feature Name | Python |
|---|---|---|
| PARSE-001 | Open from file path | yes |
| PARSE-002 | Open from bytes | yes |
| PARSE-003 | Is-encrypted | yes |
| PARSE-004 | Unlock with password | yes |
| PARSE-005 | Page count | yes |
| PARSE-006 | PDF version | yes |
| PARSE-007 | Parsed page dimensions | yes |
| PARSE-008 | Extract text single page | yes |
| PARSE-009 | Extract text all pages | yes |
| PARSE-010 | Text chunking | yes |

## OPS — Document operations

| Feature ID | Feature Name | Python |
|---|---|---|
| OPS-001 | Split to files | yes |
| OPS-002 | Merge from files | yes |
| OPS-003 | Rotate all pages | yes |
| OPS-004 | Extract pages | yes |
| OPS-005 | Overlay/watermark | yes |
| OPS-006 | Page reordering | yes |

## ERR — Error model

| Feature ID | Feature Name | Python |
|---|---|---|
| ERR-001 | Base PdfError | yes |
| ERR-002 | PdfParseError | yes |
| ERR-003 | PdfIoError | yes |
| ERR-004 | PdfEncryptionError | yes |
| ERR-005 | PdfPermissionError | yes |

---

## Scope of this document

This table covers the **core PDF generation, parsing, and operations surface** that the ecosystem-wide parity framework tracks across bridges (Python, .NET, WASM). The Python bridge also exposes a larger feature set not represented in this core surface — tables, charts, dashboards, annotations (deep), forms (deep), AI/ML pipeline (`DocumentChunker`, `MarkdownExporter`, `RagChunk`), signatures, PDF/A validation, XMP metadata, templates, MCP server. Those live in the internal TDD plan (`.private/tdd-plan-full.md`) and in the `_oxidize_pdf.pyi` type stub.

## Known gaps

- **OCR**: the Rust core exposes a Tesseract-backed OCR provider (`oxidize-pdf-core/src/text/ocr/`), but it is **not wrapped in the Python bridge** yet. This is the main user-facing gap for scanned-PDF pipelines.
- **OPS-001**: `split_pdf` uses a hardcoded `page_{n}.pdf` naming pattern. The core may support custom patterns — check if this should be exposed.

## Incremento activo — #260 (2026-10-13)

Por decisión del usuario, #253 queda pendiente de una publicación del core con
el arreglo AES (el índice oficial sigue en 5.4.2); no se cambia el pin a Git ni
se inicia una publicación upstream. Se implementa #260 en el bridge actual.

| Requisito | Estado final | Evidencia de cierre |
| --- | --- | --- |
| PartitionConfig aplicable y completo | Demostrado | Los nueve campos llegan al core; tablas, headers y umbral de títulos cambian la clasificación |
| Grafo de elementos | Demostrado | Relaciones padre/hijo y anterior/siguiente conservadas; índices fuera de rango devuelven excepciones Python |
| Conteo de tokens propio | Demostrado | Callback controla división y estimaciones, incluso conteos no aditivos; primera excepción preservada y sin resultado parcial |
| Exportaciones documentales | Demostrado | JSON documental y Markdown con contenido esperado; documentos bloqueados conservan errores |
| Contrato de distribución | Demostrado localmente | Stubs, consumidor estricto, contrato por miembro, regresión y mutación discriminante |

### Uso del bridge

```python
from oxidize_pdf import HybridChunkConfig, PartitionConfig, PdfReader

reader = PdfReader.open("documento.pdf")
elements, graph = reader.partition_graph(PartitionConfig(detect_tables=False))
chunks = reader.rag_chunks_with_counter(
    HybridChunkConfig(max_tokens=128),
    lambda text: len(text.encode("utf-8")),  # presupuesto en bytes en este ejemplo
)
json_document = reader.to_json()
markdown = reader.to_element_markdown()
```

El contador recibe el texto completo que debe medir y devuelve un entero no
negativo representable por `usize`; `bool` no es válido. Se trata como no aditivo
para respetar tokenizadores cuyo conteo cambia al unir textos. Sus excepciones se
propagan sin sustituirlas; el reader puede reutilizarse tras el error. El callback
no debe volver a llamar al mismo reader mientras este está prestado por PyO3.
`overlap_tokens` se conserva como campo del core, pero 5.4.2 lo reserva y no
implementa solapamiento. Un fragmento indivisible puede exceder el presupuesto y
se identifica mediante `is_oversized`, conforme al contrato upstream.

### Resumen ejecutivo de revisión

Implementación y revisión local de #260 sobre `f7bfe53` más el diff actual, con
core publicado 5.4.2 sin cambios de dependencias. Se revisaron los 12 archivos de
código, tests, tipos y distribución afectados. El adaptador Python/Rust conserva
la configuración, los índices del grafo y los errores. La revisión no constituye
publicación ni integración remota.

### Contratos y evidencia

Los PDFs de aceptación se escriben manualmente: sus textos, coordenadas y tablas
no se generan usando el productor que se está probando. El recorrido ejecutado
es Python → PyO3 → PdfDocument del core real. Los tests cubren los siete nuevos
métodos, todos los campos configurables, perfiles no predeterminados, grafo vacío,
índices inválidos, documentos bloqueados, callbacks inválidos y reentrada.

[RED](evidence/issue-260/red.log): 21 casos fallan en la API inicial ausente.
[GREEN](evidence/issue-260/focused.log): 23 casos nuevos y seis comprobaciones de
contrato pasan. En una copia desechable se sustituyeron la configuración por la
predeterminada y el contador personalizado por el del core: los cinco tests
seleccionados fallaron por clasificación, presupuesto y excepción incorrectos,
no por montaje ([mutación](evidence/issue-260/mutation.log)). La copia cargó su
propia extensión, sin instalarla en el entorno principal.

La revisión manual verificó el límite `usize`, rechazo de booleanos, conservación
de la primera excepción, ausencia de mutex retenido durante callbacks y descarte
del resultado tras un error. La iteración nativa es finita aunque el adaptador
infallible del core devuelva cero después del primer error. Los accesos al grafo
comprueban límites antes de indexar. La protección de préstamos de PyO3 rechaza
reentrada al reader, y se verifica que luego puede reutilizarse.

### Hallazgos

No quedan incumplimientos detectados de los criterios de #260. Los otros trece
hallazgos conservan sus issues: #253 requiere una publicación del core y mantiene
su consecuencia de seguridad; #265 conserva los huecos de tipado ajenos a RAG.
La ausencia de solapamiento en 5.4.2 se documenta como limitación upstream; este
incremento no promete implementar algoritmos adicionales del core.

### Calidad de Tests (Kripteia)

[Análisis Python](evidence/issue-260/kripteia-python.log): 100/100, 13 funciones
en un archivo (23 casos pytest); ningún infractor señalado. El análisis Rust
en `src` detecta cero tests Rust: no aporta evidencia conductual. El score se
complementa con fixtures independientes, RED/GREEN y mutación real.

### Análisis de Seguridad (Kripteia Security)

Los análisis de [Rust](evidence/issue-260/kripteia-rust.log) y Python no detectan
problemas en el alcance escaneado. Ambos avisan de telemetría no escribible; los
análisis sí terminan. Se revisaron manualmente las fronteras de callbacks, errores
e índices. Este resultado no elimina el hallazgo AES #253 del core dependiente.

### Métricas y estado de entrega

- 12 archivos revisados de implementación, tipos, tests y distribución; cero
  archivos de producto modificados como consecuencia de hallazgos de la revisión.
- Regresión: [2.362 pruebas de biblioteca](evidence/issue-260/regression.log) y
  [295 MCP, un skip](evidence/issue-260/mcp.log).
- [Mypy](evidence/issue-260/typing.log): 24 archivos del paquete y ocho consumidores
  estrictos; consumidor nuevo también verificado para Python 3.10.
- Clippy con warnings prohibidos, build sin features predeterminadas y contrato
  de paridad ejecutados; resultados y hashes en
  [validation.json](evidence/issue-260/validation.json).
- Bloqueantes locales de #260: ninguno. Pendiente de integración/publicación;
  la issue remota permanece abierta. Siguiente acción: revisar e integrar el diff.
