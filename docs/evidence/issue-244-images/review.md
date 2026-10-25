# Revisión del incremento de imágenes de #244

## Resumen ejecutivo

Base 838f6b6, core =5.4.2 y PyO3 0.28. Construcción raw/RGBA/gris e inspección
de payload, formato, profundidad, alpha y máscara. No cambia el core ni activa
external-images. Quedan fuera creación/aplicación de máscaras, el objeto escritor
y from_file_raw; no se declara paridad completa de Image ni de #244.
El borrador TaggedPdf previo no pertenece a esta entrega.

## Contratos y evidencia

| Contrato | Evidencia | Estado |
| --- | --- | --- |
| Espacios de color y profundidades | RGB/CMYK/gris, 1/2/4/8/16 bits y filas de ancho no múltiplo de byte; header y stream PDF inspeccionados independientemente | Demostrado |
| RGBA y transparencia | Separación RGB/alpha, SMask y render Poppler con rojo opaco, verde semitransparente y fondo blanco | Demostrado |
| Datos/formato/ownership | Bytes exactos, JPEG codificado/PNG decodificado, máscara válida tras eliminar original, propiedades sin setter | Demostrado |
| Validación previa | Dimensiones cero/overflow, tamaños incoherentes, profundidad inválida y unsigned; no-op mutante del guard detectado | Demostrado |
| Contrato público | Dos enums, tres constructores, cinco getters, stubs y consumidor estricto actual/Python 3.10 | Demostrado |

focused.log: 48 passed (32 casos nuevos, ocho históricos de Image, ocho gate).
regression.log: 2606 pruebas de biblioteca aprobadas, sin MCP; incluye el borrador
local TaggedPdf. La entrega aislada excluirá ese borrador y tendrá evidencia
propia. mutation.log: diez fallos esperados DID NOT RAISE al quitar solo el guard
de from_raw_data; dos casos de otros constructores siguen pasando. Mutante
compilado en /tmp/oxidize-244-image-mutant y cargado solo en un proceso separado;
no sustituye la extensión instalada ni modifica fuentes originales.

Inspección de código: cálculo checked del tamaño de fila antes de multiplicar
por altura; redondeo por fila, no del total de bits; copia de entrada posterior a
validación. Guards u32 independientes antes del producto interno de core para
RGBA/gris. Conversiones exhaustivas de enums. Datos RGBA propios antes de detach;
soft_mask y bytes retornan snapshots. Page.add_image clona la imagen, y las
pruebas pasan por ese consumidor y la escritura real. No unsafe ni dependencias
nuevas; sin I/O en las nuevas API. No se modifica comportamiento de loaders
JPEG/PNG/TIFF existentes.

## Hallazgos

Sin hallazgos pendientes en el incremento. Los productos u32 sin comprobación
en los constructores de core se protegen en la nueva frontera Python mediante
checked_mul y pruebas de overflow; no se infiere que el core haya sido corregido.
El soporte de máscaras adicionales y features opcionales sigue bajo #244/#262,
fuera del contrato acotado de construcción e inspección aquí demostrado.

## Calidad de Tests (Kripteia)

kripteia-python.log: 98, ocho funciones y un archivo. La penalización de
 test_poppler_pixels_and_alpha interpreta skipif como ignore; el caso se ejecutó
localmente y pasó. CI Linux 3.12 exige qpdf, pdftotext y pdftoppm. Sin esos tools
el caso externo es condicional en otras plataformas, no la inspección de streams.
kripteia-rust.log: 100, cero tests detectados; no representa cobertura Rust.
Las pruebas invocan la extensión real; diez fallos del mutante prueban que
reclaman el rechazo, no simplemente que los constructores devuelven un objeto.

## Análisis de Seguridad (Kripteia Security)

Ambos análisis sin hallazgos. Inspección adicional de overflow, longitud, tamaño
de fila, ownership y memoria antes de llamar al core. Los límites de argumento
no se presentan como una cuota global de memoria; inputs ya materializados son
propiedad del llamante. No hay red, shell, secretos ni código unsafe en el binding.
Los subprocess de test usan herramientas fijas y archivos temporales sintéticos.

## Métricas

- Once archivos de producto, integración, tipos, tests y documentación revisados.
- Hallazgos pendientes: cero dentro del incremento.
- Pendientes: validación de entrega aislada, CI multiplataforma e integración.

## Entrega aislada

Rueda compilada sobre develop 838f6b6 sin TaggedPdf: 2591 pruebas de biblioteca
aprobadas, 485 exports nativos y 486 públicos. Inventario/gate, mypy del paquete
(26 archivos) y consumidor estricto aprobados. Clippy con warnings como errores
y compilación sin default features aprobados. Los análisis de gate/workflow
no encuentran problemas de seguridad; el scan YAML no sustituye el CI.
Hashes de fuentes de entrega en validation.json. Pendientes: CI remota y merge.
