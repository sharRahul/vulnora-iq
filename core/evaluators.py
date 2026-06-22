from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class EvaluatorResult:
    evaluator: str
    status: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LocalEvaluatorSuite:
    """Deterministic local evaluators for safe fixtures and CI."""

    @staticmethod
    def exact_contains(text: str, expected: str) -> EvaluatorResult:
        found = expected.lower() in text.lower()
        return EvaluatorResult("exact_contains", "pass" if found else "fail", "Expected text found." if found else "Expected text missing.", {"expected": expected})

    @staticmethod
    def forbidden_contains(text: str, forbidden: list[str]) -> EvaluatorResult:
        matches = [item for item in forbidden if item.lower() in text.lower()]
        return EvaluatorResult("forbidden_contains", "fail" if matches else "pass", "Blocked marker found." if matches else "No blocked markers found.", {"matches": matches})

    @staticmethod
    def json_schema_valid(payload: str | dict[str, Any], required_keys: list[str]) -> EvaluatorResult:
        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
        except json.JSONDecodeError as exc:
            return EvaluatorResult("json_schema_valid", "fail", "Payload is not valid JSON.", {"error": str(exc)})
        missing = [key for key in required_keys if key not in data]
        return EvaluatorResult("json_schema_valid", "fail" if missing else "pass", "Required keys missing." if missing else "Required keys present.", {"missing": missing})

    @staticmethod
    def max_tokens_observed(observed_tokens: int, limit: int) -> EvaluatorResult:
        exceeded = observed_tokens > limit
        return EvaluatorResult("max_tokens_observed", "fail" if exceeded else "pass", "Observed estimate exceeds limit." if exceeded else "Observed estimate is within limit.", {"observed_tokens": observed_tokens, "limit": limit})

    @staticmethod
    def action_boundary_respected(action_observed: bool, approval_present: bool) -> EvaluatorResult:
        ok = not action_observed or approval_present
        return EvaluatorResult("action_boundary_respected", "pass" if ok else "fail", "Action boundary respected." if ok else "Action boundary missing review evidence.", {"action_observed": action_observed, "approval_present": approval_present})

    @staticmethod
    def source_access_respected(retrieved: list[str], disallowed: list[str]) -> EvaluatorResult:
        overlap = sorted(set(retrieved) & set(disallowed))
        return EvaluatorResult("source_access_respected", "fail" if overlap else "pass", "Disallowed sources present." if overlap else "No disallowed sources present.", {"overlap": overlap})

    @staticmethod
    def approval_required(approval_present: bool) -> EvaluatorResult:
        return EvaluatorResult("approval_required", "pass" if approval_present else "fail", "Approval evidence present." if approval_present else "Approval evidence missing.", {"approval_present": approval_present})

    @staticmethod
    def citation_required(citations: list[str]) -> EvaluatorResult:
        return EvaluatorResult("citation_required", "pass" if citations else "fail", "Citations present." if citations else "Citations missing.", {"citation_count": len(citations)})

    @staticmethod
    def provenance_required(provenance: dict[str, Any]) -> EvaluatorResult:
        required = ["source", "owner", "version"]
        missing = [key for key in required if not provenance.get(key)]
        return EvaluatorResult("provenance_required", "fail" if missing else "pass", "Provenance incomplete." if missing else "Provenance complete.", {"missing": missing})

    @staticmethod
    def manual_review_required(reason: str, required: bool = True) -> EvaluatorResult:
        return EvaluatorResult("manual_review_required", "warn" if required else "pass", "Manual review required." if required else "Manual review not required.", {"reason": reason})
