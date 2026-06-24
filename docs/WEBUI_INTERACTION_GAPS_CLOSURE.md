# WebUI Interaction Gaps Closure

This document records the PR 9 closure work for the remaining WebUI interaction gaps.

## Implemented

### Debounced filtering

Catalog and history search inputs are now intercepted by the WebUI enhancement layer and applied after a short debounce interval. This prevents repeated full re-rendering on every keystroke while keeping the existing static WebUI architecture.

### Retry actions

The global status banner now gets contextual retry actions for recoverable failures:

- interrupted realtime streams can retry live refresh;
- failed scan starts can retry the start action;
- generic data-loading failures can retry data loading.

Authentication and permission errors intentionally do not get generic retry buttons because those require user or role changes.

### Elapsed and ETA metrics

The active scan detail grid now receives Elapsed and ETA cards. The values are computed client-side from visible progress changes and reset when a scan is idle or failed.

### Hosted browser scan-start flow

A hosted Playwright configuration starts the WebUI server, loads the browser UI, selects a demo target/profile, starts a scan, and confirms that the hosted API creates the scan job. Full scan completion, dashboard, and artifact assertions remain future extended-browser coverage so normal CI stays bounded by browser/server behavior rather than scan runtime.

## Validation commands

```bash
npm run build:webui
npm run test:webui
npm run test:webui:hosted
```

CI runs the static and hosted WebUI browser checks only on the Python 3.12 matrix leg.

## Remaining future work

The following are still future improvements, not PR 9 blockers:

- authenticated hosted browser flow with token entry;
- completed-dashboard and artifact browser assertions in an extended test job;
- axe accessibility test gate;
- visual regression snapshots;
- deeper assertions for every catalog/history/finding filter combination.
