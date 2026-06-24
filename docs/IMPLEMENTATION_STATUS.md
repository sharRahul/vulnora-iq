# Implementation status

This document separates current implemented capability from future assurance and maturity work.

> **Current maturity:** VulnoraIQ `0.2.0` is a Docker-first, self-hosted AI security testing lab with controlled internal production-readiness gates. It supports authorised local/internal testing of LLM, RAG, tool-using, agentic, and GenAI data-security scenarios through a Python scanner, target adapters, a hosted React WebUI, WebUI assistant backend/model controls, expanded target templates, CLI, SQLite job persistence, reports, evidence, on-demand signed release packages, supply-chain workflow evidence, loopback-only local Docker publishing, and CI validation. This is complete for self-hosted laptop/server use within the current authorised local/internal scope.

> **Assurance limitation:** OWASP, GenAI, Agentic, and MITRE mappings are framework evidence and planning/validation controls. They are not independently validated VAPT-grade assurance. See [`ASSESSMENT_ASSURANCE.md`](ASSESSMENT_ASSURANCE.md) for the full assurance boundary.

## Mainline status as of 2026-06-24

| Area | Status | Evidence |
| --- | --- | --- |
| Version/package | Complete for `0.2.0` beta | `pyproject.toml`, package entry points, metadata validation. |
| Docker-first safe lab | Complete for current local scope | `docker-compose.yml`, loopback-only `127.0.0.1:8787:8787` WebUI publishing, Dockerfile, mock-agent, Docker smoke tests. |
| Real authorised target testing | Complete for current local/internal scope | Target adapters, target validation, scanner wiring, runtime target APIs, mock-agent targets. |
| React WebUI | Complete as supported WebUI | `webui/console/` source and `webui/static/console/` built assets. Legacy static console has been removed. |
| WebUI target workspace | Complete for current backend APIs | Search/filtering, readiness metrics, health/status pills, safety checklist, target save/delete, validation, scan launch, recent jobs, SSE progress, finding actions/history. |
| WebUI assistant | Complete for current self-hosted path | Assistant backend API, CSRF-protected chat requests, model controls, and React controls. |
| CLI | Complete for current scope | `targets list`, `targets validate`, `scan`, `reports list`, `jobs list`, and `jobs show`. |
| Auth/security hardening | Complete for self-hosted internal scope | Token auth, trusted proxy mode, CSRF, rate limiting, request limits, security headers, audit logs, metrics, artifact path protection. |
| Persistence | Complete for current scope | SQLite job store with WAL, schema versioning, foreign keys, busy timeout. |
| OWASP LLM | Complete for current safe local/internal scope | OWASP docs, oracles, fixtures, profile/module coverage, mapping validation. |
| OWASP AI Testing Guide | Complete for safe synthetic coverage | AITG manifest, validator, `owasp-aitg-full` profile, and implementation roadmap. |
| GenAI Security | Complete for current controlled scenario-harness scope | `DSGAI01–DSGAI21`, scenario cases, deterministic evaluators, validator, tests, docs. |
| Agentic Applications | Complete for repo-level self-hosted readiness gates | Agentic readiness plan, mapping validation, CI gates. |
| MITRE ATLAS | Complete for planning/mapping governance scope | Matrix docs, crosswalk, mapping validator, third-party notices. |
| Release packaging | Complete for self-hosted package scope | Manual release workflow, double-click launchers, bootstrap `.venv`, checksums, GitHub artifact attestations, optional GPG signatures. |
| Supply-chain workflow | Complete for current container release scope | Trivy filesystem/image scans, SARIF artifacts, SPDX/CycloneDX SBOMs, optional strict gates, GHCR publish, Cosign keyless signing, and verification evidence. |
| CI | Complete gate set | Python matrix, Ruff, mypy, pytest, pip check/audit, validators, hosted WebUI flow, demo scan, functional acceptance, loopback/docs cleanup regression tests. |

## Current complete capability

| Capability | Current implementation |
| --- | --- |
| Safe local demo | `demo` target remains an in-memory safe target requiring no external keys. |
| Docker mock-agent lab | Deterministic local target with chat-completions, Ollama-generate, RAG, webhook, and dry-run tool-loop contracts. |
| Loopback Docker WebUI | Docker Compose publishes the WebUI as `127.0.0.1:8787:8787`; tests fail if it regresses to all-interface publishing. |
| Configured target adapters | HTTP JSON, chat-completions, Ollama-generate, webhook JSON, RAG query, and agent tool-loop shapes. |
| Authorisation gate | CLI `--authorised` and WebUI checklist for non-demo scans. |
| Scanner/reporting | Markdown, JSON, SARIF, Markdown dashboard, HTML dashboard, branded export and evidence output. |
| Policy and scoring | Findings, scores, policy status, exceptions, and approval evidence validation. |
| WebUI server | Hardened Python hosted server with security headers, CSRF, rate limiting, structured errors, metrics, audit logs, SSE events, persisted finding APIs, and assistant chat API wrapper. |
| WebUI console | React TypeScript SecOps console with target management, dashboards, findings/intelligence panels, live assistant chat, and typed UI data models. |
| Target template library | Common LLM APIs, RAG endpoints, local model servers, agent frameworks, and provider gateway templates with dry-run defaults and validator coverage. |
| Persistence | SQLite default with operational backup/restore tooling. |
| Release packages | Windows `.zip`, Linux `.tar.gz`, and macOS `.dmg` packages with double-click bootstrap launchers, checksums, artifact attestations, and optional GPG signatures. |
| Supply-chain evidence | Workflow artifacts include Trivy tables/SARIF files, filesystem SPDX SBOM, image CycloneDX SBOM, and Cosign verification when image publishing is enabled. |
| Release validation | Package metadata, OWASP/ATLAS mapping, GenAI readiness, production readiness, runtime config, and functional acceptance scripts. |

## Known incomplete or future maturity items

| Area | Status |
| --- | --- |
| Enterprise identity | Trusted proxy identity exists; direct OIDC/JWT remains future work and is planned in `docs/future-plans/OIDC_JWT_AUTH_PLAN.md`. |
| Native installer certificates | On-demand release packages are signed/attested; Authenticode Windows installers, notarised macOS app/pkg installers, and distro-native Linux packages remain future work. |
| SIEM integration | Audit logs exist; packaged SIEM schemas/rules remain future work. |
| Multi-instance operation | CSRF/rate-limit stores and SQLite remain single-instance/local-server oriented. |
| Independent assurance | Independent assurance workflow, checklist, and evidence bundle generation are implemented; external independent review remains required before stronger assurance claims. |
| Real-world GenAI assurance | Current harness uses safe synthetic scenarios and controlled validation; broader approved-environment validation remains future maturity work. |

## Safe usage summary

```bash
docker compose build
docker compose up -d
docker compose exec vulnoraiq-web vulnoraiq targets validate --target local_mock_agent
docker compose exec vulnoraiq-web vulnoraiq scan --target local_mock_agent --profile ai_agent_foundation --authorised
```

For host-native demo/development:

```bash
python launch-vulnoraiq-webui.py
vulnoraiq --target demo --profile baseline
```

## Documentation rule

Keep `README.md`, `docs/README.md`, this file, WebUI/CLI/Docker docs, safety/target docs, scorecard, backlog, assurance doc, `SECURITY.md`, and `CHANGELOG.md` aligned whenever code changes affect deployment posture, target support, WebUI behaviour, CI gates, or release claims.
