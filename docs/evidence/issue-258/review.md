# Revisión de #258 — core 5.5.0

## Resumen ejecutivo

Base develop `91261a4fbc09e2fa0fface4106c81082bf8414d8`, cambios de #258
registrados en este commit. Se revisan bindings, consumers nativos, exportaciones,
stubs, pruebas y gates. Los cuatro criterios de #258 quedan demostrados localmente.
No se cambia el core ni se declara paridad total de #244. CI/integración pendientes.

## Contratos y evidencia

| Contrato | Evidencia | Estado |
| --- | --- | --- |
| Todos los campos configurables/consultables; presets compatibles | tests/test_streaming_memory_options.py, typing.log, consumer-typing.log | Demostrado |
| Namespaces correctos, consumidores reales | StreamingDocument usa streaming::StreamingOptions; LazyDocument usa memory::MemoryOptions; mutation.log | Demostrado |
| Límites de contenidos decodificados, caché y errores | Fixtures PDF independientes, variantes comprimidas y arrays de streams, límites exactos, caché deshabilitada/evicción/clear/reintento | Demostrado |
| Efecto del buffer y lazy/eager | native.log: lector instrumentado, lecturas reales diferentes y cero lecturas tras eager | Demostrado |
| Ciclo de vida y ownership | Cierre/context manager, handles liberados, snapshots válidos tras cierre; errores de tipos, rangos y documentos cifrados | Demostrado |
| Compatibilidad | library.log: 2700 pasan; mcp.log: 295 pasan/1 skip; 5 pruebas nativas; Clippy/no-default/paridad/tipos | Demostrado localmente |

La mutación desechable sustituyó las opciones por Default en ambos `open`.
Fallaron los cuatro casos de límite decodificado (no lanza error) y las cachés
lazy 0/1 (capacidad incorrecta); un caso cache=2 pasó. `mutation.log`: 6 failed,
1 passed. El árbol de entrega no fue mutado y la suite verde usa el wheel final.

Revisión manual: sin unsafe nuevo; opciones clonadas antes de liberar GIL,
consumidores unsendable, errores propagados, valores devueltos owned. Los límites
son de payload/caché del adaptador, no RAM total ni pico; el parser y valores
retenidos por el usuario quedan fuera. Los flags unsupported se notifican y no
se habilitan silenciosamente. Se conserva PageStreamer, incluido seek/rotación;
StreamingDocument expone MediaBox nativa sin rotación. Los contadores no
instrumentados se documentan como tales. Esto satisface #258; paridad global y
los modos unsupported siguen en #244, sin promesas adicionales.

## Hallazgos

1. `LazyDocument.page_count` había perdido la docstring del contrato read-only.
   Corregida; prueba histórica pasa en el wheel final.
2. Las firmas nuevas del registro de paridad omitían `self` de métodos de instancia.
   Corregidas contra las firmas públicas; regresión completa pasa.
3. El montaje aislado de pruebas nativas no encontraba la extensión al anteponer
   python/ al PYTHONPATH. Se instaló el artefacto del wheel en ese árbol ignorado;
   las cinco pruebas pasan. CI usa maturin develop, que ya prepara ese montaje.

No quedan hallazgos bloqueantes. El ejemplo README se contrastó con los getters
reales (`number` y `extract_text_streaming`). Los fallos iniciales de resolución
mypy se corrigieron seleccionando el wheel aislado en PYTHONPATH.

## Calidad de Tests (Kripteia)

Rust: score 100, una función nativa. Advertencias sobre constantes y unwrap:
las constantes proceden de fixtures independientes; unwrap hace fallar la prueba
con el error real, no lo silencia. Python: score 99, 11 funciones; aviso de ratio
assert/setup en el caso de rechazo de cifrado, revisado: las dos excepciones son
el comportamiento requerido, no una carencia de aserciones. Logs adjuntos.

## Análisis de Seguridad (Kripteia Security)

Ambos análisis ejecutados: “No security issues found”. Alcance: nuevo módulo Rust
y nuevas pruebas Python, complementado con revisión manual de las fronteras
adyacentes y lectura de los consumidores core 5.5.0. Un scan limpio no acredita
límites de memoria globales ni seguridad del parser para todo PDF arbitrario.

## Métricas

Cambios revisados: módulo, tres integraciones Rust, retirada del wrapper anterior,
exports/stubs, pruebas Python/Rust/typing, scripts y workflow, README y registro.
Hallazgos: 3 resueltos (incluye montaje); ninguno pendiente de corrección.
La fase de revisión fue de lectura; las correcciones se aplicaron dentro del
encargo de implementación. Pendiente: CI multiplataforma y merge del mismo head.
