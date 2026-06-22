from __future__ import annotations

import pytest

from core.scanner import Scanner


def test_demo_baseline_runs_without_authorisation() -> None:
    result = Scanner().scan(target_name="demo", profile_name="baseline")

    assert result.target_name == "demo"
    assert result.profile_name == "baseline"
    assert result.finding_count == 6
    assert result.highest_severity == "info"


def test_configured_target_requires_authorisation() -> None:
    scanner = Scanner()

    with pytest.raises(PermissionError):
        scanner.scan(target_name="custom_http_agent", profile_name="baseline")


def test_placeholder_configured_target_is_rejected_when_authorised() -> None:
    scanner = Scanner()

    with pytest.raises(ValueError, match="placeholder"):
        scanner.scan(target_name="custom_http_agent", profile_name="baseline", authorised=True)
