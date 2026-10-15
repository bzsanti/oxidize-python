## Resumen ejecutivo

Revisión de #280 sobre develop 28655ed6 más el diff de esta entrega: binding
Rust/PyO3, exports/stubs, contrato, consumidores, tests, documentación y CI.
La API conserva la inspección de oxidize-pdf =5.4.2 sin modificar documentos.
Sin hallazgos pendientes del incremento. La revisión local está completa;
aceptación de CI y merge se registran después. No certifica PDF/UA.

## Contratos y evidencia

| Contrato y fuente | Contraejemplo / consumidor / resultado |
| --- | --- |
| Todos los campos públicos de verification/tagged_pdf.rs 5.4.2 | Comparación manual campo a campo; conversión exhaustiva de 27 códigos; snapshots tipados; consumidor mypy sin Any |
| Payload original y referencias | Fixture PDF escrita sin el writer del producto; qpdf confirma generación 7, parent owner y bytes 00ff; tests verifican mapas, elementos, artefactos y MCIDs |
| Cuatro presupuestos del core | Cero debe fallar; contenido crudo/Flate pasa con longitud exacta y falla con un byte menos; seis casos discriminantes |
| Fallos y hallazgos distintos | Ciclos y owner incorrecto producen reportes inválidos; malformed/cifrado producen PdfParseError/PdfEncryptionError; ausencia de tags es warning válido |
| Ownership y FFI | Bytes y opciones propios antes de py.detach, sin punteros/unsafe; resultados frozen y contenedores clonados; mutar snapshots no cambia informe |

`focused.log`: 27 passed. `regression.log`: 2826 passed, 1 skipped antes de añadir
los tres casos de cifrado/frontera (verificados después en el conjunto focalizado).
Guards de paridad y tipado: 475 exports públicos; mypy --strict --disallow-any-expr
sobre tests/typing/tagged_validation.py sin errores; rustfmt del módulo limpio.
No cambiaron Cargo.toml ni Cargo.lock (Rust 2021, MSRV 1.88, PyO3 0.28).

Mutación ejecutada en copia desechable /tmp/issue-280-mutant: sustituir en
validate_tagged_pdf `options.map(|v| v.inner).unwrap_or_default()` por
`core::TaggedPdfValidationOptions::default()`, conservando el argumento. Compilar
con maturin build --locked, extraer wheel a directorio aislado e insertarlo antes
del import; ejecutar pytest -k 'each_budget_is_effective or decoded_byte_limit_boundary'.
`mutant.log`: seis fallos DID NOT RAISE PdfError, exit 1; ninguna dependencia o
fixture fallida. La extensión instalada original permanece intacta y los seis
casos pasan con ella. La prueba discrimina el paso real de opciones al core.

Límite comprobado de alcance: los budgets del validador no acotan copia inicial,
parsing previo ni memoria/tiempo global; README lo declara. El editor TaggedPdf
queda en #262 y OCR en #278/#279; ninguno es necesario para este lector.

## Hallazgos

Sin hallazgos pendientes. Durante revisión se precisaron las excepciones en los
tests (PdfError/PdfParseError) y se documentó el alcance real de los presupuestos.
La ausencia de Lang es Error en core, no Warning: la expectativa inicial de test
se corrigió tras consultar la fuente; no se cambió el contrato del producto.

## Calidad de Tests (Kripteia)

`kripteia-python.log`: score 100, 10 funciones, 1 archivo (19 casos pytest).
Sin offenders con penalización. `kripteia-rust.log`: score 100, 0 tests/0 archivos
de tests: no es cobertura Rust; la lógica se ejercita desde la extensión Python.
Los scores no sustituyen la fixture independiente ni la mutación.

## Análisis de Seguridad (Kripteia Security)

Ambos logs: “No security issues found.” Inspección manual adicional de conversiones
unsigned, clonación antes de liberar GIL, ausencia de unsafe/I/O externo en el
binding y propagación de errores. No hay rutas de shell/red ni secretos de
producto; contraseñas de test locales. El backend y parser no se reauditan como
biblioteca completa; su límite de parsing previo se expone expresamente.

## Métricas

- 12 archivos de implementación, integración y documentación revisados; evidencia adicional leída.
- Hallazgos pendientes: 0.
- Archivos de producto modificados por la revisión: 0 (ajustes de tests/documentación dentro de la entrega autorizada).
- Verificaciones pendientes: CI del commit final.
