# GenAI Security production readiness plan

Plan status: Completed for `0.3.0` self-hosted internal deployment.

This is the controlled internal enterprise deployment gate for the Docker-first laptop/server application model.

**Scenario harness status:** production-grade scenario harness for controlled internal validation.

**Scope:** GenAI data-security and governance assessment readiness for authorised internal LLM, RAG, vector-store, provider, tool, telemetry, multimodal, and model-artifact assessments.

**Readiness claim:** VulnoraIQ has a production-grade scenario harness for controlled internal GenAI Security validation. The harness expands the source-confirmed `DSGAI01–DSGAI21` taxonomy into **84 concrete scenario cases**: expected-control, control-gap, ambiguous-review, and boundary-condition coverage for every source-confirmed category.

**Assurance boundary:** this is **not independent real-world detection assurance**. It means the scenario matrix, evidence contract, evaluator chain, confidence floors, manual-review routing, source-discrepancy tracking, tests, and CI gates are production-grade for controlled internal validation. Certified VAPT-grade assurance and independent real-world GenAI detection validation remain outside this claim.

## Source-confirmed baseline

VulnoraIQ tracks the OWASP GenAI Data Security categories `DSGAI01–DSGAI21` from reviewed source material.

> **Source discrepancy:** the GenAI document narrative references `DSGAI01–DSGAI25`, while the accessible table of contents confirms `DSGAI01–DSGAI21`. `DSGAI22–DSGAI25` remain explicitly preserved as unresolved source discrepancy / map-later items in `benchmarks/fixtures/genai/scenarios.yaml`.

## Phase status

| Phase | Area | Status | Release gate |
| --- | --- | --- | --- |
| GENAI-0 | Boundary and source confirmation | Complete | Docs preserve the source-confirmed range and source discrepancy. |
| GENAI-1 | Scenario manifests | Complete | `benchmarks/fixtures/genai/scenarios.yaml` defines the v2 matrix with 84 concrete scenario cases. |
| GENAI-2 | Evaluator composition | Complete | `core/genai_evaluators.py` provides deterministic evaluators, confidence-floor checks, acceptance criteria checks, and aggregate result handling. |
| GENAI-3 | Evidence schema contract | Complete | `genai-production-v2` requires evidence, confidence, evaluator, acceptance, severity, false-positive, and false-negative fields. |
| GENAI-4 | Reports and dashboard language | Complete | GenAI findings must state assessed surface, synthetic evidence basis, manual-review requirement, and assurance limitation. |
| GENAI-5 | COMPASS workflow integration | Complete | Observe, Orient, Decide, Act workflow is mapped to inventory, mapping, prioritisation, and report/retest actions. |
| GENAI-6 | CI and release gates | Complete | `scripts/validate_genai_readiness.py`, tests, package validation, and CI workflows validate the harness. |
| GENAI-7 | Independent assurance maturity | Future maturity | Requires approved-environment validation, provider/data inventory integrations, SIEM/SOAR integration, and independent assessment. |

## Production-grade scenario harness

The v2 manifest defines:

- `21` source-confirmed GenAI categories;
- `4` required fixture types per category;
- `84 concrete scenario cases` generated from the category and fixture matrix;
- required evidence contract version `genai-production-v2`;
- deterministic evaluator chain;
- confidence floors for each fixture type;
- required manual review for every GenAI scenario case;
- safe-fixture enforcement to avoid live sensitive data in CI;
- real-world validation flag preserved to prevent overclaiming.

## Required evidence contract

Every scenario case expands into a result requiring fields such as:

- `genai_id`;
- `genai_risk_area`;
- `data_classification`;
- `data_surface`;
- `redaction_status`;
- `manual_review_required`;
- `manual_review_reason`;
- `mitre_atlas_tactics`;
- evaluator output;
- confidence;
- acceptance criteria;
- false-positive and false-negative notes.

## Current codebase integration

| Integration point | Status |
| --- | --- |
| Scenario manifest | Complete. |
| Deterministic evaluators | Complete. |
| GenAI readiness validator | Complete. |
| CI validation | Complete. |
| Reports/assurance wording | Complete for current scope. |
| Docker-first lab compatibility | Complete through scanner/report/evidence paths. |
| React WebUI deep GenAI dashboarding | Future maturity item beyond current target-management work. |

## Not claimed

This plan does not claim that VulnoraIQ can independently detect every real GenAI data-security issue in production environments. That stronger claim requires approved real-environment validation, provider/data inventory connectors, governance evidence, privacy/legal review, and independent assurance.

## Approved-environment validation implementation

The harness now includes controlled approved-environment validation support: target templates, minimal adapter interfaces, URL/host/authorisation/rate-limit validation, dry-run defaults, and redaction checks. Synthetic scenarios remain the default readiness evidence, and external independent assurance remains required for stronger claims.
