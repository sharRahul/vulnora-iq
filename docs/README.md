# VulnoraIQ Documentation

This folder documents the current VulnoraIQ `0.2.0` codebase.

> **Current posture:** Docker-first, self-hosted AI security testing lab for authorised local or internal-server assessment.  
> **Current WebUI:** React 18 + TypeScript + Vite console served by `webui/hosted_server.py`; the legacy static console has been removed.  
> **Assessment boundary:** findings are structured internal evidence requiring human review. VulnoraIQ is not certified VAPT-grade assurance.

## Current status snapshot

| Area | Status |
| --- | --- |
| Docker lab | Complete for current safe local AI-agent/RAG/tool-loop testing scope. `docker-compose.yml` starts `vulnoraiq-web`, `local-mock-agent`, and optional `test-runner` on a private Docker network. |
| Real target support | Complete for current authorised local/internal scope. Target adapters support HTTP JSON, chat-completions, Ollama generate, RAG query, webhook JSON, and dry-run tool-loop contracts. |
| Target safety | Complete for current scope. Non-demo targets require authorisation, safety profiles, rate/time/size bounds, host allowlists, and redaction before evidence persistence. |
| WebUI | Current supported UI is the React SecOps console in `webui/console/`, built to `webui/static/console/`. |
| WebUI target workspace | Current code includes target search/filtering, readiness metrics, health/status pills, safety checklist, target save/delete, target validation, scan launch, and recent job refresh through backend APIs. |
| CLI | `vulnoraiq` supports `targets list`, `targets validate`, `scan`, `reports list`, `jobs list`, and `jobs show`. |
| Persistence | SQLite job store with WAL, foreign keys, busy timeout, and schema versioning. |
| Security hardening | Auth, trusted proxy mode, CSRF, request limits, rate limiting, security headers, audit logs, metrics, artifact path protection, and production startup validation. |
| CI | Python 3.10/3.11/3.12 checks plus lint, typing, tests, dependency checks/audit, metadata validation, OWASP/ATLAS validation, GenAI validation, production-readiness validation, hosted WebUI Playwright flow, demo scan, and functional acceptance path. |
| Release/packaging | Release-only platform artifact and Python package workflows are documented; signed/native installers remain future maturity work. |

## Start here

| Need | Document |
| --- | --- |
| Project overview and quick start | [`../README.md`](../README.md) |
| Docker-first lab startup and troubleshooting | [`DOCKER_TESTING.md`](DOCKER_TESTING.md) |
| Safety model and authorisation rules | [`SAFETY_MODEL.md`](SAFETY_MODEL.md) |
| Target configuration and runtime target rules | [`TARGET_CONFIGURATION.md`](TARGET_CONFIGURATION.md) |
| WebUI operator guide | [`WEBUI_GUIDE.md`](WEBUI_GUIDE.md) |
| WebUI categorized test catalogue | [`WEB_UI_TEST_CATALOG.md`](WEB_UI_TEST_CATALOG.md) |
| CLI usage | [`CLI_GUIDE.md`](CLI_GUIDE.md) |
| AI-agent testing flow | [`AI_AGENT_TESTING.md`](AI_AGENT_TESTING.md) |
| Deployment guide | [`DEPLOYMENT.md`](DEPLOYMENT.md) |
| Operations runbook | [`RUNBOOK.md`](RUNBOOK.md) |
| Incident response | [`INCIDENT_RESPONSE.md`](INCIDENT_RESPONSE.md) |
| Release checklist | [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) |
| Release artifacts | [`RELEASE_ARTIFACTS.md`](RELEASE_ARTIFACTS.md) |
| Python package publishing | [`PYPI_PACKAGE.md`](PYPI_PACKAGE.md) |
| Migration from legacy versions | [`MIGRATION.md`](MIGRATION.md) |
| Current implementation status | [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) |
| Production scorecard | [`PRODUCTION_READINESS_SCORECARD.md`](PRODUCTION_READINESS_SCORECARD.md) |
| Hardening backlog | [`PRODUCTION_HARDENING_BACKLOG.md`](PRODUCTION_HARDENING_BACKLOG.md) |
| Assessment assurance limitations | [`ASSESSMENT_ASSURANCE.md`](ASSESSMENT_ASSURANCE.md) |

## Security-framework documentation

| Area | Document |
| --- | --- |
| OWASP AI Testing Guide current integration | [`AI_TESTING_GUIDE_INTEGRATION.md`](AI_TESTING_GUIDE_INTEGRATION.md) |
| OWASP AI Testing Guide roadmap | [`AI_TESTING_GUIDE_IMPLEMENTATION_PLAN.md`](AI_TESTING_GUIDE_IMPLEMENTATION_PLAN.md) |
| OWASP LLM framework/control mapping roadmap | [`OWASP_LLM_TOP10_MAPPING_IMPLEMENTATION_PLAN.md`](OWASP_LLM_TOP10_MAPPING_IMPLEMENTATION_PLAN.md) |
| OWASP LLM 2025 category specs | [`owasp/`](owasp/) |
| OWASP LLM production-readiness plan | [`owasp/PRODUCTION_READINESS_PLAN.md`](owasp/PRODUCTION_READINESS_PLAN.md) |
| OWASP to MITRE ATLAS crosswalk | [`owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`](owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md) |
| GenAI Security production-readiness plan | [`genai/PRODUCTION_READINESS_PLAN.md`](genai/PRODUCTION_READINESS_PLAN.md) |
| Agentic Applications repo-level readiness | [`AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`](AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md) |
| Agentic source-doc readiness plan | [`agentic/PRODUCTION_READINESS_PLAN.md`](agentic/PRODUCTION_READINESS_PLAN.md) |
| MITRE ATLAS matrix | [`MITRE_ATLAS_AI_MATRIX.md`](MITRE_ATLAS_AI_MATRIX.md) |
| MITRE ATLAS mapping notes | [`mitre-atlas-mapping.md`](mitre-atlas-mapping.md) |
| Source document review index | [`owasp-documents/`](owasp-documents/) |

## WebUI planning and history

| Document | Current meaning |
| --- | --- |
| [`WEBUI_VALIDATED_IMPLEMENTATION_PLAN.md`](WEBUI_VALIDATED_IMPLEMENTATION_PLAN.md) | Historical validated plan for the WebUI improvement series; the original no-build/static direction has now been superseded by the React console. |
| [`WEBUI_IMPROVEMENT_SERIES_SUMMARY.md`](WEBUI_IMPROVEMENT_SERIES_SUMMARY.md) | Historical summary of PRs #29-#44 plus later WebUI changes. |
| [`WEBUI_LAYOUT_PLAN.md`](WEBUI_LAYOUT_PLAN.md) | Future layout direction. Parts are now implemented by the React SecOps console and target-management workspace. |
| [`WEBUI_RELEASE_HARDENING.md`](WEBUI_RELEASE_HARDENING.md) | Release checks for package-data static assets, browser tests, and production WebUI hardening. |
| [`DOCKER_RUNTIME_DEPENDENCIES.md`](DOCKER_RUNTIME_DEPENDENCIES.md) | Historical Docker-optional dependency notes. Current real AI-agent lab usage is Docker-first. |

## Maintenance rule

When code changes alter deployment posture, target support, WebUI behaviour, release gates, or assessment claims, update these together:

1. `README.md`
2. `docs/README.md`
3. `docs/IMPLEMENTATION_STATUS.md`
4. `docs/DOCKER_TESTING.md`
5. `docs/WEBUI_GUIDE.md`
6. `docs/CLI_GUIDE.md`
7. `docs/SAFETY_MODEL.md`
8. `docs/TARGET_CONFIGURATION.md`
9. `docs/PRODUCTION_READINESS_SCORECARD.md`
10. `docs/PRODUCTION_HARDENING_BACKLOG.md`
11. `docs/ASSESSMENT_ASSURANCE.md`
12. `SECURITY.md`
13. `CHANGELOG.md`

If a capability is complete only for the current local/internal scope, mark that scope clearly. Do not convert framework coverage, synthetic harness coverage, or successful local scans into certified assurance claims.
