# VulnoraIQ Modern Web UI

The VulnoraIQ Web UI provides a user-friendly console for VAPT specialists to run local/demo-safe AI security assessments, monitor scan progress in real time, and present completed outputs.

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

Authentication is **enabled by default**. The page loads without a token, but all
assessment data and actions require one. When auth is enabled the top bar shows a
**Sign in required** prompt: paste an access token and select **Connect**. The console
then sends the token (default header `X-VulnoraIQ-Token`) on every request and attaches
a CSRF token to scan submissions automatically.

Tokens map to roles and permissions:

| Token source | Role | Capabilities |
| --- | --- | --- |
| `VULNORAIQ_ADMIN_TOKEN` | admin | view, download, demo + configured scans, full config/targets |
| `VULNORAIQ_ANALYST_TOKEN` | analyst | view, download, demo scans |
| `VULNORAIQ_VIEWER_TOKEN` | viewer | view and download only |

For local development (non-production) you can sign in with the built-in
`vulnoraiq-internal-admin-token`, or disable auth entirely with
`VULNORAIQ_AUTH_ENABLED=false` (open-access demo mode, not for shared deployments).
Use **Sign out** in the top bar to clear the session token.

## User workflow

1. Sign in with an access token (when auth is enabled).
2. Select a target.
3. Select an assessment profile or a single test from the categorised catalog.
4. Confirm authorisation for any configured non-demo target.
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

Authentication is enabled by default; static UI assets are served publicly so the
sign-in prompt can load, while every `/api/*` data endpoint stays behind token auth.
Set `VULNORAIQ_AUTH_ENABLED=false` only for isolated local development. Role and token
configuration lives in `config/web_users.yaml` (file-based fallback) or the
`VULNORAIQ_*_TOKEN` environment variables (preferred for hosted deployments).

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

- The default `demo` target is local and safe.
- Configured targets still pass through the scanner authorisation gate.
- Placeholder endpoints are rejected by the scanner.
- Target contract validation is available before configured target testing.
- The Web UI does not bypass policy, approval, RAG, agent, or target validation.
- The UI reuses existing report generators rather than creating a separate evidence path.
- Results are experimental until OWASP checks are validated beyond the starter oracle layer.

## Operator notes

Use VulnoraIQ for demonstrations, tabletop reviews, internal VAPT reporting, and presenting completed evidence packs. For CI/CD usage, prefer the command-line tools and GitHub Actions workflow.
