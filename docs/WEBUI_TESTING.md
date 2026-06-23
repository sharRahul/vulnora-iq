# WebUI Testing

The WebUI test layer adds browser-level smoke coverage on top of the existing Python CI gates.

## Local commands

```bash
python -m pip install -e .[dev]
npm install
npx playwright install chromium
npm run test:webui
```

The current Playwright smoke test loads `webui/static/index.html` directly as a static file. It does not start the hosted server, which keeps the first browser gate stable and fast. Hosted-server, auth, scan queueing, and dashboard-flow tests are tracked as future coverage after the static smoke path is stable.

## CI behavior

Browser tests run only on the Python 3.12 CI matrix leg to avoid multiplying browser setup across all supported Python versions. The existing Python lint, type-check, pytest, package metadata, mapping, readiness, and demo scan gates remain unchanged.

## Current coverage

- Loads the static console shell.
- Verifies the primary VulnoraIQ and scan-selection headings render.

## Future coverage

- Hosted WebUI server startup.
- Login/token flow when auth is enabled.
- Demo scan queueing and dashboard rendering.
- Catalog, history, and findings filtering.
- Accessibility checks with axe once the layout stabilizes.
- Advisory visual snapshots before turning visual regression into a required gate.
