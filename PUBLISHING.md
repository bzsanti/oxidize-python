# Publishing to PyPI

## One-time setup: Trusted Publisher

Before the first release, configure PyPI to trust this repository's GitHub Actions workflow.

### 1. Register the trusted publisher on PyPI

1. Go to https://pypi.org/manage/account/publishing/
2. Under **Add a new pending publisher** fill in:
   - **PyPI project name**: `oxidize-pdf`
   - **Owner**: `bzsanti`
   - **Repository name**: `oxidize-python`
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`
3. Click **Add**

### 2. Create the GitHub environment

1. Go to your repository **Settings → Environments**
2. Click **New environment**, name it `pypi`
3. Under **Deployment protection rules**, optionally enable:
   - **Required reviewers** — adds a manual approval step before each publish
4. Save

### 3. Verify repository permissions

The `release.yml` workflow requires these permissions (already configured in the file):
- `id-token: write` — for OIDC token exchange with PyPI
- `contents: read` — to checkout the code
- `attestations: write` — for build provenance (optional)

## Creating a release

```bash
# Ensure you're on main with the latest code
git checkout main
git pull origin main

# Tag the release
git tag v0.1.0
git push origin v0.1.0
```

This triggers the `release.yml` workflow which:
1. Builds wheels for Linux (x86_64, aarch64), macOS (universal2), Windows (x86_64)
2. Builds a source distribution (sdist)
3. Publishes everything to PyPI via OIDC trusted publisher

## Version bumps

Update the version in **both** files before tagging:
- `pyproject.toml` → `version = "X.Y.Z"`
- `Cargo.toml` → `version = "X.Y.Z"`

## Troubleshooting

### "Trusted publisher not configured"
Ensure the PyPI pending publisher matches exactly: owner `bzsanti`, repo `oxidize-python`, workflow `release.yml`, environment `pypi`.

### "Environment 'pypi' not found"
Create the environment in GitHub repository Settings → Environments.

### Build fails on a specific platform
Check the workflow run logs. Common causes:
- Rust compilation errors on cross-compilation targets
- Missing system dependencies in the manylinux container
