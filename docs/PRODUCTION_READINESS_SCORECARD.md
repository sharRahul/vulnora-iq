# Production Readiness Scorecard

**Assessment date:** 2026-06-23  
**Scope:** VulnoraIQ `0.2.0` self-hosted laptop/server deployment for authorised LLM, RAG, tool-using, agentic, and GenAI data-security assessments.  
**Rating scale:** 0-10, where 10 means fully hardened for the stated scope.

## Verdict

VulnoraIQ is **complete for the self-hosted internal deployment scope** when deployed with production configuration validation, strong environment-backed tokens or trusted reverse-proxy identity, reverse-proxy/TLS controls where remote internal access is required, SQLite persistence, and the documented runbook/incident-response process.

The local standalone launcher is **complete for laptop/workstation use**: cross-platform launchers start the local Web UI, run dependency/startup checks, prepare the local SQLite/output paths, open the browser, and provide a loopback launcher-mode stop control. Launcher mode is not the shared/production deployment path.

The GenAI Security readiness gate is now **complete for the current controlled-internal scenario-harness scope**: `DSGAI01–DSGAI21` have safe synthetic scenario coverage, deterministic evaluator primitives, required evidence fields, source discrepancy tracking, package metadata validation, tests, and CI workflow gates.

VulnoraIQ does **not** claim production-validated real-environment GenAI detection assurance or certified VAPT-grade assurance. Findings remain framework evidence requiring human review.

## Self-hosted deployment scorecard

| Area | Score | Evidence | Remaining maturity item | Blocking for self-hosted internal? |
| --- | ---: | --- | --- | --- |
| 1. Authentication and authorisation | 9/10 | `webui/auth.py`, `webui/production_checks.py`, `tests/test_webui_auth_production.py`, `tests/test_webui_auth_and_persistence.py` | Token revocation service or direct OIDC/SSO. | No |
| 2. CSRF / session protection | 9/10 | `webui/hosted_server.py`, `tests/test_webui_csrf.py`, `tests/test_webui_auth_and_persistence.py` | Shared CSRF state for multi-instance designs. | No |
| 3. Request hardening | 9/10 | `webui/hosted_server.py`, `webui/production_checks.py`, `tests/test_webui_request_errors.py` | Formal request model library or Content-Type schema enforcement. | No |
| 4. Rate limiting and abuse controls | 8/10 | `webui/hosted_server.py`, `tests/test_webui_rate_limit.py`, `.env.production.example` | Per-user/shared limiter. | No |
| 5. Security headers | 9/10 | `webui/hosted_server.py`, `tests/test_webui_security_headers.py` | CSP reporting endpoint, COOP/COEP, or HSTS preload. | No |
| 6. Reverse proxy and TLS | 9/10 | `docs/DEPLOYMENT.md`, `docs/RUNBOOK.md`, `webui/production_checks.py`, `tests/test_webui_proxy_ip.py` | Organisation-specific TLS/proxy deployment validation. | No |
| 7. Persistence and migrations | 9/10 | `webui/persistent_jobs.py`, `tests/test_sqlite_job_store.py`, `docs/MIGRATION.md` | Alembic-style migration framework or PostgreSQL backend. | No |
| 8. Audit logging | 9/10 | `webui/hosted_server.py`, `tests/test_webui_audit_logging.py`, `docs/RUNBOOK.md` | Shipped SIEM schema/rotation package. | No |
| 9. Observability and monitoring | 9/10 | `/healthz`, `/readyz`, `/metrics`, `tests/test_metrics.py`, Docker healthcheck | Alert rules, SLOs, or distributed tracing. | No |
| 10. Backup and restore | 9/10 | `scripts/backup_sqlite_store.py`, `scripts/restore_sqlite_store.py`, `tests/test_backup_restore.py`, `docs/RUNBOOK.md` | Automated backup scheduler or backup-age metric. | No |
| 11. Containerisation | 9/10 | `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `.env.production.example`, `tests/test_container_config.py` | Container image signing or container scanner workflow. | No |
| 12. CI/CD and quality gates | 9/10 | `.github/workflows/ci.yml`, `.github/workflows/python-ci.yml`, `pyproject.toml`, `tests/`, `scripts/validate_package_metadata.py`, `scripts/validate_production_testing_readiness.py`, `scripts/validate_owasp_atlas_mappings.py`, `scripts/validate_genai_readiness.py` | Build/publish release workflow, SAST/DAST pipeline, or image scan gate. | No |
| 13. Secrets management | 8/10 | `webui/auth.py`, `.env.production.example`, `webui/production_checks.py`, `docs/RUNBOOK.md` | Direct Vault/AWS/Azure/GCP secrets-manager integration or automated rotation. | No |
| 14. Operational runbooks | 8/10 | `docs/RUNBOOK.md`, `docs/DEPLOYMENT.md`, backup/restore scripts, launcher startup/shutdown docs | Environment-specific contacts, alert thresholds, and capacity planning. | No |
| 15. Incident response | 6/10 | `docs/INCIDENT_RESPONSE.md`, audit logs, metrics, rollback guidance | Organisation-specific escalation contacts, breach-notification process, SIEM rules, and tabletop validation. | No |
| 16. Release management | 7/10 | `docs/RELEASE_CHECKLIST.md`, `CHANGELOG.md`, `scripts/build_release_package.py`, `scripts/validate_package_metadata.py` | Signed artifacts, staged release workflow, or automated release publishing. | No |
| 17. Scanner / evaluator assurance | 9/10 | `docs/ASSESSMENT_ASSURANCE.md`, `core/production_detection.py`, `core/evaluators.py`, `core/genai_evaluators.py`, `config/owasp_oracles.yaml`, `tests/test_production_detection.py`, `tests/test_genai_readiness_validation.py` | Independent validation against approved real environments or certified VAPT assurance. | No |
| 18. Single-instance limitations | 8/10 | Single-instance deployment boundary, SQLite WAL persistence, reverse-proxy docs | Shared CSRF/rate-limit state or horizontally scalable database. | No |
| 19. OWASP / MITRE ATLAS mapping governance | 9/10 | `scripts/validate_owasp_atlas_mappings.py`, `tests/test_owasp_atlas_mapping_validation.py`, `.github/workflows/ci.yml`, `.github/workflows/python-ci.yml` | Manual security review before stronger assurance claims. | No |
| 20. GenAI Security readiness governance | 8/10 | `benchmarks/fixtures/genai/scenarios.yaml`, `core/genai_evaluators.py`, `scripts/validate_genai_readiness.py`, `tests/test_genai_readiness_validation.py`, CI workflows, `docs/genai/PRODUCTION_READINESS_PLAN.md` | Approved-environment validation, provider inventory connectors, dashboard/report depth, and independent assurance. | No |
| 21. Standalone local app startup | 8/10 | `launch-vulnoraiq-webui.*`, `scripts/launch_webui.py`, `webui/static/launcher-controls.*`, README launcher docs | Signed installers/native packages and broader OS-level QA. | No |

**Overall self-hosted internal score:** **8.5/10**

The gate-compliance register scores **10/10** because all self-hosted internal blockers are closed and all current-scope items are complete. The scorecard remains lower because it includes non-blocking maturity items such as SIEM integration, OIDC, signed releases, SAST/DAST, image scanning, GenAI approved-environment validation, native installers, and independent assurance.

## Current release claim

Use:

> Self-hosted laptop/server AI security testing application with controlled internal production-readiness gate passed.

Allowed GenAI-specific wording:

> GenAI Security readiness gate completed for controlled internal assessment use with safe synthetic `DSGAI01–DSGAI21` scenario coverage.

Allowed standalone-app wording:

> Local standalone launcher available for laptop/workstation self-hosted use with startup checks, browser launch, and loopback stop control.

Do not use:

- certified VAPT-grade ready
- production pentest replacement
- independently validated real-environment GenAI detection coverage
- launcher mode as a shared production service

## Validation commands

```bash
python -m pip install -e .[dev]
ruff check .
mypy .
pytest -q
python -m pip check
pip-audit
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py \
  --run-functional \
  --output-dir reports/output/production-readiness
```

## Related documents

- [`genai/PRODUCTION_READINESS_PLAN.md`](genai/PRODUCTION_READINESS_PLAN.md)
- [`AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`](AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md)
- [`PRODUCTION_HARDENING_BACKLOG.md`](PRODUCTION_HARDENING_BACKLOG.md)
- [`DEPLOYMENT.md`](DEPLOYMENT.md)
- [`RUNBOOK.md`](RUNBOOK.md)
- [`INCIDENT_RESPONSE.md`](INCIDENT_RESPONSE.md)
- [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md)
- [`ASSESSMENT_ASSURANCE.md`](ASSESSMENT_ASSURANCE.md)

*This scorecard is a living document. Update it whenever a control is added, downgraded, deferred, or independently validated.*
