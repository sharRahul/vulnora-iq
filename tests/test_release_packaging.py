from __future__ import annotations

import zipfile
from pathlib import Path

from scripts.build_platform_release_package import build_platform_package


def test_double_click_launchers_use_bootstrap() -> None:
    assert "scripts\\bootstrap_launch.py" in Path("launch-vulnoraiq-webui.bat").read_text(encoding="utf-8")
    assert "scripts/bootstrap_launch.py" in Path("launch-vulnoraiq-webui.command").read_text(encoding="utf-8")
    assert "scripts/bootstrap_launch.py" in Path("launch-vulnoraiq-webui.sh").read_text(encoding="utf-8")
    bootstrap = Path("scripts/bootstrap_launch.py").read_text(encoding="utf-8")
    assert '"-m"' in bootstrap
    assert '"venv"' in bootstrap
    assert "pip" in bootstrap
    assert '"scripts"' in bootstrap
    assert '"launch_webui.py"' in bootstrap


def test_windows_release_package_contains_bootstrap_and_start_here(tmp_path: Path) -> None:
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
    assert ".venv" in start_here
    assert "SHA256SUMS.txt" in start_here
    assert "scripts\\bootstrap_launch.py" in launcher


def test_release_workflow_produces_signed_attested_bundle() -> None:
    workflow = Path(".github/workflows/release-build.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "signing_mode:" in workflow
    assert "actions/attest-build-provenance@v2" in workflow
    assert "SHA256SUMS.txt" in workflow
    assert "RELEASE_GPG_PRIVATE_KEY" in workflow
    assert "gpg --batch" in workflow
    assert "vulnoraiq-${{ env.VULNORAIQ_RELEASE_VERSION }}-signed-release" in workflow
    assert "gh release upload" in workflow
