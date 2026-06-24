# VulnoraIQ

**VulnoraIQ** is a Docker-first, self-hosted AI testing lab for authorised local or internal use. It supports LLM, RAG, AI-agent, target-adapter, evidence, reporting, WebUI, and CI validation workflows.

VulnoraIQ is a **self-hosted internal application**. The same scope covers an **internal server** deployment when production auth, reverse proxy, TLS, audit, and backup controls are configured. The current release claim is scoped: **self-hosted laptop/server AI security testing application with controlled internal production-readiness gate passed**. Findings are framework evidence for human review, not certified VAPT-grade assurance.

## Current status

| Area | Current status |
| --- | --- |
| Version | `0.2.0` beta |
| Default posture | Local laptop/workstation Docker Compose lab with loopback-only WebUI publishing |
| WebUI | React 18 + TypeScript + Vite SecOps console served by `webui/hosted_server.py` |
| Local targets | Deterministic mock AI-agent target for chat-completions, Ollama-generate, RAG, webhook, and dry-run tool-loop contracts |
| Target support | Authorised local/internal adapters, target validation, dry-run defaults, allow-lists, rate limits, and evidence capture |
| Persistence | SQLite job store with WAL mode, foreign keys, busy timeout, and schema versioning |
| Security controls | Token auth, trusted reverse-proxy identity, CSRF, rate limits, request limits, security headers, metrics, audit logs, production startup checks |
| CI/release | Python matrix, lint/type/tests, dependency checks, WebUI browser flow, functional acceptance, release packaging, SBOMs, Trivy reports, and Cosign image-signing path |
| Future identity | Direct OIDC/JWT is intentionally deferred; see `docs/future-plans/OIDC_JWT_AUTH_PLAN.md` |

## Quick start

```bash
docker compose build
docker compose up -d
docker compose ps
```

Open <http://localhost:8787>.

The Compose lab starts:

- `vulnoraiq-web` — hosted WebUI, CLI, scanner, SQLite job store, reports, evidence, and audit paths.
- `local-mock-agent` — deterministic local target reachable only inside the Docker lab network.
- `test-runner` — optional test-profile container.

The WebUI is published on host loopback only: `127.0.0.1:8787:8787`. Keep this binding for normal local use.

```bash
docker compose exec vulnoraiq-web vulnoraiq targets list
docker compose exec vulnoraiq-web vulnoraiq targets validate --target local_mock_agent
docker compose exec vulnoraiq-web vulnoraiq scan --target local_mock_agent --profile ai_agent_foundation --authorised
docker compose exec vulnoraiq-web vulnoraiq reports list
docker compose exec vulnoraiq-web vulnoraiq jobs list
```

## WebUI and CLI

The supported WebUI is the built React console under `webui/static/console/`; the source app lives in `webui/console/`.

Current WebUI capabilities include target inventory, runtime target save/delete, target validation, scan launch, SSE scan progress, finding status/remediation actions, assistant backend model controls, dashboards, findings, and workflow panels.

For host-native demo/development outside Docker:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
python launch-vulnoraiq-webui.py
```

Launcher mode is loopback-only and intended for local laptop/workstation use. For shared or internal-server deployments, use production mode and follow `docs/DEPLOYMENT.md`.

## Deployment and security boundary

Local Docker and launcher paths are for single-user controlled use. Shared/internal-server deployment requires production configuration validation, real secrets, TLS at a trusted reverse proxy, protected metrics/health endpoints, audit retention, backups, and authorised target governance.

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

Use trusted reverse-proxy identity only when the proxy authenticates users and strips spoofed identity headers. Direct OIDC/JWT remains future work, not a blocker for current local single-user usage.

## Validation and release gates

```bash
ruff check .
mypy .
pytest -q
python -m pip check
pip-audit
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py --output-dir reports/output/production-readiness
python scripts/validate_runtime_production_config.py
python scripts/validate_production_testing_readiness.py --run-functional --output-dir reports/output/production-readiness
```

WebUI browser flow:

```bash
npm install
npx playwright install chromium --with-deps
npm run test:webui:hosted
```

Docker and supply-chain checks are covered by Docker smoke tests and the security supply-chain workflow.

## Documentation and roadmap

| Need | Document |
| --- | --- |
| Documentation index and status | [`docs/README.md`](docs/README.md), [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) |
| Docker lab | [`docs/DOCKER_TESTING.md`](docs/DOCKER_TESTING.md) |
| Deployment and operations | [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md), [`docs/RUNBOOK.md`](docs/RUNBOOK.md), [`docs/INCIDENT_RESPONSE.md`](docs/INCIDENT_RESPONSE.md) |
| WebUI and CLI | [`docs/WEBUI_GUIDE.md`](docs/WEBUI_GUIDE.md), [`docs/WEB_UI_TEST_CATALOG.md`](docs/WEB_UI_TEST_CATALOG.md), [`docs/CLI_GUIDE.md`](docs/CLI_GUIDE.md) |
| Safety and targets | [`docs/SAFETY_MODEL.md`](docs/SAFETY_MODEL.md), [`docs/TARGET_CONFIGURATION.md`](docs/TARGET_CONFIGURATION.md) |
| Release and supply chain | [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md), [`docs/RELEASE_ARTIFACTS.md`](docs/RELEASE_ARTIFACTS.md), [`docs/SUPPLY_CHAIN_PIPELINE.md`](docs/SUPPLY_CHAIN_PIPELINE.md), [`docs/PYPI_PACKAGE.md`](docs/PYPI_PACKAGE.md) |
| Readiness and assurance | [`docs/PRODUCTION_READINESS_SCORECARD.md`](docs/PRODUCTION_READINESS_SCORECARD.md), [`docs/PRODUCTION_HARDENING_BACKLOG.md`](docs/PRODUCTION_HARDENING_BACKLOG.md), [`docs/ASSESSMENT_ASSURANCE.md`](docs/ASSESSMENT_ASSURANCE.md) |
| Future identity plan | [`docs/future-plans/OIDC_JWT_AUTH_PLAN.md`](docs/future-plans/OIDC_JWT_AUTH_PLAN.md) |

Current future maturity priorities are direct OIDC/JWT support for enterprise deployments, native OS certificate-signed installers, SIEM rule packs, multi-instance shared state, approved-environment validation, and external independent review.

## License and notices

VulnoraIQ-specific source code and documentation are licensed under Apache-2.0. See [`LICENSE`](LICENSE).

Some documentation and planning data is derived from MITRE ATLAS. MITRE ATLAS data is copyright 2021-2026 MITRE and licensed under the Apache License, Version 2.0. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
