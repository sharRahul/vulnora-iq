from __future__ import annotations

import pytest

from core.payload_loader import PayloadLibrary
from core.scanner import Scanner
from modules.registry import ModuleRegistry


def test_module_registry_resolves_builtin_module() -> None:
    registry = ModuleRegistry()

    module = registry.get("owasp_llm01_prompt_injection")

    assert module.metadata.name == "owasp_llm01_prompt_injection"
    assert module.metadata.owasp_id == "LLM01:2025"


def test_module_registry_rejects_unknown_module() -> None:
    registry = ModuleRegistry()

    with pytest.raises(KeyError):
        registry.get("missing_module")


def test_payload_library_loads_baseline_payloads() -> None:
    library = PayloadLibrary()

    payloads = library.for_module("owasp_llm02_sensitive_information_disclosure", ["safe_baseline"])

    assert payloads
    assert payloads[0].id == "baseline-sensitive-001"


def test_scan_evidence_includes_payload_ids() -> None:
    result = Scanner().scan(target_name="demo", profile_name="baseline")

    evidence = result.findings[0].evidence
    assert "payload_ids" in evidence
    assert evidence["payload_count"] >= 1
