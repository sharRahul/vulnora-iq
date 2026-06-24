from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from core.scanner import Scanner
from integrations.target_adapters import redact, validate_real_environment_config
from webui.persistent_jobs import SqliteJobStore


def test_sqlite_scan_events_and_finding_history_persist(tmp_path: Path) -> None:
    store = SqliteJobStore(tmp_path / "jobs.db")
    job = store.create("demo", "baseline", False, created_by="alice")
    store.update(job.id, lambda j: j.add_event("scan_started", "started", 10))
    events = store.list_events_after(job.id, 0)
    assert events[0].type == "scan_queued"
    assert any(event.type == "scan_started" for event in events)

    store.update(job.id, lambda j: j.summary.update({"findings": [{"id": "f-1", "title": "safe finding"}]}))
    state = store.update_finding(job.id, "f-1", {"status": "triaged", "remediation_note": "owner reviewing"}, "alice")
    assert state is not None
    assert state["status"] == "triaged"
    assert store.finding_history(job.id, "f-1")[0]["actor"] == "alice"


def test_aitg_manifest_and_profile_execute_32_entries() -> None:
    data = yaml.safe_load(Path("benchmarks/fixtures/aitg/aitg_32_manifest.yaml").read_text())
    assert len(data["aitg_tests"]) == 32
    result = Scanner().scan(target_name="demo", profile_name="owasp-aitg-full")
    assert result.finding_count == 32
    assert {finding.evidence["status"] for finding in result.findings} == {"passed"}


def test_real_environment_config_requires_authorisation_and_redacts_secret() -> None:
    with pytest.raises(ValueError, match="explicit_authorisation"):
        validate_real_environment_config("unsafe", {"base_url": "http://localhost:8080", "endpoint_path": "/v1"})
    cfg = validate_real_environment_config(
        "safe",
        {
            "base_url": "http://localhost:8080",
            "endpoint_path": "/v1",
            "explicit_authorisation": True,
            "allowed_host_pattern": "localhost",
            "rate_limit": {"requests_per_second": 1},
        },
    )
    assert cfg["explicit_authorisation"] is True
    assert "redacted" in json.dumps(redact({"Authorization": "Bearer example-token"})).lower()


def test_react_console_uses_backend_scan_and_finding_apis() -> None:
    app = Path("webui/console/src/App.tsx").read_text(encoding="utf-8")
    backlog = Path("docs/PRODUCTION_HARDENING_BACKLOG.md").read_text(encoding="utf-8")

    assert "TODO(api): wire to POST /api/scans" not in app
    assert "TODO(api): PATCH /api/findings" not in app
    assert "setAppliedFindingIds" not in app
    assert "window.setTimeout" not in app

    assert 'api<ScanJob>("/api/scans"' in app
    assert "new EventSource" in app
    assert "/api/scans/${encodeURIComponent(scan.id)}/events" in app
    assert 'method: "PATCH"' in app
    assert "/findings/${encodeURIComponent(finding.id)}" in app
    assert "/history" in app
    assert "refreshScanFindings" in app
    assert "refreshFindingHistory" in app

    current_backlog = backlog.split("## Current maturity backlog", 1)[1].split("## Production claim rule", 1)[0]
    assert "WebUI live progress" not in current_backlog
    assert "WebUI finding actions" not in current_backlog
    assert "High-priority items completed on 2026-06-24" in backlog
