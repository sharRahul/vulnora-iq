from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class AtlasValidationResult:
    mapping_path: str
    status: str
    technique_count: int = 0
    module_mapping_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class MitreAtlasMapping:
    """Loads and validates the local MITRE ATLAS mapping catalog."""

    def __init__(self, path: str | Path = "config/mitre_atlas_mapping.yaml") -> None:
        self.path = Path(path)
        self._data: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        if self._data is None:
            self._data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        return self._data

    def techniques_for_module(self, module_name: str) -> list[str]:
        data = self.load()
        return list(data.get("module_mappings", {}).get(module_name, []))

    def validate(self) -> AtlasValidationResult:
        if not self.path.exists():
            return AtlasValidationResult(
                mapping_path=str(self.path),
                status="fail",
                errors=[f"MITRE ATLAS mapping file not found: {self.path}"],
            )

        data = self.load()
        techniques = data.get("techniques", {}) or {}
        module_mappings = data.get("module_mappings", {}) or {}
        errors: list[str] = []
        warnings: list[str] = []

        if not data.get("source", {}).get("atlas_version"):
            warnings.append("source.atlas_version is missing")
        if not techniques:
            errors.append("No techniques are defined")
        if not module_mappings:
            errors.append("No module mappings are defined")

        for technique_id, technique in techniques.items():
            if not str(technique_id).startswith("AML.T"):
                errors.append(f"Technique id does not look like an ATLAS AML technique: {technique_id}")
            if not technique.get("name"):
                errors.append(f"Technique {technique_id} is missing a name")
            if not technique.get("rationale"):
                warnings.append(f"Technique {technique_id} is missing a rationale")

        for module_name, mapped_ids in module_mappings.items():
            if not mapped_ids:
                errors.append(f"Module {module_name} has no mapped techniques")
            for technique_id in mapped_ids:
                if technique_id not in techniques:
                    errors.append(f"Module {module_name} references unknown technique {technique_id}")

        status = "fail" if errors else "warn" if warnings else "pass"
        return AtlasValidationResult(
            mapping_path=str(self.path),
            status=status,
            technique_count=len(techniques),
            module_mapping_count=len(module_mappings),
            errors=errors,
            warnings=warnings,
        )
