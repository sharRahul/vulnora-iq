# Docker Runtime Dependencies

Docker is optional for VulnoraIQ. The core WebUI, demo scans, reports, dashboards, and local launcher do not require Docker.

Docker is only needed when starting Docker-hosted AI agent runtime templates from the WebUI.

## Check Docker availability

Use the runtime check script:

```bash
python scripts/check_docker_runtime.py
python scripts/check_docker_runtime.py --json
```

The script uses the same Docker discovery logic as the WebUI agent runtime manager, including the `VULNORAIQ_DOCKER_CLI` override.

## Installation boundary

VulnoraIQ should not silently install Docker as part of normal dependency setup. Docker installation can require administrator rights, service changes, virtualization changes, and operating-system package changes.

The WebUI should therefore:

- detect whether Docker is available;
- show clear remediation guidance when it is missing;
- allow the user to set `VULNORAIQ_DOCKER_CLI` when Docker is installed outside `PATH`;
- skip Docker-dependent tests gracefully when Docker is not available.

## Recommended user flow

1. Run the WebUI normally.
2. Review the startup dependency panel.
3. If Docker is shown as missing, install Docker using official OS guidance.
4. Restart the WebUI.
5. Re-run the Docker runtime check.

## CI behavior

Normal CI should not install Docker Engine. Docker-dependent checks should be conditional and should report a clear skip reason when Docker is unavailable.
