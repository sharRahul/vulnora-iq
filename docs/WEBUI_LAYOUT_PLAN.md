# VulnoraIQ WebUI layout plan

This document now records the WebUI layout status and future-plan direction.

## Current status

The original WebUI improvement plan has been partly superseded by the React SecOps console. The supported WebUI is now:

- source app: `webui/console/`;
- build tool: Vite;
- framework: React 18 + TypeScript;
- built assets: `webui/static/console/`;
- runtime server: `webui/hosted_server.py`.

The legacy static console has been removed.

## Implemented layout direction

| Area | Current status |
| --- | --- |
| App shell | Implemented in the React console. |
| Dashboard/overview | Implemented with typed UI data models and dashboard panels. |
| Target workspace | Implemented with search/filtering, readiness metrics, validation, safety checklist, scan controls, and recent jobs. |
| Findings/intelligence panels | Present in the React console with typed demo state where backend APIs are not yet implemented. |
| Responsive UI | Implemented through the React/Tailwind layout direction and build pipeline. |
| Static serving | Implemented through package-data assets served by the Python hosted server. |

## Current target-management workspace

The target-management workspace currently integrates with backend APIs for:

- target inventory;
- runtime target save/delete;
- connectivity validation;
- scan creation;
- recent job refresh.

It also surfaces safety and readiness information before an assessment is started.

## Remaining layout/backend plan

| Area | Future work |
| --- | --- |
| Live assessment progress | Wire React views to real SSE `/api/scans/{id}/events`. |
| Finding workflow | Persist finding status transitions and remediation actions. |
| Assistant panel | Replace typed demo assistant state with a real backend API and model controls. |
| GenAI/OWASP dashboards | Add deeper framework coverage drill-downs and evidence quality views. |
| Target templates | Add guided creation flows for common LLM, RAG, local model, and agent runtime shapes. |
| Release polish | Keep screenshots, docs, package data, and Playwright hosted-flow tests aligned with the shipped layout. |

## Layout principles that remain valid

- Keep first-run local/Docker setup understandable.
- Keep target authorisation and safety context visible.
- Make repeat assessment runs fast for experienced users.
- Preserve keyboard/accessibility basics.
- Keep reports/evidence/export actions visible after scans.
- Avoid overclaiming assurance in UI text.

## Completion definition

The WebUI layout work should be considered complete for the next maturity stage when major UI panels are backed by persisted APIs, browser tests cover the main analyst flows, and documentation/screenshots match the built console served by `vulnoraiq-web`.
