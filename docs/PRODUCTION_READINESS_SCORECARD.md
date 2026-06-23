# Production Readiness Scorecard

**Assessment date:** 2026-06-23  
**Scope:** VulnoraIQ `0.2.0` controlled internal enterprise deployment for authorised LLM, RAG, tool-using, agentic, and GenAI data-security assessments.  
**Rating scale:** 0-10, where 10 means fully hardened for the stated scope.

## Verdict

VulnoraIQ is **ready for controlled internal enterprise deployment** when deployed with production configuration validation, strong environment-backed tokens or trusted reverse-proxy identity, reverse-proxy/TLS controls, SQLite persistence, and the documented runbook/incident-response process.

The GenAI Security readiness gate is now **working starter complete** for controlled internal assessment use: `DSGAI01–DSGAI21` have safe synthetic scenario coverage, deterministic evaluator primitives, required evidence fields, source discrepancy tracking, package metadata validation, tests, and CI workflow gates.

VulnoraIQ is **not ready for public internet-facing, multi-tenant SaaS, unsupervised production hosting, production-validated real-world GenAI detection assurance, or certified VAPT-grade assurance**. Those capabilities remain deferred to the public/SaaS and independent-assurance backlog.

## Controlled internal deployment scorecard

| Area | Score | Evidence | Remaining gap | Blocking for controlled internal? |
| --- | ---: | --- | --- | --- |
| 1. Authentication and authorisation | 9/10 | `webui/auth.py`, `webui/production_checks.py`, `tests/test_webui_auth_production.py`, `tests/test_webui_auth_and_persistence.py` | No token revocation service or direct OIDC/SSO. | No |
| 2. CSRF / session protection | 9/10 | `webui/hosted_server.py`, `tests/test_webui_csrf.py`, `tests/test_webui_auth_and_persistence.py` | In-memory CSRF store is single-instance only. | No |
| 3. Request hardening | 9/10 | `webui/hosted_server.py`, `webui/production_checks.py`, `tests/test_webui_request_errors.py` | No formal request model library or Content-Type schema enforcement. | No |
| 4. Rate limiting and abuse controls | 8/10 | `webui/hosted_server.py`, `tests/test_webui_rate_limit.py`, `.env.production.example` | Per-IP and in-memory only; no per-user/shared limiter. | No |
| 5. Security headers | 9/10 | `webui/hosted_server.py`, `tests/test_webui_security_headers.py` | No CSP reporting endpoint, COOP/COEP, or HSTS preload. | No |
| 6. Reverse proxy and TLS | 9/10 | `docs/DEPLOYMENT.md`, `docs/RUNBOOK.md`, `webui/production_checks.py`, `tests/test_webui_proxy_ip.py` | TLS delegated to nginx/Caddy/reverse proxy. | No |
| 7. Persistence and migrations | 9/10 | `webui/persistent_jobs.py`, `tests/test_sqlite_job_store.py`, `docs/MIGRATION.md` | No Alembic-style migration framework or PostgreSQL backend. | No |
| 8. Audit logging | 9/10 | `webui/hosted_server.py`, `tests/test_webui_audit_logging.py`, `docs/RUNBOOK.md` | Console JSON audit logging only; no shipped SIEM schema/rotation package. | No |
| 9. Observability and monitoring | 9/10 | `/healthz`, `/readyz`, `/metrics`, `tests/test_metrics.py`, Docker healthcheck | No alert rules, SLOs, or distributed tracing. | No |
| 10. Backup and restore | 9/10 | `scripts/backup_sqlite_store.py`, `scripts/restore_sqlite_store.py`, `tests/test_backup_restore.py`, `docs/RUNBOOK.md` | No automated backup scheduler or backup-age metric. | No |
| 11. Containerisation | 9/10 | `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `.env.production.example`, `tests/test_container_config.py` | No container image signing or container scanner workflow. | No |
| 12. CI/CD and quality gates | 9/10 | `.github/workflows/ci.yml`, `.github/workflows/python-ci.yml`, `pyproject.toml`, `tests/`, `scripts/validate_package_metadata.py`, `scripts/validate_production_testing_readiness.py`, `scripts/validate_owasp_atlas_mappings.py`, `scripts/validate_genai_readiness.py` | No build/publish release workflow, SAST/DAST pipeline, or image scan gate. | No |
| 13. Secrets management | 8/10 | `webui/auth.py`, `.env.production.example`, `webui/production_checks.py`, `docs/RUNBOOK.md` | No direct Vault/AWS/Azure/GCP secrets-manager integration or automated rotation. | No |
| 14. Operational runbooks | 7/10 | `docs/RUNBOOK.md`, `docs/DEPLOYMENT.md`, backup/restore scripts | Needs environment-specific contacts, alert thresholds, and capacity planning. | No |
| 15. Incident response | 6/10 | `docs/INCIDENT_RESPONSE.md`, audit logs, metrics, rollback guidance | Needs organisation-specific escalation contacts, breach-notification process, SIEM rules, and tabletop validation. | No |
| 16. Release management | 7/10 | `docs/RELEASE_CHECKLIST.md`, `CHANGELOG.md`, `scripts/build_release_package.py`, `scripts/validate_package_metadata.py` | No signed artifacts, canary release workflow, or automated release publishing. | No |
| 17. Scanner / evaluator assurance | 9/10 | `docs/ASSESSMENT_ASSURANCE.md`, `core/production_detection.py`, `core/evaluators.py`, `core/genai_evaluators.py`, `config/owasp_oracles.yaml`, `tests/test_production_detection.py`, `tests/test_genai_readiness_validation.py` | No independent validation against authorised real targets or certified VAPT assurance. | No |
| 18. Multi-instance / multi-tenant limitations | 8/10 | Single-instance deployment boundary, SQLite WAL persistence, reverse-proxy docs | No tenant isolation, shared CSRF/rate-limit state, or horizontally scalable database. | No for controlled internal; yes for SaaS. |
| 19. OWASP / MITRE ATLAS mapping governance | 9/10 | `scripts/validate_owasp_atlas_mappings.py`, `tests/test_owasp_atlas_mapping_validation.py`, `.github/workflows/ci.yml`, `.github/workflows/python-ci.yml` | Current mappings are framework mappings and require manual security review before assurance claims. | No |
| 20. GenAI Security readiness governance | 8/10 | `benchmarks/fixtures/genai/scenarios.yaml`, `core/genai_evaluators.py`, `scripts/validate_genai_readiness.py`, `tests/test_genai_readiness_validation.py`, CI workflows, `docs/genai/PRODUCTION_READINESS_PLAN.md` | Working-starter safe synthetic coverage only; needs real-world validation, provider inventory connectors, dashboard/report depth, and independent assurance. | No |

**Overall controlled internal score:** **8.5/10**

The gate-compliance register scores **10/10** because all controlled-internal blockers are closed. The scorecard remains lower because it includes non-blocking maturity items such as SIEM integration, OIDC, signed releases, SAST/DAST, public/SaaS architecture, GenAI real-world validation, and independent assurance.

## Public internet / SaaS readiness scorecard

| Area | Score | Blocking gaps |
| --- | ---: | --- |
| Authentication and authorisation | 3/10 | No direct OIDC/SSO, no tenant identity model, no account lockout. |
| CSRF / session protection | 4/10 | In-memory single-instance CSRF store; no shared session layer. |
| Request hardening | 4/10 | No WAF/CDN reference architecture, no formal request schema layer. |
| Rate limiting and abuse controls | 3/10 | No per-user, tenant, or shared distributed limiter. |
| Security headers | 5/10 | Needs CSP reporting, COOP/COEP, HSTS preload, public endpoint hardening. |
| Reverse proxy and TLS | 4/10 | TLS delegated; no public ingress/WAF/DDoS architecture. |
| Persistence and migrations | 3/10 | SQLite is not a SaaS database; no PostgreSQL/HA/multi-tenant backend. |
| Audit logging | 4/10 | No central log aggregation, immutable audit storage, or SIEM pack. |
| Observability and monitoring | 4/10 | No SLOs, alerts, synthetic monitoring, or incident paging integration. |
| Backup and restore | 3/10 | No PITR, database HA, RPO/RTO, or cross-region backup pattern. |
| Containerisation | 5/10 | No Helm/Kubernetes/registry signing/image scan reference implementation. |
| CI/CD and quality gates | 4/10 | No public release workflow, SAST/DAST, image signing, or staged deployment. |
| Secrets management | 4/10 | No dynamic secrets, KMS/Vault adapter, or automated rotation. |
| Operational runbooks | 3/10 | Runbook exists but lacks SaaS incident scale, tenant support, and HA recovery. |
| Incident response | 3/10 | Plan exists but needs organisation-specific SOC, legal, and customer notification process. |
| Release management | 3/10 | No canary/blue-green, migration automation, or signed release chain. |
| Scanner/evaluator assurance | 4/10 | No independent audit/certification or continuous adversarial benchmark. |
| Multi-instance / multi-tenant limitations | 2/10 | No tenant isolation or horizontally scalable architecture. |
| OWASP / MITRE ATLAS mapping governance | 6/10 | Good traceability foundation, but mappings are not assurance-certified. |
| GenAI Security readiness governance | 4/10 | Working-starter safe synthetic coverage only; no tenant-aware GenAI validation or independent assurance. |

**Overall public internet / SaaS score:** **3.8/10**

## Current release claim

Use:

> Controlled internal enterprise production-readiness gate passed.

Allowed GenAI-specific wording:

> GenAI Security working-starter readiness gate completed for controlled internal assessment use with safe synthetic `DSGAI01–DSGAI21` scenario coverage.

Do not use:

- public internet ready
- SaaS ready
- multi-tenant ready
- certified VAPT-grade ready
- production pentest replacement
- independently validated real-world GenAI detection coverage

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
  --output-dir reports/output/production-readiness \
  --screenshot docs/assets/vulnoraiq-dashboard-example.svg
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
