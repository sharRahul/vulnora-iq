# VulnoraIQ Documentation

This folder documents the current VulnoraIQ `0.2.0` codebase.

> **Current posture:** self-hosted AI security testing application with Desktop Mode for laptop/workstation use and Docker Lab Mode for server, VM, CI, and dev-lab use.  
> **Current WebUI:** React 18 + TypeScript + Vite console served by `webui/hosted_server.py`.  
> **Default network boundary:** local WebUI launchers bind to host loopback at `127.0.0.1:8787`.  
> **Assessment boundary:** findings are structured internal evidence requiring human review. VulnoraIQ is not certified VAPT-grade assurance.

## Current status snapshot

| Area | Status |
| --- | --- |
| Desktop Mode | Phase 1 implemented for source/release-package use: VulnoraIQ starts natively on the host, uses Docker only for sandboxed Agent Lab runtimes, stores reports under `scan-reports/`, and stores Agent Lab projects under `agent-lab/`. |
| Docker Lab | Complete for the current local lab scope. `docker-compose.yml` starts `vulnoraiq-web` and optional `test-runner` on a private Docker network with loopback-only WebUI publishing. |
| Experimental Agent Lab | Implemented as an experimental local-lab workflow at `/agent-lab` for importing real AI-agent projects, configuring model providers, selecting CPU/GPU runtime options, building/running containers, auto-creating targets, and launching authorised scans. |
| Target support | Complete for current approved local/internal scope with HTTP JSON, chat-completions, Ollama generate, RAG query, webhook JSON, and dry-run tool-loop contracts. |
| WebUI | Current supported UI is the React SecOps console in `webui/console/`, built to `webui/static/console/`. A clean start shows no dummy assets, findings, or dashboard data. |
| WebUI backend | Target management, scan launch, SSE progress, finding actions/history, assistant model controls, and Agent Lab APIs are implemented. |
| CLI | `vulnoraiq` supports `targets list`, `targets validate`, `scan`, `reports list`, `jobs list`, and `jobs show`. |
| Security hardening | Auth, trusted proxy mode, CSRF, request limits, rate limiting, security headers, audit logs, metrics, artifact path protection, production startup validation, and loopback-only local publishing. Agent Lab remains experimental because it can build and run local Docker containers. |
| CI | Python matrix checks plus lint, typing, tests, dependency checks, validators, hosted WebUI flow, functional acceptance, supply-chain reports, SBOMs, and image signing workflow. |
| Release/packaging | Release-only platform artifact and Python package workflows are documented; native OS certificate-signed installers and bundled desktop runtime remain future maturity work. |

## Start here

| Need | Document |
| --- | --- |
| Project overview and quick start | [`../README.md`](../README.md) |
| End-to-end user guide | [`USER_GUIDE.md`](USER_GUIDE.md) |
| Manual QA regression test plan | [`MANUAL_TEST_PLAN.md`](MANUAL_TEST_PLAN.md) |
| Prompt for Codex/Claude Code/manual LLM testers | [`LLM_MANUAL_TESTING_PROMPT.md`](LLM_MANUAL_TESTING_PROMPT.md) |
| Desktop vs Docker Lab run modes | [`RUN_MODES_DESKTOP_AND_DOCKER_LAB.md`](RUN_MODES_DESKTOP_AND_DOCKER_LAB.md) |
| Experimental Agent Lab workflow | [`AGENT_LAB.md`](AGENT_LAB.md) |
| Experimental Agent Lab implementation plan | [`AGENT_LAB_PLAN.md`](AGENT_LAB_PLAN.md) |
| Docker Lab startup and troubleshooting | [`DOCKER_TESTING.md`](DOCKER_TESTING.md) |
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
| Supply-chain pipeline | [`SUPPLY_CHAIN_PIPELINE.md`](SUPPLY_CHAIN_PIPELINE.md) |
| Python package publishing | [`PYPI_PACKAGE.md`](PYPI_PACKAGE.md) |
| Migration from legacy versions | [`MIGRATION.md`](MIGRATION.md) |
| Current implementation status | [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) |
| Production scorecard | [`PRODUCTION_READINESS_SCORECARD.md`](PRODUCTION_READINESS_SCORECARD.md) |
| Hardening backlog | [`PRODUCTION_HARDENING_BACKLOG.md`](PRODUCTION_HARDENING_BACKLOG.md) |
| Assessment assurance limitations | [`ASSESSMENT_ASSURANCE.md`](ASSESSMENT_ASSURANCE.md) |
| Future OIDC/JWT auth plan | [`future-plans/OIDC_JWT_AUTH_PLAN.md`](future-plans/OIDC_JWT_AUTH_PLAN.md) |

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

## WebUI and future planning

| Document | Current meaning |
| --- | --- |
| [`WEBUI_LAYOUT_PLAN.md`](WEBUI_LAYOUT_PLAN.md) | Future layout direction. Parts are implemented by the React SecOps console, target-management workspace, and experimental Agent Lab. |
| [`WEBUI_RELEASE_HARDENING.md`](WEBUI_RELEASE_HARDENING.md) | Release checks for package-data static assets, browser tests, and production WebUI hardening. |
| [`future-plans/OIDC_JWT_AUTH_PLAN.md`](future-plans/OIDC_JWT_AUTH_PLAN.md) | Future enterprise identity plan. OIDC/JWT is not required for current local single-user use. |

## Maintenance rule

When code changes alter deployment posture, target support, WebUI behaviour, release gates, or assessment claims, update these together:

1. `README.md`
2. `docs/README.md`
3. `docs/USER_GUIDE.md`
4. `docs/MANUAL_TEST_PLAN.md`
5. `docs/LLM_MANUAL_TESTING_PROMPT.md`
6. `docs/IMPLEMENTATION_STATUS.md`
7. `docs/DOCKER_TESTING.md`
8. `docs/WEBUI_GUIDE.md`
9. `docs/CLI_GUIDE.md`
10. `docs/SAFETY_MODEL.md`
11. `docs/TARGET_CONFIGURATION.md`
12. `docs/PRODUCTION_READINESS_SCORECARD.md`
13. `docs/PRODUCTION_HARDENING_BACKLOG.md`
14. `docs/ASSESSMENT_ASSURANCE.md`
15. `SECURITY.md`
16. `CHANGELOG.md`

If a capability is complete only for the current local/internal scope, mark that scope clearly. Do not convert framework coverage, synthetic harness coverage, or successful local scans into certified assurance claims.
