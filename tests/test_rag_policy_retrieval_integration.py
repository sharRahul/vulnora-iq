from __future__ import annotations

from core.scanner import Scanner


def test_rag_policy_includes_retrieval_harness_evidence() -> None:
    result = Scanner().scan(target_name="demo", profile_name="rag")

    policy = next(item for item in result.policy_results if item.policy_id == "rag_corpus_integrity_required")
    assert policy.status == "pass"
    assert policy.evidence["retrieval_status"] == "pass"
    assert policy.evidence["retrieval_scenario_count"] == 3
    assert policy.evidence["retrieval_failed_count"] == 0
    assert policy.evidence["retrieval_results"]
