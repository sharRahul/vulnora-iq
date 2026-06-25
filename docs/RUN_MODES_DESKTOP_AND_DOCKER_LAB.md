# VulnoraIQ run modes: desktop default and Docker lab advanced

This document defines the product direction for VulnoraIQ launch and runtime modes.

## Product decision

VulnoraIQ will support two explicit launch modes:

| Mode | Intended users | Where VulnoraIQ runs | Where imported agents run | Report location |
| --- | --- | --- | --- | --- |
| Desktop Mode | Laptop and workstation users | Native host process | Docker containers | `./scan-reports/` |
| Docker Lab Mode | Servers, VMs, CI, dev labs | Docker Compose container | Docker containers | Docker volume or mapped folders |

Desktop Mode is the default product direction for normal users. Docker Lab Mode remains supported for reproducible lab, CI, server, and VM workflows.

## Desktop Mode target flow

```text
User clicks native launcher
  -> VulnoraIQ starts on the host machine
  -> Browser opens http://127.0.0.1:8787
  -> User opens Agent Lab
  -> User imports/selects a real AI-agent project
  -> VulnoraIQ stores it under ./agent-lab/projects/
  -> User configures API key, local LLM, remote LLM, CPU/GPU runtime
  -> VulnoraIQ uses Docker only to build/run the imported agent
  -> VulnoraIQ auto-creates a target for the running agent
  -> User runs scans from the WebUI
  -> Jobs, reports, evidence, audit, and exports are stored under ./scan-reports/
  -> Dashboard loads results from the local job store and report/evidence folders
```

Desktop Mode uses Docker as a sandbox for imported targets, not as the runtime for VulnoraIQ itself.

## Docker Lab Mode target flow

```text
User starts Docker Lab launcher or manual Docker Compose
  -> Docker Compose builds/starts vulnoraiq-web
  -> Browser opens http://127.0.0.1:8787
  -> User opens Agent Lab
  -> User imports/selects a real AI-agent project
  -> VulnoraIQ stores it under /data/agent_lab/projects
  -> User configures API key, local LLM, remote LLM, CPU/GPU runtime
  -> vulnoraiq-web uses Docker to build/run the imported agent
  -> VulnoraIQ auto-creates a target for the running agent
  -> User runs scans from the WebUI
  -> Jobs, reports, evidence, and audit are stored under /data
```

Docker Lab Mode keeps the current reproducible containerised lab model.

## Folder contract

Desktop Mode must create and use these folders in the checkout/release root:

```text
scan-reports/
  jobs.db
  reports/
  evidence/
  audit/
  exports/

agent-lab/
  projects/
  deployments.yaml
```

Docker Lab Mode may keep using `/data`, but should optionally support host-visible bind mounts later:

```text
./scan-reports:/data/reports-visible or equivalent mapped output
./agent-lab:/data/agent_lab
```

## Runtime responsibilities

| Responsibility | Desktop Mode | Docker Lab Mode |
| --- | --- | --- |
| Start WebUI | Host process | Compose service |
| Build imported agent | Host Docker CLI/API | Docker CLI/API from `vulnoraiq-web` |
| Run imported agent | Docker container | Docker container |
| Scan target | Host VulnoraIQ scanner | Containerised VulnoraIQ scanner |
| Agent target URL | Published localhost port | Container DNS on Compose network |
| Reports | Host folder | `/data` volume or mapped folder |
| Best default | End users | Advanced/dev/server/CI |

## Implementation phases

### Phase 1: repo/source mode foundation

- Add a native desktop launcher script that runs VulnoraIQ on the host.
- Set Desktop Mode environment variables for `scan-reports/` and `agent-lab/`.
- Keep Docker Lab launchers available as explicit advanced launchers.
- Make Agent Lab create/use a desktop Docker network when running from host.
- Make Agent Lab auto-created targets use `127.0.0.1:<port>` in Desktop Mode and container DNS in Docker Lab Mode.
- Update tests and docs for both modes.

### Phase 2: packaged desktop application

- Build platform bundles that include a Python runtime or frozen executable.
- Make the primary double-click launcher start Desktop Mode without requiring host Python.
- Keep Docker Desktop as the only external prerequisite for normal users.
- Store all reports and Agent Lab data in user-visible folders.

### Phase 3: UX polish

- Add WebUI run-mode indicator.
- Add a reports folder opener/exporter.
- Add backup/export before reset.
- Add a mode selector/help page that explains Desktop Mode vs Docker Lab Mode.

## Security notes

- Imported agents remain untrusted and must run in Docker containers by default.
- API keys configured for imported agents should be injected into the agent runtime only and redacted from stored metadata.
- Desktop Mode should keep the WebUI on `127.0.0.1`.
- Docker Lab Mode must remain loopback-only unless deployed behind production auth, TLS, reverse proxy controls, audit retention, and backups.
