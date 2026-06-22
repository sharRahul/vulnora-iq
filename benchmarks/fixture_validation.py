from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(slots=True)
class BenchmarkFixtureValidationResult:
    status: str
    fixture_count: int
    covered_modules: list[str]
    errors: list[str] = field(default_factory=list)


class BenchmarkFixtureValidator:
    def __init__(self, fixture_path: str | Path = "benchmarks/fixtures/owasp_starter_fixture.yaml") -> None:
        self.fixture_path = Path(fixture_path)

    def validate(self) -> BenchmarkFixtureValidationResult:
        data = yaml.safe_load(self.fixture_path.read_text(encoding="utf-8")) or {}
        fixtures = data.get("fixtures", [])
        errors: list[str] = []
        covered = sorted({str(item.get("module")) for item in fixtures})
        expected = {f"owasp_llm{index:02d}" for index in range(1, 11)}
        present = {self._category_id(module) for module in covered if module.startswith("owasp_llm")}
        missing = sorted(expected - present)
        if missing:
            errors.append(f"Missing OWASP starter fixture categories: {', '.join(missing)}")
        for item in fixtures:
            for field_name in ("id", "module", "expected_oracle_status", "target"):
                if not item.get(field_name):
                    errors.append(f"Fixture missing {field_name}: {item}")
        return BenchmarkFixtureValidationResult("fail" if errors else "pass", len(fixtures), covered, errors)

    @staticmethod
    def _category_id(module_name: str) -> str:
        parts = module_name.split("_")
        return "_".join(parts[:2]) if len(parts) >= 2 else module_name
