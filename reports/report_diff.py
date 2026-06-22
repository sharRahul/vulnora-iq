from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ReportDiff:
    baseline_report: str
    current_report: str
    finding_count_delta: int
    added_findings: list[dict[str, Any]]
    removed_findings: list[dict[str, Any]]
    changed_findings: list[dict[str, Any]]
    policy_status_changed: bool
    baseline_policy_status: str
    current_policy_status: str
    severity_count_delta: dict[str, int]

    @property
    def has_regression(self) -> bool:
        return bool(self.added_findings or self.changed_findings or self.policy_status_changed)


def load_report(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def finding_key(finding: dict[str, Any]) -> str:
    return "|".join(
        [
            str(finding.get("owasp_id", "")),
            str(finding.get("title", "")),
            str(finding.get("affected_component", "")),
        ]
    )


def diff_reports(baseline_path: str | Path, current_path: str | Path) -> ReportDiff:
    baseline = load_report(baseline_path)
    current = load_report(current_path)

    baseline_findings = {finding_key(item): item for item in baseline.get("findings", [])}
    current_findings = {finding_key(item): item for item in current.get("findings", [])}

    added_keys = sorted(set(current_findings) - set(baseline_findings))
    removed_keys = sorted(set(baseline_findings) - set(current_findings))
    shared_keys = sorted(set(current_findings) & set(baseline_findings))

    changed: list[dict[str, Any]] = []
    for key in shared_keys:
        before = baseline_findings[key]
        after = current_findings[key]
        changes: dict[str, Any] = {}
        for field in ["severity", "score", "recommendation", "mitre_atlas"]:
            if before.get(field) != after.get(field):
                changes[field] = {"before": before.get(field), "after": after.get(field)}
        if changes:
            changed.append({"key": key, "title": after.get("title"), "changes": changes})

    severities = set(baseline.get("severity_counts", {})) | set(current.get("severity_counts", {}))
    severity_delta = {
        severity: int(current.get("severity_counts", {}).get(severity, 0)) - int(baseline.get("severity_counts", {}).get(severity, 0))
        for severity in sorted(severities)
    }

    return ReportDiff(
        baseline_report=str(baseline_path),
        current_report=str(current_path),
        finding_count_delta=int(current.get("finding_count", 0)) - int(baseline.get("finding_count", 0)),
        added_findings=[current_findings[key] for key in added_keys],
        removed_findings=[baseline_findings[key] for key in removed_keys],
        changed_findings=changed,
        policy_status_changed=baseline.get("policy_status") != current.get("policy_status"),
        baseline_policy_status=str(baseline.get("policy_status", "unknown")),
        current_policy_status=str(current.get("policy_status", "unknown")),
        severity_count_delta=severity_delta,
    )


def write_json(diff: ReportDiff, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(diff), indent=2, sort_keys=True, default=str), encoding="utf-8")
    return output


def write_markdown(diff: ReportDiff, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# LLM Assessment Report Diff",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Baseline report | `{diff.baseline_report}` |",
        f"| Current report | `{diff.current_report}` |",
        f"| Finding count delta | `{diff.finding_count_delta}` |",
        f"| Policy status changed | `{diff.policy_status_changed}` |",
        f"| Baseline policy status | `{diff.baseline_policy_status}` |",
        f"| Current policy status | `{diff.current_policy_status}` |",
        f"| Regression detected | `{diff.has_regression}` |",
        "",
        "## Severity deltas",
        "",
        "| Severity | Delta |",
        "| --- | --- |",
    ]
    for severity, delta in diff.severity_count_delta.items():
        lines.append(f"| {severity} | {delta} |")

    lines.extend(["", "## Added findings", ""])
    if diff.added_findings:
        for finding in diff.added_findings:
            lines.append(f"- `{finding.get('severity')}` {finding.get('title')} ({finding.get('owasp_id')})")
    else:
        lines.append("No added findings.")

    lines.extend(["", "## Removed findings", ""])
    if diff.removed_findings:
        for finding in diff.removed_findings:
            lines.append(f"- `{finding.get('severity')}` {finding.get('title')} ({finding.get('owasp_id')})")
    else:
        lines.append("No removed findings.")

    lines.extend(["", "## Changed findings", ""])
    if diff.changed_findings:
        for finding in diff.changed_findings:
            lines.append(f"- {finding['title']}: `{json.dumps(finding['changes'], sort_keys=True)}`")
    else:
        lines.append("No changed findings.")

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Diff two structured LLM VAPT JSON reports.")
    parser.add_argument("--baseline", required=True, help="Baseline JSON report path.")
    parser.add_argument("--current", required=True, help="Current JSON report path.")
    parser.add_argument("--json-output", default="reports/output/report-diff.json", help="Diff JSON output path.")
    parser.add_argument("--markdown-output", default="reports/output/report-diff.md", help="Diff Markdown output path.")
    parser.add_argument("--fail-on-regression", action="store_true", help="Exit with code 1 if added/changed findings or policy status changes are detected.")
    args = parser.parse_args()

    diff = diff_reports(args.baseline, args.current)
    json_output = write_json(diff, args.json_output)
    markdown_output = write_markdown(diff, args.markdown_output)
    print(f"Diff written to {json_output} and {markdown_output}. Regression: {diff.has_regression}")
    if args.fail_on_regression and diff.has_regression:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
