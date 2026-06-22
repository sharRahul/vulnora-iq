from __future__ import annotations

from pathlib import Path

import yaml

from core.payload_loader import PayloadLibrary

EXPECTED_MODULES = {
    "owasp_llm01_prompt_injection",
    "owasp_llm02_sensitive_information_disclosure",
    "owasp_llm03_supply_chain",
    "owasp_llm04_data_and_model_poisoning",
    "owasp_llm05_improper_output_handling",
    "owasp_llm06_excessive_agency",
    "owasp_llm07_system_prompt_leakage",
    "owasp_llm08_vector_embedding_weaknesses",
    "owasp_llm09_misinformation",
    "owasp_llm10_unbounded_consumption",
}
SOURCE_DOCUMENT = "docs/owasp-documents/LLMAll_en-US_FINAL.pdf"


def _payload_data() -> dict:
    return yaml.safe_load(Path("payloads/owasp_document_examples.yaml").read_text(encoding="utf-8"))


def test_document_payloads_cover_all_owasp_modules():
    data = _payload_data()
    covered = set()
    for payload in data["payloads"]:
        covered.update(payload["metadata"].get("applies_to", []))

    assert data["source"]["document_path"] == SOURCE_DOCUMENT
    assert EXPECTED_MODULES <= covered
    assert len(data["payloads"]) >= 10


def test_document_payload_metadata_is_complete():
    for payload in _payload_data()["payloads"]:
        metadata = payload["metadata"]
        assert payload["id"].startswith("owasp-doc-llm")
        assert payload["input"]
        assert payload["expected_behavior"]
        assert metadata["source_document"] == SOURCE_DOCUMENT
        assert metadata["review_status"] == "reviewed"
        assert metadata["owasp_id"].startswith("LLM")
        assert metadata["scenario_type"]
        assert metadata["applies_to"]


def test_default_config_loads_document_examples():
    config = yaml.safe_load(Path("config/default.yaml").read_text(encoding="utf-8"))
    assert "owasp_document_examples" in config["payload_libraries"]


def test_payload_library_selects_document_examples_by_module():
    library = PayloadLibrary()
    for module_name in EXPECTED_MODULES:
        selected = library.for_module(module_name, library_names=["owasp_document_examples"])
        assert selected, module_name
        assert any((payload.metadata or {}).get("source_document") == SOURCE_DOCUMENT for payload in selected)
