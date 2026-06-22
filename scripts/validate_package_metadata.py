from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


EXPECTED_OWASP_DOCS = [
    "LLM01_PROMPT_INJECTION.md",
    "LLM02_SENSITIVE_INFORMATION_DISCLOSURE.md",
    "LLM03_SUPPLY_CHAIN.md",
    "LLM04_DATA_AND_MODEL_POISONING.md",
    "LLM05_IMPROPER_OUTPUT_HANDLING.md",
    "LLM06_EXCESSIVE_AGENCY.md",
    "LLM07_SYSTEM_PROMPT_LEAKAGE.md",
    "LLM08_VECTOR_AND_EMBEDDING_WEAKNESSES.md",
    "LLM09_MISINFORMATION.md",
    "LLM10_UNBOUNDED_CONSUMPTION.md",
]
EXPECTED_MITRE_ATLAS_DOC = Path("docs/MITRE_ATLAS_AI_MATRIX.md")


@dataclass(slots=True)
class PackageMetadataValidationResult:
    status: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class PackageMetadataValidator:
    """Validates release metadata before packaging or publishing."""

    def __init__(self, pyproject_path: str | Path = "pyproject.toml", config_path: str | Path = "config/default.yaml") -> None:
        self.pyproject_path = Path(pyproject_path)
        self.config_path = Path(config_path)

    def validate(self) -> PackageMetadataValidationResult:
        pyproject = self.pyproject_path.read_text(encoding="utf-8")
        config = yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
        errors: list[str] = []
        warnings: list[str] = []
        package_name = self._match(pyproject, r'^name = "([^"]+)"')
        package_version = self._match(pyproject, r'^version = "([^"]+)"')
        framework = config.get("framework", {})
        if package_name != "vulnoraiq":
            errors.append(f"Unexpected package name: {package_name}")
        if package_version != str(framework.get("version")):
            errors.append(f"pyproject version {package_version} does not match framework version {framework.get('version')}")
        if framework.get("display_name") != "VulnoraIQ":
            errors.append("framework.display_name must be VulnoraIQ")
        for command in (
            "vulnoraiq",
            "vulnoraiq-web",
            "vulnoraiq-dashboard",
            "vulnoraiq-diff",
            "vulnoraiq-package",
            "vulnoraiq-benchmark",
            "vulnoraiq-generate-atlas-matrix",
            "vulnoraiq-html-export",
            "vulnoraiq-validate-package",
        ):
            if command not in pyproject:
                errors.append(f"Missing CLI entry point: {command}")
        readme = Path("README.md").read_text(encoding="utf-8")
        if "not ready for real-world VAPT" not in readme:
            warnings.append("README maturity warning was not found")
        owasp_dir = Path("docs/owasp")
        for expected_doc in EXPECTED_OWASP_DOCS:
            if not (owasp_dir / expected_doc).exists():
                errors.append(f"Missing OWASP implementation doc: {expected_doc}")
        if not EXPECTED_MITRE_ATLAS_DOC.exists():
            errors.append(f"Missing MITRE ATLAS AI matrix doc: {EXPECTED_MITRE_ATLAS_DOC}")
        if not Path("scripts/generate_mitre_atlas_matrix.py").exists():
            errors.append("Missing MITRE ATLAS matrix generator")
        if not Path("examples/local_demo_targets/owasp_fixture_targets.py").exists():
            errors.append("Missing OWASP fixture target file")
        if not Path("core/evaluators.py").exists():
            errors.append("Missing deterministic evaluator suite")
        return PackageMetadataValidationResult("fail" if errors else "warn" if warnings else "pass", errors, warnings)

    @staticmethod
    def _match(text: str, pattern: str) -> str | None:
        match = re.search(pattern, text, flags=re.MULTILINE)
        return match.group(1) if match else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate VulnoraIQ package metadata before release.")
    parser.add_argument("--pyproject", default="pyproject.toml")
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args()
    result = PackageMetadataValidator(args.pyproject, args.config).validate()
    print(f"Package metadata validation status: {result.status}")
    for error in result.errors:
        print(f"ERROR: {error}")
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    if result.status == "fail":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
