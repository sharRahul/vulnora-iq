# Deployment Guide

This guide describes the supported VulnoraIQ `0.2.0` deployment posture.

> **Scope:** VulnoraIQ `0.2.0` has passed the controlled internal enterprise production-readiness gate. It is suitable for single-organisation/internal deployment when configured with the controls below. GenAI Security readiness is working starter coverage for controlled internal assessment use. VulnoraIQ is **not** public internet-facing SaaS or multi-tenant ready without additional controls such as OIDC/SSO, tenant isolation, HA persistence, distributed rate limiting, WAF/CDN/DDoS protection, and external testing.

## Quick start: local development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]

# Safe local CLI demo
vulnoraiq --target demo --profile baseline

# Local Web UI, bound to localhost
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Health checks:

```bash
curl http://127.0.0.1:8787/healthz
curl http://127.0.0.1:8787/readyz
```

The demo target is safe and local. Configured non-demo targets require explicit authorisation.

## Quick start: production-mode validation

Production mode fails closed when unsafe runtime configuration is detected.

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

Production-mode validation checks:

- auth is enabled
- admin token is set and at least 20 characters
- known demo/default tokens are rejected
- internal development admin token is disabled
- JSON job store is rejected in production
- SQLite path is not obviously ephemeral or unsafe
- output directory is writable
- config directory is readable
- trusted proxy CIDRs are valid when proxy headers are enabled
- binding to `0.0.0.0` or `::` without trusted proxy configuration fails
- rate-limit, request-body, and CSRF TTL values are sane
- audit logging level is valid

## Release and assessment readiness validation

Run these after checkout, before a release candidate, and after changing docs, mappings, or GenAI scenario assets:

```bash
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py
python scripts/validate_runtime_production_config.py
```

The GenAI readiness validator checks:

- `DSGAI01–DSGAI21` source-confirmed scenario coverage
- `DSGAI22–DSGAI25` source-discrepancy preservation
- secure, vulnerable, ambiguous, and edge-case fixture coverage
- required GenAI evidence fields
- MITRE ATLAS tactic ID format
- GenAI readiness documentation alignment

## Container deployment

Build and run with persistent data:

```bash
docker build -t vulnoraiq:0.2.0-rc .
docker run --rm -p 8787:8787 \
  -v vulnoraiq-data:/data \
  -e VULNORAIQ_ENV=production \
  -e VULNORAIQ_AUTH_ENABLED=true \
  -e VULNORAIQ_ADMIN_TOKEN="$(openssl rand -hex 32)" \
  -e VULNORAIQ_JOB_STORE_BACKEND=sqlite \
  -e VULNORAIQ_JOB_STORE_PATH=/data/jobs.db \
  -e VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports \
  vulnoraiq:0.2.0-rc
```

The container runs as a non-root user, uses `/data` for SQLite DB and reports, exposes port `8787`, and includes a `/healthz` healthcheck.

## Docker Compose

```bash
cp .env.production.example .env.production
# Edit .env.production and replace every placeholder token before starting.
docker compose up --build
```

Do not commit real `.env.production` files. Commit only `.env.production.example` with placeholders.

## Authentication

Auth is **enabled by default** and fail-closed. Anonymous requests to protected routes receive HTTP `401`.

### Token auth, default mode

```bash
export VULNORAIQ_AUTH_MODE=token
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="$(openssl rand -hex 32)"
export VULNORAIQ_ANALYST_TOKEN="$(openssl rand -hex 32)"
export VULNORAIQ_VIEWER_TOKEN="$(openssl rand -hex 32)"
```

Clients pass the token via the `X-VulnoraIQ-Token` header. Tokens are compared using constant-time comparison.

| Role | Permissions |
| --- | --- |
| `viewer` | view scans, download artifacts |
| `analyst` | viewer + start demo scans |
| `admin` | analyst + start configured-target scans, manage runtime |

### Trusted reverse-proxy identity mode

Use this only when an upstream proxy performs authentication and strips spoofed identity headers from untrusted clients.

```bash
export VULNORAIQ_AUTH_MODE=trusted_proxy
export VULNORAIQ_TRUST_PROXY_HEADERS=true
export VULNORAIQ_TRUSTED_PROXY_CIDRS="127.0.0.1/32,::1/128"
```

Supported identity headers:

| Header | Purpose |
| --- | --- |
| `X-Authenticated-User` | required username |
| `X-Authenticated-Email` | informational email |
| `X-Authenticated-Groups` | informational group list |
| `X-VulnoraIQ-Role` | `viewer`, `analyst`, or `admin`; unknown roles default to viewer |

Spoofed identity headers from untrusted client IPs are ignored.

## Proxy IP trust

By default, VulnoraIQ does **not** trust `X-Forwarded-For`. This prevents client-IP spoofing.

```bash
export VULNORAIQ_TRUST_PROXY_HEADERS=true
export VULNORAIQ_TRUSTED_PROXY_CIDRS="10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
```

The server trusts forwarded client IPs only when the direct connection source is within a trusted CIDR.

## Web UI endpoints

| Endpoint | Auth | Purpose |
| --- | --- | --- |
| `/` | required | static Web UI |
| `/healthz` | public | liveness |
| `/readyz` | public | readiness based on target/profile config |
| `/metrics` | required by default | Prometheus metrics |
| `/api/csrf-token` | required | CSRF token for state-changing requests |
| `/api/config` | required | role-aware safe configuration view |
| `/api/scans` | required | list or create scans |
| `/api/scans/<id>` | required | scan details |
| `/api/scans/<id>/events` | required | Server-Sent Events stream |
| `/api/scans/<id>/artifact/<name>` | required | artifact download |

`POST /api/scans` requires `X-CSRF-Token`.

## Security features

### Request size and parsing

- `VULNORAIQ_MAX_REQUEST_BODY` defaults to `10485760` bytes / 10 MB.
- Oversized requests return HTTP `413`.
- Invalid `Content-Length` and malformed JSON return HTTP `400`.
- API errors are JSON responses with security headers.

### CSRF

- Tokens are scoped to the authenticated principal, or client IP for anonymous development flows.
- `VULNORAIQ_CSRF_TOKEN_TTL` defaults to `300` seconds.
- Expired tokens are cleaned periodically.

### Rate limiting and scan concurrency

```bash
export VULNORAIQ_RATE_LIMIT_WINDOW=60
export VULNORAIQ_RATE_LIMIT_MAX=60
export VULNORAIQ_MAX_CONCURRENT_SCANS=5
export VULNORAIQ_SCAN_QUEUE_LIMIT=20
```

The application rate limiter is in-memory and per-process. For public exposure or multi-instance deployment, enforce rate limiting at the reverse proxy/WAF layer and use a shared rate-limit backend in a future architecture.

## Persistence

SQLite is the default and production-supported backend for controlled internal deployment.

```bash
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
```

SQLite settings applied by the job store:

- WAL mode
- foreign keys enabled
- busy timeout
- schema version table
- `jobs` and `events` tables

JSON persistence is legacy/development only, and production validation rejects it.

## Audit logging

Audit events are emitted as JSON lines on the `vulnoraiq.audit` logger. Audit logs must not include auth tokens, CSRF tokens, request bodies, secrets, or full report contents.

Recommended operations:

- ship logs to SIEM using your standard log shipper
- retain audit logs according to internal policy
- alert on repeated auth failures, CSRF failures, rate-limit spikes, unsafe artifact access attempts, and scan queue saturation

## Reverse proxy and TLS

The built-in HTTP server should run behind a reverse proxy for controlled enterprise deployment. See the runbook for nginx/Caddy validation commands and certificate checks.

## Backup and restore

```bash
python scripts/backup_sqlite_store.py /data/jobs.db /data/backups/jobs-$(date +%Y%m%d-%H%M%S).db --compress --validate --retention 90
python scripts/restore_sqlite_store.py /data/backups/jobs-YYYYMMDD-HHMMSS.db.gz /tmp/vulnoraiq-restore-test.db --compressed --validate
```

## GenAI Security deployment notes

GenAI readiness assets are repository assets, not runtime secrets:

- scenario manifest: `benchmarks/fixtures/genai/scenarios.yaml`
- evaluator suite: `core/genai_evaluators.py`
- readiness validator: `scripts/validate_genai_readiness.py`
- tests: `tests/test_genai_readiness_validation.py`

Run the GenAI validator before release and after modifying GenAI docs, scenario coverage, evidence fields, or source discrepancy tracking. The validator passing means the working-starter gate is consistent; it does not prove production-validated real-world GenAI detection assurance.
