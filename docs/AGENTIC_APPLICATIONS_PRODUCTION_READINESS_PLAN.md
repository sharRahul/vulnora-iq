# Agentic Applications Production Readiness Plan

**Plan status:** Completed for `0.2.0` controlled internal enterprise deployment. Public internet / SaaS hardening remains deferred and out of scope for this completion decision.

**Scope:** VulnoraIQ controlled internal enterprise deployment for authorised LLM, RAG, tool-using, and agentic application assessments.

**Version target:** `0.2.0`

**Production boundary:** This plan finishes the controlled-internal production-readiness tranche. It does **not** claim public internet, multi-tenant SaaS, certified VAPT-grade assurance, or unsupervised third-party scanning readiness.

## Readiness definition

VulnoraIQ is production-ready for controlled internal assessment use when all phase gates below are implemented, documented, and enforced by tests or CI.

Required release language:

> Controlled internal enterprise production-readiness gate passed.

Disallowed release language:

- public SaaS ready
- multi-tenant ready
- unsupervised internet-facing ready
- certified VAPT-grade assurance
- authorised to test third-party systems without written permission

## Phase status

| Phase | Area | Status | Release gate |
| --- | --- | --- | --- |
| 0 | Scope and responsible-use boundary | Complete | README, SECURITY policy, and assessment assurance docs must state authorised-use boundaries. |
| 1 | Agentic threat mapping governance | Complete | Active oracles and production checks must include OWASP family, OWASP ID, MITRE ATLAS tactic, mapping status, evidence surface, and manual-review flag. |
| 2 | Authentication and authorisation | Complete | Web UI auth enabled by default; production mode fails closed without strong env-backed token or trusted proxy configuration. |
| 3 | Request and browser hardening | Complete | CSRF, request-size limits, malformed JSON handling, security headers, artifact path protection, and rate limits enforced. |
| 4 | Persistence and migrations | Complete | SQLite is the default production job store, with WAL, foreign keys, busy timeout, and schema version tracking. |
| 5 | Auditability and observability | Complete | Structured audit logs, health, readiness, metrics, and request correlation are available. |
| 6 | Deployment and containerisation | Complete | Dockerfile, Compose, production env example, healthcheck, non-root user, `/data` volume, and reverse-proxy guidance exist. |
| 7 | Operations and incident response | Complete | Runbook, incident response plan, backup/restore, rollback, and migration guidance exist. |
| 8 | Release and CI quality gates | Complete | CI runs lint, typing, tests, package validation, OWASP/ATLAS mapping validation, production-readiness validation, and functional acceptance. |
| 9 | Public internet / SaaS hardening | Deferred | Requires OIDC/SSO, tenant isolation, shared persistence, shared rate/CSRF stores, stronger abuse controls, and independent assurance. |

## Phase 0: Scope and responsible-use boundary

**Objective:** prevent overclaiming and unsafe usage.

Implemented controls:

- README maturity banner limits `0.2.0` to controlled internal enterprise deployment.
- SECURITY policy requires authorised use only.
- Assessment assurance documentation states that findings are framework evidence requiring human review, not certified VAPT assurance.

Gate:

```bash
python scripts/validate_production_testing_readiness.py
```

## Phase 1: Agentic threat mapping governance

**Objective:** make coverage traceable across OWASP and MITRE ATLAS before any oracle/check becomes active.

Required metadata for every active oracle or production check:

- `owasp_family`
- `owasp_id`
- `mitre_atlas_tactics`
- `mapping_status`
- `evidence_surface`
- `manual_review_required`

Implemented controls:

- `config/owasp_oracles.yaml` contains metadata for active safe local oracles.
- `config/production_owasp_detection.yaml` contains metadata for production-oriented deterministic checks.
- `scripts/validate_owasp_atlas_mappings.py` validates required fields, allowed families, OWASP ID shape, MITRE ATLAS tactic shape, mapping status, evidence surface values, and boolean manual-review flags.
- `tests/test_owasp_atlas_mapping_validation.py` validates positive and negative cases and checks repository configs.
- CI now runs the validator explicitly in both workflow paths.

Gate:

```bash
python scripts/validate_owasp_atlas_mappings.py
pytest tests/test_owasp_atlas_mapping_validation.py -q
```

## Phase 2: Authentication and authorisation

**Objective:** prevent unauthenticated or unauthorised scan control.

Implemented controls:

- Token auth enabled by default.
- Production mode rejects disabled auth, short or default/demo tokens, unsafe file-auth configuration, and internal dev-token use.
- Trusted reverse-proxy identity mode requires explicit trusted proxy CIDRs.
- Viewer, analyst, and admin roles limit scan, metrics, artifact, and config access.
- Non-demo scan targets require explicit authorisation.

Gate:

```bash
pytest tests/test_webui_auth_production.py tests/test_scanner_authorisation.py -q
python scripts/validate_runtime_production_config.py
```

## Phase 3: Request and browser hardening

**Objective:** harden web request handling for controlled internal deployment.

Implemented controls:

- CSRF tokens for state-changing scan creation.
- Request body size limit.
- Malformed JSON and unsupported method handling.
- Artifact traversal protection.
- Security headers, including CSP, frame denial, MIME sniffing prevention, referrer policy, permissions policy, and conditional HSTS.
- Per-IP rate limiting and scan queue/concurrency limits.

Gate:

```bash
pytest tests/test_webui_csrf.py tests/test_webui_request_errors.py tests/test_webui_security_headers.py tests/test_webui_rate_limit.py -q
```

## Phase 4: Persistence and migrations

**Objective:** replace demo-style persistence with controlled internal job persistence.

Implemented controls:

- SQLite job store is the default backend.
- WAL, foreign keys, busy timeout, normalized jobs/events tables, and schema versioning are enabled.
- JSON backend is retained only for development/legacy compatibility.
- Backup and restore scripts validate schema and counts.

Gate:

```bash
pytest tests/test_sqlite_job_store.py tests/test_backup_restore.py -q
python scripts/backup_sqlite_store.py /data/jobs.db /data/backups/jobs-test.db --compress --validate --retention 90
```

## Phase 5: Auditability and observability

**Objective:** give operators evidence for health, incidents, and accountability.

Implemented controls:

- `/healthz` liveness endpoint.
- `/readyz` readiness endpoint.
- Auth-protected `/metrics` endpoint by default.
- Structured JSON audit logging with request IDs and security event types.
- Audit logs avoid tokens, CSRF tokens, request bodies, secrets, and full report contents.

Gate:

```bash
pytest tests/test_metrics.py tests/test_webui_audit_logging.py -q
```

## Phase 6: Deployment and containerisation

**Objective:** provide a repeatable controlled-internal deployment path.

Implemented controls:

- Non-root Dockerfile.
- `/data` volume for reports and SQLite.
- Docker healthcheck.
- Docker Compose file.
- `.env.production.example` with placeholders only.
- Reverse proxy/TLS guidance for nginx and Caddy.
- Runtime production-config validation.

Gate:

```bash
docker build -t vulnoraiq:0.2.0-rc .
python scripts/container_smoke_test.py
python scripts/validate_runtime_production_config.py
```

## Phase 7: Operations and incident response

**Objective:** make the service supportable after deployment.

Implemented controls:

- `docs/RUNBOOK.md` covers service management, health, metrics, logs, token rotation, backup/restore, stuck scans, proxy checks, troubleshooting, upgrade, and rollback.
- `docs/INCIDENT_RESPONSE.md` covers severity, evidence sources, containment, recovery, post-incident review, and communication guidance.
- `docs/MIGRATION.md` covers migration from `0.0.1.x` to `0.2.0`.
- `docs/RELEASE_CHECKLIST.md` defines staged release verification.

Gate:

```bash
python scripts/validate_production_testing_readiness.py --output-dir reports/output/production-readiness
```

## Phase 8: Release and CI quality gates

**Objective:** prevent regression before release or merge.

Implemented CI gates:

- `python -m pip check`
- `pip-audit` review signal
- `ruff check .`
- `mypy` / `mypy --explicit-package-bases .`
- `pytest`
- package metadata validation
- OWASP/MITRE mapping metadata validation
- target contract validation
- benchmark fixture validation
- functional acceptance path
- baseline/RAG/agent scan smoke tests
- report diff and trend smoke tests
- benchmark regression gate
- release package smoke test
- production-readiness validation

Release candidate gate:

```bash
python -m pip install -e .[dev]
ruff check .
mypy .
pytest -q
python -m pip check
pip-audit
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_production_testing_readiness.py \
  --run-functional \
  --output-dir reports/output/production-readiness
```

## Deferred Phase 9: Public internet and SaaS hardening

This is intentionally deferred and must not block `0.2.0` controlled-internal readiness.

Required future capabilities before public/SaaS claims:

- OIDC/SSO or equivalent enterprise identity integration.
- Tenant isolation and per-tenant configuration/data boundaries.
- PostgreSQL or equivalent multi-instance database backend.
- Shared CSRF/session/rate-limit state such as Redis.
- Per-user and global abuse controls.
- Centralised SIEM/alerting integration.
- WAF/CDN/DDoS guidance or reference architecture.
- Independent security assessment or penetration test.
- Performance/load testing and SLOs.
- Release artifact signing and container security scanning.

## Completion decision

**Completed for `0.2.0` controlled internal enterprise deployment.** Phases 0-8 are complete, documented, and backed by repository checks or CI gates. Phase 9 is explicitly out of scope and remains the future public internet / SaaS hardening backlog.
