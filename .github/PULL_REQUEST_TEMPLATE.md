## Summary

<!-- What does this PR change, and why? -->

## Changes

<!-- Bullet the concrete changes. -->

## Testing

<!-- How did you verify this? Paste relevant test output. -->

- [ ] `pytest tests/ --ignore=tests/mcp_tests` passes
- [ ] `cargo clippy --all-targets -- -D warnings` clean
- [ ] `mypy python/oxidize_pdf/` clean (if stubs changed)
- [ ] New behavior is covered by tests that assert real content (no smoke tests)

## Checklist

- [ ] Branch follows gitflow (targets `develop`)
- [ ] No breaking change to existing public APIs (or it is documented above)
