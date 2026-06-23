# GenAI Security Production Readiness Plan

**Plan status:** Completed for `0.2.0` controlled internal enterprise deployment.

**Scenario harness status:** production-grade scenario harness for controlled internal validation.

**Scope:** GenAI data-security and governance assessment readiness for authorised internal LLM, RAG, vector-store, provider, tool, telemetry, multimodal, and model-artifact assessments.

**Readiness claim:** VulnoraIQ has a **production-grade scenario harness** for controlled internal GenAI Security validation. The harness expands the source-confirmed `DSGAI01–DSGAI21` taxonomy into **84 concrete scenario cases**: secure, vulnerable, ambiguous-review, and edge-case-boundary coverage for every source-confirmed category.

**Assurance boundary:** this is **not independent real-world detection assurance**. It means the scenario matrix, evidence contract, evaluator chain, confidence floors, manual-review routing, source-discrepancy tracking, tests, and CI gates are production-grade for controlled internal validation. Public internet / SaaS readiness, certified VAPT-grade assurance, and independent real-world GenAI detection validation remain outside this claim.

## Source-confirmed baseline

VulnoraIQ tracks the OWASP GenAI Data Security categories `DSGAI01–DSGAI21` from the reviewed source material.

> **Source discrepancy:** the GenAI document narrative references `DSGAI01–DSGAI25`, while the accessible table of contents confirms `DSGAI01–DSGAI21`. `DSGAI22–DSGAI25` remain explicitly preserved as unresolved source discrepancy / map-later items in `benchmarks/fixtures/genai/scenarios.yaml`.

## Phase status

| Phase | Area | Status | Release gate |
| --- | --- | --- | --- |
| GENAI-0 | Boundary and source confirmation | Complete | Docs preserve the `DSGAI01–DSGAI21` source-confirmed range and the `DSGAI22–DSGAI25` discrepancy. |
| GENAI-1 | Scenario manifests | Complete | `benchmarks/fixtures/genai/scenarios.yaml` now defines a v2 production-grade matrix with 84 concrete scenario cases. |
| GENAI-2 | Evaluator composition | Complete | `core/genai_evaluators.py` provides deterministic evaluators, confidence-floor checks, acceptance criteria checks, and aggregate-result handling. |
| GENAI-3 | Evidence schema contract | Complete | `genai-production-v2` requires evidence, confidence, evaluator, acceptance, severity, false-positive, and false-negative fields. |
| GENAI-4 | Reports and dashboard language | Complete | GenAI findings must state the assessed surface, synthetic evidence basis, manual-review requirement, and assurance limitation. |
| GENAI-5 | COMPASS workflow integration | Complete | Observe, Orient, Decide, Act workflow is mapped to inventory, mapping, prioritisation, and report/retest actions. |
| GENAI-6 | CI and release gates | Complete | `scripts/validate_genai_readiness.py`, tests, package validation, and both CI workflows validate the harness. |
| GENAI-7 | Public/SaaS hardening | Deferred | Requires tenant isolation, external assurance, SIEM/SOAR integration, SLOs, public ingress protection, and stronger identity/governance integrations. |

## Production-grade scenario harness

The v2 manifest defines:

- `21` source-confirmed GenAI categories.
- `4` required fixture types per category: `secure`, `vulnerable`, `ambiguous`, `edge_case`.
- `84 concrete scenario cases` generated from the category × fixture matrix.
- Required evidence contract version `genai-production-v2`.
- Required evaluator chain:
  - `data_classification_present`
  - `data_surface_allowed`
  - `evidence_fields_present`
  - `restricted_marker_leakage`
  - `scenario_expectation`
  - `confidence_floor_met`
  - `acceptance_criteria_present`
- Confidence floors for each fixture type.
- Severity requirements, including high/critical severity for vulnerable production cases.
- Required manual review for every GenAI scenario case.
- Safe-fixture enforcement to avoid live sensitive data in CI.
- Real-world validation flag preserved to prevent overclaiming.

## Required evidence contract

Every scenario case expands into a result requiring:

- `genai_id`
- `genai_risk_area`
- `scenario_id`
- `fixture_type`
- `data_classification`
- `data_surface`
- `control_objective`
- `production_signal`
- `redaction_status`
- `manual_review_reason`
- `evaluator_chain`
- `acceptance_criteria`
- `severity`
- `confidence_floor`
- `mitre_atlas_tactics`
- `false_positive_notes`
- `false_negative_notes`

The validator fails the release if any of these required controls drift.

## Validation

```bash
python scripts/validate_genai_readiness.py
pytest tests/test_genai_readiness_validation.py -q
python scripts/validate_package_metadata.py
```

## Completion decision

**Completed for `0.2.0` controlled internal enterprise GenAI Security readiness.** The scenario harness is now production-grade for controlled internal validation with 84 concrete scenario cases, strict evidence contract validation, deterministic evaluator checks, and CI/release gates. This remains **not independent real-world detection assurance** and does not support public/SaaS/certified claims without the deferred hardening and independent validation work.
