# WebUI Testing

The WebUI test layer adds browser-level smoke and hosted API scan-start coverage on top of the existing Python CI gates.

## Local commands

```bash
python -m pip install -e .[dev]
npm install
npx playwright install chromium
npm run test:webui
npm run test:webui:hosted
```

`npm run test:webui` loads `webui/static/index.html` directly as a static file. This keeps the first browser gate stable and fast.

`npm run test:webui:hosted` starts the hosted WebUI with authentication disabled, verifies the browser can load the hosted UI shell, requests a CSRF token, starts a demo scan through the hosted API, and confirms the server creates the scan job. It intentionally avoids waiting for full scan completion or opening the realtime stream so CI remains bounded and does not depend on assessment duration.

## CI behavior

Browser tests run only on the Python 3.12 CI matrix leg to avoid multiplying browser setup across all supported Python versions. The existing Python lint, type-check, pytest, package metadata, mapping, readiness, and demo scan gates remain unchanged.

## Current coverage

- Loads the static console shell.
- Verifies the primary VulnoraIQ and scan-selection headings render.
- Starts the hosted WebUI server.
- Verifies hosted runtime metric elements render.
- Starts a demo scan through the hosted API.
- Verifies a scan job is created through the hosted API.

## Future coverage

- Login/token flow when auth is enabled.
- Full browser-driven form submission once realtime stream handling has dedicated trace artifacts.
- Completed-dashboard and artifact assertions in a longer-running browser flow.
- Catalog, history, and findings filtering assertions beyond static DOM behavior.
- Accessibility checks with axe once the layout stabilizes.
- Advisory visual snapshots before turning visual regression into a required gate.
