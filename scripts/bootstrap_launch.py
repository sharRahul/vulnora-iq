from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT / ".venv"
BOOTSTRAP_MARKER = VENV_DIR / ".vulnoraiq-bootstrap-ok"


def _venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _run(command: list[str]) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def _ensure_virtualenv() -> Path:
    python = _venv_python()
    if not python.exists():
        print("Creating local VulnoraIQ virtual environment in .venv ...")
        _run([sys.executable, "-m", "venv", str(VENV_DIR)])
    if not BOOTSTRAP_MARKER.exists():
        print("Installing VulnoraIQ dependencies into the local virtual environment ...")
        _run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
        _run([str(python), "-m", "pip", "install", "-e", ".[release]"])
        BOOTSTRAP_MARKER.write_text("ok\n", encoding="utf-8")
    return python


def main() -> None:
    os.chdir(ROOT)
    python = _ensure_virtualenv()
    launcher = ROOT / "scripts" / "launch_webui.py"
    os.execv(str(python), [str(python), str(launcher), *sys.argv[1:]])


if __name__ == "__main__":
    main()
