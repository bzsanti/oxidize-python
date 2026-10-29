# oxidize-pdf 0.23.1

- Upgrade PyO3 from 0.28.3 to 0.29.2, resolving RUSTSEC-2026-0176 and RUSTSEC-2026-0177.
- Update the exact Rust core dependency from 5.5.0 to the published 5.5.4, including ECDSA dependency remediation for RUSTSEC-2026-0387 and intervening PDF correctness fixes.
- Preserve the public Python API and Python >=3.10 abi3 wheels for Linux x64/ARM64, macOS x64/ARM64 and Windows x64.

See [core compatibility](docs/UPSTREAM-5.5.4.md) for dependency identities and validation. Local validation with PyO3 0.29.2 passed 3,117 tests with two pre-existing skips, typing/parity, Clippy and the native dependency policy. Platform and publication gates are tracked in #299.

The audit no longer reports the two PyO3 advisories; the pre-existing RSA RUSTSEC-2023-0071 and informational unsound/yanked warnings remain. No new advisory suppression is added. This is not an advisory-free dependency claim.

Missing OCR and other parity APIs remain tracked separately. Incremental changes preserve history and are not irreversible redaction. Batch timeouts do not interrupt work or roll back output. See the compatibility notes for changed core behavior and supported binding operations.

Install: `pip install oxidize-pdf==0.23.1`.
