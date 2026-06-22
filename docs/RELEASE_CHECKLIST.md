# VulnoraIQ Release Checklist

> **Version:** 0.2.0
> **Owner:** Release Manager
> **Last Updated:** 2026-06-22

---

## Pre-Release Checklist

Before starting any release process, verify the following:

- [ ] All planned features/ fixes for this release are merged to `main`
- [ ] No known P0/P1 bugs are open against this release
- [ ] CI pipeline is green on `main` for the last 24 hours
- [ ] All required approvals are obtained (see Required Approvals section)
- [ ] Release Manager is assigned and confirmed
- [ ] Release notes draft is prepared
- [ ] Stakeholders have been notified of the release window
- [ ] Maintenance window is confirmed (if downtime is expected)

---

## Version Numbering Scheme

VulnoraIQ follows **Semantic Versioning 2.0.0**:

```
MAJOR.MINOR.PATCH[-PRERELEASE]
```

| Component | When to bump | Example |
|-----------|-------------|---------|
| **MAJOR** | Breaking API/DB schema/configuration changes | 2.0.0 |
| **MINOR** | New features, no breaking changes | 1.3.0 |
| **PATCH** | Bug fixes, security patches, minor improvements | 1.2.1 |
| **PRERELEASE** | RC, alpha, beta suffixes | 1.3.0-rc.1 |

### Pre-release suffixes

- `-rc.N` — Release Candidate N (e.g., `1.3.0-rc.1`)
- `-alpha.N` — Alpha build (internal testing)
- `-beta.N` — Beta build (limited external testing)

---

## Release Candidate Process

For non-trivial releases, create at least one Release Candidate (RC) before the final release.

1. Branch from `main` into `release/v<MAJOR>.<MINOR>.<PATCH>-rc.N`
2. Complete all items in Stage 1 (Version & Changelog)
3. Run Stages 2–4 (Validation pipeline)
4. Tag `v<version>-rc.N` and push
5. Deploy RC to staging environment
6. Run integration and smoke tests in staging
7. Gather sign-off from QA and Product
8. If issues found, fix on the release branch, increment RC number, repeat
9. Once all issues are resolved, merge into `main` and proceed with final release

---

## Hotfix Process

For critical issues in production that cannot wait for the next regular release:

1. Branch from the latest release tag: `hotfix/v<MAJOR>.<MINOR>.<PATCH+1>-hotfix`
2. Apply the minimal fix
3. Complete all checklist stages (1–4)
4. Obtain expedited approvals (Engineering Lead + Security if applicable)
5. Tag `v<version>` and push
6. Merge back into `main` and the active release branch
7. Post-release verification in production
8. Document the incident and root cause

> **Note:** Hotfixes bypass the RC process but still require full validation pipeline execution.

---

## Required Approvals

| Role | Required For |
|------|-------------|
| Engineering Lead | Stage 1 (version/changelog review), Stage 5 (release sign-off) |
| QA Lead | Stage 4 (test results review) |
| Security Lead | Stage 7 (security review), any release with security fixes |
| Product Manager | Feature releases, changelog final review |
| Release Manager | All stages — overall coordination and sign-off |
| CTO/VP Eng | MAJOR version releases only |

---

## Release Checklist

### Stage 1: Version Bump & Changelog

- [ ] **1.1** Update version in `pyproject.toml`
- [ ] **1.2** Add new version section to `CHANGELOG.md` with date
- [ ] **1.3** Review changelog entries:
  - [ ] New features clearly documented
  - [ ] Security fixes called out (reference CVE if applicable)
  - [ ] Breaking changes marked with `[BREAKING]` prefix
  - [ ] Deprecated APIs listed with migration path
  - [ ] Upgrade steps documented (if any)
- [ ] **1.4** Commit version bump and changelog with message: `chore: bump version to v<X.Y.Z>`
- [ ] **1.5** Engineering Lead approval

### Stage 2: Lint & Static Analysis

- [ ] **2.1** Run Ruff lint check

      ```bash
      ruff check .
      ```

- [ ] **2.2** Run mypy type check

      ```bash
      mypy .
      ```

- [ ] **2.3** Resolve any lint/type errors (zero warnings policy)

### Stage 3: Tests

- [ ] **3.1** Run pytest

      ```bash
      pytest
      ```

- [ ] **3.2** All tests pass (zero failures)
- [ ] **3.3** Code coverage meets threshold (≥80%)

### Stage 4: Validation Scripts

- [ ] **4.1** Run metadata validation

      ```bash
      python scripts/validate_package_metadata.py
      ```

- [ ] **4.2** Run production readiness validation

      ```bash
      python scripts/validate_production_testing_readiness.py
      ```

- [ ] **4.3** Run runtime config validation

      ```bash
      python scripts/validate_runtime_production_config.py
      ```

- [ ] **4.4** All validation scripts pass (exit code 0)

### Stage 5: Docker Build & Smoke Test

- [ ] **5.1** Build Docker image

      ```bash
      docker build -t vulnoraiq:<version> .
      docker build -t vulnoraiq:latest .
      ```

- [ ] **5.2** Run container smoke test

      ```bash
      docker run --rm vulnoraiq:<version> --version
      docker run --rm vulnoraiq:<version> --help
      ```

- [ ] **5.3** Verify container starts and health endpoint responds (if applicable)
- [ ] **5.4** QA Lead approval

### Stage 6: Backup / Restore Test

- [ ] **6.1** Verify backup script executes successfully
- [ ] **6.2** Perform restore from backup to a test environment
- [ ] **6.3** Verify data integrity after restore
- [ ] **6.4** Document any schema migrations or breaking data changes

### Stage 7: Documentation Review

- [ ] **7.1** API documentation is up to date
- [ ] **7.2** Configuration reference reflects new/ changed options
- [ ] **7.3** Upgrade / migration guide is updated (if applicable)
- [ ] **7.4** README and quickstart are current
- [ ] **7.5** CHANGELOG is accurate and well-formatted

### Stage 8: Security Review

- [ ] **8.1** All dependencies are scanned for known vulnerabilities

      ```bash
      pip-audit
      ```

- [ ] **8.2** No new high/ critical severity vulnerabilities introduced
- [ ] **8.3** Security fixes are verified (if applicable)
- [ ] **8.4** Secrets/ credentials are not hardcoded or committed
- [ ] **8.5** Security Lead sign-off (or documented waiver)

### Stage 9: Git Tag & Release

- [ ] **9.1** Create and push annotated tag

      ```bash
      git tag -a v<X.Y.Z> -m "Release v<X.Y.Z>"
      git push origin v<X.Y.Z>
      ```

- [ ] **9.2** Create GitHub Release from the tag
- [ ] **9.3** Attach release notes (generated from CHANGELOG)
- [ ] **9.4** Upload build artifacts (Docker image, distribution packages)
- [ ] **9.5** Notify stakeholders of the release

### Stage 10: Post-Release Verification

- [ ] **10.1** Verify GitHub Actions/ CI completed for the tag
- [ ] **10.2** Deploy to production (following deployment playbook)
- [ ] **10.3** Verify production health endpoints
- [ ] **10.4** Run smoke tests against production
- [ ] **10.5** Monitor logs and metrics for 1 hour post-deployment
- [ ] **10.6** Confirm no regression in key metrics (error rate, latency, throughput)
- [ ] **10.7** Release Manager final sign-off

---

## Checklist Tracking Table

| Stage | Item | Status | Owner | Notes |
|-------|------|--------|-------|-------|
| Pre-Release | All pre-checks complete | ☐ | Release Manager | |
| 1 | Version bump & changelog | ☐ | | |
| 2 | Lint & static analysis | ☐ | | |
| 3 | Tests | ☐ | | |
| 4 | Validation scripts | ☐ | | |
| 5 | Docker build & smoke test | ☐ | | |
| 6 | Backup / restore test | ☐ | | |
| 7 | Documentation review | ☐ | | |
| 8 | Security review | ☐ | | |
| 9 | Git tag & release | ☐ | | |
| 10 | Post-release verification | ☐ | | |
| **Final** | **Release Manager sign-off** | ☐ | | |

---

## Quick Reference: Commands by Stage

| Stage | Command |
|-------|---------|
| 1 | `git commit -m "chore: bump version to v<X.Y.Z>"` |
| 2 | `ruff check . && mypy .` |
| 3 | `pytest` |
| 4 | `python scripts/validate_package_metadata.py && python scripts/validate_production_testing_readiness.py && python scripts/validate_runtime_production_config.py` |
| 5 | `docker build -t vulnoraiq:<version> . && docker run --rm vulnoraiq:<version> --version` |
| 8 | `pip-audit` |
| 9 | `git tag -a v<X.Y.Z> -m "Release v<X.Y.Z>" && git push origin v<X.Y.Z>` |

---

## Rollback Plan

If post-release verification fails or a critical issue is discovered:

1. **Immediate:** Revert to previous Docker image tag in production
2. **Short-term:** Create hotfix branch from the release tag
3. **Follow:** The hotfix process above
4. **Communication:** Notify all stakeholders of the rollback and ETA for fix

> **Rollback trigger criteria:** Error rate > 1%, p99 latency > 5s, any P0 security finding, data integrity issue.
