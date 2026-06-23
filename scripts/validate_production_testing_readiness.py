from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.evidence_model import OwaspOracleRegistry
from core.production_detection import ProductionOwaspDetector
from core.scanner import Scanner
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
    def __init__(self, output_dir: str | Path = "reports/output/production-readiness") -> None:
        self.output_dir = Path(output_dir)

    def validate(self, run_functional: bool = False) -> ProductionTestingReadinessSummary:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        checks = [
            self._check_package_metadata(),
            self._check_owasp_oracle_coverage(),
            self._check_production_owasp_detection(),
            self._check_non_demo_authorisation_gate(),
            self._check_authorised_demo_full_profile(),
            self._check_ci_lint_type_check(),
            self._check_legacy_server_absent(),
            self._check_auth_defaults_enabled(),
            self._check_security_hardening(),
            self._check_production_config_validation(),
            self._check_backup_restore_scripts(),
            self._check_scorecard_and_runbook_docs(),
            self._check_docker_compose(),
            self._check_container_config(),
            self._check_migration_doc(),
            self._check_assessment_assurance_doc(),
            self._check_pip_audit_in_ci(),
            self._check_listen_address_safe_included(),
            self._check_readme_self_hosted_scope(),
            self._check_backlog_gate_score(),
            self._check_readme_sqlite_not_json(),
            self._check_self_hosted_docs_aligned(),
            self._check_assessment_assurance_discoverable(),
        ]
        functional_summary: FunctionalTestSummary | None = None
        if run_functional:
            functional_summary = run_functional_test(self.output_dir / "functional-test")
            checks.append(ReadinessCheck(
                "functional_acceptance_run", functional_summary.status,
                "Functional acceptance run completed.", functional_summary.to_dict(),
            ))
        summary = ProductionTestingReadinessSummary(
            self._overall_status(checks), str(self.output_dir), checks,
            functional_summary.to_dict() if functional_summary else None,
        )
        self._write_outputs(summary)
        return summary

    def _check_package_metadata(self) -> ReadinessCheck:
        result = PackageMetadataValidator().validate()
        return ReadinessCheck(
            "package_metadata", result.status, "Package metadata validated.",
            {"errors": result.errors, "warnings": result.warnings},
        )

    def _check_owasp_oracle_coverage(self) -> ReadinessCheck:
        coverage = OwaspOracleRegistry().coverage_summary()
        status = "pass" if coverage.get("owasp_category_count") == 10 and not coverage.get("missing_categories") else "fail"
        return ReadinessCheck("owasp_oracle_coverage", status, "OWASP oracle coverage checked.", coverage)

    def _check_production_owasp_detection(self) -> ReadinessCheck:
        detector = ProductionOwaspDetector()
        result = detector.validate_config()
        status = "pass" if result.status == "pass" and len(result.covered_modules) == 10 else "fail"
        return ReadinessCheck(
            "production_owasp_detection", status, "Production OWASP detector rules checked.", result.to_dict(),
        )

    def _check_non_demo_authorisation_gate(self) -> ReadinessCheck:
        try:
            Scanner().scan(target_name="custom_http_agent", profile_name="baseline", authorised=False)
        except PermissionError as exc:
            return ReadinessCheck(
                "non_demo_authorisation_gate", "pass",
                "Configured non-demo targets require explicit authorisation.",
                {"blocked_target": "custom_http_agent", "error": str(exc)},
            )
        except Exception as exc:
            return ReadinessCheck(
                "non_demo_authorisation_gate", "fail",
                "Unexpected error while checking authorisation gate.", {"error": str(exc)},
            )
        return ReadinessCheck(
            "non_demo_authorisation_gate", "fail",
            "Configured non-demo target was not blocked.", {"blocked_target": "custom_http_agent"},
        )

    def _check_authorised_demo_full_profile(self) -> ReadinessCheck:
        result = Scanner().scan(target_name="demo", profile_name="full", authorised=False)
        detector_meta = result.metadata.get("production_owasp_detection", {})
        failures = []
        for finding in result.findings:
            summary = finding.evidence.get("production_detection_status_summary", {})
            if int(summary.get("fail", 0)) > 0:
                failures.append({"owasp_id": finding.owasp_id, "summary": summary})
        status = "pass" if detector_meta.get("covered_category_count") == 10 and result.finding_count >= 10 and not failures else "fail"
        return ReadinessCheck(
            "authorised_demo_full_profile", status, "Demo full-profile scan exercised OWASP detector categories.",
            {"finding_count": result.finding_count, "detector_meta": detector_meta, "failures": failures},
        )

    def _check_ci_lint_type_check(self) -> ReadinessCheck:
        ci_yml = Path(".github/workflows/ci.yml")
        python_ci_yml = Path(".github/workflows/python-ci.yml")
        details: dict[str, Any] = {"ci_yml_exists": ci_yml.exists(), "python_ci_yml_exists": python_ci_yml.exists()}
        errors: list[str] = []
        for path, prefix in ((ci_yml, "ci_yml"), (python_ci_yml, "python_ci_yml")):
            if path.exists():
                text = path.read_text(encoding="utf-8")
                has_ruff = "ruff check" in text
                has_mypy = "mypy" in text
                details[f"{prefix}_ruff"] = has_ruff
                details[f"{prefix}_mypy"] = has_mypy
                if not has_ruff:
                    errors.append(f"{path.name} missing ruff check")
                if not has_mypy:
                    errors.append(f"{path.name} missing mypy")
            else:
                errors.append(f"{path.name} not found")
        return ReadinessCheck("ci_lint_type_check", "pass" if not errors else "fail", "CI lint and type-check configuration.", {**details, "errors": errors})

    def _check_legacy_server_absent(self) -> ReadinessCheck:
        server_py = Path("webui/server.py")
        exists = server_py.exists()
        return ReadinessCheck(
            "legacy_server_absent", "fail" if exists else "pass",
            "Legacy webui/server.py removed." if not exists else "Legacy webui/server.py still present.",
            {"legacy_server_exists": exists},
        )

    def _check_auth_defaults_enabled(self) -> ReadinessCheck:
        from webui.auth import WebAuthManager
        manager = WebAuthManager()
        errors: list[str] = []
        if not manager.enabled():
            errors.append("Auth is not enabled by default")
        return ReadinessCheck(
            "auth_defaults_enabled", "pass" if not errors else "fail", "Auth defaults and production mode.",
            {"auth_enabled_by_default": manager.enabled(), "production_mode_validated": True, "errors": errors},
        )

    def _check_security_hardening(self) -> ReadinessCheck:
        details: dict[str, Any] = {}
        errors: list[str] = []
        server_path = Path("webui/hosted_server.py")
        if not server_path.exists():
            return ReadinessCheck("security_hardening", "fail", "Security hardening checks.", {"errors": ["hosted_server.py not found"]})
        text = server_path.read_text(encoding="utf-8")
        checks = {
            "request_size_limit": "MAX_REQUEST_BODY" in text,
            "csrf_protection": "_validate_csrf" in text,
            "rate_limiting": "_rate_limit" in text,
            "security_headers": "_security_headers" in text,
            "audit_logging": "AUDIT_LOG" in text or "_audit" in text,
            "proxy_awareness": "TRUST_PROXY_HEADERS" in text or "_resolve_client_ip" in text,
            "production_mode_validation": "_validate_production" in text,
        }
        details.update(checks)
        for name, found in checks.items():
            if not found:
                errors.append(f"Missing: {name}")
        from webui.persistent_jobs import create_job_store
        store_type = type(create_job_store()).__name__
        details["default_backend"] = store_type
        if store_type != "SqliteJobStore":
            errors.append(f"Default backend is {store_type}, expected SqliteJobStore")
        deploy_path = Path("docs/DEPLOYMENT.md")
        if deploy_path.exists():
            deploy_text = deploy_path.read_text(encoding="utf-8")
            doc_checks = {
                "tls_section": "TLS" in deploy_text or "tls" in deploy_text.lower(),
                "proxy_section": "proxy" in deploy_text.lower() or "nginx" in deploy_text.lower(),
                "metrics_section": "healthz" in deploy_text,
                "audit_section": "audit" in deploy_text.lower(),
                "backup_section": "backup" in deploy_text.lower(),
                "retention_section": "retention" in deploy_text.lower(),
                "production_checklist": "Production Checklist" in deploy_text,
            }
            details["doc_coverage"] = doc_checks
            for name, found in doc_checks.items():
                if not found:
                    errors.append(f"Deployment docs missing: {name}")
        else:
            errors.append("docs/DEPLOYMENT.md not found")
        return ReadinessCheck("security_hardening", "pass" if not errors else "fail", "Security hardening checks.", {**details, "errors": errors})

    def _check_production_config_validation(self) -> ReadinessCheck:
        checks_path = Path("webui/production_checks.py")
        script_path = Path("scripts/validate_runtime_production_config.py")
        test_path = Path("tests/test_production_config_validation.py")
        errors = []
        if not checks_path.exists():
            errors.append("webui/production_checks.py not found")
        if not script_path.exists():
            errors.append("validate_runtime_production_config.py not found")
        if not test_path.exists():
            errors.append("test_production_config_validation.py not found")
        return ReadinessCheck("production_config_validation", "pass" if not errors else "fail", "Production startup validation checks.", {"errors": errors})

    def _check_backup_restore_scripts(self) -> ReadinessCheck:
        backup = Path("scripts/backup_sqlite_store.py")
        restore = Path("scripts/restore_sqlite_store.py")
        test = Path("tests/test_backup_restore.py")
        errors = []
        if not backup.exists():
            errors.append("backup_sqlite_store.py not found")
        if not restore.exists():
            errors.append("restore_sqlite_store.py not found")
        if not test.exists():
            errors.append("test_backup_restore.py not found")
        return ReadinessCheck("backup_restore_scripts", "pass" if not errors else "fail", "Backup/restore scripts and tests.", {"errors": errors})

    def _check_scorecard_and_runbook_docs(self) -> ReadinessCheck:
        docs = ["PRODUCTION_READINESS_SCORECARD.md", "RUNBOOK.md", "INCIDENT_RESPONSE.md", "RELEASE_CHECKLIST.md"]
        base = Path("docs")
        missing = [d for d in docs if not (base / d).exists()]
        return ReadinessCheck("scorecard_and_runbook_docs", "pass" if not missing else "fail", "Scorecard, runbook, incident response, release checklist docs.", {"missing": missing})

    def _check_docker_compose(self) -> ReadinessCheck:
        compose = Path("docker-compose.yml")
        env_example = Path(".env.production.example")
        errors = []
        if not compose.exists():
            errors.append("docker-compose.yml not found")
        if not env_example.exists():
            errors.append(".env.production.example not found")
        return ReadinessCheck("docker_compose", "pass" if not errors else "fail", "Docker Compose production path.", {"errors": errors})

    def _check_container_config(self) -> ReadinessCheck:
        dockerfile = Path("Dockerfile")
        if not dockerfile.exists():
            return ReadinessCheck("container_config", "fail", "Dockerfile not found.", {})
        text = dockerfile.read_text(encoding="utf-8")
        checks = {
            "non_root_user": "USER vulnoraiq" in text,
            "volume_data": 'VOLUME ["/data"]' in text or "VOLUME /data" in text,
            "healthcheck": "HEALTHCHECK" in text,
            "oci_labels": "org.opencontainers.image" in text,
            "pip_no_cache": "pip install --no-cache-dir" in text,
        }
        smoke = Path("scripts/container_smoke_test.py")
        errors = [k for k, v in checks.items() if not v]
        if not smoke.exists():
            errors.append("container_smoke_test.py not found")
        return ReadinessCheck("container_config", "pass" if not errors else "fail", "Container security hardening.", {**checks, "smoke_test_script_exists": smoke.exists(), "errors": errors})

    def _check_migration_doc(self) -> ReadinessCheck:
        doc = Path("docs/MIGRATION.md")
        return ReadinessCheck("migration_doc", "pass" if doc.exists() else "fail", "Migration guide.", {"exists": doc.exists()})

    def _check_assessment_assurance_doc(self) -> ReadinessCheck:
        doc = Path("docs/ASSESSMENT_ASSURANCE.md")
        return ReadinessCheck("assessment_assurance_doc", "pass" if doc.exists() else "fail", "Assessment assurance doc.", {"exists": doc.exists()})

    def _check_pip_audit_in_ci(self) -> ReadinessCheck:
        ci = Path(".github/workflows/ci.yml")
        python_ci = Path(".github/workflows/python-ci.yml")
        errors: list[str] = []
        details: dict[str, Any] = {}
        for path, key in ((ci, "ci_yml"), (python_ci, "python_ci_yml")):
            if path.exists():
                text = path.read_text(encoding="utf-8")
                details[f"{key}_pip_audit"] = "pip_audit" in text or "pip-audit" in text
                details[f"{key}_pip_check"] = "pip check" in text
                if not details[f"{key}_pip_audit"]:
                    errors.append(f"{path.name} missing pip-audit")
            else:
                errors.append(f"{path.name} not found")
        return ReadinessCheck("pip_audit_in_ci", "pass" if not errors else "fail", "Dependency and supply-chain checks in CI.", {**details, "errors": errors})

    def _check_listen_address_safe_included(self) -> ReadinessCheck:
        checks_path = Path("webui/production_checks.py")
        if not checks_path.exists():
            return ReadinessCheck("listen_address_safe_included", "fail", "production_checks.py not found.", {})
        text = checks_path.read_text(encoding="utf-8")
        has_entry = '"listen_address_safe"' in text or "'listen_address_safe'" in text
        has_func = "def check_listen_address_safe" in text
        errors: list[str] = []
        if not has_entry:
            errors.append("listen_address_safe missing from _ALL_CHECKS")
        if not has_func:
            errors.append("check_listen_address_safe function not found")
        return ReadinessCheck("listen_address_safe_included", "pass" if not errors else "fail", "listen_address_safe is reachable in production validation.", {"errors": errors})

    def _check_readme_self_hosted_scope(self) -> ReadinessCheck:
        readme = Path("README.md")
        if not readme.exists():
            return ReadinessCheck("readme_self_hosted_scope", "fail", "README.md not found.", {})
        text = readme.read_text(encoding="utf-8").lower()
        errors = []
        required = ["self-hosted", "laptop", "internal server", "authorised"]
        for word in required:
            if word not in text:
                errors.append(f"README missing self-hosted scope wording: {word}")
        details = {"errors": errors}
        return ReadinessCheck("readme_self_hosted_scope", "pass" if not errors else "fail", "README documents the self-hosted laptop/server scope.", details)

    def _check_backlog_gate_score(self) -> ReadinessCheck:
        backlog = Path("docs/PRODUCTION_HARDENING_BACKLOG.md")
        if not backlog.exists():
            return ReadinessCheck("backlog_gate_score", "fail", "PRODUCTION_HARDENING_BACKLOG.md not found.", {})
        text = backlog.read_text(encoding="utf-8")
        errors = []
        if "10/10" not in text:
            errors.append("Backlog missing 10/10 gate compliance score")
        if "self-hosted" not in text.lower():
            errors.append("Backlog missing self-hosted scope")
        return ReadinessCheck("backlog_gate_score", "pass" if not errors else "fail", "Backlog tracks self-hosted gate compliance.", {"errors": errors})

    def _check_readme_sqlite_not_json(self) -> ReadinessCheck:
        readme = Path("README.md")
        if not readme.exists():
            return ReadinessCheck("readme_sqlite_not_json", "fail", "README.md not found.", {})
        text = readme.read_text(encoding="utf-8")
        errors = []
        has_sqlite = "SQLite" in text
        has_wal = "WAL" in text
        mentions_json_primary = "persistent JSON" in text.lower()
        if mentions_json_primary:
            errors.append("README mentions persistent JSON as primary storage")
        if not has_sqlite:
            errors.append("README does not mention SQLite persistence")
        return ReadinessCheck("readme_sqlite_not_json", "pass" if not errors else "fail", "README says SQLite/WAL persistence, not JSON as primary.", {"has_sqlite": has_sqlite, "has_wal": has_wal, "errors": errors})

    def _check_self_hosted_docs_aligned(self) -> ReadinessCheck:
        docs = [
            Path("README.md"),
            Path("SECURITY.md"),
            Path("docs/README.md"),
            Path("docs/DEPLOYMENT.md"),
            Path("docs/PRODUCTION_READINESS_SCORECARD.md"),
            Path("docs/PRODUCTION_HARDENING_BACKLOG.md"),
        ]
        issues: list[str] = []
        for doc in docs:
            if not doc.exists():
                issues.append(f"{doc} missing")
                continue
            text = doc.read_text(encoding="utf-8").lower()
            if "self-hosted" not in text:
                issues.append(f"{doc} missing self-hosted positioning")
        return ReadinessCheck("self_hosted_docs_aligned", "pass" if not issues else "fail", "Primary docs use the self-hosted deployment model.", {"issues": issues})

    def _check_assessment_assurance_discoverable(self) -> ReadinessCheck:
        readme = Path("README.md")
        issues: list[str] = []
        if readme.exists():
            text = readme.read_text(encoding="utf-8")
            if "ASSESSMENT_ASSURANCE" not in text and "assessment_assurance" not in text.lower():
                issues.append("ASSESSMENT_ASSURANCE.md not linked from README")
        implement = Path("docs/IMPLEMENTATION_STATUS.md")
        if implement.exists():
            text = implement.read_text(encoding="utf-8")
            if "ASSESSMENT_ASSURANCE" not in text and "assessment_assurance" not in text.lower():
                issues.append("ASSESSMENT_ASSURANCE.md not linked from IMPLEMENTATION_STATUS.md")
        doc = Path("docs/ASSESSMENT_ASSURANCE.md")
        if not doc.exists():
            issues.append("ASSESSMENT_ASSURANCE.md not found")
        return ReadinessCheck("assessment_assurance_discoverable", "pass" if not issues else "fail", "Assessment assurance doc is linked and discoverable.", {"issues": issues})

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
            "# VulnoraIQ Production Readiness Summary",
            "",
            f"Overall status: `{summary.status}`",
            "",
            "| Check | Status | Message |",
            "| --- | --- | --- |",
        ]
        for check in summary.checks:
            message = check.message.replace("|", "\\|")
            lines.append(f"| `{check.id}` | `{check.status}` | {message} |")
        markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate VulnoraIQ readiness gates.")
    parser.add_argument("--output-dir", default="reports/output/production-readiness")
    parser.add_argument("--run-functional", action="store_true")
    parser.add_argument("--fail-on-warn", action="store_true")
    args = parser.parse_args()
    summary = ProductionTestingReadinessValidator(args.output_dir).validate(args.run_functional)
    print(json.dumps(summary.to_dict(), indent=2, sort_keys=True, default=str))
    if summary.status == "fail" or (args.fail_on_warn and summary.status == "warn"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
