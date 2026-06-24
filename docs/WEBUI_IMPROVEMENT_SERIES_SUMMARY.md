# WebUI improvement series summary

This document summarises the WebUI changes and clarifies which older plan items have been superseded by the current React console.

## Current WebUI baseline

The supported WebUI is now the React 18 + TypeScript console in `webui/console/`, built into `webui/static/console/` and served by `webui/hosted_server.py`.

The legacy static console has been removed. Historical no-build/static-console plan items should be treated as completed, superseded, or archival depending on the item.

## Major PR history

| PR | Theme | Current result |
| --- | --- | --- |
| #29 | Initial polish/accessibility | Historical baseline improvements. |
| #30 | Frontend structure cleanup | Superseded by React console structure. |
| #31 | WebUI tests/CI | Browser flow remains part of current CI direction. |
| #32 | Optional Vite path | Superseded by current React/Vite console becoming the supported WebUI source. |
| #33 | Auth/session direction | Production auth is handled by hosted server controls and docs. |
| #39 | Docker runtime checks | Docker dependency guidance remains useful; real AI-agent lab is now Docker-first. |
| #40 | WebUI release metadata | Release-hardening guidance remains relevant. |
| #41/#44 | Final docs/layout plan | Historical final docs, now refreshed to reflect React console and Docker-first lab. |
| #42 | WebUI interactions | Historical interaction improvements before the React overhaul. |
| #43 | React SecOps console overhaul | Current supported UI architecture. |
| #45 | Remove legacy static WebUI | Legacy static console removed from supported path. |
| #46 | Real target testing UI/backend | Target adapters, runtime target APIs, mock-agent, and docs added. |
| #47 | Docker-first AI-agent lab | Current safe lab baseline. |
| #49 | Enhanced target-management workspace | Current production-facing target workspace with backend target/scan API wiring. |

## Current implemented WebUI state

- React app shell and dashboard panels.
- Target-management workspace with search/filtering and readiness metrics.
- Backend target inventory, runtime target save/delete, target validation, scan creation, and recent job refresh.
- Built static assets committed under `webui/static/console/`.
- Hosted WebUI browser flow in CI.
- Security posture remains handled by the Python hosted server: auth, CSRF, rate limits, headers, metrics, audit logs, and path controls.

## Deferred/current gaps

- SSE-backed live progress in React.
- Persisted finding status/remediation APIs.
- Real assistant chat backend.
- Deeper GenAI/OWASP dashboard drill-downs.
- Signed/native release installers.

## Documentation rule

When WebUI behaviour changes, update:

- `README.md`
- `docs/README.md`
- `docs/WEBUI_GUIDE.md`
- `docs/WEBUI_LAYOUT_PLAN.md`
- `docs/WEB_UI_TEST_CATALOG.md`
- `docs/IMPLEMENTATION_STATUS.md`
- `docs/PRODUCTION_READINESS_SCORECARD.md`
- `webui/console/README.md`
