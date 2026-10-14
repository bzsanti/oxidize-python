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
- Bloqueantes de #260: ninguno. Integrada en develop mediante PR #267
  (`0a3c4c1`), con 26 checks aprobados. Pendiente de una futura publicación.

## Incremento #254 / #255 — 2026-10-14

Base: `0a3c4c1` (PR #267 integrada), core 5.4.2. Se reemplaza el adaptador
Python al PageStreamer ficticio por el parser real del core publicado.
No se modifica la dependencia ni el repositorio Rust. La clase nativa de
streaming upstream sigue siendo un stub; este cambio deja de utilizarla.
La paridad global #244 y las opciones de streaming #258 siguen pendientes.

### Resumen ejecutivo

El iterador Python entrega páginas con texto y geometría reales, valida el
archivo al abrirlo y conserva errores tipados. Los ocho tests anteriores que
aceptaban el stub se sustituyen por 15 casos con PDFs escritos manualmente.
Se conserva la API existente y se añade cierre explícito/context manager.
`total_pages()` ahora devuelve siempre el número real; `seek_to_page(n)` acepta
índices entre cero y el total incluido (EOF), y rechaza los superiores.
Los documentos cifrados se rechazan explícitamente; para desbloquearlos debe
usarse PdfReader. Los fallos de extracción ocurren en `next()`, que no avanza
el cursor cuando falla. `extract_text_streaming()` devuelve la instantánea ya
extraída, sin lecturas adicionales.

### Contratos y evidencia

| Requisito | Estado | Evidencia |
| --- | --- | --- |
| Páginas, dimensiones y texto reales (#254) | Demostrado | Fixture 321×456, sentinel exacto y comparación con PdfReader; Flate, 0/1/2/5 páginas, EOF repetido |
| Geometría y navegación (#254) | Demostrado | MediaBox heredado con origen no nulo, rotación 90°, seek hacia atrás y EOF, rechazo sin mover cursor |
| Entrada inválida y errores (#254) | Demostrado | PDF inválido/truncado, fichero ausente, cifrado y stream corrupto; reintento falla en la misma página |
| Recursos (#254) | Demostrado para el contrato descrito | Parser local a cada next, sin cachés retenidas; página dañada posterior no se decodifica antes de seleccionarla; close/context manager y páginas conservadas |
| Tests discriminantes (#255) | Demostrado | Dos fallos por cero páginas y dos por texto fijo en extensión mutada aislada |
| Distribución y tipado | Demostrado localmente | Stubs, consumidor estricto en CI y contrato de miembros; CI remota pendiente |

El recorrido probado es Python → PyO3 → PdfDocument/TextExtractor reales.
Los fixtures declaran bytes PDF, coordenadas y sentinels independientemente del
productor. [RED](evidence/issue-254-255/red.log) registra el comportamiento inicial;
[GREEN](evidence/issue-254-255/focused.log) registra los 76 casos focalizados.
[Mutación](evidence/issue-254-255/mutation.json): una copia compilada aislada devuelve
cero páginas o texto fijo. Se verificó la ruta de su extensión; los cuatro fallos
son aserciones conductuales, no fallos de montaje. El código de producto no se
mutó para ejecutar esa prueba.

### Contrato de recursos y uso

```python
from oxidize_pdf import PageStreamer

with PageStreamer.open("documento.pdf") as stream:
    while (page := stream.next()) is not None:
        print(page.number, page.media_box(), page.extract_text_streaming())
```

Se mantiene un descriptor del archivo fuente, que debe permanecer sin cambios
mientras se usa. Cada `next()` duplica temporalmente ese descriptor, reconstruye
el índice y extrae solo la página seleccionada. Al terminar o fallar, libera el
parser, su descriptor y todas sus cachés. No se acumulan cachés entre páginas;
las páginas que retiene el llamante sí ocupan su propio texto y geometría.
La memoria depende del índice, recursos y contenido decodificado de la página:
no hay una cota numérica ni garantía de memoria constante. La reconstrucción del
índice por página añade coste de CPU/lectura; no se hace una afirmación de mejora
de rendimiento. Es una alternativa funcional al stub publicado, no una
implementación de lectura secuencial de bytes sin seek.

`close()` es idempotente; leer, buscar o entrar en un contexto cerrado falla con
ValueError. El conteo sigue disponible y las páginas ya entregadas siguen siendo
válidas. El context manager cierra incluso ante una excepción del llamante.
El fichero también se libera al destruir el iterador. No se ofrece autenticación,
OCR ni la configuración pendiente de #258.

### Hallazgos

No se detectan bloqueantes nuevos en el adaptador Python. Se inspeccionaron
propiedad de descriptores, préstamos PyO3 durante GIL liberado, propagación de
errores, EOF, overflow y actualización del cursor solo tras éxito. El parser se
construye dentro de la operación; no quedan referencias a sus datos en las páginas.
El coste de reconstrucción del índice y los límites upstream quedan declarados
arriba. El problema AES #253 sigue pendiente y no queda cubierto por estos scans.

### Calidad de Tests (Kripteia)

[Python](evidence/issue-254-255/kripteia-python.log): 100/100, nueve funciones,
un archivo (15 casos parametrizados), sin infractores señalados. El análisis
Rust encuentra cero tests en src: no representa cobertura. La evidencia
conductual procede de pytest con extensión real y de las mutaciones descritas.

### Análisis de Seguridad (Kripteia Security)

Los scans de [Rust](evidence/issue-254-255/kripteia-rust.log) y del archivo Python
no detectan problemas. Se revisaron manualmente lectura de archivos, errores,
vida de recursos y ausencia de datos inventados tras fallos. No se auditó de nuevo
todo el parser dependiente ni se certifican límites contra PDFs adversarios.

### Métricas y entrega

- Diez archivos de código, tipos, tests, contrato y CI revisados; seguimiento en
  este documento. Sin cambios de producto adicionales por hallazgos de la revisión.
- Regresión de biblioteca: 2.369 pruebas aprobadas; MCP: 295 aprobadas, un skip.
  El primer intento MCP se interrumpió por bloqueo IPC del sandbox; la ejecución
  fuera del sandbox pasó. La restauración tras mutación detectó un artefacto de
  Cargo reutilizado; se forzó recompilación y se repitió la regresión final.
- Build, Clippy con warnings prohibidos, compilación mínima, mypy de 24 archivos
  y consumidor estricto pasan; contrato parcial aprobado, 442 exports.
- Evidencias en `docs/evidence/issue-254-255/`; estado final y hashes en validation.json.
- Implementación y aceptación local terminadas. Integración, CI remota y
  publicación son estados separados; no se declara cerrada la paridad global.

## Incremento #256 — 2026-10-14

Base: `25bb005`, PR #268 integrada con 26 checks aprobados. #254/#255 tienen su
implementación integrada; todavía no se ha publicado una versión nueva.

### Resumen ejecutivo

El bridge conserva los payloads de las siete variantes de ParseEvent. Se añaden
`data`, `object`, `entries` y `dict` manteniendo los campos existentes, incluidos
`data_len` y `entry_count`. Los eventos siguen siendo diccionarios Python.
`PdfValue` añade las propiedades de lectura `kind` y `value`; sus constructores
y usos en firma se conservan. No se modifica el core 5.4.2 ni su algoritmo.

### Contratos y evidencia

| Requisito | Estado | Evidencia |
| --- | --- | --- |
| Bytes de StreamData y compatibilidad | Demostrado | Feed real con payload exacto, data_len y object_id; prueba nativa con NUL, espacios, newline y bytes no UTF-8 |
| ObjectEnd completo | Demostrado | Feed conserva Null upstream; prueba del conversor con objeto entero no nulo, id y generation |
| XRef y Trailer | Demostrado en el conversor | Eventos Rust sintéticos con entradas no vacías, offset u64::MAX, referencia Root y Size; **no** se afirma que feed los emita |
| Valores PDF utilizables | Demostrado | Diez variantes, bytes sin decodificación, referencia exacta, contenedores independientes e inmutabilidad |
| Errores y drenaje | Demostrado | TypeError de feed no elimina eventos pendientes; take_events vacía la cola y los resultados conservan su propiedad |
| Tipado y contrato | Demostrado | Unión de TypedDict discriminados, consumidor estricto en Python 3.10, miembros del parser/PdfValue y campos de cada evento protegidos |

[RED](evidence/issue-256/red.log): once fallos por payloads/getters ausentes y un
caso ya válido. [GREEN](evidence/issue-256/focused.log): 88 casos focalizados,
incluida regresión de firma. [Pruebas nativas](evidence/issue-256/native.log): tres
casos inyectan eventos core en el mismo conversor usado por take_events, con el
intérprete Python real; no sustituyen el parser para afirmar que parsea XRef.
Eliminar un payload hace fallar los accesos/aserciones exactos. El checker incluye
un control negativo que elimina `StreamDataEvent.data` y exige detectar la pérdida.

El runner nativo usa un directorio de build separado y enlaza CPython únicamente
en el build de tests. Verifica que los tres tests estén presentes antes de
lanzarlos; se ejecuta en CI Linux/Python 3.12. Las wheels conservan sus features
y ABI; los tests Python se ejecutan en toda la matriz existente.

### Uso y límites del core

```python
from oxidize_pdf import IncrementalParser

parser = IncrementalParser()
parser.feed(b"1 0 obj\nstream\nactual payload\nendstream\nendobj\n")
for event in parser.take_events():
    if event["type"] == "stream_data":
        assert event["data"] == b"actual payload"
    elif event["type"] == "object_end":
        print(event["object"].kind, event["object"].value)
```

Los tipos están disponibles en `oxidize_pdf.parse_events`; la unión `ParseEvent`
también se exporta desde el paquete. Son descripciones estáticas de diccionarios,
no validadores ni objetos adicionales obligatorios en runtime.

| PdfValue.kind | PdfValue.value |
| --- | --- |
| null | None |
| boolean / integer / real | bool / int / float |
| string / name | bytes / str |
| array / dictionary | list[PdfValue] / dict[str, PdfValue] |
| stream | tuple[dict[str, PdfValue], bytes] |
| reference | tuple[int, int] (número, generación) |

Los contenedores devueltos son copias; modificarlos no altera el PdfValue. No se
resuelven referencias ni se decodifican strings/streams del objeto. El resultado
de `feed`, en cambio, ya puede haber perdido información **antes** del bridge:
core 5.4.2 devuelve Null en ObjectEnd, no emite XRef/Trailer, normaliza UTF-8
inválido y recorta espacios/newlines de cada línea. Tampoco garantiza conservar
una secuencia UTF-8 dividida entre feeds. No se pueden reconstruir los bytes PDF
originales a partir de estos eventos. Esas limitaciones permanecen bajo #244;
esta entrega cierra la pérdida adicional causada por el bridge (#256).

### Hallazgos

No se detectan incumplimientos nuevos del contrato del bridge. Se inspeccionaron
las conversiones de todas las variantes, el tamaño completo u64 de offsets,
propiedad tras drenar la cola, bytes sin conversión textual y compatibilidad con
los consumidores de PdfValue de firma. La conversión de contenedores no resuelve
referencias ni recorre el grafo PDF; clona sus valores internos. El runner no
construye comandos shell a partir de entradas PDF. Los límites upstream anteriores
son explícitos y no se consideran resueltos; #253 (AES) tampoco cambia.

### Calidad de Tests (Kripteia)

[Python](evidence/issue-256/kripteia-tests.log): 100/100, seis funciones y doce casos.
[Rust](evidence/issue-256/kripteia-rust.log): 100/100, tres tests. Los avisos
heurísticos sobre constantes y unwrap se revisaron: las constantes son oráculos
independientes del conversor y unwrap hace fallar el test con el error; no lo
silencia. Las aserciones señalan la línea/valor fallido. No se usa el score como
prueba de fidelidad del parser.

### Análisis de Seguridad (Kripteia Security)

Scans Rust, tests Python, módulo de tipos y runner: sin hallazgos en los alcances
escaneados. El módulo de tipos y runner no contienen tests detectables; sus scores
no representan cobertura. Revisión manual de bytes, enteros, propiedad, carga del
intérprete y comandos sin shell completada. No hay nueva validación del parser
upstream frente a PDF malicioso ni nuevas garantías de memoria.

### Métricas y estado de entrega

- Dieciséis archivos de código, tipos, tests, contrato y CI revisados, además del
  seguimiento. No se requirieron correcciones de producto durante la revisión.
- 2.382 tests de biblioteca; 295 MCP, un skip; 88 focalizados; tres tests nativos.
- Build, Clippy con warnings prohibidos, compilación mínima, mypy (25 archivos y
  consumidor estricto, también Python 3.10), contrato y siete controles de contrato
  aprobados. La última edición de Rust solo añade docstrings y aserciones nativas;
  se recompila y repite la suite focalizada sobre esa extensión final.
- Evidencias en `docs/evidence/issue-256/`, hashes en validation.json.
- Sin bloqueantes locales. Integración/CI remota/publicación se verifican por
  separado; no se declara paridad global ni un parser incremental completo.
