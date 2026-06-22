from __future__ import annotations

import json

from core.scanner import Scanner
from dashboards.generate_dashboard import DashboardGenerator
from reports.json_report_generator import JsonReportGenerator
from reports.report_generator import MarkdownReportGenerator


def test_policy_results_are_attached_to_scan() -> None:
    result = Scanner().scan(target_name="demo", profile_name="baseline")

    assert result.policy_results
    assert result.policy_status in {"pass", "warn", "fail"}
    assert {policy.policy_id for policy in result.policy_results} >= {
        "no_secret_disclosure",
        "tool_execution_requires_allowlist",
        "rag_corpus_integrity_required",
        "critical_ai_action_requires_human_approval",
    }


def test_json_report_contains_policy_results(tmp_path) -> None:
    result = Scanner().scan(target_name="demo", profile_name="baseline")
    output = JsonReportGenerator().generate(result, tmp_path / "report.json")

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["policy_status"] == result.policy_status
    assert data["policy_results"]
    assert data["findings"]


def test_markdown_report_contains_policy_section(tmp_path) -> None:
    result = Scanner().scan(target_name="demo", profile_name="baseline")
    output = MarkdownReportGenerator().generate(result, tmp_path / "report.md")

    text = output.read_text(encoding="utf-8")
    assert "## Policy Evaluation" in text
    assert "Policy status" in text


def test_dashboard_generator_uses_json_report(tmp_path) -> None:
    result = Scanner().scan(target_name="demo", profile_name="baseline")
    json_output = JsonReportGenerator().generate(result, tmp_path / "report.json")
    report = json.loads(json_output.read_text(encoding="utf-8"))
    dashboard = DashboardGenerator().generate_from_report(report, tmp_path / "dashboard.md")

    text = dashboard.read_text(encoding="utf-8")
    assert "# LLM Assessment Dashboard" in text
    assert "## Policy status" in text
    assert "## OWASP coverage" in text
