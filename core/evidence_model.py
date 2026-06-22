from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class OracleResult:
    oracle_id: str
    owasp_id: str
    status: str
    expected_matches: list[str] = field(default_factory=list)
    forbidden_matches: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class InteractionEvidence:
    payload_id: str
    input_preview: str
    response_preview: str
    expected_behavior: str
    oracle_status: str
    oracle_result: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class OwaspOracleRegistry:
    """Safe local oracle registry for starter OWASP LLM checks."""

    def __init__(self, path: str | Path = "config/owasp_oracles.yaml") -> None:
        self.path = Path(path)
        self._data: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        if self._data is None:
            self._data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        return self._data

    def coverage_status(self) -> str:
        return str(self.load().get("coverage_status", "unknown"))

    def oracle_for(self, module_name: str) -> dict[str, Any] | None:
        return self.load().get("oracles", {}).get(module_name)

    def coverage_summary(self) -> dict[str, Any]:
        oracles = self.load().get("oracles", {})
        expected_ids = {f"owasp_llm{index:02d}" for index in range(1, 11)}
        present_ids = {self._category_id(key) for key in oracles if key.startswith("owasp_llm")}
        return {
            "coverage_status": self.coverage_status(),
            "oracle_count": len(oracles),
            "owasp_category_count": len(present_ids),
            "missing_categories": sorted(expected_ids - present_ids),
        }

    def evaluate(self, module_name: str, evidence: dict[str, Any], response_text: str) -> OracleResult:
        oracle = self.oracle_for(module_name)
        if not oracle:
            return OracleResult(
                oracle_id=module_name,
                owasp_id=evidence.get("owasp_id", "UNMAPPED"),
                status="warn",
                notes=["No oracle configured for module."],
            )
        lowered = response_text.lower()
        expected = [signal for signal in oracle.get("expected_signals", []) if str(signal).lower() in lowered]
        forbidden = [signal for signal in oracle.get("forbidden_signals", []) if str(signal).lower() in lowered]
        missing_evidence = [field for field in oracle.get("required_evidence", []) if field not in evidence]
        status = "fail" if forbidden or missing_evidence else "pass" if expected or not oracle.get("expected_signals") else "warn"
        notes: list[str] = []
        if not expected and oracle.get("expected_signals"):
            notes.append("No expected response signals were observed; manual review may be needed.")
        return OracleResult(
            oracle_id=module_name,
            owasp_id=str(oracle.get("owasp_id", evidence.get("owasp_id", "UNMAPPED"))),
            status=status,
            expected_matches=[str(item) for item in expected],
            forbidden_matches=[str(item) for item in forbidden],
            missing_evidence=[str(item) for item in missing_evidence],
            notes=notes,
        )

    @staticmethod
    def _category_id(module_name: str) -> str:
        parts = module_name.split("_")
        return "_".join(parts[:2]) if len(parts) >= 2 else module_name
