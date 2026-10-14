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

## Incremento #257 — BatchOptions y ejecución observable

Base: PR #269 fusionada en develop (`753c8d9`). Contrato: issue #257, core 5.4.2.

| Requisito y fuente | Estado y evidencia | Bloqueante / siguiente acción |
| --- | --- | --- |
| Seis campos de BatchOptions, getters, unidades y tipos (#257) | Incumplido: solo dos argumentos | Añadir opciones y validar extremos; tests de API y typing |
| Callbacks ejecutables y excepciones visibles (#257) | Pendiente: execute retiene GIL | Adaptador por procesador, liberar GIL, comprobar en subproceso con deadline |
| Verificar límites/errores del ejecutor (#257) | Core worker ignora memoria y timeout | Prueba real con límites mínimos y documentación explícita; no prometer enforcement |
| Regresión y revisión | Pendiente | Tests, contrato, Clippy, typing y ambos análisis Kripteia |

### Contrato público

`BatchOptions(parallelism=None, stop_on_error=None, *,
memory_limit_per_worker=536870912, progress_interval=0.1,
progress_callback=None, job_timeout=300.0)` conserva los dos argumentos
posicionales. Los seis campos tienen getters de solo lectura. `None` en los dos
primeros selecciona el default del core: min(CPUs, 8) y False. Memoria en bytes;
intervalo y timeout en segundos, redondeados a nanosegundos. Conteos positivos;
duraciones finitas, positivas y representables (mínimo redondeado: 1 ns).
`job_timeout=None` desactiva la opción. Callback debe ser callable o None.

Los callbacks reciben snapshots propios `ProgressInfo`; pueden conservarse tras
execute. El ejecutor libera el GIL, el hilo de progreso vuelve a adquirirlo al
llamar Python y el callback final se ejecuta en el hilo de execute. Deben retornar
pronto y utilizar el snapshot: el procesador es de un solo uso y no admite acceso
reentrante durante execute. El core puede emitir un estado completo más de una
vez y no emite callbacks para lotes vacíos. El intervalo controla el sleep del
hilo; intervalos largos pueden retrasar el retorno de execute, que espera ese hilo.

La primera excepción del callback se conserva y se vuelve a lanzar en execute
**después de que los trabajos terminen**; se suprimen callbacks posteriores.
No revierte archivos ni cancela trabajos. Reutilizar opciones en otro procesador
crea estado de errores independiente. Los ciclos callback/opciones/procesador
participan en el recolector de Python.

Core 5.4.2 **no aplica** memory_limit_per_worker ni job_timeout: almacena los
valores, pero `batch/worker.rs` recibe `_memory_limit` y ejecuta normalmente con
`Some(_timeout)`. La prueba real completa un PDF con 1 byte y 1 ns, mide una
duración superior al timeout y comprueba el archivo de salida. No son límites
de seguridad ni protección frente a documentos adversos. `stop_on_error` marca
cancelación y omite trabajos aún no enviados, pero los ya encolados pueden seguir;
no garantiza detenerse en el primer trabajo fallido. La cancelación previa omite
trabajos sin generar sus archivos; su snapshot final puede no ser `is_complete`
porque el core no cuenta cancelados como completados/fallidos.

Estas limitaciones upstream quedan bajo #244; #257 exige exponerlas y verificarlas,
no implementar un planificador nuevo ni cambiar el pin del core. Las funciones
batch independientes conservan su API y no aceptan BatchOptions.

### Resumen ejecutivo y evidencia final

Contrato #257 demostrado sobre el pin 5.4.2. Se revisaron constructor, getters,
conversión de duraciones, transferencia de opciones al core, callbacks y lifecycle,
stubs/consumidor estricto, gate de paridad, CI y pruebas reales. No cambia el core.

| Requisito | Evidencia final | Estado |
| --- | --- | --- |
| Seis campos/defaults/unidades/validación y API anterior | test_defaults_and_explicit_options, test_invalid_counts/durations/callback; mypy Python 3.10 | Demostrado |
| Callbacks, errores, snapshots, reutilización y cancelación | test_executor_callbacks_errors_and_limits; ejecutor real en subproceso con timeout de 20 s | Demostrado |
| Límites inertes documentados | Código publicado worker.rs y trabajo exitoso con 1 byte/1 ns | Demostrado; sin garantías de límites |
| Propiedad y recolección | Dos fallos reproducidos antes de integrar GC, ambos pasan después | Demostrado |
| Regresión/gates/revisión | Logs focused, regression, mcp, clippy, minimal, mypy, parity y Kripteia | Demostrado localmente |

RED inicial: 19 fallos y dos pases ante la extensión anterior, por campos ausentes
y validación incompleta (`red.log`). RED de GC: dos fallos y 21 pases ante la
primera implementación (`gc-red.log`); los objetos callback seguían vivos después
de gc.collect. GREEN final: 85 focalizados, incluidos los dos controles de GC.
La prueba del GIL está acotada por timeout, pero no se ejecutó una mutación que
retenga el GIL; no se atribuye a esa prueba evidencia RED de deadlock.

### Hallazgos

1. **Ciclos de referencias Python no visibles al GC**: `src/tier8.rs` y
   `src/batch_recovery_streaming.rs`, campos callback — un callback que conservase
   sus opciones/procesador retenía ambos indefinidamente. Corregido con referencias
   Python independientes y métodos __traverse__/__clear__. Evidencia RED/GREEN
   anterior. Revisión final de Arc y Py: cada propietario expone una referencia
   Python; los Arc internos comparten el adaptador sin duplicar referencias Python.

Sin bloqueantes restantes del contrato #257. Los límites y la cancelación parcial
upstream descritos arriba permanecen en #244 por ser comportamiento nativo que
esta issue exige caracterizar, no reemplazar. No se afirma paridad global.

### Calidad de Tests (Kripteia)

Python: 93/100, seis funciones y 23 casos. Avisos de similitud entre validadores
revisados: enteros y duraciones tienen dominios y errores diferentes. El aviso de
pocas aserciones en executor ignora las aserciones dentro del script ejecutado:
se comprueban archivo, estados, errores, identidad de excepción, snapshots y
cancelación. El control de GC usa una sola aserción deliberada sobre weakref.
Rust: 100/100, tres tests preexistentes en parse_events; no equivale a cobertura
Rust de BatchOptions. Los avisos sobre constantes/unwrap en esos tests ya estaban
reconciliados en #256. Logs: `kripteia-python.log` y `kripteia-rust.log`.

### Análisis de Seguridad (Kripteia Security)

Ambos scans, Python del nuevo test y Rust de src, sin hallazgos. Revisión manual:
no nuevo unsafe; duración inválida produce ValueError sin panic; callback se llama
sin sostener el mutex; error no se silencia; procesador se consume una sola vez;
snapshots clonados sin préstamos nativos; subproceso de pruebas sin shell y con
ruta temporal como argumento. No se ofrece aislamiento de callbacks ni límites de
recursos; un callback bloqueante puede bloquear execute, igual que otros callbacks
Python síncronos. Sin cambios de rutas/permisos de archivos del ejecutor nativo.

### Métricas y estado de entrega

- Ocho archivos técnicos más este seguimiento revisados; un hallazgo corregido
  en una fase de implementación y revisado de nuevo. Sin cambios durante la
  última pasada de revisión.
- 2.405 tests de biblioteca; 295 MCP, un skip; 85 focalizados; Clippy con warnings
  prohibidos, compilación mínima, mypy de 25 archivos más consumidor estricto
  Python 3.10 y contrato de paridad aprobados.
- Se reutiliza MCP anterior a la corrección GC: no cambió la superficie MCP ni
  usa BatchOptions; la suite de biblioteca y checks nativos sí se repitieron.
- Evidencias: `docs/evidence/issue-257/`; hashes de fuentes en validation.json.
  CI remota y aceptación/merge se verifican por separado.

## Incremento #264 — Errores de firma estructurados

Base: #270 fusionada (`940ab7a`); contrato #264 sobre core 5.4.2.

| Requisito | Estado inicial | Bloqueante / evidencia de cierre |
| --- | --- | --- |
| Variante y todos los campos nativos | Incumplido: signing/upstream aplanan a string | Conversor exhaustivo y tests de las 14 variantes |
| PdfError compatible y mensajes legibles | Incumplido en APIs security que usan builtins | Subclases con compatibilidad PdfError + ValueError/RuntimeError |
| Ramas reales y detalles tipados | Pendiente | Fallos reales de preparación, CMS y ByteRange; tipos y contrato |
| Paridad/revisión/regresión | Pendiente | Gate negativo de errores, suites y Kripteia |

Alcance: las excepciones SignatureError que cruzan signing, slots, detección y
security. Los resultados agregados de verify_pdf_signatures se revisan por
separado: su campo error es un resultado, no una excepción lanzada.

### Resumen ejecutivo

#264 conserva las 14 variantes de SignatureError del core 5.4.2 mediante un
conversor exhaustivo compartido. `PdfSignatureError` hereda de PdfError;
`PdfSignatureValueError` y `PdfSignatureRuntimeError` añaden compatibilidad con
ValueError/RuntimeError según la clasificación previa de security. Los mensajes
siguen siendo los de Display; `code` es un Literal estable y `details` un
SignatureErrorDetails con los campos originales, sin parsear mensajes.

La revisión amplió el alcance al consumidor agregado: su uso de `.is_ok()`
marcaba firmas criptográficamente inválidas como válidas. Se reprodujo antes de
corregirlo. `verify_pdf_signatures` usa ahora el parser/verificador detallados del
core (atributos CMS y ByteRange), exige ambos flags válidos y expone `error_code`
y `error_details`, manteniendo las claves anteriores. Los flags falsos producen
hash_verification_failed o signature_verification_failed. El resultado tipado es
SignatureVerificationSummary. Esto verifica integridad criptográfica, **no**
confianza del certificado, revocación, timestamps ni autorización del firmante.

### Contratos y evidencia

| Contrato/fuente | Evidencia | Estado |
| --- | --- | --- |
| #264: 14 variantes y campos | Test nativo preserves_all_signature_variants_and_fields; compara fixtures y claves del contrato JSON | Demostrado |
| PdfError/mensaje y categorías históricas | Pruebas reales de preparación, slots, CMS, hash y pickle | Demostrado |
| ByteRange/algoritmo | Offset/length/document_size reales; fixture nativo algoritmo desconocido, u64::MAX y enteros > 2^53 | Demostrado |
| Error en detección standalone | ByteRange ausente produce missing_field y field=ByteRange | Demostrado |
| Firma inválida nunca válida por ser Ok | Firma RSA válida y alterada, con/sin atributos; alteración de bytes cubiertos; CMS inválido | Demostrado |
| Tipos y paridad | Consumidor estricto Python 3.10; Literal/TypedDict, herencia y códigos; controles negativos de código/tipo | Demostrado |

`red.log` recoge cuatro fallos de la API anterior; `bridge-red.log` demuestra que
los errores anteriores no pertenecían a PdfSignatureError aunque la clase ya
existía en Python. `aggregate-red.log`: cuatro pases, tres fallos; ambas firmas
RSA alteradas daban valid=True, y el CMS inválido carecía de error_code. GREEN:
102 focalizados y cuatro tests nativos (uno recorre las 14 variantes).

La primera ejecución nativa no encontró el paquete al no activar el editable
venv en el intérprete embebido. Se corrigió PYTHONPATH en el runner para usar el
paquete real de este checkout; la ejecución final es satisfactoria. No se cuenta
ese fallo de montaje como evidencia funcional.

### API de errores

| code | details (campos presentes) |
| --- | --- |
| missing_field | field: str |
| invalid_byte_range / invalid_signature_dict / contents_extraction_failed | details: str |
| acro_form_not_found / no_signature_fields | ninguno |
| parse_error | message: str |
| cms_parsing_failed | details: str |
| unsupported_algorithm | algorithm: str |
| byte_range_exceeds_document | offset, length, document_size: int (bytes, u64 íntegro) |
| hash_verification_failed / signature_verification_failed | details: str |
| certificate_extraction_failed / certificate_validation_failed | details: str |

Los tipos se exportan desde oxidize_pdf y oxidize_pdf.signature_errors. Solo están
presentes las claves de la variante; el TypedDict las marca opcionales para
representar esa unión de campos. Cada excepción posee su diccionario; mantiene
args=(mensaje,) y conserva atributos al serializar con pickle. El código no usa
pickle sobre entradas PDF; el test solo serializa una excepción creada localmente.
Errores ajenos a SignatureError (p.ej. conversión Python de argumentos, lectura
inicial del PDF) conservan sus clases previas.

### Hallazgos

1. **Clasificación y campos descartados**: `src/signing.rs`, `src/upstream.rs`,
   `src/security.rs` y las llamadas de detección en `src/parser.rs` convertían a
   mensajes. Corregido con `src/signature_errors.rs:6`, match exhaustivo y clases
   tipadas. Todos los consumidores que lanzan SignatureError usan ese conversor.
2. **Resultado criptográfico falso tratado como válido**: `src/parser.rs:2110`,
   verify_pdf_signatures confundía Ok con flags válidos y descartaba errores de
   verificación. Corregido con verificador detallado, evaluación de is_valid y
   preservación de datos. Dos regresiones RED/GREEN y controles de PDF alterado.
3. **Detección del lector promovido devuelve vacío**: `src/parser.rs:674`, rama
   FileDocument/CursorDocument preexistente. Un PDF con ByteRange ausente devuelve
   [] por PdfReader.detect_signatures y missing_field por el standalone. Destino:
   #244, auditoría pendiente del lifecycle del lector; requiere acceso al lector
   nativo consumido por PdfDocument. No se oculta ni se interpreta [] como prueba
   de ausencia de firmas. No bloquea conservar los SignatureError que cruzan la
   frontera (#264), ni el standalone corregido; no se declara reparado ese método.

### Calidad de Tests (Kripteia)

Python: 100/100, siete funciones y ocho casos en el nuevo fichero; pruebas reales
sin mocks, claves y valores independientes del mensaje. Rust: 100/100, cuatro
tests, uno nuevo cubriendo 14 variantes. Aviso de unwrap revisado: está en tests,
hace fallar con el error y no lo silencia; valores esperados son fixtures ajenos
al conversor. Runner, gate y módulo de errores no contienen tests detectables;
sus scores no se interpretan como cobertura. Logs kripteia-*.log.

### Análisis de Seguridad (Kripteia Security)

Scans Rust, tests Python, tipos/excepciones y dos scripts: sin hallazgos. Revisión
manual detectó y corrigió el fallo de verificación descrito; un scan limpio no lo
habría descartado. No nuevo unsafe ni dependencias; tamaños u64 se convierten a
int sin flotantes; excepciones no cambian un fallo a éxito. El runner usa comandos
sin shell y una ruta local explícita para el intérprete embebido. La limitación de
detect_signatures tras promoción permanece registrada y fuera de las garantías
nuevas; no se promete validación completa de confianza ni paridad global.

### Métricas y entrega

- Dieciocho archivos técnicos y este seguimiento revisados. Tres hallazgos:
  dos resueltos; uno previo derivado a #244 con frontera y consecuencia explícitas.
- 2.416 tests de biblioteca; 295 MCP, un skip; 102 focalizados; cuatro tests
  nativos. Clippy con warnings prohibidos, compilación mínima, mypy (26 archivos
  y consumidor estricto Python 3.10), contrato y negativos aprobados.
- Tras la regresión se añadieron aserciones de alteración de bytes cubiertos:
  se repitieron los 102 focalizados y Kripteia Python; producto sin cambios.
- Sin bloqueantes locales de #264. Evidencias en `docs/evidence/issue-264/` y
  hashes en validation.json. CI remota, aceptación y merge se verifican aparte.

## Incremento #261 — Lectura acotada de outlines existentes

Base: PR #271 fusionada; #264 cerrada. Se aplica scoped-delivery y quality-review.

| Requisito (#261) | Estado inicial | Evidencia de cierre prevista |
| --- | --- | --- |
| outline/outline_with_options y cuatro presupuestos | Sin binding | API sobre PdfDocument real, tipos y defaults |
| Destinos, estilos, jerarquía y estado | Sin resultados legibles | Fixtures PDF independientes; ocho vistas y destinos nombrados |
| Ausencia, árboles malformados y límites | Pendiente | None/árbol vacío, ciclos y errores, frontera de cada presupuesto |
| Stubs, paridad y revisión | Pendiente | Tipos estrictos, contrato, regresión y Kripteia |

### Resumen ejecutivo

Se exponen `PdfReader.outline()` y `outline_with_options(OutlineReadOptions)` sobre
el lector real de core 5.4.2, liberando el GIL durante la lectura. Devuelven None
si no existe /Outlines y ReadOutline(items=[]) si existe un árbol vacío. Errores
de estructura, referencias o presupuestos se propagan como PdfParseError, sin
resultados parciales. Funciona sobre lectores de archivo y de bytes, ya promovidos
a PdfDocument. No utiliza el camino limitado de detect_signatures de #264.

Los resultados ReadOutline, ReadOutlineItem y ReadOutlineDestination son snapshots
propios, de solo lectura y distintos de OutlineTree/OutlineItem/Destination de
creación. Sus listas son copias; modificarlas no altera ni el snapshot ni el PDF.
La lectura conserva título, jerarquía, RGB opcional, negrita, cursiva y estado
abierto/cerrado. Los destinos se resuelven a índices de página base cero; se
conservan las ocho vistas PDF, sus parámetros y null como None (incluido zoom=0).

### Contratos y evidencia

| Requisito #261 | Evidencia | Estado |
| --- | --- | --- |
| Métodos, defaults y opciones consultables | test_outline_options_defaults_and_validation; typing y contrato JSON | Demostrado |
| Ausencia distinta de árbol vacío | test_absent_and_empty_outlines_are_distinct | Demostrado |
| Jerarquía, estilos, título Unicode y propiedad | test_hierarchy_styles_resolved_destinations_and_owned_results, archivo/bytes | Demostrado |
| Destinos explícitos/GoTo/nombrados y ocho vistas | test_all_destination_views; name tree y diccionario /Dests legado con referencia indirecta | Demostrado |
| Cada presupuesto, frontera y reintento | test_each_budget_is_enforced_and_reader_can_retry y nodos intermedios de nombres | Demostrado |
| Árboles/destinos malformados | Ciclos de siblings, nombres y nodos; Parent erróneo, destino ausente/fuera de rango, flags inválidos y enlaces incompletos | Demostrado |
| Tipos y gate de paridad | mypy estricto Python 3.10; diez checks de contrato/controles negativos | Demostrado |

RED inicial: 23 casos fallan por API ausente (`red.log`). GREEN: 26 casos de lectura
más diez de contrato = 36 focalizados. Fixtures construyen objetos y xref de PDF
independientemente del escritor de outlines; no se sustituye el parser. La prueba
original usó por error page_count() en vez de la propiedad page_count; se corrigió
ese montaje, sin modificar el producto ni contar el fallo como defecto funcional.

### Opciones, unidades y límites

| Campo | Default | Semántica |
| --- | --- | --- |
| max_items | 100000 | Ítems de outline visitados |
| max_depth | 256 | Profundidad de outlines, árbol de nombres y resolución de destinos |
| max_named_destinations | 100000 | Destinos nombrados recogidos |
| max_name_tree_nodes | 100000 | Nodos del árbol de nombres, incluidos intermedios vacíos |

Todos son enteros no negativos representables como usize; cero es válido y puede
rechazar un árbol no vacío. La raíz del outline tiene profundidad cero. Los
getters no permiten modificar las opciones tras construcción. El core construye
primero el mapa de páginas y puede cargar objetos/cache del documento: estos
presupuestos **no** limitan memoria total, tamaño PDF, tiempo o el coste del árbol
de páginas. Las copias de snapshots también ocupan memoria. Aumentar los límites
no convierte entradas arbitrariamente grandes en seguras.

ReadOutlineDestination expone page_index, kind y parameters. El orden es
XYZ(left,top,zoom), FitR(left,bottom,right,top), FitH/FitBH(top), FitV/FitBV(left),
Fit/FitB(). Los nombres originales quedan resueltos, no se conservan como alias.
El core no representa acciones distintas de GoTo como destinos de página;
`destination=None` puede indicar acción no GoTo o ausencia de destino. No se
exportan ni ejecutan diccionarios de acción. Esta entrega es lectura de outlines,
no una API para editar o reproducir íntegramente sus diccionarios originales.

### Hallazgos

Sin incumplimientos pendientes del contrato #261 tras la revisión. Se revisaron
ambos backends de ReaderState, la liberación del GIL sin referencias Python,
propiedad de árboles/listas, conversiones de todos los DestinationType y errores
al superar cada presupuesto. El guard de PageRef no resuelta produce PdfParseError
si el core incumpliese su contrato; el lector publicado resuelve a PageNumber.
Las limitaciones de representación/recursos anteriores son explícitas y permanecen
bajo #244; no se presenta lectura como creación ni como límite total de memoria.

### Calidad de Tests (Kripteia)

Python: 98/100, diez funciones, 26 casos. Dos avisos de similitud entre tests de
árboles inválidos y ciclos de nombres: tienen el mismo patrón pytest.raises pero
activan recorridos distintos; se conservan ambas familias. Rust: 100/100, cuatro
tests preexistentes (parse_events y signature_errors); no representa cobertura
unitaria Rust nueva de outlines. Los tests de integración Python sí ejecutan el
nuevo binding y el core real. Avisos de unwrap en tests anteriores revisados en
#256/#264 y sin cambios relevantes aquí. Logs kripteia-tests/rust.log.

### Análisis de Seguridad (Kripteia Security)

Ambos scans, Rust de src y Python del nuevo test: sin hallazgos. Revisión manual:
ningún unsafe nuevo, ningún destino ejecutado, ningún comando construido desde
PDF, presupuestos copiados antes de liberar GIL y enteros negativos/fuera de
rango rechazados en la frontera PyO3. Se prueban ciclos y fallos de enlaces y
resolución, sin devolver árboles parcialmente aceptados. No se afirma que los
presupuestos de outlines cubran el parser completo o el árbol de páginas.

### Métricas y estado de entrega

- Once archivos técnicos y este seguimiento revisados; sin cambios de producto
  durante la revisión final. Sin nuevos bloqueantes del contrato #261.
- 2.442 tests de biblioteca; 295 MCP, un skip; 36 focalizados. Build, Clippy con
  warnings prohibidos, compilación mínima, mypy (26 archivos y consumidor
  estricto Python 3.10), contrato y controles negativos aprobados.
- Evidencias en `docs/evidence/issue-261/`; hashes de fuentes en validation.json.
  CI remota, aceptación y merge se comprueban aparte; no se declara paridad global.
