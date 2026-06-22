from __future__ import annotations

from scripts.validate_production_testing_readiness import (
    ProductionTestingReadinessSummary,
    ProductionTestingReadinessValidator,
    ReadinessCheck,
)


def test_non_demo_authorisation_gate_blocks_configured_targets(tmp_path):
    validator = ProductionTestingReadinessValidator(tmp_path)
    gate = validator._check_non_demo_authorisation_gate()

    assert gate.status == "pass"
    assert gate.details["blocked_target"] == "custom_http_agent"


def test_readiness_summary_outputs_are_written(tmp_path):
    validator = ProductionTestingReadinessValidator(tmp_path)
    summary = ProductionTestingReadinessSummary(
        status="pass",
        output_dir=str(tmp_path),
        checks=[
            ReadinessCheck(
                id="unit_test_gate",
                status="pass",
                message="Synthetic readiness gate used for output serialization testing.",
            )
        ],
    )

    validator._write_outputs(summary)

    json_output = tmp_path / "production-testing-readiness-summary.json"
    markdown_output = tmp_path / "production-testing-readiness-summary.md"
    assert json_output.exists()
    assert markdown_output.exists()
    assert "unit_test_gate" in json_output.read_text(encoding="utf-8")
    assert "unit_test_gate" in markdown_output.read_text(encoding="utf-8")


def test_overall_status_precedence():
    checks = [
        ReadinessCheck(id="pass", status="pass", message="pass"),
        ReadinessCheck(id="warn", status="warn", message="warn"),
        ReadinessCheck(id="fail", status="fail", message="fail"),
    ]

    assert ProductionTestingReadinessValidator._overall_status(checks) == "fail"
    assert ProductionTestingReadinessValidator._overall_status(checks[:2]) == "warn"
    assert ProductionTestingReadinessValidator._overall_status(checks[:1]) == "pass"
