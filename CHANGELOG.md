# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-06-22

### Added

- Production startup validation (`webui/production_checks.py`, `scripts/validate_runtime_production_config.py`)
- Trusted reverse-proxy identity auth mode (`VULNORAIQ_AUTH_MODE=trusted_proxy`)
- Structured JSON-line audit logging with request correlation IDs
- Prometheus `/metrics` endpoint (auth-protected by default)
- SQLite backup and restore scripts (`scripts/backup_sqlite_store.py`, `scripts/restore_sqlite_store.py`)
- Docker Compose production-like environment (`docker-compose.yml`, `.env.production.example`)
- Scan concurrency limits (`VULNORAIQ_MAX_CONCURRENT_SCANS`, `VULNORAIQ_SCAN_QUEUE_LIMIT`)
- Container smoke test script
- Production readiness scorecard, runbook, incident response, release checklist, migration guide, assessment assurance docs
- Dependency checks (pip-audit, pip check) in CI
- Regression tests for trusted proxy identity mode (spoofed headers, CIDR enforcement, role mapping, permissions)
- Validator checks: listen_address_safe reachability, no SaaS overclaim in README, SQLite/WAL persistence claim, public/SaaS limitations documented, assessment assurance doc discoverable

### Changed

- Version bumped to 0.2.0
- Auth: env-driven token auth with hmac constant-time comparison, production-mode validation, trusted proxy identity support
- CSRF: per-session tokens with TTL/cleanup
- Rate limiting: configurable window/max, periodic store cleanup
- Security headers: CSP, HSTS (conditional), X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy on every response
- Proxy IP resolution with trusted CIDR support
- SQLite job store as default (WAL mode, schema versioning)
- HTTP error handling standardized with correct status codes and security headers
- Config endpoint is role-aware (admin sees full config, viewers see safe subset)
- Artifact download hardened against path traversal
- Metrics counters for auth, CSRF, rate limit, scan, artifact events
- Deployment guide with production checklist, runbook, incident response docs
- **listen_address_safe** added to `_ALL_CHECKS` (was unreachable); 4 new `validate_all` tests for 127.0.0.1/0.0.0.0+proxy/0.0.0.0+no-proxy/invalid-CIDR scenarios
- Production readiness scorecard updated: rating scale scoped to controlled internal; stale "no trusted_proxy test coverage" claim removed
- PRODUCTION_HARDENING_BACKLOG.md: added "Notes on scoring" clarifying 10/10 gate vs 8.4/10 scorecard average; remaining gaps section updated
- RUNBOOK.md: added disclaimer that it is a template requiring adaptation
- RELEASE_CHECKLIST.md: version/date updated
- README.md: added ASSESSMENT_ASSURANCE.md link to maturity banner
- **`_ALL_CHECKS` in `production_checks.py`**: `listen_address_safe` entry added so the check is actually reachable

### Fixed

- CSRF test expiry now uses direct store manipulation instead of unreliable monkeypatch
- Ruff import ordering across test files
- README, IMPLEMENTATION_STATUS, PRODUCTION_HARDENING_BACKLOG maturity claims updated
- HTTP error responses now include security headers and request IDs
- Scanner exceptions no longer leak internals
- `listen_address_safe` was defined but never added to `_ALL_CHECKS` — now reachable via `validate_all()`
- `.env.production.example` excluded by `.gitignore` `.env.*` pattern — added negation rule

### Security

- Production mode fails closed on unsafe config
- Demo tokens rejected in production
- Internal admin token disabled in production
- Known demo credentials blocked in production
- Oversized requests return 413, not 400
- Malformed JSON returns 400
- Path traversal blocked on artifact download
- SQLite path validated against ephemeral locations
- Rate limit, request body, CSRF TTL validated as sane/positive
- Audit logs never include tokens, CSRF tokens, request bodies, or secrets
- **listen_address_safe**: listening on 0.0.0.0/:: without proxy trust fails production checks

### Breaking

- Legacy `webui/server.py` removed (use `webui/hosted_server.py` only)
- JSON job store backend is legacy/dev only; SQLite is default
- File-based auth is disabled in production mode
- `VULNORAIQ_ADMIN_TOKEN` is required in production (min 20 characters)
- Minimum Python 3.10 required
- `VULNORAIQ_AUTH_MODE=token` is default; set to `trusted_proxy` for proxy-based identity

## [0.1.0] - 2026-05-13

### Added

- Initial enterprise-ready repository scaffold.
- OWASP LLM Top 10 2025-aligned module structure.
- Core scanner, runner, orchestrator, risk scoring, and results engine.
- RAG, agent, payload, reporting, dashboard, and CI scaffolding.
- Safe demo target and unit tests.
- Policy-as-code and MITRE ATLAS mapping documentation.
