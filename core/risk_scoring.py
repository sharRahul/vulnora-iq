from __future__ import annotations

from core.types import Finding


SEVERITY_BASE_SCORE = {
    "info": 0.5,
    "low": 2.0,
    "medium": 5.0,
    "high": 8.0,
    "critical": 9.5,
}


def score_finding(finding: Finding) -> float:
    """Score a finding using a transparent AI VAPT scoring model."""

    base = SEVERITY_BASE_SCORE.get(finding.severity.lower(), 0.5)
    evidence_bonus = min(len(finding.evidence) * 0.2, 0.8)
    atlas_bonus = 0.4 if finding.mitre_atlas else 0.0
    return round(min(base + evidence_bonus + atlas_bonus, 10.0), 1)


def score_findings(findings: list[Finding]) -> list[Finding]:
    for finding in findings:
        finding.score = score_finding(finding)
    return findings
