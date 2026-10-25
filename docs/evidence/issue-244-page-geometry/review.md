# Revisión de geometría Page — 2026-10-17

## Resumen ejecutivo

Incremento independiente de #244 sobre HEAD 333516184c70fe79bab4e9c735ec38fb6e4ebdb6
más el trabajo local anterior. Core =5.4.2, sin cambios de dependencias.
Se exponen cinco propiedades calculadas de Page: content_width, content_height,
content_area, effective_width y effective_height. No quedan bloqueantes locales.
La evaluación previa de LayoutManager detectó un bloqueo del core; se conserva
su evidencia separada y no se incorpora ese binding.

## Contratos y evidencia

| Contrato | Evidencia | Estado |
| --- | --- | --- |
| Contenido = dimensiones menos márgenes, bounds (left,bottom,right,top) | Página 200x300 con márgenes 11/23/37/41 devuelve 136x252 y (41,37,177,289); segunda asignación cambia resultados | Demostrado |
| Efectivas incluyen rotación; base/contenido no rotan | Cuatro rotaciones con dimensiones asimétricas; lectura directa de MediaBox/Rotate en bytes serializados | Demostrado |
| Márgenes excesivos sin clamping, sistema de coordenadas no cambia getters | -10x-30 y bounds invertidos con pantalla/90° | Demostrado |
| Solo lectura, sin cambios al leer ni tras rotación rechazada | Cinco asignaciones rechazadas, 45° conserva 90° previo | Demostrado |
| Tipos y contrato públicos | typing.log, inventory.log, parity.log y 41 pruebas focalizadas | Demostrado |
| Compatibilidad de biblioteca | regression.log: 2635 passed | Demostrado |

La extensión nativa editable se compiló antes de los tests. Clippy --all-targets
con -D warnings y git diff --check pasan. Se reutiliza la inspección de features:
los cinco métodos de Page son incondicionales del mismo core, y no se cambia
ninguna dependencia ni cfg; no se repite el build sin defaults del incremento
anterior. No se reformatea el archivo completo, que tiene estilo previo.
MCP no cambia y se excluye de la regresión. CI multiplataforma e integración
remota siguen pendientes. La validación local incluye los cambios previos del
checkout; no certifica los borradores TaggedPdf ni la paridad global.

Inspección manual: getters O(1) sin I/O ni asignaciones de estado; retornan f64 o
una tupla propia. No hay unsafe, referencias Python retenidas ni nuevos errores
silenciados. Las pruebas usan números esperados independientes y examinan la
serialización real; no replican la implementación para construir el oráculo.
No se requiere una mutación de alto impacto para estos getters de geometría.
Se mantienen y ejecutan los controles negativos existentes de paridad.

## Hallazgos

1. **LayoutManager Custom no agota espacio**: core page.rs:3862 y :3879 ignoran
   el cursor al comprobar capacidad/espacio restante. El probe reserva cuatro
   elementos y alcanza current_y=-260 con will_fit=true. Corregir la comprobación
   en función del cursor y límites transformados, o rechazar sistemas no
   soportados, antes de prometer prevención de desbordamiento. Evidencia:
   ../issue-244-layout-probe/probe.log. Bloquea ese subcontrato, no estos getters.
2. **Posición PDF de LayoutManager contradice la base descrita**: core
   page.rs:3895 devuelve 180 para cursor 190, alto 40 y espacio 10; la base del
   elemento es 150. Aclarar el contrato y, si se mantiene base inferior como
   indica el comentario, devolver y_position conservando el cursor 140. No se
   corrige ni se expone aquí; queda pendiente bajo #244.

No hay hallazgos pendientes en la implementación de geometría Page.

## Calidad de Tests (Kripteia)

kripteia-python.log: score 100, 4 funciones, 1 archivo (7 casos pytest).
kripteia-parity.log: score 100, 1 función parametrizada, 1 archivo.
kripteia-rust.log: 0 funciones detectadas; las pruebas funcionales se ejecutan
sobre la extensión desde Python. Los scores no sustituyen la evidencia geométrica.

## Análisis de Seguridad (Kripteia Security)

Los tres scans reportan `No security issues found`. Se revisaron manualmente la
frontera PyO3, retorno por valor y ausencia de mutaciones. No es un análisis del
core completo ni una aprobación de LayoutManager.

## Métricas

- Archivos del incremento revisados: 8, con hashes en validation.json; además,
  funciones fuente Page/LayoutManager del core publicado.
- Hallazgos externos: 2; bloqueantes del incremento de getters: 0.
- Archivos de producto modificados durante la revisión final: 0.
- Pendiente: integración remota y CI multiplataforma.
