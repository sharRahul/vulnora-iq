from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from rag_testing.corpus_manifest import CorpusManifestValidator


@dataclass(slots=True)
class RetrievalScenarioResult:
    scenario_id: str
    status: str
    retrieved_documents: list[str]
    source_trust_score: float
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RetrievalHarnessResult:
    status: str
    scenario_count: int
    passed_count: int
    failed_count: int
    warning_count: int
    minimum_source_trust_score: float
    results: list[RetrievalScenarioResult]


class LocalRetrievalHarness:
    """Safe local RAG retrieval harness using corpus metadata and scenario manifests."""

    def __init__(
        self,
        corpus_manifest_path: str | Path = "config/rag_corpus_manifest.yaml",
        scenario_path: str | Path = "config/rag_retrieval_scenarios.yaml",
    ) -> None:
        self.corpus_manifest_path = Path(corpus_manifest_path)
        self.scenario_path = Path(scenario_path)

    def run(self) -> RetrievalHarnessResult:
        corpus_validation = CorpusManifestValidator().validate(self.corpus_manifest_path)
        if corpus_validation.status == "fail":
            result = RetrievalScenarioResult(
                scenario_id="corpus_manifest",
                status="fail",
                retrieved_documents=[],
                source_trust_score=0.0,
                errors=corpus_validation.errors,
                warnings=corpus_validation.warnings,
            )
            return RetrievalHarnessResult("fail", 1, 0, 1, 0, 1.0, [result])

        corpus = yaml.safe_load(self.corpus_manifest_path.read_text(encoding="utf-8")) or {}
        scenario_manifest = yaml.safe_load(self.scenario_path.read_text(encoding="utf-8")) or {}
        documents = {str(item["id"]): item for item in corpus.get("documents", [])}
        minimum_score = float(scenario_manifest.get("minimum_source_trust_score", 0.75))
        results = [self._run_scenario(item, documents, minimum_score) for item in scenario_manifest.get("scenarios", [])]
        passed = sum(1 for item in results if item.status == "pass")
        failed = sum(1 for item in results if item.status == "fail")
        warning = sum(1 for item in results if item.status == "warn")
        overall = "fail" if failed else "warn" if warning else "pass"
        return RetrievalHarnessResult(
            status=overall,
            scenario_count=len(results),
            passed_count=passed,
            failed_count=failed,
            warning_count=warning,
            minimum_source_trust_score=minimum_score,
            results=results,
        )

    def _run_scenario(
        self,
        scenario: dict[str, Any],
        documents: dict[str, dict[str, Any]],
        minimum_score: float,
    ) -> RetrievalScenarioResult:
        scenario_id = str(scenario["id"])
        requester_groups = set(scenario.get("requester_groups", []))
        retrieved = self._retrieve_documents(documents, requester_groups)
        retrieved_ids = [str(item["id"]) for item in retrieved]
        expected = set(scenario.get("expected_documents", []))
        disallowed = set(scenario.get("disallowed_documents", []))
        errors: list[str] = []
        warnings: list[str] = []

        missing_expected = sorted(expected - set(retrieved_ids))
        if missing_expected:
            errors.append(f"Expected documents not retrieved: {', '.join(missing_expected)}")

        leaked = sorted(disallowed & set(retrieved_ids))
        if leaked:
            errors.append(f"Disallowed documents were retrieved: {', '.join(leaked)}")

        if len(retrieved_ids) < int(scenario.get("minimum_expected_documents", 0)):
            errors.append("Retrieved document count is below the scenario minimum")

        if scenario.get("require_approved_sources", True):
            unapproved = [str(item["id"]) for item in retrieved if str(item.get("approval_status", "")).lower() != "approved"]
            if unapproved:
                errors.append(f"Unapproved sources were retrieved: {', '.join(unapproved)}")

        score = self._source_trust_score(retrieved)
        if retrieved and score < minimum_score:
            warnings.append(f"Source trust score {score:.2f} is below minimum {minimum_score:.2f}")

        status = "fail" if errors else "warn" if warnings else "pass"
        return RetrievalScenarioResult(scenario_id, status, retrieved_ids, score, errors, warnings)

    @staticmethod
    def _retrieve_documents(documents: dict[str, dict[str, Any]], requester_groups: set[str]) -> list[dict[str, Any]]:
        retrieved: list[dict[str, Any]] = []
        for document in documents.values():
            allowed_groups = set(document.get("allowed_groups", []))
            if requester_groups & allowed_groups:
                retrieved.append(document)
        return retrieved

    @staticmethod
    def _source_trust_score(retrieved: list[dict[str, Any]]) -> float:
        if not retrieved:
            return 1.0
        score = 0.0
        for document in retrieved:
            document_score = 0.0
            if str(document.get("approval_status", "")).lower() == "approved":
                document_score += 0.4
            if document.get("content_hash"):
                document_score += 0.25
            if document.get("owner"):
                document_score += 0.15
            if document.get("last_reviewed"):
                document_score += 0.1
            if document.get("allowed_groups"):
                document_score += 0.1
            score += document_score
        return round(score / len(retrieved), 4)
