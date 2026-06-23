# OWASP LLM Top 10 Mapping Implementation Plan

## Purpose

This plan defines how VulnoraIQ should use the `emmanuelgjr/owaspllmtop10mapping` repository as an input source for framework/control mappings around OWASP Top 10 for LLM risks.

The goal is to move from simple OWASP/ATLAS labels to a normalized, queryable mapping layer that can enrich findings, reports, dashboards, and remediation guidance with control-framework context.

## Source basis

Reviewed source:

- `emmanuelgjr/owaspllmtop10mapping` repository README.
- Repository file listing from GitHub.
- Sample mapping files: `NIST.md` and `MITREATLAS.md`.

Key source observations:

- The repository provides mappings between OWASP Top 10 for LLM categories and multiple cybersecurity frameworks/standards.
- The README lists mapping targets including NIST CSF, ISO/IEC 27001, ISO/IEC 20547-4:2020, MITRE ATT&CK, CIS Controls, CVE/CWE, FAIR, STRIDE, ENISA, ASVS, SAMM, MITRE ATLAS, BSIMM, OPENCRE, and CycloneDX ML SBOM.
- The repository is archived and read-only, so VulnoraIQ should treat it as a static reference source rather than a continuously maintained upstream dependency.
- The README states the project is MIT licensed.
- The sample `NIST.md` maps LLM risks to Identify, Protect, Detect, Respond, and Recover actions.
- The sample `MITREATLAS.md` maps LLM risks to ATLAS/ATT&CK-style technique IDs and includes mitigations, but also warns that mappings are approximations and should be adapted to context.

## Important compatibility issue

The mapping repository appears aligned to an earlier OWASP LLM Top 10 naming set, for example:

- `LLM02: Insecure Output Handling`
- `LLM04: Model Denial of Service`
- `LLM06: Sensitive Information Disclosure`
- `LLM07: Insecure Plugin Design`

VulnoraIQ currently works toward OWASP LLM 2025 coverage. Therefore, this source must not be ingested as if it were automatically authoritative for 2025 categories.

Implementation must include:

1. Source version metadata.
2. OWASP LLM version metadata.
3. Category-normalization rules.
4. Mapping confidence.
5. Review status.
6. A clear warning where legacy LLM category names differ from the current VulnoraIQ OWASP LLM taxonomy.

## Implementation goal

VulnoraIQ should gain a framework mapping subsystem that:

- Stores OWASP LLM to framework mappings in a normalized YAML/JSON format.
- Preserves source provenance and license attribution.
- Supports versioned OWASP LLM categories.
- Allows findings to include framework mappings when applicable.
- Allows reports to generate framework-specific views.
- Avoids overclaiming compliance or certification.
- Allows mappings to be marked as exact, partial, inferred, approximate, or needs review.

## Target architecture

```text
external mapping source docs
        |
        v
scripts/import_owasp_llm_framework_mappings.py
        |
        v
config/mappings/owasp_llm_framework_mappings.yaml
        |
        +--> schemas/owasp_llm_framework_mappings.schema.json
        |
        v
core/framework_mapping_registry.py
        |
        +--> finding enrichment
        +--> WebUI filtering
        +--> JSON/Markdown/HTML report sections
        +--> CI coverage validation
```

## New or updated repository artifacts

| Area | Planned files |
| --- | --- |
| Source review | `docs/sources/owasp_llm_mapping_source_review.md` |
| Normalized mappings | `config/mappings/owasp_llm_framework_mappings.yaml` |
| Schema | `schemas/owasp_llm_framework_mappings.schema.json` |
| Import helper | `scripts/import_owasp_llm_framework_mappings.py` |
| Registry | `core/framework_mapping_registry.py` |
| Tests | `tests/test_framework_mapping_registry.py`, `tests/test_owasp_llm_mapping_schema.py` |
| Report docs | Update report templates and documentation |
| WebUI | Add framework-mapping fields to finding details and filters |

## Mapping schema design

Each mapping entry should preserve source and confidence:

```yaml
mappings:
  - source_repository: emmanuelgjr/owaspllmtop10mapping
    source_file: NIST.md
    source_license: MIT
    source_status: archived
    source_retrieved_at: 2026-06-23
    source_owasp_llm_version: legacy-pre-2025
    normalized_owasp_llm_id: LLM01
    normalized_owasp_llm_name: Prompt Injection
    source_owasp_llm_name: Prompt Injection
    framework: NIST CSF
    framework_version: unspecified
    framework_control: Identify
    mapping_type: function
    mapping_confidence: medium
    mapping_status: needs_review
    implementation_use:
      - report_enrichment
      - remediation_guidance
    guidance: Recognize potential sources and impacts of prompt injection attacks.
```

Required fields:

- `source_repository`
- `source_file`
- `source_license`
- `source_status`
- `source_retrieved_at`
- `source_owasp_llm_version`
- `normalized_owasp_llm_id`
- `framework`
- `framework_control`
- `mapping_confidence`
- `mapping_status`

## Framework coverage plan

| Source file | Planned VulnoraIQ use |
| --- | --- |
| `NIST.md` | NIST CSF function-level finding enrichment and remediation grouping. |
| `ISO27001.md` | ISO 27001 control mapping for governance/security reports. |
| `ISO20547-4:2020.md` | Big-data architecture security/privacy context for AI data systems. |
| `MITREATT&CK.md` | Enterprise adversary technique context, clearly separated from MITRE ATLAS. |
| `MITREATLAS.md` | AI adversary technique context and mitigation hints, subject to validation. |
| `CIS_Controls.md` | Practical security control recommendations. |
| `CVE_CWE.md` | Weakness/vulnerability taxonomy enrichment. |
| `FAIR.md` | Risk quantification classification support. |
| `STRIDE.md` | Threat-model category mapping. |
| `ENISA.md` | EU security good-practice context. |
| `ASVS.md` | Web application verification mapping where LLM app risks touch web controls. |
| `SAMM.md` | Secure SDLC maturity mapping. |
| `BSIMM.md` | Software security initiative maturity mapping. |
| `OPEN_CRE.md` | Common requirement/control linking. |
| `CycloneDX_Software-Bill-of-Materials(SBOM).md` | ML/AI SBOM supply-chain reporting context. |

## Phase plan

### Phase 0 — Source and license review

Deliverables:

- Add `docs/sources/owasp_llm_mapping_source_review.md`.
- Record repository archived status, retrieval date, file list, and license.
- Record that this source is not automatically authoritative for OWASP LLM 2025.

Acceptance criteria:

- Every imported mapping has license/source attribution.
- Documentation states that mappings are contextual guidance, not proof of compliance.

### Phase 1 — Normalized schema

Deliverables:

- `schemas/owasp_llm_framework_mappings.schema.json`.
- Initial `config/mappings/owasp_llm_framework_mappings.yaml` with manually curated sample mappings.
- Mapping status values:
  - `validated`
  - `needs_review`
  - `legacy_name_review_required`
  - `deprecated`

Acceptance criteria:

- CI validates the mapping manifest.
- CI rejects entries without source provenance.
- CI rejects entries without OWASP LLM version metadata.

### Phase 2 — OWASP LLM version normalization

Deliverables:

- `config/mappings/owasp_llm_version_aliases.yaml`.
- Normalization logic for legacy category names to VulnoraIQ's current OWASP LLM taxonomy.
- Explicit `manual_review_required` output where no safe exact mapping exists.

Acceptance criteria:

- Legacy names do not silently overwrite current names.
- Every legacy mapping is marked with confidence and review status.

### Phase 3 — Import helper

Deliverables:

- `scripts/import_owasp_llm_framework_mappings.py`.
- Parser for repository Markdown mapping files.
- Generated draft YAML output.
- Human review workflow before mappings become `validated`.

Acceptance criteria:

- The importer can generate draft mappings from the source repository files.
- Generated mappings default to `needs_review`, not `validated`.

### Phase 4 — Runtime registry and finding enrichment

Deliverables:

- `core/framework_mapping_registry.py`.
- Finding enrichment step that attaches relevant framework mappings based on OWASP LLM category.
- Report model extension for framework mappings.

Acceptance criteria:

- Findings can show NIST, ISO, MITRE, CIS, ASVS, SAMM, and SBOM context where available.
- Findings clearly show mapping confidence and source.
- Reports do not claim audit compliance from mapping presence alone.

### Phase 5 — WebUI and report integration

Deliverables:

- WebUI filters by framework.
- Finding detail section for framework/control mappings.
- Executive report section:
  - OWASP LLM category coverage
  - framework mapping coverage
  - control gaps
  - evidence gaps

Acceptance criteria:

- User can filter findings by framework.
- Reports include a framework mapping appendix.
- JSON export includes machine-readable mapping entries.

### Phase 6 — CI validation and documentation

Deliverables:

- `scripts/validate_framework_mappings.py`.
- Tests for mapping schema, registry lookup, and report serialization.
- Updates to docs index and implementation status.

Acceptance criteria:

- CI fails when a mapping has missing source metadata.
- CI fails when a framework mapping references an unknown OWASP LLM ID.
- CI confirms all framework names are normalized.

## Suggested normalized framework names

Use these exact framework IDs internally:

```yaml
NIST_CSF
ISO_27001
ISO_20547_4
MITRE_ATTACK
MITRE_ATLAS
CIS_CONTROLS
CVE_CWE
FAIR
STRIDE
ENISA
OWASP_ASVS
OWASP_SAMM
BSIMM
OPENCRE
CYCLONEDX_ML_SBOM
```

## Report wording rules

Allowed wording:

- "This finding maps to the following framework/control areas."
- "The mapping is provided as contextual remediation guidance."
- "Mapping confidence: medium; review required."
- "Framework coverage does not prove compliance."

Disallowed wording:

- "Compliant with ISO 27001."
- "NIST certified."
- "ATLAS coverage complete."
- "This control is satisfied."
- "Audit ready" unless evidence has been reviewed by a qualified auditor.

## Safety and quality controls

- Keep mappings separate from exploit/test payloads.
- Do not let mappings inflate severity without a deterministic rule.
- Do not create false compliance claims.
- Include provenance in all reports.
- Treat old OWASP LLM names as aliases requiring review.
- Keep mapping confidence visible in UI and exports.

## Completion definition

This implementation can be called complete when:

1. The mapping source has been reviewed and attributed.
2. A normalized mapping manifest exists and passes schema validation.
3. Legacy OWASP LLM names are safely normalized with confidence labels.
4. Findings can be enriched with framework mappings.
5. WebUI and reports show mappings without compliance overclaiming.
6. CI validates source metadata, framework IDs, OWASP IDs, and mapping confidence.
7. Documentation explains that the mapping layer is guidance and traceability, not certification.
