from __future__ import annotations

from pathlib import Path

import yaml

from scripts.validate_owasp_atlas_mappings import validate_default_configs, validate_mapping_file


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _valid_entry() -> dict:
    return {
        "owasp_family": "LLM",
        "owasp_id": "LLM01:2025",
        "mitre_atlas_tactics": ["AML.TA0004", "AML.TA0005"],
        "mapping_status": "candidate",
        "evidence_surface": ["prompt", "response", "scanner_evidence"],
        "manual_review_required": True,
    }


def test_validate_mapping_file_passes_for_complete_active_entries(tmp_path: Path) -> None:
    path = tmp_path / "oracles.yaml"
    _write_yaml(path, {"oracles": {"owasp_llm01_prompt_injection": _valid_entry()}})

    result = validate_mapping_file(path, "oracles", "test_oracles")

    assert result["status"] == "pass"
    assert result["checked_count"] == 1
    assert result["errors"] == []


def test_validate_mapping_file_fails_when_required_mapping_field_missing(tmp_path: Path) -> None:
    path = tmp_path / "oracles.yaml"
    entry = _valid_entry()
    entry.pop("mitre_atlas_tactics")
    _write_yaml(path, {"oracles": {"owasp_llm01_prompt_injection": entry}})

    result = validate_mapping_file(path, "oracles", "test_oracles")

    assert result["status"] == "fail"
    assert any("mitre_atlas_tactics" in error for error in result["errors"])


def test_validate_mapping_file_rejects_invalid_field_shapes(tmp_path: Path) -> None:
    path = tmp_path / "rules.yaml"
    entry = _valid_entry()
    entry["mitre_atlas_tactics"] = ["TA0004"]
    entry["evidence_surface"] = ["not_a_surface"]
    entry["manual_review_required"] = "yes"
    _write_yaml(path, {"rules": {"owasp_llm01_prompt_injection": entry}})

    result = validate_mapping_file(path, "rules", "test_rules")

    assert result["status"] == "fail"
    assert any("invalid MITRE ATLAS tactic" in error for error in result["errors"])
    assert any("invalid evidence_surface" in error for error in result["errors"])
    assert any("manual_review_required must be a boolean" in error for error in result["errors"])


def test_validate_mapping_file_skips_inactive_entries(tmp_path: Path) -> None:
    path = tmp_path / "oracles.yaml"
    inactive_missing_metadata = {"active": False, "owasp_id": "LLM01:2025"}
    _write_yaml(path, {"oracles": {"owasp_llm01_prompt_injection": inactive_missing_metadata}})

    result = validate_mapping_file(path, "oracles", "test_oracles")

    assert result["status"] == "fail"
    assert result["checked_count"] == 0
    assert result["skipped_count"] == 1
    assert any("no active entries" in error for error in result["errors"])


def test_validate_default_configs_passes_repository_configs() -> None:
    result = validate_default_configs()

    assert result["status"] == "pass"
    assert result["checked_count"] >= 20
    assert result["errors"] == []
