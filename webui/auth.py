from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class AuthPrincipal:
    username: str
    role: str
    permissions: set[str]
    authenticated: bool


_ENV_AUTH_ENABLED = "VULNORAIQ_AUTH_ENABLED"
_ENV_ADMIN_TOKEN = "VULNORAIQ_ADMIN_TOKEN"
_ENV_ANALYST_TOKEN = "VULNORAIQ_ANALYST_TOKEN"
_ENV_VIEWER_TOKEN = "VULNORAIQ_VIEWER_TOKEN"
_ENV_PRODUCTION = "VULNORAIQ_ENV"
_ENV_AUTH_MODE = "VULNORAIQ_AUTH_MODE"

_DEFAULT_PERMISSIONS: dict[str, set[str]] = {
    "viewer": {"view_scans", "download_artifacts", "view_own_scans", "download_own_artifacts"},
    "analyst": {
        "view_scans",
        "download_artifacts",
        "view_own_scans",
        "download_own_artifacts",
        "start_demo_scan",
    },
    "admin": {
        "view_scans",
        "download_artifacts",
        "view_own_scans",
        "download_own_artifacts",
        "view_all_scans",
        "download_all_artifacts",
        "start_demo_scan",
        "start_configured_scan",
        "manage_runtime",
    },
}

_INTERNAL_ADMIN_TOKEN = "vulnoraiq-internal-admin-token"

_MIN_TOKEN_LENGTH = 20

# Proxy identity header names
_PROXY_HEADER_USER = "X-Authenticated-User"
_PROXY_HEADER_EMAIL = "X-Authenticated-Email"
_PROXY_HEADER_GROUPS = "X-Authenticated-Groups"
_PROXY_HEADER_ROLE = "X-VulnoraIQ-Role"

_DEFAULT_ROLE_MAPPING: dict[str, str] = {
    "admin": "admin",
    "analyst": "analyst",
    "viewer": "viewer",
}


class WebAuthManager:
    """Role-aware auth manager driven by environment variables.

    Auth is enabled by default (VULNORAIQ_AUTH_ENABLED=true).
    Set VULNORAIQ_AUTH_ENABLED=false to disable (not recommended for production).

    Auth modes (VULNORAIQ_AUTH_MODE):
      token (default) - env var token matching with constant-time comparison
      trusted_proxy  - identity headers from trusted reverse proxy

    Token env vars (mutually exclusive with file config):
      VULNORAIQ_ADMIN_TOKEN  - full access
      VULNORAIQ_ANALYST_TOKEN - demo-scan + view access
      VULNORAIQ_VIEWER_TOKEN  - view-only access

    Falls back to config/web_users.yaml if no token env vars are set.
    The file-based fallback is NOT allowed in production mode.

    Production mode (VULNORAIQ_ENV=production):
      - Auth must be enabled
      - At least VULNORAIQ_ADMIN_TOKEN must be set and meet minimum length
      - File-based demo users are rejected
      - Internal admin token is disabled
    """

    def __init__(self, path: str | Path = "config/web_users.yaml") -> None:
        self.path = Path(path)
        self._config: dict[str, Any] | None = None
        self._env_tokens: dict[str, str] | None = None

    def is_production(self) -> bool:
        return os.getenv(_ENV_PRODUCTION, "").strip().lower() == "production"

    def auth_mode(self) -> str:
        return os.getenv(_ENV_AUTH_MODE, "token").strip().lower()

    def _validate_production(self) -> None:
        if not self.is_production():
            return
        if not self.enabled():
            raise RuntimeError(
                "Production mode requires VULNORAIQ_AUTH_ENABLED=true. "
                "Set VULNORAIQ_ENV=development to run with auth disabled."
            )
        env_tokens = self._load_env_tokens()
        if not env_tokens or "admin" not in env_tokens.values():
            raise RuntimeError(
                "Production mode requires at least VULNORAIQ_ADMIN_TOKEN to be set "
                "with a value of 20 characters or more."
            )
        for token, role in env_tokens.items():
            if role == "admin" and len(token) < _MIN_TOKEN_LENGTH:
                raise RuntimeError(
                    f"VULNORAIQ_ADMIN_TOKEN must be at least {_MIN_TOKEN_LENGTH} characters "
                    f"in production mode (got {len(token)})."
                )

    def _load_env_tokens(self) -> dict[str, str]:
        if self._env_tokens is None:
            tokens: dict[str, str] = {}
            for key, role in [
                (_ENV_ADMIN_TOKEN, "admin"),
                (_ENV_ANALYST_TOKEN, "analyst"),
                (_ENV_VIEWER_TOKEN, "viewer"),
            ]:
                val = os.getenv(key, "").strip()
                if val:
                    tokens[val] = role
            self._env_tokens = tokens
        return self._env_tokens

    def has_file_auth(self) -> bool:
        if not self.path.exists():
            return False
        users = self.load().get("users", [])
        return any(u.get("status") == "active" for u in users)

    def load(self) -> dict[str, Any]:
        if self._config is None:
            if self.path.exists():
                self._config = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
            else:
                self._config = {}
        return self._config

    def enabled(self) -> bool:
        env_val = os.getenv(_ENV_AUTH_ENABLED)
        if env_val is not None:
            return env_val.lower() in ("1", "true", "yes")
        if self.is_production():
            return True
        cfg = self.load()
        return cfg.get("auth", {}).get("enabled", True) if cfg else True

    def header_name(self) -> str:
        return str(self.load().get("auth", {}).get("header_name", "X-VulnoraIQ-Token"))

    def anonymous(self) -> AuthPrincipal:
        return AuthPrincipal("anonymous", "viewer", _DEFAULT_PERMISSIONS["viewer"], authenticated=False)

    def authenticate_token(self, token: str | None) -> AuthPrincipal | None:
        if not self.enabled():
            return AuthPrincipal("anonymous", "analyst", _DEFAULT_PERMISSIONS["analyst"], authenticated=False)

        if not token:
            return None

        if not self.is_production() and token == _INTERNAL_ADMIN_TOKEN:
            return AuthPrincipal("internal", "admin", _DEFAULT_PERMISSIONS["admin"], authenticated=True)

        env_tokens = self._load_env_tokens()
        if env_tokens:
            for candidate, role in env_tokens.items():
                if hmac.compare_digest(candidate, token):
                    return AuthPrincipal(f"env-{role}", role, _DEFAULT_PERMISSIONS[role], authenticated=True)
            return None

        if self.is_production():
            return None

        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        for user in self.load().get("users", []):
            if user.get("status") != "active":
                continue
            if str(user.get("token_hash")) == digest:
                role = str(user.get("role", "viewer"))
                return AuthPrincipal(str(user.get("username")), role, self.permissions_for_role(role), authenticated=True)
        return None

    def authenticate_proxy_identity(
        self,
        headers: dict[str, str],
        trusted: bool,
        role_mapping: dict[str, str] | None = None,
    ) -> AuthPrincipal | None:
        """Authenticate via trusted reverse-proxy identity headers."""
        if not self.enabled():
            return AuthPrincipal("anonymous", "analyst", _DEFAULT_PERMISSIONS["analyst"], authenticated=False)

        if not trusted:
            return None

        username = headers.get(_PROXY_HEADER_USER, "").strip()
        if not username:
            return None

        role_header = headers.get(_PROXY_HEADER_ROLE, "").strip().lower()
        mapping = role_mapping or _DEFAULT_ROLE_MAPPING
        role = mapping.get(role_header, "viewer")
        return AuthPrincipal(f"proxy:{username}", role, self.permissions_for_role(role), authenticated=True)

    def permissions_for_role(self, role: str) -> set[str]:
        if role in _DEFAULT_PERMISSIONS:
            return _DEFAULT_PERMISSIONS[role]
        roles = self.load().get("roles", {})
        visited: set[str] = set()

        def collect(current_role: str) -> set[str]:
            if current_role in visited:
                return set()
            visited.add(current_role)
            spec = roles.get(current_role, {})
            permissions = set(spec.get("permissions", []))
            for parent in spec.get("inherits", []) or []:
                permissions |= collect(str(parent))
            return permissions

        return collect(role)

    @staticmethod
    def can(principal: AuthPrincipal, permission: str) -> bool:
        return permission in principal.permissions
