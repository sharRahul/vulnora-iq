# VulnorAIQ Console (React tri-pane SecOps UI)

A modern, enterprise-grade security operations console for VulnorAIQ, built as a
self-contained Vite + React + TypeScript app. It replaces the legacy single-page
static console with a tri-pane analyst workspace and an executive overview.

## Stack

- **React 18 + TypeScript** (strict)
- **Vite 6** build
- **Tailwind CSS** utility styling + design tokens (`src/index.css`)
- **shadcn/ui-style primitives** on **Radix UI** (`src/components/ui/*`)
- **Recharts** for the burn-down and severity charts
- **lucide-react** icons
- **Manrope** (UI) + **JetBrains Mono** (code) fonts

## Develop

```bash
cd webui/console
npm install
npm run dev        # local dev server (Vite)
npm run typecheck  # tsc --noEmit
npm run build      # type-check + production build
```

## How it is served

`npm run build` emits static assets into `../static/console/` with a base path of
`/static/console/`. The Python hosted server (`webui/hosted_server.py`) serves
`console/index.html` at `/`. No Node runtime is required to serve the built
console.

## Architecture

- `src/types/` — strongly typed domain model (Asset, Finding, Severity, CVE/CWE,
  Remediation, ChatMessage, DashboardMetrics, VulnerabilityTrendPoint, …).
- `src/data/mock.ts` — realistic demo data. Replace with live API wiring.
- `src/components/` — `AppShell`, `HeaderBar`, `WorkspaceLayout`, navigation,
  workspace, intelligence, dashboard, target management, and shared UI primitives.

## Backend integration status

The target-management workspace is wired to the hosted backend for:

- `GET /api/targets` — load configured and runtime targets.
- `POST /api/targets/save` and `POST /api/targets/delete` — runtime target CRUD.
- `POST /api/targets/{id}/validate` — target connectivity checks.
- `GET /api/scans` and `POST /api/scans` — scan history refresh and authorised scan launch.

Remaining backend integration TODOs:

- SSE `/api/scans/{id}/events` — live scan progress streaming.
- `POST /api/findings/{id}/apply-fix` — persist an applied remediation.
- `PATCH /api/findings/{id}` — status transitions (e.g. mark for review).
- `POST /api/assistant/chat` — back the "Ask VulnorAIQ" panel with the real model.

Until those exist, the UI uses typed mock data and mocked state transitions.
