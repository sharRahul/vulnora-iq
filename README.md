# VulnoraIQ

**VulnoraIQ** is an AI security assessment framework for authorised testing of **LLM applications, RAG pipelines, AI agents, tool-using systems, GenAI data flows, vector stores, providers, telemetry, reports, and orchestration layers**.

It helps security teams run internal AI-application assessments, collect evidence, score findings, generate reports, and track OWASP LLM / OWASP GenAI / Agentic / MITRE ATLAS coverage as the framework matures.

---

## Current status

**Version:** `0.2.0`  
**Deployment posture:** controlled internal enterprise production-readiness gate passed  
**Assessment assurance:** starter/framework evidence, not certified VAPT-grade assurance

| Area | Status |
| --- | --- |
| Local demo / development | Supported |
| Controlled internal enterprise deployment | Supported with production configuration validation |
| OWASP LLM coverage | Working starter |
| GenAI Security readiness | Working starter with safe synthetic `DSGAI01–DSGAI21` scenarios and CI validation |
| Agentic Applications readiness | Complete for controlled internal phase gates |
| Public internet-facing deployment | Not recommended without extra controls |
| Multi-tenant SaaS hosting | Not supported |
| Certified VAPT-grade security assurance | Not claimed |

`0.2.0` may be described as:

> **Controlled internal enterprise production-readiness gate passed.**

It must **not** be described as public SaaS ready, multi-tenant ready, unsupervised internet-facing ready, certified VAPT-grade assurance, or not ready for real-world VAPT replacement claims.

For details, see:

- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — deployment and production configuration
- [`docs/PRODUCTION_READINESS_SCORECARD.md`](docs/PRODUCTION_READINESS_SCORECARD.md) — scored readiness
- [`docs/PRODUCTION_HARDENING_BACKLOG.md`](docs/PRODUCTION_HARDENING_BACKLOG.md) — remaining gaps and accepted risks
- [`docs/genai/PRODUCTION_READINESS_PLAN.md`](docs/genai/PRODUCTION_READINESS_PLAN.md) — GenAI Security readiness plan
- [`docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`](docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md) — Agentic Applications readiness plan
- [`docs/ASSESSMENT_ASSURANCE.md`](docs/ASSESSMENT_ASSURANCE.md) — scanner/evaluator limitations
- [`SECURITY.md`](SECURITY.md) — security policy and responsible-use requirements

---

## Responsible-use boundary

Use VulnoraIQ only against systems you own or are explicitly authorised to assess.

The default `demo` target is safe and local. Configured non-demo targets require an explicit authorisation flag. Do not run assessments against third-party systems without written permission.

---

## Dashboard example

The dashboard below is generated from the safe local functional test path and shows the intended reporting workflow.

![VulnoraIQ dashboard example](docs/assets/vulnoraiq-dashboard-example.svg)

---

## What VulnoraIQ provides today

### Assessment framework

- Safe local demo target with no external API keys.
- Baseline, RAG, agent, and full assessment profiles.
- Configured target adapters for HTTP JSON, chat-completions-compatible APIs, Ollama-style generate APIs, and webhook JSON shapes.
- Explicit authorisation gate for non-demo targets.
- Scanner, scoring, result model, policy evaluation, scoped policy exceptions, and approval evidence validation.
- Markdown, JSON, SARIF-style, Markdown dashboard, HTML dashboard, diff, trend, benchmark, and branded HTML export outputs.

### OWASP / GenAI / Agentic / MITRE coverage

- OWASP LLM Top 10 2025 implementation specs for all 10 categories in [`docs/owasp/`](docs/owasp/).
- Safe starter oracle coverage for all 10 OWASP LLM 2025 categories.
- GenAI Security working-starter scenario manifest for `DSGAI01–DSGAI21` in [`benchmarks/fixtures/genai/scenarios.yaml`](benchmarks/fixtures/genai/scenarios.yaml).
- GenAI deterministic evaluator primitives in [`core/genai_evaluators.py`](core/genai_evaluators.py).
- GenAI readiness gate in [`scripts/validate_genai_readiness.py`](scripts/validate_genai_readiness.py).
- Agentic Applications readiness phase gate in [`docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`](docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md).
- MITRE ATLAS AI planning matrix in [`docs/MITRE_ATLAS_AI_MATRIX.md`](docs/MITRE_ATLAS_AI_MATRIX.md).
- Source-driven ATLAS matrix generation with explicit `Unmapped / map later` backlog preservation.
- MITRE ATLAS-derived documentation tracked in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

### Production hardening for controlled internal deployment

- Hosted Web UI with Server-Sent Events progress updates.
- Auth enabled by default and fail-closed.
- Environment-token auth and trusted reverse-proxy identity mode.
- Role-based access: viewer, analyst, admin.
- Production-mode startup validation.
- CSRF protection for state-changing scan requests.
- Request-size limits, malformed JSON handling, and structured API errors.
- Per-IP rate limiting and scan concurrency/queue limits.
- Security headers on normal and error responses.
- Trusted proxy CIDR checks for forwarded IP and identity headers.
- SQLite job persistence by default with WAL mode, foreign keys, busy timeout, and schema versioning.
- Structured JSON audit logs with request correlation IDs.
- Auth-protected Prometheus `/metrics` endpoint by default.
- Artifact path protection and role-aware config endpoint output.
- SQLite backup/restore scripts with validation, compression, and retention support.
- Non-root Dockerfile, `/data` volume, healthcheck, Docker Compose, and `.env.production.example`.
- CI gates for Ruff, mypy, pytest, `pip check`, `pip-audit`, package metadata validation, OWASP/ATLAS mapping validation, GenAI readiness validation, production-readiness validation, and functional acceptance.

---

## Quick start: local demo

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]

vulnoraiq --target demo --profile baseline
```

The demo target uses an in-memory echo client and does not call external services.

---

## Web UI: production-mode startup

Production mode fails closed if required controls are missing or unsafe.

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="$(openssl rand -hex 32)"
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
export VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports

python scripts/validate_runtime_production_config.py
vulnoraiq-web --host 127.0.0.1 --port 8787
```

---

## Running authorised scans

```bash
vulnoraiq \
  --target demo \
  --profile baseline \
  --output reports/output/demo-report.md \
  --json-output reports/output/demo-report.json \
  --sarif-output reports/output/demo-report.sarif \
  --dashboard-output reports/output/demo-dashboard.md \
  --html-dashboard-output reports/output/demo-dashboard.html
```

Only use configured targets against systems you own or are explicitly authorised to assess:

```bash
vulnoraiq \
  --target custom_http_agent \
  --profile baseline \
  --authorised
```

---

## Functional acceptance and release gates

```bash
ruff check .
mypy .
pytest -q
python -m pip check
pip-audit
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py
python scripts/validate_runtime_production_config.py
python scripts/validate_production_testing_readiness.py \
  --run-functional \
  --output-dir reports/output/production-readiness \
  --screenshot docs/assets/vulnoraiq-dashboard-example.svg
```

If Docker is available:

```bash
docker build -t vulnoraiq:0.2.0-rc .
python scripts/container_smoke_test.py
```

---

## Documentation map

| Need | Document |
| --- | --- |
| Documentation index | [`docs/README.md`](docs/README.md) |
| Deployment and environment variables | [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) |
| Operations runbook | [`docs/RUNBOOK.md`](docs/RUNBOOK.md) |
| Incident response | [`docs/INCIDENT_RESPONSE.md`](docs/INCIDENT_RESPONSE.md) |
| Release process | [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) |
| Migration from `0.0.1.x` to `0.2.0` | [`docs/MIGRATION.md`](docs/MIGRATION.md) |
| Readiness scorecard | [`docs/PRODUCTION_READINESS_SCORECARD.md`](docs/PRODUCTION_READINESS_SCORECARD.md) |
| Hardening backlog | [`docs/PRODUCTION_HARDENING_BACKLOG.md`](docs/PRODUCTION_HARDENING_BACKLOG.md) |
| Assessment assurance limits | [`docs/ASSESSMENT_ASSURANCE.md`](docs/ASSESSMENT_ASSURANCE.md) |
| GenAI Security readiness | [`docs/genai/PRODUCTION_READINESS_PLAN.md`](docs/genai/PRODUCTION_READINESS_PLAN.md) |
| Agentic Applications readiness | [`docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`](docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md) |
| Implementation status | [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) |
| OWASP LLM 2025 specs | [`docs/owasp/`](docs/owasp/) |
| MITRE ATLAS AI matrix | [`docs/MITRE_ATLAS_AI_MATRIX.md`](docs/MITRE_ATLAS_AI_MATRIX.md) |

---

## Roadmap

Next engineering priorities:

- deeper OWASP/GenAI category logic and evaluator thresholds
- richer real-world fixtures and benchmark targets
- provider/data inventory connectors for GenAI assessments
- native OIDC/JWT validation
- distributed rate limiting and shared CSRF/session state
- PostgreSQL or another HA persistence backend for multi-instance deployments
- WAF/CDN/DDoS deployment guidance
- tenant isolation model for SaaS
- independent penetration test of the Web UI and assessment engine
- report language maturity review for external assurance use

---

## License and third-party notices

VulnoraIQ-specific source code and documentation are licensed under this repository's license. See [`LICENSE`](LICENSE).

Some documentation and planning data is derived from MITRE ATLAS. MITRE ATLAS data is copyright 2021-2026 MITRE and licensed under the Apache License, Version 2.0. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
