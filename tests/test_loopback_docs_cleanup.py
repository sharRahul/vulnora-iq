from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

REMOVED_DOCS = {
    "WEBUI_VALIDATED_IMPLEMENTATION_PLAN.md",
    "WEBUI_IMPROVEMENT_SERIES_SUMMARY.md",
    "DOCKER_RUNTIME_DEPENDENCIES.md",
}


def test_docker_compose_webui_port_is_loopback_only() -> None:
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    service = compose["services"]["vulnoraiq-web"]
    ports = [str(port) for port in service.get("ports", [])]

    assert "127.0.0.1:8787:8787" in ports
    assert "8787:8787" not in ports
    assert "0.0.0.0:8787:8787" not in ports


def test_removed_archival_docs_are_not_linked() -> None:
    for filename in REMOVED_DOCS:
        assert not (ROOT / "docs" / filename).exists(), f"stale documentation still exists: {filename}"

    searchable_markdown = [ROOT / "README.md", ROOT / "SECURITY.md", ROOT / "CHANGELOG.md"]
    searchable_markdown.extend((ROOT / "docs").rglob("*.md"))
    combined = "\n".join(path.read_text(encoding="utf-8") for path in searchable_markdown if path.exists())

    for filename in REMOVED_DOCS:
        assert filename not in combined, f"stale documentation is still referenced: {filename}"
