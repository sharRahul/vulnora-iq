from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.scanner import Scanner
from dashboards.generate_dashboard import DashboardGenerator
from dashboards.html_dashboard import HtmlDashboardGenerator
from reports.json_report_generator import JsonReportGenerator
from reports.report_generator import MarkdownReportGenerator
from reports.sarif_report_generator import SarifReportGenerator

PRODUCTION_READY_MARKER = "authorised_production_assessment_testing_ready"


@dataclass(slots=True)
class FunctionalTestSummary:
    status: str
    target: str
    profile: str
    output_dir: str
    generated_files: list[str]
    checks: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_functional_test(
    output_dir: str | Path = "reports/output/functional-test",
) -> FunctionalTestSummary:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    markdown_path = output_root / "functional-report.md"
    json_path = output_root / "functional-report.json"
    sarif_path = output_root / "functional-report.sarif"
    dashboard_path = output_root / "functional-dashboard.md"
    html_dashboard_path = output_root / "functional-dashboard.html"
    summary_path = output_root / "functional-test-summary.json"

    result = Scanner(config_dir=Path("config")).scan(target_name="demo", profile_name="baseline", authorised=False)
    markdown_output = MarkdownReportGenerator().generate(result, markdown_path)
    json_output = JsonReportGenerator().generate(result, json_path)
    sarif_output = SarifReportGenerator().generate(result, sarif_path)
    report_data = json.loads(Path(json_output).read_text(encoding="utf-8"))
    dashboard_output = DashboardGenerator().generate_from_report(report_data, dashboard_path)
    html_output = HtmlDashboardGenerator().generate_from_report(report_data, html_dashboard_path)

    generated = [str(markdown_output), str(json_output), str(sarif_output), str(dashboard_output), str(html_output), str(summary_path)]
    checks: dict[str, str] = {}
    errors: list[str] = []

    for path in generated[:-1]:
        file_path = Path(path)
        checks[f"non_empty:{file_path.name}"] = "pass" if file_path.exists() and file_path.stat().st_size > 0 else "fail"
        if checks[f"non_empty:{file_path.name}"] == "fail":
            errors.append(f"Missing or empty output: {file_path}")

    required_fields = ["target", "profile", "finding_count", "policy_status", "metadata", "findings", "policy_results"]
    missing_fields = [field for field in required_fields if field not in report_data]
    checks["json_required_fields"] = "pass" if not missing_fields else "fail"
    if missing_fields:
        errors.append(f"Functional JSON report missing fields: {', '.join(missing_fields)}")

    checks["demo_baseline_scope"] = "pass" if report_data.get("target") == "demo" and report_data.get("profile") == "baseline" else "fail"
    if checks["demo_baseline_scope"] == "fail":
        errors.append("Functional run did not execute demo/baseline scope.")

    metadata = report_data.get("metadata", {})
    oracle_coverage = metadata.get("owasp_oracle_coverage", {})
    production_coverage = metadata.get("production_owasp_detection", {})
    checks["owasp_category_count"] = "pass" if oracle_coverage.get("owasp_category_count") == 10 else "fail"
    checks["production_owasp_detector_count"] = "pass" if production_coverage.get("covered_category_count") == 10 else "fail"
    checks["production_validation_marker"] = "pass" if metadata.get("production_validation_status") == PRODUCTION_READY_MARKER else "fail"
    if checks["owasp_category_count"] == "fail":
        errors.append("OWASP oracle coverage does not report all 10 categories.")
    if checks["production_owasp_detector_count"] == "fail":
        errors.append("Production OWASP detector coverage does not report all 10 categories.")
    if checks["production_validation_marker"] == "fail":
        errors.append("Production assessment readiness marker is missing or incorrect.")

    html_text = Path(html_output).read_text(encoding="utf-8")
    checks["html_dashboard_title"] = "pass" if "VulnoraIQ Assessment Dashboard" in html_text else "fail"
    if checks["html_dashboard_title"] == "fail":
        errors.append("HTML dashboard title was not found.")

    status = "pass" if not errors else "fail"
    summary = FunctionalTestSummary(status, "demo", "baseline", str(output_root), generated, checks, errors)
    summary_path.write_text(json.dumps(summary.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run VulnoraIQ functional acceptance test and generate dashboard artifacts.")
    parser.add_argument("--output-dir", default="reports/output/functional-test")
    args = parser.parse_args()
    summary = run_functional_test(args.output_dir)
    print(json.dumps(summary.to_dict(), indent=2, sort_keys=True))
    if summary.status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
