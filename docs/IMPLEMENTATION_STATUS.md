# Implementation Status

This document separates current working capability from roadmap items so users can understand what is ready today.

## Current working capability

| Area | Status | Notes |
| --- | --- | --- |
| Python package scaffold | Working | The project installs as a Python package with a CLI entry point. |
| Demo target | Working | The default `demo` target uses an in-memory echo client and requires no external API keys. |
| Profiles | Working | `baseline`, `rag`, `agent`, and `full` profiles are defined in `config/attack_profiles.yaml`. |
| Scanner | Working | The scanner loads config, selects a profile, runs configured starter checks, scores findings, and returns a scan result. |
| Report generation | Working | Markdown reports include executive summary, severity counts, findings, recommendations, and evidence JSON. |
| Non-demo authorisation gate | Working | Configured targets outside demo mode require the explicit CLI authorisation flag. |
| HTTP JSON target adapter | Starter | A minimal HTTP JSON adapter exists for explicitly authorised local or owned targets. |
| OWASP LLM 2025 mapping | Partial | Checks are mapped to OWASP LLM 2025 IDs in config and module definitions. |
| MITRE ATLAS mapping | Pending | A validated ATLAS mapping table still needs to be added. Existing output marks this as pending rather than complete. |
| Policy-as-code | Partial | Policy YAML exists, and the authorisation gate is enforced. Other policy decisions are not fully enforced yet. |
| RAG testing | Starter | RAG-related profile entries exist, but corpus fixtures and retrieval harnesses are not complete. |
| Agent testing | Starter | Agent-related profile entries exist, but full tool, memory, and multi-agent harnesses are not complete. |
| Dashboards | Not started | Dashboard helpers are listed in the structure but do not yet provide a complete visual workflow. |

## Current safe usage

Use the demo mode first:

```bash
python scripts/run_scan.py --target demo --profile baseline
```

For any configured target outside demo mode:

1. Confirm the target is owned by you or explicitly approved for assessment.
2. Replace the placeholder endpoint in `config/targets.yaml`.
3. Set any required token environment variable.
4. Run with the CLI authorisation flag.
5. Store reports securely and review evidence before sharing.

## Gap backlog

1. Add validated MITRE ATLAS mapping data.
2. Add fixture-based tests for scanner, profiles, report generation, and non-demo authorisation behaviour.
3. Add a formal module plugin interface instead of hard-coded starter definitions.
4. Add payload library schemas and safe local payload fixtures.
5. Add RAG corpus fixtures, retrieval checks, source-trust scoring, and corpus integrity validation.
6. Add agent tool-permission, memory-integrity, and orchestration harnesses.
7. Enforce all policy decisions in `config/policies.yaml`, not just authorisation.
8. Add JSON report export and optional SARIF-style output for CI use.
9. Add dashboard output for profile coverage, severity, and OWASP category summaries.
10. Add contributor docs for writing new modules and target adapters.

## Documentation rule

README claims should stay aligned to this file. If a capability is only a starter, placeholder, or roadmap item, mark it as such in both places.
