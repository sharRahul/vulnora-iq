from __future__ import annotations

from scripts.validate_package_metadata import PackageMetadataValidator


def test_package_metadata_validation_passes_current_repo() -> None:
    result = PackageMetadataValidator().validate()

    assert result.status == "pass"
    assert not result.errors
