from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from agent_testing.runtime_manifest import AgentRuntimeValidator


@dataclass(slots=True)
class AgentExecutionScenarioResult:
    scenario_id: str
    status: str
    tool_call_count: int
    memory_write_count: int
    observed_status: str = "pass"
    expected_status: str = "pass"
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AgentExecutionHarnessResult:
    status: str
    scenario_count: int
    passed_count: int
    failed_count: int
    warning_count: int
    results: list[AgentExecutionScenarioResult]


class AgentExecutionHarness:
    """Safe local harness for agent tool, memory, approval, and rollback planning."""

    def __init__(
        self,
        runtime_manifest_path: str | Path = "config/agent_runtime.yaml",
        scenario_path: str | Path = "config/agent_execution_scenarios.yaml",
    ) -> None:
        self.runtime_manifest_path = Path(runtime_manifest_path)
        self.scenario_path = Path(scenario_path)

    def run(self) -> AgentExecutionHarnessResult:
        runtime_validation = AgentRuntimeValidator().validate(self.runtime_manifest_path)
        if runtime_validation.status == "fail":
            result = AgentExecutionScenarioResult(
                scenario_id="agent_runtime_manifest",
                status="fail",
                tool_call_count=0,
                memory_write_count=0,
                observed_status="fail",
                expected_status="pass",
                errors=runtime_validation.errors,
                warnings=runtime_validation.warnings,
            )
            return AgentExecutionHarnessResult("fail", 1, 0, 1, 0, [result])

        runtime = yaml.safe_load(self.runtime_manifest_path.read_text(encoding="utf-8")) or {}
        scenario_manifest = yaml.safe_load(self.scenario_path.read_text(encoding="utf-8")) or {}
        tools = {str(item["name"]): item for item in runtime.get("tools", [])}
        memory_stores = {str(item["name"]): item for item in runtime.get("memory", {}).get("stores", [])}
        required_plan_fields = runtime.get("orchestration", {}).get("required_plan_fields", [])
        high_impact_categories = set(runtime.get("orchestration", {}).get("high_impact_categories", []))
        results = [
            self._run_scenario(item, tools, memory_stores, required_plan_fields, high_impact_categories)
            for item in scenario_manifest.get("scenarios", [])
        ]
        passed = sum(1 for item in results if item.status == "pass")
        failed = sum(1 for item in results if item.status == "fail")
        warning = sum(1 for item in results if item.status == "warn")
        status = "fail" if failed else "warn" if warning else "pass"
        return AgentExecutionHarnessResult(status, len(results), passed, failed, warning, results)

    def _run_scenario(
        self,
        scenario: dict[str, Any],
        tools: dict[str, dict[str, Any]],
        memory_stores: dict[str, dict[str, Any]],
        required_plan_fields: list[str],
        high_impact_categories: set[str],
    ) -> AgentExecutionScenarioResult:
        scenario_id = str(scenario["id"])
        errors: list[str] = []
        warnings: list[str] = []
        self._validate_plan_fields(scenario, required_plan_fields, errors)
        self._validate_tool_calls(scenario, tools, high_impact_categories, errors)
        self._validate_memory_writes(scenario, memory_stores, errors)

        expected_status = str(scenario.get("expected_status", "pass"))
        observed_status = "fail" if errors else "warn" if warnings else "pass"
        scenario_status = "pass" if expected_status == observed_status else "fail"
        if scenario_status == "fail":
            errors.append(f"Expected scenario status {expected_status}, observed {observed_status}")

        return AgentExecutionScenarioResult(
            scenario_id=scenario_id,
            status=scenario_status,
            tool_call_count=len(scenario.get("requested_tool_calls", [])),
            memory_write_count=len(scenario.get("memory_writes", [])),
            observed_status=observed_status,
            expected_status=expected_status,
            errors=errors,
            warnings=warnings,
        )

    @staticmethod
    def _validate_plan_fields(scenario: dict[str, Any], required_plan_fields: list[str], errors: list[str]) -> None:
        field_map = {
            "objective": scenario.get("objective"),
            "steps": scenario.get("requested_tool_calls", []),
            "approval_points": scenario.get("approval_points", []),
            "rollback_plan": scenario.get("rollback_plan"),
        }
        for field_name in required_plan_fields:
            if not field_map.get(field_name):
                errors.append(f"Scenario is missing required plan field: {field_name}")

    @staticmethod
    def _validate_tool_calls(
        scenario: dict[str, Any],
        tools: dict[str, dict[str, Any]],
        high_impact_categories: set[str],
        errors: list[str],
    ) -> None:
        approval_points = set(scenario.get("approval_points", []))
        for call in scenario.get("requested_tool_calls", []):
            tool_name = str(call.get("tool"))
            tool = tools.get(tool_name)
            if not tool:
                errors.append(f"Unknown tool requested: {tool_name}")
                continue
            if tool.get("allowed") is not True:
                errors.append(f"Tool is not allowed by runtime manifest: {tool_name}")
            if tool.get("requires_approval") is True and call.get("approved") is not True:
                errors.append(f"Tool call requires approval but call is not approved: {tool_name}")
            category = str(call.get("category") or tool.get("category"))
            if category in high_impact_categories and not approval_points:
                errors.append(f"High-impact tool call lacks approval point: {tool_name}")

    @staticmethod
    def _validate_memory_writes(
        scenario: dict[str, Any],
        memory_stores: dict[str, dict[str, Any]],
        errors: list[str],
    ) -> None:
        approval_points = set(scenario.get("approval_points", []))
        for write in scenario.get("memory_writes", []):
            store_name = str(write.get("store"))
            store = memory_stores.get(store_name)
            if not store:
                errors.append(f"Unknown memory store requested: {store_name}")
                continue
            if store.get("write_approval_required") is True and write.get("approved") is not True:
                errors.append(f"Memory write requires approval but write is not approved: {store_name}")
            if store.get("write_approval_required") is True and not approval_points:
                errors.append(f"Memory write lacks approval point: {store_name}")
            if store.get("integrity_check") and not write.get("integrity_reference"):
                errors.append(f"Memory write lacks integrity reference: {store_name}")
