from __future__ import annotations

import argparse
import os
import zipfile
from dataclasses import dataclass
from pathlib import Path

DEFAULT_VERSION = "0.2.0"
DEFAULT_OUTPUT_DIR = Path("dist/release")

ROOT_FILES = [
    "README.md",
    "ACCEPTABLE_USE.md",
    "LICENSE",
    "NOTICE",
    "SECURITY.md",
    "CHANGELOG.md",
    "THIRD_PARTY_NOTICES.md",
    "pyproject.toml",
    "launch-vulnoraiq-webui.py",
    "launch-vulnoraiq-webui.bat",
    "launch-vulnoraiq-webui.command",
    "launch-vulnoraiq-webui.sh",
]

ROOT_DIRS = [
    "agent_testing",
    "benchmarks",
    "config",
    "core",
    "dashboards",
    "docs",
    "examples",
    "integrations",
    "modules",
    "payloads",
    "rag_testing",
    "reports",
    "scripts",
    "webui",
]

EXCLUDED_PARTS = {
    ".git",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "venv",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".db", ".key", ".pem"}
EXCLUDED_NAME_FRAGMENTS = (".secret", "_secret", "local")
PLATFORMS = {"windows", "linux", "macos"}
EXECUTABLE_LAUNCHERS = {"launch-vulnoraiq-webui.command", "launch-vulnoraiq-webui.sh"}


@dataclass(frozen=True)
class ReleasePackage:
    platform: str
    version: str
    output: Path
    file_count: int


def _is_excluded(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDED_PARTS:
        return True
    if path.suffix in EXCLUDED_SUFFIXES:
        return True
    lowered = str(path).lower()
    return any(fragment in lowered for fragment in EXCLUDED_NAME_FRAGMENTS)


def _iter_release_files() -> list[Path]:
    files: list[Path] = []
    for raw_file in ROOT_FILES:
        path = Path(raw_file)
        if path.exists() and path.is_file() and not _is_excluded(path):
            files.append(path)
    for raw_dir in ROOT_DIRS:
        path = Path(raw_dir)
        if not path.exists() or not path.is_dir():
            continue
        files.extend(item for item in sorted(path.rglob("*")) if item.is_file() and not _is_excluded(item))
    unique = sorted(set(files), key=lambda item: item.as_posix())
    return unique


def _readme_for(platform: str, version: str) -> str:
    launcher = {
        "windows": "launch-vulnoraiq-webui.bat",
        "linux": "launch-vulnoraiq-webui.sh",
        "macos": "launch-vulnoraiq-webui.command",
    }[platform]
    return f"""VulnoraIQ {version} {platform} release package

This package is for local/self-hosted authorised AI security assessment only.

Quick start
-----------
1. Install Python 3.10 or newer.
2. Open a terminal in this extracted folder.
3. Run:

   python -m venv .venv
   python -m pip install --upgrade pip
   python -m pip install -e .

4. Start the Web UI with:

   {launcher}

Alternative cross-platform launcher:

   python launch-vulnoraiq-webui.py

Security and acceptable use
---------------------------
Use VulnoraIQ only against systems you own or are explicitly authorised to assess.
See ACCEPTABLE_USE.md, SECURITY.md, and LICENSE before use.

Production/internal server mode
-------------------------------
For shared or internal-server deployments, do not expose local launcher mode.
Use vulnoraiq-web with production environment validation and auth enabled.
"""


def _write_file(archive: zipfile.ZipFile, archive_path: str, data: bytes, executable: bool = False) -> None:
    info = zipfile.ZipInfo(archive_path)
    info.compress_type = zipfile.ZIP_DEFLATED
    mode = 0o755 if executable else 0o644
    info.external_attr = (mode & 0xFFFF) << 16
    archive.writestr(info, data)


def build_platform_package(
    platform: str,
    version: str = DEFAULT_VERSION,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> ReleasePackage:
    if platform not in PLATFORMS:
        supported = ", ".join(sorted(PLATFORMS))
        raise ValueError(f"Unsupported platform {platform!r}; expected one of: {supported}")
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    output = output_root / f"vulnoraiq-{version}-{platform}.zip"
    prefix = f"vulnoraiq-{version}-{platform}"
    release_files = _iter_release_files()
    if not release_files:
        raise RuntimeError("No release files selected")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        _write_file(archive, f"{prefix}/START_HERE.txt", _readme_for(platform, version).encode("utf-8"))
        for file_path in release_files:
            archive_name = f"{prefix}/{file_path.as_posix()}"
            executable = file_path.name in EXECUTABLE_LAUNCHERS
            _write_file(archive, archive_name, file_path.read_bytes(), executable=executable)
    return ReleasePackage(platform=platform, version=version, output=output, file_count=len(release_files) + 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build VulnoraIQ platform release package archives.")
    parser.add_argument("--platform", choices=sorted(PLATFORMS), required=True)
    parser.add_argument("--version", default=os.getenv("VULNORAIQ_RELEASE_VERSION", DEFAULT_VERSION))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    package = build_platform_package(args.platform, args.version, args.output_dir)
    print(f"Built {package.output} with {package.file_count} files")


if __name__ == "__main__":
    main()
