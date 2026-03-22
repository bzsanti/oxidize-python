# oxidize-python Compatibility

Bridge version: 0.1.1
Last updated: 2026-03-14

## Core dependency

| Constraint | Value |
|---|---|
| Cargo.toml | `oxidize-pdf = { version = "2.1.0", ... }` |
| Effective range | `>=2.1.0, <3.0.0` (standard Rust SemVer caret) |
| Latest tested | 2.1.0 (2.3.0 is current; update pending) |

## Python support

| Python version | Supported |
|---|---|
| 3.10 | yes |
| 3.11 | yes |
| 3.12 | yes |
| 3.13 | yes |
| 3.9 and below | no |

## Platform support

| Platform | Architecture | Supported |
|---|---|---|
| Linux | x86_64 (manylinux_2_28) | yes |
| Linux | aarch64 (manylinux_2_28, cross-compiled) | yes |
| macOS | arm64 (native on macos-14) | yes |
| macOS | x86_64 (cross-compiled from arm64) | yes |
| Windows | x86_64 | yes |
| Windows | aarch64 | no |

## Build dependencies

| Dependency | Version constraint | Purpose |
|---|---|---|
| PyO3 | 0.28 | Python-Rust FFI |
| Maturin | >=1.0, <2.0 | Build system |
| Rust toolchain | >=1.77 (stable) | Compilation |

## Upgrading the core dependency

When oxidize-pdf releases a new version, the `receive-core-update` workflow
will automatically open a PR updating this file's "Latest tested" row and the
Cargo.toml version. Review the PR and follow the checklist before merging.

When oxidize-pdf releases a new MAJOR version (e.g., 3.0.0), this bridge
will need its own MAJOR version bump. The core range in Cargo.toml must be
updated to `>=3.0.0, <4.0.0` and any removed APIs must be handled.
