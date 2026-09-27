# Binding adoption #627 — quality review, 2026-09-27

## Resumen ejecutivo

Reviewed the 16-file staged change on oxidize-python develop (base recorded in
validation JSON), before creating its PR. The package is 0.20.1, pins core
=5.1.5 from crates.io, and keeps Rust/Python runtime sources unchanged. Core
and provider registry checksums were verified by Cargo. No path/git overrides.

## Contratos y evidencia

- Dependency policy: all five actual binding target graphs pass. The copied
  core policy and its 11 regression cases reject native sources, compiler
  crates, native archives and unreviewed links; pinned PyO3 interpreter ABI
  and Windows system import libraries are distinguished from bundled crypto.
- Distribution: fresh release wheel built with CC/CXX=false; 2525 tests pass,
  2 skip. Source archive includes Cargo.lock and all three public DER fixtures;
  its wheel builds locked/offline with the same disabled compiler environment
  (reuses already compiled dependency artifacts). Fresh isolated installation
  passes five certificate/CMS cases. Neither artifact was published locally.
- Binding behavior: two trust stores reject the external fixture root; RSA and
  ECDSA CMS retain independently generated signer identity and algorithms;
  malformed DER raises RuntimeError. Assertions use public binding results.
  These are compatibility checks; positive chain and CRL validation are proved
  by the core/provider suites, since the binding exposes no custom root API.
- CI/release: 15 Python/OS test combinations retained; five graph gates added;
  release calls the full reusable workflow before publishing. CC/CXX=false is
  explicit both on hosts and in maturin Docker options. YAML/version/pin checks
  pass. Binary Git attributes preserve fixtures on Windows. Registry publishing
  remains exclusively in existing GitHub Actions workflows.
- Type contracts: mypy passes 24 package files and 2 strict contract files.

## Hallazgos

No new findings in the change. The existing aggregate signature boolean and
no-compression core build remain outside this dependency adoption and documented
in core TASKS.md as awaiting separate issues. Pytest reports one pre-existing
non-Collection parametrization deprecation in test_core_5_1_bindings.py; it is
unchanged and does not fail this validation. No baseline was recalibrated.

## Calidad de Tests (Kripteia)

Real analysis: score 100, 3 functions, 1 file for new certificate tests (5 cases
at runtime). Script-directory analysis reports 0 tests/0 files: unittest tests
are not detected by this analyzer; all 11 were executed directly and manually
reviewed. The score is not proof of complete cryptographic coverage.

## Análisis de Seguridad (Kripteia Security)

Both required executions completed: new tests and scripts each report
"No security issues found." Reviewed DER files are public fixtures, no private
keys. Policy subprocesses use argv, fixed CI targets and no shell interpolation.
No new runtime FFI, unsafe code, signing or cryptographic arithmetic.

## Métricas

- Archivos revisados: 16, plus unchanged public API and workflow callers.
- Hallazgos nuevos: 0; pre-existing limitations stated above.
- Archivos de producto modificados por la revisión: 0.
- Pendiente: remote multiplatform CI, merge and GitHub publication of binding.

Exact command output, artifact checksums and target graphs are in the companion
2026-09-27-python-627-validation.json. QR is complete for the local candidate;
issue #627 remains open until remote acceptance is verified.
