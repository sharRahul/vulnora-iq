from __future__ import annotations

import argparse
import importlib.util
import logging
import os
import socket
import sys
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "reports" / "output" / "webui"
DEFAULT_JOB_STORE = DEFAULT_OUTPUT_ROOT / "jobs.db"


def _status_item(name: str, status: str, detail: str) -> dict[str, str]:
    return {"name": name, "status": status, "detail": detail}


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def build_startup_status(host: str, port: int, shutdown_allowed: bool) -> dict[str, Any]:
    output_root = Path(os.getenv("VULNORAIQ_WEB_OUTPUT_ROOT", str(DEFAULT_OUTPUT_ROOT)))
    job_store_path = Path(os.getenv("VULNORAIQ_JOB_STORE_PATH", str(DEFAULT_JOB_STORE)))
    python_ok = sys.version_info >= (3, 10)
    dependency_checks = [
        _status_item(
            "Python runtime",
            "pass" if python_ok else "fail",
            f"Python {sys.version.split()[0]} detected; VulnoraIQ requires Python 3.10 or newer.",
        ),
        _status_item(
            "PyYAML dependency",
            "pass" if _module_available("yaml") else "fail",
            "Required to load YAML configuration files.",
        ),
        _status_item(
            "VulnoraIQ package modules",
            "pass" if (ROOT / "core" / "scanner.py").exists() else "fail",
            "Core scanner package is available from this checkout.",
        ),
        _status_item(
            "Targets config",
            "pass" if (ROOT / "config" / "targets.yaml").exists() else "fail",
            "Target definitions are available.",
        ),
        _status_item(
            "Attack profiles config",
            "pass" if (ROOT / "config" / "attack_profiles.yaml").exists() else "fail",
            "Assessment profiles are available.",
        ),
        _status_item(
            "Web UI assets",
            "pass" if (ROOT / "webui" / "static" / "index.html").exists() else "fail",
            "Static Web UI files are present.",
        ),
        _status_item(
            "Output directory",
            "pass" if output_root.exists() else "warn",
            f"Reports will be written under {output_root}.",
        ),
        _status_item(
            "SQLite job store",
            "pass" if job_store_path.parent.exists() else "warn",
            f"Job history will use {job_store_path}.",
        ),
    ]
    blocked = any(item["status"] == "fail" for item in dependency_checks)
    warnings = any(item["status"] == "warn" for item in dependency_checks)
    status = "blocked" if blocked else "warning" if warnings else "ready"
    quick_start_actions = [
        _status_item("Create output directory", "pass", f"Ensured {output_root} exists before server startup."),
        _status_item("Configure local job store", "pass", f"Using SQLite path {job_store_path}."),
        _status_item("Open browser", "pass", f"Browser launched at http://{host}:{port}/."),
        _status_item("Local session", "pass", "Launcher mode runs on loopback for local self-hosted assessment work."),
        _status_item(
            "Stop button",
            "pass" if shutdown_allowed else "warn",
            "Enabled only for loopback launcher mode with explicit shutdown permission.",
        ),
    ]
    change_options = [
        _status_item("Host", "pass", f"Current host: {host}. Change with --host or edit the launcher file."),
        _status_item("Port", "pass", f"Current port: {port}. Change with --port or edit the launcher file."),
        _status_item("Output root", "pass", f"Current output root: {output_root}. Change VULNORAIQ_WEB_OUTPUT_ROOT."),
        _status_item("Job store", "pass", f"Current job store: {job_store_path}. Change VULNORAIQ_JOB_STORE_PATH."),
        _status_item(
            "Auth",
            "pass",
            f"Launcher auth setting: {os.getenv('VULNORAIQ_AUTH_ENABLED', 'false')} for local loopback mode.",
        ),
    ]
    return {
        "status": status,
        "message": (
            "Local launcher checks passed."
            if status == "ready"
            else "Review warnings or failures before running scans."
        ),
        "launcher_mode": True,
        "host": host,
        "port": port,
        "url": f"http://{host}:{port}/",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "shutdown_allowed": shutdown_allowed,
        "dependency_checks": dependency_checks,
        "quick_start_actions": quick_start_actions,
        "change_options": change_options,
    }


def _configure_environment(args: argparse.Namespace) -> None:
    DEFAULT_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("VULNORAIQ_ENV", "development")
    os.environ.setdefault("VULNORAIQ_AUTH_ENABLED", "false")
    os.environ.setdefault("VULNORAIQ_ENABLE_WEB_SHUTDOWN", "true")
    os.environ.setdefault("VULNORAIQ_JOB_STORE_BACKEND", "sqlite")
    os.environ.setdefault("VULNORAIQ_JOB_STORE_PATH", str(DEFAULT_JOB_STORE))
    os.environ.setdefault("VULNORAIQ_WEB_OUTPUT_ROOT", str(DEFAULT_OUTPUT_ROOT))
    os.environ.setdefault("VULNORAIQ_HOST", args.host)
    os.environ.setdefault("VULNORAIQ_PORT", str(args.port))


def _port_is_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) != 0


def _wait_for_health(url: str, timeout: float = 12.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(f"{url}/healthz", timeout=1.0) as response:  # noqa: S310 - local launcher URL
                if response.status == HTTPStatus.OK:
                    return True
        except (OSError, URLError):
            time.sleep(0.25)
    return False


def _shutdown_allowed_for(host: str) -> bool:
    env_value = os.getenv("VULNORAIQ_ENABLE_WEB_SHUTDOWN", "true").strip().lower()
    enabled = env_value in ("1", "true", "yes")
    return enabled and host in {"127.0.0.1", "localhost", "::1"}


def _open_browser_when_ready(base_url: str) -> None:
    if not _wait_for_health(base_url):
        print("VulnoraIQ Web UI did not become ready quickly. Check the console output for errors.")
        return
    webbrowser.open(f"{base_url}/?launcher=1")
    print(f"Opened VulnoraIQ Web UI: {base_url}/")


def run_launcher(args: argparse.Namespace) -> int:
    os.chdir(ROOT)
    _configure_environment(args)
    shutdown_allowed = _shutdown_allowed_for(args.host)
    base_url = f"http://{args.host}:{args.port}"
    if not _port_is_available(args.host, args.port):
        print(f"Port {args.port} is already in use. Opening the existing local server.")
        webbrowser.open(f"{base_url}/?launcher=1")
        return 0

    from webui.hosted_server import (  # noqa: PLC0415
        AUTH_MANAGER,
        HostedWebUiHandler,
        _audit_structured,
        _inc_metric,
        _rate_limit_cleanup_loop,
        _validate_csrf,
    )

    class LauncherWebUiHandler(HostedWebUiHandler):
        def _do_GET_routes(self, path: str, client_ip: str, request_id: str) -> None:
            if path.split("?", 1)[0] == "/api/startup":
                principal = self._principal(client_ip)
                if not principal:
                    _inc_metric("auth_failures")
                    _audit_structured(
                        "auth_failure",
                        AUTH_MANAGER.anonymous(),
                        request_id,
                        client_ip,
                        "GET",
                        "/api/startup",
                        401,
                        "startup checks auth required",
                    )
                    self._send_error_response(HTTPStatus.UNAUTHORIZED, "authentication required")
                    return
                if not self._check_rate_limit(principal, client_ip):
                    return
                self._send_json(build_startup_status(args.host, args.port, shutdown_allowed))
                return
            super()._do_GET_routes(path, client_ip, request_id)

        def _do_POST_routes(self, path: str, client_ip: str, request_id: str) -> None:
            clean_path = path.split("?", 1)[0]
            if clean_path == "/api/server/shutdown":
                principal = self._principal(client_ip)
                if not principal:
                    _inc_metric("auth_failures")
                    _audit_structured(
                        "auth_failure",
                        AUTH_MANAGER.anonymous(),
                        request_id,
                        client_ip,
                        "POST",
                        clean_path,
                        401,
                        "shutdown auth required",
                    )
                    self._send_error_response(HTTPStatus.UNAUTHORIZED, "authentication required")
                    return
                if not self._check_rate_limit(principal, client_ip):
                    return
                session_key = self._session_key(principal)
                csrf_token = self.headers.get("X-CSRF-Token")
                if not _validate_csrf(session_key, csrf_token):
                    _inc_metric("csrf_failures")
                    _audit_structured(
                        "csrf_failure",
                        principal,
                        request_id,
                        client_ip,
                        "POST",
                        clean_path,
                        403,
                        "shutdown invalid csrf",
                    )
                    self._send_error_response(HTTPStatus.FORBIDDEN, "invalid or missing CSRF token")
                    return
                if not shutdown_allowed:
                    self._send_error_response(HTTPStatus.CONFLICT, "server shutdown is disabled for this runtime")
                    return
                _audit_structured(
                    "server_shutdown_requested",
                    principal,
                    request_id,
                    client_ip,
                    "POST",
                    clean_path,
                    202,
                    "launcher stop requested",
                )
                self._send_json(
                    {
                        "status": "stopping",
                        "message": "Local VulnoraIQ Web UI server is stopping.",
                    },
                    status=HTTPStatus.ACCEPTED,
                )
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            super()._do_POST_routes(path, client_ip, request_id)

    logging.basicConfig(
        level=os.getenv("VULNORAIQ_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    threading.Thread(target=_rate_limit_cleanup_loop, daemon=True).start()
    server = ThreadingHTTPServer((args.host, args.port), LauncherWebUiHandler)
    print("VulnoraIQ local launcher checks:")
    for item in build_startup_status(args.host, args.port, shutdown_allowed)["dependency_checks"]:
        print(f"- {item['status'].upper()}: {item['name']} - {item['detail']}")
    if not args.no_browser:
        threading.Thread(target=_open_browser_when_ready, args=(base_url,), daemon=True).start()
    print(f"VulnoraIQ Web UI running at {base_url}/")
    print("Use the Web UI Stop local server button or press Ctrl+C in this window to stop it.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping VulnoraIQ Web UI...")
    finally:
        server.server_close()
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the local VulnoraIQ Web UI and open it in a browser.")
    parser.add_argument("--host", default="127.0.0.1", help="Host/interface to bind. Default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=8787, help="Port to bind. Default: 8787")
    parser.add_argument("--no-browser", action="store_true", help="Start the server without opening a browser window")
    return parser.parse_args(argv)


def main() -> None:
    raise SystemExit(run_launcher(parse_args()))


if __name__ == "__main__":
    main()
