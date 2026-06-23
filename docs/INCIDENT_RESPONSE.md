# VulnoraIQ Incident Response Plan

This plan covers VulnoraIQ `0.2.0` self-hosted laptop/server deployments.

> **Scope:** These procedures assume a local or internal-server deployment using token auth or trusted reverse-proxy identity, SQLite persistence, structured audit logs, reverse-proxy/TLS controls where needed, and working-starter GenAI Security readiness validation. Adapt contacts, escalation channels, legal process, and SIEM tooling to your organisation.

## Severity definitions

| Severity | Description | Initial response target | Escalation |
| --- | --- | --- | --- |
| Critical | Auth bypass, confirmed token misuse, artifact/report exposure, arbitrary file access, runtime compromise, corrupted production DB with no clean backup | Immediate | Security lead + engineering lead + legal/comms if data exposure |
| High | Suspected auth abuse, trusted-proxy spoofing attempt, repeated CSRF/rate-limit abuse, exploitable dependency issue, GenAI readiness regression that affects release claims | < 1 hour | Security + engineering |
| Medium | Misconfiguration, failed backup, limited DoS, missing expected audit/metric signal, GenAI manifest/docs drift | < 4 hours | Engineering owner |
| Low | Documentation issue, safe-demo-only issue, non-sensitive monitoring gap | Next sprint | Repo maintainer |

## Evidence sources

Use the following first:

- `vulnoraiq.audit` JSON-line audit logs
- application logs from Docker Compose or systemd
- `/metrics` counters, especially auth/CSRF/rate-limit/internal-error counters
- SQLite job store `/data/jobs.db`
- reports/artifacts under `/data/reports`
- GenAI readiness assets: `benchmarks/fixtures/genai/scenarios.yaml`, `core/genai_evaluators.py`, `scripts/validate_genai_readiness.py`, and `tests/test_genai_readiness_validation.py`
- reverse proxy logs and network-control logs, if deployed
- GitHub Actions logs for CI/security pipeline failures

Audit logs should include `timestamp`, `event`, `request_id`, `user`, `role`, `authenticated`, `client_ip`, `method`, `path`, `status`, and `detail`.

## Immediate containment checklist

For any high or critical incident:

1. Preserve logs and affected SQLite DB/report artifacts.
2. Restrict network access at the reverse proxy if exposure is suspected.
3. Rotate `VULNORAIQ_ADMIN_TOKEN`, analyst token, viewer token, and any target API tokens if they may be exposed.
4. Confirm `VULNORAIQ_ENV=production` and `VULNORAIQ_AUTH_ENABLED=true` are active.
5. Run `python scripts/validate_runtime_production_config.py` after any config change.
6. Run `python scripts/validate_genai_readiness.py` if GenAI docs, manifests, evidence fields, or release claims may be affected.
7. Take a SQLite backup before destructive changes.
8. Open a private tracking issue or GitHub Security Advisory if the framework itself is affected.

## Incident types

### 1. Auth token leak

**Detection**

- Secret scanning detects `VULNORAIQ_ADMIN_TOKEN` or another token.
- Token appears in commit history, logs, screenshots, tickets, or chat.
- Audit logs show unexpected successful requests using a role token.

**Containment**

1. Rotate the affected token immediately.
2. Restart the service or redeploy with the new secret.
3. Verify old token fails with HTTP `401`.
4. Review audit logs for the exposure window.
5. If token was committed, purge it from history using your organisation's approved process and invalidate all exposed copies.

**Recovery**

- Re-run runtime validation.
- Confirm `/api/scans`, `/api/csrf-token`, and `/metrics` require valid auth.
- Add regression or secret-scanning rules if the leak bypassed existing controls.

### 2. Unauthorised access attempt

**Detection**

- Repeated `auth_failure` or `authz_failure` audit events.
- High `vulnoraiq_auth_failures_total` or `vulnoraiq_authz_failures_total`.
- Reverse proxy logs show unusual endpoint enumeration.

**Containment**

1. Block offending IP/CIDR at reverse proxy or firewall.
2. Rotate tokens if a valid token may have been guessed or reused.
3. Tighten proxy rate limits.
4. Verify trusted-proxy headers are accepted only from configured CIDRs.

**Recovery**

- Review logs for successful access.
- Verify no unauthorised scan was created or artifact downloaded.
- Add monitoring alerts for repeated `auth_failure` / `authz_failure`.

### 3. Trusted-proxy identity spoofing attempt

**Detection**

- Requests include trusted identity headers from untrusted IPs.
- Unexpected `proxy:<username>` actor appears in audit logs.

**Containment**

1. Confirm `VULNORAIQ_TRUST_PROXY_HEADERS=true` is set only when behind a trusted reverse proxy.
2. Confirm `VULNORAIQ_TRUSTED_PROXY_CIDRS` includes only the proxy network.
3. Configure the reverse proxy to strip identity headers from all inbound client requests before setting its own.
4. Temporarily switch to `VULNORAIQ_AUTH_MODE=token` if proxy identity is suspect.

**Recovery**

- Re-run trusted proxy regression tests.
- Review role assignments and audit logs for affected users.

### 4. CSRF failure spike

**Detection**

- Elevated `vulnoraiq_csrf_failures_total`.
- Audit events `csrf_failure` on `POST /api/scans`.

**Containment**

1. Confirm the Web UI fetches `/api/csrf-token` before scan creation.
2. Check `VULNORAIQ_CSRF_TOKEN_TTL` is positive and appropriate.
3. Block suspicious clients if failures appear malicious.

**Recovery**

- Confirm valid token flow works.
- Add alerting on CSRF failures above baseline.

### 5. Rate-limit spike or scan queue exhaustion

**Detection**

- HTTP `429` responses.
- `rate_limit_exceeded` or `scan_queue_full` audit events.
- Elevated `vulnoraiq_rate_limit_exceeded_total` or `vulnoraiq_scan_queue_full_total`.

**Containment**

1. Identify source IPs and authenticated users.
2. Add proxy limits if traffic is abusive.
3. Tune `VULNORAIQ_RATE_LIMIT_MAX`, `VULNORAIQ_RATE_LIMIT_WINDOW`, `VULNORAIQ_MAX_CONCURRENT_SCANS`, and `VULNORAIQ_SCAN_QUEUE_LIMIT` only after confirming capacity.
4. Avoid disabling limits to make tests or demos pass.

**Recovery**

- Confirm active scan count returns to baseline.
- Review whether queue limits need capacity planning updates.

### 6. Report or artifact exposure

**Detection**

- Unexpected `artifact_download` audit event.
- User reports access to an artifact they should not see.
- Report files are found outside the intended `/data/reports` or controlled storage path.

**Containment**

1. Remove external access to the Web UI or artifact path at the proxy.
2. Preserve the affected artifact and logs.
3. Rotate tokens if access may be token-related.
4. Confirm artifact path protections are active.
5. Review `job.outputs` paths in SQLite for unexpected values.

**Recovery**

- Restore or regenerate affected reports if tampered.
- Add tests for the exposure path if a framework bug caused it.
- Follow internal breach-notification policy if sensitive data was exposed.

### 7. Corrupted SQLite store

**Detection**

- SQLite integrity errors.
- Backup validation fails.
- Missing or inconsistent jobs/events.

**Containment**

1. Stop the service.
2. Copy the affected DB for forensic review.
3. Run integrity check.
4. Restore from the latest validated backup.

**Recovery**

```bash
python scripts/restore_sqlite_store.py \
  /data/backups/jobs-YYYYMMDD-HHMMSS.db.gz \
  /data/jobs.db \
  --compressed \
  --validate
```

Restart and verify `/healthz`, `/readyz`, scan history, and artifact download.

### 8. Failed backup or restore

**Detection**

- `backup_sqlite_store.py` exits non-zero.
- Validation reports missing schema, job table, or event table.
- Retention cleanup removes too much or too little.

**Containment**

1. Stop retention cleanup if it is causing data loss.
2. Preserve the failed backup file.
3. Create a fresh backup with `--validate`.
4. Check available disk space and permissions.

**Recovery**

- Restore from a previous known-good backup.
- Document RPO/RTO impact.
- Add monitoring for backup age and validation status.

### 9. Dependency vulnerability

**Detection**

- `pip-audit` reports a vulnerable dependency.
- GitHub Dependabot or security advisory opens an alert.

**Containment**

1. Assess whether the vulnerable package is runtime, dev-only, or unused.
2. Patch or pin a fixed version.
3. Run quality and readiness checks.
4. Update `CHANGELOG.md` if the fix affects users.

### 10. Web UI security bug

Examples:

- auth bypass
- CSRF bypass
- unsafe proxy-header trust
- token leakage in logs
- report/artifact unauthorised access

**Response**

1. Reproduce locally with a failing regression test.
2. Fix the root cause.
3. Run the full readiness gate.
4. Update `SECURITY.md`, `CHANGELOG.md`, and docs if operator action is required.
5. Release a patch or security advisory if exploitable.

### 11. GenAI readiness regression

Examples:

- `scripts/validate_genai_readiness.py` fails on a release branch.
- `DSGAI01–DSGAI21` scenario coverage is missing or incomplete.
- `DSGAI22–DSGAI25` source discrepancy tracking is removed.
- Required GenAI evidence fields drift from docs or reports.
- Docs overstate GenAI coverage beyond working-starter evidence.

**Response**

1. Treat this as a release-blocking documentation/validation incident.
2. Preserve the failing GitHub Actions logs.
3. Fix the scenario manifest, evaluator, tests, or docs.
4. Run:

   ```bash
   python scripts/validate_genai_readiness.py
   pytest tests/test_genai_readiness_validation.py -q
   python scripts/validate_package_metadata.py
   ```

5. Update release notes and assurance docs if wording changed.

## Post-incident review

For medium/high/critical incidents, record:

- timeline
- affected version/commit
- detection source
- root cause
- impact and blast radius
- containment actions
- recovery actions
- tests added
- docs updated
- release/advisory decision

## Validation commands after incident remediation

```bash
ruff check .
mypy .
pytest -q
python -m pip check
pip-audit
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py
python scripts/validate_runtime_production_config.py
python scripts/validate_production_testing_readiness.py \
  --run-functional \
  --output-dir reports/output/production-readiness
```

If Docker is available:

```bash
docker build -t vulnoraiq:incident-fix .
python scripts/container_smoke_test.py
```

## Communication guidance

Do not overclaim assurance in incident communications. Use the project boundary language:

- Self-hosted laptop/server deployment: supported when configured and validated.
- GenAI Security readiness: working starter evidence for controlled internal assessment use.
- Scanner findings: framework evidence requiring human review, not certified VAPT assurance.
