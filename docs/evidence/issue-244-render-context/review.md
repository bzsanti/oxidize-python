# Revisión RenderContext — 2026-10-17

## Resumen ejecutivo

Incremento de #244 sobre HEAD 333516184c70fe79bab4e9c735ec38fb6e4ebdb6 y
el trabajo local anterior de coordenadas. Core =5.4.2 y PyO3 0.28. La superficie
RenderContext de coordinate_system.rs queda expuesta: constructor, cuatro campos
públicos mutables y dos métodos. No quedan bloqueantes de este incremento local.
No se certifican los borradores TaggedPdf ni los demás subcontratos de #244.

## Contratos y evidencia

| Contrato/fuente | Contraejemplo y consumidor | Resultado |
| --- | --- | --- |
| Core RenderContext::new inicializa matriz según sistema/altura | Punto (17,19) en PDF/pantalla/custom distingue las tres ramas | Demostrado: test_initial_context_and_conversions, tres casos |
| Mutación de sistema/altura afecta conversiones | Pantalla de 800 a 900: y=781 pasa a 881; cambio a PDF devuelve 19 | Demostrado: test_mutations_use_live_system_and_height_without_refreshing_matrix |
| current_transform es independiente de conversiones | Matriz cero no elimina resultado custom; Y solo usa x=0 | Demostrado: test_custom_context_y_uses_zero_x_and_ignores_cached_transform |
| Lecturas propias y errores sin cambio parcial | Snapshots sobreviven a reemplazos; cuatro asignaciones inválidas preservan estado | Demostrado: pruebas de mutación y test_invalid_assignments_preserve_context |
| Exports, tipos, CI y guard | Constructor, setters y retornos estrictamente tipados; ocho controles negativos del guard | Demostrado: typing.log, inventory.log, parity.log, focused-final.log |

34 pruebas focalizadas y 2628 pruebas de biblioteca pasan sobre la extensión
nativa editable actual (regression.log). Clippy -D warnings, cargo check sin
features predeterminadas, mypy --strict --disallow-any-expr e inventario pasan.
rustfmt --check del módulo afectado y git diff --check pasan. No se ejecutó MCP,
que no cambia. No hay pruebas de geometría que sustituyan al core con un mock.
El orden de ejecución inicial fue incorrecto: focused.log corresponde a import
antes de acabar la instalación, no a un defecto funcional ni a un control RED;
focused-final.log es la ejecución válida tras completar la compilación.

Inspección manual: cada getter retorna copia de valor, cada setter extrae y
valida el tipo Python antes de asignar un único campo; PyO3 conserva la exclusión
de préstamos mutables. Sin referencias Python retenidas, unsafe añadido, I/O ni
trabajo no acotado. No se añaden invariantes numéricos ajenos al core. Los métodos
usan el sistema/altura actuales; leer la matriz almacenada sería una regresión
que las pruebas con matriz cero y cambio de altura detectan. No se introduce
recalculado automático. Estas son operaciones locales de geometría, sin cambios
de permisos, durabilidad o disponibilidad; no requieren mutación de alto impacto.

## Hallazgos

Ningún hallazgo confirmado pendiente en este incremento. La independencia entre
current_transform y conversiones es comportamiento explícito del core, documentado
en README y docstring. El fallo forense de #263 sigue registrado en su evidencia
anterior y no se reabre ni se modifica aquí.

## Calidad de Tests (Kripteia)

kripteia-python.log: score 100, 4 funciones, 1 archivo (6 casos pytest).
kripteia-parity.log: score 100, 1 función parametrizada, 1 archivo.
kripteia-rust.log: 0 funciones de test detectadas; la cobertura funcional está
en Python sobre el módulo nativo. El score del scanner no acredita corrección.

## Análisis de Seguridad (Kripteia Security)

Los tres análisis reportan `No security issues found`. La inspección manual de
FFI, ownership, mutaciones y consumidores no identifica problemas pendientes.
Los análisis no constituyen una revisión del core completo ni de todo el checkout.

## Métricas

- Archivos revisados: 12, inventariados con hashes en validation.json.
- Hallazgos pendientes del incremento: 0.
- Archivos de producto modificados durante la revisión final: 0.
- Pendiente: CI multiplataforma e integración remota; no commit/push/publicación.
