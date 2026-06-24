# VulnoraIQ Console (React SecOps UI)

A modern security operations console for VulnoraIQ, built as a self-contained Vite + React + TypeScript app.

It is now the supported WebUI. The legacy static console has been removed.

## Stack

- **React 18 + TypeScript**
- **Vite 6** build
- **Tailwind CSS** utility styling + design tokens (`src/index.css`)
- **shadcn/ui-style primitives** on **Radix UI** (`src/components/ui/*`)
- **Recharts** for charts
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

`npm run build` emits static assets into `../static/console/` with a base path of `/static/console/`. The Python hosted server (`webui/hosted_server.py`) serves `console/index.html` at `/`.

No Node runtime is required to serve the built console.

## Architecture

- `src/types/` — strongly typed domain model for targets, jobs, findings, dashboard metrics, trends, remediation, and assistant/chat state.
- `src/components/` — app shell, header, workspace layout, navigation, dashboard, intelligence, findings, target management, and shared UI primitives.
- `src/data/mock.ts` — demo data for panels whose backend APIs are not complete yet.

## Backend integration status

The target-management workspace is wired to the hosted backend for:

- `GET /api/targets` — load configured and runtime targets.
- `POST /api/targets/save` and `POST /api/targets/delete` — runtime target CRUD.
- `POST /api/targets/{id}/validate` — target connectivity checks.
- `GET /api/scans` and `POST /api/scans` — scan history refresh and authorised scan creation.

Current target workspace features include search, environment filtering, readiness metrics, health/status pills, safety checklist, profile selection, scan controls, recent job list, and enhanced target cards/panels.

## Remaining backend integration TODOs

- SSE `/api/scans/{id}/events` — live scan progress streaming.
- `POST /api/findings/{id}/apply-fix` — persist an applied remediation.
- `PATCH /api/findings/{id}` — persisted status transitions.
- `POST /api/assistant/chat` — back the assistant panel with a real model/API integration.

Until those APIs exist, the affected panels use typed demo data and local UI state transitions.
