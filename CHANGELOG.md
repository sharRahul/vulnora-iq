# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Removed

- All demo, mock, and fixture targets from default runtime. No default scan target; `--target` is now required. Backend rejects target IDs containing `demo`, `mock`, `fake`, or `fixture` unless `VULNORAIQ_ALLOW_TEST_FIXTURE_TARGETS=true` is set.
- `local-mock-agent` service removed from default Docker Compose; moved behind `profiles: ["test"]`.
- `start_demo_scan` permission removed; all scans use `start_configured_scan`.
- Demo special-casing in scan authorisation gate and module severity logic.
- `config/targets.yaml` and `config/targets.docker.yaml` cleaned of all fake targets; replaced with commented templates.
- WebUI "Run Scan" no longer defaults to `target: demo`; requires a configured target; disabled when none exist.

### Added

- Experimental Agent Lab WebUI flow for importing real AI-agent projects, configuring LLM provider settings, choosing CPU/GPU Docker runtime options, building/running agents, auto-creating runtime targets, and launching authorised scans.
- Agent Lab backend APIs under `/api/agent-lab/*` for project import, analysis, Dockerfile generation, deployment, deployment inventory, and cleanup.
- Agent Lab static page served at `/agent-lab` and embedded in the React Project Importer workspace.
- Agent Lab documentation in `docs/AGENT_LAB.md` and implementation plan in `docs/AGENT_LAB_PLAN.md`.
- Package-data inclusion for `webui/static/agent-lab/*`.
- Agent Lab smoke tests for project ID policy and provider environment mapping.
- OWASP AI Testing Guide foundation suite and single-test Web UI profiles covering GenAI red teaming methodology, CSA agentic AI red teaming, OWASP AI Exchange controls, AI Security and Privacy design, AI VSS scoring review, and NIST AI 100-2 adversarial ML taxonomy alignment.
- Safe `payloads/ai_testing_guide.yaml` methodology payload library for authorised local/internal AI assessment runs.
- Local OWASP lab AI agent target templates for HTTP JSON, chat-completions-compatible, Ollama generate, and webhook JSON contracts.
- Documentation for testing actual local AI agents through `docs/AI_TESTING_GUIDE_INTEGRATION.md`.
- Release-only Windows, Linux, and macOS artifact build workflow triggered by published GitHub Releases or manual dispatch only.
- Platform release package builder for native release formats: `vulnoraiq-<version>-windows.zip`, `vulnoraiq-<version>-linux.tar.gz`, and `vulnoraiq-<version>-macos.dmg`.
- On-demand release signing bundle with SHA256 checksums, GitHub artifact attestations, and optional GPG detached signatures.
- Self-bootstrapping double-click release launchers that create `.venv`, install VulnoraIQ locally, and start the WebUI.
- Linux `VulnoraIQ.desktop` launcher descriptor for extracted release packages.
- Release artifact documentation in `docs/RELEASE_ARTIFACTS.md`.
- Python package build workflow for wheel/source distributions, with manual TestPyPI/PyPI publishing using trusted publishing.
- PyPI package publishing documentation in `docs/PYPI_PACKAGE.md`.
- Cross-platform local Web UI launchers for standalone laptop/workstation use.
- Local launcher startup checks for Python runtime, required dependencies, core modules, target/profile config, Web UI assets, output directory, and SQLite job-store readiness.
- Web UI startup and local-server-controls panel with dependency checks, quick-start actions, runtime options, refresh checks, and loopback launcher-mode **Stop local server** control.
- Docker-first AI-agent lab with deterministic mock agent, Docker target config, safety profile, and smoke tooling.
- React target-management workspace with target search/filtering, readiness metrics, validation, authorisation checklist, scan creation controls, and recent job refresh.
- WebUI assistant backend API with CSRF-protected chat requests, server-side model controls, and React model/temperature/instruction controls.
- Expanded real-environment target templates for Anthropic Claude, Google Gemini, Cohere, Ollama, vLLM, LocalAI, Pinecone/LangChain RAG, LangGraph, CrewAI, LiteLLM, Portkey, and AWS Bedrock gateway patterns.
- Future OIDC/JWT authentication implementation plan under `docs/future-plans/`.
- Regression tests that ensure Docker WebUI publishing stays loopback-only and removed archival docs are not re-linked.
- README prerequisites for Docker, launcher, source/package, wheel-build, and WebUI development run paths.
- WebUI visual alignment utilities and regression coverage for icon/text wrapping in the header, cards, and target workspace.
- `docs/USER_GUIDE.md` with an end-to-end operating guide for startup, clean-state behaviour, target setup, scan execution, finding review, evidence, and safe operation.
- Regression tests that prevent reintroducing WebUI dummy data and verify the user guide remains linked.

### Changed

- Security policy and safety model now explicitly describe Agent Lab as an experimental local-lab capability that requires local Docker build/run access.
- Dockerfile and Compose configuration now prepare Agent Lab import roots and host gateway connectivity for local LLM providers.
- WebUI Project Importer now opens the Agent Lab workflow.
- Web UI styling now honours the user's system light/dark appearance preference through `prefers-color-scheme`.
- Project license changed from MIT to Apache License 2.0.
- Package metadata now declares `Apache-2.0`, includes license files, PyPI classifiers, project URLs, keywords, and a release extra for package builds.
- Package metadata validation now checks PyPI publishing metadata and release extras.
- Documentation now consistently describes VulnoraIQ as a Docker-first, self-hosted laptop/workstation/internal-server application for authorised AI assessment work.
- Current-scope readiness items are now consistently marked **Complete** for the self-hosted/internal assessment scope.
- README, docs index, deployment guide, security policy, implementation status, readiness scorecard, backlog, release checklist, assurance, runbook, incident response, GenAI readiness plan, and Agentic Applications readiness plan were aligned to the same product positioning and completion vocabulary.
- Local standalone launcher mode is documented as a loopback-only convenience path, separate from the hardened hosted/production `vulnoraiq-web` path.
- Docker Compose now publishes the WebUI only on host loopback through `127.0.0.1:8787:8787` for the default local lab.
- WebUI docs now identify the React console as the supported UI and mark the legacy static console direction as superseded.
- `vulnoraiq-web` now starts the assistant-enabled hosted WebUI wrapper.
- Release packaging now rebuilds React assets before packaging and publishes final release bundles from a signing/attestation job.
- README and SECURITY were rewritten to reflect the current loopback-local, self-hosted internal scope.
- WebUI header, target manager, KPI cards, action buttons, and asset cards now use responsive alignment/wrapping rules so icons and labels stay together across narrow layouts.
- WebUI overview/workspace state now comes from backend scans only; clean installs show zero/empty state and previously run scans are loaded from `/api/scans`.

### Fixed

- Browser ZIP upload is wired to the Agent Lab archive import endpoint.
- Web UI catalog toolbar overflow where the `Showing ... options` badge could clip into the neighbouring panel in narrow columns.
- `scripts/run_scan.py` jobs-show typing issue that could fail `mypy` by reusing a loop variable for an optional job lookup.
- Stale documentation index entries that pointed readers toward superseded planning notes.
- WebUI icon/text placement issues caused by fixed-width target panes, non-wrapping button labels, and long target/job labels.

### Removed

- Superseded archival WebUI and Docker planning notes whose useful content is now covered by the current README, Docker, deployment, WebUI, and future-plan docs.
- WebUI mock/demo data module and fallback dashboard/assets/findings so clean startup no longer displays dummy information.

### Notes

- VulnoraIQ findings remain framework evidence requiring human review.
- Experimental Agent Lab imports and runs real operator-provided code. Review imported source and generated evidence before treating results as confirmed.
- This release does not claim certified VAPT-grade assurance or independently validated real-environment GenAI detection coverage.
- Launcher and default Docker Compose modes are intended for local laptop/workstation use only; exposed or shared deployments must use production mode with auth enabled and production configuration validation.
- Platform release artifacts use native formats where practical: Windows `.zip`, Linux `.tar.gz`, and macOS `.dmg`.
- Release packages include checksums and GitHub artifact attestations by default; detached GPG signatures are produced when signing secrets are configured.
- Native OS certificate-signed installers remain future maturity items.
- Direct OIDC/JWT remains future work and is not required for current local single-user use.
- PyPI publication is opt-in and should be tested on TestPyPI before publishing to PyPI.

## [0.2.0] - 2026-06-22

### Added

- Production startup validation.
- Trusted reverse-proxy identity auth mode.
- Structured audit logging with request correlation IDs.
- Prometheus-format metrics endpoint protected by default.
- SQLite backup and restore scripts.
- Docker Compose production-like environment.
- Scan concurrency limits.
- Container smoke test script.
- Production readiness scorecard, runbook, incident response, release checklist, migration guide, and assessment assurance docs.
- Dependency checks in CI.
- OWASP-to-MITRE ATLAS planning crosswalk and mapping metadata validator.
- GenAI security implementation planning docs.
- Agentic Applications security implementation planning docs.
- OWASP source document review index.
- Source-confirmed GenAI Data Security category extraction for `DSGAI01–DSGAI21`.
- Source-confirmed OWASP Top 10 for Agentic Applications category extraction for `ASI01–ASI10`.

### Changed

- Version bumped to 0.2.0.
- Auth, CSRF, rate limiting, security headers, proxy IP resolution, SQLite persistence, HTTP errors, configuration output, metrics, and deployment docs were hardened for the self-hosted application model.
- Production readiness docs were updated for self-hosted internal scope.
- README, SECURITY.md, and docs index were rewritten for the `0.2.0` self-hosted production posture.
- `docs/genai/` and `docs/agentic/` were updated from placeholder planning IDs to source-confirmed ranges.
- Active LLM oracle/check configs now include OWASP-to-ATLAS mapping metadata.

### Fixed

- CSRF expiry test stability.
