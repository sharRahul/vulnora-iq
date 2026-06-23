from __future__ import annotations

import os
from urllib.parse import urlparse

_ALLOWED_SCHEMES = {"http", "https"}


def _allowed_hosts() -> set[str]:
    raw = os.getenv("VULNORAIQ_ALLOWED_TARGET_HOSTS", "")
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def _hostname_matches(hostname: str, allowed: str) -> bool:
    if allowed.startswith("*."):
        suffix = allowed[1:]
        return hostname.endswith(suffix) and hostname != allowed[2:]
    return hostname == allowed


def validate_target_endpoint(endpoint: str) -> str:
    """Validate configured outbound target URLs before assessment requests are sent."""
    parsed = urlparse(endpoint)
    if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
        raise ValueError("Target endpoint must use http or https.")
    if not parsed.hostname:
        raise ValueError("Target endpoint must include a hostname.")
    if parsed.username or parsed.password:
        raise ValueError("Target endpoint must not embed credentials in the URL.")

    hostname = parsed.hostname.lower()
    allowed_hosts = _allowed_hosts()
    if allowed_hosts and not any(_hostname_matches(hostname, allowed) for allowed in allowed_hosts):
        raise ValueError("Target endpoint host is not in VULNORAIQ_ALLOWED_TARGET_HOSTS.")
    return endpoint
