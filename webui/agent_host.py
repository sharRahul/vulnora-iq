from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import Any

import yaml

LOGGER = logging.getLogger("vulnoraiq.webui.agent_host")
CONFIG_ROOT = Path(os.getenv("VULNORAIQ_CONFIG_DIR", "config"))
TEMPLATES_PATH = CONFIG_ROOT / "agent_templates.yaml"
AGENT_LABEL = "vulnoraiq.agent"
AGENT_NETWORK = "vulnoraiq_vulnoraiq-lab"
DOCKER_TIMEOUT = int(os.getenv("VULNORAIQ_DOCKER_COMMAND_TIMEOUT", "600"))


def _run_docker(args: list[str]) -> tuple[str, str]:
    result = subprocess.run(["docker"] + args, capture_output=True, text=True, timeout=DOCKER_TIMEOUT)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"docker {' '.join(args)} failed")
    return result.stdout.strip(), result.stderr.strip()


def _container_name(agent_id: str) -> str:
    return f"vulnoraiq-agent-{agent_id}"


def load_templates() -> dict[str, Any]:
    if not TEMPLATES_PATH.exists():
        return {}
    data = yaml.safe_load(TEMPLATES_PATH.read_text(encoding="utf-8")) or {}
    return data.get("templates", {})


class AgentHost:
    def list_agents(self) -> list[dict[str, Any]]:
        try:
            out, _ = _run_docker(
                ["ps", "-a", "--filter", f"label={AGENT_LABEL}", "--format", "{{.ID}}\t{{.Label \"vulnoraiq.agent.id\"}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"]
            )
            if not out:
                return []
            agents = []
            for line in out.split("\n"):
                parts = line.strip().split("\t")
                if len(parts) >= 4:
                    agents.append({
                        "container_id": parts[0],
                        "id": parts[1],
                        "image": parts[2],
                        "status": parts[3],
                        "ports": parts[4] if len(parts) > 4 else "",
                    })
            return agents
        except RuntimeError as exc:
            LOGGER.warning("Failed to list agents: %s", exc)
            return []

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        for agent in self.list_agents():
            if agent["id"] == agent_id:
                return agent
        return None

    def deploy(self, agent_id: str, template_key: str | None = None, image: str | None = None, env: dict[str, str] | None = None) -> dict[str, Any]:
        name = _container_name(agent_id)
        existing = self.get_agent(agent_id)
        if existing:
            raise ValueError(f"Agent '{agent_id}' is already running (container {existing['container_id']})")

        templates = load_templates()
        if template_key and template_key in templates:
            tmpl = templates[template_key]
            image_name = tmpl.get("image", image or "")
            build = tmpl.get("build")
            ports = tmpl.get("ports", [])
            default_env = dict(tmpl.get("env", {}))
            if env:
                default_env.update(env)
            env = default_env
            if build:
                ctx = build.get("context", ".")
                df = build.get("dockerfile", "Dockerfile")
                LOGGER.info("Building image %s from %s", image_name, ctx)
                _run_docker(["build", "-t", image_name, "-f", df, ctx])
        else:
            if not image:
                raise ValueError("Either template_key or image must be provided")
            image_name = image
            ports = []

        cmd = ["run", "-d", "--name", name, "--label", f"{AGENT_LABEL}={agent_id}", "--label", f"vulnoraiq.agent.id={agent_id}", "--network", AGENT_NETWORK]
        for p in ports:
            cmd += ["-p", str(p)]
        if env:
            for k, v in env.items():
                if v:
                    cmd += ["-e", f"{k}={v}"]
        cmd.append(image_name)
        try:
            out, _ = _run_docker(cmd)
        except RuntimeError as exc:
            raise RuntimeError(f"Failed to deploy agent '{agent_id}': {exc}") from exc

        container_id = out.strip()
        return {"container_id": container_id, "agent_id": agent_id, "name": name, "image": image_name, "status": "deployed"}

    def stop(self, agent_id: str) -> bool:
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        _run_docker(["stop", agent["container_id"]])
        return True

    def start(self, agent_id: str) -> bool:
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        _run_docker(["start", agent["container_id"]])
        return True

    def remove(self, agent_id: str) -> bool:
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        try:
            _run_docker(["rm", "-f", agent["container_id"]])
        except RuntimeError:
            pass
        return True

    def logs(self, agent_id: str, tail: int = 50) -> str:
        agent = self.get_agent(agent_id)
        if not agent:
            return ""
        out, _ = _run_docker(["logs", "--tail", str(tail), agent["container_id"]])
        return out

    def ensure_network(self) -> None:
        try:
            _run_docker(["network", "inspect", AGENT_NETWORK])
        except RuntimeError:
            LOGGER.info("Creating network %s", AGENT_NETWORK)
            _run_docker(["network", "create", AGENT_NETWORK])


_HOST = AgentHost()


def list_agents() -> list[dict[str, Any]]:
    return _HOST.list_agents()


def get_agent(agent_id: str) -> dict[str, Any] | None:
    return _HOST.get_agent(agent_id)


def deploy_agent(agent_id: str, template_key: str | None = None, image: str | None = None, env: dict[str, str] | None = None) -> dict[str, Any]:
    _HOST.ensure_network()
    return _HOST.deploy(agent_id, template_key, image, env)


def stop_agent(agent_id: str) -> bool:
    return _HOST.stop(agent_id)


def start_agent(agent_id: str) -> bool:
    return _HOST.start(agent_id)


def remove_agent(agent_id: str) -> bool:
    return _HOST.remove(agent_id)


def agent_logs(agent_id: str, tail: int = 50) -> str:
    return _HOST.logs(agent_id, tail)


def list_templates() -> dict[str, Any]:
    return load_templates()


def template_targets(template_key: str) -> list[dict[str, Any]]:
    templates = load_templates()
    tmpl = templates.get(template_key, {})
    return tmpl.get("targets", [])
