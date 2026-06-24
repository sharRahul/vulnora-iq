#!/usr/bin/env bash
# VulnoraIQ Web UI double-click launcher for Linux.
set -euo pipefail
cd "$(dirname "$0")"
echo "Starting VulnoraIQ Web UI..."
if command -v python3 >/dev/null 2>&1; then
  python3 scripts/bootstrap_launch.py "$@"
else
  python scripts/bootstrap_launch.py "$@"
fi
echo "VulnoraIQ Web UI launcher has stopped."
read -r -p "Press Enter to close this window..." _
