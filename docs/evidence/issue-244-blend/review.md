# Revisión BlendMode — #244

## Resumen ejecutivo

Base oxidize-python 2efeec4. Implementación basada exclusivamente en el crate
publicado oxidize-pdf =5.4.2. No se usa develop del core ni se cambia su pin.
Alcance: seis classattrs, pdf_name y repr exhaustivo, stubs y contratos asociados.
Ocho fuentes revisadas: binding, stub, dos tests/consumidores, guard, contrato,
workflow y README. Sin cambios de dependencias ni de la conexión Page existente.

## Contratos y evidencia

- Tabla literal de los 16 nombres comprueba compatibilidad anterior y seis
  valores nuevos; repr conserva la convención de constantes Python. El match
  Rust es exhaustivo. pdf_name delega al enum del core publicado.
- Valores congelados: asignar método en una instancia falla. PyO3 rechaza string
  en Page.set_blend_mode. El consumidor clona el enum y serializa ExtGState.
- Cada modo nuevo aparece como /BM correcto en el PDF. Poppler renderiza fondo
  gris y fuente roja; se comprueban centro y exterior con tolerancia de 1–2 bytes
  para redondeo. Oráculos derivados de luminosidad 0.3 y mezcla sobre 0.5, no
  copiados del binding ni calculados por el propio escritor bajo prueba.
- Algunos modos coinciden en este fixture; el nombre /BM y el test de nombres
  distinguen esas variantes. El raster comprueba su aplicación, no una batería
  exhaustiva de todas las combinaciones de color del estándar PDF.
- Control negativo sobre copia desechable: forzar NORMAL produce 12 fallos
  (seis nombres /BM y seis colores), sin modificar fuentes de producto.
- 51 tests enfocados pasan. Tipos, inventario y guard: typing.log. La matriz
  Linux 3.12 instala Poppler; otras máquinas pueden omitir solo el raster.

## Hallazgos

Sin hallazgos pendientes en el subcontrato. No se extiende la conclusión al
resto de ExtGState ni a conformidad completa de renderizadores PDF externos.
Revisión manual de parámetros, ownership, retorno estático de nombre, errores
y compatibilidad. El cambio no añade unsafe, archivos, callbacks ni parser.

## Calidad de Tests (Kripteia)

Python: score 100, cuatro funciones (29 casos parametrizados), sin observaciones.
Rust: score 100, cero tests detectados: no demuestra cobertura. El binding se
verifica desde Python y con consumidor PDF independiente. Salidas en logs.

## Análisis de Seguridad (Kripteia Security)

Ambos análisis: No security issues found. Sin nueva frontera de entrada ni
conversión dinámica de nombres. Las constantes contienen variantes Rust cerradas;
la ejecución de Poppler está solo en tests, sin shell y con timeout.

## Métricas

- Fuentes revisadas: 8; hallazgos pendientes: 0.
- Archivos de producto modificados durante revisión: 0.
- Regresión/Clippy: resultados en sus logs.
- CI y merge pendientes al redactar; registrar evidencia final antes del cierre.
