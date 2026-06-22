from __future__ import annotations

from integrations.contract_validation import TargetContractValidator


def test_default_target_contracts_are_shape_valid_but_placeholder_warn() -> None:
    result = TargetContractValidator().validate()

    assert result.status == "warn"
    assert result.validated_count >= 4
    assert not result.errors
    assert result.warnings
