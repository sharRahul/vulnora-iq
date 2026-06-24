# VulnoraIQ WebUI Layout Plan

This plan describes the next-generation WebUI layout direction after the WebUI improvement series.

## Layout goals

- Keep the WebUI understandable for first-time local users.
- Make expert workflows faster for repeat assessment runs.
- Keep the page usable on laptop, desktop, tablet, and narrow mobile screens.
- Preserve accessibility, keyboard navigation, and readable status updates.
- Avoid hiding important safety and authorisation context.

## Proposed information architecture

### 1. Top bar

Purpose: identity, environment, auth/session, theme, and quick health.

Contents:

- VulnoraIQ brand mark and product name.
- Environment pill: Local, Internal, Production.
- Auth/session identity and role.
- Theme toggle.
- Health indicator linking to startup checks.

### 2. Left navigation rail on desktop

Desktop view should use a compact navigation rail:

- Home
- Startup
- Test catalog
- Run scan
- Progress
- Dashboard
- History
- Artifacts
- Settings

On screens below tablet width, this becomes a top segmented control or collapsible menu.

### 3. Home summary

Purpose: answer “what can I do now?” quickly.

Cards:

- Ready state: config loaded, auth state, Docker optional runtime state.
- Last scan summary.
- Recommended next action.
- Safety reminder for configured targets.

### 4. Test catalog workspace

Purpose: let the user select exactly what to test.

Layout:

- Search and filters at the top.
- Category tabs or chips: Suites, OWASP LLM, RAG, Agentic, GenAI, Other.
- Cards with short descriptions, module count, and mapping badges.
- Selected profile drawer on the right desktop; inline summary on mobile.

### 5. Run scan panel

Purpose: make the pre-run decision clear.

Layout:

- Target selector.
- Profile/test selector.
- Authorisation gate.
- Run readiness checklist.
- Start button with queueing/loading state.
- Error banner at top.

### 6. Progress workspace

Purpose: make active work visible and trustworthy.

Layout:

- Current job header: target, profile, status, elapsed time.
- Circular progress ring for quick glance.
- Linear progress bar for exact progress and stage.
- Timeline with icons for queued, running, success, warning, failed.
- Connection state: live, reconnecting, polling fallback.

### 7. Dashboard workspace

Purpose: review results and prepare evidence.

Layout:

- Summary cards at top.
- Top risks accordion open by default.
- Severity and policy summary side by side on desktop.
- Findings table/cards with severity, policy, mapping, component, confidence.
- Artifact accordion with export links.
- Copy summary and export actions grouped together.

### 8. History workspace

Purpose: retrieve previous work quickly.

Layout:

- Search and status filters.
- Recent scan list.
- Saved view filters later.
- Compare with previous scan action later.

### 9. Settings workspace

Purpose: avoid crowding operational controls into the main workflow.

Contents:

- Local launcher settings.
- Output path and job store path.
- Docker runtime status and guidance.
- Auth/session mode summary.
- Link to deployment docs.

## Responsive behavior

| Width | Behavior |
| --- | --- |
| Desktop | Navigation rail plus two-column workspaces where useful. |
| Laptop | Single top bar, compact cards, two columns only for dashboard/progress. |
| Tablet | Navigation becomes horizontal/segmented; most workspaces stack. |
| Mobile <= 480px | One-column layout, full-width controls, short card labels, accordions default collapsed except current task. |

## Component direction

Use these component patterns consistently:

- `StatusBanner` for visible errors and retry guidance.
- `Toast` for temporary success messages.
- `ReadinessCard` for pre-run checks.
- `ProgressHeader` plus `ProgressTimeline` for active jobs.
- `RiskCard`, `FindingCard`, and `ArtifactGroup` for dashboard sections.
- `FilterToolbar` for catalog, findings, and history.

## Visual direction

- Keep the navy/warm-accent identity.
- Use system fonts unless bundled local fonts are added later.
- Keep light and dark mode tokenized.
- Use icons only as supporting cues, never as the only status indicator.
- Maintain WCAG AA contrast targets.

## Implementation order

1. Finish modularizing state/API/stream/dashboard code.
2. Add deeper browser tests for scan and dashboard flows.
3. Move startup/settings into a dedicated workspace.
4. Convert history and dashboard to reusable card/list components.
5. Add optional client-side routing for deep links.
6. Add richer trend visualizations only after historical data views are stable.
