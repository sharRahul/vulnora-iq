from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


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
        for command in ("vulnoraiq", "vulnoraiq-web", "vulnoraiq-dashboard", "vulnoraiq-diff", "vulnoraiq-package", "vulnoraiq-benchmark"):
            if command not in pyproject:
                errors.append(f"Missing CLI entry point: {command}")
        if "not ready for real-world VAPT" not in Path("README.md").read_text(encoding="utf-8"):
            warnings.append("README maturity warning was not found")
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
