# VulnoraIQ Documentation

This folder contains the operational, security, production-readiness, assurance, OWASP, GenAI, Agentic, and MITRE ATLAS documentation for VulnoraIQ.

> **Current version:** `0.2.0`  
> **Current posture:** self-hosted laptop/server application with controlled internal production-readiness gate passed.  
> **Boundary:** authorised local or internal-server assessment use; not certified VAPT-grade assurance.

## Start here

| Need | Document |
| --- | --- |
| Quick start, standalone launcher, feature overview, maturity statement | [`../README.md`](../README.md) |
| Acceptable use and misuse disclaimer | [`../ACCEPTABLE_USE.md`](../ACCEPTABLE_USE.md) |
| Security policy and vulnerability reporting | [`../SECURITY.md`](../SECURITY.md) |
| Deployment, local launcher, env vars, TLS/reverse proxy, metrics, backups | [`DEPLOYMENT.md`](DEPLOYMENT.md) |
| Day-2 operations, local/server startup, shutdown, and troubleshooting | [`RUNBOOK.md`](RUNBOOK.md) |
| Release gates and RC/final tagging | [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) |
| Release-only Windows/Linux/macOS artifact builds | [`RELEASE_ARTIFACTS.md`](RELEASE_ARTIFACTS.md) |
| Python wheel/source package build and PyPI publishing | [`PYPI_PACKAGE.md`](PYPI_PACKAGE.md) |
| Incident handling | [`INCIDENT_RESPONSE.md`](INCIDENT_RESPONSE.md) |
| Upgrade from `0.0.1.x` to `0.2.0` | [`MIGRATION.md`](MIGRATION.md) |
| Web UI categorized test catalog | [`WEB_UI_TEST_CATALOG.md`](WEB_UI_TEST_CATALOG.md) |
| OWASP AI Testing Guide integration and actual local AI agent setup | [`AI_TESTING_GUIDE_INTEGRATION.md`](AI_TESTING_GUIDE_INTEGRATION.md) |
| OWASP AI Testing Guide full implementation roadmap | [`AI_TESTING_GUIDE_IMPLEMENTATION_PLAN.md`](AI_TESTING_GUIDE_IMPLEMENTATION_PLAN.md) |
| OWASP LLM framework/control mapping implementation roadmap | [`OWASP_LLM_TOP10_MAPPING_IMPLEMENTATION_PLAN.md`](OWASP_LLM_TOP10_MAPPING_IMPLEMENTATION_PLAN.md) |
| Phase-by-phase GenAI Security readiness gate | [`genai/PRODUCTION_READINESS_PLAN.md`](genai/PRODUCTION_READINESS_PLAN.md) |
| Phase-by-phase Agentic Applications readiness gate | [`AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`](AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md) |
| Readiness scoring | [`PRODUCTION_READINESS_SCORECARD.md`](PRODUCTION_READINESS_SCORECARD.md) |
| Hardening backlog and accepted risks | [`PRODUCTION_HARDENING_BACKLOG.md`](PRODUCTION_HARDENING_BACKLOG.md) |
| What scan findings do and do not prove | [`ASSESSMENT_ASSURANCE.md`](ASSESSMENT_ASSURANCE.md) |
| Current implementation status | [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) |

## Production-readiness boundary

VulnoraIQ `0.2.0` may be described as:

> Self-hosted laptop/server AI security testing application with controlled internal production-readiness gate passed.

It must **not** be described as:

- certified VAPT-grade assurance
- a substitute for external penetration testing
- independently validated real-world GenAI detection assurance

## Current control summary

| Area | Status |
| --- | --- |
| Standalone local launcher | Complete: cross-platform launcher files, startup/dependency checks, local browser open, startup panel, and loopback-only stop control |
| Release artifact workflow | Complete: Windows `.zip`, Linux `.tar.gz`, and macOS unsigned `.dmg` packages are built only on published GitHub Releases or manual release-build dispatch |
| Python package workflow | Complete: wheel/source distributions are built on published GitHub Releases or manual dispatch, with TestPyPI/PyPI publish controlled by manual workflow input |
| Auth | Complete: fail-closed token auth for hosted/production mode; trusted reverse-proxy identity mode available |
| Production startup validation | Complete: runtime checks via `webui/production_checks.py` and `scripts/validate_runtime_production_config.py` |
| Web hardening | Complete: CSRF, request-size limits, rate limiting, security headers, structured errors |
| Persistence | Complete: SQLite default with WAL, foreign keys, busy timeout, schema versioning |
| Observability | Complete: `/healthz`, `/readyz`, auth-protected `/metrics`, structured JSON audit logs |
| Backup/restore | Complete: SQLite online backup and restore scripts with validation |
| Container | Complete: non-root Dockerfile, `/data` volume, healthcheck, Docker Compose example |
| CI gates | Complete: Ruff, mypy, pytest, pip check, pip-audit, metadata validation, OWASP/ATLAS mapping validation, GenAI readiness validation, readiness validation, functional acceptance |
| Web UI test catalog | Complete: categorized suites and single-test runnable profiles are visible from the dashboard |
| OWASP AI Testing Guide integration | Complete for current controlled, safe methodology-harness scope with local AI agent target templates; not certified assurance |
| OWASP AI Testing Guide implementation plan | Planned: full 32-test AITG manifest, runtime/evidence modules, pillar suites, WebUI/reporting, and CI validation |
| OWASP LLM framework mapping implementation plan | Planned: normalized framework/control mapping registry with source provenance, confidence, WebUI/report enrichment, and CI validation |

## OWASP, GenAI, Agentic, and MITRE documentation

| Area | Document |
| --- | --- |
| OWASP AI Testing Guide integration | [`AI_TESTING_GUIDE_INTEGRATION.md`](AI_TESTING_GUIDE_INTEGRATION.md) |
| OWASP AI Testing Guide implementation plan | [`AI_TESTING_GUIDE_IMPLEMENTATION_PLAN.md`](AI_TESTING_GUIDE_IMPLEMENTATION_PLAN.md) |
| OWASP LLM framework/control mapping implementation plan | [`OWASP_LLM_TOP10_MAPPING_IMPLEMENTATION_PLAN.md`](OWASP_LLM_TOP10_MAPPING_IMPLEMENTATION_PLAN.md) |
| OWASP LLM 2025 category specs | [`owasp/`](owasp/) |
| OWASP LLM production-readiness plan | [`owasp/PRODUCTION_READINESS_PLAN.md`](owasp/PRODUCTION_READINESS_PLAN.md) |
| OWASP to MITRE ATLAS crosswalk | [`owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`](owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md) |
| GenAI Security implementation plan | [`genai/`](genai/) |
| GenAI Security production-readiness plan | [`genai/PRODUCTION_READINESS_PLAN.md`](genai/PRODUCTION_READINESS_PLAN.md) |
| GenAI Security scenario manifest | [`../benchmarks/fixtures/genai/scenarios.yaml`](../benchmarks/fixtures/genai/scenarios.yaml) |
| GenAI Security readiness validator | [`../scripts/validate_genai_readiness.py`](../scripts/validate_genai_readiness.py) |
| Agentic Applications implementation plan | [`agentic/`](agentic/) |
| Agentic Applications source-doc production-readiness plan | [`agentic/PRODUCTION_READINESS_PLAN.md`](agentic/PRODUCTION_READINESS_PLAN.md) |
| Agentic Applications repo phase gate | [`AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`](AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md) |
| OWASP source document review index | [`owasp-documents/`](owasp-documents/) |
| MITRE ATLAS AI planning matrix | [`MITRE_ATLAS_AI_MATRIX.md`](MITRE_ATLAS_AI_MATRIX.md) |
| MITRE ATLAS mapping notes | [`mitre-atlas-mapping.md`](mitre-atlas-mapping.md) |

The OWASP, GenAI, Agentic, and MITRE documents are complete for the current self-hosted/internal readiness and planning scope. They should not be interpreted as proof that every mapped technique has independently validated real-environment detection coverage.

## Source document review status

The uploaded source PDFs have been reviewed for category extraction and planning alignment:

- `owasp-documents/OWASP-GenAI-COMPASS-RunBook-1.0.pdf` — reviewed for COMPASS/OODA workflow and framework alignment.
- `owasp-documents/OWASP-GenAI-Data-Security-Risks-and-Mitigations-2026-v1.0.pdf` — `DSGAI01–DSGAI21` extracted and mapped. The document narrative references `DSGAI01–DSGAI25`; discrepancy remains tracked.
- `owasp-documents/OWASP-Top-10-for-Agentic-Applications-2026-12.6.pdf` — `ASI01–ASI10` extracted and mapped.
- `owasp-documents/OWASP-Top10-for-Agentic-Applications_AIUC-1-Crosswalk-May26.pdf` — reviewed for Primary/Secondary relevance methodology and strategic gaps.
- `owasp-documents/State-of-Agentic-AI-Security-and-Governance-v2.01.pdf` — reviewed for governance maturity, adoption-tier prioritisation, identity/NHI, AI SBOM/provenance, and runtime governance themes.

Source category names are confirmed for `DSGAI01–DSGAI21` and `ASI01–ASI10`. GenAI Security coverage is now complete for the current controlled-internal scenario-harness scope, backed by safe synthetic scenario manifests, deterministic evaluators, and CI validation; it is still not certified assurance.

## Documentation maintenance rule

When production posture or assessment coverage changes, update these together:

1. `README.md`
2. `SECURITY.md`
3. `docs/README.md`
4. `docs/DEPLOYMENT.md`
5. `docs/IMPLEMENTATION_STATUS.md`
6. `docs/genai/PRODUCTION_READINESS_PLAN.md`
7. `docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`
8. `docs/PRODUCTION_READINESS_SCORECARD.md`
9. `docs/PRODUCTION_HARDENING_BACKLOG.md`
10. `docs/ASSESSMENT_ASSURANCE.md`
11. `docs/owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`
12. `docs/genai/`
13. `docs/agentic/`
14. `docs/owasp-documents/`
15. `CHANGELOG.md`

If a capability is complete only for the current self-hosted/internal scope, source discrepancy, accepted risk, future maturity item, or assurance limitation, mark it clearly in every document that mentions it.
