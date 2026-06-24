# WebUI Build Pipeline

VulnoraIQ keeps the default WebUI path static and self-hosted. The optional Vite build step is for release validation and packaging only.

The build root is `webui/static`. Generated files are written under `webui/static/dist`.

The local launcher and hosted server continue to serve committed files from `webui/static` directly. Node is not required for normal local use.

The workflow validates this build only on the Python 3.12 matrix leg to avoid repeating browser and Node setup across every Python version.

`pyproject.toml` now allows packaged static assets and optional generated static output to be included in future release packages.
