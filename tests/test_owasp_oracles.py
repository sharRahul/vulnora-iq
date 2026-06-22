from __future__ import annotations

from core.evidence_model import OwaspOracleRegistry
from core.scanner import Scanner


def test_oracle_registry_covers_all_owasp_llm_categories() -> None:
    summary = OwaspOracleRegistry().coverage_summary()

    assert summary["coverage_status"] == "starter_validated"
    assert summary["owasp_category_count"] == 10
    assert summary["missing_categories"] == []


def test_baseline_scan_contains_structured_oracle_evidence() -> None:
    result = Scanner().scan(target_name="demo", profile_name="baseline")

    assert result.metadata["owasp_oracle_coverage"]["owasp_category_count"] == 10
    for finding in result.findings:
        assert "oracle_coverage_status" in finding.evidence
        assert "interaction_evidence" in finding.evidence
        assert finding.evidence["interaction_evidence"]
        assert "oracle_status" in finding.evidence["interaction_evidence"][0]
