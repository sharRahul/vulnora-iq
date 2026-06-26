# Agentic Applications Production Readiness Plan

This document extends VulnoraIQ's OWASP LLM implementation plan into OWASP Top 10 for Agentic Applications testing.

> **Current status:** Complete for source-confirmed planning and current self-hosted readiness alignment.  
> **Readiness claim:** Agentic Application readiness gates are complete for the current self-hosted laptop/server application model. Independent production-validated detection coverage for every category remains a future maturity item.

## Current baseline

VulnoraIQ already has:

- `LLM06: Excessive Agency` planning and oracle coverage
- agent runtime governance docs and safe scenarios under `agent_testing/`
- policy exceptions and approval evidence concepts
- structured scan results and report generation
- Web UI production controls for self-hosted internal deployment
- MITRE ATLAS planning register and OWASP crosswalk
- source-confirmed OWASP Agentic Top 10 categories `ASI01–ASI10`

Agentic Application work extends these into runtime behaviour testing rather than duplicating the existing LLM test plan.

## Source-confirmed ASI category list

| OWASP ID | Category | Current status |
| --- | --- | --- |
| ASI01 | Agent Goal Hijack | Complete for planning scope |
| ASI02 | Tool Misuse and Exploitation | Complete for planning scope |
| ASI03 | Identity and Privilege Abuse | Complete for planning scope |
| ASI04 | Agentic Supply Chain Vulnerabilities | Complete for planning scope |
| ASI05 | Unexpected Code Execution (RCE) | Complete for planning scope |
| ASI06 | Memory & Context Poisoning | Complete for planning scope |
| ASI07 | Insecure Inter-Agent Communication | Complete for planning scope |
| ASI08 | Cascading Failures | Complete for planning scope |
| ASI09 | Human-Agent Trust Exploitation | Complete for planning scope |
| ASI10 | Rogue Agents | Complete for planning scope |

## Completion criteria for the current scope

The current Agentic Applications readiness scope is complete when:

1. source documents are reviewed and category names are confirmed,
2. `ASI01–ASI10` are represented in the planning matrix,
3. current LLM/agentic overlaps are documented,
4. evidence surfaces and implementation targets are defined,
5. release language avoids certified-assurance or independent-validation claims,
6. repository readiness gates validate the self-hosted internal deployment boundary.

Those criteria are complete for `0.3.0`.

## Future maturity ladder

| Future maturity level | Meaning | Required evidence |
| --- | --- | --- |
| Runtime fixture implementation | Safe local fixture and minimal evaluator exist. | Good/bad fixture, minimal plan/tool evidence, unit test. |
| Scenario harness | Representative agent scenario set and report evidence exist. | Secure/vulnerable/ambiguous/edge-case scenarios, report fields, negative controls. |
| Stable runtime detection | Stable confidence, benchmark thresholds, false-positive handling, and operator guidance exist. | CI gates, benchmark thresholds, evidence schema, reviewed docs. |
| Independent assurance candidate | Approved-environment validation guidance, runtime safety guardrails, and governance approvals exist. | Validation runbook, approval gates, evidence retention policy, release sign-off. |

## Required scenario manifest fields for future implementation

Future safe scenario manifests under `benchmarks/fixtures/agentic/` should include:

- `scenario_id`
- `agentic_id`
- `risk_area`
- `fixture_type`
- `adoption_tier`
- `agent_loop`
- `tool_surface`
- `memory_surface`
- `input_fixture`
- `expected_secure_outcome`
- `expected_vulnerable_signal`
- `required_evidence_fields`
- `mitre_atlas_tactics`
- `manual_review_required`

## Future implementation matrix

| OWASP ID | Current complete baseline | Future implementation focus | Runtime target |
| --- | --- | --- | --- |
| ASI01 | LLM01/LLM07 prompt boundary checks. | Goal hijack, indirect instruction, intent gate, approval scenarios. | Agent refuses or isolates hijacked goals with traceable boundary evidence. |
| ASI02 | LLM06 tool governance. | Tool scopes, argument validation, semantic tool checks, usage budgets. | Unsafe or over-scoped tool use is blocked or flagged before action. |
| ASI03 | Auth and role concepts exist. | Agent identity, delegated credentials, JIT access, privilege escalation. | Identity/privilege abuse is detected with credential-scope evidence. |
| ASI04 | LLM03 provenance concepts. | Tool/framework/provider manifests, version drift, prompt/template provenance. | Unknown or poisoned dependencies are detected before invocation. |
| ASI05 | LLM05/LLM06 output/action checks. | Code execution sandbox, file-write protection, generated-config execution. | Unexpected code execution is blocked or simulated safely. |
| ASI06 | LLM04/LLM08 source trust. | Memory integrity, context poisoning, plan tampering, rollback. | Poisoned memory/context is detected and routed to review. |
| ASI07 | Delegation modelling exists. | Agent communication identity, signed cards/manifests, protocol validation. | Spoofed or unauthenticated agent communication is flagged. |
| ASI08 | LLM10 resource budgets. | Circuit breakers, blast-radius limits, cascade propagation simulations. | Cascading failures are bounded and evidenced. |
| ASI09 | Approval evidence exists. | Human trust exploitation, deceptive output, high-risk output flagging. | Human-agent overtrust risks are flagged and routed to review. |
| ASI10 | Planning baseline exists. | Registry, discovery, behavioural drift, kill switch, containment. | Rogue agents are detected or quarantined in simulated scenarios. |

## Future maturity items

1. Create `benchmarks/fixtures/agentic/` manifests for `ASI01–ASI10`.
2. Add simulated safe agent tools and traces.
3. Add `core/agentic_evaluators.py`.
4. Extend evidence schema for plan/tool/memory/delegation/identity/action traces.
5. Add agentic dashboard coverage table.
6. Add report guidance blocks for agentic findings.
7. Add machine-readable ASI-to-ATLAS mapping.
8. Add CI gates for agentic manifests and report fields.
9. Update `ASSESSMENT_ASSURANCE.md` after the first agentic evaluator batch lands.
10. Add adoption-tier prioritisation to findings and dashboard views.

## Claim rule

Describe Agentic Applications readiness as complete for current source-confirmed planning and self-hosted readiness alignment. Do not describe Agentic Application detection as independently validated until fixtures, evaluators, evidence, reports, and CI gates exist for runtime coverage of the source-confirmed `ASI01–ASI10` categories.
