# oxidize-pdf Ecosystem Compatibility Matrix

Last updated: 2026-03-14

This is the ecosystem-wide compatibility reference. Each bridge repo also contains
a `docs/COMPATIBILITY.md` scoped to that bridge only.

---

## oxidize-python (PyPI: `oxidize-pdf`)

| Bridge version | Core (oxidize-pdf) | PyO3 | Maturin | Python | Platforms |
|---|---|---|---|---|---|
| 0.1.x | >=2.1.0, <3.0.0 | 0.28 | >=1.0, <2.0 | 3.10 – 3.13 | Linux x86_64, Linux aarch64, macOS arm64, macOS x86_64, Windows x86_64 |

### Minimum Rust toolchain: 1.77

---

## oxidize-pdf-dotnet (NuGet: `oxidize-pdf-dotnet`)

| Bridge version | Core (oxidize-pdf) | FFI | .NET | Platforms |
|---|---|---|---|---|
| 0.3.x | >=2.1.0, <3.0.0 | C ABI (cdylib) | 6, 7, 8 | Linux x86_64, Windows x86_64 |

### Notes
- macOS is not currently supported by the .NET bridge.
- aarch64 Linux is not currently supported by the .NET bridge.

---

## oxidize-wasm (npm: `@bzsanti/oxidize-pdf`) — PLANNED

| Bridge version | Core (oxidize-pdf) | wasm-bindgen | wasm-pack | Target | Environments |
|---|---|---|---|---|---|
| (not yet published) | >=2.3.0, <3.0.0 | 0.2.x | 0.13.x | wasm32-unknown-unknown | Browser (ESM), Node.js 18+ |

### Prerequisites before first release
- [ ] Audit oxidize-pdf core for wasm32 compilation blockers (std::fs usage)
- [ ] Gate file-based APIs in core behind `fs` feature flag
- [ ] Verify `cargo build --target wasm32-unknown-unknown --no-default-features --features compression` succeeds

---

## Core version history

| oxidize-pdf version | Release date | Breaking changes | Bridge impact |
|---|---|---|---|
| 2.1.0 | (unknown) | none | Initial version targeted by Python + .NET bridges |
| 2.3.0 | (current) | none | Bridges currently 2 versions behind |

---

## How to read this matrix

- A bridge with `>=2.1.0, <3.0.0` will compile against any core version from 2.1.0 up to (but not including) 3.0.0.
- When oxidize-pdf 3.0.0 is released, all bridges will need a major version update before they compile against it.
- A bridge version of `0.x.y` means pre-1.0; minor bumps may contain breaking changes within the bridge's own public API.
