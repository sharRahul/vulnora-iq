# Agentic Applications production readiness plan

**Plan status:** Completed for the current `0.2.0` self-hosted internal deployment scope.  
**Current deployment model:** Docker-first local AI-agent testing lab plus production-mode hosted server for internal self-hosted use.  
**Version target:** `0.2.0`.

## Production boundary

This plan completes the repo-level self-hosted readiness tranche for authorised LLM, RAG, tool-using, and agentic application assessments.

It does **not** claim:

- certified VAPT-grade assurance;
- independent assurance for every agentic risk category;
- authorisation to assess systems without written permission;
- production SaaS readiness.

## Current release language

Allowed:

> Self-hosted laptop/server AI security testing application with controlled internal production-readiness gate passed.

Also allowed:

> Docker-first local AI-agent testing lab with deterministic mock-agent targets, safety profiles, explicit authorisation gates, and a React target-management console.

## Phase status

| Phase | Area | Status | Current evidence |
| --- | --- | --- | --- |
| 0 | Scope and responsible-use boundary | Complete | README, SECURITY, safety model, assessment assurance docs. |
| 1 | Agentic threat mapping governance | Complete | OWASP/MITRE mapping validator, docs, matrix/crosswalk. |
| 2 | Authentication and authorisation | Complete | Production auth fail-closed, token/trusted-proxy modes, role-aware endpoints. |
| 3 | Request and browser hardening | Complete | CSRF, request limits, malformed JSON handling, security headers, artifact path protection, rate limits. |
| 4 | Persistence and migrations | Complete | SQLite job store, WAL, schema versioning, backup/restore. |
| 5 | Auditability and observability | Complete | Audit logs, request IDs, health/readiness/metrics. |
| 6 | Deployment and containerisation | Complete | Dockerfile, Compose, mock-agent, Docker targets, non-root container, healthchecks. |
| 7 | Operations and incident response | Complete | Deployment guide, runbook, incident response, migration, release checklist. |
| 8 | Release and CI quality gates | Complete | Ruff, mypy, pytest, dependency audit, validators, hosted WebUI flow, demo scan, functional acceptance. |
| 9 | Real authorised target testing | Complete for current local/internal scope | Target adapters, runtime target APIs, target validation, Docker lab targets. |
| 10 | React WebUI target management | Complete for current backend APIs | Search/filter, readiness metrics, safety checklist, target CRUD, validation, scan launch, recent jobs. |

## Current implemented agentic testing support

- `agent` and `ai_agent_foundation` profiles.
- Docker `local_agent_tool_loop` target with dry-run workflow behaviour.
- Host-native `agent_tool_loop` template.
- Agency-oriented modules and policy/evidence output.
- WebUI target readiness checklist and explicit authorisation guard.
- Reports and findings requiring human review.

## Remaining agentic maturity work

| Area | Future work |
| --- | --- |
| Tool-use depth | More realistic permission, approval, and state-transition fixtures. |
| Agent memory | Stronger memory poisoning, retrieval, and persistence scenarios. |
| Multi-agent workflows | More explicit inter-agent trust boundary and delegation tests. |
| Runtime telemetry | Optional collection of tool-call logs, trace events, and workflow decisions from approved targets. |
| Independent assurance | Third-party validation of agentic evaluator thresholds and report claims. |

## Completion rule

This plan remains complete only for the current self-hosted/internal readiness scope. Any stronger wording must wait for approved-environment validation and independent assurance.
