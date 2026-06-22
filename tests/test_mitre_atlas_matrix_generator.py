from __future__ import annotations

from pathlib import Path

import yaml

from scripts.generate_mitre_atlas_matrix import UNMAPPED_LABEL, render_matrix, write_or_check


def _fixture() -> dict:
    return {
        "format-version": "6.0.0",
        "collection": {"name": "ATLAS", "version": "test", "modified-date": "2026-01-01"},
        "tactics": {
            "AML.TA0001": {"name": "AI Attack Staging", "attack-reference": {"id": "TA0042"}},
            "AML.TA0002": {"name": "Prompt Boundary Review"},
        },
        "techniques": {
            "AML.T0005": {
                "name": "Create Proxy AI Model",
                "maturity": "Demonstrated",
                "platforms": ["Predictive AI", "Generative AI"],
            },
            "AML.T0051": {
                "name": "LLM Prompt Injection",
                "maturity": "Demonstrated",
                "platforms": ["Generative AI", "Agentic AI"],
            },
        },
        "relationships": {
            "AML.T0005": {"achieves": ["AML.TA0001"]},
            "AML.T0051": {"achieves": ["AML.TA0002"]},
        },
    }


def test_render_matrix_includes_all_tactics_and_techniques() -> None:
    rendered = render_matrix(_fixture(), "fixture.yaml")

    assert "AML.TA0001" in rendered
    assert "AI Attack Staging" in rendered
    assert "AML.TA0002" in rendered
    assert "Prompt Boundary Review" in rendered
    assert "AML.T0005" in rendered
    assert "Create Proxy AI Model" in rendered
    assert "AML.T0051" in rendered
    assert "LLM Prompt Injection" in rendered


def test_render_matrix_keeps_unmapped_items_visible() -> None:
    rendered = render_matrix(_fixture(), "fixture.yaml")

    assert UNMAPPED_LABEL in rendered
    assert "## Unmapped / map later backlog" in rendered
    assert "AML.TA0001" in rendered
    assert "AML.T0005" in rendered


def test_render_matrix_adds_candidate_mapping_when_known_hint_exists() -> None:
    rendered = render_matrix(_fixture(), "fixture.yaml")

    assert "LLM01 Prompt Injection" in rendered
    assert "Prompt boundary and protected-instruction checks" in rendered
    assert "Candidate mapping / needs validation" in rendered


def test_write_or_check_detects_drift(tmp_path: Path) -> None:
    source = tmp_path / "atlas.yaml"
    output = tmp_path / "matrix.md"
    source.write_text(yaml.safe_dump(_fixture()), encoding="utf-8")

    assert write_or_check(str(source), output, check=False) == 0
    assert write_or_check(str(source), output, check=True) == 0
    output.write_text(output.read_text(encoding="utf-8") + "\nmanual drift\n", encoding="utf-8")
    assert write_or_check(str(source), output, check=True) == 1
