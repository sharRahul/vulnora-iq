# VulnoraIQ Modern Web UI

The VulnoraIQ Web UI provides a user-friendly console for VAPT specialists to run AI security assessments against configured authorised targets, monitor scan progress in real time, and review completed outputs.

## Start the UI

```bash
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Or run directly from source:

```bash
python -m webui.hosted_server --host 127.0.0.1 --port 8787
```

Open:

```text
http://127.0.0.1:8787
```

## Signing in

VulnoraIQ supports two primary WebUI auth modes:

- `VULNORAIQ_AUTH_MODE=local_admin` for single-user local/Desktop Mode on loopback only.
- `VULNORAIQ_AUTH_MODE=token` for shared/internal or production use with explicit tokens.

In `local_admin` mode, the local operator is resolved as `local-admin` with the `admin`
role and the UI does not require a sign-in token. In `token` mode, the page can load
without a token, but API data and mutating actions require one. The console sends the
token (default header `X-VulnoraIQ-Token`) on every request and attaches a CSRF token
to mutating submissions automatically.

Token mode maps tokens to roles and permissions:

| Token source | Role | Capabilities |
| --- | --- | --- |
| `VULNORAIQ_ADMIN_TOKEN` | admin | view, download, configured scans, full config/targets |
| `VULNORAIQ_ANALYST_TOKEN` | analyst | view, download |
| `VULNORAIQ_VIEWER_TOKEN` | viewer | view and download only |

`VULNORAIQ_AUTH_ENABLED=false` remains a backward-compatible alias for local
single-user admin behavior in non-production environments, but the preferred explicit
setting is `VULNORAIQ_AUTH_MODE=local_admin`. Production/shared deployments should use
`VULNORAIQ_ENV=production`, `VULNORAIQ_AUTH_MODE=token`, and
`VULNORAIQ_ADMIN_TOKEN`.

Use **Sign out** in the top bar to clear a token-mode session.

## User workflow

1. Sign in with an access token (when auth is enabled).
2. Select a target.
3. Select an assessment profile or a single test from the categorised catalog.
4. Confirm authorisation for the configured target.
5. Start the assessment.
6. Watch the progress ring and realtime event timeline.
7. Review the completed executive dashboard.
8. Download presentation-ready outputs.

## Hosted-mode foundations

The hosted server uses:

- `webui/hosted_server.py` for the active `vulnoraiq-web` entry point.
- `webui/auth.py` for local role and permission checks.
- `config/web_users.yaml` for viewer, analyst, and admin role configuration.
- `webui/persistent_jobs.py` for JSON-backed scan job storage.
- `reports/output/webui/jobs.json` as the default persistent job history file.

Static UI assets are served publicly so the console can load, while `/api/*` data
endpoints follow the configured auth mode. Use `local_admin` only for isolated local
loopback operation. Role and token configuration lives in `config/web_users.yaml`
(file-based fallback) or the `VULNORAIQ_*_TOKEN` environment variables (preferred for
token-mode deployments).

## Dashboard sections

The completed scan dashboard shows:

- target and profile summary
- finding count
- highest severity
- policy status
- severity distribution
- policy evaluation results
- finding summaries
- report download links
- persistent scan history

## Realtime progress

The UI uses Server-Sent Events from:

```text
/api/scans/{job_id}/events
```

Events include stage, message, progress percentage, timestamp, and level.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Load the web UI. |
| `GET` | `/api/config` | Return configured targets and profiles. |
| `POST` | `/api/scans` | Start a scan. |
| `GET` | `/api/scans` | List recent scan jobs. |
| `GET` | `/api/scans/{job_id}` | Get job state, events, summary, and outputs. |
| `GET` | `/api/scans/{job_id}/events` | Stream realtime events with SSE. |
| `GET` | `/api/scans/{job_id}/artifact/{name}` | Download generated artifacts. |

## Generated artifacts

Each completed Web UI scan writes artifacts under:

```text
reports/output/webui/{job_id}/
```

Generated artifacts:

- `scan-report.md`
- `scan-report.json`
- `scan-report.sarif`
- `dashboard.md`
- `dashboard.html`

## Safety model

- Every target passes through the scanner authorisation gate.
- Configured targets still pass through the scanner authorisation gate.
- Placeholder endpoints are rejected by the scanner.
- Target contract validation is available before configured target testing.
- The Web UI does not bypass policy, approval, RAG, agent, or target validation.
- The UI reuses existing report generators rather than creating a separate evidence path.
- Results are experimental until OWASP checks are validated beyond the starter oracle layer.

## Operator notes

Use VulnoraIQ for internal VAPT reporting, authorised AI security assessments, and presenting completed evidence packs. For CI/CD usage, prefer the command-line tools and GitHub Actions workflow.
