from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCKER_LAB_LAUNCHERS = [
    ROOT / "launch-vulnoraiq-docker-lab.bat",
    ROOT / "launch-vulnoraiq-docker-lab.command",
    ROOT / "launch-vulnoraiq-docker-lab.sh",
]


def test_docker_lab_launchers_run_docker_compose_directly() -> None:
    for launcher in DOCKER_LAB_LAUNCHERS:
        content = launcher.read_text(encoding="utf-8")
        assert "docker compose build" in content
        assert "docker compose up -d" in content
        assert "docker compose ps" in content
        assert "bootstrap_launch.py" not in content
