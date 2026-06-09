# Contributing to oxidize-pdf (Python)

Thank you for your interest in contributing! This is the Python binding for the
[`oxidize-pdf`](https://github.com/bzsanti/oxidizePdf) pure-Rust PDF engine,
built with [PyO3](https://pyo3.rs) and [maturin](https://www.maturin.rs).

## Prerequisites

- Rust 1.88+ (stable) — the binding's MSRV tracks the core crate.
- Python 3.10+
- Git and a GitHub account

## Development Setup

1. **Fork and clone**
   ```bash
   git clone https://github.com/your-username/oxidize-python.git
   cd oxidize-python
   ```

2. **Create a virtual environment and install dev dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Build the native extension into the venv**
   ```bash
   maturin develop
   ```

4. **Run the test suite**
   ```bash
   pytest tests/ --ignore=tests/mcp_tests
   ```

5. **Type-check the stubs**
   ```bash
   mypy python/oxidize_pdf/
   ```

## Development Workflow (gitflow)

This repo follows gitflow: `feature/*` / `fix/*` / `chore/*` branches → `develop` → `main`.

1. **Branch from `develop`**
   ```bash
   git checkout develop && git pull
   git checkout -b feature/your-change
   ```

2. **Keep the tree green before every commit**
   ```bash
   cargo clippy --all-targets -- -D warnings
   pytest tests/ --ignore=tests/mcp_tests
   mypy python/oxidize_pdf/
   ```

3. **Open a PR against `develop`.** CI runs the test matrix across 3 operating
   systems and 4 Python versions; all must pass before merge.

## Testing Discipline

- **No smoke tests.** A test must verify real behavior and exact content, not
  just that a call returns without raising or that a file is non-empty.
- For bug fixes, follow strict TDD: write a test that reproduces the bug first,
  then the fix.
- Read the generated output (PDF bytes, extracted text, JSON) and assert on its
  content directly.

## Exposing New Core APIs

When the upstream `oxidize-pdf` crate gains a feature you want to surface:

1. Bump the `oxidize-pdf` dependency in `Cargo.toml` (pinned `=X.Y.Z`).
2. Add the PyO3 wrapper in the relevant `src/*.rs` module, mirroring the
   existing `Py*` class patterns.
3. Register the class/function in the module and export it from
   `python/oxidize_pdf/__init__.py`.
4. Add behavior tests under `tests/`.

## Reporting Bugs and Requesting Features

Use the issue templates. For security vulnerabilities, follow
[SECURITY.md](./SECURITY.md) — do not open a public issue.

## Code of Conduct

This project adheres to the [Contributor Covenant](./CODE_OF_CONDUCT.md). By
participating, you are expected to uphold it.
