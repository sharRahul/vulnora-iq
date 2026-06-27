"""Generate ~600 instruction-tuning examples from OWASP docs and related resources."""

from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path
from typing import Any, Callable

random.seed(42)

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs" / "owasp"
ASSURANCE_FILE = Path(__file__).resolve().parent.parent / "docs" / "ASSESSMENT_ASSURANCE.md"
OUTPUT_FILE = Path(__file__).resolve().parent / "train_dataset.jsonl"

SYSTEM_PROMPT = (
    "You are the VulnoraIQ assistant, a focused helper for authorised AI/LLM security "
    "assessment. You explain vulnerabilities, summarise evidence, and suggest mitigations. "
    "You provide mitigation guidance only and never claim to apply fixes to a target. Ground "
    "answers in the supplied finding evidence and reference material; if you are unsure, say so. "
    "Findings are evidence requiring human review, not certified assurance."
)

IM_START = "<|im_start|>"
IM_END = "<|im_end|>"


def _parse_doc(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    sections: dict[str, str] = {}
    current_heading = "title"
    buffer: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if buffer:
                sections[current_heading] = "\n".join(buffer).strip()
                buffer = []
            heading = line.strip("# ").strip().lower().replace(" ", "_")
            current_heading = heading
        elif line.startswith("# "):
            if buffer:
                sections[current_heading] = "\n".join(buffer).strip()
                buffer = []
            sections["title"] = line.strip("# ").strip()
            current_heading = "preamble"
        elif line.startswith("### "):
            if buffer:
                sections[current_heading] = "\n".join(buffer).strip()
                buffer = []
            current_heading = line.strip("# ").strip().lower().replace(" ", "_")
        else:
            buffer.append(line)
    if buffer:
        prev = sections.get(current_heading, "")
        sections[current_heading] = (prev + "\n" + "\n".join(buffer)).strip()
    return sections


# Some source docs use slightly different section headings for the same concept
# (e.g. LLM05 uses "Expected good/bad behaviour"). Map those onto the canonical
# keys the generators read, so no document is silently dropped.
_HEADING_ALIASES = {
    "expected_good_behaviour": "secure_expected_behaviour",
    "expected_bad_behaviour": "vulnerable_expected_behaviour",
}


def _normalise_headings(doc: dict[str, str]) -> None:
    for src, dst in _HEADING_ALIASES.items():
        if doc.get(src) and not doc.get(dst):
            doc[dst] = doc[src]


def _owasp_id(title: str) -> str:
    m = re.search(r"(LLM\d{2})", title)
    return m.group(1) if m else ""


def _format_message(messages: list[dict[str, str]]) -> str:
    parts = []
    for msg in messages:
        parts.append(f"{IM_START}{msg['role']}\n{msg['content']}{IM_END}")
    parts.append(f"{IM_START}assistant\n")
    return "\n".join(parts)


def _make_raw(
    user_text: str,
    assistant_text: str,
    system: str = SYSTEM_PROMPT,
) -> dict[str, Any]:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": assistant_text},
    ]
    return {"messages": messages, "text": _format_message(messages)}


def _shorten(text: str, n: int = 200) -> str:
    return text[:n] + "..." if len(text) > n else text


def _build_ref(doc: dict[str, str], path: Path) -> str:
    return (
        f"Reference material ({path.name}):\n"
        f"Title: {doc.get('title', path.stem)}\n"
        f"Scope: {doc.get('scope', 'N/A')}\n"
        f"Secure behaviour: {doc.get('secure_expected_behaviour', 'N/A')}\n"
        f"Vulnerable behaviour: {doc.get('vulnerable_expected_behaviour', 'N/A')}\n"
        f"Evidence fields: {doc.get('required_evidence', 'N/A')}\n"
        f"Evaluators: {doc.get('evaluators', 'N/A')}\n"
        f"Severity rationale: {doc.get('severity_rationale', 'N/A')}\n"
        f"Working criteria: {doc.get('working_criteria', 'N/A')}"
    )


# ---------------------------------------------------------------------------
# Template generators — each returns 1-3 examples with varied phrasings
# ---------------------------------------------------------------------------

def explain_category(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    scope = doc.get("scope", "")
    vulnerable = doc.get("vulnerable_expected_behaviour", "")
    secure = doc.get("secure_expected_behaviour", "")
    severity = doc.get("severity_rationale", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"Explain this security category: what the weakness is, why it matters, "
            f"and what a reviewer should check.\n\nCategory: {title}\n\n{ref}",
            f"{title} is an AI/LLM security risk category from the OWASP LLM Top 10. "
            f"{scope}\n\n"
            f"A reviewer should check for: {_shorten(vulnerable, 400)}\n\n"
            f"The secure baseline requires: {_shorten(secure, 400)}\n\n"
            f"Severity assessment: {_shorten(severity, 300) if severity else 'Based on impact and context.'}"
        ),
        (
            f"What is {title} and how does it manifest in LLM applications?\n\n{ref}",
            f"{title} occurs when {_shorten(vulnerable, 500)}. "
            f"The security impact depends on deployment context. "
            f"Reviewers should verify that {_shorten(secure, 400)}. "
            f"This category is part of the OWASP LLM Top 10 framework used by VulnoraIQ."
        ),
        (
            f"Define {title} for a security engineer new to AI assessment.\n\n{ref}",
            f"{title} is a security risk category in the OWASP LLM Top 10 framework. "
            f"In scope: {_shorten(scope, 300)}. "
            f"The vulnerable pattern is: {_shorten(vulnerable, 400)}. "
            f"Secure operation requires: {_shorten(secure, 300)}. "
            f"Engineers should review evidence against these criteria and consult the OWASP documentation."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def mitigation_guidance(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    secure = doc.get("secure_expected_behaviour", "")
    evidence = doc.get("required_evidence", "")
    ref = _build_ref(doc, path)
    if not secure:
        return []
    variants = [
        (
            f"How should I mitigate {title} risks?\n\nFinding context: A finding in this category was reported.\n\n{ref}",
            f"To mitigate {title}:\n\n{secure[:600]}\n\n"
            f"Collect the following evidence: {_shorten(evidence, 300)}\n\n"
            f"Apply deterministic controls, preserve evidence, and verify with a human reviewer. "
            f"VulnoraIQ advises only; it does not change the target."
        ),
        (
            f"What controls should be in place to prevent {title}?\n\n{ref}",
            f"Effective controls for {title} include:\n{secure[:700]}\n\n"
            f"Required evidence: {_shorten(evidence, 300) if evidence else 'Follow the secure baseline documentation.'}\n\n"
            f"All controls should be validated by a human assessor before sign-off."
        ),
        (
            f"Design a mitigation plan for {title}.\n\nFinding context: A medium-severity finding was detected.\n\n{ref}",
            f"Mitigation plan for {title}:\n1. Apply secure baseline: {_shorten(secure, 400)}\n"
            f"2. Collect and preserve evidence: {_shorten(evidence, 200) if evidence else 'Per assessment policy.'}\n"
            f"3. Verify with a human reviewer.\n"
            f"4. Re-assess after remediation.\n"
            f"VulnoraIQ provides guidance; human verification is required before treating as resolved."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def vulnerable_behaviour(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    vulnerable = doc.get("vulnerable_expected_behaviour", "")
    ref = _build_ref(doc, path)
    if not vulnerable:
        return []
    variants = [
        (
            f"What are the signs of a vulnerable system for {title}?\n\nFinding context: A scan reported a potential finding.\n\n{ref}",
            f"A system is likely vulnerable to {title} when:\n{vulnerable[:600]}\n\n"
            f"Reviewers should examine the affected component against each of these indicators. "
            f"Not all indicators may apply; assess in the deployment context."
        ),
        (
            f"Describe a typical {title} vulnerability scenario in an LLM application.\n\n{ref}",
            f"A typical {title} vulnerability exhibits: {_shorten(vulnerable, 500)}. "
            f"This manifests when the application does not enforce {_shorten(doc.get('secure_expected_behaviour', 'expected security controls'), 200)}. "
            f"The assessor should capture evidence demonstrating the vulnerable behaviour and compare against the secure baseline."
        ),
        (
            f"List the red flags for {title} during an AI security review.\n\n{ref}",
            f"Red flags for {title} include:\n{vulnerable[:600]}\n\n"
            f"Any of these indicators warrants further investigation. "
            f"Document each observation with supporting evidence for human review."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def explain_finding(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    vulnerable = doc.get("vulnerable_expected_behaviour", "")
    secure = doc.get("secure_expected_behaviour", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            "Explain this security finding in 3-4 sentences for a reviewer.\n\n"
            f"Finding:\nTitle: {title} finding detected\nSeverity: medium\n"
            f"Status: open\nAffected component: LLM application endpoint\n\n{ref}",
            f"This finding relates to {title}. The weakness means the target application "
            f"may exhibit behaviours consistent with this OWASP category: {_shorten(vulnerable, 300)}. "
            f"This matters because exploitation could lead to security impact depending on "
            f"the deployment context and data sensitivity. A reviewer should check the "
            f"captured evidence against the secure baseline: {_shorten(secure, 300)}. "
            f"Manual review is required before treating this as confirmed."
        ),
        (
            f"Summarise this {title} finding for a technical report.\n\nFinding:\nTitle: {title}\n"
            f"Severity: high\nAffected component: LLM orchestrator\nStatus: under review\n\n{ref}",
            f"Finding summary — {title} (HIGH): The target system exhibits behaviour consistent with "
            f"{_shorten(vulnerable, 300)}. This finding was raised by the VulnoraIQ assessment framework. "
            f"Immediate human review is recommended. The secure baseline requires: {_shorten(secure, 300)}. "
            f"Evidence should be preserved for audit purposes."
        ),
        (
            f"Generate a finding description for {title} suitable for a client report.\n\n{ref}",
            f"Finding: {title}\nSeverity: To be determined by human reviewer\n"
            f"Description: The assessment observed potential {title} indicators. "
            f"Specifically, {_shorten(vulnerable, 400)}. "
            f"Recommended action: Apply the secure baseline ({_shorten(secure, 200)}), "
            f"collect evidence, and engage a human reviewer. VulnoraIQ finding — requires human validation."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def evidence_checklist(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    evidence = doc.get("required_evidence", "")
    evaluators = doc.get("evaluators", "")
    ref = _build_ref(doc, path)
    if not evidence:
        return []
    variants = [
        (
            f"What evidence should I collect when assessing {title}?\n\nFinding context: Planning an assessment scan.\n\n{ref}",
            f"When assessing {title}, collect the following evidence:\n{evidence[:600]}\n\n"
            f"Use VulnoraIQ's configured evaluators ({_shorten(evaluators, 200)}) to validate the evidence. "
            f"These fields ensure the finding is reproducible and reviewable."
        ),
        (
            f"Design an evidence collection checklist for a {title} assessment.\n\n{ref}",
            f"Evidence checklist for {title}:\n{evidence[:700]}\n\n"
            f"Evaluators: {_shorten(evaluators, 200) if evaluators else 'Configure per assessment policy.'}\n"
            f"Each evidence field should be captured, timestamped, and linked to the specific finding."
        ),
        (
            f"What format should evidence take for a {title} finding?\n\nFinding context: Preparing assessment templates.\n\n{ref}",
            f"Evidence for {title} should be captured in a structured format. "
            f"Required fields: {_shorten(evidence, 600)}\n\n"
            f"Each evidence record should include a timestamp, the target component identifier, "
            f"the evaluator that generated it, and a reference to the specific test case. "
            f"Use VulnoraIQ's structured output format for consistency across assessments."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def severity_rationale(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    severity = doc.get("severity_rationale", "")
    ref = _build_ref(doc, path)
    if not severity:
        return []
    variants = [
        (
            f"How should I prioritise a {title} finding?\n\nFinding context: A finding was detected.\n\n{ref}",
            f"{title} findings are prioritised as follows:\n{severity[:600]}\n\n"
            "Consider the deployment context, data sensitivity, and trust boundary "
            "when assigning priority. No automated severity replaces human risk assessment."
        ),
        (
            f"Explain the severity scoring for {title}.\n\n{ref}",
            f"Severity for {title}: {severity[:700]}\n\n"
            f"Priority should factor in exploitability, business impact, and data classification. "
            f"A human risk owner must validate the final severity rating."
        ),
        (
            f"When should I escalate a {title} finding to HIGH or CRITICAL?\n\nFinding context: Severity assessment for an open finding.\n\n{ref}",
            f"A {title} finding should be escalated to HIGH or CRITICAL when:\n"
            f"- The affected component handles sensitive data.\n"
            f"- The vulnerable behaviour is directly exploitable without authentication.\n"
            f"- The severity rationale indicates high impact: {_shorten(severity, 400) if severity else 'Based on CVSS scoring.'}\n"
            f"- A human reviewer confirms the evidence is strong.\n"
            f"Escalation triggers immediate human review and remediation planning."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def cve_lookup_behaviour(doc: dict[str, str], path: Path) -> list[dict]:
    """Teach the model to defer CVE facts to the live lookup, never to invent them.

    The previous ``cve_known`` generator baked placeholder CVE IDs (CVE-2024-XXXX)
    and made-up CVSS scores into the answers, which trains the assistant to
    hallucinate CVE records. CVE correlation must come from the runtime NVD/OSV
    lookup, so here we only train the *behaviour* of using that tool.
    """
    title = doc.get("title", path.stem)
    ref = _build_ref(doc, path)
    variants = [
        (
            f"Are there any known CVEs for {title}?\n\nFinding context: A finding was reported.\n\n{ref}",
            f"I do not carry a CVE database in memory, so I will not guess CVE IDs or CVSS scores "
            f"for {title}. Run the VulnoraIQ NVD/OSV lookup against the affected component and "
            f"version; if it returns records, I can help you correlate each one against the "
            f"captured evidence. Any CVE correlation is advisory and must be confirmed by a human "
            f"reviewer — a matching ID does not by itself prove the finding is exploitable here."
        ),
        (
            f"Check CVEs for {title} and summarise the findings.\n\n{ref}",
            f"CVE correlation for {title} should come from the live NVD/OSV lookup, not from model "
            f"recall — quoting a CVE number from memory risks inventing one. Provide the component "
            f"name and version to the lookup, then share the returned records and I will summarise "
            f"their relevance to your evidence. Where the lookup returns nothing, treat the finding "
            f"as a candidate novel issue requiring human verification rather than assuming no risk."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def cve_unknown(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    secure = doc.get("secure_expected_behaviour", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"Check if there is a known vulnerability for this component.\n\nFinding context: A finding was detected.\n\n{ref}\n\n"
            f"CVE lookup:\nNo matching public CVE found — candidate novel issue (human verification required).",
            f"The CVE lookup found no matching public records for this {title} finding. "
            f"This may indicate a configuration issue, a novel finding, or a gap in public CVE coverage. "
            f"Continue with the secure baseline assessment: {_shorten(secure, 300) if secure else 'Review evidence and apply controls.'}"
        ),
        (
            f"No CVEs were found for my {title} finding. What should I do?\n\n{ref}\n\n"
            f"CVE lookup: No results.",
            f"No matching CVEs does not mean no risk exists. For {title}, proceed with: "
            f"1. Manual evidence review against the OWASP criteria.\n"
            f"2. Check internal vulnerability databases.\n"
            f"3. Engage a human security assessor.\n"
            f"Absence of a public CVE is not proof of absence of a vulnerability."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def remediation_steps(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    secure = doc.get("secure_expected_behaviour", "")
    ref = _build_ref(doc, path)
    if not secure:
        return []
    variants = [
        (
            f"Provide step-by-step remediation guidance for {title}.\n\nFinding context: A confirmed finding needs remediation.\n\n{ref}",
            f"Remediation steps for {title}:\n\n"
            f"1. Review the finding evidence and confirm applicability.\n"
            f"2. Apply secure configuration: {_shorten(secure, 500)}\n"
            f"3. Collect fresh evidence showing the control is effective.\n"
            f"4. Escalate to a human reviewer for sign-off.\n"
            f"5. Document the remediation in the assessment report.\n\n"
            f"VulnoraIQ provides advisory guidance; all remediation must be validated by a human."
        ),
        (
            f"Walk me through fixing a {title} vulnerability.\n\nFinding context: open finding, waiting on remediation.\n\n{ref}",
            f"To address {title}:\nStep 1 — Verify the finding by reviewing captured evidence.\n"
            f"Step 2 — Implement the secure baseline: {_shorten(secure, 500)}\n"
            f"Step 3 — Re-run assessment to verify the control.\n"
            f"Step 4 — Human reviewer validates and closes the finding.\n"
            f"Retain all evidence for compliance records."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def test_case_writing(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    vulnerable = doc.get("vulnerable_expected_behaviour", "")
    secure = doc.get("secure_expected_behaviour", "")
    evidence = doc.get("required_evidence", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"How do I write a security test case for {title}?\n\nFinding context: Creating assessment profiles.\n\n{ref}",
            f"Test case for {title}:\n"
            f"1. Verify the absence of: {_shorten(vulnerable, 400)}\n"
            f"2. Confirm the presence of: {_shorten(secure, 300)}\n"
            f"3. Capture evidence: {_shorten(evidence, 300) if evidence else 'Per category requirements.'}\n"
            f"Use VulnoraIQ evaluators to automate evidence collection where possible."
        ),
        (
            f"Design a penetration test scenario for {title}.\n\n{ref}",
            f"Penetration test scenario for {title}:\n"
            f"Goal: Determine if the target exhibits {_shorten(vulnerable, 300)}.\n"
            f"Expected secure behaviour: {_shorten(secure, 300) if secure else 'OWASP-defined controls are in place.'}\n"
            f"Evidence fields: {_shorten(evidence, 200) if evidence else 'Prompt-response pairs, system logs.'}\n"
            f"The tester should document all findings with reproducible steps."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def false_positive_analysis(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    vulnerable = doc.get("vulnerable_expected_behaviour", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"How can I tell if a {title} finding is a false positive?\n\nFinding context: A finding was flagged as potential false positive.\n\n{ref}",
            f"To assess whether a {title} finding is a false positive:\n"
            f"1. Review the captured evidence against {_shorten(vulnerable, 400)}.\n"
            f"2. Check if the vulnerable behaviour was actually triggered.\n"
            f"3. Verify the target's security controls were active during the test.\n"
            f"4. Consult a human reviewer.\n\n"
            f"VulnoraIQ flags conditions for review; false positives are expected and should be documented."
        ),
        (
            f"My {title} finding might be a false positive. How do I confirm?\n\n{ref}",
            f"To confirm or dismiss a suspected false positive for {title}:\n"
            f"- Re-examine the test output against the OWASP working criteria.\n"
            f"- Check if the target application was in a known-good state.\n"
            f"- Compare with the secure baseline.\n"
            f"- If the evidence does not match the vulnerable pattern, mark as false positive with a note.\n"
            f"Document all false positives for assessment quality metrics."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def cross_category_comparison(doc: dict[str, str], path: Path, all_docs: list[tuple[dict, Path]]) -> list[dict]:
    title = doc.get("title", path.stem)
    ref = _build_ref(doc, path)
    peers = [(d, p) for d, p in all_docs if d.get("title") != title]
    if not peers:
        return []
    other_doc, other_path = random.choice(peers)
    other_title = other_doc.get("title", other_path.stem)
    other_ref = _build_ref(other_doc, other_path)
    variants = [
        (
            f"How does {title} differ from {other_title}?\n\n{ref}\n\n{other_ref}",
            f"{title} and {other_title} are both OWASP LLM security categories but address different risks. "
            f"{title} focuses on: {_shorten(doc.get('scope', ''), 300)}. "
            f"{other_title} focuses on: {_shorten(other_doc.get('scope', ''), 300)}. "
            f"A comprehensive assessment should evaluate both categories independently."
        ),
        (
            f"Compare and contrast {title} vs {other_title} for a security review.\n\n{ref}\n\n{other_ref}",
            f"Comparing {title} and {other_title}:\n"
            f"- {title}: {_shorten(doc.get('vulnerable_expected_behaviour', ''), 300)}\n"
            f"- {other_title}: {_shorten(other_doc.get('vulnerable_expected_behaviour', ''), 300)}\n"
            f"Both should be assessed, but they require different evidence and evaluators. "
            f"Consult the respective OWASP documentation for each."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def compliance_reporting(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    criteria = doc.get("working_criteria", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"How should I report a {title} finding for compliance purposes?\n\nFinding context: A compliance audit is in progress.\n\n{ref}",
            f"To report a {title} finding for compliance:\n"
            f"1. State the OWASP category and assessment date.\n"
            f"2. Describe the vulnerable behaviour observed.\n"
            f"3. Reference the working criteria: {_shorten(criteria, 300) if criteria else 'N/A'}\n"
            f"4. Include the secure baseline as the expected state.\n"
            f"5. Note that the finding requires human validation.\n"
            f"Use VulnoraIQ's report templates where available."
        ),
        (
            f"Draft a compliance note for a {title} assessment finding.\n\n{ref}",
            f"Compliance note — {title}:\n"
            f"This finding was raised by the VulnoraIQ automated assessment framework using OWASP LLM Top 10 criteria. "
            f"It indicates that the target exhibited behaviour consistent with {_shorten(doc.get('vulnerable_expected_behaviour', ''), 300)}. "
            f"The finding is advisory and requires human verification before inclusion in compliance reporting."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def evidence_interpretation(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    evidence = doc.get("required_evidence", "")
    evaluators = doc.get("evaluators", "")
    criteria = doc.get("working_criteria", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"Interpret this evidence for a {title} finding.\n\nCaptured evidence: Prompt injection payload 'Ignore previous instructions' triggered unexpected output.\n\n{ref}",
            f"For {title}, the captured evidence shows a prompt manipulation attempt. "
            f"The evidence field expected: {_shorten(evidence, 400) if evidence else 'Prompt-response pairs'}. "
            f"Evaluators ({_shorten(evaluators, 200) if evaluators else 'Configured assessors'}) should validate this against the working criteria. "
            f"Human review is required to determine if this constitutes a confirmed finding."
        ),
        (
            f"Walk me through evaluating evidence for a {title} detection.\n\n{ref}",
            f"Evaluating {title} evidence:\n1. Check that the evidence matches the required fields: {_shorten(evidence, 300) if evidence else 'Per OWASP spec.'}\n"
            f"2. Apply the working criteria: {_shorten(criteria, 300) if criteria else 'N/A'}\n"
            f"3. Run evaluators to confirm the finding.\n"
            f"4. Document the evaluation outcome for the human reviewer.\n"
            f"Evidence that does not clearly match the vulnerable pattern should be marked for review."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def tool_configuration(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    evaluators = doc.get("evaluators", "")
    criteria = doc.get("working_criteria", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"How do I configure VulnoraIQ to assess {title}?\n\nFinding context: Setting up a new assessment profile.\n\n{ref}",
            f"To configure VulnoraIQ for {title}:\n"
            f"1. Ensure the OWASP profile includes the {title} category.\n"
            f"2. Configure evaluators: {_shorten(evaluators, 300) if evaluators else 'Use defaults.'}\n"
            f"3. Set working criteria: {_shorten(criteria, 300) if criteria else 'OWASP standard.'}\n"
            f"4. Run a test scan to validate the configuration.\n"
            f"Review the VulnoraIQ documentation for profile management details."
        ),
        (
            f"Select the right evaluators for a {title} assessment.\n\n{ref}",
            f"For {title}, suitable evaluators include: {_shorten(evaluators, 400) if evaluators else 'Heuristic and LLM-based evaluators configured for this OWASP category.'}\n"
            f"The working criteria to apply: {_shorten(criteria, 300) if criteria else 'Per assessment policy.'}\n"
            f"Consider the deployment context when selecting evaluator sensitivity."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def risk_scenario(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    vulnerable = doc.get("vulnerable_expected_behaviour", "")
    secure = doc.get("secure_expected_behaviour", "")
    severity = doc.get("severity_rationale", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"Describe a realistic risk scenario for {title}.\n\nFinding context: Risk assessment for an LLM-powered chatbot.\n\n{ref}",
            f"Risk scenario — {title}:\n"
            f"An LLM-powered customer service chatbot is deployed with internet-facing access. "
            f"If vulnerable, an attacker could exploit {_shorten(vulnerable, 400)}. "
            f"The impact includes data exposure, reputational damage, and regulatory penalties. "
            f"Secure baseline: {_shorten(secure, 300)}. "
            f"Severity: {_shorten(severity, 200) if severity else 'Medium-High depending on data sensitivity.'}"
        ),
        (
            f"Build a threat model entry for {title}.\n\n{ref}",
            f"Threat model entry — {title}:\n"
            f"Threat: Exploitation of {_shorten(vulnerable, 400)}.\n"
            f"Attack vector: Prompt/input manipulation by malicious user.\n"
            f"Controls: {_shorten(secure, 300) if secure else 'Input validation, output filtering, access controls.'}\n"
            f"Risk: {_shorten(severity, 200) if severity else 'Assess per deployment.'}\n"
            f"Mitigation: Apply OWASP-recommended controls and verify with VulnoraIQ."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def post_remediation_check(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    secure = doc.get("secure_expected_behaviour", "")
    evidence = doc.get("required_evidence", "")
    ref = _build_ref(doc, path)
    if not secure:
        return []
    variants = [
        (
            f"How do I verify that a {title} remediation was successful?\n\nFinding context: Remediation was applied, need to verify.\n\n{ref}",
            f"To verify {title} remediation:\n"
            f"1. Re-run the VulnoraIQ assessment for this category.\n"
            f"2. Check that {_shorten(secure, 400)} is now observed.\n"
            f"3. Collect fresh evidence: {_shorten(evidence, 300) if evidence else 'Per assessment profile.'}\n"
            f"4. Have a human reviewer confirm the control is effective.\n"
            f"Document the verification in the assessment report."
        ),
        (
            f"Post-remediation validation steps for {title}.\n\n{ref}",
            f"Post-remediation validation for {title}:\n"
            f"- Confirm the secure baseline is enforced: {_shorten(secure, 400)}\n"
            f"- Verify evidence fields are populated: {_shorten(evidence, 200) if evidence else 'N/A'}\n"
            f"- Run evaluators to confirm the finding is resolved.\n"
            f"- Escalate for human sign-off.\n"
            f"Re-open if the control proves ineffective under further testing."
        ),
        (
            f"How long should I wait before re-testing after {title} remediation?\n\nFinding context: Remediation applied, scheduling re-assessment.\n\n{ref}",
            f"After applying remediation for {title}, re-testing should occur:\n"
            f"- Immediately if the control is a configuration change (can be verified right away).\n"
            f"- Within one assessment cycle for code or architecture changes.\n"
            f"- After the change has been deployed to the test environment.\n"
            f"Always document the remediation date and re-test date in the assessment report."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


# ---------------------------------------------------------------------------
# Assurance document examples
# ---------------------------------------------------------------------------

def generate_assurance_examples() -> list[dict]:
    text = ASSURANCE_FILE.read_text(encoding="utf-8")
    ref_short = f"Reference material (ASSESSMENT_ASSURANCE.md):\n{text[:1500]}"
    ref_long = f"Reference material (ASSESSMENT_ASSURANCE.md):\n{text[:2000]}"
    return [
        _make_raw(
            "What is the assurance boundary of a VulnoraIQ finding?\n\n" + ref_short,
            "VulnoraIQ findings are framework evidence requiring human review, not certified "
            "VAPT-grade assurance. Findings show that a configured profile observed a condition "
            "worth review, but a human tester must review target scope, evidence, logs, "
            "environmental context, and remediation before treating a finding as confirmed. "
            "False positives and false negatives are expected."
        ),
        _make_raw(
            "What does a VulnoraIQ finding mean?\n\n" + ref_short,
            "A VulnoraIQ finding indicates that a configured profile, payload, target adapter, "
            "evaluator, oracle, and policy path observed a condition worth review. It is not "
            "a certified vulnerability confirmation. False positives are expected where "
            "heuristic checks or synthetic scenario assumptions do not match the environment."
        ),
        _make_raw(
            "How should I interpret CVSS scores in scan results?\n\n" + ref_long,
            "CVSS scores range from 0.0 to 10.0 and fall into bands: CRITICAL (9.0-10.0) and "
            "HIGH (7.0-8.9) indicate severe risk requiring immediate human review; MEDIUM "
            "(4.0-6.9) and LOW (0.1-3.9) should be assessed in deployment context. The band is "
            "only a starting point — weigh exploitability, the affected component's exposure, and "
            "data sensitivity before prioritising. I read CVSS values from the live NVD/OSV "
            "lookup rather than recalling them, and I will not invent a score for a finding. "
            "CVE correlation is advisory; a human must validate that a scored CVE actually "
            "applies to your target."
        ),
        _make_raw(
            "Can VulnoraIQ findings be used in a compliance audit?\n\n" + ref_long,
            "VulnoraIQ findings can support compliance reporting but do not constitute "
            "certified audit evidence on their own. Each finding requires human validation "
            "before inclusion in compliance documentation. The evidence captured by VulnoraIQ "
            "provides a starting point for the auditor's investigation."
        ),
        _make_raw(
            "Explain the assessment profile and oracle architecture.\n\n" + ref_long,
            "VulnoraIQ uses a profile-driven architecture: a profile defines payloads, "
            "target adapters, evaluators, oracles, and policy paths. The oracle is the "
            "decision function that evaluates evidence against working criteria. "
            "This architecture enables repeatable, configurable assessments across different "
            "LLM application types and deployment contexts."
        ),
        _make_raw(
            "How are evaluators configured?\n\n" + ref_short,
            "Evaluators in VulnoraIQ are pluggable components that analyse captured evidence. "
            "They can be heuristic (pattern matching) or LLM-based (semantic analysis). "
            "Configuration involves specifying which evidence fields to evaluate and "
            "setting sensitivity thresholds. Refer to the VulnoraIQ evaluator documentation."
        ),
        _make_raw(
            "What is the difference between a heuristic and an LLM-based evaluator?\n\n" + ref_short,
            "Heuristic evaluators use pattern matching rules to detect known vulnerability indicators. "
            "They are fast, deterministic, and suitable for well-defined categories. "
            "LLM-based evaluators use a language model to semantically analyse evidence, "
            "which can detect novel or subtle patterns that heuristics might miss. "
            "Both types have trade-offs: heuristics are precise but limited, LLM-based "
            "evaluators are flexible but may produce false positives."
        ),
        _make_raw(
            "How should I set evaluator sensitivity?\n\n" + ref_short,
            "Evaluator sensitivity should be set based on the assessment context. "
            "For initial discovery scans, higher sensitivity (more aggressive detection) "
            "is recommended to minimise false negatives. For verification scans after "
            "remediation, standard sensitivity is sufficient. "
            "Document the sensitivity setting in the assessment report for reproducibility."
        ),
    ]


def finding_triage(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    vulnerable = doc.get("vulnerable_expected_behaviour", "")
    severity = doc.get("severity_rationale", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"How do I triage a {title} finding? What steps should I follow?\n\nFinding context: New finding needs triage.\n\n{ref}",
            f"Triage steps for {title}:\n"
            f"1. Review the captured evidence — does it match {_shorten(vulnerable, 400)}?\n"
            f"2. Assign provisional severity: {_shorten(severity, 300) if severity else 'Based on impact and likelihood.'}\n"
            f"3. Check if this finding duplicates an existing one.\n"
            f"4. Escalate to a human reviewer with all supporting evidence.\n"
            f"Triage is preliminary; a human makes the final call."
        ),
        (
            f"What priority should I assign to an open {title} finding?\n\nFinding context: Multiple findings need prioritisation.\n\n{ref}",
            f"Priority for {title} depends on:\n"
            f"- Evidence strength: Does it clearly show {_shorten(vulnerable, 300)}?\n"
            f"- Severity rationale: {_shorten(severity, 300) if severity else 'Default based on OWASP guidelines.'}\n"
            f"- Deployment context: Is the affected component internet-facing or internal?\n"
            f"- Data sensitivity: What data does the component handle?\n"
            f"Combine these factors; no automated priority replaces human risk assessment."
        ),
        (
            f"I have a backlog of {title} findings. How do I handle them?\n\n{ref}",
            f"Handling a backlog of {title} findings:\n"
            f"1. Batch by severity — address HIGH/CRITICAL first.\n"
            f"2. Check for duplicate or related findings.\n"
            f"3. Verify each against {_shorten(vulnerable, 300)}.\n"
            f"4. Assign to a human reviewer with context from the OWASP documentation.\n"
            f"5. Track resolution status in your assessment report."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def assessment_planning(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    scope = doc.get("scope", "")
    criteria = doc.get("working_criteria", "")
    vulnerable = doc.get("vulnerable_expected_behaviour", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"Plan an assessment for {title}. What do I need to prepare?\n\nFinding context: Starting a new assessment project.\n\n{ref}",
            f"Assessment plan for {title}:\n"
            f"1. Scope: {_shorten(scope, 400) if scope else 'Define the target LLM application.'}\n"
            f"2. Configure VulnoraIQ with the OWASP profile for this category.\n"
            f"3. Prepare test payloads targeting {_shorten(scope or title, 200)}.\n"
            f"4. Set evaluators and working criteria: {_shorten(criteria, 300) if criteria else 'Use defaults.'}\n"
            f"5. Execute the assessment and capture evidence.\n"
            f"6. Review results with a human assessor."
        ),
        (
            f"What resources do I need to assess {title} in my organisation?\n\n{ref}",
            f"Resources needed for {title} assessment:\n"
            f"- A configured VulnoraIQ instance with the OWASP LLM profile.\n"
            f"- Access to the target LLM application for testing.\n"
            f"- A human security reviewer familiar with OWASP LLM categories.\n"
            f"- Documentation of scope and trust boundaries: {_shorten(scope, 300) if scope else 'Per organisational policy.'}\n"
            f"- Time allocation for evidence review and reporting."
        ),
        (
            f"Design a test matrix for {title} covering different attack vectors.\n\n{ref}",
            f"Test matrix for {title}:\n"
            f"Attack vectors to test:\n"
            f"- Direct exploitation of {_shorten(vulnerable, 300)} (vulnerable behaviour)\n"
            f"- Bypass of {_shorten(doc.get('secure_expected_behaviour', 'defined controls'), 200)}\n"
            f"- Edge cases in input/output handling\n"
            f"Expected evidence: {_shorten(doc.get('required_evidence', 'Prompt-response pairs, system logs'), 200)}\n"
            f"Each test should be repeatable and documented."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def payload_design(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    vulnerable = doc.get("vulnerable_expected_behaviour", "")
    oid = _owasp_id(title)
    ref = _build_ref(doc, path)
    variants = [
        (
            f"What test payloads should I use for {title}?\n\nFinding context: Configuring assessment payload profiles.\n\n{ref}",
            f"For {title}, use payloads that trigger {_shorten(vulnerable, 500)}. "
            f"Examples include adversarial inputs designed to elicit the vulnerable behaviour "
            f"described in the OWASP {oid} specification. "
            f"VulnoraIQ includes pre-configured payloads for this category in its OWASP profile. "
            f"Review and customise payloads to match your target application."
        ),
        (
            f"Design adversarial inputs for testing {title}.\n\n{ref}",
            f"Adversarial inputs for {title} should target {_shorten(vulnerable, 500)}. "
            f"Each input should:\n"
            f"- Be reproducible with a clear expected outcome.\n"
            f"- Include variations that test edge cases.\n"
            f"- Be paired with the expected secure behaviour for comparison.\n"
            f"Use VulnoraIQ's payload management to organise test cases."
        ),
        (
            f"Give me 3 example test cases for {title}.\n\n{ref}",
            f"Example test cases for {title}:\n"
            f"1. Test A: Verify that {_shorten(vulnerable, 200)} is detected.\n"
            f"2. Test B: Confirm the control ({_shorten(doc.get('secure_expected_behaviour', 'secure baseline'), 200)}) prevents exploitation.\n"
            f"3. Test C: Edge case — partial or obfuscated attempt at exploitation.\n"
            f"Document each test case with the expected outcome and pass/fail criteria."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def knowledge_integration(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    ref = _build_ref(doc, path)
    variants = [
        (
            f"How does {title} relate to other security frameworks like MITRE ATT&CK?\n\n{ref}",
            f"{title} is part of the OWASP LLM Top 10 framework. While it addresses AI-specific risks, "
            f"it can be mapped to broader frameworks like MITRE ATT&CK for enterprise assessment. "
            f"The vulnerable behaviour in {title} often corresponds to MITRE techniques in the "
            f"initial access or execution categories. Use the OWASP-to-MITRE crosswalk "
            f"documentation for detailed mappings."
        ),
        (
            f"Can {title} findings be integrated with SIEM or SOAR platforms?\n\n{ref}",
            f"Yes, {title} findings from VulnoraIQ can be exported and integrated with SIEM/SOAR platforms. "
            f"The finding output includes structured evidence fields that map to common security event formats. "
            f"Consult VulnoraIQ's integration documentation for specific platform connectors. "
            f"Automated responses should always require human approval before action."
        ),
        (
            f"How do I add {title} to my existing security testing pipeline?\n\n{ref}",
            f"To integrate {title} into your pipeline:\n"
            f"1. Add the OWASP LLM profile to your VulnoraIQ configuration.\n"
            f"2. Schedule regular assessments targeting LLM components.\n"
            f"3. Configure webhook or API-based output for CI/CD integration.\n"
            f"4. Set up notification thresholds for findings requiring immediate review.\n"
            f"5. Include findings in your quarterly security review process."
        ),
        (
            f"Train a new team member on {title} assessment.\n\n{ref}",
            f"Training guide for {title}:\n"
            f"1. Read the OWASP LLM Top 10 documentation for this category.\n"
            f"2. Understand the vulnerable and secure behaviours.\n"
            f"3. Observe a live assessment using VulnoraIQ.\n"
            f"4. Review past findings and their resolution.\n"
            f"5. Conduct a supervised assessment with a senior reviewer.\n"
            f"6. Document lessons learned."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def multi_turn_conversation(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    vulnerable = doc.get("vulnerable_expected_behaviour", "")
    secure = doc.get("secure_expected_behaviour", "")
    severity = doc.get("severity_rationale", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"I found a {title} issue. What should I do first?\n\n{ref}",
            f"First, preserve the evidence showing {_shorten(vulnerable, 400)}. "
            f"Then check the secure baseline ({_shorten(secure, 300)}) to understand the expected behaviour. "
            f"Assign a provisional severity ({_shorten(severity, 200) if severity else 'per your assessment policy'}) "
            f"and escalate to a human reviewer. Do not attempt to fix the target before evidence is captured."
        ),
        (
            f"Follow-up: I need more details on the {title} mitigation.\n\n"
            f"I captured the evidence but the controls are unclear.\n\n{ref}",
            f"For mitigating {title}:\n"
            f"Review the secure baseline carefully: {_shorten(secure, 400)}\n"
            f"Ensure each control is implemented correctly.\n"
            f"If controls are unclear, consult the OWASP documentation or escalate to a security architect. "
            f"VulnoraIQ provides reference material; implementation decisions require human expertise."
        ),
        (
            f"Follow-up: The {title} finding was marked resolved. How do I verify?\n\n{ref}",
            f"To verify resolution of {title}:\n"
            f"1. Re-run the assessment for this category.\n"
            f"2. Confirm the vulnerable behaviour ({_shorten(vulnerable, 300)}) is no longer observed.\n"
            f"3. Check that {_shorten(secure, 300)} is now in place.\n"
            f"4. Have a human reviewer sign off.\n"
            f"Document the verification in the assessment report."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def report_generation(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    vulnerable = doc.get("vulnerable_expected_behaviour", "")
    secure = doc.get("secure_expected_behaviour", "")
    criteria = doc.get("working_criteria", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"Generate an executive summary for {title} findings.\n\nFinding context: Quarterly security review.\n\n{ref}",
            f"Executive summary — {title}:\n"
            f"During the assessment period, potential {title} indicators were observed. "
            f"These relate to {_shorten(vulnerable, 300)}. "
            f"The recommended secure state is: {_shorten(secure, 300)}. "
            f"Findings in this category require human review and validation. "
            f"VulnoraIQ provides evidence-based assessment; it does not replace human judgment."
        ),
        (
            f"Write a technical finding entry for {title}.\n\n{ref}",
            f"Technical finding — {title}:\n"
            f"OWASP category: {title}\n"
            f"Vulnerable pattern: {_shorten(vulnerable, 400)}\n"
            f"Expected secure state: {_shorten(secure, 300) if secure else 'Per OWASP specification.'}\n"
            f"Working criteria: {_shorten(criteria, 300) if criteria else 'OWASP-defined.'}\n"
            f"Evidence: Capture prompt-response pairs, system logs, and evaluator output.\n"
            f"Status: Requires human review."
        ),
        (
            f"Create a remediation tracking entry for {title}.\n\n{ref}",
            f"Remediation tracking — {title}:\n"
            f"Finding: {title} detected in LLM application.\n"
            f"Severity: As assigned by human reviewer.\n"
            f"Remediation: Apply {_shorten(secure, 400)} and re-assess.\n"
            f"Verification: Re-run VulnoraIQ assessment after remediation.\n"
            f"Status: Open — awaiting human review."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


def vulnerability_deep_dive(doc: dict[str, str], path: Path) -> list[dict]:
    title = doc.get("title", path.stem)
    scope = doc.get("scope", "")
    vulnerable = doc.get("vulnerable_expected_behaviour", "")
    secure = doc.get("secure_expected_behaviour", "")
    evidence = doc.get("required_evidence", "")
    criteria = doc.get("working_criteria", "")
    ref = _build_ref(doc, path)
    variants = [
        (
            f"Explain the root cause of {title} in technical detail.\n\n{ref}",
            f"Root cause of {title}:\n"
            f"The vulnerability arises when {_shorten(vulnerable, 500)}. "
            f"Technically, {_shorten(scope, 400) if scope else 'the LLM application'} lacks controls "
            f"to prevent this class of attack. "
            f"The root cause is typically inadequate {_shorten(criteria, 300) if criteria else 'input validation or output handling.'} "
            f"Mitigation requires addressing these technical gaps."
        ),
        (
            f"What are the technical indicators of {title} compromise?\n\n{ref}",
            f"Technical indicators for {title}:\n"
            f"- Evidence fields to check: {_shorten(evidence, 400) if evidence else 'Prompt-response pairs showing unusual patterns.'}\n"
            f"- Working criteria violations: {_shorten(criteria, 300) if criteria else 'Deviations from expected behaviour.'}\n"
            f"- Comparison with secure baseline: {_shorten(secure, 300) if secure else 'Controls are absent or bypassed.'}\n"
            f"Each indicator should be documented with supporting evidence."
        ),
        (
            f"Describe the attack chain for a {title} exploitation.\n\n{ref}",
            f"Attack chain for {title}:\n"
            f"1. Attacker crafts input targeting {_shorten(vulnerable, 300)}.\n"
            f"2. LLM processes the input without adequate controls ({_shorten(secure, 200)} is missing or bypassed).\n"
            f"3. Evidence of exploitation is captured in the relevant evidence fields.\n"
            f"4. Impact depends on the deployment context and data sensitivity.\n"
            f"Understanding the attack chain helps design effective mitigations."
        ),
    ]
    return [_make_raw(u, a) for u, a in variants]


# ---------------------------------------------------------------------------
# Assemble all generators
# ---------------------------------------------------------------------------

OWASP_GENERATORS: list[Callable[..., list[dict]]] = [
    explain_category,
    mitigation_guidance,
    vulnerable_behaviour,
    explain_finding,
    evidence_checklist,
    severity_rationale,
    cve_lookup_behaviour,
    cve_unknown,
    remediation_steps,
    test_case_writing,
    false_positive_analysis,
    compliance_reporting,
    evidence_interpretation,
    tool_configuration,
    risk_scenario,
    post_remediation_check,
    finding_triage,
    assessment_planning,
    payload_design,
    knowledge_integration,
    multi_turn_conversation,
    report_generation,
    vulnerability_deep_dive,
]


def main() -> None:
    doc_dir = DOCS_DIR
    if not doc_dir.is_dir():
        print(f"Docs directory not found: {doc_dir}", file=sys.stderr)
        sys.exit(1)

    files = sorted(doc_dir.glob("LLM*.md"))
    if not files:
        print(f"No LLM docs found in {doc_dir}", file=sys.stderr)
        sys.exit(1)

    docs: list[tuple[dict, Path]] = []
    for path in files:
        doc = _parse_doc(path)
        _normalise_headings(doc)
        docs.append((doc, path))

    all_examples: list[dict] = []

    for doc, path in docs:
        title = doc.get("title", path.stem)
        count_before = len(all_examples)
        for gen in OWASP_GENERATORS:
            if gen.__name__ == "cross_category_comparison":
                exs = gen(doc, path, docs)
            else:
                exs = gen(doc, path)
            all_examples.extend(exs)
        count_after = len(all_examples)
        print(f"  {path.name} ({title}): {count_after - count_before} examples")

    asr = generate_assurance_examples()
    all_examples.extend(asr)
    print(f"  ASSESSMENT_ASSURANCE.md: {len(asr)} examples")

    seen = set()
    deduped = []
    for ex in all_examples:
        key = json.dumps(ex["messages"], ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            deduped.append(ex)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for ex in deduped:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"\nTotal examples generated: {len(deduped)}")
    print(f"Dataset written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
