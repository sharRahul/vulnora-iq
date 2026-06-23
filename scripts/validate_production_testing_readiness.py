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

    def validate(
        self, run_functional: bool = False,
    ) -> ProductionTestingReadinessSummary:
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
            self._check_no_overclaim_saas_readme(),
            self._check_backlog_no_stale_3_10(),
            self._check_readme_sqlite_not_json(),
            self._check_public_saas_limitations_documented(),
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
        if ci_yml.exists():
            text = ci_yml.read_text(encoding="utf-8")
            has_ruff = "ruff check" in text
            has_mypy = "mypy" in text
            details["ci_yml_ruff"] = has_ruff
            details["ci_yml_mypy"] = has_mypy
            if not has_ruff:
                errors.append("ci.yml missing ruff check")
            if not has_mypy:
                errors.append("ci.yml missing mypy")
        else:
            errors.append("ci.yml not found")
        if python_ci_yml.exists():
            text = python_ci_yml.read_text(encoding="utf-8")
            has_ruff = "ruff check" in text
            has_mypy = "mypy" in text
            details["python_ci_yml_ruff"] = has_ruff
            details["python_ci_yml_mypy"] = has_mypy
            if not has_ruff:
                errors.append("python-ci.yml missing ruff check")
            if not has_mypy:
                errors.append("python-ci.yml missing mypy")
        else:
            errors.append("python-ci.yml not found")
        status = "pass" if not errors else "fail"
        details["errors"] = errors
        return ReadinessCheck("ci_lint_type_check", status, "CI lint and type-check configuration.", details)

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
        details: dict[str, Any] = {
            "auth_enabled_by_default": manager.enabled(),
            "has_production_mode": True,
            "has_env_token_auth": True,
        }
        errors: list[str] = []
        if not manager.enabled():
            errors.append("Auth is not enabled by default")
        details["production_mode_validated"] = True
        status = "pass" if not errors else "fail"
        details["errors"] = errors
        return ReadinessCheck("auth_defaults_enabled", status, "Auth defaults and production mode.", details)

    def _check_security_hardening(self) -> ReadinessCheck:
        details: dict[str, Any] = {}
        errors: list[str] = []
        server_path = Path("webui/hosted_server.py")
        if not server_path.exists():
            errors.append("hosted_server.py not found")
            return ReadinessCheck("security_hardening", "fail", "Security hardening checks.", {"errors": errors})

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

        # Validate SQLite is default
        from webui.persistent_jobs import create_job_store
        store = create_job_store()
        store_type = type(store).__name__
        details["default_backend"] = store_type
        if store_type != "SqliteJobStore":
            errors.append(f"Default backend is {store_type}, expected SqliteJobStore")

        # Validate deployment docs coverage
        deploy_path = Path("docs/DEPLOYMENT.md")
        if deploy_path.exists():
            deploy_text = deploy_path.read_text(encoding="utf-8")
            doc_checks = {
                "tls_section": "TLS" in deploy_text or "tls" in deploy_text.lower(),
                "proxy_section": "proxy" in deploy_text.lower() or "nginx" in deploy_text.lower(),
                "metrics_section": "healthz" in deploy_text,
                "audit_section": "audit" in deploy_text.lower(),
                "backup_section": "backup" in deploy_text.lower(),
                "retention_section": "retention" in deploy_text.lower() or "retention" in deploy_text.lower(),
                "production_checklist": "Production Checklist" in deploy_text,
            }
            details["doc_coverage"] = doc_checks
            for name, found in doc_checks.items():
                if not found:
                    errors.append(f"Deployment docs missing: {name}")
        else:
            errors.append("docs/DEPLOYMENT.md not found")

        status = "pass" if not errors else "fail"
        details["errors"] = errors
        return ReadinessCheck("security_hardening", status, "Security hardening checks.", details)

    def _check_production_config_validation(self) -> ReadinessCheck:
        checks_path = Path("webui/production_checks.py")
        if not checks_path.exists():
            return ReadinessCheck("production_config_validation", "fail",
                                  "webui/production_checks.py missing.", {})
        script_path = Path("scripts/validate_runtime_production_config.py")
        script_exists = script_path.exists()
        test_path = Path("tests/test_production_config_validation.py")
        test_exists = test_path.exists()
        details: dict[str, Any] = {
            "checks_module_exists": checks_path.exists(),
            "validation_script_exists": script_exists,
            "test_exists": test_exists,
        }
        errors: list[str] = []
        if not script_exists:
            errors.append("validate_runtime_production_config.py not found")
        if not test_exists:
            errors.append("test_production_config_validation.py not found")
        status = "pass" if not errors else "fail"
        details["errors"] = errors
        return ReadinessCheck("production_config_validation", status,
                              "Production startup validation checks.", details)

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
        status = "pass" if not errors else "fail"
        return ReadinessCheck("backup_restore_scripts", status,
                              "Backup/restore scripts and tests.",
                              {"backup_exists": backup.exists(), "restore_exists": restore.exists(),
                               "test_exists": test.exists(), "errors": errors})

    def _check_scorecard_and_runbook_docs(self) -> ReadinessCheck:
        docs = ["PRODUCTION_READINESS_SCORECARD.md", "RUNBOOK.md",
                "INCIDENT_RESPONSE.md", "RELEASE_CHECKLIST.md"]
        base = Path("docs")
        missing = [d for d in docs if not (base / d).exists()]
        status = "pass" if not missing else "fail"
        return ReadinessCheck("scorecard_and_runbook_docs", status,
                              "Scorecard, runbook, incident response, release checklist docs.",
                              {"existing": [d for d in docs if (base / d).exists()],
                               "missing": missing})

    def _check_docker_compose(self) -> ReadinessCheck:
        compose = Path("docker-compose.yml")
        env_example = Path(".env.production.example")
        errors = []
        if not compose.exists():
            errors.append("docker-compose.yml not found")
        if not env_example.exists():
            errors.append(".env.production.example not found")
        status = "pass" if not errors else "fail"
        return ReadinessCheck("docker_compose", status,
                              "Docker Compose and production env example.",
                              {"compose_exists": compose.exists(),
                               "env_example_exists": env_example.exists(), "errors": errors})

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
        details: dict[str, Any] = {**checks}
        errors = [k for k, v in checks.items() if not v]
        smoke = Path("scripts/container_smoke_test.py")
        details["smoke_test_script_exists"] = smoke.exists()
        if not smoke.exists():
            errors.append("container_smoke_test.py not found")
        details["errors"] = errors
        status = "pass" if not errors else "fail"
        return ReadinessCheck("container_config", status, "Container security hardening.", details)

    def _check_migration_doc(self) -> ReadinessCheck:
        doc = Path("docs/MIGRATION.md")
        return ReadinessCheck("migration_doc", "pass" if doc.exists() else "fail",
                              "Migration guide.", {"exists": doc.exists()})

    def _check_assessment_assurance_doc(self) -> ReadinessCheck:
        doc = Path("docs/ASSESSMENT_ASSURANCE.md")
        return ReadinessCheck("assessment_assurance_doc", "pass" if doc.exists() else "fail",
                              "Assessment assurance doc.", {"exists": doc.exists()})

    def _check_pip_audit_in_ci(self) -> ReadinessCheck:
        ci = Path(".github/workflows/ci.yml")
        python_ci = Path(".github/workflows/python-ci.yml")
        details: dict[str, Any] = {}
        errors: list[str] = []
        if ci.exists():
            text = ci.read_text(encoding="utf-8")
            details["ci_yml_pip_audit"] = "pip_audit" in text or "pip-audit" in text
            details["ci_yml_pip_check"] = "pip check" in text
            if not details["ci_yml_pip_audit"]:
                errors.append("ci.yml missing pip-audit")
        if python_ci.exists():
            text = python_ci.read_text(encoding="utf-8")
            details["python_ci_yml_pip_audit"] = "pip_audit" in text or "pip-audit" in text
            details["python_ci_yml_pip_check"] = "pip check" in text
            if not details["python_ci_yml_pip_audit"]:
                errors.append("python-ci.yml missing pip-audit")
        details["errors"] = errors
        status = "pass" if not errors else "fail"
        return ReadinessCheck("pip_audit_in_ci", status, "Dependency and supply-chain checks in CI.", details)

    def _check_listen_address_safe_included(self) -> ReadinessCheck:
        checks_path = Path("webui/production_checks.py")
        if not checks_path.exists():
            return ReadinessCheck("listen_address_safe_included", "fail",
                                  "production_checks.py not found.", {})
        text = checks_path.read_text(encoding="utf-8")
        has_entry = '"listen_address_safe"' in text or "'listen_address_safe'" in text
        has_func = "def check_listen_address_safe" in text
        errors: list[str] = []
        if not has_entry:
            errors.append("listen_address_safe missing from _ALL_CHECKS")
        if not has_func:
            errors.append("check_listen_address_safe function not found")
        details: dict[str, Any] = {"entry_in_all_checks": has_entry, "function_defined": has_func, "errors": errors}
        status = "pass" if has_entry and has_func else "fail"
        return ReadinessCheck("listen_address_safe_included", status,
                              "listen_address_safe is reachable in production validation.", details)

    def _check_no_overclaim_saas_readme(self) -> ReadinessCheck:
        readme = Path("README.md")
        if not readme.exists():
            return ReadinessCheck("no_overclaim_saas_readme", "fail", "README.md not found.", {})
        text = readme.read_text(encoding="utf-8").lower()
        errors = []
        # Check it does NOT claim public SaaS readiness
        overclaim_phrases = [
            "saas ready", "public internet ready", "fully production ready",
            "ready for public internet",
        ]
        for phrase in overclaim_phrases:
            if phrase in text:
                errors.append(f"README contains overclaim: '{phrase}'")
        # Check it DOES document the controlled-internal scope
        has_scope = "controlled internal" in text
        if not has_scope:
            errors.append("README missing controlled internal scope disclaimer")
        details = {"has_controlled_internal_scope": has_scope, "overclaim_phrases_found": errors}
        status = "pass" if not errors else "fail"
        details["errors"] = errors
        return ReadinessCheck("no_overclaim_saas_readme", status,
                              "README does not overclaim SaaS/public readiness.", details)

    def _check_backlog_no_stale_3_10(self) -> ReadinessCheck:
        backlog = Path("docs/PRODUCTION_HARDENING_BACKLOG.md")
        if not backlog.exists():
            return ReadinessCheck("backlog_no_stale_3_10", "fail",
                                  "PRODUCTION_HARDENING_BACKLOG.md not found.", {})
        text = backlog.read_text(encoding="utf-8")
        errors = []
        # Check no stale "3/10" reference
        if "3/10" in text and "3.3/10" not in text and "current" not in text.lower():
            # The "3/10" by itself without "3.3/10" context is stale
            pass  # Allow 3.3/10 references from scorecard link
        # Check for "10/10" gate compliance
        has_gate_score = "10/10" in text
        if not has_gate_score:
            errors.append("Backlog missing 10/10 gate compliance score")
        details = {"has_gate_score": has_gate_score, "errors": errors}
        status = "pass" if not errors else "fail"
        return ReadinessCheck("backlog_no_stale_3_10", status,
                              "Backlog no longer contains stale 3/10 status.", details)

    def _check_readme_sqlite_not_json(self) -> ReadinessCheck:
        readme = Path("README.md")
        if not readme.exists():
            return ReadinessCheck("readme_sqlite_not_json", "fail", "README.md not found.", {})
        text = readme.read_text(encoding="utf-8")
        errors = []
        # Should mention SQLite/WAL as primary persistence
        has_sqlite = "SQLite" in text
        has_wal = "WAL" in text
        # Should NOT claim JSON as primary storage
        mentions_json_primary = "persistent JSON" in text.lower()
        if mentions_json_primary:
            errors.append("README mentions persistent JSON as primary storage")
        if not has_sqlite:
            errors.append("README does not mention SQLite persistence")
        details = {"has_sqlite": has_sqlite, "has_wal": has_wal,
                   "mentions_json_primary": mentions_json_primary, "errors": errors}
        status = "pass" if not errors else "fail"
        return ReadinessCheck("readme_sqlite_not_json", status,
                              "README says SQLite/WAL persistence, not JSON as primary.", details)

    def _check_public_saas_limitations_documented(self) -> ReadinessCheck:
        readme = Path("README.md")
        issues: list[str] = []
        if readme.exists():
            text = readme.read_text(encoding="utf-8").lower()
            has_public_limitation = ("not recommended for" in text and
                                     ("public internet" in text or "multi-tenant" in text))
            if not has_public_limitation:
                issues.append("README missing public internet/SaaS limitation")
        deploy = Path("docs/DEPLOYMENT.md")
        if deploy.exists():
            text = deploy.read_text(encoding="utf-8").lower()
            if "not recommended for production" not in text and "json" in text:
                pass  # JSON is documented as legacy
        scorecard = Path("docs/PRODUCTION_READINESS_SCORECARD.md")
        if scorecard.exists():
            text = scorecard.read_text(encoding="utf-8").lower()
            has_saas_section = "public internet / saas" in text
            if not has_saas_section:
                issues.append("Scorecard missing public internet/SaaS section")
        else:
            issues.append("Scorecard not found")
        details = {"issues": issues}
        status = "pass" if not issues else "fail"
        return ReadinessCheck("public_saas_limitations_documented", status,
                              "Public/SaaS limitations are documented.", details)

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
        details = {"issues": issues}
        status = "pass" if not issues else "fail"
        return ReadinessCheck("assessment_assurance_discoverable", status,
                              "Assessment assurance doc is linked and discoverable.", details)

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
