# VulnoraIQ WebUI Validated Implementation Plan

This plan records the agreed WebUI implementation roadmap, the items intentionally deferred or discarded, and the PR sequence used to land the work safely.

## Scope

The WebUI should become easier to use, more accessible, more maintainable, and more testable without weakening VulnoraIQ's self-hosted security posture. The implementation is split into stacked PRs so each change can be reviewed independently and merged in order.

## PR sequence

| PR | Theme | Outcome |
| --- | --- | --- |
| 1 | Responsive, dark mode, accessibility, loading/error feedback | Improve the current static WebUI without changing the backend API contract. |
| 2 | Frontend structure cleanup | Move toward modular vanilla JS/CSS helpers while preserving the no-build runtime path. |
| 3 | WebUI tests and CI | Add browser-level smoke/a11y checks and keep Python CI stable. |
| 4 | Optional build pipeline | Add Vite as an optional asset build path while keeping committed static assets usable. |
| 5 | Auth/session hardening | Prepare production-safe HTTP-only cookie mode and document OIDC as a later enterprise integration. |
| 6 | Docker dependency automation | Add explicit Docker runtime checks/install helpers without silently modifying user machines. |
| 7 | Docker/package metadata and release hardening | Align Docker/package metadata and release validation around the WebUI changes. |
| 8 | Final documentation and WebUI layout plan | Consolidate docs, onboarding, and future layout direction after implementation. |

## Implement now

### Responsive layout

- Add a mobile-first breakpoint at `max-width: 480px`.
- Ensure form, progress, dashboard, catalog, findings, history, and artifact sections stack cleanly on narrow screens.
- Continue using CSS Grid/Flexbox; no framework is required for this phase.

### Dark mode

- Use the real CSS `color-scheme` property, not a custom `--color-scheme` variable.
- Add `[data-theme="dark"]` design tokens.
- Respect `prefers-color-scheme` on first load.
- Add a top-bar theme toggle and persist the selected preference in local storage.

### Accessibility

- Add explicit labels to ambiguous controls.
- Use `role="status"` and `aria-live="polite"` for dynamic state.
- Improve keyboard focus with `:focus-visible`.
- Keep dynamic announcements polite and avoid excessive screen-reader chatter.

### Feedback, loading states, and errors

- Add skeleton loaders for config, catalog, history, and dashboard states.
- Disable the Start button while queueing and expose `aria-busy`.
- Consolidate user-visible errors in a top banner.
- Provide retry actions for network/API failures where safe.
- Replace persistent copy messages with transient toast notifications and screen-reader announcements.

### Dashboard polish

- Add accessible accordions for Top risks, Findings, and Artifacts.
- Keep severity bars lightweight; add exact counts, accessible labels, and tooltips.
- Improve current-stage/timeline visuals without replacing the current backend progress model.

### Search and filtering

- Debounce catalog and history search inputs.
- Add clear-filter affordances first; multi-select filters can follow when the UI state model is modularized.

### Documentation and CI

- Every PR must include documentation updates.
- Add tests incrementally so the WebUI can be validated without making local demo use harder.

## Deferred items

| Item | Decision | Why |
| --- | --- | --- |
| React/Vue migration | Deferred | Too much churn for the current static WebUI; modular vanilla JS should land first. |
| Alpine.js | Deferred | Could help later, but not necessary for the first maintainability pass. |
| Chart.js | Deferred | Useful later for trends/benchmarks; current severity distribution does not need it. |
| Full i18n extraction | Deferred | UI strings should stabilize before a full translation resource system is introduced. |
| Virtualized catalog/history lists | Deferred | Add lazy rendering and debounced filtering first; virtual lists are only needed if data volume grows. |
| Visual regression as a required gate | Deferred | Add Playwright/axe smoke checks first; make screenshots advisory until layout stabilizes. |
| FastAPI backend migration | Deferred | The existing server already handles static assets, auth, CSRF, rate limiting, SSE, metrics, and persistence. Backend migration belongs in a separate architecture track. |
| OIDC/OAuth enterprise SSO | Deferred | Needs a backend auth flow and deployment design; prepare docs and cookie mode first. |

## Discarded items

| Item | Decision | Why |
| --- | --- | --- |
| D3 for current charts | Discarded for now | Overkill for current severity bars and would add unnecessary payload/complexity. |
| HTTP/2 server push | Discarded | Browser support and operational value are poor; cache headers and hashed/static assets are safer. |
| Production auth tokens in localStorage | Discarded | Local/session storage is script-readable; production should prefer HTTP-only secure cookies. |
| Silent Docker Engine installation | Discarded | Installing Docker requires elevated OS changes and explicit user consent. |
| Remote web font dependency for the default UI | Discarded for now | External fonts complicate offline/self-hosted use. Use a strong system UI stack unless fonts are bundled locally later. |

## Docker automation boundary

Docker should remain optional for the local launcher. The WebUI should detect Docker, explain what is missing, and provide explicit scripts. It must not silently install Docker as part of a default dependency check.

## Validation checklist for each PR

- Python package metadata remains valid.
- Static WebUI assets continue to be packaged.
- Existing Python tests, lint, mypy, pip check, pip-audit, readiness gates, and demo scan remain compatible.
- Any new Node/WebUI tests are isolated so they do not multiply across the full Python matrix.
- Documentation is updated in the same PR as implementation.
