# VulnoraIQ Production Runbook

This runbook is for VulnoraIQ `0.2.0` self-hosted laptop/server deployments.

> **Scope:** adapt paths, hostnames, secret-management steps, reverse proxy, and backup destinations to your environment. VulnoraIQ `0.2.0` is intended to run as a local or self-hosted internal application for authorised assessment work. GenAI Security coverage is working starter evidence for controlled internal assessment use, not certified assurance.

## 1. Service management

### Start service: Docker Compose

```bash
cp .env.production.example .env.production
# Edit .env.production and replace placeholders.
docker compose up -d --build
```

### Start service: direct runtime

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="replace-with-strong-token-min-20-chars"
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
export VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports

python scripts/validate_runtime_production_config.py
vulnoraiq-web --host 127.0.0.1 --port 8787
```

### Stop / restart service

```bash
# Foreground terminal run
# Press Ctrl+C in the terminal where vulnoraiq-web is running.

# Background direct run on port 8787
lsof -ti :8787 | xargs kill

# Docker Compose
docker compose down
docker compose restart

# systemd
sudo systemctl stop vulnoraiq
sudo systemctl restart vulnoraiq
sudo systemctl status vulnoraiq --no-pager
```

## 2. Health, readiness, and metrics

```bash
curl -f http://127.0.0.1:8787/healthz
curl -f http://127.0.0.1:8787/readyz
curl -H "X-VulnoraIQ-Token: $VULNORAIQ_ADMIN_TOKEN" http://127.0.0.1:8787/metrics
```

Key metrics to monitor:

- `vulnoraiq_up`
- `vulnoraiq_auth_failures_total`
- `vulnoraiq_authz_failures_total`
- `vulnoraiq_csrf_failures_total`
- `vulnoraiq_rate_limit_exceeded_total`
- `vulnoraiq_scans_created_total`
- `vulnoraiq_scans_completed_total`
- `vulnoraiq_scans_failed_total`
- `vulnoraiq_active_scans`
- `vulnoraiq_scan_queue_full_total`
- `vulnoraiq_internal_errors_total`

## 3. Logs and audit events

```bash
docker compose logs -f --tail=100
sudo journalctl -u vulnoraiq -n 100 -f
```

Audit events are JSON lines emitted by the `vulnoraiq.audit` logger. Audit logs must not contain tokens, CSRF tokens, request bodies, secrets, or full report contents.

## 4. Runtime and readiness validation

Run before starting or after changing environment variables, docs, mappings, GenAI scenarios, or release assets:

```bash
python scripts/validate_runtime_production_config.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_package_metadata.py
python scripts/validate_production_testing_readiness.py
```

Important production checks:

- auth enabled
- admin token set and strong enough
- no demo/default production token
- SQLite backend in production
- writable output path
- readable config path
- trusted proxy CIDRs valid when enabled
- `0.0.0.0` / `::` binding fails unless trusted proxy config is present
- sane rate limit, request body, and CSRF TTL values

Important GenAI checks:

- `DSGAI01–DSGAI21` source-confirmed categories are covered
- `DSGAI22–DSGAI25` source discrepancy remains tracked
- secure, vulnerable, ambiguous, and edge-case fixture coverage is present
- required GenAI evidence fields are present
- MITRE ATLAS tactic IDs are valid
- GenAI readiness docs remain aligned

## 5. Token rotation

1. Generate a new token:

   ```bash
   openssl rand -hex 32
   ```

2. Update the secret source or runtime env var, for example `VULNORAIQ_ADMIN_TOKEN`.
3. Restart the service.
4. Verify old token is rejected and new token works.
5. Review audit logs for failed use of the old token.

## 6. Backup and restore

### Create SQLite backup

```bash
mkdir -p /data/backups
python scripts/backup_sqlite_store.py \
  /data/jobs.db \
  /data/backups/jobs-$(date +%Y%m%d-%H%M%S).db \
  --compress \
  --validate \
  --retention 90
```

### Restore SQLite backup

```bash
sudo systemctl stop vulnoraiq || docker compose down
cp /data/jobs.db /data/jobs.db.before-restore-$(date +%Y%m%d-%H%M%S)
python scripts/restore_sqlite_store.py \
  /data/backups/jobs-YYYYMMDD-HHMMSS.db.gz \
  /data/jobs.db \
  --compressed \
  --validate
sudo systemctl start vulnoraiq || docker compose up -d
curl -f http://127.0.0.1:8787/healthz
curl -f http://127.0.0.1:8787/readyz
```

Run a restore drill once per release candidate and record the result in the release checklist.

## 7. Clear stuck scans

There is no separate job-management CLI yet. Use this controlled manual procedure:

1. Stop the service.
2. Back up `/data/jobs.db`.
3. Inspect stuck rows.
4. If a job is confirmed stale, mark failed.
5. Restart the service and verify `/api/scans`.

## 8. Reverse proxy and TLS checks

Use these checks when running on an internal server behind nginx or Caddy:

```bash
sudo nginx -t
caddy validate --config /etc/caddy/Caddyfile
curl -f https://vulnoraiq.example.com/healthz
```

Certificate expiry:

```bash
echo | openssl s_client -servername vulnoraiq.example.com \
  -connect vulnoraiq.example.com:443 2>/dev/null | \
  openssl x509 -noout -dates
```

## 9. Troubleshooting

| Symptom | Check | Likely resolution |
| --- | --- | --- |
| Service exits on startup | `docker compose logs` or `journalctl -u vulnoraiq` | Run `scripts/validate_runtime_production_config.py`; fix failed production check |
| `401 authentication required` | Token header missing or wrong | Send `X-VulnoraIQ-Token`; rotate/regenerate token if needed |
| `403 forbidden` | Role lacks permission or CSRF missing | Use admin/analyst token as appropriate; fetch `/api/csrf-token` before POST |
| `413 request too large` | Body exceeds `VULNORAIQ_MAX_REQUEST_BODY` | Reduce request size or raise limit within production validation bounds |
| `429 rate limit exceeded` | IP exceeded app rate limit | Check client retry behaviour; tune env vars; add proxy limits where needed |
| `scan queue at capacity` | Too many active/queued scans | Tune `VULNORAIQ_MAX_CONCURRENT_SCANS` / `VULNORAIQ_SCAN_QUEUE_LIMIT` or wait |
| `/metrics` returns 401 | Metrics auth required | Add `X-VulnoraIQ-Token` or intentionally disable auth only in a protected monitoring network |
| Ready check returns 503 | Targets/profiles failed to load | Check `VULNORAIQ_CONFIG_DIR`, `config/targets.yaml`, and `config/attack_profiles.yaml` |
| SQLite error | DB missing, corrupted, or not writable | Check `/data` permissions; run backup/restore validation |
| Artifacts return 404 | Report path missing or job incomplete | Confirm job status and `/data/reports` persistence |
| GenAI readiness validator fails | Scenario manifest, evidence fields, docs, or source discrepancy drifted | Fix `benchmarks/fixtures/genai/scenarios.yaml`, `docs/genai/`, or validator tests |

## 10. Upgrade procedure

1. Review `CHANGELOG.md`, `docs/MIGRATION.md`, `docs/genai/PRODUCTION_READINESS_PLAN.md`, and `docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md`.
2. Back up SQLite DB.
3. Pull or build the new image.
4. Run validation commands:

   ```bash
   ruff check .
   mypy .
   pytest -q
   python scripts/validate_package_metadata.py
   python scripts/validate_owasp_atlas_mappings.py
   python scripts/validate_genai_readiness.py
   python scripts/validate_production_testing_readiness.py
   ```

5. Start the release candidate.
6. Verify `/healthz`, `/readyz`, `/metrics`, Web UI auth, scan creation, artifact download, backup, restore, and GenAI readiness validation.
7. Monitor logs and metrics for at least one hour.

## 11. Rollback procedure

1. Stop the service.
2. Restore the previous image/tag or code revision.
3. Restore the pre-upgrade SQLite backup if schema/data changed.
4. Start the previous version.
5. Verify `/healthz`, `/readyz`, scan history, artifacts, and release validators.
6. Document the rollback reason in `CHANGELOG.md` or release notes.

## 12. Reference

| Artifact | Typical path |
| --- | --- |
| SQLite job store | `/data/jobs.db` |
| Reports/artifacts | `/data/reports` |
| Backups | `/data/backups` |
| Production env file | `.env.production` or secret-manager injected env |
| Example env file | `.env.production.example` |
| GenAI scenario manifest | `benchmarks/fixtures/genai/scenarios.yaml` |

| Variable | Purpose |
| --- | --- |
| `VULNORAIQ_ENV=production` | Enable production validation |
| `VULNORAIQ_ADMIN_TOKEN` | Required admin token |
| `VULNORAIQ_AUTH_MODE` | `token` or `trusted_proxy` |
| `VULNORAIQ_JOB_STORE_BACKEND=sqlite` | Production persistence backend |
| `VULNORAIQ_JOB_STORE_PATH` | SQLite path |
| `VULNORAIQ_WEB_OUTPUT_ROOT` | Report/artifact output path |
| `VULNORAIQ_TRUST_PROXY_HEADERS` | Trust proxy headers when enabled |
| `VULNORAIQ_TRUSTED_PROXY_CIDRS` | Allowed proxy source networks |
| `VULNORAIQ_METRICS_AUTH_REQUIRED` | Protect `/metrics`; default true |

## 13. Escalation

Use [`INCIDENT_RESPONSE.md`](INCIDENT_RESPONSE.md) for security events. Escalate immediately for suspected token leak, access-control failure, report exposure, repeated rate-limit spikes, scan queue exhaustion, corrupted SQLite store, dependency issue affecting runtime security, or GenAI readiness regression on a release branch.
