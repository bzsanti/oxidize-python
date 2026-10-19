# Revisión TaggedPdf de #262 sobre core 5.5.0

## Resumen ejecutivo

Base develop `1b8015831e25ad36c2a82fa744b59cf3342fb9b6`, después de #289.
Recuperado y completado el borrador de editor; no se modifica el core. Alcance:
cinco mutaciones, preparación ordenada, opciones, planes/reportes y contratos
Python. #262 sigue abierta para los demás editores/OCR/features opcionales.

## Contratos y evidencia

| Contrato y fuente | Frontera y contraejemplo | Evidencia actual |
| --- | --- | --- |
| core writer::IncrementalTaggedPdfEditor y cinco TaggedPdfMutation | Conversión owned PyO3, getters/snapshots y firmas; evitar pérdida de campos | typing/parity/consumer-typing logs; fixtures reales |
| Identidad/prefijo y aplicación atómica | Generación 7, atributos opacos/maps, batches inválidos y editor reutilizable | tests/test_incremental_tagged.py y qpdf; 56 focalizadas pasan sin skips |
| Orden secuencial core #762 | Cambio seguido de restauración/removal debe respetar último valor | Tres casos de regresión y qpdf; defecto previo 5.4.2 ya corregido en 5.5.0 |
| Recuperación efectiva y xref streams | Falta ParentTree/StructParents, idioma ausente, inventario separado | Ocho combinaciones de fixture independiente; qpdf valida archivo final y objeto 6,7 |
| Preparación exige validez sin inventar metadatos | Descripción ausente, valores vacíos/erróneos, sobrescritura de descripción | Reparación explícita y rechazos en plan/apply |
| Permisos/cifrado/límites | P1/P2/P3 en plan/apply vacíos y preflight/builders; cuatro budgets | Rechazos ejecutados; fixtures DocMDP prueban política, no autentican firmas |
| Compatibilidad | Consumidores existentes de PdfValue y tagged validation | 2746 biblioteca; 295 MCP/1 skip previo; Clippy, no-default y tipos pasan |

Preflight puede recuperar para inspeccionar, sin mutar el editor. Preparación se
reproduce por operación y sus costes de parsing/copias no están globalmente
acotados por TaggedPdfLimits. Se documenta sin prometer RAM global ni PDF/UA.
No hay unsafe ni I/O nuevo en el binding. Conversiones unsigned verificadas por
PyO3, errors propagados; préstamos limitados al detach y retornos propios.

## Hallazgos

1. El borrador histórico tenía pendiente recuperación/xref/preparación. Resuelto
   con fixtures independientes, matriz y errores efectivos sobre core 5.5.0.
2. La inscripción histórica de paridad no exigía las pruebas TaggedPdf. Corregida:
   registro de las 15 funciones y copia del fixture en el control negativo del gate.
3. La pérdida secuencial upstream #762 bloqueaba el borrador original. Resuelta
   por la publicación 5.5.0 y las tres regresiones actuales con qpdf.

Sin hallazgos pendientes de implementación. Revisión funcional y de ownership
completada. Control negativo discriminante y aceptación remota se registran abajo.

## Calidad de Tests (Kripteia)

Python: score 99, 15 funciones. Aviso sobre test_external_qpdf interpretado como
ignore: usa skipif por disponibilidad externa; aquí se ejecutó y pasó sin skip.
Rust: score 100, cero tests detectados; no representa cobertura Rust. Las pruebas
Python cargan el wheel real, no mocks. Logs adjuntos. Expectativas de generación,
bytes opacos, texto y offsets provienen de fixtures independientes del writer.

## Análisis de Seguridad (Kripteia Security)

Ambos análisis ejecutados, sin hallazgos (“No security issues found”). Cobertura:
nuevo módulo Rust y pruebas Python, complementada con revisión de core
incremental_tagged_pdf y rutas de recuperación/permisos. No certifica toda la
seguridad del parser. Los subprocess qpdf de tests son listas de argumentos,
archivos temporales y nuevas invocaciones con timeout; no hay shell dinámico.

## Métricas

Se revisaron módulo, integración/visibilidad, exports/stubs, fixtures/pruebas,
consumidor, contrato/gates y README. Tres pendientes históricos resueltos;
ningún hallazgo nuevo que requiera modificar el producto durante la revisión.
Verificaciones pendientes: control negativo y CI/integración del head final.

## Control discriminante y conciliación final

En copia desechable se descartaron todas las mutaciones de plan/apply y se
ocultó /DocMDP al construir el editor. El test de atributo falló por plan vacío;
P1/P2/P3 fallaron por ausencia de PdfPermissionError (DID NOT RAISE).
Resultado: 4 failed/31 deselected, mutation.log. El wheel entregable no se mutó.
Sobre ese wheel, los 56 tests focalizados finales pasan sin skips.

Para evitar una falsa prueba de autorización, el control usa un PDF etiquetado
válido con política DocMDP serializada independientemente, ByteRange cubriendo
la definición y excluyendo Contents. No es una firma criptográfica auténtica.
El primer intento de fixture fue rechazado por ByteRange inválido; se corrigió
el montaje y se mantuvo la exigencia de PdfPermissionError. Se conservan además
los tests previos con el fixture de certificación del repositorio.

La última edición afecta solo al fixture de pruebas; se revalidaron todas las
56 focalizadas y ambos resultados RED/GREEN. Se reutiliza regresión 2746/MCP295,
Clippy/no-default/tipos sobre las mismas fuentes funcionales. Kripteia Python
repetido tras el ajuste, sin hallazgos de seguridad. Pendiente: CI e integración.
