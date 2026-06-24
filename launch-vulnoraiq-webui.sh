#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "Starting VulnoraIQ WebUI at http://127.0.0.1:8787 ..."
if command -v python3 >/dev/null 2>&1; then
  python3 scripts/bootstrap_launch.py "$@"
else
  python scripts/bootstrap_launch.py "$@"
fi
echo "VulnoraIQ WebUI has stopped."
read -r -p "Press Enter to close this window..." _
