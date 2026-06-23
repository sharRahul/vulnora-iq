# Implementation Status

This document separates current complete capability from future assurance and maturity items so users can understand what is ready today.

> **Current maturity:** VulnoraIQ version `0.2.0` has passed the **controlled internal production-readiness gate** for self-hosted laptop/server use, with security hardening, SQLite persistence, auth, CSRF, rate limiting, audit logging, metrics, backup/restore tooling, container support, production startup validation, completed OWASP LLM readiness coverage for the current safe local/internal scope, completed Agentic Applications readiness gates, and completed GenAI Security scenario-harness readiness for `DSGAI01–DSGAI21`.

> **Important limitation:** OWASP LLM 2025, GenAI Security, Agentic Applications, and MITRE ATLAS mappings are framework evidence and planning/validation controls. They are not the same as independently validated assurance. Treat output as development and internal assessment evidence requiring human review.

## Seven-phase implementation status

| Phase | Status | Completed implementation |
| --- | --- | --- |
| Phase 1 — OWASP depth | Complete for current scope | `docs/owasp/` contains implementation specs for all 10 OWASP LLM 2025 categories. |
| Phase 2 — Safe demo fixtures | Complete for current scope | `examples/local_demo_targets/owasp_fixture_targets.py` models local good/bad control behaviour for all 10 categories. |
| Phase 3 — Stronger evaluators | Complete for current scope | `core/evaluators.py` adds deterministic local evaluators for text checks, schema checks, source access, provenance, approval, citations, action boundaries, resource limits, and manual review. |
| Phase 4 — Contract-tested adapters | Complete for current scope | `config/target_contracts.yaml` and `integrations/contract_validation.py` validate configured target adapter shapes before approved testing. |
| Phase 5 — Web UI hardening | Complete for self-hosted production scope | `webui/hosted_server.py`, `webui/auth.py`, `webui/persistent_jobs.py`, and `webui/production_checks.py` provide the hardened Web UI with env-token auth, trusted proxy identity mode, CSRF, rate limiting, security headers, proxy trust, audit logging, metrics, request IDs, concurrency limits, and startup validation. |
| Phase 6 — Report quality and presentation | Complete for current scope | Report generation includes structured evidence; `reports/html_export_package.py` builds a branded export bundle; `docs/assets/vulnoraiq-webui-home.png` provides a README Web UI home screen image. |
| Phase 7 — Release gates | Complete for self-hosted production scope | Package metadata, GenAI readiness, OWASP/ATLAS mapping, production readiness, runtime config, backup/restore, Docker smoke tooling, and CI gates validate package, runtime, docs, readiness, and functional acceptance. |

## GenAI Security Production Readiness Plan

| Scope | Status | Evidence |
| --- | --- | --- |
| Controlled internal GenAI Security readiness for `DSGAI01–DSGAI21` | Complete for current scope | `docs/genai/PRODUCTION_READINESS_PLAN.md`, `benchmarks/fixtures/genai/scenarios.yaml`, `core/genai_evaluators.py`, `scripts/validate_genai_readiness.py`, `tests/test_genai_readiness_validation.py` |
| Source discrepancy `DSGAI22–DSGAI25` | Tracked / map later | Preserved in `benchmarks/fixtures/genai/scenarios.yaml` metadata. |
| Stronger assurance validation | Future maturity item | Requires approved environment validation, evidence review, and independent assessment before stronger assurance claims. |

## Agentic Applications Production Readiness Plan

| Scope | Status | Evidence |
| --- | --- | --- |
| Self-hosted controlled internal deployment gates | Complete | `docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`, `scripts/validate_owasp_atlas_mappings.py`, `.github/workflows/ci.yml`, `.github/workflows/python-ci.yml` |
| Independent assurance validation | Future maturity item | Tracked through the scorecard, assurance documentation, and hardening backlog. |

## Current complete capability

| Area | Status | Notes |
| --- | --- | --- |
| Python package scaffold | Complete | VulnoraIQ version `0.2.0` installs as a Python package with CLI entry points. |
| Functional acceptance runner | Complete | `scripts/run_functional_test.py` runs a safe demo/baseline assessment, validates outputs, and refreshes the dashboard example PNG. |
| Production readiness gate | Complete for self-hosted production scope | `scripts/validate_production_testing_readiness.py` validates production controls and documentation guardrails. |
| Production runtime config validation | Complete for self-hosted production scope | `scripts/validate_runtime_production_config.py` validates runtime environment before startup. |
| GenAI Security readiness plan | Complete for current scope | `DSGAI01–DSGAI21` safe synthetic scenario coverage, deterministic evaluators, validator, tests, package metadata integration, and CI workflow gates. |
| Agentic production readiness plan | Complete for self-hosted internal deployment | Agentic readiness gates are complete for the intended local/internal-server application model. |
| Web UI home screen image | Complete | `docs/assets/vulnoraiq-webui-home.png` is a real captured Web UI home screen screenshot referenced in `README.md`. |
| Modern Web UI | Complete for self-hosted production scope | `webui/hosted_server.py` — hardened HTTP server with auth, CSRF, rate limiting, security headers, proxy trust, audit logging, metrics, request IDs, concurrency limits, and structured error handling. |
| Authentication | Complete for self-hosted production scope | `webui/auth.py` — env-driven token auth with hmac constant-time comparison, production-mode validation, trusted reverse-proxy identity headers, role-based access control. |
| CSRF protection | Complete for self-hosted production scope | Per-session CSRF tokens with configurable TTL, periodic cleanup, validated on state-changing requests. |
| Rate limiting | Complete for self-hosted production scope | IP-based in-memory rate limiting with configurable window/max and periodic cleanup. Use reverse-proxy controls for internal server deployments that need centralised network controls. |
| Security headers | Complete for self-hosted production scope | CSP, HSTS conditional behaviour, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy on every response. |
| Proxy IP trust | Complete for self-hosted production scope | `X-Forwarded-For` and trusted proxy identity are trusted only from configured CIDRs. |
| Audit logging | Complete for self-hosted production scope | Structured JSON-line audit with request IDs, no token/secret/request-body leakage. |
| Prometheus metrics | Complete for self-hosted production scope | `/metrics` endpoint with request/scan/auth counters, protected by default. |
| Job persistence | Complete for self-hosted production scope | SQLite default with WAL mode, schema versioning, foreign keys, and busy timeout. JSON store is legacy/dev only. |
| Backup and restore | Complete for self-hosted production scope | `scripts/backup_sqlite_store.py` and `scripts/restore_sqlite_store.py` use the SQLite online backup API, validation, compression, and retention. |
| Container deployment | Complete for self-hosted production scope | Dockerfile with non-root user, `/data` volume, healthcheck; `docker-compose.yml` with production env example. |
| Concurrency limits | Complete for self-hosted production scope | Configurable max concurrent scans and queue limit, with audit of rejected requests. |
| Scan artifact security | Complete for self-hosted production scope | Path protection, allowlist-based artifact lookup, audit logging, proper Content-Disposition. |
| Runbook and incident response | Complete for self-hosted production scope | `docs/RUNBOOK.md`, `docs/INCIDENT_RESPONSE.md`, `docs/RELEASE_CHECKLIST.md`. |
| Demo target | Complete | The default `demo` target uses an in-memory echo client and requires no external API keys. |
| Local demo targets | Complete for current scope | Safe HTTP JSON, control-gap, and OWASP good/bad fixture targets for local demonstration and tests. |
| Configured target adapters | Complete for current scope | Chat-completions-compatible, Ollama-style generate, webhook JSON, and HTTP JSON endpoint shapes. |
| Profiles | Complete for current scope | `baseline`, `rag`, `agent`, and `full` profiles are defined and validated by smoke/functional flows. |
| Scanner | Complete for current scope | Scanner loads config, runs profile modules, scores findings, evaluates policy, and creates evidence. Findings require human review. |
| OWASP LLM 2025 oracle coverage | Complete for current scope | Safe oracle coverage exists for all 10 OWASP LLM 2025 categories. |
| GenAI Security coverage | Complete for current scope | Safe synthetic `DSGAI01–DSGAI21` manifest, deterministic evaluator suite, CI validator, and source discrepancy tracking. |
| MITRE ATLAS AI matrix | Complete for current scope | Planning matrix with source-driven generation and unmapped backlog preservation. |
| Package metadata validation | Complete for self-hosted production scope | Validates package name, version, CLI entries, README maturity warnings, OWASP docs, MITRE ATLAS doc, third-party notices, functional test assets, evaluators, fixtures, OWASP/ATLAS metadata, and GenAI readiness assets before release. |
| OWASP/ATLAS mapping metadata validation | Complete for self-hosted production scope | `scripts/validate_owasp_atlas_mappings.py` and CI validate required mapping metadata for active oracles/checks. |
| GenAI readiness validation | Complete for self-hosted production scope | `scripts/validate_genai_readiness.py` and CI validate GenAI scenario manifests, evidence fields, fixture coverage, docs, and source discrepancy tracking. |
| CI | Complete for self-hosted production scope | GitHub Actions across Python 3.10/3.11/3.12; Ruff, mypy, pytest, pip check, pip-audit, metadata validation, OWASP/ATLAS mapping validation, GenAI readiness validation, production readiness validation, demo scan, functional acceptance readiness path. |

## Current safe usage

Run the Web UI in production mode:

```bash
VULNORAIQ_ENV=production \
VULNORAIQ_AUTH_ENABLED=true \
VULNORAIQ_ADMIN_TOKEN="your-strong-token-min-20-chars" \
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Validate production and assessment readiness:

```bash
python scripts/validate_runtime_production_config.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py
python scripts/validate_production_testing_readiness.py \
  --run-functional \
  --output-dir reports/output/production-readiness
```

For any configured target outside demo mode:

1. Confirm the target is owned by you or explicitly approved for assessment.
2. Replace the placeholder endpoint in `config/targets.yaml`.
3. Validate target contracts before testing.
4. Set any required token environment variable.
5. Run with the CLI authorisation flag or tick the Web UI authorisation confirmation.
6. Treat results as framework evidence requiring human review.
7. Store reports securely and review evidence before sharing.

## Implementation roadmap status

All production hardening blockers PRD-001 through PRD-012 are closed for self-hosted internal deployment. The OWASP LLM 2025 safe local/internal readiness scope is complete for all 10 categories. The Agentic Applications Production Readiness Plan is complete for the intended laptop/server application model. The GenAI Security Production Readiness Plan is complete for `DSGAI01–DSGAI21` controlled internal readiness.

The next phases should focus on:

- Scanner/evaluator depth: deeper OWASP and GenAI check logic, evaluator thresholds, fixture realism, and approved environment validation.
- Packaged laptop/server installation paths and smoother local startup/shutdown guidance.
- Target adapter templates for AI agents, LLM APIs, RAG systems, and local model servers.
- Report language and assurance validation for stronger claims.

Scanner and evaluator assurance limitations are documented in [`docs/ASSESSMENT_ASSURANCE.md`](ASSESSMENT_ASSURANCE.md).

## Documentation rule

README, `SECURITY.md`, and all top-level docs must remain aligned. If a capability is complete only for the current self-hosted/internal scope, source discrepancy, accepted risk, future maturity item, or assurance limitation, mark that clearly everywhere it appears.
