# Production hardening backlog

Status: live blocker and maturity register  
Current operational readiness: 10/10 for the current self-hosted internal deployment scope  
Target: Docker-first laptop/workstation/internal-server assessment lab.

## Current verdict

VulnoraIQ is complete for the current self-hosted internal deployment scope with Docker-first lab startup, authorised target adapters, React WebUI target management, SQLite persistence, auth/security hardening, audit/metrics, OWASP/GenAI/Agentic/MITRE governance, WebUI assistant backend controls, expanded target templates, on-demand signed release packages, supply-chain workflow, and CI gates.

Self-hosted internal deployment readiness is attested by this blocker register, the production-readiness scorecard, the implementation status, the assessment assurance boundary, the release gates, the supply-chain workflow, and the CI validators.

The current release claim remains:

> Self-hosted laptop/server AI security testing application with controlled internal production-readiness gate passed.

This does not mean certified VAPT-grade assurance or independently validated real-world GenAI detection coverage.

## Closed blockers

| ID | Area | Required outcome | Current evidence |
| --- | --- | --- | --- |
| PRD-001 | Logging | Structured application and audit logging. | `webui/hosted_server.py`, audit tests. |
| PRD-002 | Web server | Documented self-hosted deployment path. | `docs/DEPLOYMENT.md`, `docs/RUNBOOK.md`. |
| PRD-003 | Web UI consolidation | One supported web runtime. | Legacy static console removed; React bundle served from `webui/static/console/`. |
| PRD-004 | Authentication | Production auth fails closed without strong config. | `webui/auth.py`, production checks. |
| PRD-005 | Web hardening | CSRF, rate limiting, security headers, request limits. | Hosted server and tests. |
| PRD-006 | Runtime configuration | Environment-variable overrides for runtime paths. | Hosted server, Docker Compose, deployment docs. |
| PRD-007 | Persistence | SQLite job persistence and migration/version handling. | `webui/persistent_jobs.py`, SQLite tests. |
| PRD-008 | Containerisation | Deployable container baseline. | `Dockerfile`, `docker-compose.yml`, mock-agent image, healthchecks. |
| PRD-009 | Quality gates | Ruff, mypy, pytest, dependency gates, CI. | `.github/workflows/ci.yml`, validation scripts. |
| PRD-010 | Observability | Health, readiness, metrics endpoints. | `/healthz`, `/readyz`, `/metrics`, Docker healthcheck. |
| PRD-011 | OWASP/MITRE mapping governance | Required mapping metadata is checked in CI. | `scripts/validate_owasp_atlas_mappings.py`. |
| PRD-012 | GenAI readiness governance | GenAI scenario/docs/evidence drift is checked in CI. | `scripts/validate_genai_readiness.py`, scenario harness. |
| PRD-013 | Local launcher | Laptop/workstation launcher path. | `launch-vulnoraiq-webui.*`, launcher script. |
| PRD-014 | Target testing | Authorised target adapters and validation. | Target adapters, `config/targets*.yaml`, runtime target APIs. |
| PRD-015 | Docker-first AI-agent lab | Local deterministic AI-agent/RAG/tool-loop test lab. | Docker Compose, `docker/mock-agent/`, `scripts/docker_smoke_test.py`. |
| PRD-016 | React WebUI target management | Operator target workspace for real target testing. | React target manager with backend target/scan API wiring. |
| PRD-017 | Supply-chain workflow | Container image reports, SBOM outputs, and keyless image signing. | `.github/workflows/security-supply-chain.yml`, `docs/SUPPLY_CHAIN_PIPELINE.md`, workflow regression tests. |

## Current maturity backlog

| Area | Future maturity item | Priority |
| --- | --- | --- |
| Full OWASP AI Testing Guide | Extend beyond safe synthetic coverage with reviewer-approved real-target evidence modules and reporting. | High |
| Real-environment GenAI validation | Continue validating GenAI harness against approved internal environments, provider configs, vector stores, telemetry, and governance workflows. | High |
| Enterprise identity | Add direct OIDC/JWT support beyond trusted reverse-proxy identity. | Medium |
| Native installer certificates | Add Authenticode-signed Windows `.exe/.msi`, notarised macOS `.pkg/.app`, and Linux distro packages after certificate/secrets decisions. | Medium |
| SIEM integration | Add audit schema, alert rules, and integration guidance. | Medium |
| Multi-instance operation | Add shared state for CSRF/rate limits and a server database option. | Low |
| Independent review | External review of the framework, WebUI, scanner, and report claims. | High |

## Production claim rule

Allowed wording must stay scoped to self-hosted/internal readiness. Stronger claims should wait for the future maturity items above.

## High-priority items completed on 2026-06-24

The previous high-priority backlog entries for WebUI live progress, WebUI finding actions, full AITG coverage, controlled real-environment GenAI validation support, and independent assurance workflow support have implementation, tests, and CI validators. Remaining maturity work includes external reviewer execution, SIEM/SOAR integrations, native installer certificate signing, and stronger third-party validation.

## Medium-priority items completed on 2026-06-24

The previous medium-priority backlog entries for the WebUI assistant backend/model controls and target template expansion are implemented with backend API wiring, React model controls, CSRF-protected requests, expanded provider/RAG/local/agent/gateway templates, and validator coverage.

## Release-packaging item completed on 2026-06-24

The previous packaging backlog entry for on-demand signed release packages is implemented with manual GitHub Actions dispatch, platform packages, self-bootstrapping double-click launchers, SHA256 checksums, GitHub artifact attestations, and optional GPG detached signatures. Native OS certificate-signed installers remain a separate future maturity item.

## Supply-chain workflow items completed on 2026-06-24

The previous container supply-chain and application pipeline backlog entries are implemented with filesystem/image reports, SARIF outputs, SPDX/CycloneDX SBOMs, optional strict manual gates, GHCR publishing, Cosign keyless image signing, signature verification evidence, GitHub job summaries, and downloadable workflow artifacts.
