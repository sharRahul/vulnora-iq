from __future__ import annotations

from scripts.validate_production_testing_readiness import ProductionTestingReadinessValidator


def test_production_testing_readiness_gate_without_functional_run(tmp_path):
    summary = ProductionTestingReadinessValidator(tmp_path).validate(run_functional=False)

    check_ids = {check.id for check in summary.checks}
    assert summary.status in {"pass", "warn"}
    assert "package_metadata" in check_ids
    assert "target_contracts" in check_ids
    assert "benchmark_fixtures" in check_ids
    assert "mitre_atlas_mapping" in check_ids
    assert "owasp_oracle_coverage" in check_ids
    assert "non_demo_authorisation_gate" in check_ids
    assert "documentation_and_ci_wiring" in check_ids
    assert (tmp_path / "production-testing-readiness-summary.json").exists()
    assert (tmp_path / "production-testing-readiness-summary.md").exists()


def test_non_demo_authorisation_gate_blocks_configured_targets(tmp_path):
    summary = ProductionTestingReadinessValidator(tmp_path).validate(run_functional=False)
    gate = next(check for check in summary.checks if check.id == "non_demo_authorisation_gate")

    assert gate.status == "pass"
    assert gate.details["blocked_target"] == "custom_http_agent"
