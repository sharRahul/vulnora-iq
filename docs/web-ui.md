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

## User workflow

1. Select a target.
2. Select an assessment profile.
3. Confirm authorisation for any configured non-demo target.
4. Start the assessment.
5. Watch the progress ring and realtime event timeline.
6. Review the completed executive dashboard.
7. Download presentation-ready outputs.

## Hosted-mode foundations

The hosted server uses:

- `webui/hosted_server.py` for the active `vulnoraiq-web` entry point.
- `webui/auth.py` for local role and permission checks.
- `config/web_users.yaml` for viewer, analyst, and admin role configuration.
- `webui/persistent_jobs.py` for JSON-backed scan job storage.
- `reports/output/webui/jobs.json` as the default persistent job history file.

Authentication is disabled by default for local development, but the role model is implemented so hosted deployments can enable token-based access in `config/web_users.yaml`.

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
