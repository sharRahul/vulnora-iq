from __future__ import annotations

import pytest

from integrations.endpoint_security import validate_target_endpoint
from webui.auth import AuthPrincipal
from webui.hosted_server import _can_download_job_artifact, _can_view_job
from webui.persistent_jobs import PersistedScanJob


def test_non_admin_cannot_view_another_users_scan() -> None:
    principal = AuthPrincipal("alice", "analyst", {"view_scans", "download_artifacts"}, authenticated=True)
    job = PersistedScanJob("job-1", "demo", "baseline", False, created_by="bob")
    assert not _can_view_job(principal, job)


def test_non_admin_can_view_own_scan() -> None:
    principal = AuthPrincipal("alice", "analyst", {"view_scans", "download_artifacts"}, authenticated=True)
    job = PersistedScanJob("job-1", "demo", "baseline", False, created_by="alice")
    assert _can_view_job(principal, job)


def test_admin_can_view_all_scans() -> None:
    principal = AuthPrincipal("admin", "admin", {"view_all_scans", "download_all_artifacts"}, authenticated=True)
    job = PersistedScanJob("job-1", "demo", "baseline", False, created_by="bob")
    assert _can_view_job(principal, job)


def test_non_admin_cannot_download_another_users_artifact() -> None:
    principal = AuthPrincipal("alice", "analyst", {"view_scans", "download_artifacts"}, authenticated=True)
    job = PersistedScanJob("job-1", "demo", "baseline", False, created_by="bob")
    assert not _can_download_job_artifact(principal, job)


def test_target_endpoint_requires_http_scheme() -> None:
    with pytest.raises(ValueError, match="http or https"):
        validate_target_endpoint("file:///etc/passwd")


def test_target_endpoint_rejects_url_credentials() -> None:
    with pytest.raises(ValueError, match="credentials"):
        validate_target_endpoint("https://user:secret@example.com/api")


def test_target_endpoint_allows_configured_host(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ALLOWED_TARGET_HOSTS", "api.internal.example.com,*.lab.example.com")
    assert validate_target_endpoint("https://api.internal.example.com/agent") == "https://api.internal.example.com/agent"
    assert validate_target_endpoint("https://red.lab.example.com/agent") == "https://red.lab.example.com/agent"


def test_target_endpoint_blocks_unlisted_host(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ALLOWED_TARGET_HOSTS", "api.internal.example.com")
    with pytest.raises(ValueError, match="not in"):
        validate_target_endpoint("https://other.example.com/agent")
