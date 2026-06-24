# VulnoraIQ User Guide

This guide explains how to use VulnoraIQ as a local or internal AI security testing application. It assumes you are testing only systems you own or are explicitly authorised to assess.

## 1. Choose how to run VulnoraIQ

Use one of these supported paths:

| Path | Best for | Start command |
| --- | --- | --- |
| Docker GUI lab | Recommended local use | `docker compose up -d` |
| Double-click launcher | Simple local source/release package use | `.bat`, `.command`, or `.sh` launcher |
| Python package/source checkout | CLI and local WebUI use | `vulnoraiq-web --host 127.0.0.1 --port 8787` |
| Internal server | Shared controlled environment | production config validation plus reverse proxy/TLS/auth |

For a clean first run, the dashboard is intentionally empty. VulnoraIQ does not show sample findings, mock assets, or dummy dashboard data.

## 2. Start the local browser GUI

Recommended Docker flow:

```bash
docker compose build
docker compose up -d
docker compose ps
```

Open the GUI in your browser:

```text
http://localhost:8787
```

The default Docker lab binds the WebUI to loopback only: `127.0.0.1:8787:8787`.

Cleanly stop the Docker lab:

```bash
docker compose down
```

Delete local jobs, reports, evidence, audit data, and Docker volumes only when you intentionally want a full reset:

```bash
docker compose down -v
```

## 3. Clean workspace dashboard

A clean workspace shows:

- zero dashboard metrics;
- no assets;
- no findings;
- no sample vulnerability data;
- a message explaining that scans must be run before evidence appears.

After you run scans, VulnoraIQ loads saved backend scan data and shows only your scan jobs, findings, statuses, evidence, and reports.

## 4. Configure targets

Open **Targets** in the WebUI to manage authorised AI systems.

For each non-demo target, confirm:

- target name and target ID;
- endpoint/base URL;
- request type and payload template;
- response extraction path;
- owner/contact details;
- authorisation requirement;
- safety profile;
- rate limit;
- credentials through environment variables, not hard-coded secrets.

Use **Test connectivity** before running a scan.

## 5. Run a scan

You can run scans from either the header or the Targets page.

Header flow:

1. Select **Run Scan**.
2. Watch the live backend scan status.
3. Wait for completion.
4. Review the populated findings and evidence.

Target flow:

1. Open **Targets**.
2. Select a configured target.
3. Choose a scan profile.
4. Select **Start authorised scan**.
5. Monitor live progress and recent jobs.

CLI example:

```bash
docker compose exec vulnoraiq-web vulnoraiq scan --target local_mock_agent --profile ai_agent_foundation --authorised
```

## 6. Review and act on findings

When findings exist, open **Workspace** and select a finding.

Review:

- evidence;
- affected component;
- OWASP/MITRE mapping where available;
- recommendation;
- remediation rationale;
- current review/remediation status.

Use WebUI actions to mark findings for review or fixed. VulnoraIQ persists finding status changes in the backend scan store.

## 7. Find reports, evidence, and history

Use the WebUI for interactive triage and the CLI for direct inspection:

```bash
docker compose exec vulnoraiq-web vulnoraiq reports list
docker compose exec vulnoraiq-web vulnoraiq jobs list
```

Reports and evidence are written under the configured output root. In Docker, use the configured volume/output path for the `vulnoraiq-web` service.

## 8. Operate safely

VulnoraIQ is for authorised assessment only.

Do not scan external or third-party systems unless you have explicit written permission. For shared/internal-server deployments, enable production configuration, strong secrets, TLS through a trusted reverse proxy, audit retention, backups, and protected health/metrics endpoints.
