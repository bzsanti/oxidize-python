# Revisión TextNote/Highlight — #262, core 5.5.0

## Resumen ejecutivo

Base develop `d253efac9b828eb7eb2a86c04142accdd3bc5031`; implementación de
TextNote/Highlight en este commit. Sin modificación del core ni publicación.
Los dos consumidores publicados aplican validate_annotation_policy en batches
no vacíos; #712 sigue administrativamente abierta, pero su corrección está
presente en 5.5.0 y queda verificada por pruebas positivas/negativas.

Revisión de bindings, contratos y documentación completada. Aceptación local
satisfecha; CI e integración pendientes. #262 conserva OCR y features opcionales.

## Contratos y evidencia

| Contrato | Frontera/contraejemplo | Evidencia y estado |
| --- | --- | --- |
| API completa de core writer::incremental_text_notes/highlights | Identidades con generación, campos/results, cinco operaciones, geometría/color/opacity validados | 13 tipos expuestos, firmas/getters en contrato, consumidor estricto; demostrado |
| Preservación y consumo real | Prefijo exacto, anotaciones ajenas, metadatos, contenidos de página, Unicode y dimensiones | Fixtures independientes con arrays directos/indirectos y xref clásico/stream; qpdf JSON y render Poppler con anotaciones ocultas; demostrado |
| Identidad y resultados | Notas con generación 9, highlights con generación 4; added_notes en orden frente a highlights completos | Ciclos alta/edición/borrado, relectura y snapshots; demostrado |
| Atomicidad y errores | Batch válido+inválido, duplicados, identidad/subtipo/generación errónea, límites crop y valores no finitos | Editor reutilizable tras error, no-op conserva bytes; demostrado |
| DocMDP | P1/P2 rechazan add/update/remove; P3 permite operaciones; reads/no-op disponibles | 15 casos de política sintética más 2 casos P2 sobre fixture de certificación original; demostrado |
| Cifrado y geometrías no soportadas | Rechazo en lectura/aplicación, anotación directa objetivo o compartida | Casos ejecutados, sin panic ni error tragado; demostrado |
| Compatibilidad | Integración en exports/stubs/gate y suite existente | 2821 biblioteca; 295 MCP/1 skip previo; Clippy/no-default/tipos/paridad; demostrado |

Los 75 casos focalizados pasan sin skips. La geometría usa CropBox/MediaBox
heredada en espacio PDF sin rotar. qpdf verifica valores literales y atributos
opacos; los objetos de contenido/metadata/Info/Link son idénticos y Poppler conserva
el raster de página con anotaciones ocultas. No se declara interoperabilidad de
apariencia de anotaciones para todo visor ni firma criptográficamente válida de
los fixtures sintéticos. Eliminación incremental conserva historial; no redacción.

Inspección: módulo Rust sin unsafe, unwrap ni conversiones enteras truncadas.
Objetos owned antes de detach; editor frozen con bytes inmutables, referencias
limitadas a la llamada, errores core propagados. Las copias de resultados y
colecciones evitan mutación de snapshots. No se promete límite global de RAM;
validaciones se delegan al core en el mismo momento que la API nativa.

## Controles discriminantes

1. Copia desechable omite DocMDP únicamente para ejecutar apply y restaura el
   prefijo de origen en la respuesta. Esto mantiene lectura/no-op y evita que una
   diferencia incidental de bytes sustituya a la prueba de permisos. Resultado:
   12 fallos DID NOT RAISE PdfPermissionError (P1/P2, incluidos fixtures originales),
   5 P3 pasan. policy-mutation.log. Ambos editores reales pasan los 17 casos.
2. Otra copia conserva reports nativos pero devuelve los bytes originales en ambos
   apply. qpdf encuentra `old note` en vez de `café 世界 😀` en las cuatro variantes.
   payload-mutation.log: 4 fallos esperados, sin errores de montaje. Prueba que
   los tests no aceptan reports correctos con un artefacto sin cambios.

El árbol entregable nunca fue mutado. Los tests GREEN usan el wheel aislado final.

## Hallazgos

1. **Referencias de tipos no importadas en el primer stub**:
   `python/oxidize_pdf/_oxidize_pdf.pyi:5739` — List/Tuple introducían Any en el
   consumidor estricto. Corregido usando list/tuple, como el resto del proyecto;
   consumidor --strict --disallow-any-expr y paquete completo pasan. Una lectura
   concurrente durante reinstalación conservó inicialmente el resultado anterior;
   revalidación final sin cache confirma la corrección.

Sin hallazgos abiertos. La ejecución de tests externos es condicional al ejecutable
para portabilidad, pero qpdf/Poppler estaban disponibles y los cuatro casos se
han ejecutado localmente; CI Linux 3.12 instala ambos y se verificará su log.

## Calidad de Tests (Kripteia)

Python: score 98, 12 funciones analizadas (75 casos parametrizados). Único aviso:
external_objects_unicode_metadata_and_content_preserved interpreta skipif como
ignore; ejecutado aquí sin skips. Rust: score 100, cero tests detectados; no es
cobertura del módulo. Las pruebas atraviesan la extensión real. Expectativas de
objetos/Unicode/píxeles independientes del writer. Logs kripteia-*.log adjuntos.

## Análisis de Seguridad (Kripteia Security)

Ambos análisis ejecutados: “No security issues found”. Revisados manualmente
permisos, cifrado, ownership/GIL, rangos u32/u16, no-finitos, longitud de arrays y
atomicidad. Subprocess de tests usa argumentos separados, paths temporales y
timeout. Alcance de scan: módulo nuevo y tests; no certifica todo el parser core.

## Métricas

12 archivos de producto/integración/documentación/tests revisados, más catálogo
core y gates. Un hallazgo corregido en implementación, ninguno pendiente.
La fase de revisión no modificó archivos de producto. Pendiente: CI e integración
sobre el mismo head. Publicación de paquete fuera del alcance.
