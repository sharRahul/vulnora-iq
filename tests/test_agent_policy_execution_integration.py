from __future__ import annotations

from core.scanner import Scanner


def test_agent_tool_policy_includes_execution_harness_evidence() -> None:
    result = Scanner().scan(target_name="demo", profile_name="agent")

    policy = next(item for item in result.policy_results if item.policy_id == "tool_execution_requires_allowlist")
    assert policy.status == "pass"
    assert policy.evidence["execution_status"] == "pass"
    assert policy.evidence["execution_scenario_count"] == 3
    assert policy.evidence["execution_failed_count"] == 0
    assert policy.evidence["execution_results"]


def test_agent_approval_policy_includes_memory_and_orchestration_evidence() -> None:
    result = Scanner().scan(target_name="demo", profile_name="agent")

    policy = next(item for item in result.policy_results if item.policy_id == "critical_ai_action_requires_human_approval")
    assert policy.status == "pass"
    assert policy.evidence["memory_store_count"] == 2
    assert policy.evidence["execution_passed_count"] == 3
