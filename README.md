# VulnoraIQ

**VulnoraIQ** is a self-hosted AI security assessment application for authorised testing of **LLM applications, RAG pipelines, AI agents, tool-using systems, GenAI data flows, vector stores, providers, telemetry, reports, and orchestration layers**.

It is designed to run on a **laptop, workstation, lab machine, or internal server** so security teams can test AI agents and LLM applications they own or are explicitly authorised to assess.

VulnoraIQ helps teams collect evidence, score findings, generate reports, and track OWASP LLM / OWASP GenAI / Agentic / MITRE ATLAS coverage as the framework matures.

---

## Current status

**Version:** `0.2.0`  
**Deployment posture:** self-hosted laptop/server application with controlled internal production-readiness gate passed  
**Assessment assurance:** framework evidence requiring human review, not certified VAPT-grade assurance

| Area | Status |
| --- | --- |
| Local laptop / workstation demo | Complete |
| Self-hosted internal server deployment | Complete with production configuration validation |
| OWASP LLM coverage | Complete for current safe local/internal assessment scope |
| GenAI Security readiness | Complete for `DSGAI01–DSGAI21` controlled internal scenario-harness scope |
| Agentic Applications readiness | Complete for controlled internal phase gates |
| Certified VAPT-grade security assurance | Not claimed |

> **Maturity warning:** VulnoraIQ is intended to run as a local or self-hosted internal application for authorised assessment work.

`0.2.0` may be described as:

> **Self-hosted laptop/server AI security testing application with controlled internal production-readiness gate passed.**

It must **not** be described as certified VAPT-grade assurance or a real-world VAPT replacement.

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

## Home screen

The screenshot below is the VulnoraIQ Web UI home screen, captured from the running console. It shows the startup and local-server-controls panel, the test selection and run-readiness form, realtime progress, the completed-assessment dashboard area, and recent scan history on a single page.

![VulnoraIQ Web UI home screen](docs/assets/vulnoraiq-webui-home.png)

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

- Complete OWASP LLM Top 10 2025 implementation specs for all 10 categories in [`docs/owasp/`](docs/owasp/).
- Complete safe oracle coverage for all 10 OWASP LLM 2025 categories in the current local/internal assessment scope.
- Complete GenAI Security scenario-harness coverage for `DSGAI01–DSGAI21` in [`benchmarks/fixtures/genai/scenarios.yaml`](benchmarks/fixtures/genai/scenarios.yaml).
- GenAI deterministic evaluator primitives in [`core/genai_evaluators.py`](core/genai_evaluators.py).
- GenAI readiness gate in [`scripts/validate_genai_readiness.py`](scripts/validate_genai_readiness.py).
- Agentic Applications readiness phase gate in [`docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`](docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md).
- MITRE ATLAS AI planning matrix in [`docs/MITRE_ATLAS_AI_MATRIX.md`](docs/MITRE_ATLAS_AI_MATRIX.md).
- Source-driven ATLAS matrix generation with explicit `Unmapped / map later` backlog preservation.
- MITRE ATLAS-derived documentation tracked in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

### Production hardening for self-hosted internal deployment

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

## Run the Web UI: double-click launcher

For local self-hosted use you do not need to remember any commands. After a one-time
`pip install -e .` (or `pip install -e .[dev]`), double-click the launcher for your
platform from the repository root:

| Platform | Double-click file |
| --- | --- |
| Windows | `launch-vulnoraiq-webui.bat` |
| macOS | `launch-vulnoraiq-webui.command` |
| Linux | `launch-vulnoraiq-webui.sh` |
| Any platform (Python) | `launch-vulnoraiq-webui.py` |

The launcher runs the same steps for every platform:

1. Runs **startup dependency checks** (Python version, `PyYAML`, `requests`, `rich`,
   core package modules, target/profile configuration, Web UI assets, output directory,
   and the SQLite job store).
2. Performs **quick-start actions** — ensures the local output directory and SQLite job
   store exist, binds to loopback for safe local assessment, and opens the console in your
   default browser.
3. Opens [`http://127.0.0.1:8787/`](http://127.0.0.1:8787/) automatically once the server
   is healthy.

The startup panel inside the Web UI shows the live results of those checks, the current
**configuration options** (host, port, output root, job store, auth) and how to change
each one, plus a **Stop local server** button so you can shut the server down cleanly from
the browser without returning to the terminal.

![VulnoraIQ Web UI startup and local server controls](docs/assets/vulnoraiq-webui-startup.png)

You can override the defaults when launching from a terminal:

```bash
python launch-vulnoraiq-webui.py --host 127.0.0.1 --port 8888   # custom port
python launch-vulnoraiq-webui.py --no-browser                   # start without opening a browser
```

The launcher runs in local development mode with authentication disabled and the in-browser
stop control enabled. It is intended for laptop/workstation use on loopback only; for an
exposed or shared deployment use the self-hosted startup below.

---

## How to use the application

Once the console is open in your browser:

1. **Check startup readiness.** The *Startup and local server controls* panel at the top
   shows the dependency and quick-start checks. A green **Ready for local assessment** badge
   means you can run scans. Use **Refresh checks** to re-run them at any time.
2. **Choose what to run.** In *Choose tests and run scan*, pick a **Target** (start with the
   safe local `demo` target) and a **Test option** — either a full assessment suite or a
   single focused OWASP LLM / RAG / agentic test from the categorised catalogue. The
   *Run readiness* panel summarises exactly what will run before you start.
3. **Authorise configured targets.** The `demo` target needs no authorisation. For any
   configured non-demo target you must tick the authorisation checkbox confirming you own
   or are explicitly authorised to assess it.
4. **Start the assessment** with **Start selected assessment** and watch the *Realtime
   progress* panel update live (initialising → scanning → policy → dashboard → completed).
5. **Review the dashboard.** When the scan completes, the *Completed assessment dashboard*
   shows summary cards, top risks, the severity distribution, policy evaluation, and a
   filterable findings list with evidence previews.
6. **Export outputs.** Download the Markdown, JSON, SARIF, Markdown dashboard, and HTML
   dashboard artifacts from the *Outputs for presentation* section.
7. **Stop the server** when you are done with the red **Stop local server** button in the
   startup panel — the local server shuts down cleanly and the launcher window exits.

---

## Web UI: self-hosted startup

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

### Stopping the Web UI server

If you started the Web UI with a double-click launcher, use the **Stop local server** button in the startup panel of the console to shut it down cleanly from the browser.

If the Web UI is running in the foreground, stop it with `Ctrl+C` in the terminal where `vulnoraiq-web` is running.

If it was started in the background, find the process that is listening on port `8787` and terminate it:

```bash
lsof -ti :8787 | xargs kill
```

Use a forced kill only if the process does not stop cleanly:

```bash
lsof -ti :8787 | xargs kill -9
```

For Docker Compose deployments, stop the service with:

```bash
docker compose down
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
  --output-dir reports/output/production-readiness
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

Post-completion hardening priorities:

- deeper OWASP/GenAI category logic and evaluator thresholds
- richer local and self-hosted benchmark targets
- provider/data inventory connectors for authorised GenAI assessments
- clearer target adapter templates for AI agents, LLM APIs, RAG systems, and local model servers
- packaged laptop/server installation paths
- optional OIDC/JWT validation for enterprise self-hosted deployments
- stronger single-server operations guidance for reverse proxy, TLS, backups, and audit logs
- independent penetration test of the Web UI and assessment engine
- report language maturity review for external assurance use

---

## License and third-party notices

VulnoraIQ-specific source code and documentation are licensed under this repository's license. See [`LICENSE`](LICENSE).

Some documentation and planning data is derived from MITRE ATLAS. MITRE ATLAS data is copyright 2021-2026 MITRE and licensed under the Apache License, Version 2.0. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
