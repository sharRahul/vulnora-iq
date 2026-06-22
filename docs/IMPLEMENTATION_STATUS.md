# Implementation Status

This document separates current working capability from roadmap items so users can understand what is ready today.

## Current working capability

| Area | Status | Notes |
| --- | --- | --- |
| Python package scaffold | Working | Version `1.1.0` installs as a Python package with CLI entry points for assessment, Web UI, dashboard generation, report diffing, benchmark runs, trend outputs, ATLAS refresh, and release package building. |
| Modern Web UI | Working starter | `webui/server.py` and `webui/static/` provide a browser console for launching scans, realtime progress via Server-Sent Events, completed dashboard views, scan history, and artifact downloads. |
| Demo target | Working | The default `demo` target uses an in-memory echo client and requires no external API keys. |
| Local demo targets | Working starter | `examples/local_demo_targets/` contains a safe HTTP JSON target and a control-gap fixture for local demonstration and tests. |
| Configured target adapters | Working starter | `integrations/adapters.py` supports chat-completions-compatible, Ollama-style generate, webhook JSON, and HTTP JSON endpoints, all gated by explicit authorisation. |
| Profiles | Working | `baseline`, `rag`, `agent`, and `full` profiles are defined in `config/attack_profiles.yaml`. |
| Scanner | Working | The scanner loads config, selects a profile, runs configured modules, scores findings, attaches metadata, evaluates policy, and returns a scan result. |
| Module plugin interface | Working starter | `modules/base.py`, `modules/starter.py`, and `modules/registry.py` provide a formal module protocol, starter module implementation, and registry lookup. |
| Payload libraries | Working starter | `core/payload_loader.py` loads safe YAML payload libraries from `payloads/` and maps them to module names. |
| Non-demo authorisation gate | Working | Configured targets outside demo mode require the explicit CLI authorisation flag. |
| Policy-as-code | Working starter | Policy YAML is evaluated by `core/policy_engine.py` for sensitive marker checks, severity thresholds, agent runtime governance, RAG corpus/retrieval integrity, approval gates, and scoped exceptions. |
| Policy exceptions | Working starter | `config/policy_exceptions.yaml` and `core/exception_registry.py` support owner, reason, expiry, target, profile, approval reference, and compensating control metadata. |
| Approval evidence validation | Working starter | `config/approval_evidence.yaml` and `core/approval_evidence.py` validate approval references and local SHA-256 integrity signatures before exceptions suppress policy outcomes. |
| Report generation | Working | Markdown, JSON, and SARIF-style reports include findings, evidence, and policy evaluation. |
| Report diffing | Working starter | `reports/report_diff.py` compares two structured JSON reports, emits JSON/Markdown diffs, and can fail on regression. |
| Policy trend tracking | Working starter | `reports/policy_trends.py` builds JSON/Markdown trend summaries across assessment reports. |
| Diff trend dashboards | Working starter | `dashboards/diff_trend_dashboard.py` builds Markdown/HTML dashboards from report-diff files. |
| Dashboard generation | Working | Markdown and HTML dashboards are generated from the structured JSON report. |
| Release packaging | Working starter | `config/release_package.yaml` and `scripts/build_release_package.py` package safe demo outputs and non-sensitive examples into a ZIP artifact. |
| Benchmarks | Working starter | `benchmarks/benchmark_suite.yaml` and `benchmarks/run_benchmarks.py` provide repeatable local regression checks. |
| HTTP JSON target adapter | Working starter | The original HTTP JSON adapter remains available for explicitly authorised local or owned targets. |
| OWASP LLM 2025 mapping | Partial | Checks are mapped to OWASP LLM 2025 IDs in config and module metadata. |
| MITRE ATLAS mapping | Working starter | `config/mitre_atlas_mapping.yaml` and `core/mitre_atlas.py` validate a local ATLAS mapping catalog and populate starter findings with AML technique IDs. |
| ATLAS refresh tooling | Working starter | `config/atlas_refresh.yaml` and `scripts/refresh_mitre_atlas.py` can refresh local technique metadata from a local ATLAS YAML fixture or configured source URL. |
| RAG corpus manifest validation | Working starter | `config/rag_corpus_manifest.yaml` and `rag_testing/corpus_manifest.py` validate source metadata, approvals, hashes, and access groups. |
| RAG retrieval testing | Working starter | `config/rag_retrieval_scenarios.yaml` and `rag_testing/retrieval_harness.py` validate expected retrieval, access boundaries, approved sources, and source-trust scoring. |
| Agent runtime governance | Working starter | `config/agent_runtime.yaml` and `agent_testing/runtime_manifest.py` validate tool allowlists, high-impact approvals, memory integrity settings, and orchestration plan requirements. |
| Agent execution testing | Working starter | `config/agent_execution_scenarios.yaml` and `agent_testing/execution_harness.py` validate simulated tool calls, approval points, memory writes, integrity references, and rollback-plan coverage. |
| CI | Working starter | GitHub Actions installs the package, runs tests across supported Python versions, runs baseline/RAG/agent smoke assessments, generates report diffs, trend outputs, benchmarks, builds the release package, and uploads artifacts. |

## Current safe usage

Run the Web UI:

```bash
llm-vapt-web --host 127.0.0.1 --port 8787
```

Use the CLI demo mode:

```bash
python scripts/run_scan.py --target demo --profile baseline
```

Compare two structured JSON reports:

```bash
python -m reports.report_diff --baseline reports/output/baseline.json --current reports/output/current.json
```

Build policy and diff trends:

```bash
python -m reports.policy_trends --input-dir reports/output
python -m dashboards.diff_trend_dashboard --input-dir reports/output
```

Run benchmarks:

```bash
python -m benchmarks.run_benchmarks --manifest benchmarks/benchmark_suite.yaml --fail-on-regression
```

Build a safe local release package after generating demo outputs:

```bash
python scripts/build_release_package.py --manifest config/release_package.yaml
```

For any configured target outside demo mode:

1. Confirm the target is owned by you or explicitly approved for assessment.
2. Replace the placeholder endpoint in `config/targets.yaml`.
3. Set any required token environment variable.
4. Run with the CLI authorisation flag or tick the Web UI authorisation confirmation.
5. Store reports securely and review evidence before sharing.

## Remaining roadmap

1. Add authentication and role separation for hosted multi-user Web UI deployments.
2. Add persistent job storage instead of in-memory Web UI scan history.
3. Add deeper production-specific adapters once real authorised target contracts are known.
4. Expand benchmark corpora with more local safe fixtures.
5. Add richer HTML branding and export packaging.
6. Add package metadata validation before release.
7. Add scheduled ATLAS refresh workflows if maintainers want automated external data updates.

## Documentation rule

README claims should stay aligned to this file. If a capability is only a starter, placeholder, or roadmap item, mark it as such in both places.
