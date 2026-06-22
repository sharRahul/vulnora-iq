# VulnoraIQ Production Runbook

> **Note:** This runbook is a template that must be adapted to your specific deployment environment (container orchestrator, reverse proxy, backup destination paths, monitoring stack, etc.). The commands and paths shown are illustrative; replace placeholders like `/path/to/vulnoraiq`, `/var/log/vulnoraiq/`, and example hostnames with your actual values. See [`DEPLOYMENT.md`](DEPLOYMENT.md) for the production checklist and [`INCIDENT_RESPONSE.md`](INCIDENT_RESPONSE.md) for security incident procedures.

## 1. Service Management

### Start service
```bash
# Docker
docker compose up -d

# Systemd (Linux)
sudo systemctl start vulnoraiq

# Direct (binary)
/path/to/vulnoraiq serve --config /etc/vulnoraiq/prod.yml
```

### Stop service
```bash
# Docker
docker compose down

# Systemd
sudo systemctl stop vulnoraiq

# Direct (graceful)
kill -SIGTERM $(pgrep vulnoraiq)
```

### Restart service
```bash
# Docker
docker compose restart

# Systemd
sudo systemctl restart vulnoraiq
```

### Check health
```bash
curl -f http://localhost:8080/healthz
# Expect: 200 OK with JSON body: {"status":"healthy"}
```

### Check readiness
```bash
curl -f http://localhost:8080/readyz
# Expect: 200 OK when all dependencies (DB, queue) are reachable
```

### Check logs
```bash
# Docker
docker compose logs -f --tail=100

# Systemd journal
sudo journalctl -u vulnoraiq -n 100 -f

# Direct (log file)
tail -f /var/log/vulnoraiq/app.log
```

### Rotate secrets
```bash
# Trigger manual rotation (updates API keys, JWTs, and DB credentials)
/path/to/vulnoraiq rotate-secrets --config /etc/vulnoraiq/prod.yml

# Verify rotation took effect
curl -f http://localhost:8080/healthz
```

### Create backup
```bash
# Full backup (DB + config + scan data)
/path/to/vulnoraiq backup create \
  --output /var/backups/vulnoraiq/backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  --config /etc/vulnoraiq/prod.yml

# PostgreSQL-only backup
pg_dump -h localhost -U vulnoraiq -d vulnoraiq \
  -F c -f /var/backups/vulnoraiq/db-$(date +%Y%m%d-%H%M%S).dump
```

### Restore backup
```bash
# Full restore
/path/to/vulnoraiq backup restore \
  --input /var/backups/vulnoraiq/backup-20260501-120000.tar.gz \
  --config /etc/vulnoraiq/prod.yml

# DB-only restore
pg_restore -h localhost -U vulnoraiq -d vulnoraiq \
  -F c -c /var/backups/vulnoraiq/db-20260501-120000.dump
```

### Clear stuck jobs
```bash
# Force-clear any scans or jobs in 'running' state for > 1 hour
/path/to/vulnoraiq jobs clear-stuck --age 1h --config /etc/vulnoraiq/prod.yml

# Verify no stuck jobs remain
/path/to/vulnoraiq jobs list --status running --config /etc/vulnoraiq/prod.yml
```

### Verify reverse proxy
```bash
# If using nginx
nginx -t

# Check proxy is passing health checks
curl -f -H "Host: vulnoraiq.example.com" http://127.0.0.1:80/healthz

# If using Caddy
caddy validate --config /etc/caddy/Caddyfile
```

### Verify TLS
```bash
# Check certificate expiry
echo | openssl s_client -servername vulnoraiq.example.com \
  -connect vulnoraiq.example.com:443 2>/dev/null | \
  openssl x509 -noout -dates

# Full cipher/chain test
openssl s_client -connect vulnoraiq.example.com:443 -tls1_2
```

### Validate production config
```bash
/path/to/vulnoraiq config validate --config /etc/vulnoraiq/prod.yml
# Must exit 0 with no errors
```

### Upgrade procedure
```bash
# 1. Pull latest image or binary
docker compose pull
# or: sudo apt update && sudo apt upgrade vulnoraiq

# 2. Create backup
/path/to/vulnoraiq backup create --config /etc/vulnoraiq/prod.yml

# 3. Run migrations (automated on start in most setups)
docker compose up -d

# 4. Verify
curl -f http://localhost:8080/healthz && \
  curl -f http://localhost:8080/readyz

# 5. Run smoke test
/path/to/vulnoraiq smoke-test --config /etc/vulnoraiq/prod.yml
```

### Rollback procedure
```bash
# 1. Revert to previous image/tag
docker compose down
docker compose -f docker-compose.yml -f docker-compose.rollback.yml up -d

# 2. Restore database from backup taken before upgrade
pg_restore -h localhost -U vulnoraiq -d vulnoraiq \
  -F c -c /var/backups/vulnoraiq/db-pre-upgrade.dump

# 3. Restart service
docker compose restart

# 4. Verify
curl -f http://localhost:8080/healthz
```

---

## 2. Monitoring

### Health endpoint
| Endpoint | Method | Expected code | Response |
|----------|--------|---------------|----------|
| `/healthz` | GET | 200 | `{"status":"healthy"}` |
| `/healthz` | GET | 503 | `{"status":"unhealthy","reason":"..."}` |

**Check command:**
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/healthz
```

### Readiness endpoint
| Endpoint | Method | Expected code | Response |
|----------|--------|---------------|----------|
| `/readyz` | GET | 200 | `{"status":"ready"}` |
| `/readyz` | GET | 503 | `{"status":"not ready","dependencies":{...}}` |

Dependencies checked: PostgreSQL, Redis/RabbitMQ, S3 storage, license server.

### Metrics endpoint
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/metrics` | GET | Prometheus-format metrics |

**Key metrics to alert on:**
```
vulnoraiq_scans_total
vulnoraiq_scans_failed_total
vulnoraiq_scan_duration_seconds
vulnoraiq_api_requests_total
vulnoraiq_api_request_duration_seconds
vulnoraiq_queue_depth
vulnoraiq_license_days_remaining
process_resident_memory_bytes
process_cpu_seconds_total
```

### Audit log location and format
**Location:** `/var/log/vulnoraiq/audit.log`

**Format (JSON, one line per event):**
```json
{
  "timestamp": "2026-05-01T12:00:00.000Z",
  "actor": "admin@example.com",
  "action": "scan.create",
  "resource": "scan/abc-123",
  "result": "success",
  "client_ip": "10.0.0.1",
  "request_id": "req-xyz-456"
}
```

Rotated daily, retained 90 days via `logrotate`.

### Application log location and format
**Location:** `/var/log/vulnoraiq/app.log`

**Format (JSON, one line per event):**
```json
{
  "timestamp": "2026-05-01T12:00:00.000Z",
  "level": "info",
  "logger": "api",
  "message": "Scan completed",
  "scan_id": "abc-123",
  "duration_ms": 45200,
  "error": null
}
```

Levels: `debug`, `info`, `warn`, `error`, `fatal`.

---

## 3. Troubleshooting

### Service won't start
| Symptom | Check | Resolution |
|---------|-------|------------|
| Port 8080 in use | `netstat -ano \| findstr :8080` | Change port or kill conflicting process |
| DB connection refused | `nc -zv localhost 5432` | Ensure PostgreSQL is running; check `DATABASE_URL` |
| Config parse error | `vulnoraiq config validate` | Fix YAML syntax errors in `prod.yml` |
| Permission denied (Linux) | `ls -la /var/log/vulnoraiq/` | `chown -R vulnoraiq:vulnoraiq /var/log/vulnoraiq/` |
| Docker: container exits immediately | `docker compose logs <service>` | Look for config/migration errors |

### Auth failures
| Symptom | Check | Resolution |
|---------|-------|------------|
| 401 on login | Is user active? | `vulnoraiq users list \| grep user@example.com` |
| 401 on API call | JWT expired? | Re-issue token; verify `JWT_SECRET` not rotated mid-session |
| 403 forbidden | Permission missing? | `vulnoraiq users roles --user user@example.com` |
| OIDC failing | IdP reachable? | `curl -f https://idp.example.com/.well-known/openid-configuration` |

### Rate limiting
| Symptom | Check | Resolution |
|---------|-------|------------|
| 429 Too Many Requests | `grep "rate limit" /var/log/vulnoraiq/app.log` | Increase `RATE_LIMIT_PER_MIN` or add burst capacity |
| Legitimate traffic blocked | Check `X-Forwarded-For` upstream | Ensure reverse proxy sets `X-Forwarded-For` correctly |
| Reset rate limit | — | `vulnoraiq rate-limit reset --key <client_ip> --config /etc/vulnoraiq/prod.yml` |

### Scan failures
| Symptom | Check | Resolution |
|---------|-------|------------|
| Scan stuck in `running` | `vulnoraiq jobs list --status running` | `vulnoraiq jobs clear-stuck --age 1h` |
| Scan fails with timeout | `grep <scan_id> /var/log/vulnoraiq/app.log` | Increase `SCAN_TIMEOUT` env var; check target availability |
| Scanner engine error | `journalctl -u vulnoraiq-scanner` | Restart scanner container; check scanner license |
| OOM during scan | `docker stats`; check `dmesg` for oom-kill | Reduce scan concurrency (`MAX_CONCURRENT_SCANS`) |

### Database corruption
| Symptom | Check | Resolution |
|---------|-------|------------|
| `relation does not exist` | `\dt` in psql | Run migrations: `vulnoraiq db migrate` |
| Unique constraint violations | Check for duplicate PK | Restore from last known-good backup |
| Slow queries / locks | `SELECT * FROM pg_stat_activity WHERE state = 'active'` | `SELECT pg_terminate_backend(pid) WHERE ...` |
| Index corruption | `REINDEX DATABASE vulnoraiq;` | Run `REINDEX` during maintenance window |

### Disk full
| Symptom | Check | Resolution |
|---------|-------|------------|
| 500 errors / write failures | `df -h /var/log/vulnoraiq /var/lib/postgresql` | Remove old archives; increase volume size |
| Audit log too large | `du -sh /var/log/vulnoraiq/audit.log` | Force logrotate: `logrotate -f /etc/logrotate.d/vulnoraiq` |
| Scan data filling disk | `du -sh /var/lib/vulnoraiq/scans/` | Tune `SCAN_DATA_RETENTION_DAYS`; purge old scan artifacts |

---

## 4. Reference

### Default ports
| Service | Port |
|---------|------|
| HTTP API | 8080 |
| HTTPS API | 8443 |
| Metrics (Prometheus scrape) | 9090 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| RabbitMQ (AMQP) | 5672 |
| RabbitMQ (management UI) | 15672 |

### File locations
| Artifact | Path |
|----------|------|
| Production config | `/etc/vulnoraiq/prod.yml` |
| App log | `/var/log/vulnoraiq/app.log` |
| Audit log | `/var/log/vulnoraiq/audit.log` |
| Default data directory | `/var/lib/vulnoraiq/` |
| Scan artifacts | `/var/lib/vulnoraiq/scans/` |
| Backups directory | `/var/backups/vulnoraiq/` |
| TLS certificate | `/etc/vulnoraiq/tls/cert.pem` |
| TLS private key | `/etc/vulnoraiq/tls/key.pem` |
| Docker Compose file | `/opt/vulnoraiq/docker-compose.yml` |
| Systemd unit file | `/etc/systemd/system/vulnoraiq.service` |

### Environment variables
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgres://vulnoraiq:pass@localhost:5432/vulnoraiq` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `AMQP_URL` | `amqp://guest:guest@localhost:5672` | RabbitMQ connection string |
| `JWT_SECRET` | *(required)* | Secret for signing JWTs |
| `JWT_EXPIRY` | `15m` | Access token TTL |
| `REFRESH_TOKEN_EXPIRY` | `7d` | Refresh token TTL |
| `RATE_LIMIT_PER_MIN` | `60` | API rate limit per client IP |
| `MAX_CONCURRENT_SCANS` | `5` | Max simultaneous scans |
| `SCAN_TIMEOUT` | `30m` | Per-scan timeout |
| `SCAN_DATA_RETENTION_DAYS` | `30` | Days to keep scan artifacts |
| `LOG_LEVEL` | `info` | Log level: debug, info, warn, error |
| `LOG_FORMAT` | `json` | Log format: json or text |
| `AUDIT_LOG_ENABLED` | `true` | Enable audit logging |
| `STORAGE_BACKEND` | `local` | Storage: local or s3 |
| `S3_BUCKET` | — | S3 bucket name (if STORAGE_BACKEND=s3) |
| `LICENSE_KEY` | *(required)* | License key for scanner engine |
| `PROMETHEUS_PUSHGATEWAY` | — | Pushgateway URL for metrics push |
| `HEALTH_CHECK_INTERVAL` | `30s` | Interval for dependency health checks |

### Docker commands
```bash
# Build images
docker compose build

# Start all services
docker compose up -d

# Tail logs
docker compose logs -f

# Scale worker count
docker compose up -d --scale worker=4

# Run database migrations explicitly
docker compose run --rm api migrate

# Execute a shell in a running container
docker compose exec api sh

# Restart a single service
docker compose restart api

# Pull latest images
docker compose pull

# Full teardown (includes volumes)
docker compose down -v

# Inspect container health
docker inspect --format '{{json .State.Health}}' vulnoraiq-api-1

# Check resource usage
docker stats --no-stream

# Prune unused resources
docker system prune -f
```
