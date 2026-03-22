# oxidize-pdf Ecosystem Lifecycle Strategy

**Version**: 1.0
**Date**: 2026-03-14
**Scope**: oxidize-pdf (Rust core) + oxidize-python + oxidize-pdf-dotnet + oxidize-wasm (planned)

---

## Table of Contents

1. [Versioning Strategy](#1-versioning-strategy)
2. [Dependency Propagation Automation](#2-dependency-propagation-automation)
3. [Feature Parity Tracking](#3-feature-parity-tracking)
4. [Compatibility Matrix](#4-compatibility-matrix)
5. [Breaking Change Protocol](#5-breaking-change-protocol)
6. [WASM Bridge Architecture](#6-wasm-bridge-architecture)
7. [Release Coordination Workflow](#7-release-coordination-workflow)
8. [CI/CD Integration per Repository](#8-cicd-integration-per-repository)

---

## 1. Versioning Strategy

### Decision: Independent SemVer per bridge, with a declared core compatibility range

**Recommendation: Independent SemVer for each bridge repo.**

Do NOT couple bridge versions to the core version. Here is the honest reasoning:

#### Why coupling is tempting but wrong

A coupled scheme (bridge version always equals core version) looks clean on paper but creates real operational problems:

- The Python bridge at v0.1.1 already has its own meaningful history: bug fixes in the PyO3 bindings, CI improvements, type stub corrections. None of those correspond to oxidize-pdf changes. Forcing those into a core-aligned number discards that information.
- Bridges will inevitably need patch releases (typo in docstring, mypy stub fix, manylinux rebuild for a new distro) with zero change in the core dependency. Under coupling, you either ship a fake core bump or violate the scheme immediately.
- When oxidize-pdf reaches v3.0.0, the Python bridge may be at v0.3.0 — users of the Python package do not need to know or care about core versioning.
- npm, PyPI, NuGet, and crates.io each have their own established conventions and user expectations. Imposing an artificial cross-registry coupling creates confusion in each ecosystem.

#### The correct model: declared compatibility metadata

Each bridge expresses what it requires from the core via its own Cargo.toml dependency specification:

```toml
# Cargo.toml in oxidize-python
oxidize-pdf = { version = ">=2.1.0, <3.0.0", ... }
```

This is the standard Rust SemVer range mechanism. It is the source of truth. The compatibility matrix (section 4) formalizes it for human readers.

#### Bridge versioning rules

Each bridge follows standard SemVer independently:

- **PATCH**: Bug fixes in bridge code (bindings, stubs, CI, docs), no change to minimum core version.
- **MINOR**: New features exposed in the bridge (wrapping new core APIs), or raising the minimum core version within the same core major. No breaking changes to the bridge's public API.
- **MAJOR**: Breaking changes to the bridge's public API (renamed class, changed method signature, removed symbol). This is independent of whether the core had a breaking change.

#### Practical implication right now

Both oxidize-python (v0.1.1) and oxidize-pdf-dotnet (v0.3.1) are on pre-1.0 (major=0). Under SemVer, 0.x minor bumps are allowed to be breaking. Before reaching v1.0, each bridge should:

1. Define a stability guarantee date and target v1.0.
2. Until then, treat every minor bump as potentially breaking and document it clearly in the changelog.

---

## 2. Dependency Propagation Automation

### Problem

When oxidize-pdf publishes a new version to crates.io, the bridges need to:
1. Know about it automatically.
2. Get a PR opened against their `develop` branch that updates `Cargo.toml`.
3. Have that PR go through CI before merging.

### Why Dependabot alone is not sufficient

Dependabot can detect new crates.io versions. However it:
- Cannot be configured to open PRs against a specific target branch other than the default.
- Runs on a schedule (daily/weekly), not on-push from the upstream repo.
- Cannot run custom validation logic (e.g., check that the new version actually compiles before opening the PR).
- Does not support cross-repository coordination.

### Recommended approach: crates.io polling workflow + Dependabot as fallback

The architecture has two layers:

**Layer 1 — Core repo push trigger (primary)**

In `github.com/bzsanti/oxidizePdf`, add a workflow (`notify-bridges.yml`) that fires on every push to `main`. It calls the GitHub API to dispatch a `repository_dispatch` event to each bridge repo. This is near-real-time (minutes after a tag lands on main).

**Layer 2 — Crates.io polling (safety net)**

Each bridge repo has a scheduled workflow (`check-core-update.yml`) that polls crates.io once per day, compares the latest published version to what is pinned in `Cargo.toml`, and opens a PR if they differ. This catches the case where the dispatch in Layer 1 failed.

See `docs/lifecycle/workflows/` for the concrete YAML for all of these.

### PR content requirements

The auto-generated PR must contain:
- Updated `Cargo.toml` with the new version.
- A CHANGELOG entry stub in `CHANGELOG.md` (if it exists in the repo).
- The PR body must include: old version, new version, link to core CHANGELOG, and a checklist of manual review steps.
- Label: `dependency-update`, `automated`.

---

## 3. Feature Parity Tracking

### The core API surface

The canonical feature list lives in a machine-readable file: `docs/lifecycle/API_SURFACE.md` (this repository, as the furthest-along bridge). It defines every feature group with a unique identifier. All bridges reference these identifiers.

### Feature status file per bridge

Each bridge repo contains `docs/FEATURE_PARITY.md`. The format is a table with columns:

| Feature ID | Feature Name | Core Since | Python | .NET | WASM | Notes |
|---|---|---|---|---|---|---|

Status values: `yes`, `no`, `partial`, `n/a` (feature is not applicable to this runtime, e.g., file I/O for WASM).

The file is updated manually by Santiago when implementing features. There is no automated extraction (the bridge code is the ground truth; generating metadata from it automatically would require a Rust proc-macro or AST analysis that is not worth the investment for a solo project).

### Automated parity gap report (CI-level)

The bridge CI runs a Python script (`scripts/check_parity.py`) that reads the local `FEATURE_PARITY.md` and asserts that no feature marked `yes` in the core actually has `no` in this bridge when the core version is bumped. This is a coarse guard — it does not replace manual review but it prevents accidentally shipping a bridge update that silently drops a previously-working feature.

The `check_parity.py` script is simple: it reads both files as TOML/Markdown tables and fails with a diff if a regression is detected.

### Current parity gap: oxidize-pdf-dotnet

oxidize-pdf-dotnet currently exposes only text extraction and chunking. The work required to reach parity with the Python bridge is substantial (document creation, graphics, operations, security, full parser). This gap should be tracked as GitHub Issues in the dotnet repo with labels `feature-parity` and priority ordering.

---

## 4. Compatibility Matrix

### Location

`docs/lifecycle/COMPATIBILITY_MATRIX.md` in this repository (used as the ecosystem-wide reference).

Each bridge repo also contains `docs/COMPATIBILITY.md` scoped to that bridge only.

### Format

```markdown
## oxidize-python

| Bridge version | Core (oxidize-pdf) | PyO3 | Python | Platforms |
|---|---|---|---|---|
| 0.1.x | >=2.1.0, <3.0.0 | 0.28 | 3.10 – 3.13 | Linux x86_64/aarch64, macOS arm64/x86_64, Windows x86_64 |

## oxidize-pdf-dotnet

| Bridge version | Core (oxidize-pdf) | FFI ABI | .NET | Platforms |
|---|---|---|---|---|
| 0.3.x | >=2.1.0, <3.0.0 | cdylib stable | 6, 7, 8 | Linux x86_64, Windows x86_64 |

## oxidize-wasm (planned)

| Bridge version | Core (oxidize-pdf) | wasm-bindgen | Target | Environments |
|---|---|---|---|---|
| (not yet published) | >=2.3.0, <3.0.0 | 0.2.x | wasm32-unknown-unknown | Browser (ESM), Node.js 18+ |
```

### Who updates it

Santiago updates the matrix as part of every release process, both for the core and for each bridge. It is the human-readable contract. The Cargo.toml dependency range is the machine-enforced version of the same contract.

---

## 5. Breaking Change Protocol

This protocol applies whenever oxidize-pdf (core) needs to change a public API that bridges depend on.

### Definitions

- **Additive change**: New public item (function, type, variant, field). No protocol required. Bridges may optionally expose it.
- **Behavioral change**: Existing API has different observable behavior. Treat as breaking unless clearly a bug fix.
- **Breaking change**: Renamed item, removed item, changed function signature, changed error type, changed trait implementation.

### Five-step protocol

#### Step 1: Deprecation in core (core minor or patch release)

In the oxidize-pdf codebase:

1. Mark the old API with `#[deprecated(since = "X.Y.Z", note = "Use `new_name` instead")]`.
2. Introduce the replacement API in the same release if possible.
3. The deprecation must appear in the core CHANGELOG under `### Deprecated`.
4. A GitHub Issue is opened in bzsanti/oxidizePdf titled `[Breaking Planned] Remove <api_name> in vX+1.0.0` with label `breaking-planned`.

The deprecated API remains fully functional. No bridge changes are required at this step.

#### Step 2: Bridge adaptation window (next 1-2 bridge minor releases)

Each bridge:
1. Updates its core dependency to the version containing the deprecation.
2. Migrates its own binding code from the deprecated API to the replacement.
3. If the bridge exposed the deprecated API to its consumers (Python, .NET, WASM), it ALSO deprecates its public API using the target language's mechanism:
   - Python: `warnings.warn("...", DeprecationWarning, stacklevel=2)` in a shim.
   - .NET: `[Obsolete("...", false)]` on the P/Invoke wrapper.
   - WASM/JS: `/** @deprecated ... */` JSDoc on the exported function.
4. The bridge does NOT remove the deprecated bridge API yet — only adds the deprecation warning.

This step is complete when all three bridges are adapted. Target: within 30 days of core deprecation release.

#### Step 3: Core major release removes the deprecated API

1. The deprecated API is removed from oxidize-pdf in the next MAJOR version bump.
2. The core CHANGELOG documents the removal under `### Removed`.
3. The GitHub Issue from Step 1 is closed.
4. The dependency propagation automation (Section 2) opens PRs against all bridge repos.

#### Step 4: Bridge major releases remove the deprecated bridge API

Each bridge opens a `release/vX.0.0-deprecation-cleanup` branch (following the repo's gitflow). On this branch:
1. Remove the deprecated bridge API shims.
2. Update the `Cargo.toml` dependency to the new core major range (`>=3.0.0, <4.0.0`).
3. Update the bridge MAJOR version.
4. Update `docs/FEATURE_PARITY.md` and `docs/COMPATIBILITY.md`.

The PR for this branch is the bridge's major release PR. It must not be merged until CI passes on all platforms.

#### Step 5: Announce and update compatibility matrix

After all bridge major releases land:
1. Update `docs/lifecycle/COMPATIBILITY_MATRIX.md` with the new version rows.
2. Update `docs/lifecycle/API_SURFACE.md` to remove the deprecated feature entries.
3. Tag the ecosystem-wide update with a comment in the core repo's GitHub release notes linking to all bridge releases.

### Honest assessment of timing for a solo developer

The five-step protocol above is correct in structure. The practical risk is that Steps 2 and 4 will accumulate if multiple deprecations happen in parallel. The mitigation is to batch deprecations: do not ship a core major until 2-3 deprecation cycles have accumulated. This reduces the cognitive overhead of bridge maintenance.

---

## 6. WASM Bridge Architecture

### Technology choice: wasm-pack with wasm-bindgen

**Do not use raw `wasm-bindgen` CLI directly.** `wasm-pack` wraps it and handles:
- The `pkg/` output directory with correct `package.json`.
- `--target bundler` vs `--target nodejs` vs `--target web` output modes.
- npm publish integration.
- Generating TypeScript type definitions automatically from `#[wasm_bindgen]` annotations.

The cost is a thin tool dependency on `wasm-pack`. That cost is worth it.

#### wasm-bindgen vs wasm-pack clarification

`wasm-bindgen` is a Rust macro + JS glue generator. `wasm-pack` is a build tool that invokes `wasm-bindgen` internally plus handles packaging. Use `wasm-pack` as the entry point; think of `wasm-bindgen` as the underlying engine.

### What the WASM API surface should and should not expose

WASM running in a browser has no filesystem access. WASM running in Node.js has filesystem access but the bridge should not assume it. This has direct consequences:

**What to expose:**
- `Document`, `Page`, `Font`, `Color`, `TextAlign`, `Margins`, `Point`, `Rectangle` — identical to Python bridge.
- `document.toBytes(): Uint8Array` — returns the PDF as bytes. The JS caller decides what to do with them (download, send to server, write to disk in Node.js).
- `PdfReader.fromBytes(data: Uint8Array)` — accepts bytes. The JS caller handles reading the file.
- `mergeFromBytes(inputs: Uint8Array[]): Uint8Array` — bytes in, bytes out.
- `splitToBytes(input: Uint8Array): Uint8Array[]` — splits into array of byte arrays.
- `rotateBytes(input: Uint8Array, degrees: number): Uint8Array`.
- `extractPagesBytes(input: Uint8Array, pageIndices: number[]): Uint8Array`.

**What NOT to expose (design constraint, not a shortcut):**
- Any function that takes a file path string. Paths are meaningless in the browser and unreliable cross-environment. The WASM bridge is bytes-in, bytes-out only.
- Streaming interfaces — WASM linear memory does not support async streaming well. Accept the full buffer.

This means the WASM API is not identical to the Python API in the operations module, but it IS feature-equivalent. This distinction belongs in `docs/FEATURE_PARITY.md` under the `n/a` column.

### Repository structure for oxidize-wasm

```
oxidize-wasm/
  Cargo.toml           (crate-type = ["cdylib"], depends on oxidize-pdf)
  src/
    lib.rs
    document.rs        (mirrors oxidize-python/src/document.rs but with wasm_bindgen)
    page.rs
    types.rs
    text.rs
    operations.rs      (bytes-in/bytes-out versions)
    parser.rs          (from_bytes instead of open(path))
  pkg/                 (generated by wasm-pack, gitignored)
  .github/workflows/
    ci.yml
    release.yml
  package.json         (for npm metadata, manually maintained)
  README.md
```

### Cargo.toml for oxidize-wasm

```toml
[package]
name = "oxidize-wasm"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"
oxidize-pdf = { version = ">=2.3.0, <3.0.0", default-features = false, features = ["compression"] }

[package.metadata.wasm-pack.profile.release]
wasm-opt = ["-Oz"]
```

Note: `default-features = false` is important. The core likely has features that depend on `std` filesystem operations that will not compile to wasm32. Verify this with `cargo build --target wasm32-unknown-unknown` and add feature flags as needed.

### Critical technical risk: oxidize-pdf compilation to wasm32

oxidize-pdf uses `std::fs::File` (visible in `parser.rs` of this Python bridge — `PdfReader<File>` and `PdfDocument<File>`). File I/O types do not compile to `wasm32-unknown-unknown`. The core library must be audited for:
- Any `std::fs` usage in default-enabled code paths.
- Any `std::io::Read`/`Write` implementations that are file-backed rather than cursor-backed.

The correct solution is to gate file-based APIs in the core behind a `fs` feature flag (default enabled), keeping the core logic on `Read`/`Write` traits. The WASM bridge only enables the non-`fs` code paths and works with byte buffers.

This audit must happen before the WASM bridge is started. It may require a minor refactor in the core. This is not optional — if the core does not compile to wasm32, the WASM bridge cannot exist.

### Publishing to npm

Use `wasm-pack publish` in the release workflow. The package name on npm should be `oxidize-pdf` (consistent with PyPI). If the npm name is taken, use `@bzsanti/oxidize-pdf` (scoped package).

Scoped packages (`@bzsanti/oxidize-pdf`) are actually preferable for a solo developer because:
- No name squatting risk.
- Clear ownership signal.
- npm scoped packages under a personal namespace require no organization setup.

### TypeScript support

`wasm-pack` generates `.d.ts` files automatically from `#[wasm_bindgen]` annotations. These should be reviewed and supplemented with hand-written documentation comments the same way the Python bridge has `.pyi` stubs.

---

## 7. Release Coordination Workflow

### End-to-end flow from core change to all bridges updated

```
[Santiago] develops feature/fix in oxidize-pdf
    |
    v
[Core repo] PR: feature/* → develop → CI passes
    |
    v
[Core repo] PR: develop → main → CI passes → merge
    |
    v
[Santiago] Updates Cargo.toml version, tags v2.4.0 on main
    |
    v
[Core repo CI] release.yml fires → publishes to crates.io
    |
    v
[Core repo CI] notify-bridges.yml fires → dispatches repository_dispatch
                to oxidize-python, oxidize-pdf-dotnet, oxidize-wasm
    |
    v (parallel, one per bridge repo)
[Bridge repo CI] receive-core-update.yml fires
    → reads new version from event payload
    → updates Cargo.toml
    → runs `cargo update` to update Cargo.lock
    → runs `cargo check` to verify it compiles
    → opens PR: "chore: update oxidize-pdf to v2.4.0"
    → sets labels: dependency-update, automated
    |
    v
[Santiago] Reviews and merges the PR in each bridge
    → CI runs full test matrix on the PR
    → merge to develop
    |
    v
[Santiago] Decides whether the core update warrants a bridge release
    → If the core adds new APIs the bridge should expose: create feature/* branch,
       implement bindings, open PR to develop, then release/* to main
    → If the core is purely additive/fix and bridge needs no changes:
       the dependency update PR IS the release candidate
    |
    v
[Santiago] Tags bridge release: v0.2.0 (if new features) or v0.1.2 (if just dep update)
    |
    v
[Bridge CI] release.yml fires → publishes to PyPI / NuGet / npm
```

### The manual decision point is intentional

The automation opens the dependency update PR. The decision to release the bridge after merging it is always Santiago's. This is the correct design. Fully automated bridge releases (auto-tag on merge) would be dangerous:
- A new core version might expose APIs that should be wrapped before shipping to users.
- A new core version might introduce a behavioral change that breaks bridge tests (the PR CI would catch this, but auto-releasing before fixing would publish a broken package).
- PyPI, NuGet, and npm releases are permanent. A yanked release is a bad user experience.

### Release frequency guideline

- Core patch releases (2.3.x → 2.3.x+1): Bridges should update within 2 weeks. No bridge release required unless the patch fixed a bug affecting the bridge.
- Core minor releases (2.3.x → 2.4.0): Bridges should update and release within 4 weeks. This release should expose any new APIs if possible.
- Core major releases (2.x.y → 3.0.0): Bridges have 60 days to ship their own major release. The old bridge major version (pinned to the old core major) should receive critical bug fixes for 90 days after the new one lands, then go EOL.

---

## 8. CI/CD Integration per Repository

### oxidize-pdf (core) — additional workflows needed

The core repo needs two new workflows added:

**notify-bridges.yml** — fires after a successful crates.io publish and dispatches events to bridge repos. See `docs/lifecycle/workflows/core-notify-bridges.yml`.

**api-surface-extract.yml** — on every push to main, extracts the public API surface from rustdoc JSON output and commits an updated `docs/api-surface.json` if it changed. This file is what the bridge parity check scripts read. See `docs/lifecycle/workflows/core-api-surface.yml`.

### oxidize-python — additional workflows needed

**receive-core-update.yml** — handles `repository_dispatch` from the core repo and from the daily cron. Opens the dependency update PR. See `docs/lifecycle/workflows/bridge-receive-core-update.yml`.

**check-core-update.yml** — daily cron fallback that polls crates.io directly. See `docs/lifecycle/workflows/bridge-check-core-update.yml`.

**parity-check.yml** — runs on every push to develop and main, verifying that `docs/FEATURE_PARITY.md` is consistent with what is actually exported in `__init__.py`. See `docs/lifecycle/workflows/bridge-parity-check.yml`.

### oxidize-pdf-dotnet — same three additional workflows

Same `receive-core-update.yml`, `check-core-update.yml`, and `parity-check.yml`. The parity check script will need a .NET-specific implementation (reads the P/Invoke wrapper public surface).

### oxidize-wasm — full CI from scratch

The CI for the WASM bridge has different requirements:
- Must install `wasm-pack` (not Maturin).
- Must test against both browser (via headless Chrome/Firefox via `wasm-pack test --headless`) and Node.js environments.
- Must verify TypeScript types compile (`tsc --noEmit`).

See `docs/lifecycle/workflows/wasm-ci.yml` and `docs/lifecycle/workflows/wasm-release.yml`.
