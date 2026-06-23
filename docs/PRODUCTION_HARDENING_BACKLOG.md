# Production Hardening Backlog

Status: live blocker register
Current operational readiness: 10/10 (controlled internal deployment)
Target: controlled production assessment readiness, not SaaS multi-tenant production hosting.

## Current verdict

VulnoraIQ is ready for **controlled internal enterprise deployment** with the security, operational, and deployment controls listed below. It is **not ready for public internet-facing, multi-tenant SaaS, or unsupervised production hosting**. See [`PRODUCTION_READINESS_SCORECARD.md`](PRODUCTION_READINESS_SCORECARD.md) for detailed scoring and remaining gaps, and [`AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`](AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md) for the phase-by-phase implementation gate.

## Closed blockers (completed in production hardening tranche)

| ID | Area | Required outcome | Evidence |
| --- | --- | --- | --- |
| PRD-001 | Logging | Structured application logging with request, job, scan, error, and audit events. | `webui/hosted_server.py` — structured JSON-line audit logging with request IDs, 15+ audited event types; `tests/test_webui_audit_logging.py` |
| PRD-002 | Web server | Documented reverse-proxy or ASGI/WSGI production deployment path. | `docs/DEPLOYMENT.md` — nginx/Caddy reverse proxy configs; `docs/RUNBOOK.md` — proxy verification steps |
| PRD-003 | Web UI consolidation | One supported web runtime with legacy paths removed. | `webui/server.py` removed; only `webui/hosted_server.py` remains |
| PRD-004 | Authentication | Auth enabled for non-local deployments, env/secret token source, no shared credentials. | `webui/auth.py` — env-driven token auth, hmac compare, production-mode validation; `tests/test_webui_auth_production.py` |
| PRD-005 | Web hardening | CSRF, rate limiting, security headers, request limits. | `webui/hosted_server.py` — CSRF with TTL/cleanup, rate limiting, CSP/HSTS/XFO headers, 10MB request limit; `tests/test_webui_csrf.py`, `tests/test_webui_rate_limit.py`, `tests/test_webui_security_headers.py` |
| PRD-006 | Configuration | Environment-variable overrides for all runtime paths. | `webui/hosted_server.py` — VULNORAIQ_CONFIG_DIR, VULNORAIQ_WEB_OUTPUT_ROOT, VULNORAIQ_JOB_STORE_PATH, VULNORAIQ_WEB_USERS_PATH, etc. |
| PRD-007 | Persistence | SQLite-backed job persistence with migrations. | `webui/persistent_jobs.py` — SqliteJobStore with WAL, foreign keys, schema versioning; `tests/test_sqlite_job_store.py` |
| PRD-008 | Containerisation | Deployable container baseline. | `Dockerfile` — non-root user, /data volume, healthcheck; `.dockerignore`; `docker-compose.yml` |
| PRD-009 | Quality gates | Ruff, mypy, CI enforcement. | `.github/workflows/ci.yml`, `.github/workflows/python-ci.yml` — ruff check, mypy, pytest, metadata validation |
| PRD-010 | Observability | Health, readiness, metrics endpoints. | `/healthz`, `/readyz`, `/metrics` in `webui/hosted_server.py`; `tests/test_metrics.py` |
| PRD-011 | Agentic mapping governance | CI fails if any active oracle/check lacks OWASP family, OWASP ID, MITRE ATLAS tactic, mapping status, evidence surface, or manual-review flag. | `scripts/validate_owasp_atlas_mappings.py`; `tests/test_owasp_atlas_mapping_validation.py`; `.github/workflows/ci.yml`; `.github/workflows/python-ci.yml` |

## Current controlled-internal readiness (scored at 10/10)

All blockers PRD-001 through PRD-011 are **Closed**. See [`PRODUCTION_READINESS_SCORECARD.md`](PRODUCTION_READINESS_SCORECARD.md) for detailed section scoring.

## Remaining gaps for public internet / SaaS / multi-tenant

| Area | Gap | Priority |
| --- | --- | --- |
| TLS termination | Relies on reverse proxy (nginx/Caddy); not built-in | Medium |
| Horizontal scaling | No shared-nothing / stateless design | High |
| OIDC/SSO | Proxy-header identity only; no direct OIDC | Medium |
| Database HA | SQLite is single-file; requires NAS/backup | Low |
| Full audit trail | Missing user-management events (create/delete/role-change) | Low |
| Penetration testing | No third-party pentest results | High |
| Multi-tenancy | No tenant isolation or per-tenant config | High |
| Rate limiting per-user | IP-based only; not per-authenticated-user | Medium |
| Secrets rotation | Documented but no automated rotation tool | Medium |

### Notes on scoring

The 10/10 gate-compliance score means all PRD-001 through PRD-011 blockers are closed. The actual scorecard average for controlled internal deployment is **8.5/10** (see [`PRODUCTION_READINESS_SCORECARD.md`](PRODUCTION_READINESS_SCORECARD.md)), reflecting remaining non-blocking maturity items such as SIEM integration, OIDC, signed releases, SAST/DAST, public/SaaS architecture, and independent assurance.

## Production claim rule

Do not describe VulnoraIQ as public-internet or multi-tenant SaaS ready until the remaining gaps above are addressed. Controlled internal deployment readiness is attested by this register, the scorecard, the Agentic Applications Production Readiness Plan, and the production-readiness validation gate.
