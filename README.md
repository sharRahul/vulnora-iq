# VulnoraIQ

**VulnoraIQ** is a Docker-first, self-hosted testing lab for authorised local or internal use with a browser GUI, CLI, reports, evidence, and CI validation workflows.

VulnoraIQ is a **self-hosted internal application**. The same scope covers an **internal server** deployment when production auth, reverse proxy, TLS, audit, and backup controls are configured. The current release claim is scoped: **self-hosted laptop/server AI security testing application with controlled internal production-readiness gate passed**. Findings are framework evidence for human review, not certified VAPT-grade assurance. See [`docs/ASSESSMENT_ASSURANCE.md`](docs/ASSESSMENT_ASSURANCE.md).

## Current status

| Area | Current status |
| --- | --- |
| Version | `0.2.0` beta |
| GUI/WebUI | Yes. Browser-based React console served by `vulnoraiq-web` / `webui/hosted_server.py`. |
| Default posture | Local laptop/workstation Docker Compose lab with loopback-only WebUI publishing. |
| Local target | Deterministic mock target for local lab testing. |
| Persistence | SQLite job store with WAL mode, foreign keys, busy timeout, and schema versioning. |
| Future identity | Direct OIDC/JWT is deferred; see `docs/future-plans/OIDC_JWT_AUTH_PLAN.md`. |

## Quick start

Recommended local GUI path with Docker Compose. This does not install VulnoraIQ into your host Python environment.

```bash
docker compose build
docker compose up -d
docker compose ps
```

Open the GUI/WebUI in your browser: <http://localhost:8787>.

The WebUI is published on host loopback only: `127.0.0.1:8787:8787`.

Useful Docker commands:

```bash
docker compose exec vulnoraiq-web vulnoraiq targets list
docker compose exec vulnoraiq-web vulnoraiq targets validate --target local_mock_agent
docker compose exec vulnoraiq-web vulnoraiq scan --target local_mock_agent --profile ai_agent_foundation --authorised
docker compose exec vulnoraiq-web vulnoraiq reports list
docker compose exec vulnoraiq-web vulnoraiq jobs list
```

Cleanly close the Docker lab:

```bash
docker compose down
```

Only use this when you intentionally want to delete local jobs, reports, evidence, audit data, and Docker volumes:

```bash
docker compose down -v
```

Restart later:

```bash
docker compose up -d
```

Install from a source/package checkout and run locally without Docker:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .[dev]
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Open <http://127.0.0.1:8787>. Cleanly close with `Ctrl+C` in the terminal that started `vulnoraiq-web`.

Build and install a local wheel package:

```bash
python -m pip install -e .[release]
python -m build
pip install dist/vulnoraiq-0.2.0-py3-none-any.whl
vulnoraiq-web --host 127.0.0.1 --port 8787
```

If a package-index release is published later:

```bash
pip install vulnoraiq
vulnoraiq-web --host 127.0.0.1 --port 8787
```

## WebUI and CLI

The supported GUI is the built React console under `webui/static/console/`; the source app lives in `webui/console/`. It is a browser GUI, not a native desktop window.

The existing double-click launchers are part of the supported GUI flow for source checkouts and release packages:

| Platform | Launcher |
| --- | --- |
| Windows | `launch-vulnoraiq-webui.bat` |
| macOS | `launch-vulnoraiq-webui.command` |
| Linux | `launch-vulnoraiq-webui.sh` |

These launchers call `scripts/bootstrap_launch.py`, create or reuse `.venv`, prepare the local package environment, and start the browser WebUI on loopback.

You can also run the local launcher directly from a source checkout:

```bash
python launch-vulnoraiq-webui.py
```

Close launcher mode with the WebUI **Stop local server** control when available, or press `Ctrl+C` in the terminal that started it.

## Deployment and security boundary

Local Docker and launcher paths are for single-user controlled use. Shared/internal-server deployment requires production configuration validation, real secrets, TLS at a trusted reverse proxy, audit retention, backups, and authorised target governance.

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
```

WebUI browser flow:

```bash
npm install
npx playwright install chromium --with-deps
npm run test:webui:hosted
```

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

## License and notices

VulnoraIQ-specific source code and documentation are licensed under Apache-2.0. See [`LICENSE`](LICENSE).

Some documentation and planning data is derived from MITRE ATLAS. MITRE ATLAS data is copyright 2021-2026 MITRE and licensed under the Apache License, Version 2.0. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
