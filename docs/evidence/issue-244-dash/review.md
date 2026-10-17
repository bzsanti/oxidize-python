# Revisión LineDashPattern — #244

## Resumen ejecutivo

Base 043a7d6, core 5.4.2. Alcance: factorías dashed/dotted, lectura de array/phase
y serialización. Se revisaron src/graphics.rs, stubs, consumidor tipado, tests,
contrato de paridad, su guard, README y wiring de CI (ocho fuentes).
Sin cambios al core, dependencias, entrypoints MCP ni APIs anteriores.

## Contratos y evidencia

- Las factorías llaman al core con los dos parámetros en orden y fase cero.
  Tests verifican números literales distintos para cada factoría y solid.
- El constructor copia la lista; array retorna copia y phase es de solo lectura.
  Se mutan las listas de entrada/salida y se rechaza asignación a ambas propiedades.
- Serialización fiel: dos decimales, no finitos a cero, negativos conservados y
  fase cero emitida para array vacío. Lectura conserva los valores originales.
  No se promete validación de legalidad de patrones arbitrarios.
- Page.set_dash_pattern clona el patrón y usa el escritor real. Cuatro PDFs se
  renderizan con Poppler: solid, dashed, dotted y fase 5. Los píxeles interiores
  del trazo distinguen huecos y segmentos, sin depender de antialiasing del borde.
- Control negativo desechable elimina fase 5: exactamente un fallo (custom),
  tres casos pasan; wrong-phase-control.log. Los tests originales pasan.
- Inventario, consumidor estricto y paridad pasan: typing.log. CI Linux 3.12
  instala Poppler; los tests de raster se omiten solo cuando no está disponible.

Inspección adicional: no unsafe, rutas, callbacks ni manejo de archivos nuevos
por el binding. Lista propiedad de Python, copia O(n), sin referencias prestadas.
La superficie no amplía las garantías del escritor ni asegura que dotted use
puntas redondas; el README explica el control mediante longitud y line cap.

## Hallazgos

Sin hallazgos pendientes del subcontrato. La advertencia heurística de Kripteia
sobre ratio de asserts se contrastó con el bucle de cuatro píxeles por caso y
el control negativo efectivo. El montaje de PDF/render necesita esas líneas;
no se añaden asserts redundantes para aumentar el score. No bloquea aceptación.

## Calidad de Tests (Kripteia)

Python: score 98, cuatro funciones, siete casos. Test de raster score 90 por dos
asserts estáticos frente a 22 líneas de montaje (8%). Ver evaluación anterior.
Rust: score 100, cero tests encontrados: no acredita cobertura; se valida el
binding desde Python. Logs completos kripteia-python.log y kripteia-rust.log.

## Análisis de Seguridad (Kripteia Security)

Ambos análisis: No security issues found. La revisión manual cubre ownership,
conversiones, extracción fallida de tipos y los límites numéricos documentados.
No hay nueva frontera de ejecución externa en el producto; Poppler se ejecuta
solo en tests, sin shell, con rutas temporales y timeout.

## Métricas

- Ocho fuentes revisadas; cero archivos de producto modificados por revisión.
- Hallazgos pendientes: 0.
- Resultados de regresión y Clippy: logs correspondientes.
- Pendiente antes de entrega: CI y merge; registrar resultado exacto al concluir.
