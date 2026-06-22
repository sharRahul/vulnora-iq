# OWASP GenAI and Data Privacy Test Plan

Status: implementation-ready
Source set: `docs/owasp-documents/`

## Goal

Add safe, repeatable VulnoraIQ scenario coverage for GenAI and data privacy control validation.

## Plan

1. Add a dedicated payload library: `payloads/owasp_genai_data_privacy.yaml`.
2. Add source metadata that points to `docs/owasp-documents/`.
3. Map each scenario to existing VulnoraIQ module identifiers through `metadata.applies_to`.
4. Add CI tests that fail when GenAI or privacy scenario families are missing.
5. Keep all scenario text safe, synthetic, and control-oriented.

## GenAI families

- governance
- context boundary
- retrieval trust
- agent approval
- output validation
- generated content review
- provenance and auditability
- bounded resource use

## Data privacy families

- data minimisation
- consent and lawful basis
- purpose limitation
- redaction
- tenant boundary
- retention and deletion
- audit logging
- processor review
- privacy impact review
- user rights handling

## Acceptance criteria

CI should verify that all required families exist, each scenario has source metadata, and the default config loads the scenario library.
