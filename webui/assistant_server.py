from __future__ import annotations

import argparse
import logging
import os
import threading
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from webui import hosted_server as base
from webui.assistant import AssistantOrchestrator

ASSISTANT = AssistantOrchestrator()
LOGGER = logging.getLogger("vulnoraiq.webui")


class AssistantHostedWebUiHandler(base.HostedWebUiHandler):
    """Hosted WebUI handler with assistant endpoints enabled."""

    def _do_GET_routes(self, path: str, client_ip: str, request_id: str) -> None:
        clean_path = urlparse(path).path
        if clean_path == "/api/assistant/config":
            principal = self._require_principal(client_ip, "GET", clean_path, request_id)
            if not principal or not self._check_rate_limit(principal, client_ip):
                return
            if not base.AUTH_MANAGER.can(principal, "view_scans"):
                self._forbidden()
                return
            self._send_json(ASSISTANT.available_config())
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
        super()._do_POST_routes(path, client_ip, request_id)


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
