from __future__ import annotations

from core.approval_evidence import ApprovalEvidenceRegistry


def test_default_approval_evidence_validates() -> None:
    result = ApprovalEvidenceRegistry().validate_reference("DEMO-APPROVAL-001")

    assert result.status == "pass"
    assert not result.errors


def test_missing_approval_reference_fails() -> None:
    result = ApprovalEvidenceRegistry().validate_reference("DOES-NOT-EXIST")

    assert result.status == "fail"
    assert result.errors
