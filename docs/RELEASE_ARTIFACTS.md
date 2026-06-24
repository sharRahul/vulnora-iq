# Release artifacts

This document describes how VulnoraIQ release artifacts are built for Windows, Linux, and macOS.

## Trigger policy

Platform release artifacts must **not** be built on every commit, push, or pull request.

The `Build Release Artifacts` workflow in `.github/workflows/release-build.yml` runs only when:

1. a GitHub Release is published; or
2. a maintainer manually starts the workflow with `workflow_dispatch`.

Normal quality gates remain in `.github/workflows/ci.yml` and any Python-specific CI workflow.

## Artifacts produced

| Platform | Artifact |
| --- | --- |
| Windows | `vulnoraiq-<version>-windows.zip` |
| Linux | `vulnoraiq-<version>-linux.tar.gz` |
| macOS | `vulnoraiq-<version>-macos.dmg` |

Each package should include:

- platform launcher files;
- Python source/package files;
- current React WebUI built static assets under `webui/static/console/`;
- safe configuration files;
- Docker and Docker Compose lab files where applicable;
- documentation;
- `LICENSE`, `NOTICE`, `SECURITY.md`, `ACCEPTABLE_USE.md`, and `THIRD_PARTY_NOTICES.md`;
- a generated `START_HERE.txt` with platform-specific startup instructions.

Generated reports, local SQLite databases, secrets, keys, virtual environments, build output, local runtime target files, and local config files are excluded.

## Local package build command

```bash
python scripts/build_platform_release_package.py \
  --platform linux \
  --version 0.2.0 \
  --output-dir dist/release
```

Supported platform values:

- `windows` -> `.zip`
- `linux` -> `.tar.gz`
- `macos` -> `.dmg`

macOS `.dmg` creation uses `hdiutil`, so that target must run on macOS. The GitHub release workflow uses `macos-latest` for this job.

## Required validation before artifact build

```bash
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py --output-dir reports/output/production-readiness
```

For WebUI release confidence, also run:

```bash
cd webui/console
npm install
npm run typecheck
npm run build
cd ../..
npm install
npx playwright install chromium --with-deps
npm run test:webui:hosted
```

For Docker lab confidence, also run:

```bash
docker compose build
python scripts/docker_smoke_test.py
```

## Published release run

When a GitHub Release is published, the workflow should:

1. resolve the release tag as the artifact version;
2. build Windows, Linux, and macOS packages on matching hosted runners;
3. validate package metadata/readiness before packaging;
4. upload all packages as workflow artifacts;
5. upload the packages to the GitHub Release.

## Current limitations

The current release artifacts are repository-checkout style packages with platform launchers and committed WebUI static assets. The macOS `.dmg` is unsigned and not notarised. Signed `.exe`, `.msi`, `.pkg`, notarised `.dmg`, `.deb`, `.rpm`, Homebrew, Winget, image signing, and SBOM-based supply-chain release flows remain future maturity items.
