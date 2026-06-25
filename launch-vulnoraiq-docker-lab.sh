#!/usr/bin/env bash
set -euo pipefail

# VulnoraIQ Advanced Docker Lab launcher for Linux.
# Prerequisite: Docker Desktop or a compatible Docker engine with Docker Compose v2.

cd "$(dirname "$0")"
WEBUI_URL="http://127.0.0.1:8787"
CONTAINER_NAME="vulnoraiq-web"
MAX_ATTEMPTS=60

echo "============================================================"
echo " VulnoraIQ Advanced Docker Lab Launcher"
echo "============================================================"
echo ""
echo "This launcher will run the full Docker Compose lab:"
echo "  1. Check Docker is installed and running"
echo "  2. Build VulnoraIQ containers"
echo "  3. Start Docker Compose in the background"
echo "  4. Wait for the WebUI health check"
echo "  5. Open the browser"
echo ""

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker was not found on PATH. Install/start Docker Desktop, then run this launcher again."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but the Docker engine is not running. Start Docker Desktop and try again."
  exit 1
fi

if [[ ! -f docker-compose.yml ]]; then
  echo "docker-compose.yml was not found. Run this launcher from the VulnoraIQ repository or release folder."
  exit 1
fi

echo "[1/4] Building VulnoraIQ Docker image..."
docker compose build

echo ""
echo "[2/4] Starting VulnoraIQ containers..."
docker compose up -d

echo ""
echo "[3/4] Current container status:"
docker compose ps

echo ""
echo "[4/4] Waiting for VulnoraIQ WebUI to become healthy..."
for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
  status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER_NAME" 2>/dev/null || true)"
  if [[ "$status" == "healthy" || "$status" == "running" ]]; then
    echo ""
    echo "VulnoraIQ WebUI is ready: $WEBUI_URL"
    if command -v xdg-open >/dev/null 2>&1; then
      xdg-open "$WEBUI_URL" >/dev/null 2>&1 || true
    elif command -v sensible-browser >/dev/null 2>&1; then
      sensible-browser "$WEBUI_URL" >/dev/null 2>&1 || true
    else
      echo "Open this URL in your browser: $WEBUI_URL"
    fi
    echo ""
    echo "Docker containers are running in the background. To stop them later, run:"
    echo "  docker compose down"
    exit 0
  fi
  if [[ "$attempt" == "1" || "$attempt" == "10" || "$attempt" == "20" || "$attempt" == "30" || "$attempt" == "40" || "$attempt" == "50" ]]; then
    echo "  Status: ${status:-not-created-yet}; still waiting..."
  fi
  sleep 2
done

echo ""
echo "VulnoraIQ did not become healthy in time. Check logs with:"
echo "  docker compose logs vulnoraiq-web"
exit 1
