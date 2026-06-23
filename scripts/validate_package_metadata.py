from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from scripts.validate_genai_readiness import validate_default as validate_genai_readiness
from scripts.validate_owasp_atlas_mappings import validate_default_configs

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
EXPECTED_CLI_ENTRY_POINTS = [
    "vulnoraiq",
    "vulnoraiq-web",
    "vulnoraiq-dashboard",
    "vulnoraiq-diff",
    "vulnoraiq-package",
    "vulnoraiq-benchmark",
    "vulnoraiq-functional-test",
    "vulnoraiq-production-readiness",
    "vulnoraiq-policy-trend",
    "vulnoraiq-diff-trend",
    "vulnoraiq-refresh-atlas",
    "vulnoraiq-generate-atlas-matrix",
    "vulnoraiq-html-export",
    "vulnoraiq-validate-package",
    "vulnoraiq-validate-owasp-atlas-mappings",
    "vulnoraiq-validate-genai-readiness",
]
EXPECTED_LICENSE = "Apache-2.0"
EXPECTED_LICENSE_FILE = Path("LICENSE")
EXPECTED_MITRE_ATLAS_DOC = Path("docs/MITRE_ATLAS_AI_MATRIX.md")
EXPECTED_THIRD_PARTY_NOTICES = Path("THIRD_PARTY_NOTICES.md")
EXPECTED_DASHBOARD_EXAMPLE = Path("docs/assets/vulnoraiq-webui-home.png")
EXPECTED_FUNCTIONAL_RUNNER = Path("scripts/run_functional_test.py")
EXPECTED_PRODUCTION_READINESS_RUNNER = Path("scripts/validate_production_testing_readiness.py")
EXPECTED_OWASP_ATLAS_MAPPING_RUNNER = Path("scripts/validate_owasp_atlas_mappings.py")
EXPECTED_GENAI_READINESS_RUNNER = Path("scripts/validate_genai_readiness.py")
EXPECTED_GENAI_MANIFEST = Path("benchmarks/fixtures/genai/scenarios.yaml")


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
        package_license = self._match(pyproject, r'^license = \{ text = "([^"]+)" \}')
        framework = config.get("framework", {})
        if package_name != "vulnoraiq":
            errors.append(f"Unexpected package name: {package_name}")
        if package_version != str(framework.get("version")):
            errors.append(f"pyproject version {package_version} does not match framework version {framework.get('version')}")
        if package_license != EXPECTED_LICENSE:
            errors.append(f"pyproject license must be {EXPECTED_LICENSE}, found {package_license}")
        if not EXPECTED_LICENSE_FILE.exists():
            errors.append(f"Missing project license file: {EXPECTED_LICENSE_FILE}")
        else:
            license_text = EXPECTED_LICENSE_FILE.read_text(encoding="utf-8")
            for required_text in (
                "Apache License",
                "Version 2.0, January 2004",
                "Copyright 2026 Rahul Sharma",
                "Licensed under the Apache License, Version 2.0",
            ):
                if required_text not in license_text:
                    errors.append(f"LICENSE missing required Apache-2.0 text: {required_text}")
        if framework.get("display_name") != "VulnoraIQ":
            errors.append("framework.display_name must be VulnoraIQ")
        for command in EXPECTED_CLI_ENTRY_POINTS:
            if command not in pyproject:
                errors.append(f"Missing CLI entry point: {command}")
        readme = Path("README.md").read_text(encoding="utf-8")
        readme_lower = readme.lower()
        if "self-hosted" not in readme_lower or "laptop/server" not in readme_lower:
            warnings.append("README self-hosted laptop/server maturity wording was not found")
        if "certified VAPT-grade assurance" not in readme:
            warnings.append("README assurance limitation wording was not found")
        if "docs/assets/vulnoraiq-webui-home.png" not in readme:
            errors.append("README must include the Web UI home screen image")
        owasp_dir = Path("docs/owasp")
        for expected_doc in EXPECTED_OWASP_DOCS:
            if not (owasp_dir / expected_doc).exists():
                errors.append(f"Missing OWASP implementation doc: {expected_doc}")
        if not EXPECTED_MITRE_ATLAS_DOC.exists():
            errors.append(f"Missing MITRE ATLAS AI matrix doc: {EXPECTED_MITRE_ATLAS_DOC}")
        if not EXPECTED_THIRD_PARTY_NOTICES.exists():
            errors.append(f"Missing third-party notices file: {EXPECTED_THIRD_PARTY_NOTICES}")
        else:
            notice = EXPECTED_THIRD_PARTY_NOTICES.read_text(encoding="utf-8")
            for required_text in (
                "MITRE ATLAS",
                "Apache License, Version 2.0",
                "Copyright 2021-2026 MITRE",
                "VulnoraIQ-specific source code",
            ):
                if required_text not in notice:
                    errors.append(f"Third-party notices missing required attribution text: {required_text}")
        if EXPECTED_MITRE_ATLAS_DOC.exists():
            matrix = EXPECTED_MITRE_ATLAS_DOC.read_text(encoding="utf-8")
            if "THIRD_PARTY_NOTICES.md" not in matrix:
                errors.append("MITRE ATLAS matrix must link to THIRD_PARTY_NOTICES.md")
        if not Path("scripts/generate_mitre_atlas_matrix.py").exists():
            errors.append("Missing MITRE ATLAS matrix generator")
        if not EXPECTED_FUNCTIONAL_RUNNER.exists():
            errors.append(f"Missing functional acceptance runner: {EXPECTED_FUNCTIONAL_RUNNER}")
        if not EXPECTED_PRODUCTION_READINESS_RUNNER.exists():
            errors.append(f"Missing production-testing readiness runner: {EXPECTED_PRODUCTION_READINESS_RUNNER}")
        if not EXPECTED_OWASP_ATLAS_MAPPING_RUNNER.exists():
            errors.append(f"Missing OWASP ATLAS mapping validator: {EXPECTED_OWASP_ATLAS_MAPPING_RUNNER}")
        else:
            mapping_result = validate_default_configs()
            if mapping_result["status"] != "pass":
                for error in mapping_result["errors"]:
                    errors.append(f"OWASP ATLAS mapping validation failed: {error}")
        if not EXPECTED_GENAI_READINESS_RUNNER.exists():
            errors.append(f"Missing GenAI readiness validator: {EXPECTED_GENAI_READINESS_RUNNER}")
        if not EXPECTED_GENAI_MANIFEST.exists():
            errors.append(f"Missing GenAI readiness manifest: {EXPECTED_GENAI_MANIFEST}")
        if EXPECTED_GENAI_READINESS_RUNNER.exists() and EXPECTED_GENAI_MANIFEST.exists():
            genai_result = validate_genai_readiness()
            if genai_result["status"] != "pass":
                for error in genai_result["errors"]:
                    errors.append(f"GenAI readiness validation failed: {error}")
        if not EXPECTED_DASHBOARD_EXAMPLE.exists():
            errors.append(f"Missing dashboard example image: {EXPECTED_DASHBOARD_EXAMPLE}")
        else:
            image_bytes = EXPECTED_DASHBOARD_EXAMPLE.read_bytes()
            if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
                errors.append("Dashboard example image must be a PNG file")
        if not Path("examples/local_demo_targets/owasp_fixture_targets.py").exists():
            errors.append("Missing OWASP fixture target file")
        if not Path("core/evaluators.py").exists():
            errors.append("Missing deterministic evaluator suite")
        if not Path("core/genai_evaluators.py").exists():
            errors.append("Missing GenAI deterministic evaluator suite")
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
