from __future__ import annotations

import zipfile

from reports.html_export_package import HtmlExportPackager


def test_html_export_package_includes_expected_artifacts(tmp_path) -> None:
    output_dir = tmp_path / "reports"
    output_dir.mkdir()
    (output_dir / "dashboard.html").write_text("<h1>demo</h1>", encoding="utf-8")
    (output_dir / "scan-report.json").write_text("{}", encoding="utf-8")
    (output_dir / "scan-report.md").write_text("# report", encoding="utf-8")
    package_path = tmp_path / "export.zip"

    result = HtmlExportPackager().package(output_dir, package_path)

    assert result.status == "pass"
    with zipfile.ZipFile(package_path) as archive:
        names = set(archive.namelist())
    assert "dashboard.html" in names
    assert "scan-report.json" in names
    assert "scan-report.md" in names
    assert "VULNORAIQ_EXPORT_MANIFEST.yaml" in names
