from __future__ import annotations

import zipfile
from pathlib import Path

from scripts.build_platform_release_package import build_platform_package


def test_double_click_launchers_use_docker_directly() -> None:
    for launcher in [
        Path("launch-vulnoraiq-webui.bat"),
        Path("launch-vulnoraiq-webui.command"),
        Path("launch-vulnoraiq-webui.sh"),
    ]:
        text = launcher.read_text(encoding="utf-8")
        assert "docker compose build" in text
        assert "docker compose up -d" in text
        assert "docker compose ps" in text
        assert "bootstrap_launch.py" not in text

    bootstrap = Path("scripts/bootstrap_launch.py").read_text(encoding="utf-8")
    assert "docker" in bootstrap
    assert "compose" in bootstrap
    assert "docker-compose.yml" in bootstrap
    assert "http://127.0.0.1:8787" in bootstrap
    assert "webbrowser.open" in bootstrap


def test_windows_release_package_contains_docker_only_launcher_and_start_here(tmp_path: Path) -> None:
    package = build_platform_package("windows", version="9.9.9-test", output_dir=tmp_path)
    assert package.output.exists()
    with zipfile.ZipFile(package.output) as archive:
        names = set(archive.namelist())
        prefix = "vulnoraiq-9.9.9-test-windows/"
        assert prefix + "START_HERE.txt" in names
        assert prefix + "launch-vulnoraiq-webui.bat" in names
        assert prefix + "scripts/bootstrap_launch.py" in names
        assert prefix + "webui/static/console/index.html" in names
        start_here = archive.read(prefix + "START_HERE.txt").decode("utf-8")
        launcher = archive.read(prefix + "launch-vulnoraiq-webui.bat").decode("utf-8")
    assert "Double-click quick start" in start_here
    assert "Docker" in start_here
    assert "SHA256SUMS.txt" in start_here
    assert "docker compose build" in launcher
    assert "docker compose up -d" in launcher
    assert "bootstrap_launch.py" not in launcher


def test_release_workflow_produces_signed_attested_bundle() -> None:
    workflow = Path(".github/workflows/release-build.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "signing_mode:" in workflow
    assert "actions/attest-build-provenance@v2" in workflow
    assert "SHA256SUMS.txt" in workflow
    assert "RELEASE_GPG" in workflow
    assert "gpg --batch" in workflow
    assert "signed-release" in workflow
    assert "gh release upload" in workflow
