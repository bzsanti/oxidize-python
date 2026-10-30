# Rust core 5.5.5 compatibility

The bridge pins the published registry crate `oxidize-pdf = "=5.5.5"`, with unchanged feature selection and no path override.

Registry checksum: `26295a8746f2b46af857f3e7613eb619773e7ddc028fde8ec1b9cb86092370bb`.

Core fixes cover minimum patched trust-store and key-distrust dependency versions, encrypted object streams, extraction spacing and compact lines, and page generations during signature and document-timestamp preparation. Existing binding parity gaps remain outside this dependency update.

Bridge validation and independent review are pending.
