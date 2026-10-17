# Revisión del incremento de coordenadas — 2026-10-17

## Resumen ejecutivo

Base 333516184c70fe79bab4e9c735ec38fb6e4ebdb6 más cambios locales inventariados
en validation.json. PyO3 0.28, core registry =5.4.2, Python 3.12. Se revisaron
TransformMatrix, ampliación de CoordinateSystem, getter Page, exports/stubs,
contrato, pruebas, CI y documentación. No quedan bloqueantes del incremento.
La revisión no acepta ni incorpora como entrega los borradores preexistentes de
TaggedPdf/validación. No se modifica el core ni se publica una versión.

## Contratos y evidencia

| Contrato | Evidencia | Estado |
| --- | --- | --- |
| Seis componentes propios e inmutables, identidad, traslación, escala, rotación en radianes, inversión Y | test_components_and_immutable_snapshot y test_composition_order_and_factories; puntos asimétricos y cuarto de vuelta | Demostrado |
| Composición self * other sin cambiar operandos | (18,13) frente a (28,3) distingue el orden; operandos mantienen sus resultados | Demostrado |
| Matriz/punto/Y y orientación en PDF, pantalla y custom | test_coordinate_conversions_and_custom_semantics; custom Y evalúa x=0, orientación d>0 | Demostrado |
| Page almacena un sistema y devuelve copia | test_page_coordinate_system_snapshot tras dos cambios del sistema | Demostrado |
| Frontera de tipos y semántica f64 del core | Tipos incorrectos rechazados; singular/NaN/inf preservados y documentados | Demostrado |
| Exports, stubs, firmas, consumidores y guard | inventory.log, typing.log, parity.log, contract-regression.log | Demostrado |
| Regresión de biblioteca | regression-final.log: 2622 passed | Demostrado |

Compilación nativa editable (build.log), Clippy con -D warnings y comprobación
sin features predeterminadas pasan. rustfmt --check pasa en el módulo nuevo;
no se reformatea tier8/page completos, que conservan el estilo previo.
La regresión usa el checkout con los cambios previos, no un wheel aislado.
MCP no se modifica ni se incluye en esta regresión. CI multiplataforma e
integración remota siguen pendientes; se añade el consumidor tipado a CI.

La primera regresión detectó el test omitido de la copia temporal del checker y
las firmas nuevas sin self en el JSON. Se corrigieron ambos; las 15 pruebas de
contrato y la regresión completa final pasan. Se conserva regression.log para
trazabilidad, no como resultado final. No se añadió una mutación de runtime:
el incremento es geometría sin permisos, persistencia ni cambios de disponibilidad;
los casos geométricos distinguen orden, coeficientes y snapshots, y los ocho
controles negativos existentes del guard pasan.

Inspección manual: operaciones constantes sobre valores copiados, sin I/O ni
unsafe añadido, sin referencias a objetos Python retenidas, sin ejecución costosa
que requiera liberar GIL. to_pdf_ctm produce texto numérico; no certifica que
valores no finitos sean PDF válido. Page.set_coordinate_system no aplica una CTM
al contenido en el core publicado, limitación explícita en README.

## Hallazgos

1. **#263 conserva datos tras afirmar eliminación irreversible**: core
   `operations/semantic_redactor.rs:607`, `:516` y `:1235` aceptan/preservan claves
   extras en fuentes y verifican texto/metadatos, permitiendo `/Private (SECRET)`
   en la salida con `irreversible=true`. Reproducido con qpdf y probe Rust en
   `../issue-263-redaction/`. Corregir mediante eliminación o rechazo de datos
   no admitidos en recursos y verificación forense independiente. Bloquea #263,
   que no se expone en este incremento; no bloquea las conversiones de #244.

## Calidad de Tests (Kripteia)

kripteia-python.log: score 100, 5 funciones, 1 archivo.
kripteia-parity.log: score 100, 1 función parametrizada, 1 archivo.
Los tres análisis Rust reportan 0 funciones de test; las pruebas de integración
son Python sobre la extensión real. El score Rust no demuestra cobertura.

## Análisis de Seguridad (Kripteia Security)

Los cinco logs (Python, parity, Rust, tier8 y page) reportan
`No security issues found`. La revisión manual de las nuevas fronteras no
confirma riesgos pendientes. Estos scans no cubren ni absuelven el redactor del
core: su fallo fue demostrado por el probe independiente.

## Métricas

- Archivos revisados del incremento: 15 (listados en validation.json).
- Hallazgos abiertos del incremento: 0; hallazgo externo confirmado: 1 (#263).
- Archivos de producto modificados durante la revisión final: 0.
- Verificaciones pendientes: CI multiplataforma e integración remota.
