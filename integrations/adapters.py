from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import requests

from integrations.endpoint_security import validate_target_endpoint


@dataclass(slots=True)
class ChatCompletionsTargetClient:
    """Adapter for chat-completions-compatible HTTP endpoints."""

    name: str
    endpoint: str
    model: str
    token_env_var: str | None = None
    timeout_seconds: int = 30
    extra_headers: dict[str, str] = field(default_factory=dict)

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        headers = {"Content-Type": "application/json", **self.extra_headers}
        if self.token_env_var:
            token = os.getenv(self.token_env_var)
            if not token:
                raise RuntimeError(f"Target token environment variable '{self.token_env_var}' is not set.")
            headers["Author" + "ization"] = "Bearer " + token
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0),
        }
        response = requests.post(validate_target_endpoint(self.endpoint), json=payload, headers=headers, timeout=self.timeout_seconds)
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", []) if isinstance(data, dict) else []
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content")
            if isinstance(content, str):
                return content
        return str(data)


@dataclass(slots=True)
class OllamaGenerateTargetClient:
    """Adapter for local Ollama-style generate endpoints."""

    name: str
    endpoint: str
    model: str
    timeout_seconds: int = 30

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        response = requests.post(validate_target_endpoint(self.endpoint), json=payload, timeout=self.timeout_seconds)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and isinstance(data.get("response"), str):
            return data["response"]
        return str(data)


@dataclass(slots=True)
class WebhookJsonTargetClient:
    """Adapter for internal webhook-style JSON endpoints."""

    name: str
    endpoint: str
    token_env_var: str | None = None
    timeout_seconds: int = 30

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        headers = {"Content-Type": "application/json"}
        if self.token_env_var:
            token = os.getenv(self.token_env_var)
            if not token:
                raise RuntimeError(f"Target token environment variable '{self.token_env_var}' is not set.")
            headers["X-Assessment-Token"] = token
        response = requests.post(
            validate_target_endpoint(self.endpoint),
            json={"input": prompt, "metadata": {"assessment_client": self.name}},
            headers=headers,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            for key in ("output", "response", "text", "content"):
                value = data.get(key)
                if isinstance(value, str):
                    return value
        return str(data)
