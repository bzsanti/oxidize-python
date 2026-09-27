# Native-free certificate verification

Tracked by https://github.com/bzsanti/oxidizePdf/issues/627.

The binding pins oxidize-pdf =5.1.5 from crates.io, which uses oxidize-webpki
0.1.0, rustls-pki-types and RustCrypto/Dalek for public-key signature verification.
WebPKI retains chains, trust anchors, dates, constraints, key usage and CRLs.
Unsupported inputs fail rather than bypass verification. No private-key signing
or custom cryptographic arithmetic was introduced by this dependency update.

The production graph must contain no bundled C/C++/assembly implementation or
native compiler dependency. PyO3's Python interpreter ABI and platform system
interfaces are distinguished from bundled native cryptography. Rust-only source
is not a security certification; existing upstream cryptographic limitations
still apply. Optional Tesseract is not enabled by this binding.

CI runs the core's source/dependency policy on the actual binding graph for all
five release targets, and runs builds with CC/CXX disabled. The copied MIT
policy script originates from oxidizePdf PR #631; its PyO3 ABI exception is
version-specific and must be reviewed when PyO3 changes.

The legacy aggregate verify_pdf_signatures boolean is a separately tracked
pre-existing limitation; certificate tests inspect is_trusted/is_valid rather
than treating that aggregate flag as proof of verification.
