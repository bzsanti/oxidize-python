# oxidize-pdf 0.20.1 — Native-free certificate verification

- Pin the Rust core to published oxidize-pdf 5.1.5, using oxidize-webpki 0.1.0
  from crates.io. No path/Git override and no native cryptography dependency.
- Preserve certificate/signature behavior and the existing Python API.
- Gate production dependency graphs in CI and builds with C/C++ disabled.
- Include fixed external certificate fixtures for binding regression checks.

This implements the binding adoption for bzsanti/oxidizePdf#627. It does not
change the existing aggregate `verify_pdf_signatures` boolean semantics.
