# Production readiness scorecard

**Assessment date:** 2026-06-24  
**Scope:** VulnoraIQ `0.2.0` Docker-first/self-hosted laptop-server deployment for authorised LLM, RAG, tool-using, AI-agent, and GenAI data-security assessments.  
**Rating scale:** 0-10, where 10 means fully hardened for the stated scope.

## Verdict

VulnoraIQ is complete for the current **self-hosted internal deployment scope** when deployed with the documented Docker lab or production-mode server controls: explicit authorisation, safety profiles, auth for shared deployments, SQLite persistence, audit logs, metrics, reports/evidence path controls, and CI validation.

The current codebase is no longer demo/static-WebUI-first. It is now:

- Docker-first for real local AI-agent/RAG/tool-loop lab testing;
- React-console-first for the WebUI;
- backend-wired for target inventory, runtime target save/delete, target validation, scan launch, and recent job refresh;
- still limited to framework evidence requiring human review.

VulnoraIQ does **not** claim certified VAPT-grade assurance or independent real-world GenAI detection assurance.

## Scorecard

| Area | Score | Current evidence | Remaining maturity item | Blocking? |
| --- | ---: | --- | --- | --- |
| Authentication and authorisation | 9/10 | `webui/auth.py`, production checks, token/trusted-proxy modes, role controls. | Direct OIDC/JWT, token revocation. | No |
| CSRF/session protection | 9/10 | Hosted server CSRF validation and tests. | Shared CSRF state for multi-instance deployments. | No |
| Request hardening | 9/10 | Request-size limits, malformed JSON handling, structured errors. | Formal schema/model validation. | No |
| Rate limiting | 8/10 | IP-based rate limits and scan concurrency/queue controls. | Shared per-user limiter. | No |
| Security headers | 9/10 | CSP, HSTS conditional behaviour, frame/content/referrer/permissions headers. | CSP reporting and broader browser isolation policy. | No |
| Reverse proxy/TLS | 8/10 | Deployment/runbook guidance and trusted proxy CIDR checks. | Environment-specific TLS validation. | No |
| Persistence | 9/10 | SQLite WAL, foreign keys, busy timeout, schema versioning. | HA database backend or migration framework. | No |
| Audit logging | 9/10 | Structured JSON audit logs with request correlation. | SIEM schema/rule pack. | No |
| Observability | 9/10 | `/healthz`, `/readyz`, auth-protected `/metrics`, Docker healthcheck. | Alert rules/SLOs/tracing. | No |
| Backup/restore | 9/10 | SQLite online backup/restore scripts. | Automated scheduler and backup-age metrics. | No |
| Containerisation | 9/10 | Dockerfile, Compose, non-root app, private lab network, mock agent. | Image signing/scanning. | No |
| Real target testing | 8/10 | Target adapters, Docker target config, runtime target APIs, validation, safety profile. | More target templates and approved-environment validation. | No |
| WebUI | 8/10 | React console, target workspace, backend target/scan API wiring, built package data. | SSE progress, finding mutation APIs, assistant backend. | No |
| CI/CD and quality gates | 9/10 | Python matrix, lint, mypy, pytest, pip check/audit, validation scripts, Playwright hosted flow, demo/functional acceptance. | SAST/DAST/image scan gates. | No |
| Secrets management | 8/10 | Env-backed tokens/secrets and redaction requirements. | Vault/cloud secrets-manager integration. | No |
| Operational docs | 8/10 | Deployment, runbook, incident response, release, migration docs. | Org-specific contacts and alert thresholds. | No |
| Scanner/evaluator assurance | 7/10 | OWASP/GenAI/Agentic/MITRE coverage, safe fixtures, validators. | Independent validation against approved real environments. | No for current scope |
| GenAI Security harness | 8/10 | `DSGAI01–DSGAI21`, 84 scenario cases, deterministic evaluators, evidence contract, CI. | Provider/data inventory connectors and real-environment validation. | No |
| Release packaging | 7/10 | Release-only platform artifacts and Python package publishing docs. | Signed/notarised installers and distribution channels. | No |

**Overall self-hosted internal score:** **8.5/10**

The blocker register can remain closed for current self-hosted/internal scope, but the numeric score is not 10/10 because it includes future maturity items such as direct OIDC, signed installers, image scanning, SAST/DAST, SIEM integration, multi-instance state, approved-environment GenAI validation, and independent assurance.

## Allowed release wording

Use:

> Self-hosted laptop/server AI security testing application with controlled internal production-readiness gate passed.

Allowed GenAI-specific wording:

> GenAI Security readiness gate completed for controlled internal assessment use with safe synthetic `DSGAI01–DSGAI21` scenario coverage.

Allowed Docker/WebUI wording:

> Docker-first local AI-agent testing lab with a React SecOps console, backend target-management APIs, deterministic mock-agent targets, and explicit authorisation gates.

## Disallowed wording

Do not describe VulnoraIQ as:

- certified VAPT-grade;
- independently validated real-world GenAI detection assurance;
- safe to use against systems without written authorisation;
- a replacement for independent penetration testing;
- horizontally scalable production SaaS.
