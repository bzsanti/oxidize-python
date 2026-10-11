# Core 5.4.2 update

Status: local validation passed; platform CI pending. Tracking: https://github.com/bzsanti/oxidize-python/issues/241

Pins the official Rust core to exactly 5.4.2 while preserving the binding API and feature flags. Includes the standard-font, text layout, document writing and graphics serialization improvements delivered by core PR #704 (issues #700–#703). Improvements are workload-dependent: the upstream fractional-only uncompressed graphics benchmark takes 3.6% longer; no universal speedup is claimed.

Acceptance: build and regression tests against the registry package, review the dependency changes, and pass platform CI before integration. Package publication is separate from this dependency update.

Core dependency updates are manual by maintainer request (#242). The two automatic PR creation workflows are removed; existing superseded bot PRs are closed.

## Validation and review

2565 tests passed; 2 skipped by existing environment-dependent guards. Wheel build, no-default-features compile, and Clippy passed. No binding runtime source changed. The lockfile changes only oxidize-pdf version/checksum.

Reviewed contract: preserve the public binding API and enabled core features while consuming the official 5.4.2 registry artifact. Existing tests exercise real native PDF generation/extraction, errors and binding boundaries. Upstream #704 performance/serialization validation is reused; no new universal performance claim is made.

Kripteia: text measurement tests score 99 (9 tests); no security findings. The low assertion/setup heuristic reflects different-font comparisons against actual native results. The unmodified Rust source tree has pre-existing rustfmt differences; this dependency-only update does not reformat it. Both PR-opening workflows were disabled through GitHub and are removed here. All 24 superseded bot PRs were closed. Normal CI/release/parity workflows are unchanged.

Evidence: `docs/evidence/core-5.4.2/`. Remaining acceptance: platform CI and integration into develop. PyPI/NuGet versions and tags are unchanged; package publication is separate.
