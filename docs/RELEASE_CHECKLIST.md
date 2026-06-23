# VulnoraIQ Release Checklist

> **Current target:** `0.2.0` / `0.2.0-rc1`  
> **Scope:** controlled internal enterprise production-readiness release  
> **Last updated:** 2026-06-23

This checklist must be completed before tagging a production-readiness release candidate or final release.

## Release boundary

`0.2.0` may be described as:

> Controlled internal enterprise production-readiness gate passed.

Do **not** describe `0.2.0` as public SaaS, multi-tenant, unsupervised internet-facing, or certified VAPT-grade ready.

## Pre-release requirements

- [ ] All planned release changes are merged or intentionally deferred.
- [ ] `README.md`, `SECURITY.md`, `CHANGELOG.md`, and `docs/` are aligned with current maturity.
- [ ] `docs/PRODUCTION_READINESS_SCORECARD.md` and `docs/PRODUCTION_HARDENING_BACKLOG.md` do not contradict each other.
- [ ] `docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md` reflects the current phase gate status.
- [ ] `docs/ASSESSMENT_ASSURANCE.md` clearly states scanner/evaluator limitations.
- [ ] No P0/P1 release blockers remain.
- [ ] Known accepted risks are documented.
- [ ] CI is green on the release branch or `main`.

## Versioning

VulnoraIQ uses semantic versioning:

```text
MAJOR.MINOR.PATCH[-PRERELEASE]
```

Recommended flow for this release:

1. Tag `v0.2.0-rc1` after a clean local and CI validation pass.
2. Run one release-candidate validation cycle.
3. Tag `v0.2.0` only after RC smoke, Docker smoke, backup/restore, and docs review pass.

## Stage 1: version and changelog

- [ ] Confirm `pyproject.toml` version is correct.
- [ ] Confirm README maturity banner references the same version.
- [ ] Confirm `CHANGELOG.md` has a dated section for the version.
- [ ] Confirm breaking changes are listed:
  - legacy `webui/server.py` removed
  - SQLite is default persistence
  - JSON backend is dev/legacy only
  - file auth disabled in production
  - `VULNORAIQ_ADMIN_TOKEN` required in production
- [ ] Confirm release notes include known limitations.

## Stage 2: local quality gates

Run:

```bash
python -m pip install -e .[dev]
ruff check .
mypy .
pytest -q
python -m pip check
pip-audit
```

Acceptance:

- [ ] Ruff passes.
- [ ] mypy passes.
- [ ] pytest passes.
- [ ] pip check passes or unrelated environment warnings are documented.
- [ ] pip-audit has no unaccepted high/critical runtime vulnerabilities.

## Stage 3: package, mapping, and readiness validation

Run:

```bash
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_production_testing_readiness.py
python scripts/validate_runtime_production_config.py
python scripts/validate_production_testing_readiness.py \
  --run-functional \
  --output-dir reports/output/production-readiness \
  --screenshot docs/assets/vulnoraiq-dashboard-example.svg
```

Acceptance:

- [ ] Package metadata validation passes.
- [ ] OWASP/ATLAS mapping metadata validation passes.
- [ ] Production readiness validation passes all checks.
- [ ] Runtime production config validation passes under a valid production env.
- [ ] Functional acceptance passes.
- [ ] Dashboard example asset remains refreshed.

## Stage 4: Web UI smoke test

Manual or scripted checks:

- [ ] `/healthz` returns HTTP `200`.
- [ ] `/readyz` returns HTTP `200` when config is loaded.
- [ ] `/metrics` requires auth by default.
- [ ] unauthenticated `/api/scans` returns `401`.
- [ ] valid admin token can retrieve `/api/csrf-token`.
- [ ] `POST /api/scans` without CSRF returns `403`.
- [ ] valid CSRF token allows demo scan creation.
- [ ] artifact download works for completed demo scan.
- [ ] artifact path traversal attempt is rejected.
- [ ] audit logs contain request IDs and do not contain tokens or request bodies.

## Stage 5: Docker and container smoke

Run:

```bash
docker build -t vulnoraiq:0.2.0-rc .
python scripts/container_smoke_test.py
```

Acceptance:

- [ ] Image builds successfully.
- [ ] Container runs as non-root.
- [ ] `/data` volume is used for DB/reports.
- [ ] healthcheck passes.
- [ ] production mode fails without admin token.
- [ ] production mode starts with valid admin token.

## Stage 6: backup and restore

Run on a temporary/test SQLite DB:

```bash
python scripts/backup_sqlite_store.py \
  /data/jobs.db \
  /data/backups/jobs-$(date +%Y%m%d-%H%M%S).db \
  --compress \
  --validate \
  --retention 90

python scripts/restore_sqlite_store.py \
  /data/backups/jobs-YYYYMMDD-HHMMSS.db.gz \
  /tmp/vulnoraiq-restore-test.db \
  --compressed \
  --validate
```

Acceptance:

- [ ] Backup completes.
- [ ] Backup validation passes.
- [ ] Restore completes to test DB.
- [ ] Restored DB validates.
- [ ] Restore drill result is recorded.

## Stage 7: documentation review

- [ ] README quick start is current.
- [ ] README Web UI instructions include production-mode and Docker Compose path.
- [ ] `SECURITY.md` reflects `0.2.0` controls and supported versions.
- [ ] `DEPLOYMENT.md` includes latest env vars and proxy/TLS guidance.
- [ ] `RUNBOOK.md` uses real `0.2.0` commands, not placeholder PostgreSQL/Redis/JWT commands.
- [ ] `INCIDENT_RESPONSE.md` references current audit events, SQLite, metrics, and token/proxy auth.
- [ ] `MIGRATION.md` covers `0.0.1.x` to `0.2.0`.
- [ ] `ASSESSMENT_ASSURANCE.md` warns that findings are framework evidence, not certified VAPT assurance.
- [ ] `AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md` shows the current phase-by-phase gate status.
- [ ] `PRODUCTION_HARDENING_BACKLOG.md` documents public/SaaS gaps.

## Stage 8: security review

- [ ] No real secrets in repository.
- [ ] `.env.production.example` contains placeholders only.
- [ ] Production auth is fail-closed.
- [ ] `listen_address_safe` check is reachable in `validate_all()`.
- [ ] OWASP/ATLAS mapping metadata validator passes for active oracles/checks.
- [ ] Trusted proxy identity spoofing tests pass.
- [ ] CSRF, rate-limit, request-size, artifact traversal, metrics auth, and audit tests pass.
- [ ] Dependency audit is reviewed.
- [ ] Security lead or maintainer signs off.

## Stage 9: release candidate tag

```bash
git tag -a v0.2.0-rc1 -m "Release candidate v0.2.0-rc1"
git push origin v0.2.0-rc1
```

After tag:

- [ ] GitHub Actions pass for the tag.
- [ ] Release notes are generated from `CHANGELOG.md`.
- [ ] RC deployment smoke is run.
- [ ] No blocker found during RC observation window.

## Stage 10: final release tag

Only after RC validation:

```bash
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

Post-release:

- [ ] GitHub Release created.
- [ ] Changelog copied into release notes.
- [ ] Deployment docs linked.
- [ ] Security policy linked.
- [ ] Known limitations clearly visible.
- [ ] Smoke test run against released artifact/image.
- [ ] Logs and metrics monitored for at least one hour in the target environment.

## Rollback plan

Trigger rollback for:

- auth bypass or fail-open behaviour
- token leakage
- artifact exposure
- data integrity issue
- repeatable production startup failure
- broken backup/restore
- critical/high dependency vulnerability without mitigation

Rollback steps:

1. Stop the service.
2. Revert to previous image/tag/code revision.
3. Restore pre-release SQLite backup if needed.
4. Validate `/healthz`, `/readyz`, `/metrics`, scan history, and artifact access.
5. Document root cause and create a hotfix issue.

## Final release decision

| Decision | Criteria |
| --- | --- |
| Tag `v0.2.0-rc1` | All local checks pass; docs aligned; Docker/backup smoke planned or passed |
| Tag `v0.2.0` | RC cycle passed cleanly with Docker smoke, backup/restore, and CI/tag validation |
| Keep unreleased | Any production-readiness validator failure, doc contradiction, security regression, or broken runtime smoke test |
