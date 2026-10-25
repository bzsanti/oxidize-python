## Resumen ejecutivo

Incremento de #244 sobre develop 9e5b9a622fc840c28aa62d435becbad8d2aca32c:
cinco operaciones de contenido marcado de Page, sin cambiar core =5.4.2.
Se revisaron productor de operadores, wrapper, stubs, consumidores, contrato y CI.
Alcance: texto en páginas nuevas; gráficos almacenados en otros contextos y
certificación PDF/UA quedan fuera. El editor incremental #262 permanece excluido.

## Contratos y evidencia

- MCID local, anidamiento, errores sin mutación: tests ejecutan el bridge real,
  inspeccionan orden BDC/texto/EMC en streams descomprimidos y conectan el MCID
  con StructureElement/StructTree. Demostrado en focused.log.
- Etiquetas: entrada literal UTF-8, escape PDF por byte y rechazo de nombre vacío.
  Casos con delimitadores, NUL, salto de línea e intento de operadores. Una copia
  nativa sin validación/escape produce cuatro fallos por bytes incorrectos o
  excepción ausente (mutation.log), mientras el nombre simple pasa.
- ActualText: valores vacíos, delimitadores, salto de línea, acento y par sustituto
  UTF-16; inspección de hexadecimal y extracción independiente con pdftotext.
  qpdf acepta el documento. No se garantiza comportamiento de todos los visores.
- Distribución: wheel aislado, inventario, consumidor mypy estricto y gate;
  CI incluye el consumidor y sus tests. No modifica dependencias ni release.
- La primera regresión local encontró una omisión de `self` en el contrato nuevo,
  corregida; focused.log incluye el gate runtime después de la corrección.
  regression.log conserva el fallo inicial, no representa la aceptación final.

## Hallazgos

Sin hallazgos pendientes en el incremento. El core interpola nombres literalmente;
el wrapper escapa ambas entradas antes de modificar el estado. El `expect` de
formateo escribe exclusivamente a String y no introduce un error recuperable.
El llamador sigue siendo responsable de cerrar secuencias y conectar el árbol.
La inspección no constituye una revisión completa del módulo Page preexistente.

## Calidad de Tests (Kripteia)

Python: 98/100, seis funciones (once casos parametrizados). Señala baja proporción
de asserts en el test Poppler (90): las dos aserciones comprueban texto lógico
presente y texto pintado ausente, tras generación y ejecución real de herramientas.
No se añaden aserciones redundantes para mejorar la métrica. Rust: cero tests
identificados por el analizador; 100 es su valor de salida, no cobertura Rust.
Resultados completos en kripteia-python.log y kripteia-rust.log.

## Análisis de Seguridad (Kripteia Security)

Ambos análisis ejecutados: «No security issues found». Inspección manual adicional
de inyección de operadores, UTF-8/UTF-16 y validación antes de mutación. Sin nuevo
unsafe, acceso a archivos, red, secretos ni ejecución de comandos en producto.

## Métricas

- Archivos de implementación, tests, contrato, documentación y CI revisados: 9.
- Hallazgos pendientes: 0.
- Archivos de producto modificados durante la fase de revisión: 0.
- Verificación remota pendiente al redactar: matriz CI de la PR antes de integrar.
