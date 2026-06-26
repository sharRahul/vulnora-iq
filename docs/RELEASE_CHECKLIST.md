# VulnoraIQ release checklist

> **Current target:** `0.3.0` / `0.3.0-rc1`  
> **Scope:** Docker-first/self-hosted laptop-server production-readiness release  
> **Last updated:** 2026-06-26

## Release boundary

`0.3.0` may be described as:

> Self-hosted laptop/server AI security testing application with controlled internal production-readiness gate passed.

It may also be described as:

> Docker-first local AI-agent testing lab with a React SecOps console, backend target-management APIs, deterministic mock-agent targets, and explicit authorisation gates.

Do **not** describe `0.3.0` as certified VAPT-grade, independently validated real-world GenAI detection assurance, or authorised for assessment of systems without written permission.

## Required pre-release checks

Run from a clean checkout:

```bash
python -m pip install --upgrade pip
pip install -e .[dev]
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

## WebUI checks

The supported WebUI is the React console. Before release:

```bash
cd webui/console
npm install
npm run typecheck
npm run build
cd ../..
npm install
npx playwright install chromium --with-deps
npm run test:webui:hosted
```

Confirm that built assets under `webui/static/console/` are updated and served by `webui/hosted_server.py`.

## Docker checks

```bash
docker compose build
docker compose up -d
docker compose ps
python scripts/docker_smoke_test.py
docker compose exec vulnoraiq-web vulnoraiq targets validate --target local_mock_agent
docker compose exec vulnoraiq-web vulnoraiq scan --target local_mock_agent --profile ai_agent_foundation --authorised
docker compose down
```

## Documentation checks

Confirm these files match the release claim and current codebase:

- `README.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `docs/README.md`
- `docs/IMPLEMENTATION_STATUS.md`
- `docs/DOCKER_TESTING.md`
- `docs/WEBUI_GUIDE.md`
- `docs/CLI_GUIDE.md`
- `docs/SAFETY_MODEL.md`
- `docs/TARGET_CONFIGURATION.md`
- `docs/PRODUCTION_READINESS_SCORECARD.md`
- `docs/PRODUCTION_HARDENING_BACKLOG.md`
- `docs/ASSESSMENT_ASSURANCE.md`

## Release artifacts

Platform release artifacts are built only by the release workflow or manual release dispatch. See [`RELEASE_ARTIFACTS.md`](RELEASE_ARTIFACTS.md).

Python package publishing is release-only/manual. See [`PYPI_PACKAGE.md`](PYPI_PACKAGE.md).

## Final review questions

- Does every non-demo scan path require explicit authorisation?
- Does production mode fail closed without safe auth/runtime configuration?
- Does the Docker lab use the private network and service-name targets?
- Does the React console serve the current built assets?
- Do target-management UI claims match actual backend APIs?
- Are GenAI/OWASP/Agentic/MITRE claims scoped to framework evidence and human review?
- Are release notes clear about remaining maturity items?
