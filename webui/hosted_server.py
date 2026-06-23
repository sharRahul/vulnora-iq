from __future__ import annotations

import argparse
import ipaddress
import json
import logging
import mimetypes
import os
import secrets
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import yaml

from core.scanner import Scanner
from dashboards.generate_dashboard import DashboardGenerator
from dashboards.html_dashboard import HtmlDashboardGenerator
from reports.json_report_generator import JsonReportGenerator
from reports.report_generator import MarkdownReportGenerator
from reports.sarif_report_generator import SarifReportGenerator
from webui.auth import AuthPrincipal, WebAuthManager
from webui.persistent_jobs import JobStore, PersistedScanJob, create_job_store
from webui.production_checks import ProductionConfigError, validate_all

LOGGER = logging.getLogger("vulnoraiq.webui")
AUDIT_LOG = logging.getLogger("vulnoraiq.audit")
STATIC_DIR = Path(__file__).parent / "static"
CONFIG_ROOT = Path(os.getenv("VULNORAIQ_CONFIG_DIR", "config"))
OUTPUT_ROOT = Path(os.getenv("VULNORAIQ_WEB_OUTPUT_ROOT", "reports/output/webui"))
TERMINAL_STATES = {"completed", "failed"}
AUTH_MANAGER = WebAuthManager(os.getenv("VULNORAIQ_WEB_USERS_PATH", str(CONFIG_ROOT / "web_users.yaml")))
JOB_STORE: JobStore = create_job_store()
STARTED_AT = datetime.now(timezone.utc)

# Security limits
MAX_REQUEST_BODY = int(os.getenv("VULNORAIQ_MAX_REQUEST_BODY", str(10 * 1024 * 1024)))
RATE_LIMIT_WINDOW = int(os.getenv("VULNORAIQ_RATE_LIMIT_WINDOW", "60"))
RATE_LIMIT_MAX = int(os.getenv("VULNORAIQ_RATE_LIMIT_MAX", "60"))

# Proxy trust settings
TRUST_PROXY_HEADERS = os.getenv("VULNORAIQ_TRUST_PROXY_HEADERS", "false").strip().lower() in ("1", "true", "yes")
_TRUSTED_PROXY_CIDRS_ENV = os.getenv("VULNORAIQ_TRUSTED_PROXY_CIDRS", "")
TRUSTED_PROXY_NETS: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
if TRUST_PROXY_HEADERS and _TRUSTED_PROXY_CIDRS_ENV:
    for cidr in _TRUSTED_PROXY_CIDRS_ENV.split(","):
        cidr = cidr.strip()
        if cidr:
            TRUSTED_PROXY_NETS.append(ipaddress.ip_network(cidr, strict=False))

# Scan concurrency limits
MAX_CONCURRENT_SCANS = int(os.getenv("VULNORAIQ_MAX_CONCURRENT_SCANS", "5"))
SCAN_QUEUE_LIMIT = int(os.getenv("VULNORAIQ_SCAN_QUEUE_LIMIT", "20"))
_active_scans: set[str] = set()
_active_scans_lock = threading.Lock()

# Rate limiter state
_rate_limit_store: dict[str, list[float]] = {}
_rate_limit_lock = threading.Lock()

# CSRF token store
_csrf_tokens: dict[str, dict[str, Any]] = {}
_csrf_token_lock = threading.Lock()
CSRF_TOKEN_TTL = int(os.getenv("VULNORAIQ_CSRF_TOKEN_TTL", "300"))

# Metrics counters
_metrics: dict[str, int] = {}
_metrics_lock = threading.Lock()


def _inc_metric(name: str) -> None:
    with _metrics_lock:
        _metrics[name] = _metrics.get(name, 0) + 1


def _get_metrics_snapshot() -> dict[str, int]:
    with _active_scans_lock:
        active_count = len(_active_scans)
    with _metrics_lock:
        snapshot = dict(_metrics)
    snapshot["active_scans"] = active_count
    return snapshot


def _resolve_client_ip(handler: BaseHTTPRequestHandler) -> str:
    direct_ip = handler.client_address[0]
    if not TRUST_PROXY_HEADERS:
        return direct_ip
    try:
        addr = ipaddress.ip_address(direct_ip)
    except ValueError:
        return direct_ip
    is_trusted = any(addr in net for net in TRUSTED_PROXY_NETS)
    if not is_trusted:
        return direct_ip
    forwarded = handler.headers.get("X-Forwarded-For", "").strip()
    if forwarded:
        client = forwarded.split(",")[0].strip()
        try:
            ipaddress.ip_address(client)
            return client
        except ValueError:
            pass
    return direct_ip


def _is_trusted_proxy(handler: BaseHTTPRequestHandler) -> bool:
    if not TRUST_PROXY_HEADERS:
        return False
    try:
        addr = ipaddress.ip_address(handler.client_address[0])
    except ValueError:
        return False
    return any(addr in net for net in TRUSTED_PROXY_NETS)


def _generate_request_id() -> str:
    return uuid.uuid4().hex[:16]


def _safe_audit_field(value: str | None, max_len: int = 200) -> str:
    if value is None:
        return ""
    return value[:max_len].replace("\n", "\\n").replace("\r", "\\r")


def _audit_structured(
    event: str,
    principal: AuthPrincipal,
    request_id: str = "",
    client_ip: str = "",
    method: str = "",
    path: str = "",
    status: int = 0,
    detail: str = "",
) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": _safe_audit_field(event),
        "request_id": _safe_audit_field(request_id),
        "user": _safe_audit_field(principal.username),
        "role": _safe_audit_field(principal.role),
        "authenticated": str(principal.authenticated).lower(),
        "client_ip": _safe_audit_field(client_ip),
        "method": _safe_audit_field(method),
        "path": _safe_audit_field(path),
        "status": status,
        "detail": _safe_audit_field(detail),
    }
    AUDIT_LOG.info(json.dumps(record, default=str))


def _rate_limit(client_ip: str) -> bool:
    now = time.monotonic()
    with _rate_limit_lock:
        timestamps = _rate_limit_store.get(client_ip, [])
        timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        if len(timestamps) >= RATE_LIMIT_MAX:
            return False
        timestamps.append(now)
        _rate_limit_store[client_ip] = timestamps
    return True


def _clean_rate_limit_store() -> None:
    now = time.monotonic()
    with _rate_limit_lock:
        expired: list[str] = []
        for ip, timestamps in _rate_limit_store.items():
            _rate_limit_store[ip] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
            if not _rate_limit_store[ip]:
                expired.append(ip)
        for ip in expired:
            del _rate_limit_store[ip]


def _csrf_session_key(principal: AuthPrincipal, client_ip: str) -> str:
    if principal.authenticated:
        return f"user:{principal.username}"
    return f"ip:{client_ip}"


def _csrf_token_for(session_key: str) -> str:
    now = time.monotonic()
    with _csrf_token_lock:
        entry = _csrf_tokens.get(session_key)
        if entry and entry["expires"] > now:
            return entry["token"]
        token = secrets.token_urlsafe(32)
        _csrf_tokens[session_key] = {"token": token, "expires": now + CSRF_TOKEN_TTL}
        return token


def _validate_csrf(session_key: str, provided_token: str | None) -> bool:
    if not provided_token:
        return False
    now = time.monotonic()
    with _csrf_token_lock:
        entry = _csrf_tokens.get(session_key)
        if not entry:
            return False
        if entry["expires"] <= now:
            _csrf_tokens.pop(session_key, None)
            return False
        return secrets.compare_digest(entry["token"], provided_token)


def _clean_csrf_store() -> None:
    now = time.monotonic()
    with _csrf_token_lock:
        expired = [k for k, v in _csrf_tokens.items() if v["expires"] <= now]
        for k in expired:
            del _csrf_tokens[k]


def load_config() -> dict[str, Any]:
    def read_yaml(path: str) -> dict[str, Any]:
        file_path = CONFIG_ROOT / path
        if not file_path.exists():
            return {}
        return yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}

    return {
        "targets": read_yaml("targets.yaml").get("targets", {}),
        "profiles": read_yaml("attack_profiles.yaml").get("profiles", {}),
        "web_auth_enabled": AUTH_MANAGER.enabled(),
    }


def validate_scan_request(payload: dict[str, Any]) -> tuple[str, str, bool]:
    config = load_config()
    target = str(payload.get("target") or "demo")
    profile = str(payload.get("profile") or "baseline")
    authorised = bool(payload.get("authorised", False))
    if target not in config["targets"]:
        raise ValueError(f"Unknown target: {target}")
    if profile not in config["profiles"]:
        raise ValueError(f"Unknown profile: {profile}")
    return target, profile, authorised


def _acquire_scan_slot(job_id: str) -> bool:
    with _active_scans_lock:
        if len(_active_scans) >= MAX_CONCURRENT_SCANS:
            return False
        _active_scans.add(job_id)
    return True


def _release_scan_slot(job_id: str) -> None:
    with _active_scans_lock:
        _active_scans.discard(job_id)


def run_scan_job(job_id: str) -> None:
    if not _acquire_scan_slot(job_id):
        LOGGER.warning("scan_slot_denied job_id=%s max_concurrent=%d", job_id, MAX_CONCURRENT_SCANS)
        return

    def mutate(fn: Callable[[PersistedScanJob], None]) -> None:
        JOB_STORE.update(job_id, fn)

    try:
        def start_job(job: PersistedScanJob) -> None:
            job.status = "running"
            job.started_at = datetime.now(timezone.utc).isoformat()
            job.add_event("initialising", "Loading scanner configuration and selected profile.", 8)
        mutate(start_job)
        job = JOB_STORE.get(job_id)
        if not job:
            LOGGER.warning("scan_job_missing job_id=%s", job_id)
            return
        LOGGER.info("scan_job_started job_id=%s target=%s profile=%s", job.id, job.target, job.profile)
        mutate(lambda item: item.add_event("scanning", f"Running {job.profile} profile against {job.target}.", 25))
        result = Scanner().scan(target_name=job.target, profile_name=job.profile, authorised=job.authorised)

        mutate(lambda item: item.add_event("policy", "Scan completed; evaluating policies and scoring findings.", 55))
        output_dir = OUTPUT_ROOT / job.id
        output_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = MarkdownReportGenerator().generate(result, output_dir / "scan-report.md")
        json_path = JsonReportGenerator().generate(result, output_dir / "scan-report.json")
        sarif_path = SarifReportGenerator().generate(result, output_dir / "scan-report.sarif")

        mutate(lambda item: item.add_event("dashboard", "Rendering Markdown and HTML dashboards.", 75))
        report_data = json.loads(json_path.read_text(encoding="utf-8"))
        dashboard_path = DashboardGenerator().generate_from_report(report_data, output_dir / "dashboard.md")
        html_dashboard_path = HtmlDashboardGenerator().generate_from_report(report_data, output_dir / "dashboard.html")

        def complete(item: PersistedScanJob) -> None:
            item.status = "completed"
            item.completed_at = datetime.now(timezone.utc).isoformat()
            item.outputs = {
                "markdown": str(markdown_path),
                "json": str(json_path),
                "sarif": str(sarif_path),
                "dashboard_markdown": str(dashboard_path),
                "dashboard_html": str(html_dashboard_path),
            }
            item.summary = {
                "target": report_data.get("target"),
                "profile": report_data.get("profile"),
                "finding_count": report_data.get("finding_count"),
                "highest_severity": report_data.get("highest_severity"),
                "policy_status": report_data.get("policy_status"),
                "severity_counts": report_data.get("severity_counts", {}),
                "policy_results": report_data.get("policy_results", []),
                "findings": report_data.get("findings", []),
            }
            item.add_event("completed", "Scan completed and reports are ready.", 100)

        mutate(complete)
        _inc_metric("scans_completed")
        LOGGER.info("scan_job_completed job_id=%s target=%s profile=%s", job.id, job.target, job.profile)
    except Exception:  # pragma: no cover
        _inc_metric("scans_failed")
        LOGGER.exception("scan_job_failed job_id=%s", job_id)
        err_msg = "internal scan error"

        def fail(item: PersistedScanJob) -> None:
            item.status = "failed"
            item.error = err_msg
            item.completed_at = datetime.now(timezone.utc).isoformat()
            item.add_event("failed", err_msg, 100, level="error")

        mutate(fail)
    finally:
        _release_scan_slot(job_id)


class HostedWebUiHandler(BaseHTTPRequestHandler):
    server_version = "VulnoraIQWebUI/0.2.0"

    def _client_ip(self) -> str:
        return _resolve_client_ip(self)

    def _session_key(self, principal: AuthPrincipal) -> str:
        client_ip = self._client_ip()
        return _csrf_session_key(principal, client_ip)

    def _request_id(self) -> str:
        req_id = self.headers.get("X-Request-ID", "").strip()
        if req_id and len(req_id) <= 64 and req_id.isalnum():
            return req_id
        return _generate_request_id()

    def _security_headers(self, suppress_hsts: bool = False) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-XSS-Protection", "0")
        if not suppress_hsts:
            forwarded_proto = self.headers.get("X-Forwarded-Proto", "").strip().lower()
            if TRUST_PROXY_HEADERS and forwarded_proto == "https":
                self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
            elif not TRUST_PROXY_HEADERS and self._client_ip() == "127.0.0.1":
                pass
            else:
                self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; form-action 'self'; base-uri 'self'; frame-ancestors 'none'",
        )
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

    def _check_rate_limit(self, principal: AuthPrincipal, client_ip: str) -> bool:
        if not _rate_limit(client_ip):
            _inc_metric("rate_limit_exceeded")
            LOGGER.warning("rate_limit_exceeded ip=%s user=%s", client_ip, principal.username)
            _audit_structured("rate_limit_exceeded", principal, client_ip=client_ip, detail="rate limit exceeded")
            self._send_json({"error": "rate limit exceeded"}, status=HTTPStatus.TOO_MANY_REQUESTS)
            return False
        return True

    def _send_error_response(self, status: HTTPStatus, message: str) -> None:
        self._send_json({"error": message}, status=status)

    def _principal(self, client_ip: str) -> AuthPrincipal | None:
        mode = AUTH_MANAGER.auth_mode()
        if mode == "trusted_proxy":
            headers_dict = {k: self.headers.get(k, "") for k in (
                "X-Authenticated-User", "X-Authenticated-Email",
                "X-Authenticated-Groups", "X-VulnoraIQ-Role",
            )}
            return AUTH_MANAGER.authenticate_proxy_identity(
                headers_dict, trusted=_is_trusted_proxy(self),
            )
        token = self.headers.get(AUTH_MANAGER.header_name())
        return AUTH_MANAGER.authenticate_token(token)

    def _handle_request(self, method: str, path: str) -> None:
        request_id = self._request_id()
        client_ip = self._client_ip()

        try:
            self._do_route(method, path, client_ip, request_id)
        except ValueError as exc:
            _inc_metric("bad_request")
            _audit_structured("malformed_json", AUTH_MANAGER.anonymous(), request_id, client_ip, method, path, 400, str(exc))
            self._send_error_response(HTTPStatus.BAD_REQUEST, str(exc))
        except Exception:  # pragma: no cover
            _inc_metric("internal_error")
            LOGGER.exception("internal_error method=%s path=%s", method, path)
            _audit_structured("internal_error", AUTH_MANAGER.anonymous(), request_id, client_ip, method, path, 500, "internal server error")
            self._send_error_response(HTTPStatus.INTERNAL_SERVER_ERROR, "internal server error")

    def _do_route(self, method: str, path: str, client_ip: str, request_id: str) -> None:
        if method == "GET":
            self._do_GET_routes(path, client_ip, request_id)
        elif method == "POST":
            self._do_POST_routes(path, client_ip, request_id)
        else:
            self.send_error(HTTPStatus.METHOD_NOT_ALLOWED, "Method not allowed")

    def _do_GET_routes(self, path: str, client_ip: str, request_id: str) -> None:
        parsed = urlparse(path)
        clean_path = parsed.path
        req_id = request_id

        if clean_path == "/healthz":
            self._send_json({"status": "ok", "service": "vulnoraiq-web", "started_at": STARTED_AT.isoformat()})
            return
        if clean_path == "/readyz":
            config = load_config()
            ready = bool(config.get("targets")) and bool(config.get("profiles"))
            self._send_json(
                {
                    "status": "ready" if ready else "not_ready",
                    "targets_loaded": len(config.get("targets", {})),
                    "profiles_loaded": len(config.get("profiles", {})),
                    "auth_enabled": config.get("web_auth_enabled", False),
                },
                status=HTTPStatus.OK if ready else HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return
        if clean_path == "/api/session":
            # Public endpoint: lets the UI discover whether auth is required and,
            # if a token was supplied, the current identity and permissions.
            session_principal = self._principal(client_ip)
            auth_enabled = AUTH_MANAGER.enabled()
            authenticated = bool(session_principal and session_principal.authenticated)
            self._send_json(
                {
                    "auth_enabled": auth_enabled,
                    "authenticated": authenticated,
                    "auth_required": auth_enabled and session_principal is None,
                    "token_header": AUTH_MANAGER.header_name(),
                    "username": session_principal.username if session_principal else None,
                    "role": session_principal.role if session_principal else None,
                    "permissions": sorted(session_principal.permissions) if session_principal else [],
                }
            )
            return
        if clean_path == "/metrics":
            if os.getenv("VULNORAIQ_METRICS_AUTH_REQUIRED", "true").strip().lower() in ("1", "true", "yes"):
                principal = self._principal(client_ip)
                if not principal:
                    _audit_structured("auth_failure", AUTH_MANAGER.anonymous(), req_id, client_ip, "GET", clean_path, 401, "metrics auth required")
                    self._send_error_response(HTTPStatus.UNAUTHORIZED, "authentication required")
                    return
            self._serve_metrics()
            return

        # Static UI assets are public so the page can load and present a sign-in
        # prompt; all /api/* data endpoints below remain behind authentication.
        if clean_path == "/":
            self._serve_static("index.html")
            return
        if clean_path.startswith("/static/"):
            self._serve_static(clean_path.removeprefix("/static/"))
            return

        principal = self._principal(client_ip)
        if not principal:
            _inc_metric("auth_failures")
            _audit_structured("auth_failure", AUTH_MANAGER.anonymous(), req_id, client_ip, "GET", clean_path, 401, "no token provided")
            self._send_error_response(HTTPStatus.UNAUTHORIZED, "authentication required")
            return

        if not self._check_rate_limit(principal, client_ip):
            return

        if clean_path == "/api/csrf-token":
            session_key = self._session_key(principal)
            token = _csrf_token_for(session_key)
            self._send_json({"csrf_token": token})
            return
        if clean_path == "/api/config":
            full_config = load_config()
            if AUTH_MANAGER.can(principal, "manage_runtime"):
                safe_config = full_config
            else:
                safe_config = {
                    "profiles": {k: {"description": v.get("description", "")} for k, v in full_config.get("profiles", {}).items()},
                    "web_auth_enabled": full_config.get("web_auth_enabled", False),
                }
            self._send_json(safe_config)
            return
        if clean_path == "/api/scans":
            if not AUTH_MANAGER.can(principal, "view_scans"):
                _inc_metric("authz_failures")
                _audit_structured("authz_failure", principal, req_id, client_ip, "GET", clean_path, 403, "view_scans")
                self._forbidden()
                return
            self._send_json({"jobs": [job.to_dict(include_events=False) for job in JOB_STORE.list()]})
            return
        if clean_path.startswith("/api/scans/"):
            self._handle_scan_get(clean_path, principal, client_ip, req_id)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def _do_POST_routes(self, path: str, client_ip: str, request_id: str) -> None:
        clean_path = path
        req_id = request_id

        principal = self._principal(client_ip)
        if not principal:
            _inc_metric("auth_failures")
            _audit_structured("auth_failure", AUTH_MANAGER.anonymous(), req_id, client_ip, "POST", clean_path, 401, "no token provided")
            self._send_error_response(HTTPStatus.UNAUTHORIZED, "authentication required")
            return

        if not self._check_rate_limit(principal, client_ip):
            return

        if clean_path == "/api/scans":
            session_key = self._session_key(principal)
            csrf_token = self.headers.get("X-CSRF-Token")
            if not _validate_csrf(session_key, csrf_token):
                _inc_metric("csrf_failures")
                _audit_structured("csrf_failure", principal, req_id, client_ip, "POST", clean_path, 403, "invalid or missing CSRF token")
                self._send_error_response(HTTPStatus.FORBIDDEN, "invalid or missing CSRF token")
                return

            content_length_raw = self.headers.get("Content-Length", "0")
            if not content_length_raw.isdigit():
                _inc_metric("bad_request")
                _audit_structured("malformed_json", principal, req_id, client_ip, "POST", clean_path, 400, "invalid Content-Length")
                self._send_error_response(HTTPStatus.BAD_REQUEST, "invalid Content-Length")
                return

            length = int(content_length_raw)
            if length > MAX_REQUEST_BODY:
                _inc_metric("oversized_request")
                _audit_structured("oversized_request", principal, req_id, client_ip, "POST", clean_path, 413, f"request body exceeds {MAX_REQUEST_BODY} bytes")
                self._send_error_response(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, f"request body exceeds maximum allowed size ({MAX_REQUEST_BODY} bytes)")
                return

            try:
                raw_body = self.rfile.read(length).decode("utf-8")
                payload = json.loads(raw_body)
            except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                _inc_metric("bad_request")
                _audit_structured("malformed_json", principal, req_id, client_ip, "POST", clean_path, 400, "malformed JSON body")
                self._send_error_response(HTTPStatus.BAD_REQUEST, "invalid JSON in request body")
                return

            target, profile, authorised = validate_scan_request(payload)
            required_permission = "start_demo_scan" if target == "demo" else "start_configured_scan"
            if not AUTH_MANAGER.can(principal, required_permission):
                _inc_metric("authz_failures")
                _audit_structured("authz_failure", principal, req_id, client_ip, "POST", clean_path, 403, f"missing {required_permission}")
                self._forbidden()
                return

            # Check concurrency limits
            with _active_scans_lock:
                if len(_active_scans) >= SCAN_QUEUE_LIMIT:
                    _inc_metric("scan_queue_full")
                    _audit_structured("scan_queue_full", principal, req_id, client_ip, "POST", clean_path, 429, "scan queue at capacity")
                    self._send_error_response(HTTPStatus.TOO_MANY_REQUESTS, "scan queue at capacity")
                    return

            job = JOB_STORE.create(target, profile, authorised, created_by=principal.username)
            _inc_metric("scans_created")
            _audit_structured("scan_created", principal, req_id, client_ip, "POST", clean_path, 202, f"target={target} profile={profile} job_id={job.id}")
            LOGGER.info("scan_job_accepted job_id=%s target=%s profile=%s user=%s",
                        job.id, target, profile, principal.username)
            threading.Thread(target=run_scan_job, args=(job.id,), daemon=True).start()
            self._send_json(job.to_dict(), status=HTTPStatus.ACCEPTED)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_GET(self) -> None:  # noqa: N802
        self._handle_request("GET", self.path)

    def do_POST(self) -> None:  # noqa: N802
        self._handle_request("POST", self.path)

    def _handle_scan_get(self, path: str, principal: AuthPrincipal, client_ip: str, request_id: str) -> None:
        parts = [unquote(item) for item in path.split("/") if item]
        if len(parts) < 3:
            self.send_error(HTTPStatus.NOT_FOUND, "Scan not found")
            return
        job_id = parts[2]
        job = JOB_STORE.get(job_id)
        if not job:
            self.send_error(HTTPStatus.NOT_FOUND, "Scan not found")
            return
        if len(parts) == 3:
            if not AUTH_MANAGER.can(principal, "view_scans"):
                _inc_metric("authz_failures")
                _audit_structured("authz_failure", principal, request_id, client_ip, "GET", path, 403, "view_scans")
                self._forbidden()
                return
            self._send_json(job.to_dict())
            return
        action = parts[3]
        if action == "events":
            if not AUTH_MANAGER.can(principal, "view_scans"):
                _audit_structured("authz_failure", principal, request_id, client_ip, "GET", path, 403, "view_scans")
                self._forbidden()
                return
            self._send_events(job_id)
            return
        if action == "artifact" and len(parts) == 5:
            if not AUTH_MANAGER.can(principal, "download_artifacts"):
                _inc_metric("authz_failures")
                _audit_structured("authz_failure", principal, request_id, client_ip, "GET", path, 403, "download_artifacts")
                self._forbidden()
                return
            self._send_artifact(job, parts[4], client_ip, request_id)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Scan resource not found")

    def _send_artifact(self, job: PersistedScanJob, artifact_name: str, client_ip: str, request_id: str) -> None:
        name = artifact_name.replace("\\", "/")
        if "/" in name or ".." in name:
            _audit_structured("artifact_traversal_attempt", AUTH_MANAGER.anonymous(), request_id, client_ip, "GET", f"/api/scans/{job.id}/artifact/{artifact_name}", 400, "path traversal detected")
            self._send_error_response(HTTPStatus.BAD_REQUEST, "invalid artifact name")
            return

        path = job.outputs.get(artifact_name)
        if not path:
            self.send_error(HTTPStatus.NOT_FOUND, "Artifact not found")
            return
        file_path = Path(path)
        if not file_path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Artifact file not found")
            return
        data = file_path.read_bytes()
        _inc_metric("artifact_downloads")
        _audit_structured("artifact_download", self._principal(client_ip) or AUTH_MANAGER.anonymous(),
                          request_id, client_ip, "GET", f"/api/scans/{job.id}/artifact/{artifact_name}", 200,
                          f"artifact={artifact_name} job={job.id}")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(file_path.name)[0] or "application/octet-stream")
        safe_filename = file_path.name.replace('"', "")
        self.send_header("Content-Disposition", f'attachment; filename="{safe_filename}"')
        self.send_header("Content-Length", str(len(data)))
        self._security_headers()
        self.end_headers()
        self.wfile.write(data)

    def _send_events(self, job_id: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self._security_headers()
        self.end_headers()
        sent = 0
        while True:
            job = JOB_STORE.get(job_id)
            if not job:
                return
            for event in job.events[sent:]:
                self.wfile.write(f"data: {json.dumps(asdict(event), default=str)}\n\n".encode())
                self.wfile.flush()
                sent += 1
            if job.status in TERMINAL_STATES:
                self.wfile.write(f"event: done\ndata: {json.dumps(job.to_dict(), default=str)}\n\n".encode())
                self.wfile.flush()
                return
            time.sleep(0.4)

    def _serve_static(self, relative_path: str) -> None:
        safe_relative = Path(relative_path)
        if safe_relative.is_absolute() or ".." in safe_relative.parts:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid path")
            return
        file_path = STATIC_DIR / safe_relative
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Static file not found")
            return
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(file_path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self._security_headers()
        self.end_headers()
        self.wfile.write(data)

    def _serve_metrics(self) -> None:
        metrics = _get_metrics_snapshot()
        lines = [
            "# HELP vulnoraiq_up Process uptime",
            "# TYPE vulnoraiq_up gauge",
            "vulnoraiq_up 1",
            "# HELP vulnoraiq_started_at Unix timestamp when the process started",
            "# TYPE vulnoraiq_started_at gauge",
            f"vulnoraiq_started_at {STARTED_AT.timestamp():.0f}",
            "# HELP vulnoraiq_http_requests_total Total HTTP requests by method",
            "# TYPE vulnoraiq_http_requests_total counter",
        ]
        for method in ("GET", "POST"):
            count = metrics.get(f"http_{method}_total", 0)
            lines.append(f'vulnoraiq_http_requests_total{{method="{method}"}} {count}')
        lines.extend([
            "# HELP vulnoraiq_auth_failures_total Authentication failure count",
            "# TYPE vulnoraiq_auth_failures_total counter",
            f"vulnoraiq_auth_failures_total {metrics.get('auth_failures', 0)}",
            "# HELP vulnoraiq_authz_failures_total Authorization failure count",
            "# TYPE vulnoraiq_authz_failures_total counter",
            f"vulnoraiq_authz_failures_total {metrics.get('authz_failures', 0)}",
            "# HELP vulnoraiq_csrf_failures_total CSRF validation failure count",
            "# TYPE vulnoraiq_csrf_failures_total counter",
            f"vulnoraiq_csrf_failures_total {metrics.get('csrf_failures', 0)}",
            "# HELP vulnoraiq_rate_limit_exceeded_total Rate limit exceeded count",
            "# TYPE vulnoraiq_rate_limit_exceeded_total counter",
            f"vulnoraiq_rate_limit_exceeded_total {metrics.get('rate_limit_exceeded', 0)}",
            "# HELP vulnoraiq_scans_created_total Total scans created",
            "# TYPE vulnoraiq_scans_created_total counter",
            f"vulnoraiq_scans_created_total {metrics.get('scans_created', 0)}",
            "# HELP vulnoraiq_scans_completed_total Total scans completed",
            "# TYPE vulnoraiq_scans_completed_total counter",
            f"vulnoraiq_scans_completed_total {metrics.get('scans_completed', 0)}",
            "# HELP vulnoraiq_scans_failed_total Total scans failed",
            "# TYPE vulnoraiq_scans_failed_total counter",
            f"vulnoraiq_scans_failed_total {metrics.get('scans_failed', 0)}",
            "# HELP vulnoraiq_active_scans Currently active scan count",
            "# TYPE vulnoraiq_active_scans gauge",
            f"vulnoraiq_active_scans {metrics.get('active_scans', 0)}",
            "# HELP vulnoraiq_artifact_downloads_total Artifact download count",
            "# TYPE vulnoraiq_artifact_downloads_total counter",
            f"vulnoraiq_artifact_downloads_total {metrics.get('artifact_downloads', 0)}",
            "# HELP vulnoraiq_bad_requests_total Malformed request count",
            "# TYPE vulnoraiq_bad_requests_total counter",
            f"vulnoraiq_bad_requests_total {metrics.get('bad_request', 0)}",
            "# HELP vulnoraiq_oversized_requests_total Oversized request count",
            "# TYPE vulnoraiq_oversized_requests_total counter",
            f"vulnoraiq_oversized_requests_total {metrics.get('oversized_request', 0)}",
            "# HELP vulnoraiq_scan_queue_full_total Scan queue full rejections",
            "# TYPE vulnoraiq_scan_queue_full_total counter",
            f"vulnoraiq_scan_queue_full_total {metrics.get('scan_queue_full', 0)}",
            "# HELP vulnoraiq_internal_errors_total Internal server error count",
            "# TYPE vulnoraiq_internal_errors_total counter",
            f"vulnoraiq_internal_errors_total {metrics.get('internal_error', 0)}",
            "# HELP vulnoraiq_build_info Build and version information",
            "# TYPE vulnoraiq_build_info gauge",
            f'vulnoraiq_build_info{{version="{self.server_version}",backend="sqlite"}} 1',
        ])
        data = "\n".join(lines).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(data)))
        self._security_headers()
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length", "0")
        if not raw_length.isdigit():
            raise ValueError("invalid Content-Length")
        length = int(raw_length)
        if length <= 0:
            return {}
        if length > MAX_REQUEST_BODY:
            raise ValueError(f"Request body exceeds maximum allowed size ({MAX_REQUEST_BODY} bytes)")
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(f"invalid JSON: {exc}") from exc

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, indent=2, sort_keys=True, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Request-ID", self._request_id())
        self._security_headers()
        self.end_headers()
        self.wfile.write(data)

    def _forbidden(self) -> None:
        self._send_json({"error": "forbidden"}, status=HTTPStatus.FORBIDDEN)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        LOGGER.info("http_request client=%s message=%s", self.address_string(), format % args)

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        try:
            self.send_response(code)
            if message:
                self.send_header("Content-Type", "text/plain")
                body = message.encode("utf-8")
                self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Request-ID", self._request_id())
            self._security_headers()
            self.end_headers()
            if message:
                self.wfile.write(body)
        except OSError:
            pass


def create_server(host: str = "127.0.0.1", port: int = 8787) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), HostedWebUiHandler)


def _rate_limit_cleanup_loop() -> None:
    while True:
        time.sleep(RATE_LIMIT_WINDOW)
        _clean_rate_limit_store()
        _clean_csrf_store()


def main() -> None:
    logging.basicConfig(
        level=os.getenv("VULNORAIQ_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    audit_handler = logging.StreamHandler()
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(logging.Formatter("%(asctime)s AUDIT %(message)s"))
    AUDIT_LOG.addHandler(audit_handler)
    AUDIT_LOG.propagate = False

    parser = argparse.ArgumentParser(description="Run the VulnoraIQ hosted web UI.")
    parser.add_argument("--host", default=os.getenv("VULNORAIQ_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("VULNORAIQ_PORT", "8787")))
    parser.add_argument("--production", action="store_true", help="Enable production mode validation")
    parser.add_argument("--skip-production-checks", action="store_true", help="Skip production config validation")
    args = parser.parse_args()

    if args.production or AUTH_MANAGER.is_production():
        try:
            AUTH_MANAGER._validate_production()
        except RuntimeError as exc:
            LOGGER.error("production_mode_validation_failed: %s", exc)
            raise SystemExit(1) from exc

        if not args.skip_production_checks:
            try:
                results = validate_all(host=args.host)
                failed = [r for r in results if r["status"] != "pass"]
                if failed:
                    for fail in failed:
                        LOGGER.error("PRODUCTION_CONFIG_FAILURE check=%s error=%s", fail["check"], fail.get("error", "unknown"))
                    raise ProductionConfigError(f"Production config validation failed ({len(failed)} checks).")
                LOGGER.info("All production configuration checks passed (%d checks).", len(results))
            except ProductionConfigError:
                raise SystemExit(1) from None

    threading.Thread(target=_rate_limit_cleanup_loop, daemon=True).start()
    server = create_server(args.host, args.port)
    env_label = "production" if AUTH_MANAGER.is_production() else "development"
    LOGGER.info("web_ui_started env=%s url=http://%s:%s auth_enabled=%s backend=%s",
                env_label, args.host, args.port, AUTH_MANAGER.enabled(),
                os.getenv("VULNORAIQ_JOB_STORE_BACKEND", "sqlite"))
    _audit_structured("server_start", AUTH_MANAGER.anonymous(), "",
                      "", "", "", 0, f"env={env_label} host={args.host} port={args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
