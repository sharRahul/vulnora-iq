# Production Hardening Backlog

Status: live blocker register  
Current operational readiness: 10/10 (controlled internal deployment)  
Target: controlled production assessment readiness, not SaaS multi-tenant production hosting.

## Current verdict

VulnoraIQ is ready for **controlled internal enterprise deployment** with the security, operational, deployment, Agentic Applications, and GenAI Security working-starter controls listed below. The Agentic Applications Production Readiness Plan is **complete for phases 0-8** under this controlled-internal scope. The GenAI Security Production Readiness Plan is **complete at working-starter level for `DSGAI01–DSGAI21`** with safe synthetic scenario manifests, deterministic evaluators, and CI validation. VulnoraIQ is **not ready for public internet-facing, multi-tenant SaaS, unsupervised production hosting, or certified VAPT-grade assurance**.

See [`PRODUCTION_READINESS_SCORECARD.md`](PRODUCTION_READINESS_SCORECARD.md) for detailed scoring, [`AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`](AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md) for agentic phase gates, and [`genai/PRODUCTION_READINESS_PLAN.md`](genai/PRODUCTION_READINESS_PLAN.md) for GenAI Security phase gates.

## Closed blockers (completed in production hardening tranche)

| ID | Area | Required outcome | Evidence |
| --- | --- | --- | --- |
| PRD-001 | Logging | Structured application logging with request, job, scan, error, and audit events. | `webui/hosted_server.py`; `tests/test_webui_audit_logging.py` |
| PRD-002 | Web server | Documented reverse-proxy or production deployment path. | `docs/DEPLOYMENT.md`; `docs/RUNBOOK.md` |
| PRD-003 | Web UI consolidation | One supported web runtime with legacy paths removed. | `webui/server.py` removed; only `webui/hosted_server.py` remains |
| PRD-004 | Authentication | Auth enabled for non-local deployments, env/secret token source, no shared credentials. | `webui/auth.py`; `tests/test_webui_auth_production.py` |
| PRD-005 | Web hardening | CSRF, rate limiting, security headers, request limits. | `webui/hosted_server.py`; `tests/test_webui_csrf.py`; `tests/test_webui_rate_limit.py`; `tests/test_webui_security_headers.py` |
| PRD-006 | Configuration | Environment-variable overrides for all runtime paths. | `webui/hosted_server.py` runtime env support |
| PRD-007 | Persistence | SQLite-backed job persistence with migrations. | `webui/persistent_jobs.py`; `tests/test_sqlite_job_store.py` |
| PRD-008 | Containerisation | Deployable container baseline. | `Dockerfile`; `.dockerignore`; `docker-compose.yml` |
| PRD-009 | Quality gates | Ruff, mypy, CI enforcement. | `.github/workflows/ci.yml`; `.github/workflows/python-ci.yml` |
| PRD-010 | Observability | Health, readiness, metrics endpoints. | `/healthz`, `/readyz`, `/metrics`; `tests/test_metrics.py` |
| PRD-011 | Agentic mapping governance | CI fails if active oracle/check mapping metadata is missing. | `scripts/validate_owasp_atlas_mappings.py`; `tests/test_owasp_atlas_mapping_validation.py`; CI workflows |
| PRD-012 | GenAI Security readiness governance | CI fails if GenAI scenario coverage, evidence fields, source discrepancy tracking, or docs readiness drift. | `benchmarks/fixtures/genai/scenarios.yaml`; `core/genai_evaluators.py`; `scripts/validate_genai_readiness.py`; `tests/test_genai_readiness_validation.py`; CI workflows |

## Current controlled-internal readiness

All blockers PRD-001 through PRD-012 are **Closed** for the controlled internal deployment and assessment-readiness scope.

## Remaining gaps for public internet / SaaS / multi-tenant

| Area | Gap | Priority |
| --- | --- | --- |
| TLS termination | Relies on reverse proxy (nginx/Caddy); not built-in | Medium |
| Horizontal scaling | No shared-nothing / stateless design | High |
| OIDC/SSO | Proxy-header identity only; no direct OIDC | Medium |
| Database HA | SQLite is single-file; requires NAS/backup | Low |
| Full audit trail | Missing user-management events (create/delete/role-change) | Low |
| Independent assurance | No third-party assessment results | High |
| Multi-tenancy | No tenant isolation or per-tenant config | High |
| Rate limiting per-user | IP-based only; not per-authenticated-user | Medium |
| Secrets rotation | Documented but no automated rotation tool | Medium |
| GenAI real-world validation | Current GenAI coverage is safe synthetic working-starter coverage, not validated against authorised real environments | High |
| GenAI provider/data inventory | No native provider inventory connector or organisation-specific data catalogue integration | Medium |

### Notes on scoring

The 10/10 gate-compliance score means all PRD-001 through PRD-012 blockers are closed. The actual scorecard average for controlled internal deployment remains lower because it includes non-blocking maturity items such as SIEM integration, OIDC, signed releases, SAST/DAST, public/SaaS architecture, GenAI real-world validation, and independent assurance.

## Production claim rule

Do not describe VulnoraIQ as public-internet, multi-tenant SaaS, certified VAPT-grade, or independently production-validated for all GenAI categories until the remaining gaps above are addressed. Controlled internal deployment readiness is attested by this register, the scorecard, the completed Agentic Applications readiness plan, the completed GenAI Security working-starter readiness plan, and the production-readiness validation gates.
