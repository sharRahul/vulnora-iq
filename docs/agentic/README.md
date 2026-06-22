# Agentic Applications Security Implementation Plan

This folder defines VulnoraIQ's implementation plan for OWASP Agentic Applications testing.

> **Status:** planning.  
> **Scope:** AI agents, tool use, planning, memory, delegation, inter-agent workflows, and runtime governance.  
> **Boundary:** not yet active production-validated detection coverage.

## Source documents to review

- `docs/owasp-documents/OWASP-Top-10-for-Agentic-Applications-2026-12.6.pdf`
- `docs/owasp-documents/OWASP-Top10-for-Agentic-Applications_AIUC-1-Crosswalk-May26.pdf`
- `docs/owasp-documents/State-of-Agentic-AI-Security-and-Governance-v2.01.pdf`
- existing VulnoraIQ `docs/owasp/LLM06_EXCESSIVE_AGENCY.md`
- existing VulnoraIQ `agent_testing/` manifests and scenarios
- `docs/owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`

## Planning categories

The exact OWASP Agentic `ASIxx` category names must be extracted and confirmed from the source PDFs before the rows below are treated as official OWASP category names.

| Planning ID | Agentic risk/control area | Current status | Related OWASP LLM categories | Primary evidence surfaces |
| --- | --- | --- | --- | --- |
| AGENTIC-01 | Agent instruction / prompt injection | Planning | LLM01, LLM07 | prompt, retrieved context, tool description, plan trace |
| AGENTIC-02 | Excessive tool permission or agency | Planning | LLM06, LLM10 | tool manifest, action trace, approval record |
| AGENTIC-03 | Insecure delegation and inter-agent trust | Planning | LLM06 | agent identity, delegation trace, handoff policy |
| AGENTIC-04 | Tool/connector supply-chain compromise | Planning | LLM03, LLM06 | connector manifest, tool metadata, version/provenance |
| AGENTIC-05 | Memory, state, or plan poisoning | Planning | LLM04, LLM06, LLM08 | memory trace, state diff, plan graph, source metadata |
| AGENTIC-06 | Sensitive data exposure through agent actions | Planning | LLM02, LLM06 | tool trace, credential scope, output artifact, audit log |
| AGENTIC-07 | Runaway loops and resource exhaustion | Planning | LLM10, LLM06 | iteration budget, retry budget, tool-call count, cost budget |
| AGENTIC-08 | Missing human oversight and approval | Planning | LLM06, LLM05 | approval checkpoint, action classification, denied action evidence |
| AGENTIC-09 | Poor auditability and trace gaps | Planning | LLM06, LLM02 | action trace, request ID, memory trace, tool trace, report evidence |
| AGENTIC-10 | Unsafe goals, planning, and policy conflict | Planning | LLM06, LLM09, LLM10 | goal, plan, policy decision, manual-review route |

## Relationship to existing LLM tests

Existing VulnoraIQ LLM tests already cover starter forms of:

- prompt injection
- sensitive information disclosure
- supply chain
- data/model poisoning
- improper output handling
- excessive agency
- system prompt leakage
- vector/embedding weaknesses
- misinformation
- unbounded consumption

The Agentic plan expands this into agent runtime-specific testing:

- plan-act-observe loops
- tool invocation and connector permissioning
- memory writes and state transitions
- inter-agent delegation
- high-impact action approval
- traceability and non-repudiation
- bounded autonomy and budget controls
- cross-agent and cross-tool lateral movement

## Maturity rule

An Agentic planning area remains `Planning` until:

1. exact OWASP Agentic source category wording is confirmed,
2. a safe local agent fixture exists,
3. a scenario manifest exists,
4. an evaluator or validator exists,
5. report evidence includes plan/tool/memory/action traces where relevant,
6. CI validates secure, vulnerable, ambiguous, and edge-case scenarios.

A category can move to `Working starter` when it has representative fixture coverage and operator-facing report language with explicit limitations.

## Files

- [`PRODUCTION_READINESS_PLAN.md`](PRODUCTION_READINESS_PLAN.md) — phased implementation plan

## Next steps

1. Extract official ASI category names and descriptions from the OWASP Agentic PDFs.
2. Replace `AGENTIC-xx` planning IDs with confirmed `ASIxx` IDs where appropriate.
3. Add agentic scenario manifests under `benchmarks/fixtures/agentic/`.
4. Expand `agent_testing/` with safe local agent loops and tool traces.
5. Add `core/agentic_evaluators.py` or equivalent evaluator composition.
6. Add report and dashboard coverage for agentic risk areas.
7. Add MITRE ATLAS tactic and technique mappings for each confirmed ASI category.