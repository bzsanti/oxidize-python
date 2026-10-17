# Revisión conversiones Color — #244

## Resumen ejecutivo

Base 2efeec4, crate publicado oxidize-pdf =5.4.2. Rama independiente de #288.
Alcance: siete métodos de conversión/inspección, stubs, consumidor y contrato.
Ocho fuentes revisadas: types.rs, stub, dos consumidores/tests, guard, contrato,
workflow y README. No cambia core, dependencias, constructores ni getters previos.

## Contratos y evidencia

- Oráculos numéricos literales para RGB, CMYK, Gray, negro y blanco; CMYK con
  negro total conserva los canales al inspeccionar y produce RGB negro.
- to_rgb/to_cmyk producen objetos independientes; predicados y nombres Device
  corresponden al espacio almacenado. La fuente mantiene su espacio original.
- cmyk_components convierte mientras getters c/m/y/k anteriores siguen retornando
  cero para RGB. El test distingue ambos contratos para evitar un cambio implícito.
- Constructores aplican clamp; NaN se conserva en Gray y propaga a conversiones.
  No se promete validación de finitud ni gestión ICC. Fórmulas aproximadas del core.
- PDF real con color convertido (.4,.3,.2), raster Poppler y píxel (102,77,51)
  con tolerancia de redondeo. Control negativo en copia desechable sustituye por
  rojo y falla exactamente el raster; wrong-color-control.log.
- 19 tests enfocados correctos; inventario, consumidor estricto y paridad en
  typing.log. Linux Python 3.12 de CI instala Poppler.

El primer intento de tests se lanzó antes de terminar el wheel: BadZipFile al
extraer y luego importación de una extensión anterior sin métodos. Se conservó
premature-wheel.log como evidencia de montaje fallido, no de regresión funcional.
Tras esperar la finalización, se extrajo el wheel completo y focused.log pasó.

## Hallazgos

Sin hallazgos pendientes del incremento. Kripteia señala ratio bajo de asserts
en el raster (2 frente a 12 líneas de montaje); comprobado el oráculo de tres
canales y el fallo discriminante, no requiere asserts redundantes. Se conserva
la observación en el log; no bloquea este contrato.
La inspección manual confirma retornos propios, tupla sin referencias prestadas,
lecturas sin mutación y llamadas directas al core; no añade unsafe, parser ni I/O.

## Calidad de Tests (Kripteia)

Python score 98, cuatro funciones (11 casos), raster score 90 por ratio 14%.
Rust score 100 con cero tests encontrados, lo cual no acredita cobertura.
El binding se prueba desde Python, con fórmulas literales y consumidor PDF real.

## Análisis de Seguridad (Kripteia Security)

Ambos análisis: No security issues found. El binding solo devuelve valores
numéricos, bool, nombres estáticos o copias de Color. Poppler se usa solo en tests
sin shell, con archivos temporales y timeout. No se certifica todo el core.

## Métricas

- Fuentes revisadas: 8; hallazgos pendientes: 0.
- Archivos de producto modificados durante revisión: 0.
- Resultados de regresión y Clippy en los logs correspondientes.
- Pendientes: CI y merge, con reconciliación de cambios concurrentes de #288.


## Revisión de integración con #288

Integrado develop 177987c conservando ambas entradas de CI, todos los tests del
contrato, la sección BlendMode del stub y ambas secciones de documentación.
Binding y tests de Color idénticos por SHA256 al conjunto revisado; se reutilizan
sus análisis Kripteia y el control negativo. El binding de BlendMode corresponde
al PR #288 validado y fusionado. Se repiten build, regresión y tipos sobre el
conjunto integrado por los cambios del contrato/CI. Resultados integrated-*.log.
