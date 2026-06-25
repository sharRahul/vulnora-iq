# mypy: ignore-errors
from __future__ import annotations

import argparse
import logging
import os
import threading
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from webui import hosted_server as base
from webui.agent_lab import (
    analyze_agent_project,
    delete_project,
    deploy_agent_project,
    generate_dockerfile_for_project,
    import_archive_project,
    import_git_project,
    list_agent_projects,
    list_deployments,
    provider_presets,
    remove_deployment,
)
from webui.assistant import AssistantOrchestrator

ASSISTANT = AssistantOrchestrator()
LOGGER = logging.getLogger("vulnoraiq.webui")


class AssistantHostedWebUiHandler(base.HostedWebUiHandler):
    """Hosted WebUI handler with assistant and experimental Agent Lab endpoints enabled."""

    def _do_GET_routes(self, path: str, client_ip: str, request_id: str) -> None:
        clean_path = urlparse(path).path
        if clean_path in {"/agent-lab", "/agent-lab/"}:
            self._serve_static("agent-lab/index.html")
            return
        if clean_path == "/api/assistant/config":
            principal = self._require_principal(client_ip, "GET", clean_path, request_id)
            if not principal or not self._check_rate_limit(principal, client_ip):
                return
            if not base.AUTH_MANAGER.can(principal, "view_scans"):
                self._forbidden()
                return
            self._send_json(ASSISTANT.available_config())
            return
        if clean_path == "/api/agent-lab":
            principal = self._require_agent_lab_principal(client_ip, "GET", clean_path, request_id)
            if not principal:
                return
            cfg = base.load_config()
            self._send_json(
                {
                    "experimental": True,
                    "provider_presets": provider_presets(),
                    "projects": list_agent_projects(),
                    "deployments": list_deployments(),
                    "profiles": {k: {"description": v.get("description", "")} for k, v in cfg.get("profiles", {}).items()},
                    "targets": cfg.get("targets", {}),
                }
            )
            return
        if clean_path == "/api/agent-lab/projects":
            principal = self._require_agent_lab_principal(client_ip, "GET", clean_path, request_id)
            if not principal:
                return
            self._send_json({"projects": list_agent_projects()})
            return
        if clean_path.startswith("/api/agent-lab/projects/") and clean_path.endswith("/analyze"):
            principal = self._require_agent_lab_principal(client_ip, "GET", clean_path, request_id)
            if not principal:
                return
            parts = [unquote(item) for item in clean_path.split("/") if item]
            project_id = parts[3]
            self._send_json(analyze_agent_project(project_id))
            return
        if clean_path.startswith("/api/agent-lab/projects/") and clean_path.endswith("/dockerfile"):
            principal = self._require_agent_lab_principal(client_ip, "GET", clean_path, request_id)
            if not principal:
                return
            parts = [unquote(item) for item in clean_path.split("/") if item]
            project_id = parts[3]
            dockerfile = generate_dockerfile_for_project(project_id)
            self._send_json({"exists": bool(dockerfile), "dockerfile": dockerfile or ""})
            return
        if clean_path == "/api/agent-lab/deployments":
            principal = self._require_agent_lab_principal(client_ip, "GET", clean_path, request_id)
            if not principal:
                return
            self._send_json({"deployments": list_deployments()})
            return
        super()._do_GET_routes(path, client_ip, request_id)

    def _do_POST_routes(self, path: str, client_ip: str, request_id: str) -> None:
        clean_path = urlparse(path).path
        if clean_path == "/api/assistant/chat":
            principal = self._require_principal(client_ip, "POST", clean_path, request_id)
            if not principal or not self._check_rate_limit(principal, client_ip):
                return
            if not base._validate_csrf(self._session_key(principal), self.headers.get("X-CSRF-Token")):
                self._send_error_response(HTTPStatus.FORBIDDEN, "invalid or missing CSRF token")
                return
            if not base.AUTH_MANAGER.can(principal, "view_scans"):
                self._forbidden()
                return
            payload = self._read_json()
            response = ASSISTANT.chat(payload, actor=principal.username)
            base._audit_structured(
                "assistant_chat",
                principal,
                request_id,
                client_ip,
                "POST",
                clean_path,
                200,
                f"provider={response.get('provider')} model={response.get('model')}",
            )
            self._send_json(response)
            return
        if clean_path.startswith("/api/agent-lab/"):
            self._handle_agent_lab_post(clean_path, client_ip, request_id)
            return
        super()._do_POST_routes(path, client_ip, request_id)

    def _require_agent_lab_principal(self, client_ip: str, method: str, path: str, request_id: str):
        principal = self._require_principal(client_ip, method, path, request_id)
        if not principal or not self._check_rate_limit(principal, client_ip):
            return None
        if not base.AUTH_MANAGER.can(principal, "manage_runtime"):
            self._forbidden()
            return None
        return principal

    def _validate_agent_lab_csrf(self, principal) -> bool:
        if base._validate_csrf(self._session_key(principal), self.headers.get("X-CSRF-Token")):
            return True
        self._send_error_response(HTTPStatus.FORBIDDEN, "invalid or missing CSRF token")
        return False

    def _handle_agent_lab_post(self, clean_path: str, client_ip: str, request_id: str) -> None:
        principal = self._require_agent_lab_principal(client_ip, "POST", clean_path, request_id)
        if not principal or not self._validate_agent_lab_csrf(principal):
            return
        payload = self._read_json()
        if clean_path == "/api/agent-lab/import/git":
            result = import_git_project(
                str(payload.get("url") or ""),
                project_id=str(payload.get("project_id") or "") or None,
                branch=str(payload.get("branch") or "") or None,
            )
            base._audit_structured("agent_lab_import_git", principal, request_id, client_ip, "POST", clean_path, 200, result.project_id)
            self._send_json({"imported": True, **result.__dict__})
            return
        if clean_path == "/api/agent-lab/import/archive":
            result = import_archive_project(str(payload.get("archive_base64") or ""), str(payload.get("project_id") or ""))
            base._audit_structured("agent_lab_import_archive", principal, request_id, client_ip, "POST", clean_path, 200, result.project_id)
            self._send_json({"imported": True, **result.__dict__})
            return
        if clean_path.startswith("/api/agent-lab/projects/") and clean_path.endswith("/deploy"):
            parts = [unquote(item) for item in clean_path.split("/") if item]
            project_id = parts[3]
            result = deploy_agent_project(project_id, payload, base._save_runtime_target)
            base._audit_structured("agent_lab_deploy", principal, request_id, client_ip, "POST", clean_path, 200, result.project_id)
            self._send_json({"deployed": True, **result.__dict__})
            return
        if clean_path.startswith("/api/agent-lab/projects/") and clean_path.endswith("/delete"):
            parts = [unquote(item) for item in clean_path.split("/") if item]
            project_id = parts[3]
            deleted = delete_project(project_id)
            base._audit_structured("agent_lab_delete_project", principal, request_id, client_ip, "POST", clean_path, 200, project_id)
            self._send_json({"deleted": deleted, "project_id": project_id})
            return
        if clean_path.startswith("/api/agent-lab/deployments/") and clean_path.endswith("/remove"):
            parts = [unquote(item) for item in clean_path.split("/") if item]
            project_id = parts[3]
            result = remove_deployment(project_id)
            base._audit_structured("agent_lab_remove_deployment", principal, request_id, client_ip, "POST", clean_path, 200, project_id)
            self._send_json(result)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")


def create_server(host: str = "127.0.0.1", port: int = 8787) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), AssistantHostedWebUiHandler)


def main() -> None:
    logging.basicConfig(
        level=os.getenv("VULNORAIQ_LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    audit_handler = logging.StreamHandler()
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(logging.Formatter("%(asctime)s AUDIT %(message)s"))
    base.AUDIT_LOG.addHandler(audit_handler)
    base.AUDIT_LOG.propagate = False
    parser = argparse.ArgumentParser(description="Run the VulnoraIQ hosted web UI.")
    parser.add_argument("--host", default=os.getenv("VULNORAIQ_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("VULNORAIQ_PORT", "8787")))
    parser.add_argument("--production", action="store_true", help="Enable production mode validation")
    parser.add_argument("--skip-production-checks", action="store_true", help="Skip production config validation")
    args = parser.parse_args()
    if args.production or base.AUTH_MANAGER.is_production():
        try:
            base.AUTH_MANAGER._validate_production()
        except RuntimeError as exc:
            LOGGER.error("production_mode_validation_failed: %s", exc)
            raise SystemExit(1) from exc
        if not args.skip_production_checks:
            results = base.validate_all(host=args.host)
            failed = [r for r in results if r["status"] != "pass"]
            if failed:
                raise SystemExit(1)
    threading.Thread(target=base._rate_limit_cleanup_loop, daemon=True).start()
    create_server(args.host, args.port).serve_forever()


__all__: list[str] = ["AssistantHostedWebUiHandler", "create_server", "main"]


if __name__ == "__main__":
    main()
