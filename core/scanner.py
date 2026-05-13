from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from core.test_runner import TestRunner
from core.types import ScanContext, ScanResult, TargetClient
from integrations.base import DemoEchoClient


class Scanner:
    """High-level scan entry point."""

    def __init__(self, config_dir: str | Path = "config") -> None:
        self.config_dir = Path(config_dir)
        self.runner = TestRunner()

    def scan(
        self,
        target_name: str = "demo",
        profile_name: str = "baseline",
        target: TargetClient | None = None,
    ) -> ScanResult:
        config = self._load_config()
        profile = config["attack_profiles"].get("profiles", {}).get(profile_name)
        if not profile:
            raise ValueError(f"Unknown attack profile: {profile_name}")

        target_client = target or self._default_target(target_name)
        context = ScanContext(
            target_name=target_name,
            profile_name=profile_name,
            target=target_client,
            config=config,
        )
        findings = self.runner.run_modules(profile["modules"], context)
        return ScanResult(
            target_name=target_name,
            profile_name=profile_name,
            findings=findings,
            started_at=context.started_at,
            completed_at=datetime.now(timezone.utc),
        )

    def _default_target(self, target_name: str) -> TargetClient:
        if target_name == "demo":
            return DemoEchoClient()
        raise ValueError(
            f"No target client supplied for '{target_name}'. Provide an integration adapter before scanning non-demo targets."
        )

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
