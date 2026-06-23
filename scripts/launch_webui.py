from __future__ import annotations

import argparse
import importlib.util
import json
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

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "reports" / "output" / "webui"
DEFAULT_JOB_STORE = DEFAULT_OUTPUT_ROOT / "jobs.db"
LAUNCHER_SETTINGS_PATH = DEFAULT_OUTPUT_ROOT / "launcher-settings.json"
DEFAULT_RUNTIME_TARGETS = DEFAULT_OUTPUT_ROOT / "runtime_targets.yaml"
DEFAULT_AGENT_RUNTIME_REGISTRY = DEFAULT_OUTPUT_ROOT / "agent-runtimes.json"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _status_item(name: str, status: str, detail: str) -> dict[str, str]:
    return {"name": name, "status": status, "detail": detail}


def _option_item(
    key: str,
    name: str,
    value: str,
    detail: str,
    *,
    editable: bool = True,
    input_type: str = "text",
    status: str = "pass",
) -> dict[str, Any]:
    return {
        "key": key,
        "name": name,
        "value": value,
        "detail": detail,
        "editable": editable,
        "input_type": input_type,
        "status": status,
    }


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _load_launcher_settings() -> dict[str, Any]:
    if not LAUNCHER_SETTINGS_PATH.exists():
        return {}
    try:
        data = json.loads(LAUNCHER_SETTINGS_PATH.read_text(encoding="utf-8") or "{}")
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_launcher_settings(settings: dict[str, Any]) -> None:
    LAUNCHER_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    LAUNCHER_SETTINGS_PATH.write_text(json.dumps(settings, indent=2, sort_keys=True), encoding="utf-8")


def _coerce_safe_path(value: Any, field_name: str) -> Path:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} cannot be empty")
    if "\x00" in text:
        raise ValueError(f"{field_name} contains an invalid character")
    return Path(text).expanduser()


def _coerce_port(value: Any) -> int:
    try:
        port = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Port must be a number") from exc
    if port < 1024 or port > 65535:
        raise ValueError("Port must be between 1024 and 65535")
    return port


def _validate_launcher_settings(raw: dict[str, Any], current_host: str, current_port: int) -> dict[str, Any]:
    host = str(raw.get("host", current_host) or current_host).strip()
    if host not in LOOPBACK_HOSTS:
        raise ValueError("Local launcher host must stay on loopback: 127.0.0.1, localhost, or ::1")

    port = _coerce_port(raw.get("port", current_port))
    output_root = _coerce_safe_path(raw.get("output_root", os.getenv("VULNORAIQ_WEB_OUTPUT_ROOT", str(DEFAULT_OUTPUT_ROOT))), "Output root")
    job_store_path = _coerce_safe_path(
        raw.get("job_store_path", os.getenv("VULNORAIQ_JOB_STORE_PATH", str(output_root / "jobs.db"))),
        "Job store path",
    )
    if job_store_path.suffix.lower() != ".db":
        raise ValueError("Job store path must point to a .db SQLite file")

    return {
        "host": host,
        "port": port,
        "output_root": str(output_root),
        "job_store_path": str(job_store_path),
    }


def _selected_launcher_settings(default_host: str, default_port: int) -> dict[str, Any]:
    saved = _load_launcher_settings()
    try:
        return _validate_launcher_settings(saved, default_host, default_port)
    except ValueError:
        return {
            "host": default_host,
            "port": default_port,
            "output_root": str(Path(os.getenv("VULNORAIQ_WEB_OUTPUT_ROOT", str(DEFAULT_OUTPUT_ROOT))).expanduser()),
            "job_store_path": str(Path(os.getenv("VULNORAIQ_JOB_STORE_PATH", str(DEFAULT_JOB_STORE))).expanduser()),
        }


def _merge_runtime_targets(config: dict[str, Any], runtime_targets_path: Path) -> None:
    if not runtime_targets_path.exists():
        return
    runtime_targets = yaml.safe_load(runtime_targets_path.read_text(encoding="utf-8")) or {}
    if not isinstance(runtime_targets, dict):
        return
    configured_targets = config.setdefault("targets", {})
    if not ("profiles" in config or "web_auth_enabled" in config):
        configured_targets = configured_targets.setdefault("targets", {})
    for name, target in (runtime_targets.get("targets") or {}).items():
        if isinstance(target, dict):
            configured_targets[str(name)] = target


def _apply_runtime_paths(output_root: Path) -> None:
    os.environ.setdefault("VULNORAIQ_AGENT_RUNTIME_REGISTRY", str(output_root / "agent-runtimes.json"))
    os.environ.setdefault("VULNORAIQ_RUNTIME_TARGETS_PATH", str(output_root / "runtime_targets.yaml"))


def build_startup_status(host: str, port: int, shutdown_allowed: bool) -> dict[str, Any]:
    selected = _selected_launcher_settings(host, port)
    output_root = Path(os.getenv("VULNORAIQ_WEB_OUTPUT_ROOT", selected["output_root"]))
    job_store_path = Path(os.getenv("VULNORAIQ_JOB_STORE_PATH", selected["job_store_path"]))
    python_ok = sys.version_info >= (3, 10)
    dependency_checks = [
        _status_item(
            "Python runtime",
            "pass" if python_ok else "fail",
            f"Python {sys.version.split()[0]} detected; VulnoraIQ requires Python 3.10 or newer.",
        ),
        _status_item(
            "Docker runtime",
            "pass" if importlib.util.find_spec("subprocess") else "fail",
            "Required for hosting selected AI agents in local Docker containers.",
        ),
        _status_item(
            "PyYAML dependency",
            "pass" if _module_available("yaml") else "fail",
            "Required to load YAML configuration files.",
        ),
        _status_item(
            "requests dependency",
            "pass" if _module_available("requests") else "fail",
            "Required for configured HTTP/LLM target adapters.",
        ),
        _status_item(
            "rich dependency",
            "pass" if _module_available("rich") else "fail",
            "Required for CLI scan output rendering.",
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
            "AI agent runtime templates",
            "pass" if (ROOT / "config" / "agent_runtimes.yaml").exists() else "fail",
            "Docker AI agent templates are available.",
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
    configuration_options = [
        _option_item("host", "Host", str(selected["host"]), "Loopback host selected for the local launcher."),
        _option_item("port", "Port", str(selected["port"]), "Browser port selected for the local launcher.", input_type="number"),
        _option_item("output_root", "Output root", str(selected["output_root"]), "Reports, job history, and Docker agent runtime metadata are written here."),
        _option_item("job_store_path", "Job store", str(selected["job_store_path"]), "SQLite database used for scan history."),
        _option_item(
            "auth_enabled",
            "Auth",
            os.getenv("VULNORAIQ_AUTH_ENABLED", "false"),
            "Local launcher auth state. Use hosted production mode for shared or exposed deployments.",
            editable=False,
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
        "configuration_options": configuration_options,
        "settings_file": str(LAUNCHER_SETTINGS_PATH),
        "runtime_targets_file": os.getenv("VULNORAIQ_RUNTIME_TARGETS_PATH", str(DEFAULT_RUNTIME_TARGETS)),
    }


def _configure_environment(args: argparse.Namespace) -> None:
    DEFAULT_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    selected = _selected_launcher_settings(args.host, args.port)
    output_root = Path(str(selected["output_root"]))
    job_store_path = Path(str(selected["job_store_path"]))
    output_root.mkdir(parents=True, exist_ok=True)
    job_store_path.parent.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("VULNORAIQ_ENV", "development")
    os.environ.setdefault("VULNORAIQ_AUTH_ENABLED", "false")
    os.environ.setdefault("VULNORAIQ_ENABLE_WEB_SHUTDOWN", "true")
    os.environ.setdefault("VULNORAIQ_JOB_STORE_BACKEND", "sqlite")
    os.environ.setdefault("VULNORAIQ_JOB_STORE_PATH", str(job_store_path))
    os.environ.setdefault("VULNORAIQ_WEB_OUTPUT_ROOT", str(output_root))
    _apply_runtime_paths(output_root)
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
    return enabled and host in LOOPBACK_HOSTS


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

    import webui.hosted_server as hosted_runtime  # noqa: PLC0415
    from webui.agent_runtime import AgentRuntimeManager  # noqa: PLC0415
    from webui.hosted_server import (  # noqa: PLC0415
        AUTH_MANAGER,
        HostedWebUiHandler,
        _audit_structured,
        _inc_metric,
        _rate_limit_cleanup_loop,
        _validate_csrf,
    )

    agent_runtime = AgentRuntimeManager()

    class LauncherWebUiHandler(HostedWebUiHandler):
        def _require_runtime_principal(self, client_ip: str, method: str, clean_path: str, request_id: str):
            principal = self._principal(client_ip)
            if not principal:
                _inc_metric("auth_failures")
                _audit_structured(
                    "auth_failure",
                    AUTH_MANAGER.anonymous(),
                    request_id,
                    client_ip,
                    method,
                    clean_path,
                    401,
                    "runtime auth required",
                )
                self._send_error_response(HTTPStatus.UNAUTHORIZED, "authentication required")
                return None
            if not self._check_rate_limit(principal, client_ip):
                return None
            return principal

        def _validate_runtime_write(self, principal, clean_path: str) -> bool:
            if not AUTH_MANAGER.can(principal, "manage_runtime"):
                self._send_error_response(HTTPStatus.FORBIDDEN, "runtime management permission required")
                return False
            if not _validate_csrf(self._session_key(principal), self.headers.get("X-CSRF-Token")):
                _inc_metric("csrf_failures")
                self._send_error_response(HTTPStatus.FORBIDDEN, "invalid or missing CSRF token")
                return False
            if "application/json" not in self.headers.get("Content-Type", "").lower():
                self._send_error_response(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Content-Type must be application/json")
                return False
            return True

        def _do_GET_routes(self, path: str, client_ip: str, request_id: str) -> None:
            clean_path = path.split("?", 1)[0]
            if clean_path == "/api/startup":
                principal = self._require_runtime_principal(client_ip, "GET", clean_path, request_id)
                if not principal:
                    return
                self._send_json(build_startup_status(args.host, args.port, shutdown_allowed))
                return
            if clean_path == "/api/agents":
                principal = self._require_runtime_principal(client_ip, "GET", clean_path, request_id)
                if not principal:
                    return
                self._send_json(agent_runtime.list_state())
                return
            if clean_path == "/api/config":
                principal = self._require_runtime_principal(client_ip, "GET", clean_path, request_id)
                if not principal:
                    return
                cfg = hosted_runtime.load_config()
                _merge_runtime_targets(cfg, agent_runtime.runtime_targets_path)
                if not AUTH_MANAGER.can(principal, "manage_runtime"):
                    cfg = {
                        "profiles": {k: {"description": v.get("description", "")} for k, v in cfg.get("profiles", {}).items()},
                        "web_auth_enabled": cfg.get("web_auth_enabled", False),
                    }
                self._send_json(cfg)
                return
            super()._do_GET_routes(path, client_ip, request_id)

        def _do_POST_routes(self, path: str, client_ip: str, request_id: str) -> None:
            clean_path = path.split("?", 1)[0]
            if clean_path == "/api/agents/start":
                principal = self._require_runtime_principal(client_ip, "POST", clean_path, request_id)
                if not principal or not self._validate_runtime_write(principal, clean_path):
                    return
                runtime = agent_runtime.start_runtime(self._read_json())
                _audit_structured("agent_runtime_started", principal, request_id, client_ip, "POST", clean_path, 202, f"runtime={runtime['id']}")
                self._send_json({"runtime": runtime, "state": agent_runtime.list_state()}, status=HTTPStatus.ACCEPTED)
                return
            if clean_path == "/api/agents/stop":
                principal = self._require_runtime_principal(client_ip, "POST", clean_path, request_id)
                if not principal or not self._validate_runtime_write(principal, clean_path):
                    return
                runtime_id = str(self._read_json().get("runtime_id") or "")
                runtime = agent_runtime.stop_runtime(runtime_id)
                _audit_structured("agent_runtime_stopped", principal, request_id, client_ip, "POST", clean_path, 200, f"runtime={runtime['id']}")
                self._send_json({"runtime": runtime, "state": agent_runtime.list_state()})
                return
            if clean_path == "/api/startup/settings":
                principal = self._require_runtime_principal(client_ip, "POST", clean_path, request_id)
                if not principal:
                    return
                if not _validate_csrf(self._session_key(principal), self.headers.get("X-CSRF-Token")):
                    _inc_metric("csrf_failures")
                    self._send_error_response(HTTPStatus.FORBIDDEN, "invalid or missing CSRF token")
                    return
                if "application/json" not in self.headers.get("Content-Type", "").lower():
                    self._send_error_response(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Content-Type must be application/json")
                    return
                settings = _validate_launcher_settings(self._read_json(), args.host, args.port)
                _save_launcher_settings(settings)
                output_root = Path(str(settings["output_root"]))
                job_store_path = Path(str(settings["job_store_path"]))
                output_root.mkdir(parents=True, exist_ok=True)
                job_store_path.parent.mkdir(parents=True, exist_ok=True)
                os.environ["VULNORAIQ_WEB_OUTPUT_ROOT"] = str(output_root)
                os.environ["VULNORAIQ_JOB_STORE_PATH"] = str(job_store_path)
                os.environ["VULNORAIQ_AGENT_RUNTIME_REGISTRY"] = str(output_root / "agent-runtimes.json")
                os.environ["VULNORAIQ_RUNTIME_TARGETS_PATH"] = str(output_root / "runtime_targets.yaml")
                hosted_runtime.OUTPUT_ROOT = output_root
                hosted_runtime.JOB_STORE = hosted_runtime.create_job_store()
                response = build_startup_status(args.host, args.port, shutdown_allowed)
                response["settings_message"] = (
                    "Settings saved. Output root, job store, and agent runtime paths apply now; host and port apply after restarting the local launcher."
                )
                self._send_json(response)
                return
            if clean_path == "/api/server/shutdown":
                principal = self._require_runtime_principal(client_ip, "POST", clean_path, request_id)
                if not principal:
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
    saved = _load_launcher_settings()
    default_host = str(saved.get("host", "127.0.0.1"))
    try:
        default_port = _coerce_port(saved.get("port", 8787))
    except ValueError:
        default_port = 8787
    parser = argparse.ArgumentParser(description="Launch the local VulnoraIQ Web UI and open it in a browser.")
    parser.add_argument("--host", default=default_host, help="Host/interface to bind. Default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=default_port, help="Port to bind. Default: 8787")
    parser.add_argument("--no-browser", action="store_true", help="Start the server without opening a browser window")
    return parser.parse_args(argv)


def main() -> None:
    raise SystemExit(run_launcher(parse_args()))


if __name__ == "__main__":
    main()
