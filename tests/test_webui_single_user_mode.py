from __future__ import annotations

from scripts import desktop_launch
from webui.auth import WebAuthManager


def test_auth_disabled_resolves_to_local_admin(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("VULNORAIQ_AUTH_ENABLED", "false")
    monkeypatch.delenv("VULNORAIQ_ENV", raising=False)

    manager = WebAuthManager(tmp_path / "missing_web_users.yaml")
    principal = manager.authenticate_token(None)

    assert principal is not None
    assert principal.username == "local-admin"
    assert principal.role == "admin"
    assert principal.authenticated is False
    assert manager.can(principal, "manage_runtime")
    assert manager.can(principal, "start_configured_scan")


def test_desktop_launcher_defaults_to_single_user_admin(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(desktop_launch, "ROOT", tmp_path)
    monkeypatch.delenv("VULNORAIQ_AUTH_ENABLED", raising=False)

    env = desktop_launch._prepare_desktop_environment()

    assert env["VULNORAIQ_RUN_MODE"] == "desktop"
    assert env["VULNORAIQ_AUTH_ENABLED"] == "false"
    assert env["VULNORAIQ_HOST"] == "127.0.0.1"
    assert env["VULNORAIQ_AGENT_LAB_ROOT"] == str(tmp_path / "agent-lab")
