# VulnoraIQ

**VulnoraIQ** is a self-hosted AI security assessment lab for authorised testing of LLM applications, RAG systems, tool-using agents, AI-agent workflows, GenAI data-security controls, target adapters, evidence pipelines, reports, and operational guardrails.

The current codebase is **Docker-first for real AI-agent testing** and **React-console-first for the WebUI**. The safe default path starts the WebUI, scanner, job store, reports, evidence capture, and deterministic mock AI-agent target through Docker Compose. Host-native launchers still exist for local laptop/workstation development and demo use, but Docker Compose is the recommended path for real local lab testing.

> **Responsible-use boundary:** run VulnoraIQ only against systems you own or are explicitly authorised to assess. Non-demo targets require explicit authorisation. Findings are framework evidence requiring human review, not certified VAPT-grade assurance.

---

## Current status

| Area | Current status |
| --- | --- |
| Version | `0.2.0` beta |
| Supported posture | Self-hosted laptop/workstation/internal-server AI security testing lab |
| Safe default | Docker Compose lab with private network, deterministic mock agent, SQLite job store, evidence/reports under `/data`, and bounded target safety profiles |
| WebUI | React 18 + TypeScript + Vite SecOps console built into `webui/static/console/` and served by `webui/hosted_server.py` |
| Target management | Current React target workspace is wired to backend target and scan APIs for target listing, runtime target save/delete, connectivity validation, scan launch, and recent job refresh |
| CLI | `vulnoraiq` command supports target listing, target validation, authorised scans, report listing, and persisted job inspection |
| Coverage | OWASP LLM 2025 current-scope checks, OWASP AI Testing Guide foundation profile, Agentic readiness gates, GenAI `DSGAI01–DSGAI21` scenario harness, and MITRE ATLAS mapping governance |
| CI gates | Ruff, mypy, pytest on Python 3.10/3.11/3.12, pip check, pip-audit, metadata validation, OWASP/ATLAS validation, GenAI readiness validation, production-readiness validation, hosted WebUI Playwright flow, demo scan, and functional acceptance path |
| Release claim | Self-hosted laptop/server AI security testing application with controlled internal production-readiness gate passed |
| Not claimed | Certified VAPT-grade assurance, independent real-world GenAI detection assurance, or permission to test third-party systems |

Recent mainline changes now included in the documentation baseline:

- PR #45 removed the legacy static WebUI console; the React console is the supported WebUI.
- PR #46 added real authorised target testing with target adapters, scanner wiring, runtime target management, and mock-agent support.
- PR #47 made the safe lab Docker-first, with `targets.docker.yaml`, mock-agent service, safety profiles, smoke tooling, and Docker docs.
- PR #49 enhanced the React target-management workspace with search/filtering, readiness metrics, target validation, scan launch guardrails, and recent job display.

---

## Quick start: Docker-first safe lab

```bash
docker compose build
docker compose up -d
docker compose ps
```

Open <http://localhost:8787>.

The Compose lab starts:

- `vulnoraiq-web` — hosted WebUI, CLI, scanner, SQLite job store, report/evidence/audit paths.
- `local-mock-agent` — deterministic mock target exposing chat-completions, Ollama-generate, RAG, webhook, and dry-run tool-loop contracts.
- `test-runner` — optional profile service for Docker-only checks.

The lab network is private and internal. The WebUI is published on port `8787`; the mock agent is only reachable by the lab network.

### Docker CLI examples

```bash
docker compose exec vulnoraiq-web vulnoraiq targets list
docker compose exec vulnoraiq-web vulnoraiq targets validate --target local_mock_agent
docker compose exec vulnoraiq-web vulnoraiq scan --target local_mock_agent --profile ai_agent_foundation --authorised
docker compose exec vulnoraiq-web vulnoraiq reports list
docker compose exec vulnoraiq-web vulnoraiq jobs list
```

Reports are written under `/data/reports`, evidence under `/data/evidence`, audit logs under `/data/audit`, and persisted jobs in `/data/jobs.db`.

---

## WebUI overview

The current WebUI is the built React console under `webui/static/console/`, served by the Python hosted server. The source app lives in `webui/console/`.

Current WebUI capabilities:

- target inventory and runtime target management;
- search and environment filtering;
- target readiness metrics and health/status indicators;
- target connectivity validation through `POST /api/targets/{id}/validate`;
- runtime target save/delete through `POST /api/targets/save` and `POST /api/targets/delete`;
- scan history refresh through `GET /api/scans`;
- authorised scan launch through `POST /api/scans`;
- readiness checklist for authorisation, owner contact, rate limits, and safety profile;
- dashboard, findings, intelligence, and mock-assisted workflow panels.

Backend integration still intentionally uses typed mock data or mocked state for features whose APIs are not yet implemented, including live SSE scan progress, persisted finding remediation/status transitions, and the assistant chat backend.

---

## Local standalone launcher

For laptop/workstation development or demo use outside Docker:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
python launch-vulnoraiq-webui.py
```

Or double-click from the repository root:

| Platform | Launcher |
| --- | --- |
| Windows | `launch-vulnoraiq-webui.bat` |
| macOS | `launch-vulnoraiq-webui.command` |
| Linux | `launch-vulnoraiq-webui.sh` |
| Any platform | `launch-vulnoraiq-webui.py` |

Launcher mode is for loopback local use. For shared/internal-server deployment, enable auth and follow `docs/DEPLOYMENT.md`.

---

## Self-hosted production-mode startup

Production mode fails closed when required controls are missing or unsafe.

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

Use a reverse proxy for TLS, remote internal access, and organisation-specific identity controls.

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

Docker checks:

```bash
docker build -t vulnoraiq:0.2.0-rc .
python scripts/docker_smoke_test.py
```

---

## Documentation map

| Need | Document |
| --- | --- |
| Documentation index and current status | [`docs/README.md`](docs/README.md) |
| Docker-first lab usage | [`docs/DOCKER_TESTING.md`](docs/DOCKER_TESTING.md) |
| Safety and target boundaries | [`docs/SAFETY_MODEL.md`](docs/SAFETY_MODEL.md), [`docs/TARGET_CONFIGURATION.md`](docs/TARGET_CONFIGURATION.md) |
| WebUI usage | [`docs/WEBUI_GUIDE.md`](docs/WEBUI_GUIDE.md), [`docs/WEB_UI_TEST_CATALOG.md`](docs/WEB_UI_TEST_CATALOG.md) |
| CLI usage | [`docs/CLI_GUIDE.md`](docs/CLI_GUIDE.md) |
| Deployment and operations | [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md), [`docs/RUNBOOK.md`](docs/RUNBOOK.md), [`docs/INCIDENT_RESPONSE.md`](docs/INCIDENT_RESPONSE.md) |
| Release and packaging | [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md), [`docs/RELEASE_ARTIFACTS.md`](docs/RELEASE_ARTIFACTS.md), [`docs/PYPI_PACKAGE.md`](docs/PYPI_PACKAGE.md) |
| Migration | [`docs/MIGRATION.md`](docs/MIGRATION.md) |
| Implementation status | [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) |
| Readiness and hardening | [`docs/PRODUCTION_READINESS_SCORECARD.md`](docs/PRODUCTION_READINESS_SCORECARD.md), [`docs/PRODUCTION_HARDENING_BACKLOG.md`](docs/PRODUCTION_HARDENING_BACKLOG.md), [`docs/ASSESSMENT_ASSURANCE.md`](docs/ASSESSMENT_ASSURANCE.md) |
| OWASP AI Testing Guide | [`docs/AI_TESTING_GUIDE_INTEGRATION.md`](docs/AI_TESTING_GUIDE_INTEGRATION.md), [`docs/AI_TESTING_GUIDE_IMPLEMENTATION_PLAN.md`](docs/AI_TESTING_GUIDE_IMPLEMENTATION_PLAN.md) |
| OWASP LLM mapping roadmap | [`docs/OWASP_LLM_TOP10_MAPPING_IMPLEMENTATION_PLAN.md`](docs/OWASP_LLM_TOP10_MAPPING_IMPLEMENTATION_PLAN.md) |
| GenAI readiness | [`docs/genai/PRODUCTION_READINESS_PLAN.md`](docs/genai/PRODUCTION_READINESS_PLAN.md) |
| Agentic readiness | [`docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`](docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md) |
| MITRE ATLAS | [`docs/MITRE_ATLAS_AI_MATRIX.md`](docs/MITRE_ATLAS_AI_MATRIX.md), [`docs/mitre-atlas-mapping.md`](docs/mitre-atlas-mapping.md) |

---

## Roadmap

Current post-`0.2.0` maturity priorities:

- implement the full 32-test OWASP AI Testing Guide roadmap beyond the current foundation profile;
- deepen evaluator logic and thresholds for real approved environments;
- implement remaining React-console backend APIs for SSE progress, finding state transitions, remediation actions, and assistant chat;
- add richer target templates for AI agents, LLM APIs, RAG systems, local model servers, and provider/data inventories;
- add signed/notarised installers and release artifacts;
- add optional OIDC/JWT support for enterprise deployments;
- add stronger image scanning, SAST/DAST, SIEM integration, and independent assurance validation.

---

## License and notices

VulnoraIQ-specific source code and documentation are licensed under Apache-2.0. See [`LICENSE`](LICENSE).

Some documentation and planning data is derived from MITRE ATLAS. MITRE ATLAS data is copyright 2021-2026 MITRE and licensed under the Apache License, Version 2.0. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
