# GenAI Security Production Readiness Plan

This document extends VulnoraIQ's OWASP LLM implementation plan into GenAI data-security, governance, and operational controls.

> **Current status:** source-confirmed planning.  
> **Readiness claim:** no GenAI data-security category should be marked `Working` until fixtures, evaluators, evidence, reporting, and CI gates are implemented.

## Current baseline

VulnoraIQ already has:

- OWASP LLM 2025 starter oracle coverage
- deterministic evaluator primitives
- local good/bad fixture targets
- structured evidence and report generation
- production-ready controlled-internal Web UI platform controls
- MITRE ATLAS planning register and candidate OWASP mapping
- source-confirmed GenAI Data Security categories `DSGAI01–DSGAI21`

GenAI data-security work should build on this baseline rather than creating a separate assessment path.

## Source-confirmed category list

| OWASP ID | Category |
| --- | --- |
| DSGAI01 | Sensitive Data Leakage |
| DSGAI02 | Agent Identity & Credential Exposure |
| DSGAI03 | Shadow AI & Unsanctioned Data Flows |
| DSGAI04 | Data, Model & Artifact Poisoning |
| DSGAI05 | Data Integrity & Validation Failures |
| DSGAI06 | Tool, Plugin & Agent Data Exchange Risks |
| DSGAI07 | Data Governance, Lifecycle & Classification for AI Systems |
| DSGAI08 | Non-Compliance & Regulatory Violations |
| DSGAI09 | Multimodal Capture & Cross-Channel Data Leakage |
| DSGAI10 | Synthetic Data, Anonymization & Transformation Pitfalls |
| DSGAI11 | Cross-Context & Multi-User Conversation Bleed |
| DSGAI12 | Unsafe Natural-Language Data Gateways (LLM-to-SQL/Graph) |
| DSGAI13 | Vector Store Platform Data Security |
| DSGAI14 | Excessive Telemetry & Monitoring Leakage |
| DSGAI15 | Over-Broad Context Windows & Prompt Over-Sharing |
| DSGAI16 | Endpoint & Browser Assistant Overreach |
| DSGAI17 | Data Availability & Resilience Failures in AI Pipelines |
| DSGAI18 | Inference & Data Reconstruction |
| DSGAI19 | Human-in-the-Loop & Labeler Overexposure |
| DSGAI20 | Model Exfiltration & IP Replication |
| DSGAI21 | Disinformation & Integrity Attacks via Data Poisoning |

> **Source discrepancy note:** the GenAI document's narrative references `DSGAI01–DSGAI25`, but the accessible table of contents confirms `DSGAI01–DSGAI21`. Keep `DSGAI22–DSGAI25` as `source discrepancy / map later` until a complete extracted list is available.

## Maturity ladder

| Level | Meaning | Required evidence |
| --- | --- | --- |
| Planning | Risk/control area is identified but not implemented. | Source doc reference, candidate OWASP/ATLAS mapping, owner. |
| Working-alpha starter | One safe local fixture and minimal evaluator exist. | Good/bad fixture, minimal evidence, unit test. |
| Working starter | Representative scenario set and report evidence exist. | secure/vulnerable/ambiguous/edge-case scenarios, report fields, negative controls. |
| Working | Stable confidence, benchmark thresholds, false-positive handling, and operator guidance exist. | CI gates, benchmark thresholds, evidence schema, reviewed docs. |
| Production-ready candidate | Authorised validation guidance, evidence-retention rules, and governance approvals exist. | validation runbook, approval gates, retention policy, release sign-off. |

## Phase GENAI-1 — Scenario manifests

Create safe scenario manifests under:

```text
benchmarks/fixtures/genai/
```

Required fields:

- `scenario_id`
- `genai_id`
- `risk_area`
- `fixture_type`: secure, vulnerable, ambiguous, edge_case
- `data_classification`: public, internal, confidential, secret, regulated
- `data_surface`: prompt, upload, retrieval, response, tool_trace, memory, log, report, provider_metadata, vector_store, multimodal_input, model_artifact
- `input_fixture`
- `expected_secure_outcome`
- `expected_vulnerable_signal`
- `required_evidence_fields`
- `mitre_atlas_tactics`
- `manual_review_required`

Minimum scenario requirements:

| OWASP ID | Minimum scenario focus |
| --- | --- |
| DSGAI01 | synthetic secret/PII leakage in prompt, response, log, report artifact |
| DSGAI02 | scoped vs over-scoped agent credentials, JIT token, leaked credential-bearing trace |
| DSGAI03 | sanctioned provider, unknown provider, unsanctioned upload/data flow |
| DSGAI04 | approved source, poisoned corpus, tampered artifact, model/version drift |
| DSGAI05 | valid schema, stale data, invalid source, unreviewed data transformation |
| DSGAI06 | safe connector exchange, over-broad plugin access, tool data exfil path |
| DSGAI07 | classified data, missing classification, retention expiry, deletion gap |
| DSGAI08 | compliant residency/retention, missing legal basis, regulated-data exposure |
| DSGAI09 | safe multimodal input, identity document exposure, screenshot/voice leakage |
| DSGAI10 | valid transformation, reversible anonymisation, synthetic data membership risk |
| DSGAI11 | isolated conversation, cross-user bleed, multi-tenant session/cache bleed |
| DSGAI12 | safe NL-to-SQL, unsafe generated query, excessive schema/data access |
| DSGAI13 | per-tenant index, mis-scoped ACL, poisoned snapshot/import, embedding leakage |
| DSGAI14 | safe telemetry, excessive trace capture, token-like value in logs |
| DSGAI15 | minimal context, over-broad context, mixed trust-domain prompt assembly |
| DSGAI16 | constrained assistant, endpoint/browser overreach, local context leak |
| DSGAI17 | healthy pipeline, stale failover index, vector DB saturation, corrupt restore |
| DSGAI18 | safe inference, reconstruction probe, membership inference indicator |
| DSGAI19 | masked labeler view, overexposed review queue, high-sensitivity reviewer path |
| DSGAI20 | protected model artifact, extraction probe, model/IP replication indicator |
| DSGAI21 | trusted data, poisoned disinformation corpus, unsupported high-impact claim |

## Phase GENAI-2 — Evaluator composition

Add GenAI evaluator composition using existing primitives where possible.

Potential module:

```text
core/genai_evaluators.py
```

Evaluator types:

- data classification evaluator
- restricted marker evaluator
- secret/token-like pattern evaluator
- report artifact leakage evaluator
- provider metadata evaluator
- provenance and ownership evaluator
- retention and deletion evaluator
- regulatory metadata evaluator
- multimodal leakage evaluator
- context-window minimisation evaluator
- vector-store isolation evaluator
- NL-to-SQL/Graph safety evaluator
- endpoint/browser permission evaluator
- availability/resilience evaluator
- inference/reconstruction risk evaluator
- model artifact protection evaluator
- disinformation/integrity evaluator
- residual-risk and manual-review evaluator

Each evaluator should return:

- `status`: pass, warn, fail, review
- `confidence`
- `reason`
- `evidence_fields`
- `false_positive_notes`
- `manual_review_required`

## Phase GENAI-3 — Evidence schema expansion

Extend report JSON and finding evidence with:

- `genai_id`
- `genai_risk_area`
- `data_classification`
- `data_surface`
- `provider_name`
- `provider_region`
- `provider_retention_policy_known`
- `source_owner`
- `source_hash`
- `source_review_status`
- `redaction_status`
- `artifact_scan_status`
- `vector_store_scope`
- `context_window_scope`
- `retention_status`
- `regulatory_context`
- `manual_review_reason`
- `mitre_atlas_tactics`

## Phase GENAI-4 — Reports and dashboards

Add operator-facing language for each GenAI risk area:

- what the finding means
- what it does not prove
- which data surface was tested
- whether real sensitive data was observed or only a synthetic marker
- confidence explanation
- remediation guidance
- data retention and sharing cautions
- when human review is required

Dashboard additions:

- GenAI data-security coverage table
- data surface coverage chart
- report artifact leakage status
- provider risk summary
- vector-store security summary
- context-window minimisation status
- unresolved governance/control gaps

## Phase GENAI-5 — COMPASS workflow integration

Use COMPASS as the operating model:

| COMPASS phase | VulnoraIQ implementation |
| --- | --- |
| Observe | asset and data-surface inventory, provider discovery, logs/traces/RAG/vector store discovery |
| Orient | OWASP LLM + DSGAI + Agentic + MITRE ATLAS mapping, incident/control-gap correlation |
| Decide | prioritised GenAI tests, mitigations, compensating controls, and implementation backlog |
| Act | reports, tickets, roadmap items, retest scenarios, control evidence, and dashboard updates |

## Phase GENAI-6 — CI and release gates

Add gates that fail if:

- `DSGAI01–DSGAI21` categories lack scenario manifests
- scenario manifests are missing required fields
- vulnerable fixtures are missed
- secure fixtures are flagged high-confidence without reason
- report artifacts contain restricted markers outside controlled evidence fields
- GenAI findings lack data surface and classification metadata
- MITRE ATLAS tactic mappings are missing
- source discrepancy for `DSGAI22–DSGAI25` is not tracked
- docs and machine-readable crosswalk drift

## GenAI implementation matrix

| OWASP ID | Current baseline | Next implementation focus | Working target |
| --- | --- | --- | --- |
| DSGAI01 | LLM02 restricted marker checks. | Prompt/response/log/report DLP fixtures. | Synthetic leakage detected with no real-data exposure. |
| DSGAI02 | LLM06 tool governance starter. | Agent identity and credential-scope scenarios. | Over-scoped or leaked credentials are flagged. |
| DSGAI03 | Provider inventory not deep. | Shadow AI discovery and unknown provider evidence. | Unsanctioned data flows become visible. |
| DSGAI04 | LLM04 provenance checks. | Corpus/model/artifact poisoning scenarios. | Tampered source/model/artifact is detected. |
| DSGAI05 | Schema/provenance primitives exist. | Data validity/freshness/source-review scenarios. | Integrity failures include remediation-ready evidence. |
| DSGAI06 | Tool trace starter. | Plugin/tool/agent data exchange controls. | Data crossing connector boundaries is evidenced. |
| DSGAI07 | Policy exceptions exist. | Classification, retention, lifecycle metadata. | Reports show lifecycle governance gaps. |
| DSGAI08 | Policy engine exists. | Compliance/residency/legal basis evidence. | Regulated-data risks are routed to review. |
| DSGAI09 | No multimodal evaluator yet. | Multimodal DLP and privacy review fixtures. | Cross-channel leakage is detected using safe markers. |
| DSGAI10 | No synthetic data evaluator yet. | Re-identification and transformation-risk tests. | Weak anonymisation is flagged for review. |
| DSGAI11 | Session boundary concepts exist. | Conversation/cache/memory bleed scenarios. | Cross-user/context bleed is detected. |
| DSGAI12 | LLM05 schema checks exist. | NL-to-SQL/Graph intent gate and query allowlists. | Unsafe generated queries are blocked or flagged. |
| DSGAI13 | LLM08 retrieval checks exist. | Vector DB ACL, import, and tenant isolation tests. | Vector-store boundary failures are visible. |
| DSGAI14 | Audit logs exist. | Telemetry/log/report leakage scanner. | Excessive trace capture is flagged. |
| DSGAI15 | Prompt evidence exists. | Context-window minimisation and trust-domain checks. | Over-sharing is detected before report assurance. |
| DSGAI16 | LLM06 tool governance starter. | Browser/endpoint assistant permission tests. | Endpoint overreach is flagged. |
| DSGAI17 | Backup/restore exists. | AI pipeline availability, stale failover, semantic restore tests. | Silent degraded AI data failures are detected. |
| DSGAI18 | No inference evaluator yet. | Reconstruction and membership-inference-safe probes. | Reconstruction risk is routed to human review. |
| DSGAI19 | Approval evidence exists. | Labeler/reviewer data minimisation scenarios. | Human reviewer overexposure is detected. |
| DSGAI20 | Supply-chain metadata exists. | Model artifact protection and extraction probes. | Model/IP extraction risk is evidenced. |
| DSGAI21 | LLM09/LLM04 starters. | Data-poisoned disinformation/integrity scenarios. | Poisoned misinformation is flagged with source evidence. |

## Immediate backlog

1. Create `benchmarks/fixtures/genai/` manifests for `DSGAI01–DSGAI21`.
2. Add `core/genai_evaluators.py`.
3. Add GenAI evidence fields to report JSON schema.
4. Add artifact leakage scanner for Markdown/JSON/SARIF/HTML/dashboard outputs.
5. Add provider/data inventory schema under `config/`.
6. Add GenAI coverage dashboard section.
7. Add CI validation for GenAI manifests, mappings, and report fields.
8. Add generated report limitation text for GenAI data-security findings.
9. Add machine-readable DSGAI-to-ATLAS mapping.
10. Track and resolve the `DSGAI01–DSGAI25` source discrepancy.

## Claim rule

Do not describe GenAI data-security coverage as `Working` or production-ready until fixtures/evaluators exist and CI validates the scenario set.