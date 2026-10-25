# Revisión: comparación semántica de #263

## Resumen ejecutivo

Base 189acde más incremento local de comparación. Se conserva el borrador
TaggedPdf de la sesión anterior, bloqueado por upstream #762; no forma parte de
la aceptación de este incremento. Core =5.4.2, PyO3 0.28, Python abi3 3.10+.
Contrato: exponer íntegramente opciones/resultados/errores del comparador
publicado, sin prometer renderizado equivalente ni correcciones del core.
La redacción irreversible sigue siendo un subcontrato pendiente de #263.

## Contratos y evidencia

| Contrato | Evidencia | Estado |
| --- | --- | --- |
| Siete límites configurables y valores por defecto | 25 casos nuevos sobre extensión real, defaults/negativos/límites por campo y operandos | Demostrado |
| Opciones efectivas | Copia desechable ignora opciones: diez fallos DID NOT RAISE; fuentes reales: GREEN | Demostrado |
| Diferencias tipadas, orden estable y normalización soportada | Textual/Visual/Metadata/Structural/Security/SerializationOnly; Flate, renumeración y fechas | Demostrado |
| Historial y objetos | Xref sintético, tres revisiones con restauración de estado final; Added/Replaced/Freed y generación 4/5 | Demostrado |
| Snapshots completos | Colecciones y huellas bytes independientes, propiedades frozen; campos core cotejados | Demostrado |
| Formatos alternativos | qpdf crea ObjStm/XRef; pdftotext conserva texto; limitación conservadora del core documentada | Demostrado con limitación |
| Tipado/contrato | Inventario de 490 exports; consumidor mypy estricto actual y Python 3.10; gate y tests del gate | Demostrado |

`focused.log`: 33 passed, 25 casos nuevos y ocho controles del gate.
`mutation.log`: 10 fallos esperados al descartar opciones. Se compiló una copia
independiente en /tmp/oxidize-263-options-mutant; el módulo se cargó solo en el
proceso de la prueba, sin reemplazar el módulo instalado ni alterar el core.

`regression.log`: 2566 passed, ocho fallos de montaje del test de paridad porque
su copia temporal no incluía el nuevo archivo requerido. Corregido el inventario
de esa fixture en tests/test_parity_checker.py; los ocho casos pasan en
focused.log. No son fallos funcionales ni se suma esa ejecución como una suite
completamente GREEN. El resto de fuentes funcionales no cambió después de esa
regresión. Clippy con warnings como errores y cargo check sin default features
aprobados. Rustfmt del nuevo módulo y diff --check aprobados.

Inspección de productores/consumidores: bytes propios y opciones Rust antes de
detach; conversión exhaustiva de enums; hashes de 32 bytes como bytes; referencias
u32/u16 sin pérdida; xref_offset u64; errores mediante to_py_err. No unsafe,
acceso externo ni nuevas dependencias. La configuración limita el trabajo del
comparador, no todas las asignaciones del parser ni el proceso completo.

## Hallazgos

1. **Diferencias estructurales por contenedores físicos**:
   core `verification/semantic_comparison.rs:630` incluye ObjStm/XRef en los
   objetos fuera de Root/Info; se propaga fielmente en
   `src/semantic_comparison.rs:260`. Una conversión qpdf sin cambio textual
   devuelve diferencias en /Revisions y /UnreachableObjects. Destino: limitación
   upstream documentada y reproducible en test_independent_readers_and_xref_stream;
   una eventual corrección debe excluir infraestructura de serialización sin
   ocultar objetos huérfanos reales ni historial. No bloquea exponer el resultado
   actual completo, pero impide prometer equivalencia general entre layouts.
   No se cambió el core ni se declaró resuelta esta limitación.
2. **Fixture del gate incompleta**: tests/test_parity_checker.py:12 omitía el
   nuevo archivo de tests requerido por el contrato. Se añadió a su copia
   temporal; ocho casos pasan después de la corrección. Resuelto.

## Calidad de Tests (Kripteia)

kripteia-python.log: score 98, 12 funciones, un archivo; penaliza el skipif de
herramientas externas como ignore. El test qpdf/pdftotext se ejecutó localmente y
pasó, no fue omitido. kripteia-rust.log: score 100 con cero tests detectados;
no representa cobertura Rust. Las pruebas invocan la extensión real, y los
valores esperados provienen de fixtures serializadas independientemente.

## Análisis de Seguridad (Kripteia Security)

Ambos análisis: No security issues found. Revisión manual de ownership antes de
liberar GIL, ausencia de unsafe y side effects, errores en ambos operandos,
permisos de entrada cifrada y uso efectivo de los siete presupuestos. El cambio
DocMDP de test comprueba clasificación de diferencias, no autenticidad de firma.
La limitación física anterior produce diferencias adicionales, no certificación.

## Métricas

- Once archivos de implementación/integración/tests/docs revisados, más core y evidencias.
- Dos hallazgos: montaje resuelto, limitación upstream conservada y documentada.
- Sin correcciones funcionales de producto tras el análisis; ajuste de fixture.
- CI remota e integración pendientes. La aceptación global de #263 permanece abierta.

MCP: 295 passed, 1 skipped en mcp-unsandboxed.log. La ejecución restringida
se interrumpió tras esperas de IPC; no se contabiliza como fallo funcional.
La ejecución autorizada fuera del sandbox terminó en 24.91 segundos.

## Preparación de integración

Entrega aislada en /tmp/oxidize-263-delivery basada en 189acde: incluye solo
comparación semántica. Los logs originales se conservan como evidencia histórica;
sus 490 exports incluían seis tipos del borrador TaggedPdf, excluidos aquí.
Se renuevan hashes de fuentes y se valida la rueda aislada antes de CI.
Workflow añade consumidor estricto y qpdf/poppler-utils obligatorio en Linux
3.12. Instalación y command -v fallan el job si faltan esas herramientas.
Análisis del gate y workflow sin hallazgos de seguridad; el scan del YAML no
constituye validación de ejecución del workflow.

Rueda aislada: 2559 pruebas de biblioteca aprobadas (delivery-regression.log),
484 exports públicos y 483 nativos, inventario/gate correctos. Mypy de paquete
(26 archivos) y consumidor estricto sobre la rueda aprobados. La comprobación
con MYPYPATH inicialmente arrastró código fuente de signature_errors bajo flags
estrictos ajenos a este consumidor; se verificó después el consumidor contra
los stubs de la rueda, como corresponde al contrato distribuido.
