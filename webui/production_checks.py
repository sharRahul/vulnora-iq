from __future__ import annotations

import ipaddress
import logging
import os
from pathlib import Path
from typing import Any

from webui.auth import WebAuthManager

LOGGER = logging.getLogger("vulnoraiq.production_checks")

KNOWN_DEMO_TOKENS: set[str] = {"vulnoraiq-internal-admin-token", "demo", "admin", "password", "test", "changeme"}


class ProductionConfigError(RuntimeError):
    """Raised when production configuration validation fails."""


def _get_env_int(name: str, default: int) -> int:
    val = os.getenv(name, "").strip()
    if not val:
        return default
    try:
        return int(val)
    except ValueError as exc:
        raise ProductionConfigError(f"{name} must be an integer, got '{val}'") from exc


def check_auth_enabled(manager: WebAuthManager) -> None:
    if not manager.enabled():
        raise ProductionConfigError("VULNORAIQ_AUTH_ENABLED must be true in production mode.")


def check_admin_token_set(manager: WebAuthManager) -> None:
    env_tokens = manager._load_env_tokens()
    if not env_tokens or "admin" not in env_tokens.values():
        raise ProductionConfigError(
            "VULNORAIQ_ADMIN_TOKEN must be set and non-empty in production mode."
        )


def check_admin_token_length(manager: WebAuthManager) -> None:
    from webui.auth import _MIN_TOKEN_LENGTH

    env_tokens = manager._load_env_tokens()
    for token, role in env_tokens.items():
        if role == "admin" and len(token) < _MIN_TOKEN_LENGTH:
            raise ProductionConfigError(
                f"VULNORAIQ_ADMIN_TOKEN must be at least {_MIN_TOKEN_LENGTH} "
                f"characters in production mode (got {len(token)})."
            )


def check_no_demo_tokens(manager: WebAuthManager) -> None:
    env_tokens = manager._load_env_tokens()
    for token in env_tokens:
        if token in KNOWN_DEMO_TOKENS:
            raise ProductionConfigError(
                f"Known demo/default token '{token}' is not allowed in production mode."
            )


def check_internal_admin_disabled(manager: WebAuthManager) -> None:
    if not manager.is_production():
        return
    token = os.getenv("VULNORAIQ_ADMIN_TOKEN", "")
    if token and "vulnoraiq-internal-admin-token" in token:
        raise ProductionConfigError(
            "Internal admin token value is not allowed in production mode."
        )


def check_job_store_backend() -> None:
    backend = os.getenv("VULNORAIQ_JOB_STORE_BACKEND", "sqlite").strip().lower()
    if backend == "json":
        raise ProductionConfigError(
            "JSON job store backend is not allowed in production mode. "
            "Use 'sqlite' (default) or another approved backend."
        )


def check_sqlite_path_safe() -> None:
    path = os.getenv("VULNORAIQ_JOB_STORE_PATH", "")
    if not path:
        return
    resolved = Path(path).resolve()
    unsafe_markers = {"tmp", "dev", "shm", "proc", "sys"}
    for part in resolved.parts:
        if part.lower() in unsafe_markers:
            raise ProductionConfigError(
                f"SQLite path '{path}' resolves inside an ephemeral or unsafe location ({resolved})."
            )


def check_output_dir_writable() -> None:
    output_root = Path(os.getenv("VULNORAIQ_WEB_OUTPUT_ROOT", "reports/output/webui"))
    try:
        output_root.mkdir(parents=True, exist_ok=True)
        test_file = output_root / ".write_test"
        test_file.write_text("")
        test_file.unlink()
    except OSError as exc:
        raise ProductionConfigError(
            f"Output directory '{output_root}' is not writable: {exc}"
        ) from exc


def check_config_dir_readable() -> None:
    config_root = Path(os.getenv("VULNORAIQ_CONFIG_DIR", "config"))
    if not config_root.exists():
        raise ProductionConfigError(
            f"Config directory '{config_root}' does not exist."
        )
    if not config_root.is_dir():
        raise ProductionConfigError(
            f"Config path '{config_root}' is not a directory."
        )
    try:
        for _item in config_root.iterdir():
            pass
    except OSError as exc:
        raise ProductionConfigError(
            f"Config directory '{config_root}' is not readable: {exc}"
        ) from exc


def check_proxy_cidrs_configured() -> None:
    trust = os.getenv("VULNORAIQ_TRUST_PROXY_HEADERS", "false").strip().lower() in ("1", "true", "yes")
    if trust:
        cidrs = os.getenv("VULNORAIQ_TRUSTED_PROXY_CIDRS", "").strip()
        if not cidrs:
            raise ProductionConfigError(
                "VULNORAIQ_TRUST_PROXY_HEADERS is enabled but VULNORAIQ_TRUSTED_PROXY_CIDRS is not set. "
                "Trusted proxy CIDRs must be configured when proxy headers are trusted."
            )
        for cidr in cidrs.split(","):
            cidr = cidr.strip()
            if cidr:
                try:
                    ipaddress.ip_network(cidr, strict=False)
                except ValueError as exc:
                    raise ProductionConfigError(
                        f"Invalid CIDR in VULNORAIQ_TRUSTED_PROXY_CIDRS: '{cidr}' — {exc}"
                    ) from exc


def check_listen_address_safe(host: str) -> None:
    if host in ("0.0.0.0", "::"):
        trust = os.getenv("VULNORAIQ_TRUST_PROXY_HEADERS", "false").strip().lower() in ("1", "true", "yes")
        if not trust:
            raise ProductionConfigError(
                f"Listening on {host} without proxy trust configured. "
                "When binding to all interfaces, either bind behind a reverse proxy "
                "or set VULNORAIQ_TRUST_PROXY_HEADERS=true and configure VULNORAIQ_TRUSTED_PROXY_CIDRS."
            )


def check_rate_limit_sane() -> None:
    rl_max = _get_env_int("VULNORAIQ_RATE_LIMIT_MAX", 60)
    if rl_max <= 0:
        raise ProductionConfigError(f"VULNORAIQ_RATE_LIMIT_MAX must be positive (got {rl_max}).")
    rl_window = _get_env_int("VULNORAIQ_RATE_LIMIT_WINDOW", 60)
    if rl_window <= 0:
        raise ProductionConfigError(f"VULNORAIQ_RATE_LIMIT_WINDOW must be positive (got {rl_window}).")


def check_request_body_limit_sane() -> None:
    limit = _get_env_int("VULNORAIQ_MAX_REQUEST_BODY", 10 * 1024 * 1024)
    if limit <= 0:
        raise ProductionConfigError(f"VULNORAIQ_MAX_REQUEST_BODY must be positive (got {limit}).")
    if limit > 100 * 1024 * 1024:
        raise ProductionConfigError(
            f"VULNORAIQ_MAX_REQUEST_BODY exceeds 100MB limit (got {limit})."
        )


def check_csrf_ttl_sane() -> None:
    ttl = _get_env_int("VULNORAIQ_CSRF_TOKEN_TTL", 300)
    if ttl <= 0:
        raise ProductionConfigError(f"VULNORAIQ_CSRF_TOKEN_TTL must be positive (got {ttl}).")


def check_audit_logging_configured() -> None:
    level = os.getenv("VULNORAIQ_LOG_LEVEL", "INFO").strip().upper()
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        raise ProductionConfigError(f"Invalid VULNORAIQ_LOG_LEVEL: {level}")
    if level == "DEBUG":
        LOGGER.warning("VULNORAIQ_LOG_LEVEL=DEBUG is set in production mode — may expose verbose details.")


def check_no_dev_config_active() -> None:
    dev_root = Path(os.getenv("VULNORAIQ_CONFIG_DIR", "config"))
    dev_markers = ["web_users.local.yaml", "targets.local.yaml"]
    for marker in dev_markers:
        if (dev_root / marker).exists():
            LOGGER.warning("Development config '%s' found in production mode.", marker)


_ALL_CHECKS: list[tuple[str, Any, bool]] = [
    ("auth_enabled", check_auth_enabled, True),
    ("admin_token_set", check_admin_token_set, True),
    ("admin_token_length", check_admin_token_length, True),
    ("no_demo_tokens", check_no_demo_tokens, True),
    ("internal_admin_disabled", check_internal_admin_disabled, True),
    ("job_store_backend", check_job_store_backend, False),
    ("sqlite_path_safe", check_sqlite_path_safe, False),
    ("output_dir_writable", check_output_dir_writable, False),
    ("config_dir_readable", check_config_dir_readable, False),
    ("proxy_cidrs_configured", check_proxy_cidrs_configured, False),
    ("rate_limit_sane", check_rate_limit_sane, False),
    ("request_body_limit_sane", check_request_body_limit_sane, False),
    ("csrf_ttl_sane", check_csrf_ttl_sane, False),
    ("audit_logging_configured", check_audit_logging_configured, False),
    ("no_dev_config_active", check_no_dev_config_active, False),
    ("listen_address_safe", check_listen_address_safe, False),
]


def validate_all(host: str = "127.0.0.1", manager: WebAuthManager | None = None) -> list[dict[str, Any]]:
    if manager is None:
        manager = WebAuthManager()
    results: list[dict[str, Any]] = []

    def _check_listen_address() -> None:
        check_listen_address_safe(host)

    for check_name, check_fn, needs_manager in _ALL_CHECKS:
        try:
            if check_name == "listen_address_safe":
                _check_listen_address()
            elif needs_manager:
                check_fn(manager)
            else:
                check_fn()
            results.append({"check": check_name, "status": "pass"})
        except ProductionConfigError as exc:
            results.append({"check": check_name, "status": "fail", "error": str(exc)})
            LOGGER.error("production_check_failed %s: %s", check_name, exc)
        except Exception as exc:
            results.append({"check": check_name, "status": "error", "error": str(exc)})
            LOGGER.exception("production_check_error %s: %s", check_name, exc)
    return results


def validate_and_exit(host: str = "127.0.0.1") -> None:
    results = validate_all(host=host)
    failed = [r for r in results if r["status"] != "pass"]
    if failed:
        for fail in failed:
            LOGGER.error("PRODUCTION_CONFIG_FAILURE check=%s error=%s", fail["check"], fail.get("error", "unknown"))
        raise ProductionConfigError(
            f"Production configuration validation failed: {len(failed)} check(s) failed. "
            f"Run scripts/validate_runtime_production_config.py for details."
        )
    LOGGER.info("All production configuration checks passed (%d checks).", len(results))
