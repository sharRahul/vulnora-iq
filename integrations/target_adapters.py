from __future__ import annotations

import ipaddress
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
import yaml

SECRET_PATTERNS = [re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]+=*", re.I), re.compile(r"(?i)(api[_-]?key|token|secret|password)['\"]?\s*[:=]\s*['\"]?([^,'\"\s}]+)")]


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: ("<redacted>" if any(s in k.lower() for s in ("token", "secret", "password", "key", "authorization")) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        out = value
        for pat in SECRET_PATTERNS:
            out = pat.sub(lambda m: (m.group(1) + "=<redacted>") if len(m.groups()) > 1 else "Bearer <redacted>", out)
        return out[:20000]
    return value


def get_path(data: Any, path: str | None) -> Any:
    if not path:
        return data
    cur = data
    for part in path.replace("$.", "").split("."):
        if part == "":
            continue
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            cur = cur[part]
        else:
            raise KeyError(path)
    return cur


def render_template(obj: Any, prompt: str, target: dict[str, Any]) -> Any:
    if isinstance(obj, dict):
        return {k: render_template(v, prompt, target) for k, v in obj.items()}
    if isinstance(obj, list):
        return [render_template(v, prompt, target) for v in obj]
    if isinstance(obj, str):
        return obj.replace("{{prompt}}", prompt).replace("{{input}}", prompt).replace("{{payload}}", prompt).replace("{{ payload }}", prompt).replace("{{model}}", str(target.get("model", "local-model")))
    return obj


@dataclass(slots=True)
class AdapterResult:
    ok: bool
    answer: str = ""
    status_code: int | None = None
    request: dict[str, Any] = field(default_factory=dict)
    response: dict[str, Any] = field(default_factory=dict)
    error: dict[str, Any] | None = None
    tool_calls: list[Any] = field(default_factory=list)
    retrieval_context: Any = None
    duration_ms: int = 0


class RealTargetClient:
    name: str

    def __init__(self, name: str, config: dict[str, Any]) -> None:
        self.name = name
        self.config = normalize_target_config(name, config)
        self.last_result: AdapterResult | None = None
        self._last_request_at = 0.0

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        result = self.invoke_detailed(prompt, **kwargs)
        self.last_result = result
        if not result.ok:
            return f"TARGET_ERROR: {result.error.get('message') if result.error else 'unknown error'}"
        return result.answer

    def invoke_detailed(self, prompt: str, **kwargs: Any) -> AdapterResult:
        return invoke_target(self.name, self.config, prompt)


def normalize_target_config(name: str, raw: dict[str, Any]) -> dict[str, Any]:
    cfg = dict(raw)
    if "endpoint" in cfg and "base_url" not in cfg:
        parsed = urlparse(str(cfg["endpoint"]))
        cfg["base_url"] = f"{parsed.scheme}://{parsed.netloc}"
        cfg["endpoint_path"] = parsed.path or "/"
    cfg.setdefault("name", name)
    cfg.setdefault("method", "POST")
    cfg.setdefault("headers", {})
    cfg.setdefault("timeout", cfg.get("timeout_seconds", 30))
    cfg.setdefault("retry", {"attempts": 1, "backoff_seconds": 0.2})
    cfg.setdefault("rate_limit", {"requests_per_second": 1})
    cfg.setdefault("authorisation_required", True)
    cfg.setdefault("safety_profile", "local_lab_safe")
    cfg.setdefault("environment", "local")
    cfg.setdefault("tags", [])
    t = cfg.get("type")
    if t in {"custom_agent", "custom_http_agent", "http"}:
        cfg["type"] = "http_json"
    if t == "chat_completions_compatible":
        cfg["type"] = "chat_completions"
    return cfg


def validate_target_definition(name: str, raw: dict[str, Any]) -> dict[str, Any]:
    cfg = normalize_target_config(name, raw)
    target_type = str(cfg.get("type") or "").strip()
    if target_type not in {"http_json", "chat_completions", "ollama_generate", "webhook_json", "rag_query", "agent_tool_loop"}:
        raise ValueError(f"unsupported target type: {target_type or '<missing>'}")
    if not str(cfg.get("name") or "").strip():
        raise ValueError("target name is required")
    if not str(cfg.get("base_url") or "").strip():
        raise ValueError("base_url or endpoint is required")
    endpoint_path = str(cfg.get("endpoint_path") or "/").strip()
    if not endpoint_path.startswith("/"):
        raise ValueError("endpoint_path must start with '/'")
    cfg["endpoint_path"] = endpoint_path
    if target_type in {"chat_completions", "ollama_generate"} and not str(cfg.get("model") or "").strip():
        raise ValueError(f"model is required for target type {target_type}")
    body_template = cfg.get("request_body_template")
    if body_template is not None and not isinstance(body_template, (dict, list)):
        raise ValueError("request_body_template must be a JSON object or array")
    headers = cfg.get("headers") or {}
    if not isinstance(headers, dict):
        raise ValueError("headers must be a JSON object")
    validate_url(cfg)
    return cfg


def _load_safety_profile(name: str) -> dict[str, Any]:
    path = os.getenv("VULNORAIQ_SAFETY_PROFILE_PATH") or str(os.getenv("VULNORAIQ_CONFIG_DIR", "config") + "/safety_profiles.yaml")
    try:
        data = yaml.safe_load(open(path, encoding="utf-8")) or {}
    except FileNotFoundError:
        return {}
    return (data.get("safety_profiles") or {}).get(name, {})


def validate_url(cfg: dict[str, Any]) -> str:
    url = urljoin(str(cfg.get("base_url", "")).rstrip("/") + "/", str(cfg.get("endpoint_path", "/")).lstrip("/"))
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("invalid URL: only http(s) targets with host are supported")
    profile = _load_safety_profile(str(cfg.get("safety_profile", "")))
    allowed_schemes = set(profile.get("allowed_schemes") or [])
    if allowed_schemes and parsed.scheme not in allowed_schemes:
        raise ValueError(f"scheme '{parsed.scheme}' is blocked by safety profile")
    host = parsed.hostname
    allowed_hosts = set(profile.get("allowed_hosts") or [])
    if allowed_hosts and host not in allowed_hosts:
        raise ValueError(f"host '{host}' is blocked by safety profile allowlist")
    allow_external = bool(cfg.get("allow_external", False) or profile.get("allow_external_network", False))
    if not allow_external and not allowed_hosts:
        try:
            ip = ipaddress.ip_address(host)
            allowed = ip.is_loopback or ip.is_private or ip.is_link_local
        except ValueError:
            allowed = host in {"localhost"} or host.endswith(".local") or host.endswith(".internal")
        if not allowed:
            raise ValueError("target host is not loopback/internal; external targets are blocked by default")
    return url


def _headers(cfg: dict[str, Any]) -> dict[str, str]:
    headers = {str(k): str(v) for k, v in (cfg.get("headers") or {}).items()}
    headers.setdefault("Content-Type", "application/json")
    env = cfg.get("token_env_var") or cfg.get("auth_token_env")
    if env:
        token = os.getenv(str(env))
        if not token:
            raise RuntimeError(f"Target token environment variable '{env}' is not set.")
        header = str(cfg.get("auth_header", "Authorization"))
        prefix = str(cfg.get("auth_prefix", "Bearer "))
        headers[header] = prefix + token
    return headers


def _body(cfg: dict[str, Any], prompt: str) -> Any:
    if cfg.get("request_template") is not None:
        return render_template(cfg["request_template"], prompt, cfg)
    if cfg.get("request_body_template") is not None:
        return render_template(cfg["request_body_template"], prompt, cfg)
    typ = cfg.get("type")
    if typ == "chat_completions":
        return {"model": cfg.get("model", "local-model"), "messages": [{"role": "user", "content": prompt}], "temperature": 0}
    if typ == "ollama_generate":
        return {"model": cfg.get("model", "llama3"), "prompt": prompt, "stream": False}
    if typ in {"rag_query"}:
        return {"query": prompt, "include_context": True}
    if typ in {"webhook_json", "agent_tool_loop"}:
        return {"input": prompt, "metadata": {"assessment_client": cfg.get("name")}}
    return {"prompt": prompt, "input": prompt}


def _default_response_path(typ: str) -> str | None:
    return {"chat_completions": "choices.0.message.content", "ollama_generate": "response", "rag_query": "answer"}.get(typ)


def invoke_target(name: str, cfg: dict[str, Any], prompt: str) -> AdapterResult:
    start = time.monotonic()
    try:
        url = validate_url(cfg)
        rps = float((cfg.get("rate_limit") or {}).get("requests_per_second", 0) or 0)
        if rps > 0:
            time.sleep(min(1 / rps, 2.0))
        body = _body(cfg, prompt)
        headers = _headers(cfg)
        attempts = int((cfg.get("retry") or {}).get("attempts", 1) or 1)
        method = str(cfg.get("method", "POST")).upper()
        response = None
        for attempt in range(max(1, attempts)):
            try:
                response = requests.request(method, url, json=body if method != "GET" else None, params=body if method == "GET" else None, headers=headers, timeout=float(cfg.get("timeout", cfg.get("timeout_seconds", _load_safety_profile(str(cfg.get("safety_profile", ""))).get("request_timeout_seconds", 30)))))
                break
            except requests.RequestException:
                if attempt >= attempts - 1:
                    raise
                time.sleep(float((cfg.get("retry") or {}).get("backoff_seconds", 0.2)))
        assert response is not None
        text = response.text[: int(cfg.get("max_response_bytes", _load_safety_profile(str(cfg.get("safety_profile", ""))).get("max_response_body_bytes", 200000)))]
        data: Any
        try:
            data = response.json()
        except ValueError:
            data = text
        answer_value = get_path(data, (cfg.get("response_extraction_path") or (cfg.get("response_extraction") or {}).get("path")) or _default_response_path(str(cfg.get("type"))))
        answer = answer_value if isinstance(answer_value, str) else json.dumps(answer_value, default=str)
        return AdapterResult(
            ok=200 <= response.status_code < 300,
            answer=answer,
            status_code=response.status_code,
            request={"method": method, "url": url, "headers": redact(headers), "body": redact(body)},
            response={"headers": redact(dict(response.headers)), "body": redact(data)},
            tool_calls=get_path(data, cfg.get("tool_calls_path")) if cfg.get("tool_calls_path") else [],
            retrieval_context=get_path(data, cfg.get("retrieval_context_path")) if cfg.get("retrieval_context_path") else None,
            duration_ms=int((time.monotonic() - start) * 1000),
            error=None if 200 <= response.status_code < 300 else {"type": "http_error", "message": f"HTTP {response.status_code}"},
        )
    except Exception as exc:
        return AdapterResult(ok=False, error={"type": exc.__class__.__name__, "message": redact(str(exc))}, duration_ms=int((time.monotonic() - start) * 1000))


def connectivity_check(name: str, cfg: dict[str, Any]) -> dict[str, Any]:
    cfg = normalize_target_config(name, cfg)
    prompt = str(cfg.get("health_prompt", "Health check: reply with OK."))
    result = invoke_target(name, cfg, prompt)
    return {"target_id": name, "ready": result.ok and bool(result.answer), "normalized_response": result.answer[:500], "status_code": result.status_code, "error": result.error, "request": result.request, "response_preview": redact(result.response.get("body")) if result.response else None}

class LLMTargetAdapter(RealTargetClient):
    """Minimal OpenAI-compatible LLM target adapter."""

class RAGTargetAdapter(RealTargetClient):
    """Minimal RAG endpoint target adapter."""

class AgentTargetAdapter(RealTargetClient):
    """Minimal agent framework endpoint target adapter."""

class GatewayTargetAdapter(RealTargetClient):
    """Minimal provider gateway target adapter."""


def validate_real_environment_config(name: str, raw: dict[str, Any]) -> dict[str, Any]:
    cfg = normalize_target_config(name, raw)
    if not cfg.get("explicit_authorisation") and not cfg.get("authorised"):
        raise ValueError("real-environment targets require explicit_authorisation: true")
    if cfg.get("dry_run", True) is not True and not cfg.get("allow_live_requests"):
        raise ValueError("dry-run is the default; set allow_live_requests only for approved internal validation")
    validate_url(cfg)
    if not cfg.get("allowed_hosts") and not cfg.get("allowed_host_pattern") and not _load_safety_profile(str(cfg.get("safety_profile", ""))).get("allowed_hosts"):
        raise ValueError("target allow-list or allowed_host_pattern is required")
    if not cfg.get("rate_limit"):
        raise ValueError("rate_limit is required")
    for key in ("api_key", "token", "password", "authorization"):
        if key in {str(k).lower() for k in cfg}:
            raise ValueError("credentials must be referenced through environment variables, not inline values")
    return cfg
