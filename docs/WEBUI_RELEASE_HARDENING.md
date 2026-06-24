# WebUI Release Hardening

This document captures release checks introduced during the WebUI improvement series.

## Metadata alignment

- Python package metadata uses `Apache-2.0`.
- Docker image metadata must also use `Apache-2.0`.
- WebUI static assets remain package-data so source checkouts and package installs can serve the console.

## Release validation checklist

Before a WebUI release:

1. Run the Python CI gates.
2. Run package metadata validation.
3. Run the optional WebUI build validation.
4. Run the WebUI browser smoke tests.
5. Confirm Docker remains optional for local WebUI/demo use.
6. Confirm production deployments keep auth enabled and fail closed.
7. Confirm screenshots/docs reflect the shipped layout.

## Accepted boundaries

- Optional Vite output is supported, but source checkout usage must not require Node.
- Docker runtime checks are explicit and optional.
- Full OIDC remains deferred until backend session support is implemented end-to-end.
