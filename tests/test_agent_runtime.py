from __future__ import annotations

from pathlib import Path

import yaml

from core.scanner import Scanner
from webui.agent_runtime import AgentRuntimeManager, find_docker_cli


def test_agent_runtime_templates_are_available() -> None:
    manager = AgentRuntimeManager(template_path=Path("config/agent_runtimes.yaml"))
    templates = manager.templates()

    assert "http_llm_agent" in templates
    assert templates["http_llm_agent"]["target_type"] == "http_json"
    assert templates["http_llm_agent"]["endpoint_path"] == "/agent"
    assert templates["http_llm_agent"]["build_context"] == "docker/agents/http-llm-agent"


def test_docker_cli_override_is_detected(tmp_path, monkeypatch) -> None:
    docker_cli = tmp_path / "docker"
    docker_cli.write_text("#!/bin/sh\necho Docker version test\n", encoding="utf-8")
    monkeypatch.setenv("VULNORAIQ_DOCKER_CLI", str(docker_cli))

    assert find_docker_cli() == str(docker_cli)


def test_runtime_targets_are_written_and_loaded_by_scanner(tmp_path, monkeypatch) -> None:
    runtime_targets_path = tmp_path / "runtime_targets.yaml"
    manager = AgentRuntimeManager(
        template_path=Path("config/agent_runtimes.yaml"),
        registry_path=tmp_path / "agent-runtimes.json",
        runtime_targets_path=runtime_targets_path,
    )
    manager._write_runtime_targets([
        {
            "status": "running",
            "target_name": "agent_test123",
            "target_type": "http_json",
            "name": "Test Docker Agent",
            "endpoint": "http://127.0.0.1:18080/agent",
        }
    ])

    raw_targets = yaml.safe_load(runtime_targets_path.read_text(encoding="utf-8"))
    assert raw_targets["targets"]["agent_test123"]["endpoint"] == "http://127.0.0.1:18080/agent"

    monkeypatch.setenv("VULNORAIQ_RUNTIME_TARGETS_PATH", str(runtime_targets_path))
    config = Scanner()._load_config()

    assert "agent_test123" in config["targets"]["targets"]
    assert config["targets"]["targets"]["agent_test123"]["type"] == "http_json"
