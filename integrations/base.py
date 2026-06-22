from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(slots=True)
class DemoEchoClient:
    """Safe in-memory target used for local demo scans."""

    name: str = "demo-echo"

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        lowered = prompt.lower()
        if "system prompt" in lowered or "developer message" in lowered:
            return "I can't disclose hidden instructions or protected system content."
        if "api key" in lowered or "password" in lowered or "private key" in lowered:
            return "I can't provide secrets."
        return f"Demo response received for assessment input: {prompt[:120]}"


@dataclass(slots=True)
class HttpJsonTargetClient:
    """Minimal HTTP JSON adapter for explicitly authorised AI application targets.

    The adapter posts a JSON body containing both `prompt` and `input` fields so simple
    local harnesses can choose either convention. The response is normalised from common
    JSON fields (`output`, `response`, `text`, `message`, or `content`) and falls back to
    raw response text.
    """

    name: str
    endpoint: str
    token_env_var: str | None = None
    timeout_seconds: int = 30

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        headers = {"Content-Type": "application/json"}
        if self.token_env_var:
            token = os.getenv(self.token_env_var)
            if not token:
                raise RuntimeError(
                    f"Target requires bearer token environment variable '{self.token_env_var}', but it is not set."
                )
            headers["Authorization"] = f"Bearer {token}"

        payload = {"prompt": prompt, "input": prompt}
        response = requests.post(self.endpoint, json=payload, headers=headers, timeout=self.timeout_seconds)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type.lower():
            return response.text

        data = response.json()
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            for key in ("output", "response", "text", "message", "content"):
                value = data.get(key)
                if isinstance(value, str):
                    return value
            return str(data)
        return str(data)
