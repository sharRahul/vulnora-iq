from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

REMOVED_DOC_PARTS = [
    ("WEBUI", "VALIDATED", "IMPLEMENTATION", "PLAN"),
    ("WEBUI", "IMPROVEMENT", "SERIES", "SUMMARY"),
    ("DOCKER", "RUNTIME", "DEPENDENCIES"),
]


def _removed_filename(parts: tuple[str, ...]) -> str:
    return "_".join(parts) + ".md"


def test_docker_compose_webui_port_is_loopback_only() -> None:
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    service = compose["services"]["vulnoraiq-web"]
    ports = [str(port) for port in service.get("ports", [])]

    assert "127.0.0.1:8787:8787" in ports
    assert "8787:8787" not in ports
    assert "0.0.0.0:8787:8787" not in ports


def test_removed_archival_docs_are_not_linked() -> None:
    removed_filenames = [_removed_filename(parts) for parts in REMOVED_DOC_PARTS]
    for filename in removed_filenames:
        assert not (ROOT / "docs" / filename).exists(), f"stale documentation still exists: {filename}"

    searchable_markdown = [ROOT / "README.md", ROOT / "SECURITY.md", ROOT / "CHANGELOG.md"]
    searchable_markdown.extend((ROOT / "docs").rglob("*.md"))
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in searchable_markdown
        if path.exists() and path.name not in removed_filenames
    )

    for filename in removed_filenames:
        assert filename not in combined, f"stale documentation is still referenced: {filename}"
