# WebUI guide

The supported VulnoraIQ WebUI is the React 18 + TypeScript SecOps console in `webui/console/`, built to `webui/static/console/` and served by `webui/hosted_server.py`.

The legacy static console has been removed. Static files under `webui/static/console/` are build output for the React console and are included as Python package data.

## Start the recommended Docker lab

```bash
docker compose build
docker compose up -d
```

Open <http://localhost:8787>.

## WebUI workspace areas

| Area | Current behaviour |
| --- | --- |
| Dashboard / overview | Shows high-level security and assessment status using React console data models. |
| Target management | Loads configured/runtime targets, supports search and environment filters, shows readiness metrics and status pills, validates targets, saves/deletes runtime targets, launches authorised scans, and refreshes recent jobs. |
| Findings and intelligence | Provides analyst-facing panels for findings, triage context, and dashboard exploration. Some interactions still use typed mock state until backend APIs are implemented. |
| Assessment options | Uses configured profiles and single-test options from `config/attack_profiles.yaml`. |

## Current backend API wiring

The target-management workspace is wired to:

- `GET /api/targets`
- `POST /api/targets/save`
- `POST /api/targets/delete`
- `POST /api/targets/{id}/validate`
- `GET /api/scans`
- `POST /api/scans`

The scan launch path keeps the non-demo authorisation guard. Target validation uses the same target adapter/connectivity logic as the CLI.

## Remaining WebUI backend work

These UI flows still use typed mock state or non-persistent behaviour because their backend APIs are not complete yet:

- live SSE scan progress via `/api/scans/{id}/events`;
- persisted remediation actions such as `POST /api/findings/{id}/apply-fix`;
- persisted finding status transitions such as `PATCH /api/findings/{id}`;
- real assistant chat backend for the "Ask VulnoraIQ" panel.

## Operator flow

1. Start Docker Compose and open the WebUI.
2. Go to the target workspace.
3. Search or filter for the target.
4. Validate target connectivity.
5. Review the readiness checklist.
6. Select an assessment profile or focused single-test option.
7. Confirm authorisation for non-demo targets.
8. Launch the scan.
9. Review recent jobs, findings, and report artifacts.

## Development flow

```bash
cd webui/console
npm install
npm run typecheck
npm run build
```

The production build emits assets into `webui/static/console/`. The Python hosted server serves the built console; Node is not required at runtime.

## Browser test flow

```bash
npm install
npx playwright install chromium --with-deps
npm run test:webui:hosted
```

The hosted WebUI Playwright flow is also part of the GitHub Actions CI path on Python 3.12.

## Security boundary

Launcher/local mode is for loopback laptop/workstation use. For shared/internal-server use, enable production mode, auth, reverse-proxy/TLS controls, and the documented deployment/runbook process.
