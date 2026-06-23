# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added

- Release-only Windows, Linux, and macOS artifact build workflow triggered by published GitHub Releases or manual dispatch only.
- Platform release package builder for `vulnoraiq-<version>-windows.zip`, `vulnoraiq-<version>-linux.zip`, and `vulnoraiq-<version>-macos.zip`.
- Release artifact documentation in `docs/RELEASE_ARTIFACTS.md`.
- Cross-platform local Web UI launchers for standalone laptop/workstation use:
  - `launch-vulnoraiq-webui.bat`
  - `launch-vulnoraiq-webui.command`
  - `launch-vulnoraiq-webui.sh`
  - `launch-vulnoraiq-webui.py`
- Local launcher startup checks for Python runtime, required dependencies, core modules, target/profile config, Web UI assets, output directory, and SQLite job-store readiness.
- Web UI startup and local-server-controls panel with dependency checks, quick-start actions, runtime options, refresh checks, and loopback launcher-mode **Stop local server** control.
- Quick-start guidance for stopping the Web UI in foreground, background, launcher, Docker, and Docker Compose runs.

### Changed

- Project license changed from MIT to Apache License 2.0.
- Package metadata now declares `Apache-2.0`, and package metadata validation checks the project license file and third-party notice alignment.
- Documentation now consistently describes VulnoraIQ as a self-hosted laptop/workstation/internal-server application for authorised AI assessment work.
- Current-scope readiness items are now consistently marked **Complete** for the self-hosted/internal assessment scope.
- README, docs index, deployment guide, security policy, implementation status, readiness scorecard, backlog, release checklist, assurance, runbook, incident response, GenAI readiness plan, and Agentic Applications readiness plan were aligned to the same product positioning and completion vocabulary.
- Local standalone launcher mode is documented as a loopback-only convenience path, separate from the hardened hosted/production `vulnoraiq-web` path.

### Notes

- VulnoraIQ findings remain framework evidence requiring human review.
- This release does not claim certified VAPT-grade assurance or independently validated real-environment GenAI detection coverage.
- Launcher mode is intended for local laptop/workstation use only; exposed or shared deployments must use production mode with auth enabled and production configuration validation.
- Platform release artifacts are zip packages with platform launchers, not signed native installers.

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
- Ruff import ordering across test files.
- README, implementation status, and hardening backlog maturity claims.
- HTTP error response consistency.
- Scanner exception handling.
- Production listen-address validation reachability.
- `.env.production.example` ignore-rule exception.

### Breaking

- Legacy `webui/server.py` removed.
- JSON job store backend is legacy/dev only; SQLite is default.
- File-based auth is disabled in production mode.
- `VULNORAIQ_ADMIN_TOKEN` is required in production.
- Minimum Python 3.10 required.
- `VULNORAIQ_AUTH_MODE=token` is default; set to `trusted_proxy` for proxy-based identity.

## [0.1.0] - 2026-05-13

### Added

- Initial repository scaffold.
- OWASP LLM Top 10 2025-aligned module structure.
- Core scanner, runner, orchestrator, risk scoring, and results engine.
- RAG, agent, payload, reporting, dashboard, and CI scaffolding.
- Safe demo target and unit tests.
- Policy-as-code and MITRE ATLAS mapping documentation.
