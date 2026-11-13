# 0.24.0

- Update the exact Rust core dependency to 5.6.0.
- Expose opt-in visual line ordering, incomplete ToUnicode encoding fallback, and annotation appearance extraction.
- Preserve annotation appearance object identity in recovery diagnostics.
- Align the default TJ spacing threshold with the core at 0.17; an explicit 0.2 retains the previous sensitivity.

See [compatibility and limits](docs/UPSTREAM-5.6.0.md). Broader API parity is outside this release.
