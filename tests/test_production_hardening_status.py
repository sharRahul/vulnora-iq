from __future__ import annotations

from pathlib import Path

import pytest

BACKLOG = Path("docs/PRODUCTION_HARDENING_BACKLOG.md")
README = Path("README.md")
IMPLEMENTATION_STATUS = Path("docs/IMPLEMENTATION_STATUS.md")
DOCKERFILE = Path("Dockerfile")
DEPLOYMENT_DOC = Path("docs/DEPLOYMENT.md")


def test_production_hardening_backlog_tracks_critical_blockers():
    text = BACKLOG.read_text(encoding="utf-8")
    for blocker_id in [f"PRD-{index:03d}" for index in range(1, 11)]:
        assert blocker_id in text
    assert "Current operational readiness: 10/10" in text
    assert "Self-hosted internal deployment readiness is attested" in text


def test_public_docs_keep_self_hosted_maturity_warning():
    readme = README.read_text(encoding="utf-8")
    status = IMPLEMENTATION_STATUS.read_text(encoding="utf-8")
    assert "self-hosted internal application" in readme
    assert "self-hosted laptop/server use" in status


def test_container_and_deployment_baseline_exist():
    assert DOCKERFILE.exists()
    assert DEPLOYMENT_DOC.exists()
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    deployment = DEPLOYMENT_DOC.read_text(encoding="utf-8")
    assert "/healthz" in dockerfile
    assert "vulnoraiq" in dockerfile  # non-root user exists
    assert "USER" in dockerfile
    assert "VOLUME" in dockerfile
    assert "/data" in dockerfile
    assert "VULNORAIQ_WEB_USERS_PATH" in deployment
    assert "VULNORAIQ_ADMIN_TOKEN" in deployment
    assert "Production Checklist" in deployment
    assert "reverse proxy" in deployment.lower() or "nginx" in deployment.lower()
    assert "TLS" in deployment or "tls" in deployment.lower()
    assert "backup" in deployment.lower()
    assert "audit" in deployment.lower()


@pytest.mark.parametrize(
    "required_snippet",
    [
        "[tool.ruff]",
        "[tool.mypy]",
        "ruff>=",
        "mypy>=",
    ],
)
def test_lint_and_type_check_configuration_exists(required_snippet: str):
    assert required_snippet in Path("pyproject.toml").read_text(encoding="utf-8")
