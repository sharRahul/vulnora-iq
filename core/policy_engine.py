from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.types import Finding, PolicyResult, ScanResult
from rag_testing.corpus_manifest import CorpusManifestValidator


class PolicyEngine:
    """Evaluates governance policies against assessment results.

    This engine keeps policy decisions explicit and reportable. It does not replace
    human review; it creates consistent pass, warn, and fail signals for CI/CD and
    audit evidence.
    """

    def evaluate(self, result: ScanResult, config: dict[str, Any]) -> list[PolicyResult]:
        policies = config.get("policies", {}).get("policies", {})
        evaluations: list[PolicyResult] = []

        if policies.get("no_secret_disclosure", {}).get("enabled", False):
            evaluations.append(self._evaluate_sensitive_marker_policy(result.findings, policies["no_secret_disclosure"]))

        if policies.get("tool_execution_requires_allowlist", {}).get("enabled", False):
            evaluations.append(self._evaluate_tool_allowlist_policy(result, config, policies["tool_execution_requires_allowlist"]))

        if policies.get("rag_corpus_integrity_required", {}).get("enabled", False):
            evaluations.append(self._evaluate_rag_integrity_policy(result, config, policies["rag_corpus_integrity_required"]))

        if policies.get("critical_ai_action_requires_human_approval", {}).get("enabled", False):
            evaluations.append(self._evaluate_approval_policy(config, policies["critical_ai_action_requires_human_approval"]))

        return evaluations

    def _evaluate_sensitive_marker_policy(self, findings: list[Finding], policy: dict[str, Any]) -> PolicyResult:
        markers = [str(item).lower() for item in policy.get("patterns", [])]
        matches: list[dict[str, str]] = []

        for finding in findings:
            text = json.dumps(finding.evidence, default=str).lower()
            text += " " + finding.description.lower()
            for marker in markers:
                if marker and marker in text:
                    matches.append({"finding": finding.title, "marker": marker})

        if matches:
            return PolicyResult(
                policy_id="no_secret_disclosure",
                status="fail",
                decision=policy.get("decision", "fail_on_high"),
                message="Sensitive data markers were found in assessment evidence or descriptions.",
                evidence={"matches": matches},
            )

        return PolicyResult(
            policy_id="no_secret_disclosure",
            status="pass",
            decision=policy.get("decision", "fail_on_high"),
            message="No configured sensitive data markers were found in the report evidence.",
            evidence={"markers_checked": markers},
        )

    def _evaluate_tool_allowlist_policy(self, result: ScanResult, config: dict[str, Any], policy: dict[str, Any]) -> PolicyResult:
        if result.profile_name != "agent":
            return PolicyResult(
                policy_id="tool_execution_requires_allowlist",
                status="pass",
                decision=policy.get("decision", "fail_on_medium"),
                message="Agent tool allowlist policy is not applicable to this profile.",
                evidence={"profile": result.profile_name},
            )

        target_config = config.get("targets", {}).get("targets", {}).get(result.target_name, {})
        allowed_tools = target_config.get("allowed_tools", [])
        if not allowed_tools:
            return PolicyResult(
                policy_id="tool_execution_requires_allowlist",
                status="warn",
                decision=policy.get("decision", "fail_on_medium"),
                message="Agent profile selected but no allowed_tools list is configured for the target.",
                evidence={"target": result.target_name},
            )

        return PolicyResult(
            policy_id="tool_execution_requires_allowlist",
            status="pass",
            decision=policy.get("decision", "fail_on_medium"),
            message="Configured target has an explicit allowed_tools list.",
            evidence={"target": result.target_name, "allowed_tools_count": len(allowed_tools)},
        )

    def _evaluate_rag_integrity_policy(self, result: ScanResult, config: dict[str, Any], policy: dict[str, Any]) -> PolicyResult:
        if result.profile_name != "rag":
            return PolicyResult(
                policy_id="rag_corpus_integrity_required",
                status="pass",
                decision=policy.get("decision", "warn"),
                message="RAG corpus integrity policy is not applicable to this profile.",
                evidence={"profile": result.profile_name},
            )

        corpus = config.get("default", {}).get("rag_corpus", {})
        manifest_path = corpus.get("manifest_path")
        if not manifest_path:
            return PolicyResult(
                policy_id="rag_corpus_integrity_required",
                status="warn",
                decision=policy.get("decision", "warn"),
                message="RAG profile selected but no corpus manifest is configured.",
                evidence={"configured": corpus},
            )

        validation = CorpusManifestValidator().validate(Path(manifest_path))
        return PolicyResult(
            policy_id="rag_corpus_integrity_required",
            status=validation.status,
            decision=policy.get("decision", "warn"),
            message=f"RAG corpus manifest validation completed with status: {validation.status}.",
            evidence={
                "manifest_path": validation.manifest_path,
                "document_count": validation.document_count,
                "errors": validation.errors,
                "warnings": validation.warnings,
            },
        )

    def _evaluate_approval_policy(self, config: dict[str, Any], policy: dict[str, Any]) -> PolicyResult:
        approval = config.get("default", {}).get("approval_gates", {})
        if not approval.get("high_impact_actions_require_approval", False):
            return PolicyResult(
                policy_id="critical_ai_action_requires_human_approval",
                status="warn",
                decision=policy.get("decision", "fail_on_high"),
                message="Human approval gate for high-impact AI actions is not configured.",
                evidence={"configured": approval},
            )

        return PolicyResult(
            policy_id="critical_ai_action_requires_human_approval",
            status="pass",
            decision=policy.get("decision", "fail_on_high"),
            message="Human approval gate for high-impact AI actions is configured.",
            evidence={"configured": approval},
        )
