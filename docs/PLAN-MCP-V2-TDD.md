# Migración al SDK MCP v2 mediante TDD

Fecha: 2026-09-25. Estado: implementación y validación local completadas; revisión y CI pendientes.
Evidencia y límites: [MCP-V2-VALIDATION.md](MCP-V2-VALIDATION.md).
Base inspeccionada: `develop`, `81a74e6`, paquete 0.19.0.

## Objetivo y decisiones

Una instalación limpia de `oxidize-pdf[mcp]` debe resolver SDK MCP 2.x y
servir por stdio las 12 herramientas, 5 recursos estáticos, 1 plantilla de
recurso y 5 prompts existentes, conservando los workflows PDF y los clientes
anteriores. La biblioteca sin extras debe seguir funcionando sin MCP.

- Mantener `from fastmcp import FastMCP` y migrar a FastMCP 4.x. El cambio
  `FastMCP` → `MCPServer` del SDK oficial no implica sustituir nuestra clase,
  que procede del paquete independiente `fastmcp`.
- Rangos objetivo: `fastmcp>=4,<5`, `mcp>=2,<3`; ajustar los mínimos a la
  primera combinación estable validada. Declarar también `mcp-types` si se
  importa directamente, con el rango compatible con esa combinación.
  Verificar los metadatos de distribuciones publicadas, no solo la rama main.
- Conservar Python >=3.10. Validar 3.10–3.14, pues 3.14 ya está anunciado en
  los clasificadores aunque falta en la matriz de CI. Si la resolución no
  permite ese soporte, registrar el bloqueo antes de cambiar el mínimo.
- Soporte de transporte comprometido: stdio. Clientes SDK v2 y SDK v1
  aislados; comprobar protocolo moderno y revisión legacy 2025-11-25.
- Conservar `SessionStore` y los `session_id` de creación PDF. Son estado de
  aplicación, independiente de las sesiones del protocolo.
- Sin nuevos tools, OAuth, HTTP, tasks, cambios del core Rust ni nuevas
  opciones de extracción. No adoptar mecanismos nuevos de sesión sin una
  necesidad demostrada por pruebas.
- Mantener `uv.lock` local preexistente intacto. Rangos en los metadatos del
  paquete; restricciones reproducibles de pruebas en archivos nuevos propios.

## Evidencia inicial y riesgos concretos

- Entorno inspeccionado: FastMCP 3.1.1, SDK 1.26.0, Pydantic 2.12.5.
- `pyproject.toml` declara `fastmcp>=2.0` sin techo y excluye MCP de mypy.
- Los 12 módulos de herramientas importan `ToolAnnotations` desde `mcp.types`
  y emplean campos camelCase. Hay accesos similares en tests de contratos.
- La fixture `mcp_client` utiliza `Client(mcp)` en memoria. No acredita el
  arranque del ejecutable, el empaquetado ni la interoperabilidad stdio.
- CI instala `fastmcp` por separado, sin usar el extra declarado del proyecto.
- En `oxidize-pdf-integrations`, `claude-code/bin/launch-mcp` instala el paquete
  base y solo comprueba `import oxidize_pdf`; puede aceptar un entorno sin MCP.
  El manifiesto del registry tampoco expresa actualmente el extra MCP.
- `oxidize://capabilities` anuncia `{id}` pero la plantilla registrada usa
  `{session_id}`. Añadir un contrato de consistencia antes de corregirlo.
- `MCP_SERVER_VERSION = "1.0.0"` es independiente de la versión del paquete;
  no confundir ninguna de ellas con SDK 2.x. Conservar esa semántica salvo
  decisión documentada y comprobar los metadatos anunciados.

## Disciplina TDD

Cada comportamiento nuevo o corrección seguirá **RED → GREEN → REFACTOR**:

1. Escribir el test y ejecutar el caso focalizado; registrar el fallo esperado.
2. Aplicar el cambio mínimo y ejecutar ese caso más la regresión afectada.
3. Refactorizar manteniendo verdes los mismos contratos.

No basta un fallo de importación general para demostrar cada comportamiento.
Los tests de caracterización pueden pasar en v1: su propósito es fijar la
compatibilidad antes de cambiar dependencias. Los contratos nuevos de SDK v2,
empaquetado y correcciones sí deben mostrar su RED correspondiente. Conservar
las aserciones funcionales existentes; no debilitarlas para acomodar v2.
Usar clientes reales para protocolo y PDFs reales para resultados; no mocks
del transporte como prueba de interoperabilidad. Registrar comandos, versiones
y resultado RED/GREEN por bloque en la descripción del cambio.

## Secuencia de ejecución

### 0. Establecer baseline y resolver dependencias

- [x] Crear rama de trabajo y registrar estado inicial en ambos repositorios.
- [x] Ejecutar suite MCP en el entorno actual y guardar resultado; las 2513
  pruebas del handoff son evidencia histórica, no una ejecución de este plan.
- [x] En entornos nuevos, resolver candidatos estables FastMCP 4 / SDK 2 para
  cada Python soportado; guardar informes del instalador y `pip check`.
- [x] Seleccionar versiones exactas para restricciones de CI y mínimos de
  distribución. Probar mínimos y últimas versiones admitidas por los rangos.

Salida: combinación instalable documentada y baseline reproducible. No migrar
el entorno de trabajo existente como sustituto de una instalación limpia.

### 1. Fijar contratos públicos antes del cambio

Archivos: `tests/mcp_tests/test_tool_definition_quality.py`, `test_resources.py`,
`test_prompts.py`, `test_integration.py`; nuevo `test_protocol_contract.py`.

- [x] Caracterizar catálogo exacto, parámetros requeridos, defaults, enums,
  anotaciones de efectos, formatos de respuesta y argumentos de los prompts.
- [x] Comprobar los 5 recursos, la plantilla completa y su lectura real.
- [x] RED: exigir consistencia entre catálogo anunciado y registrado; GREEN:
  corregir la plantilla anunciada conservando las URI concretas existentes.
- [x] Fijar resultados semánticos, no snapshots de descripciones enteras ni
  orden de propiedades JSON. Reutilizar las comprobaciones ya existentes.

Salida: contrato externo verificable, sin depender de atributos privados.

### 2. Migrar dependencias y API de tipos

Archivos: `pyproject.toml`, `python/oxidize_pdf/mcp/tools/*.py`, `server.py`,
`tests/mcp_tests/conftest.py` y tests afectados; nuevo `test_sdk_v2.py`.

- [x] RED: test de versión instalada SDK 2.x y arranque/descubrimiento real;
  demostrar que el entorno baseline no satisface el requisito de versión.
- [x] GREEN: declarar rangos seleccionados, migrar imports de tipos y campos
  Python a snake_case conforme a las APIs publicadas elegidas.
- [x] Verificar serialización JSON-RPC mediante alias de protocolo: no hacer
  reemplazos globales de camelCase en mensajes JSON ni en esquemas wire.
- [x] Migrar cliente de pruebas y APIs retiradas solo donde se usan. Ejecutar
  contratos del bloque 1 y las pruebas funcionales de las 12 herramientas.
- [x] Tratar avisos de deprecación de nuestros usos de MCP/FastMCP como errores,
  con cualquier excepción de terceros concreta y justificada.
- [x] REFACTOR: eliminar adaptaciones temporales para v1 del código servidor;
  la interoperabilidad legacy se prueba en el transporte.

Salida: servidor y suite en memoria verdes sobre SDK 2, sin usar los puentes
de deprecación como implementación definitiva.

### 3. Interoperabilidad stdio y ciclo de vida

Nuevo `tests/mcp_tests/test_stdio.py` y scripts cliente de integración aislados.

- [x] Crear harness con workspace temporal, timeout acotado, captura separada
  de stderr y cierre de proceso garantizado en éxito y error.
- [x] Cliente oficial SDK v2 → ejecutable `oxidize-mcp`: conexión moderna,
  descubrimiento, recursos, prompts, llamada real y cierre. Confirmar la
  revisión usada; no aceptar fallback silencioso como prueba de modo moderno.
- [x] Cliente SDK v1 fijado en otro entorno → mismo servidor v2: initialize,
  revisión legacy y mismas operaciones. Nunca instalar v1 y v2 en un proceso.
- [x] Verificar stdout reservado al protocolo y arranque tanto por ejecutable
  como por `python -m oxidize_pdf.mcp.server`.
- [x] Casos negativos: argumentos inválidos, herramienta desconocida, PDF
  ausente, ruta fuera del workspace y sesión PDF inexistente; distinguir error
  de protocolo, error de herramienta y respuesta de negocio según contrato.
- [x] RED antes de cada ajuste necesario; GREEN con implementación mínima.
  Si un contrato ya pasa, conservarlo como regresión sin inventar un fallo.

Salida: evidencia por cliente/revisión y ningún proceso abandonado. La prueba
del launcher no sustituye una comprobación manual en un host real disponible;
registrar versión del host o indicar explícitamente si no pudo ejecutarse.

### 4. Workflows y sesiones PDF

Archivos existentes: `test_integration.py`, `test_sessions.py`, tests de tools.

- [x] Reutilizar workflows actuales para crear → añadir → guardar → releer
  PDF y comprobar texto/páginas, también a través de stdio.
- [x] Preservar `session_id` entre peticiones, independencia de dos documentos,
  expiración y límite de sesiones. No prometer persistencia tras reiniciar.
- [x] Añadir casos de concurrencia solo donde el cambio del framework afecte
  a handlers síncronos o estado compartido; coordinar con eventos/barreras,
  evitando tests basados en sleeps o ratios de velocidad.
- [x] Toda regresión descubierta se reproduce primero con test focalizado.

Salida: resultados PDF y aislamiento de documentos conservados, sin ligar
su estado al handshake del protocolo.

### 5. Distribución, launcher y registry

Nuevos tests de instalación desde wheel; en el hermano, pruebas del launcher
y del comando derivado de `mcp/server.json`.

- [x] RED: wheel con `[mcp]` debe instalar SDK 2 y arrancar fuera del checkout.
  GREEN: corregir metadatos, extras o entry point que lo impidan.
- [x] Wheel base en otro entorno: generar/leer PDF y comprobar que no requiere
  `fastmcp`, `mcp` ni `mcp-types`. No usar dependencias globales ni PYTHONPATH.
- [x] RED del launcher: entorno con solo paquete base no cuenta como servidor
  listo. GREEN: instalar `[mcp]` y comprobar disponibilidad real del servidor.
- [x] Cubrir instalación nueva y actualización del entorno legacy, conservando
  las opciones de omitir actualización y el intervalo configurado.
- [x] Validar esquema oficial del registry y ejecutar su comando exacto con
  extras. Seleccionar la representación admitida por ese esquema; no inventar
  campos. Antes de publicar, usar el wheel candidato en un índice/directorio
  de prueba y registrar cualquier diferencia con el arranque de producción.
- [x] Preservar la eliminación local previa de `claude-code/.mcp.json`; trabajar
  en checkout aislado del hermano si hace falta, sin restaurar ese archivo.

Salida: consumidores limpios arrancan y ejecutan una operación real sin que
el checkout ni una instalación previa oculten dependencias faltantes.

### 6. CI, documentación y entrega

- [x] CI instala desde extras/metadatos del proyecto, con resolución mínima y
  reciente en jobs acotados; matriz funcional Python 3.10–3.14 en Linux,
  macOS y Windows. Stdio v2 en la matriz; cliente v1 al menos en Linux.
- [x] Añadir comprobación explícita de tipado MCP: la exclusión actual de mypy
  hace insuficiente el comando global. Retirar exclusión o usar configuración
  dedicada; sin silenciamientos globales para hacer pasar el análisis.
- [ ] Suite Python completa, contratos, stdio, instalación base/con extras,
  tipado existente y MCP, `pip check`, build wheel/sdist y `git diff --check`.
  Conservar checks Rust existentes en CI; sin reformateo masivo de Rust.
- [x] Documentar versiones mínimas, matriz probada, instalación `[mcp]`,
  compatibilidad legacy y cambios observables; actualizar README, notas de
  release y documentación pertinente del hermano. Conservar el texto acordado
  sobre dependencias C.
- [ ] Preparar release 0.20.0 como versión propuesta y PRs coordinados; no mover
  tags 0.19.0. Publicación y registry quedan para autorización de publicación.

## Criterios finales de aceptación

Todos los bloques anteriores completados, con fallos RED y ejecuciones GREEN
documentados para los cambios; SDK 2 acreditado desde instalación limpia;
contratos de 12 herramientas/5 recursos/1 plantilla/5 prompts preservados;
stdio moderno y legacy verificados; workflows PDF íntegros; base sin MCP;
launcher y registry reproducibles; matriz y tipado aprobados. Un fallo de
resolución, fallback no detectado o prueba saltada de estos criterios impide
declarar terminada la migración.

Rollback antes de publicación: revertir commits de migración y volver a las
restricciones baseline en entornos nuevos. Después, recomendar temporalmente
0.19.0 con la combinación legacy comprobada y preparar corrección; no alterar
artefactos publicados ni confiar en el extra antiguo sin límites superiores.

## Fuentes oficiales consultadas

- [SDK: migración v1 → v2](https://py.sdk.modelcontextprotocol.io/migration/):
  cambios de tipos/imports, campos Python y clientes.
- [FastMCP: migración desde 3](https://gofastmcp.com/getting-started/upgrading/from-fastmcp-3):
  cambios del framework que usamos.
- [FastMCP 4 estable](https://blog.gofastmcp.com/3mufbh2vcv22o): disponibilidad
  y compatibilidad anunciada con clientes anteriores; se verificará localmente.
- [Metadatos del repositorio FastMCP](https://github.com/PrefectHQ/fastmcp/blob/main/pyproject.toml):
  referencia de desarrollo; no reemplaza la inspección de wheels publicados.

La ejecución seleccionó FastMCP 4.0.9 / SDK 2.2.0 / mcp-types 2.2.0.
Los resultados locales y los criterios todavía pendientes de CI/host/publicación
se registran en MCP-V2-VALIDATION.md.
