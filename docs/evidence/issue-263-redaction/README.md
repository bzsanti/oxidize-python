# #263 forensic prerequisite: blocked on core 5.4.2

2026-10-17. Direct Rust probe against the published registry dependency, without
Python binding changes. The fixture is an independently serialized one-page PDF:
Helvetica text `(SECRET) Tj` plus `/Private (SECRET)` in that same font dictionary.
The requested bounding box intersects the visible text. The custom font key is
legal PDF extension data; even unsupported data must be removed or rejected
before claiming irreversible removal.

Reproduce from this directory (use a target directory outside the evidence):

```sh
cargo run --offline --manifest-path probe/Cargo.toml --target-dir /tmp/redaction-probe-target -- input.pdf /tmp/redaction-output.pdf
qpdf --check /tmp/redaction-output.pdf
qpdf --qdf --object-streams=disable /tmp/redaction-output.pdf /tmp/redaction-output.qdf.pdf
rg -a 'SECRET' /tmp/redaction-output.qdf.pdf
pdftotext /tmp/redaction-output.pdf -
```

Observed: `irreversible=true risks=[]`, empty extracted page text, but qpdf
recovers `/Private (SECRET)`. Retained output.pdf and output.qdf.pdf record the
actual result. This proves a residual-data failure, not merely an unsupported
input rejection. No binding or core correction, external issue/comment, or
security guarantee is published here.

Source in the pinned crate: semantic_redactor.rs:607 accepts the Standard-14 font
without rejecting extra keys, :516 reconstructs a page with preserved resources,
and :1235 verifies metadata/text operations rather than all preserved font data.
Required closure: strip/reject unsupported retained resource data and test
independent forensic inspection before exposing `redact_irreversible` as safe.
This blocks #263 acceptance, not the coordinate-transformation increment #244.
