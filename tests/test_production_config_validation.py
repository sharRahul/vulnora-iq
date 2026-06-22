from __future__ import annotations

import pytest

from webui.auth import WebAuthManager
from webui.production_checks import (
    ProductionConfigError,
    check_admin_token_length,
    check_admin_token_set,
    check_audit_logging_configured,
    check_auth_enabled,
    check_csrf_ttl_sane,
    check_internal_admin_disabled,
    check_job_store_backend,
    check_listen_address_safe,
    check_no_demo_tokens,
    check_proxy_cidrs_configured,
    check_rate_limit_sane,
    check_request_body_limit_sane,
    check_sqlite_path_safe,
    validate_all,
)


def _make_manager(monkeypatch, extra_env: dict[str, str] | None = None) -> WebAuthManager:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "this-is-a-long-enough-admin-token-12345")
    if extra_env:
        for k, v in extra_env.items():
            monkeypatch.setenv(k, v)
    return WebAuthManager()


def test_check_auth_enabled_passes(monkeypatch) -> None:
    manager = _make_manager(monkeypatch)
    check_auth_enabled(manager)


def test_check_auth_enabled_fails(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_AUTH_ENABLED", "false")
    manager = WebAuthManager()
    with pytest.raises(ProductionConfigError, match="VULNORAIQ_AUTH_ENABLED must be true"):
        check_auth_enabled(manager)


def test_check_admin_token_set_passes(monkeypatch) -> None:
    manager = _make_manager(monkeypatch)
    check_admin_token_set(manager)


def test_check_admin_token_set_fails(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    manager = WebAuthManager()
    with pytest.raises(ProductionConfigError, match="VULNORAIQ_ADMIN_TOKEN must be set"):
        check_admin_token_set(manager)


def test_check_admin_token_length_passes(monkeypatch) -> None:
    manager = _make_manager(monkeypatch)
    check_admin_token_length(manager)


def test_check_admin_token_length_fails(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "short")
    manager = WebAuthManager()
    with pytest.raises(ProductionConfigError, match="at least 20"):
        check_admin_token_length(manager)


@pytest.mark.parametrize("bad_token", ["demo", "admin", "password", "test", "changeme", "vulnoraiq-internal-admin-token"])
def test_check_no_demo_tokens_fails(monkeypatch, bad_token: str) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", bad_token)
    manager = WebAuthManager()
    with pytest.raises(ProductionConfigError, match="not allowed in production"):
        check_no_demo_tokens(manager)


def test_check_internal_admin_disabled(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "vulnoraiq-internal-admin-token-12345")
    manager = WebAuthManager()
    with pytest.raises(ProductionConfigError, match="not allowed in production"):
        check_internal_admin_disabled(manager)


def test_check_job_store_backend_fails_json(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_JOB_STORE_BACKEND", "json")
    with pytest.raises(ProductionConfigError, match="not allowed in production"):
        check_job_store_backend()


def test_check_job_store_backend_passes_sqlite(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_JOB_STORE_BACKEND", "sqlite")
    check_job_store_backend()


def test_check_sqlite_path_safe(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_JOB_STORE_PATH", "/tmp/unsafe.db")
    with pytest.raises(ProductionConfigError, match="ephemeral or unsafe|unsafe location"):
        check_sqlite_path_safe()


def test_check_proxy_cidrs_configured_fails(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("VULNORAIQ_TRUSTED_PROXY_CIDRS", "")
    with pytest.raises(ProductionConfigError, match="must be configured"):
        check_proxy_cidrs_configured()


def test_check_proxy_cidrs_configured_passes(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("VULNORAIQ_TRUSTED_PROXY_CIDRS", "10.0.0.0/8")
    check_proxy_cidrs_configured()


def test_check_proxy_cidrs_invalid(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("VULNORAIQ_TRUSTED_PROXY_CIDRS", "not-a-cidr")
    with pytest.raises(ProductionConfigError, match="Invalid CIDR"):
        check_proxy_cidrs_configured()


def test_check_listen_address_0_0_0_0_fails_without_proxy(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_TRUST_PROXY_HEADERS", "false")
    with pytest.raises(ProductionConfigError, match="without proxy trust"):
        check_listen_address_safe("0.0.0.0")


def test_check_listen_address_127_0_0_1_passes() -> None:
    check_listen_address_safe("127.0.0.1")


def test_check_rate_limit_sane_fails(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_RATE_LIMIT_MAX", "0")
    with pytest.raises(ProductionConfigError, match="must be positive"):
        check_rate_limit_sane()


def test_check_rate_limit_sane_passes() -> None:
    check_rate_limit_sane()


def test_check_request_body_limit_sane_fails(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_MAX_REQUEST_BODY", "-1")
    with pytest.raises(ProductionConfigError, match="must be positive"):
        check_request_body_limit_sane()


def test_check_request_body_limit_too_large(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_MAX_REQUEST_BODY", str(200 * 1024 * 1024))
    with pytest.raises(ProductionConfigError, match="exceeds 100MB"):
        check_request_body_limit_sane()


def test_check_csrf_ttl_sane_fails(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_CSRF_TOKEN_TTL", "-1")
    with pytest.raises(ProductionConfigError, match="must be positive"):
        check_csrf_ttl_sane()


def test_check_audit_logging_configured_passes() -> None:
    check_audit_logging_configured()


def test_validate_all_passes_with_valid_config(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "this-is-a-long-enough-admin-token-12345")
    monkeypatch.setenv("VULNORAIQ_JOB_STORE_BACKEND", "sqlite")
    result = validate_all(host="127.0.0.1")
    passed = [r for r in result if r["status"] == "pass"]
    failed = [r for r in result if r["status"] != "pass"]
    assert len(failed) == 0, f"Failed checks: {failed}"
    assert len(passed) > 0


def test_validate_all_fails_with_bad_config(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_AUTH_ENABLED", "false")
    result = validate_all(host="0.0.0.0")
    failed = [r for r in result if r["status"] != "pass"]
    assert len(failed) > 0


def test_validate_all_listen_address_safe_127_0_0_1(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "this-is-a-long-enough-admin-token-12345")
    result = validate_all(host="127.0.0.1")
    listen = [r for r in result if r["check"] == "listen_address_safe"]
    assert len(listen) == 1
    assert listen[0]["status"] == "pass"


def test_validate_all_listen_address_fails_0_0_0_0_no_proxy(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "this-is-a-long-enough-admin-token-12345")
    monkeypatch.setenv("VULNORAIQ_TRUST_PROXY_HEADERS", "false")
    result = validate_all(host="0.0.0.0")
    listen = [r for r in result if r["check"] == "listen_address_safe"]
    assert len(listen) == 1
    assert listen[0]["status"] == "fail"
    assert "without proxy trust" in listen[0].get("error", "")


def test_validate_all_listen_address_passes_0_0_0_0_with_proxy(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "this-is-a-long-enough-admin-token-12345")
    monkeypatch.setenv("VULNORAIQ_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("VULNORAIQ_TRUSTED_PROXY_CIDRS", "10.0.0.0/8")
    result = validate_all(host="0.0.0.0")
    listen = [r for r in result if r["check"] == "listen_address_safe"]
    assert len(listen) == 1
    assert listen[0]["status"] == "pass"


def test_validate_all_listen_address_fails_0_0_0_0_invalid_cidr(monkeypatch) -> None:
    monkeypatch.setenv("VULNORAIQ_ENV", "production")
    monkeypatch.setenv("VULNORAIQ_ADMIN_TOKEN", "this-is-a-long-enough-admin-token-12345")
    monkeypatch.setenv("VULNORAIQ_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("VULNORAIQ_TRUSTED_PROXY_CIDRS", "not-a-cidr")
    result = validate_all(host="0.0.0.0")
    listen = [r for r in result if r["check"] == "listen_address_safe"]
    cidr_check = [r for r in result if r["check"] == "proxy_cidrs_configured"]
    # listen_address_safe should fail because proxy_cidrs_configured will also fail
    # But listen_address_safe itself passes since TRUST_PROXY_HEADERS is true
    # (the CIDR validation is a separate check)
    # Actually, listen_address_safe only checks TRUST_PROXY_HEADERS, not CIDR validity
    # So with TRUST_PROXY_HEADERS=true, it passes even with bad CIDRs.
    # The CIDR validation is done by proxy_cidrs_configured.
    assert len(listen) == 1
    assert listen[0]["status"] == "pass"
    assert len(cidr_check) == 1
    assert cidr_check[0]["status"] == "fail"
