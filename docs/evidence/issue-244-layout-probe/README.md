# LayoutManager: prerrequisito pendiente

Core registry =5.4.2; probe Rust directo, sin cambios al core ni al binding.
`layout_probe.rs` se puede ejecutar como binario de un crate con dependencia
`oxidize-pdf = { version = "=5.4.2", default-features = false, features = ["compression", "semantic"] }`.
Se compiló offline como binario adicional del crate de probe de redacción ya
preparado en /tmp/oxidize-redaction-probe. Resultado real en probe.log.

La rama Custom de will_fit (page.rs:3862) ignora current_y; remaining_space
(:3879) devuelve una constante. Se aceptan reservas fuera de la página sin
agotamiento observable. Para PDF estándar, add_element (:3895) devuelve
current_y anterior menos spacing, no la base que describe su comentario.
La aceptación de LayoutManager requiere resolver la geometría y el agotamiento
con pruebas independientes. No se presenta como prevención de solapamientos.
Este hallazgo no bloquea los getters de geometría de Page, que no reservan espacio.

Para repetir con el manifiesto incluido, desde la raíz del repositorio:

```sh
cargo run --offline --manifest-path docs/evidence/issue-244-layout-probe/Cargo.toml --target-dir /tmp/oxidize-layout-manager-probe-target
```

El manifiesto es standalone; no se ha añadido al workspace ni a las dependencias
del binding. El probe afirma el comportamiento defectuoso para hacerlo visible;
su código de salida cero no significa que LayoutManager cumpla el contrato.
