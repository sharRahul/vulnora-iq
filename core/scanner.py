from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from core.evidence_model import OwaspOracleRegistry
from core.policy_engine import PolicyEngine
from core.production_detection import ProductionOwaspDetector
from core.test_runner import TestRunner
from core.types import ScanContext, ScanResult, TargetClient
from integrations.adapters import ChatCompletionsTargetClient, OllamaGenerateTargetClient, WebhookJsonTargetClient
from integrations.base import DemoEchoClient, HttpJsonTargetClient


class Scanner:
    """High-level assessment entry point."""

    def __init__(self, config_dir: str | Path = "config") -> None:
        self.config_dir = Path(config_dir)
        self.runner = TestRunner()
        self.policy_engine = PolicyEngine()
        self.oracle_registry = OwaspOracleRegistry()
        self.production_detector = ProductionOwaspDetector()

    def scan(
        self,
        target_name: str = "demo",
        profile_name: str = "baseline",
        target: TargetClient | None = None,
        authorised: bool = False,
    ) -> ScanResult:
        config = self._load_config()
        profile = config["attack_profiles"].get("profiles", {}).get(profile_name)
        if not profile:
            raise ValueError(f"Unknown assessment profile: {profile_name}")

        self._require_authorisation(target_name=target_name, target=target, authorised=authorised, config=config)
        target_client = target or self._default_target(target_name, config=config)
        context = ScanContext(
            target_name=target_name,
            profile_name=profile_name,
            target=target_client,
            config=config,
        )
        findings = self.runner.run_modules(profile["modules"], context)
        result = ScanResult(
            target_name=target_name,
            profile_name=profile_name,
            findings=findings,
            started_at=context.started_at,
            completed_at=datetime.now(timezone.utc),
            metadata={
                "framework": config.get("default", {}).get("framework", {}),
                "profile_description": profile.get("description", ""),
                "authorised": authorised or target_name == "demo",
                "owasp_oracle_coverage": self.oracle_registry.coverage_summary(),
                "production_owasp_detection": self.production_detector.coverage_summary(),
                "production_validation_status": "authorised_production_assessment_testing_ready",
                "assessment_scope_warning": (
                    "Run only against systems you own or are explicitly authorised to test; "
                    "findings still require tester review and business-context validation."
                ),
            },
        )
        result.policy_results = self.policy_engine.evaluate(result, config)
        return result

    def _require_authorisation(
        self,
        target_name: str,
        target: TargetClient | None,
        authorised: bool,
        config: dict[str, Any],
    ) -> None:
        policy = config.get("policies", {}).get("policies", {}).get("authorised_testing_required", {})
        policy_enabled = bool(policy.get("enabled", True))
        is_demo = target_name == "demo" and target is None
        if policy_enabled and not is_demo and not authorised:
            raise PermissionError(
                "Configured targets require explicit authorisation. Re-run with the CLI authorisation flag "
                "only for systems you own or are permitted to assess."
            )

    def _default_target(self, target_name: str, config: dict[str, Any]) -> TargetClient:
        target_config = config.get("targets", {}).get("targets", {}).get(target_name)
        if target_name == "demo":
            return DemoEchoClient()
        if not target_config:
            raise ValueError(f"Unknown target: {target_name}")

        target_type = target_config.get("type")
        endpoint = target_config.get("endpoint")
        if target_type in {"custom_agent", "custom_http_agent", "http", "http_json"}:
            self._reject_placeholder(target_name, endpoint)
            timeout = int(config.get("default", {}).get("execution", {}).get("request_timeout_seconds", 30))
            return HttpJsonTargetClient(
                name=target_name,
                endpoint=str(endpoint),
                token_env_var=target_config.get("token_env_var"),
                timeout_seconds=timeout,
            )
        if target_type in {"chat_completions", "chat_completions_compatible"}:
            self._reject_placeholder(target_name, endpoint)
            return ChatCompletionsTargetClient(
                name=target_name,
                endpoint=str(endpoint),
                model=str(target_config.get("model", "local-model")),
                token_env_var=target_config.get("token_env_var"),
                timeout_seconds=int(config.get("default", {}).get("execution", {}).get("request_timeout_seconds", 30)),
            )
        if target_type == "ollama_generate":
            self._reject_placeholder(target_name, endpoint)
            return OllamaGenerateTargetClient(
                name=target_name,
                endpoint=str(endpoint),
                model=str(target_config.get("model", "llama3")),
                timeout_seconds=int(config.get("default", {}).get("execution", {}).get("request_timeout_seconds", 30)),
            )
        if target_type == "webhook_json":
            self._reject_placeholder(target_name, endpoint)
            return WebhookJsonTargetClient(
                name=target_name,
                endpoint=str(endpoint),
                token_env_var=target_config.get("token_env_var"),
                timeout_seconds=int(config.get("default", {}).get("execution", {}).get("request_timeout_seconds", 30)),
            )

        raise ValueError(f"Unsupported target type for '{target_name}': {target_type}")

    @staticmethod
    def _reject_placeholder(target_name: str, endpoint: Any) -> None:
        if not endpoint or "example.invalid" in str(endpoint):
            raise ValueError(f"Target '{target_name}' is a placeholder. Configure a real authorised endpoint before assessment.")

    def _load_config(self) -> dict[str, Any]:
        def load_yaml(name: str) -> dict[str, Any]:
            path = self.config_dir / name
            with path.open("r", encoding="utf-8") as handle:
                return yaml.safe_load(handle) or {}

        return {
            "default": load_yaml("default.yaml"),
            "targets": load_yaml("targets.yaml"),
            "attack_profiles": load_yaml("attack_profiles.yaml"),
            "policies": load_yaml("policies.yaml"),
        }
