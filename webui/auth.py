from __future__ import annotations

import hashlib
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


class WebAuthManager:
    """Local role-aware auth manager for hosted Web UI deployments."""

    def __init__(self, path: str | Path = "config/web_users.yaml") -> None:
        self.path = Path(path)
        self._config: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        if self._config is None:
            self._config = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        return self._config

    def enabled(self) -> bool:
        return bool(self.load().get("auth", {}).get("enabled", False))

    def header_name(self) -> str:
        return str(self.load().get("auth", {}).get("header_name", "X-VulnoraIQ-Token"))

    def anonymous(self) -> AuthPrincipal:
        role = str(self.load().get("auth", {}).get("default_role", "analyst"))
        return AuthPrincipal("anonymous", role, self.permissions_for_role(role), authenticated=False)

    def authenticate_token(self, token: str | None) -> AuthPrincipal | None:
        if not self.enabled():
            return self.anonymous()
        if not token:
            return None
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        for user in self.load().get("users", []):
            if user.get("status") != "active":
                continue
            if str(user.get("token_hash")) == digest:
                role = str(user.get("role", "viewer"))
                return AuthPrincipal(str(user.get("username")), role, self.permissions_for_role(role), authenticated=True)
        return None

    def permissions_for_role(self, role: str) -> set[str]:
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
