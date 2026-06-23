# GenAI Security Implementation Plan

This folder defines VulnoraIQ's GenAI data-security and governance testing plan beyond the existing OWASP LLM 2025 category files.

> **Status:** Working starter for controlled internal enterprise assessment readiness.  
> **Scope:** OWASP GenAI Data Security Risks and Mitigations 2026, OWASP GenAI COMPASS operating model, safe synthetic scenario suites, deterministic GenAI evaluators, and VulnoraIQ evidence/reporting guardrails.  
> **Boundary:** GenAI findings are framework evidence requiring human review. VulnoraIQ does not claim certified VAPT-grade assurance, public internet/SaaS readiness, or production-validated real-world detection coverage for every category.

## Source documents reviewed

- `docs/owasp-documents/OWASP-GenAI-COMPASS-RunBook-1.0.pdf` — confirms COMPASS uses an Observe/Orient/Decide/Act workflow and integrates MITRE ATT&CK, ATLAS, NAVIGATOR, D3FEND, CAPEC, STIX, CVE, CWE, and a 5-point scoring method.
- `docs/owasp-documents/OWASP-GenAI-Data-Security-Risks-and-Mitigations-2026-v1.0.pdf` — confirms GenAI data-security categories `DSGAI01` through `DSGAI21` in the visible table of contents.
- existing VulnoraIQ `docs/owasp/` LLM implementation specs
- `docs/owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`

## Source note

The GenAI Data Security document's narrative text references a `DSGAI01–DSGAI25` taxonomy, while the accessible table of contents confirms `DSGAI01–DSGAI21`. VulnoraIQ tracks `DSGAI01–DSGAI21` as source-confirmed and keeps `DSGAI22–DSGAI25` open in `benchmarks/fixtures/genai/scenarios.yaml` until a complete extracted source list is available.

## Implemented GenAI readiness assets

| Asset | Status | Purpose |
| --- | --- | --- |
| [`PRODUCTION_READINESS_PLAN.md`](PRODUCTION_READINESS_PLAN.md) | Complete | Phase-by-phase GenAI Security readiness plan and completion decision. |
| `benchmarks/fixtures/genai/scenarios.yaml` | Working starter | Machine-readable scenario manifest for `DSGAI01–DSGAI21`, with secure, vulnerable, ambiguous, and edge-case fixture coverage. |
| `core/genai_evaluators.py` | Working starter | Deterministic GenAI evaluator composition for synthetic marker leakage, classification, data surface, evidence fields, context minimisation, and scenario expectations. |
| `scripts/validate_genai_readiness.py` | Controlled-internal release gate | Validates GenAI manifests, source discrepancy tracking, docs status, evidence fields, fixture coverage, and MITRE ATLAS tactic format. |
| `tests/test_genai_readiness_validation.py` | CI gate | Regression tests for validator and evaluator behaviour. |

## Confirmed GenAI data-security coverage areas

| OWASP ID | GenAI data-security risk | Current status | Related OWASP LLM categories | Primary evidence surfaces |
| --- | --- | --- | --- | --- |
| DSGAI01 | Sensitive Data Leakage | Working starter | LLM02, LLM07 | prompt, response, report artifact, logs |
| DSGAI02 | Agent Identity & Credential Exposure | Working starter | LLM02, LLM06 | tool trace, credential scope, agent identity metadata |
| DSGAI03 | Shadow AI & Unsanctioned Data Flows | Working starter | LLM02, LLM03, LLM06 | provider inventory, network/service discovery, policy evidence |
| DSGAI04 | Data, Model & Artifact Poisoning | Working starter | LLM03, LLM04, LLM08 | source manifest, corpus delta, model/artifact hash |
| DSGAI05 | Data Integrity & Validation Failures | Working starter | LLM04, LLM05, LLM08 | schema validation, freshness, provenance, source approval |
| DSGAI06 | Tool, Plugin & Agent Data Exchange Risks | Working starter | LLM02, LLM06 | tool trace, connector manifest, data-flow evidence |
| DSGAI07 | Data Governance, Lifecycle & Classification for AI Systems | Working starter | all LLM categories | classification labels, lineage, retention, approval evidence |
| DSGAI08 | Non-Compliance & Regulatory Violations | Working starter | LLM02, LLM03, LLM04, LLM06 | policy mapping, data residency, regulatory control evidence |
| DSGAI09 | Multimodal Capture & Cross-Channel Data Leakage | Working starter | LLM02, LLM05 | multimodal input metadata, output artifact, DLP findings |
| DSGAI10 | Synthetic Data, Anonymization & Transformation Pitfalls | Working starter | LLM02, LLM04, LLM09 | synthetic-data metadata, transformation record, re-identification risk evidence |
| DSGAI11 | Cross-Context & Multi-User Conversation Bleed | Working starter | LLM02, LLM08 | session memory, tenant/user boundary, conversation context |
| DSGAI12 | Unsafe Natural-Language Data Gateways (LLM-to-SQL/Graph) | Working starter | LLM05, LLM06 | generated query, schema allowlist, DB/tool trace |
| DSGAI13 | Vector Store Platform Data Security | Working starter | LLM02, LLM08 | vector store metadata, ACLs, tenant index, embedding trace |
| DSGAI14 | Excessive Telemetry & Monitoring Leakage | Working starter | LLM02, LLM07 | logs, traces, audit events, monitoring exports |
| DSGAI15 | Over-Broad Context Windows & Prompt Over-Sharing | Working starter | LLM01, LLM02, LLM07 | context assembly, trust-domain segments, prompt metadata |
| DSGAI16 | Endpoint & Browser Assistant Overreach | Working starter | LLM02, LLM06 | browser/endpoint permission, local context, tool trace |
| DSGAI17 | Data Availability & Resilience Failures in AI Pipelines | Working starter | LLM08, LLM09, LLM10 | vector/index availability, failover state, backup/restore validation |
| DSGAI18 | Inference & Data Reconstruction | Working starter | LLM02, LLM08 | inference probe, embedding/model output, privacy-risk evidence |
| DSGAI19 | Human-in-the-Loop & Labeler Overexposure | Working starter | LLM02, LLM06 | reviewer workflow, label queue, masking/approval evidence |
| DSGAI20 | Model Exfiltration & IP Replication | Working starter | LLM02, LLM03 | model artifact metadata, access logs, extraction probe |
| DSGAI21 | Disinformation & Integrity Attacks via Data Poisoning | Working starter | LLM04, LLM09 | poisoned-source scenario, trust score, unsupported claim evidence |

## Relationship to existing LLM tests

The existing LLM test plan focuses on model, RAG, agent, output, and resource-risk categories. The GenAI plan adds organisation-level and data-security controls:

- data asset discovery and inventory
- data classification and policy binding
- data flow mapping and lineage
- GenAI/AI data bill of materials concepts
- access governance and entitlement posture for agents
- lifecycle, retention, and deletion
- provider data handling and residency
- report/log/telemetry artifact hygiene
- multimodal data capture and leakage
- vector-store platform security
- human-review and labeler exposure controls

## COMPASS alignment

VulnoraIQ implements GenAI assessment workflow support around the COMPASS loop:

| COMPASS phase | VulnoraIQ implementation implication |
| --- | --- |
| Observe | Inventory AI assets, data stores, providers, prompts, context windows, tools, logs, and RAG/vector stores. |
| Orient | Map observed assets to OWASP LLM, DSGAI, Agentic ASI, MITRE ATLAS, incidents, and control gaps. |
| Decide | Prioritise safe GenAI scenario suites, mitigations, compensating controls, and implementation backlog. |
| Act | Generate reports, roadmap items, tickets, control evidence, and retest scenarios. |

## Validation

```bash
python scripts/validate_genai_readiness.py
pytest tests/test_genai_readiness_validation.py -q
```

## Files

- [`PRODUCTION_READINESS_PLAN.md`](PRODUCTION_READINESS_PLAN.md) — completed phased implementation plan
- `benchmarks/fixtures/genai/scenarios.yaml` — source-confirmed GenAI scenario manifest
- `core/genai_evaluators.py` — deterministic GenAI evaluator suite
- `scripts/validate_genai_readiness.py` — CI/release validator
- [`../owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md`](../owasp/OWASP_TO_MITRE_ATLAS_CROSSWALK.md) — OWASP/GenAI/Agentic to MITRE ATLAS mapping

## Remaining future work

GenAI Security remains a working starter. Future work should deepen real-world fixtures, integrate report/dashboard GenAI widgets, add provider inventory connectors, add SIEM/SOAR mappings, and validate findings against authorised real environments.
