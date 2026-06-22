# Implementation Status

This document separates current working capability from roadmap items so users can understand what is ready today.

## Current working capability

| Area | Status | Notes |
| --- | --- | --- |
| Python package scaffold | Working | The project installs as a Python package with CLI entry points for assessment and dashboard generation. |
| Demo target | Working | The default `demo` target uses an in-memory echo client and requires no external API keys. |
| Profiles | Working | `baseline`, `rag`, `agent`, and `full` profiles are defined in `config/attack_profiles.yaml`. |
| Scanner | Working | The scanner loads config, selects a profile, runs configured starter checks, scores findings, attaches metadata, and returns a scan result. |
| Non-demo authorisation gate | Working | Configured targets outside demo mode require the explicit CLI authorisation flag. |
| Policy-as-code | Working starter | Policy YAML is evaluated by `core/policy_engine.py` for sensitive marker checks, agent tool allowlists, RAG corpus integrity metadata, and approval gates. |
| Report generation | Working | Markdown and JSON reports include executive summary, severity counts, findings, evidence JSON, and policy evaluation. |
| Dashboard generation | Working | `dashboards/generate_dashboard.py` generates a Markdown dashboard from a structured JSON report. |
| HTTP JSON target adapter | Starter | A minimal HTTP JSON adapter exists for explicitly authorised local or owned targets. |
| OWASP LLM 2025 mapping | Partial | Checks are mapped to OWASP LLM 2025 IDs in config and module definitions. |
| MITRE ATLAS mapping | Pending | A validated ATLAS mapping table still needs to be added. Existing output marks this as pending rather than complete. |
| RAG testing | Starter | RAG-related profile entries and policy metadata exist, but corpus fixtures and retrieval harnesses are not complete. |
| Agent testing | Starter | Agent-related profile entries and allowlist policy checks exist, but full tool, memory, and multi-agent harnesses are not complete. |
| CI | Working starter | GitHub Actions installs the package, runs tests across supported Python versions, and runs a demo smoke assessment. |

## Current safe usage

Use the demo mode first:

```bash
python scripts/run_scan.py --target demo --profile baseline
```

This produces:

- `reports/output/scan-report.md`
- `reports/output/scan-report.json`
- `reports/output/dashboard.md`

For any configured target outside demo mode:

1. Confirm the target is owned by you or explicitly approved for assessment.
2. Replace the placeholder endpoint in `config/targets.yaml`.
3. Set any required token environment variable.
4. Run with the CLI authorisation flag.
5. Store reports securely and review evidence before sharing.

## Gap backlog

1. Add validated MITRE ATLAS mapping data.
2. Add a formal module plugin interface instead of hard-coded starter definitions.
3. Add payload library schemas and safe local payload fixtures.
4. Add RAG corpus fixtures, retrieval checks, source-trust scoring, and corpus integrity validation.
5. Add agent tool-permission, memory-integrity, and orchestration harnesses.
6. Expand policy-as-code to support severity thresholds, exception files, and signed approvals.
7. Add SARIF-style output for CI use.
8. Add HTML dashboard output.
9. Add contributor docs for writing new modules and target adapters.
10. Add release versioning and packaged example outputs.

## Documentation rule

README claims should stay aligned to this file. If a capability is only a starter, placeholder, or roadmap item, mark it as such in both places.
