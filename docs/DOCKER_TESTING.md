# Docker-first VulnoraIQ lab

VulnoraIQ's current safe path for real AI-agent, RAG, webhook, Ollama-style, and tool-loop testing is the Docker Compose lab.

The host should only run Docker commands, open the WebUI at <http://localhost:8787>, and inspect exported reports. Scans, mock-agent traffic, target validation, evidence capture, report generation, and smoke testing run inside containers.

## Start the lab

```bash
docker compose build
docker compose up -d
docker compose ps
```

Open <http://localhost:8787>.

The WebUI is published as `127.0.0.1:8787:8787`. Keep this loopback binding for normal laptop/workstation use. Do not change it to `8787:8787` unless you are intentionally moving to a shared/internal-server deployment with production auth, reverse proxy, TLS, and documented network controls.

## Services

| Service | Purpose |
| --- | --- |
| `vulnoraiq-web` | Non-root hosted WebUI and CLI container. Stores `/data/jobs.db`, `/data/reports`, `/data/evidence`, and `/data/audit`. |
| `local-mock-agent` | Deterministic mock target with chat-completions, Ollama-generate, RAG, webhook, and dry-run tool-loop endpoints. |
| `test-runner` | Optional Docker-only utility service under the `test` profile. |

All services run on the private `vulnoraiq-lab` bridge network. The network is marked internal, containers drop capabilities, and the Compose file does not use host networking, privileged mode, or Docker socket mounting. The mock agent is exposed only inside the lab network.

## Current Docker target configuration

The Docker service sets:

```text
VULNORAIQ_CONFIG_DIR=/app/config
VULNORAIQ_TARGET_CONFIG=targets.docker.yaml
VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports
VULNORAIQ_EVIDENCE_DIR=/data/evidence
VULNORAIQ_AUDIT_DIR=/data/audit
```

Docker lab targets are defined in `config/targets.docker.yaml` and use Docker service names such as `http://local-mock-agent:9090`, not host `localhost`.

## CLI from Docker

```bash
docker compose exec vulnoraiq-web vulnoraiq targets list
docker compose exec vulnoraiq-web vulnoraiq targets validate --target local_mock_agent
docker compose exec vulnoraiq-web vulnoraiq scan --target local_mock_agent --profile ai_agent_foundation --authorised
docker compose exec vulnoraiq-web vulnoraiq reports list
docker compose exec vulnoraiq-web vulnoraiq jobs list
docker compose exec vulnoraiq-web vulnoraiq jobs show --job-id <job-id>
```

## WebUI workflow

1. Start Docker Compose.
2. Open <http://localhost:8787>.
3. Use the target workspace to search/filter targets.
4. Validate target connectivity.
5. Confirm the authorisation checklist for non-demo targets.
6. Select a profile such as `ai_agent_foundation`, `baseline`, `rag`, `agent`, `full`, or a single focused profile.
7. Start the scan.
8. Review live progress, findings, policy status, recent jobs, and report outputs.
9. Update finding status/remediation actions when needed.

The React target workspace is wired to backend APIs for target inventory, runtime target save/delete, target validation, scan launch, recent job refresh, authenticated SSE progress, and persisted finding state/history.

## Smoke and acceptance checks

```bash
python scripts/docker_smoke_test.py
python scripts/validate_target_configs.py
python scripts/validate_production_testing_readiness.py --output-dir reports/output/production-readiness
python scripts/validate_production_testing_readiness.py --run-functional --output-dir reports/output/production-readiness
```

For browser testing on a host with Playwright installed:

```bash
npm install
npx playwright install chromium --with-deps
npm run test:webui:hosted
```

## Stop the lab

```bash
docker compose down
```

Use a volume reset only when you intentionally want to remove jobs, reports, evidence, and audit data:

```bash
docker compose down -v
```

## Troubleshooting

| Symptom | Check |
| --- | --- |
| WebUI does not open | `docker compose ps`, then `docker compose logs vulnoraiq-web` |
| WebUI is not reachable from another device | Expected for the local lab; it is bound to `127.0.0.1` on the host |
| Target validation fails | `docker compose logs local-mock-agent`; confirm the target uses `local-mock-agent:9090` inside Docker |
| No reports appear | Check `/data/reports` in the container and `VULNORAIQ_WEB_OUTPUT_ROOT` |
| Jobs are missing | Check `/data/jobs.db` and whether the Docker volume was reset |
| Browser tests fail locally | Confirm Playwright Chromium is installed and the environment can download browser binaries |

## Assurance boundary

Passing Docker smoke tests proves the lab wiring, target adapters, scanner path, and report/evidence generation work for deterministic mock targets. It does not prove real-world target assurance or certified VAPT-grade coverage.
