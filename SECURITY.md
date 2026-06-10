# Security Policy

## Reporting a Vulnerability

Please report security vulnerabilities **privately** — do not open a public issue.

- Use GitHub's [private vulnerability reporting](https://github.com/bzsanti/oxidize-python/security/advisories/new), or
- Email **santiago.fernandez@belowzero.tech**.

Include a description, reproduction steps, the affected version, and the impact you observed.

You can expect an initial response within 5 business days. Confirmed vulnerabilities are addressed in a patch release, and you will be credited unless you ask to remain anonymous.

## Supported Versions

Security fixes are applied to the latest released version on PyPI. Upgrade to the latest release before reporting.

`oxidize-pdf` (this package) is the Python binding for the [`oxidize-pdf`](https://github.com/bzsanti/oxidizePdf) Rust core. Vulnerabilities in the underlying PDF engine are forwarded upstream and resolved in a coordinated core + binding release.
