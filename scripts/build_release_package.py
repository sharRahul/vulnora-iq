from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from typing import Any

import yaml


DEFAULT_MANIFEST = "config/release_package.yaml"
DEFAULT_OUTPUT = "dist/vulnoraiq-example-package.zip"


def load_manifest(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def iter_paths(include_paths: list[str]) -> list[Path]:
    selected: list[Path] = []
    for raw_path in include_paths:
        path = Path(raw_path)
        if path.is_dir():
            selected.extend(item for item in sorted(path.rglob("*")) if item.is_file())
        elif path.is_file():
            selected.append(path)
    return selected


def build_package(manifest_path: str | Path = DEFAULT_MANIFEST) -> Path:
    manifest = load_manifest(manifest_path)
    output = Path(manifest.get("output_path", DEFAULT_OUTPUT))
    output.parent.mkdir(parents=True, exist_ok=True)
    include_paths = list(manifest.get("include_paths", []))
    files = iter_paths(include_paths)
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            archive.writestr(str(file_path), file_path.read_bytes())
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a safe VulnoraIQ example-output release package.")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="Release package manifest path.")
    args = parser.parse_args()
    output = build_package(args.manifest)
    print(f"VulnoraIQ release package written to {output}")


if __name__ == "__main__":
    main()
