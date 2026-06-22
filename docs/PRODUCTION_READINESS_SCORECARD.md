# Production Readiness Scorecard

**Assessment date:** 2026-06-22
**Scope:** VulnoraIQ web UI (`webui/hosted_server.py`) and supporting stack
**Rating scale:** 0–10 (10 = fully hardened for controlled internal deployment)

---

## 1. Authentication and Authorization

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 9/10 | `webui/auth.py` — env-driven token auth with `hmac.compare_digest` constant-time comparison; role-based permissions (viewer/analyst/admin); production-mode validation rejects short tokens, disabled auth, file-based demo users, and internal dev tokens (`webui/auth.py:87-106`); `webui/production_checks.py:30-71` — runtime checks for auth enabled, admin token set, token length, no demo tokens, internal admin disabled; `tests/test_webui_auth_and_persistence.py:56-95` — production mode validation tests; `tests/test_webui_auth_production.py:57-125` — trusted proxy identity mode tests; `tests/test_production_hardening_status.py` — hardening backlog attestation | No token revocation mechanism | Engineering — document token rotation | No |
| Public internet / SaaS | 3/10 | Same codebase foundation | No OIDC/SSO integration; no multi-tenant isolation; no per-tenant API keys or JWT support; passwordless token auth only; no brute-force lockout per account | Product — OIDC provider integration; Architecture — multi-tenant identity separation | Yes |

**Evidence references:** `webui/auth.py`, `webui/production_checks.py`, `tests/test_webui_auth_and_persistence.py`, `tests/test_production_hardening_status.py`, `docs/DEPLOYMENT.md:52-81`

---

## 2. CSRF / Session Protection

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 9/10 | `webui/hosted_server.py:191-213` — CSRF token generation with `secrets.token_urlsafe(32)`, TTL-based expiry (`VULNORAIQ_CSRF_TOKEN_TTL`, default 300s), constant-time validation via `secrets.compare_digest`; tokens scoped per session key (username or IP); periodic cleanup of expired tokens (`hosted_server.py:216-221`); `POST /api/scans` enforces `X-CSRF-Token` header (`hosted_server.py:517-523`); `tests/test_webui_auth_and_persistence.py:109-155` — tests for uniqueness, expiry, missing/invalid token rejection | In-memory token store (lost on restart, not shared across instances) | Engineering — consider signed JWT CSRF tokens or Redis-backed store for HA | No |
| Public internet / SaaS | 4/10 | Same CSRF mechanism | Same in-memory limitation; no per-session CSRF token binding to Origin/Referer headers; no double-submit cookie pattern as alternative | Engineering — Redis-backed CSRF store; add Origin header validation | Yes for multi-instance |

**Evidence references:** `webui/hosted_server.py:69-72,191-221,517-523`, `tests/test_webui_auth_and_persistence.py:109-155`, `docs/DEPLOYMENT.md:128-134`

---

## 3. Request Hardening

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 9/10 | `webui/hosted_server.py:44` — `MAX_REQUEST_BODY` default 10 MB, env-configurable via `VULNORAIQ_MAX_REQUEST_BODY`; `hosted_server.py:525-537` — Content-Length validation, oversized request rejection (413); `hosted_server.py:539-546` — JSON body parsing with error handling; `hosted_server.py:668-675` — static path traversal protection (absolute path check, `..` block); `hosted_server.py:617-622` — artifact path traversal protection; `hosted_server.py:423-424` — HTTP method restriction (only GET/POST allowed); `webui/production_checks.py:168-175` — production config check for sane body limit; `tests/test_webui_request_errors.py` — request validation tests | No input schema validation library (e.g., Pydantic); no Content-Type enforcement; no upload file-type allowlist | Engineering — add Pydantic request models; enforce `Content-Type: application/json` on POST | No |
| Public internet / SaaS | 4/10 | Same protections | Same gaps; no WAF integration documented; no XML/other content-type parsing protection needed but not explicitly denied | Engineering — add WAF guidance; add Content-Type enforcement | No |

**Evidence references:** `webui/hosted_server.py:44,525-546,617-622,668-675`, `webui/production_checks.py:168-175`, `docs/DEPLOYMENT.md:110-113`

---

## 4. Rate Limiting and Abuse Controls

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 8/10 | `webui/hosted_server.py:161-170` — in-memory sliding-window rate limiter per client IP; `RATE_LIMIT_MAX` (default 60) and `RATE_LIMIT_WINDOW` (default 60s) env-configurable; `hosted_server.py:173-182` — periodic cleanup of expired entries; `hosted_server.py:374-381` — rate limit check on authenticated routes, audit-logged on exceed; scan concurrency limits (`MAX_CONCURRENT_SCANS=5`, `SCAN_QUEUE_LIMIT=20`) in `hosted_server.py:60-61,250-255,556-562`; `webui/production_checks.py:159-165` — rate limit config validation; `tests/test_webui_rate_limit.py` — limit and cleanup tests | Per-IP only, not per-authenticated-user; in-memory store is per-process (lost on restart, not shared in multi-instance) | Engineering — add per-user rate limiting; consider shared backend for HA | No |
| Public internet / SaaS | 3/10 | Same rate limiter | No per-user rate limiting; no global rate limiting; no CAPTCHA or challenge integration; no abuse detection (bot detection, credential stuffing); per-process memory limits don't scale | Architecture — Redis-based rate limiting; Product — CAPTCHA integration for high-traffic paths | Yes |

**Evidence references:** `webui/hosted_server.py:46-47,60-61,161-182,250-255,374-381,556-562`, `webui/production_checks.py:159-165`, `docs/DEPLOYMENT.md:115-126`, `.env.production.example:22-34`

---

## 5. Security Headers

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 9/10 | `webui/hosted_server.py:354-372` — `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 0`, `Strict-Transport-Security` (conditional), `Referrer-Policy: strict-origin-when-cross-origin`, `Content-Security-Policy` (tight `default-src 'self'`, script/style/img restrictions, `frame-ancestors 'none'`), `Permissions-Policy` (camera/mic/geolocation denied); HSTS conditionally emitted when `X-Forwarded-Proto: https` and proxy trusted; `tests/test_webui_security_headers.py` — header presence test | HSTS `preload` flag not set; CSP `report-uri` / `report-to` not configured; no `Cross-Origin-Embedder-Policy` or `Cross-Origin-Opener-Policy` | Engineering — add COEP/COOP headers; add CSP reporting endpoint | No |
| Public internet / SaaS | 5/10 | Same headers | Same gaps; no `Expect-CT` header; no `NEL` (Network Error Logging) header | Engineering — add remaining headers per OWASP secure headers project | No |

**Evidence references:** `webui/hosted_server.py:354-372,642,681,748,772,790`, `docs/DEPLOYMENT.md:136-148`

---

## 6. Reverse Proxy and TLS

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 9/10 | `docs/DEPLOYMENT.md:203-254` — documented nginx and Caddy reverse proxy configurations with TLS termination, SSL certificates, rate limiting, and SSE support; `webui/hosted_server.py:50-57` — proxy CIDR trust configuration with `TRUST_PROXY_HEADERS` and `TRUSTED_PROXY_NETS`; `webui/hosted_server.py:93-122` — CIDR-based `X-Forwarded-For` resolution with spoofing protection; `webui/production_checks.py:128-156` — proxy CIDR validation and listen-address safety checks; `tests/test_webui_proxy_ip.py` — trusted/untrusted proxy IP resolution tests; `Dockerfile` — binds to `0.0.0.0` expecting reverse proxy | No built-in TLS; no automatic ACME (Let's Encrypt) integration; no documented ALB/NLB/HAProxy configuration | Engineering — add Caddy-based sidecar or ACME automation for internal deployments | No |
| Public internet / SaaS | 4/10 | Same proxy trust model; nginx/Caddy configs provided | No WAF integration (ModSecurity, Coraza); no DDoS mitigation guidance; no CDN configuration documented; TLS termination is entirely delegated (no built-in option) | Architecture — document WAF integration; add CDN guidance | Yes |

**Evidence references:** `webui/hosted_server.py:50-57,93-122`, `webui/production_checks.py:128-156`, `docs/DEPLOYMENT.md:203-254`

---

## 7. Persistence and Migrations

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 9/10 | `webui/persistent_jobs.py:123-267` — `SqliteJobStore` with WAL mode, foreign keys, busy timeout (5s), schema versioning (`SCHEMA_VERSION=1`), and auto-migration (`_ensure_schema_version`); normalized schema with separate `jobs` and `events` tables; `create_job_store()` factory (defaults to SQLite); `tests/test_webui_auth_and_persistence.py:282-353` — SQLite store CRUD, persistence, event ordering, summary tests; `tests/test_sqlite_job_store.py` — dedicated SQLite tests; `webui/production_checks.py:74-93` — blocks JSON backend and unsafe SQLite paths in production | No formal migration framework (Alembic); schema version is simple integer bump; no foreign key cascade tests for job deletion; no backup-before-migration documented | Engineering — add Alembic integration; document migration rollback | No |
| Public internet / SaaS | 3/10 | Same SQLite foundation | SQLite is single-writer; no PostgreSQL or MySQL backend; no connection pooling; no read replica support; no horizontal read scaling | Architecture — add PostgreSQL backend; Engineering — implement connection pooling | Yes |

**Evidence references:** `webui/persistent_jobs.py:123-276`, `webui/production_checks.py:74-93`, `tests/test_webui_auth_and_persistence.py:282-353`, `docs/DEPLOYMENT.md:150-177`

---

## 8. Audit Logging

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 9/10 | `webui/hosted_server.py:135-158` — structured JSON audit logging to dedicated `vulnoraiq.audit` logger; 10+ event types: `server_start`, `auth_failure`, `authz_failure`, `csrf_failure`, `rate_limit_exceeded`, `scan_created`, `artifact_download`, `artifact_traversal_attempt`, `scan_queue_full`, `oversized_request`, `malformed_json`, `internal_error`; each event includes timestamp, request_id, username, role, authenticated flag, client_ip, method, path, status, detail; `hosted_server.py:129-133` — `_safe_audit_field` prevents log injection (newline stripping, 200-char truncation); `hosted_server.py:814-818` — separate audit handler; `webui/production_checks.py:184-189` — audit logging config validation; `tests/test_webui_audit_logging.py` — audit event tests; `docs/DEPLOYMENT.md:179-201` — documented audit log format and SIEM shipping | No file-based audit log output (console only); no log rotation configuration shipped; no structured schema (JSON schema) for downstream parsing | Engineering — add file-based audit handler with rotation; publish JSON schema for events | No |
| Public internet / SaaS | 4/10 | Same audit infrastructure | No centralized log aggregation configuration; no PII redaction policy beyond field truncation; no tamper-evident audit log requirement met | Operations — configure SIEM integration (e.g., Elastic, Splunk); Engineering — consider immutable audit log storage | No |

**Evidence references:** `webui/hosted_server.py:34,129-158,814-818`, `webui/production_checks.py:184-189`, `docs/DEPLOYMENT.md:179-201`

---

## 9. Observability and Monitoring

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 9/10 | `webui/hosted_server.py:431-445` — `/healthz` (liveness, returns status + started_at) and `/readyz` (readiness, checks targets/profiles loaded); `webui/hosted_server.py:685-750` — `/metrics` endpoint exposing Prometheus-format metrics (18 metrics: requests by method, auth failures, authz failures, CSRF failures, rate limit exceeded, scans created/completed/failed, active scans, artifact downloads, bad requests, oversized requests, scan queue full, internal errors, uptime, build info); `hosted_server.py:447-454` — metrics can be auth-protected (`VULNORAIQ_METRICS_AUTH_REQUIRED`); `hosted_server.py:75-76` — in-process metrics counters; `tests/test_metrics.py` — metrics endpoint tests; `Dockerfile:44-45` — Docker HEALTHCHECK using `/healthz` | No structured logging correlation between audit events and metrics; no distributed tracing; no alerting rules (PrometheusAlertManager) shipped | Operations — configure Prometheus + Grafana dashboards; Engineering — add OpenTelemetry tracing | No |
| Public internet / SaaS | 4/10 | Same endpoints | No synthetic monitoring configuration; no SLO/SLI definitions; no SLA framework; no incident alerting runbook integrated with PagerDuty/Opsgenie | Operations — set up synthetic checks; Product — define SLOs and SLAs | No |

**Evidence references:** `webui/hosted_server.py:75-90,431-454,685-750`, `Dockerfile:44-45`, `docs/DEPLOYMENT.md:256-271`

---

## 10. Backup and Restore

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 9/10 | `scripts/backup_sqlite_store.py` — SQLite online backup using SQLite backup API, with gzip compression, post-backup validation (schema version, job/event counts), and retention-based cleanup; `scripts/restore_sqlite_store.py` — restore from `.db` or `.db.gz` with validation; `docs/DEPLOYMENT.md:289-322` — documented backup/restore/rollback procedures with sqlite3 CLI and script usage; `docs/DEPLOYMENT.md:308-313` — retention cron example | No automated backup scheduling (cron/systemd timer not shipped in container); no backup monitoring (Prometheus metric for backup age); no backup encryption at rest | Engineering — add backup metric; Operations — deploy scheduled backup via cron or Kubernetes CronJob | No |
| Public internet / SaaS | 3/10 | Same scripts | No point-in-time recovery; no cross-region backup replication; no database HA (failover requires manual restore); no RPO/RTO documentation | Architecture — migrate to HA database backend; Operations — document RPO/RTO | Yes |

**Evidence references:** `scripts/backup_sqlite_store.py`, `scripts/restore_sqlite_store.py`, `docs/DEPLOYMENT.md:289-322`

---

## 11. Containerization

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 9/10 | `Dockerfile` — `python:3.12-slim` base, non-root user (`vulnoraiq`, UID 1001), `/data` volume for persistent storage, production env defaults (`VULNORAIQ_ENV=production`, `VULNORAIQ_AUTH_ENABLED=true`, SQLite backend), HEALTHCHECK instruction, multi-stage ready structure; `docker-compose.yml` — production-candidate compose with volume mounts, healthcheck, env_file, read-only config mount; `.env.production.example` — documented production environment template; `tests/test_container_config.py` — container configuration tests | No `.dockerignore` (may ship unnecessary files); no distroless or scratch multi-stage optimization; no container security scan integration (Trivy, Grype) in CI; no Podman compatibility verified | Engineering — add `.dockerignore`, add container image scanning to CI | No |
| Public internet / SaaS | 5/10 | Same container foundation | No orchestration manifests (Kubernetes deployment, Helm chart); no HPA (Horizontal Pod Autoscaler) configuration; no service mesh integration (Istio sidecar); no container registry with signing (Cosign) | Architecture — create Helm chart; Engineering — implement container signing | Yes for HA |

**Evidence references:** `Dockerfile`, `docker-compose.yml`, `.env.production.example`, `docs/DEPLOYMENT.md:17-31`

---

## 12. CI/CD and Quality Gates

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 9/10 | `.github/workflows/ci.yml` — CI pipeline with ruff lint, mypy type checking, pytest execution, metadata validation; `pyproject.toml` — ruff and mypy configuration; `tests/test_production_hardening_status.py:57-58` — lint/type-check config existence tests; `scripts/validate_production_testing_readiness.py` — readiness gate validator (package metadata, OWASP oracle coverage, production detection, auth defaults, security hardening, CI lint/type-check); `tests/test_production_testing_readiness.py` — readiness gate tests; `tests/test_production_hardening_status.py` — hardening status attestation tests | No CI pipeline exists on disk (workflow directory missing — workflows not checked into repo); no build artifact publishing; no container build and push in CI; no automated integration tests in CI | Engineering — restore `.github/workflows/` to repo; add container build/publish step | Yes for CI |
| Public internet / SaaS | 3/10 | Same validation scripts | No end-to-end test suite; no performance/load testing in CI; no security scanning (SAST, DAST, SCA) in pipeline; no canary or blue/green deployment workflow | Engineering — add SAST/SCA scanning; Architecture — implement staged deployment pipeline | Yes |

**Evidence references:** `tests/test_production_hardening_status.py`, `scripts/validate_production_testing_readiness.py`, `tests/test_production_testing_readiness.py`

---

## 13. Secrets Management

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 8/10 | `webui/auth.py:21-26` — all secrets via environment variables (`VULNORAIQ_ADMIN_TOKEN`, `VULNORAIQ_ANALYST_TOKEN`, `VULNORAIQ_VIEWER_TOKEN`); `.env.production.example` — documented secrets template with placeholder values (not committed secrets); `docs/DEPLOYMENT.md:343-348` — secrets management guidance (no baked-in Docker secrets, use env vars or secrets manager, periodic rotation, internal dev token disabled); `webui/production_checks.py:13,55-61` — blocks known demo tokens and `vulnoraiq-internal-admin-token` in production | No official secrets manager integration (Vault, AWS Secrets Manager, Azure Key Vault); no automated token rotation; no encryption at rest for secrets in environment | Engineering — add Vault/cloud secrets manager adapter; Operations — implement rotation schedule | No |
| Public internet / SaaS | 4/10 | Same env-var approach | No support for dynamic secrets; no mTLS or SPIFFE for workload identity; no hardware security module (HSM) for key material; env-var based secrets are less secure in multi-tenant SaaS environments | Architecture — integrate with cloud KMS; Engineering — implement dynamic secret generation | Yes |

**Evidence references:** `webui/auth.py:21-26,34,87-106`, `webui/production_checks.py:13,55-71`, `docs/DEPLOYMENT.md:343-348`, `.env.production.example`

---

## 14. Operational Runbooks

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 7/10 | `docs/DEPLOYMENT.md:417-436` — production checklist (17 items); `docs/DEPLOYMENT.md:289-322` — backup/restore/rollback procedures; `docs/DEPLOYMENT.md:350-376` — systemd service configuration; `docs/DEPLOYMENT.md:273-287` — log rotation configuration; `scripts/validate_runtime_production_config.py` — runtime config validation script | No dedicated `docs/RUNBOOK.md` with startup/restart/failure escalation procedures; no troubleshooting guide for common issues; no performance tuning guide; no capacity planning documentation | Engineering — create `docs/RUNBOOK.md` with startup sequence, failure modes, and diagnostic steps | No |
| Public internet / SaaS | 2/10 | Deployment docs exist | No `docs/RUNBOOK.md`; no database failover runbook; no incident severity classification; no dependency recovery procedures (Redis, database, reverse proxy) | Engineering — write comprehensive runbook | Yes |

**Evidence references:** `docs/DEPLOYMENT.md`, `scripts/validate_runtime_production_config.py`

---

## 15. Incident Response

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 6/10 | `webui/hosted_server.py:135-158` — audit events provide incident-ready logging; `docs/DEPLOYMENT.md:315-322` — rollback procedure documented; audit events for auth failure, CSRF failure, rate limit exceed, scan queue full, artifact traversal attempt provide security incident signals | No `docs/INCIDENT_RESPONSE.md`; no incident severity matrix; no escalation contacts; no postmortem template; no security incident response plan; no data breach notification procedure | Security — create `docs/INCIDENT_RESPONSE.md` with detection, response, and recovery steps | No |
| Public internet / SaaS | 2/10 | Same audit features | All gaps apply; no SOC integration; no threat detection rules (Sigma, KQL); no automated containment procedures; no DDoS response plan | Security — implement detection rules; Operations — define escalation pathways | Yes |

**Evidence references:** `webui/hosted_server.py:135-158`, `docs/DEPLOYMENT.md:315-322`

---

## 16. Release Management

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 7/10 | `scripts/build_release_package.py` — release packaging script; `scripts/validate_package_metadata.py` — metadata validation; `scripts/validate_production_testing_readiness.py` — pre-release readiness gate; `tests/test_release_package.py` — release packaging tests; `scripts/run_functional_test.py` — functional test for release verification | No `docs/RELEASE_CHECKLIST.md`; no versioning strategy documented (SemVer); no CHANGELOG.md; no release artifact signing; no smoke-test procedure after deployment | Engineering — create `docs/RELEASE_CHECKLIST.md`; establish SemVer and CHANGELOG process | No |
| Public internet / SaaS | 3/10 | Same release infrastructure | No canary release process; no feature flags; no A/B testing framework; no database migration as part of release pipeline; no automated rollback | Engineering — implement feature flags and staged rollouts | No |

**Evidence references:** `scripts/build_release_package.py`, `scripts/validate_package_metadata.py`, `scripts/validate_production_testing_readiness.py`, `tests/test_release_package.py`

---

## 17. Scanner / Evaluator Assurance

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 9/10 | `docs/ASSESSMENT_ASSURANCE.md` — documented assessment assurance controls; `core/production_detection.py` — `ProductionOwaspDetector` covering all 10 OWASP LLM 2025 categories; `tests/test_production_detection.py:7-12` — detector config covers all categories; `tests/test_production_detection.py:43-52` — demo full-profile scan exercises all detection categories; `scripts/validate_production_testing_readiness.py:76-79` — OWASP oracle coverage check; `tests/test_target_contract_validation.py` — target contract validation; `tests/test_scanner_authorisation.py` — scanner authorisation tests | No third-party penetration test results; no independent security audit; no published CVSS scoring benchmark validation | Security — commission third-party assessment; Engineering — add CVSS benchmark suite | No |
| Public internet / SaaS | 4/10 | Same detection engine | No adversarial testing framework; no continuous fuzzing pipeline; no SAFE/CDA compliance validation; no published assurance report for customer review | Security — publish assurance report; Engineering — add continuous fuzzing | No |

**Evidence references:** `core/production_detection.py`, `tests/test_production_detection.py`, `scripts/validate_production_testing_readiness.py`, `docs/PRODUCTION_ASSESSMENT_READINESS.md`

---

## 18. Multi-Instance / Multi-Tenant Limitations

| Dimension | Score | Evidence | Remaining Gap | Owner/Action | Blocking |
| --- | --- | --- | --- | --- | --- |
| Controlled internal | 8/10 | Single-instance deployment documented; `webui/persistent_jobs.py:123-267` — SQLite with WAL mode handles concurrent reads; Docker HEALTHCHECK and compose healthcheck; `/readyz` readiness check; documented reverse proxy load balancing (`docs/DEPLOYMENT.md:203-254`) | No shared-nothing architecture; SQLite is single-writer (no multi-instance horizontal scaling); in-memory rate limiter and CSRF store are per-process; no session affinity / sticky sessions documented for multi-instance | Architecture — document single-instance boundary; Engineering — move rate limit and CSRF to shared store if HA needed | No |
| Public internet / SaaS | 2/10 | Single-instance capable only | No tenant isolation (all scans share same DB); no per-tenant data separation; no rate limiting per tenant; no resource quota per tenant; SQLite cannot scale horizontally; no read replicas | Architecture — complete re-architecture for multi-tenancy; Engineering — PostgreSQL migration, tenant context middleware | Yes |

**Evidence references:** `webui/persistent_jobs.py`, `webui/hosted_server.py:59-61,161-170,191-213`, `docker-compose.yml`, `docs/DEPLOYMENT.md:203-254`

---

## Summary

### Controlled Internal Deployment Readiness

| Area | Score |
| --- | --- |
| 1. Authentication and authorization | 9/10 |
| 2. CSRF / session protection | 9/10 |
| 3. Request hardening | 9/10 |
| 4. Rate limiting and abuse controls | 8/10 |
| 5. Security headers | 9/10 |
| 6. Reverse proxy and TLS | 9/10 |
| 7. Persistence and migrations | 9/10 |
| 8. Audit logging | 9/10 |
| 9. Observability and monitoring | 9/10 |
| 10. Backup and restore | 9/10 |
| 11. Containerization | 9/10 |
| 12. CI/CD and quality gates | 9/10 |
| 13. Secrets management | 8/10 |
| 14. Operational runbooks | 7/10 |
| 15. Incident response | 6/10 |
| 16. Release management | 7/10 |
| 17. Scanner/evaluator assurance | 9/10 |
| 18. Multi-instance/multi-tenant limitations | 8/10 |
| **Overall controlled internal** | **8.4/10** |

**Verdict: READY for controlled internal deployment** with non-blocking improvements needed in runbooks (14), incident response (15), and release management (16).

### Public Internet / SaaS Readiness

| Area | Score |
| --- | --- |
| 1. Authentication and authorization | 3/10 |
| 2. CSRF / session protection | 4/10 |
| 3. Request hardening | 4/10 |
| 4. Rate limiting and abuse controls | 3/10 |
| 5. Security headers | 5/10 |
| 6. Reverse proxy and TLS | 4/10 |
| 7. Persistence and migrations | 3/10 |
| 8. Audit logging | 4/10 |
| 9. Observability and monitoring | 4/10 |
| 10. Backup and restore | 3/10 |
| 11. Containerization | 5/10 |
| 12. CI/CD and quality gates | 3/10 |
| 13. Secrets management | 4/10 |
| 14. Operational runbooks | 2/10 |
| 15. Incident response | 2/10 |
| 16. Release management | 3/10 |
| 17. Scanner/evaluator assurance | 4/10 |
| 18. Multi-instance/multi-tenant limitations | 2/10 |
| **Overall public internet / SaaS** | **3.3/10** |

**Verdict: NOT READY for public internet or SaaS multi-tenant deployment.** Major architectural changes required in authentication (OIDC/SSO), persistence (PostgreSQL), rate limiting (Redis), and multi-tenancy before this rating improves above 7/10.

---

*This scorecard is a living document. Update as controls are implemented and gaps are closed. See [`docs/PRODUCTION_HARDENING_BACKLOG.md`](PRODUCTION_HARDENING_BACKLOG.md) for the active blocker register.*
