# Revisión del incremento ClippingPath (#244)

## Resumen ejecutivo

Base da70c4c (PR #285). Alcance: construcción e inspección de ClippingPath,
reglas de relleno y conexión al Page existente. Core fijado en 5.4.2.
Inspección de bindings, registro, exports, stubs, contrato de paridad, CI,
consumidor tipado y tests. Sin cambios de dependencias ni superficies MCP.

## Contratos y evidencia

- Mutadores retornan la misma instancia y preservan parámetros/orden; comandos
  esperados literales, extremos de curvas y límite del radio comprobados por
  tests/test_clipping_paths.py. Las tres factorías existentes siguen cubiertas.
- with_winding_rule crea copia; clear preserva regla. Comandos congelados y
  listas copiadas impiden que inspeccionar modifique el trazado. PyO3 extrae
  completamente el polígono antes de mutar: entrada tardía inválida es atómica.
- Page clona el trazado. El test limpia el origen después de instalarlo y
  renderiza el PDF mediante Poppler: exterior blanco, interior azul y centro
  dependiente de la regla. Se ejecutaron ambos casos, sin skips locales.
- Control negativo en copia desechable: sustituir EvenOdd por NonZero provoca
  exactamente un fallo en el píxel central; el otro caso pasa. Evidencia en
  wrong-rule-control.log. La suite de producto usa la regla correcta.
- Tipos y firmas contrastados con extensión compilada y stubs; inventario,
  consumidor estricto y guard de paridad pasan (typing-parity.log).
- La matriz Linux Python 3.12 instala Poppler; en máquinas sin renderer solo
  se omiten los dos tests raster, conservando todos los contratos de comandos.

La revisión manual recorre la conversión Python/Rust, ownership, mutación y
serialización del core. No añade unsafe ni entrada/salida de archivos al binding.
La inspección copia O(n) comandos; no promete límites de memoria ni validación
geométrica adicional. Se documenta que el llamador debe usar geometría finita.
El formateo final de Rust cambia solo whitespace respecto del wheel local.

## Hallazgos

Sin hallazgos pendientes en el subcontrato. Las limitaciones de intersect,
as_text_clip y ClippingRegion quedan en FEATURE_PARITY.md para otro incremento:
no se exponen ni se necesitan para construcción/inspección y reglas de relleno.

## Calidad de Tests (Kripteia)

Python: score 100, seis funciones en un archivo (ocho casos parametrizados).
Sin observaciones. Rust: score 100, cero tests identificados; ese resultado no
acredita cobertura. Los bindings se ejercitan a través de Python y del PDF real.
Salidas completas: kripteia-python.log y kripteia-rust.log.

## Análisis de Seguridad (Kripteia Security)

Ambos análisis: No security issues found. Alcance tests/test_clipping_paths.py
y src/graphics.rs. La inspección manual complementa los escáneres: extracción
completa antes de mutación, snapshots propios, enum cerrado, sin punteros ni
rutas controladas por el usuario añadidas al producto.

## Métricas

- Hallazgos pendientes del incremento: 0.
- Archivos de producto modificados durante revisión final: 0.
- Regresión/Clippy: resultado final en sus logs.
- Verificación remota y merge: pendientes en el momento de este informe;
  el seguimiento de entrega debe registrar su resultado antes de cierre.
