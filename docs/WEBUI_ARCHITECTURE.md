# VulnoraIQ WebUI Architecture

This document describes the maintainable static-front-end architecture used by the VulnoraIQ WebUI.

## Design constraints

- The WebUI must remain usable as a self-hosted static console served by `webui.hosted_server`.
- The default path must not require Node, npm, or a build step.
- Enhancements should be introduced through small modules that can later be bundled by Vite without changing the API contract.
- Security-sensitive operations continue to go through the backend API with CSRF protection and existing RBAC checks.

## Current layering

| Layer | Responsibility |
| --- | --- |
| `index.html` | Stable semantic structure, landmark regions, form controls, dashboard regions, script/style loading. |
| `app.js` | Existing application state, API calls, scan submission, streaming, dashboard rendering, and history rendering. |
| `webui-core.js` | Shared no-build helper namespace for future modular code: selectors, debounce, pub/sub state, normalized API errors, announcements, and retry helpers. |
| `webui-enhancements.js` | Progressive UI enhancements: theme toggle, toast feedback, status mirroring, busy-state decoration, and accessibility synchronization. |
| CSS files | Existing base styles plus enhancement styles for dark mode, responsive refinements, loading states, accordions, and feedback components. |

## Migration path

The WebUI should be moved from one large `app.js` into smaller files in these stages:

1. Add shared helpers in `webui-core.js` without changing behavior.
2. Move enhancement-only logic to modules first because it has fewer backend dependencies.
3. Extract API helpers from `app.js` into an API module while preserving token and CSRF behavior.
4. Extract stream handling into `stream.js` with abort/retry hooks.
5. Extract dashboard/catalog/history rendering into separate modules after tests cover the current behavior.
6. Optional Vite bundling can then consume the same module boundaries.

## State model

The desired final shape is a tiny pub/sub store:

```js
const store = createStore(initialState);
store.subscribe((next, previous) => { /* update a section */ });
store.setState({ filters: { ...store.state.filters, historyStatus: 'failed' } });
```

This keeps vanilla JS while removing scattered in-place mutation over time.

## API model

API calls should normalize errors into a stable shape:

```js
{
  ok: false,
  status: 403,
  message: 'Your account does not have permission for that action.',
  details: {}
}
```

The current API behavior remains unchanged until the extraction PR moves `apiFetch` into a dedicated module.

## Accessibility model

Dynamic UI updates should use shared helpers:

- `announce(message)` for polite status updates.
- `setBusy(element, true/false)` for async regions.
- `focusFirst(selector)` when a newly visible panel requires keyboard focus.

## Testing impact

This architecture supports Playwright and axe tests without needing a framework. Browser tests can assert semantic behavior, loading states, status banners, and dashboard rendering against the existing static page.
