from __future__ import annotations

from pathlib import Path

import pytest

from webui.hosted_server import validate_scan_request


def test_validate_scan_request_requires_explicit_target() -> None:
    with pytest.raises(ValueError, match="target is required"):
        validate_scan_request({})


def test_validate_scan_request_accepts_explicit_test_fixture_target() -> None:
    target, profile, authorised = validate_scan_request({"target": "demo", "profile": "baseline", "authorised": True})

    assert target == "demo"
    assert profile == "baseline"
    assert authorised is True


def test_validate_scan_request_rejects_unknown_target() -> None:
    with pytest.raises(ValueError):
        validate_scan_request({"target": "missing", "profile": "baseline"})


def test_run_scan_job_generates_webui_outputs(tmp_path, monkeypatch) -> None:
    from webui.hosted_server import run_scan_job

    monkeypatch.setattr("webui.hosted_server.OUTPUT_ROOT", Path(tmp_path))
    from webui.persistent_jobs import PersistentJobStore

    store = PersistentJobStore(tmp_path / "jobs.json")
    monkeypatch.setattr("webui.hosted_server.JOB_STORE", store)
    job = store.create("demo", "baseline", True)

    run_scan_job(job.id)

    completed = store.get(job.id)
    assert completed is not None
    assert completed.status == "completed"
    assert completed.progress == 100
    assert completed.summary["finding_count"] >= 1
    assert set(completed.outputs) == {"markdown", "json", "sarif", "dashboard_markdown", "dashboard_html"}
    assert all(Path(path).exists() for path in completed.outputs.values())
