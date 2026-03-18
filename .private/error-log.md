# Error Log

[2026-03-16] Cargo.toml apuntaba a crates.io 2.3.1 pero las APIs nuevas (overlay, reorder, extract_images_from_pdf) no compilaban

- Qué hice mal: Asumí que oxidize-pdf 2.3.1 no tenía las APIs y cambié a path local sin verificar si una versión más reciente (2.3.2) las tenía
- Causa raíz: No verifiqué todas las versiones publicadas. La 2.3.2 ya incluía las APIs necesarias
- Cómo lo solucioné: Cambié a `version = "2.3.2"` — compila y pasa los 240 tests
- Regla para evitarlo: Antes de cambiar a `path` local, verificar la última versión publicada en crates.io. Usar `path` solo como último recurso

[2026-03-16] ExtractImagesOptions tiene campo `create_dir` no `create_output_dir`

- Qué hice mal: Usé `create_output_dir` como nombre del campo basándome en la exploración del agente
- Causa raíz: El agente de exploración reportó correctamente pero yo escribí un nombre diferente del real
- Cómo lo solucioné: Cambié a usar `ExtractImagesOptions::default()` y setear solo `output_dir`
- Regla para evitarlo: Usar `Default::default()` y setear campos individualmente en lugar de struct literals cuando hay muchos campos que podrían cambiar entre versiones

[2026-03-16] Tests usaban Rectangle(x1, y1, x2, y2) pero el constructor Python es Rectangle(Point, Point)

- Qué hice mal: Escribí tests asumiendo Rectangle(x1,y1,x2,y2) sin verificar el constructor existente
- Causa raíz: No leí types.rs antes de escribir los tests de annotations
- Cómo lo solucioné: Cambié a Rectangle(Point(x1,y1), Point(x2,y2)) en todos los tests
- Regla para evitarlo: Verificar siempre constructores de tipos existentes antes de usarlos en tests nuevos

[2026-03-18] FontEncoding type mismatch: top-level re-export vs text::FontEncoding

- Qué hice mal: Usé `oxidize_pdf::FontEncoding` (re-exportado de `text::fonts::embedding`) para `PyFontEncoding`, pero `set_default_font_encoding` requiere `oxidize_pdf::text::FontEncoding` (de `text/font.rs`) — tipos diferentes con el mismo nombre
- Causa raíz: oxidize-pdf tiene dos enums `FontEncoding` en módulos distintos. El re-export top-level apunta al de embedding, pero el método de Document usa el de text::font
- Cómo lo solucioné: Cambié `pub inner: oxidize_pdf::FontEncoding` a `pub inner: oxidize_pdf::text::FontEncoding` en PyFontEncoding
- Regla para evitarlo: Cuando cargo check reporta type mismatch entre mismo tipo, verificar si hay múltiples tipos con el mismo nombre en distintos módulos. Usar la ruta completa del módulo que coincide con la firma del método destino

[2026-03-18] Page() requiere width y height pero los tests usaban Page()

- Qué hice mal: Escribí tests con `Page()` sin argumentos sin verificar el constructor
- Causa raíz: No verifiqué el constructor de Page antes de escribir los tests (error recurrente — ya documentado previamente para Rectangle)
- Cómo lo solucioné: Cambié a `Page(612.0, 792.0)` en todos los tests
- Regla para evitarlo: SIEMPRE verificar constructores de tipos existentes leyendo page.rs antes de usarlos en tests nuevos. Esta regla aplica a todos los tipos del bridge.
