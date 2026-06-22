from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from benchmarks.fixture_validation import BenchmarkFixtureValidator
from core.evidence_model import OwaspOracleRegistry
from core.mitre_atlas import MitreAtlasMapping
from core.scanner import Scanner
from integrations.contract_validation import TargetContractValidator
from scripts.run_functional_test import FunctionalTestSummary, run_functional_test
from scripts.validate_package_metadata import PackageMetadataValidator


@dataclass(slots=True)
class ReadinessCheck:
    id: str
    status: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProductionTestingReadinessSummary:
    status: str
    output_dir: str
    checks: list[ReadinessCheck]
    functional_test: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ProductionTestingReadinessValidator:
    """Runs local readiness gates before using VulnoraIQ for testing workflows.

    This is a production-testing readiness gate, not a real-world VAPT assurance
    certification. It checks that the safe demo workflow, release metadata,
    fixtures, mappings, adapter contracts, and authorisation controls are wired
    well enough for controlled testing.
    """

    def __init__(self, output_dir: str | Path = "reports/output/production-readiness") -> None:
        self.output_dir = Path(output_dir)

    def validate(
        self,
        run_functional: bool = False,
        screenshot_path: str | Path = "docs/assets/vulnoraiq-dashboard-example.svg",
    ) -> ProductionTestingReadinessSummary:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        checks = [
            self._check_package_metadata(),
            self._check_target_contracts(),
            self._check_benchmark_fixtures(),
            self._check_mitre_atlas_mapping(),
            self._check_owasp_oracle_coverage(),
            self._check_non_demo_authorisation_gate(),
            self._check_documentation_and_ci_wiring(),
        ]
        functional_summary: FunctionalTestSummary | None = None
        if run_functional:
            functional_summary = run_functional_test(
                output_dir=self.output_dir / "functional-test",
                screenshot_path=screenshot_path,
            )
            checks.append(
                ReadinessCheck(
                    id="functional_acceptance_run",
                    status=functional_summary.status,
                    message="Safe demo/baseline functional acceptance run completed.",
                    details=functional_summary.to_dict(),
                )
            )

        status = self._overall_status(checks)
        summary = ProductionTestingReadinessSummary(
            status=status,
            output_dir=str(self.output_dir),
            checks=checks,
            functional_test=functional_summary.to_dict() if functional_summary else None,
        )
        self._write_outputs(summary)
        return summary

    def _check_package_metadata(self) -> ReadinessCheck:
        result = PackageMetadataValidator().validate()
        return ReadinessCheck(
            id="package_metadata",
            status=result.status,
            message="Package metadata, CLI entry points, notices, and release assets were validated.",
            details={"errors": result.errors, "warnings": result.warnings},
        )

    def _check_target_contracts(self) -> ReadinessCheck:
        result = TargetContractValidator().validate()
        status = "fail" if result.status == "fail" else "warn" if result.warnings else "pass"
        return ReadinessCheck(
            id="target_contracts",
            status=status,
            message="Configured target adapter contracts were checked; placeholder targets remain blocked until explicitly configured.",
            details={
                "target_count": result.target_count,
                "validated_count": result.validated_count,
                "errors": result.errors,
                "warnings": result.warnings,
            },
        )

    def _check_benchmark_fixtures(self) -> ReadinessCheck:
        result = BenchmarkFixtureValidator().validate()
        return ReadinessCheck(
            id="benchmark_fixtures",
            status=result.status,
            message="OWASP starter benchmark fixtures were validated for category coverage and required fields.",
            details={
                "fixture_count": result.fixture_count,
                "covered_modules": result.covered_modules,
                "errors": result.errors,
            },
        )

    def _check_mitre_atlas_mapping(self) -> ReadinessCheck:
        result = MitreAtlasMapping().validate()
        return ReadinessCheck(
            id="mitre_atlas_mapping",
            status=result.status,
            message="Local MITRE ATLAS mapping catalog was validated.",
            details={
                "mapping_path": result.mapping_path,
                "technique_count": result.technique_count,
                "module_mapping_count": result.module_mapping_count,
                "errors": result.errors,
                "warnings": result.warnings,
            },
        )

    def _check_owasp_oracle_coverage(self) -> ReadinessCheck:
        coverage = OwaspOracleRegistry().coverage_summary()
        missing = coverage.get("missing_categories", [])
        status = "pass" if coverage.get("owasp_category_count") == 10 and not missing else "fail"
        return ReadinessCheck(
            id="owasp_oracle_coverage",
            status=status,
            message="OWASP LLM 2025 starter oracle coverage was checked across all 10 categories.",
            details=coverage,
        )

    def _check_non_demo_authorisation_gate(self) -> ReadinessCheck:
        try:
            Scanner().scan(target_name="custom_http_agent", profile_name="baseline", authorised=False)
        except PermissionError as exc:
            return ReadinessCheck(
                id="non_demo_authorisation_gate",
                status="pass",
                message="Configured non-demo targets are blocked unless explicit authorisation is supplied.",
                details={"blocked_target": "custom_http_agent", "error": str(exc)},
            )
        except Exception as exc:  # pragma: no cover - defensive signal for unexpected wiring failure
            return ReadinessCheck(
                id="non_demo_authorisation_gate",
                status="fail",
                message="Non-demo authorisation gate raised an unexpected error before producing the expected block.",
                details={"error": str(exc)},
            )
        return ReadinessCheck(
            id="non_demo_authorisation_gate",
            status="fail",
            message="Configured non-demo target scan was not blocked without explicit authorisation.",
            details={"blocked_target": "custom_http_agent"},
        )

    def _check_documentation_and_ci_wiring(self) -> ReadinessCheck:
        errors: list[str] = []
        warnings: list[str] = []
        required_paths = [
            Path("README.md"),
            Path("docs/IMPLEMENTATION_STATUS.md"),
            Path("docs/assets/vulnoraiq-dashboard-example.svg"),
            Path(".github/workflows/ci.yml"),
        ]
        for path in required_paths:
            if not path.exists():
                errors.append(f"Missing required file: {path}")

        readme = Path("README.md").read_text(encoding="utf-8") if Path("README.md").exists() else ""
        status_doc = Path("docs/IMPLEMENTATION_STATUS.md").read_text(encoding="utf-8") if Path("docs/IMPLEMENTATION_STATUS.md").exists() else ""
        ci = Path(".github/workflows/ci.yml").read_text(encoding="utf-8") if Path(".github/workflows/ci.yml").exists() else ""
        if "not ready for real-world VAPT" not in readme:
            warnings.append("README should keep the real-world VAPT maturity warning until deeper validation exists.")
        if "production-testing readiness" not in status_doc.lower().replace("_", "-"):
            warnings.append("Implementation status should mention the production-testing readiness gate.")
        if "validate_production_testing_readiness.py" not in ci:
            errors.append("CI must run the production-testing readiness gate.")
        if "run_functional_test.py" not in ci and "--run-functional" not in ci:
            errors.append("CI must run the functional acceptance path.")

        return ReadinessCheck(
            id="documentation_and_ci_wiring",
            status="fail" if errors else "warn" if warnings else "pass",
            message="Documentation, dashboard example asset, and CI readiness wiring were checked.",
            details={"errors": errors, "warnings": warnings},
        )

    @staticmethod
    def _overall_status(checks: list[ReadinessCheck]) -> str:
        statuses = {check.status for check in checks}
        if "fail" in statuses:
            return "fail"
        if "warn" in statuses:
            return "warn"
        return "pass"

    def _write_outputs(self, summary: ProductionTestingReadinessSummary) -> None:
        json_path = self.output_dir / "production-testing-readiness-summary.json"
        markdown_path = self.output_dir / "production-testing-readiness-summary.md"
        json_path.write_text(json.dumps(summary.to_dict(), indent=2, sort_keys=True, default=str), encoding="utf-8")
        lines = [
            "# VulnoraIQ Production-Testing Readiness Summary",
            "",
            f"Overall status: `{summary.status}`",
            "",
            "> This gate confirms controlled testing readiness for the safe local workflow. It does not certify real-world VAPT accuracy.",
            "",
            "| Check | Status | Message |",
            "| --- | --- | --- |",
        ]
        for check in summary.checks:
            message = check.message.replace("|", "\\|")
            lines.append(f"| `{check.id}` | `{check.status}` | {message} |")
        markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate VulnoraIQ production-testing readiness gates.")
    parser.add_argument("--output-dir", default="reports/output/production-readiness")
    parser.add_argument("--screenshot", default="docs/assets/vulnoraiq-dashboard-example.svg")
    parser.add_argument("--run-functional", action="store_true", help="Run the safe demo/baseline functional acceptance path.")
    parser.add_argument("--fail-on-warn", action="store_true", help="Treat readiness warnings as command failures.")
    args = parser.parse_args()

    summary = ProductionTestingReadinessValidator(args.output_dir).validate(
        run_functional=args.run_functional,
        screenshot_path=args.screenshot,
    )
    print(json.dumps(summary.to_dict(), indent=2, sort_keys=True, default=str))
    if summary.status == "fail" or (args.fail_on_warn and summary.status == "warn"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
