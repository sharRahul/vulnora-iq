# Implementation Status

This document separates current working capability from roadmap items so users can understand what is ready today.

## Current working capability

| Area | Status | Notes |
| --- | --- | --- |
| Python package scaffold | Working | The project installs as a Python package with CLI entry points for assessment, dashboard generation, and report diffing. |
| Demo target | Working | The default `demo` target uses an in-memory echo client and requires no external API keys. |
| Profiles | Working | `baseline`, `rag`, `agent`, and `full` profiles are defined in `config/attack_profiles.yaml`. |
| Scanner | Working | The scanner loads config, selects a profile, runs configured modules, scores findings, attaches metadata, evaluates policy, and returns a scan result. |
| Module plugin interface | Working starter | `modules/base.py`, `modules/starter.py`, and `modules/registry.py` provide a formal module protocol, starter module implementation, and registry lookup. |
| Payload libraries | Working starter | `core/payload_loader.py` loads safe YAML payload libraries from `payloads/` and maps them to module names. |
| Non-demo authorisation gate | Working | Configured targets outside demo mode require the explicit CLI authorisation flag. |
| Policy-as-code | Working starter | Policy YAML is evaluated by `core/policy_engine.py` for sensitive marker checks, severity thresholds, agent runtime governance, RAG corpus integrity metadata, approval gates, and scoped exceptions. |
| Policy exceptions | Working starter | `config/policy_exceptions.yaml` and `core/exception_registry.py` support owner, reason, expiry, target, profile, approval reference, and compensating control metadata. |
| Report generation | Working | Markdown, JSON, and SARIF-style reports include findings, evidence, and policy evaluation. |
| Report diffing | Working starter | `reports/report_diff.py` compares two structured JSON reports, emits JSON/Markdown diffs, and can fail on regression. |
| Dashboard generation | Working | Markdown and HTML dashboards are generated from the structured JSON report. |
| HTTP JSON target adapter | Starter | A minimal HTTP JSON adapter exists for explicitly authorised local or owned targets. |
| OWASP LLM 2025 mapping | Partial | Checks are mapped to OWASP LLM 2025 IDs in config and module metadata. |
| MITRE ATLAS mapping | Working starter | `config/mitre_atlas_mapping.yaml` and `core/mitre_atlas.py` validate a local ATLAS mapping catalog and populate starter findings with AML technique IDs. |
| RAG corpus manifest validation | Working starter | `config/rag_corpus_manifest.yaml` and `rag_testing/corpus_manifest.py` validate source metadata, approvals, hashes, and access groups. |
| RAG retrieval testing | Starter | RAG-related profile entries, payload libraries, and manifest policy checks exist, but retrieval harnesses are not complete. |
| Agent runtime governance | Working starter | `config/agent_runtime.yaml` and `agent_testing/runtime_manifest.py` validate tool allowlists, high-impact approvals, memory integrity settings, and orchestration plan requirements. |
| Agent testing | Starter | Agent-related profile entries, payload libraries, and runtime policy checks exist, but simulated execution and multi-agent harnesses are not complete. |
| CI | Working starter | GitHub Actions installs the package, runs tests across supported Python versions, and runs a demo smoke assessment producing Markdown, JSON, SARIF, and dashboard artifacts. |

## Current safe usage

Use the demo mode first:

```bash
python scripts/run_scan.py --target demo --profile baseline
```

This produces:

- `reports/output/scan-report.md`
- `reports/output/scan-report.json`
- `reports/output/scan-report.sarif`
- `reports/output/dashboard.md`
- `reports/output/dashboard.html`

Compare two structured JSON reports:

```bash
python -m reports.report_diff --baseline reports/output/baseline.json --current reports/output/current.json
```

For any configured target outside demo mode:

1. Confirm the target is owned by you or explicitly approved for assessment.
2. Replace the placeholder endpoint in `config/targets.yaml`.
3. Set any required token environment variable.
4. Run with the CLI authorisation flag.
5. Store reports securely and review evidence before sharing.

## Gap backlog

1. Add deeper RAG retrieval harnesses and source-trust scoring.
2. Add simulated agent execution, memory-integrity, and orchestration harnesses.
3. Add release versioning and packaged example outputs.
4. Add richer target adapters for common enterprise patterns.
5. Add example vulnerable local demo applications.
6. Add benchmark datasets for repeatable regression testing.
7. Add signed approval evidence validation for exceptions.
8. Add policy-result trend tracking across repeated runs.
9. Add automatic ATLAS data refresh tooling.
10. Add report diff trend dashboards.

## Documentation rule

README claims should stay aligned to this file. If a capability is only a starter, placeholder, or roadmap item, mark it as such in both places.
