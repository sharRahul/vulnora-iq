# Implementation Status

This document separates current working capability from roadmap items so users can understand what is ready today.

> **Current maturity:** VulnoraIQ version `0.0.1.8` is an early development build. It is suitable for local demos, framework development, UI workflow validation, functional acceptance testing, report-pipeline testing, and controlled production-testing readiness evaluation. It is **not ready for real-world VAPT testing or production security assessment use**.

> **Important limitation:** OWASP LLM 2025 coverage now has implementation specs, safe starter oracle coverage, deterministic local evaluator primitives, and local good/bad fixtures for all 10 categories. MITRE ATLAS AI technique coverage now has a source-driven planning matrix and unmapped backlog preservation, but the matrix is not the same as active production-validated detection coverage. MITRE ATLAS-derived documentation is tracked in `THIRD_PARTY_NOTICES.md`. Treat output as development evidence, not validated security assurance.

## Seven-phase implementation status

| Phase | Status | Completed implementation |
| --- | --- | --- |
| Phase 1 — OWASP depth | Working-alpha starter | `docs/owasp/` now contains implementation specs for all 10 OWASP LLM 2025 categories. |
| Phase 2 — Safe demo fixtures | Working-alpha starter | `examples/local_demo_targets/owasp_fixture_targets.py` models local good/bad control behaviour for all 10 categories. |
| Phase 3 — Stronger evaluators | Working-alpha starter | `core/evaluators.py` adds deterministic local evaluators for text checks, schema checks, source access, provenance, approval, citations, action boundaries, resource limits, and manual review. |
| Phase 4 — Contract-tested adapters | Working starter | `config/target_contracts.yaml` and `integrations/contract_validation.py` validate configured target adapter shapes before authorised testing. |
| Phase 5 — Web UI hardening foundations | Working starter | `webui/hosted_server.py`, `webui/auth.py`, and `webui/persistent_jobs.py` add hosted entry point, role-aware auth hooks, and persistent JSON job storage. |
| Phase 6 — Report quality and presentation | Working starter | Report generation includes structured evidence; `reports/html_export_package.py` builds a branded export bundle; `docs/assets/vulnoraiq-dashboard-example.svg` provides a README dashboard example image. |
| Phase 7 — Release gates | Working starter | `scripts/validate_package_metadata.py` checks package/version/CLI/docs/fixtures/evaluators/functional assets; `scripts/validate_production_testing_readiness.py` adds a production-testing readiness gate; CI runs tests, metadata checks, readiness checks, demo scan, and functional acceptance output generation. |

## Current working capability

| Area | Status | Notes |
| --- | --- | --- |
| Python package scaffold | Working starter | VulnoraIQ version `0.0.1.8` installs as a Python package with CLI entry points for assessment, Web UI, dashboard generation, report diffing, benchmark runs, functional acceptance testing, production-testing readiness validation, trend outputs, ATLAS refresh, ATLAS matrix generation, HTML export, package metadata validation, and release package building. |
| Functional acceptance runner | Working starter | `scripts/run_functional_test.py` runs a safe demo/baseline assessment, writes Markdown/JSON/SARIF/dashboard outputs, validates required fields, verifies the non-production validation marker, checks OWASP oracle category coverage, writes a JSON summary, and refreshes the dashboard example SVG. |
| Production-testing readiness gate | Working starter | `scripts/validate_production_testing_readiness.py` validates metadata, target contracts, OWASP benchmark fixtures, MITRE ATLAS mapping, OWASP oracle coverage, non-demo authorisation blocking, docs/CI wiring, and can run the safe functional acceptance path with `--run-functional`. |
| Dashboard example image | Working starter | `docs/assets/vulnoraiq-dashboard-example.svg` is referenced in `README.md` as a visual preview of the dashboard style generated from the functional test path. |
| Modern Web UI | Working starter | `webui/hosted_server.py`, `webui/auth.py`, `webui/persistent_jobs.py`, and `webui/static/` provide a browser console for launching demo scans, realtime progress via Server-Sent Events, completed dashboard views, scan history, role-aware auth hooks, persistent JSON job storage, and artifact downloads. |
| Demo target | Working | The default `demo` target uses an in-memory echo client and requires no external API keys. |
| Local demo targets | Working-alpha starter | `examples/local_demo_targets/` contains safe HTTP JSON, control-gap, and OWASP good/bad fixture targets for local demonstration and tests. |
| Configured target adapters | Working starter | `integrations/adapters.py`, `config/target_contracts.yaml`, and `integrations/contract_validation.py` support chat-completions-compatible, Ollama-style generate, webhook JSON, and HTTP JSON endpoint shapes, with contract-shape validation and explicit authorisation. |
| Profiles | Working starter | `baseline`, `rag`, `agent`, and `full` profiles are defined in `config/attack_profiles.yaml`, but coverage depth is still starter-level. |
| Scanner | Working starter | The scanner loads config, selects a profile, runs configured modules, scores findings, attaches metadata, evaluates policy, attaches OWASP oracle coverage metadata, and returns a scan result. Findings are not yet validated as production-grade security assertions. |
| Module plugin interface | Working starter | `modules/base.py`, `modules/starter.py`, and `modules/registry.py` provide a formal module protocol, starter module implementation, registry lookup, and structured oracle-backed evidence. |
| Deterministic evaluators | Working-alpha starter | `core/evaluators.py` provides local evaluator primitives that can be reused by OWASP checks, fixtures, CI, and future report confidence scoring. |
| Payload libraries | Working starter | `core/payload_loader.py` loads safe YAML payload libraries from `payloads/` and maps them to module names. |
| Non-demo authorisation gate | Working | Configured targets outside demo mode require the explicit CLI authorisation flag. |
| Policy-as-code | Working starter | Policy YAML is evaluated by `core/policy_engine.py` for sensitive marker checks, severity thresholds, agent runtime governance, RAG corpus/retrieval integrity, approval gates, and scoped exceptions. |
| Policy exceptions | Working starter | `config/policy_exceptions.yaml` and `core/exception_registry.py` support owner, reason, expiry, target, profile, approval reference, and compensating control metadata. |
| Approval evidence validation | Working starter | `config/approval_evidence.yaml` and `core/approval_evidence.py` validate approval references and local SHA-256 integrity signatures before exceptions suppress policy outcomes. |
| OWASP LLM 2025 implementation specs | Working-alpha starter | `docs/owasp/` defines scope, safe strategy, expected good/bad behaviour, evidence, evaluators, severity rationale, and working criteria for all 10 categories. |
| OWASP LLM 2025 oracle coverage | Working starter | `config/owasp_oracles.yaml` and `core/evidence_model.py` provide safe starter oracle coverage for all 10 OWASP LLM 2025 categories. |
| MITRE ATLAS AI matrix | Working starter | `docs/MITRE_ATLAS_AI_MATRIX.md` records the official-source planning path and includes a third-party notice link. `scripts/generate_mitre_atlas_matrix.py` generates tactic and technique rows with OWASP mapping, VulnoraIQ coverage area, implementation status, and `Unmapped / map later` backlog preservation. |
| Third-party notices | Working starter | `THIRD_PARTY_NOTICES.md` records MITRE ATLAS attribution, Apache License 2.0 reference, source links, and no-endorsement wording. |
| Evidence model and test oracles | Working starter | `core/evidence_model.py` creates structured `InteractionEvidence` and `OracleResult` records for module output and report evidence. |
| Report generation | Working starter | Markdown, JSON, and SARIF-style reports include findings, structured evidence, oracle results, and policy evaluation, but conclusions are only as mature as the starter checks. |
| Report diffing | Working starter | `reports/report_diff.py` compares two structured JSON reports, emits JSON/Markdown diffs, and can fail on regression. |
| Policy trend tracking | Working starter | `reports/policy_trends.py` builds JSON/Markdown trend summaries across assessment reports. |
| Diff trend dashboards | Working starter | `dashboards/diff_trend_dashboard.py` builds Markdown/HTML dashboards from report-diff files. |
| Dashboard generation | Working starter | Markdown and HTML dashboards are generated from the structured JSON report. |
| Branded HTML export packaging | Working starter | `config/report_branding.yaml` and `reports/html_export_package.py` package HTML dashboards and supporting JSON/Markdown/SARIF artifacts into a branded export ZIP. |
| Release packaging | Working starter | `config/release_package.yaml` and `scripts/build_release_package.py` package safe demo outputs, third-party notices, dashboard example image, functional runner, and non-sensitive examples into a ZIP artifact. |
| Benchmarks | Working starter | `benchmarks/benchmark_suite.yaml`, `benchmarks/fixtures/owasp_starter_fixture.yaml`, `benchmarks/fixture_validation.py`, and `benchmarks/run_benchmarks.py` provide repeatable local regression checks and fixture coverage for all 10 OWASP starter categories. |
| HTTP JSON target adapter | Working starter | The original HTTP JSON adapter remains available, with target-contract validation required before production assessment. |
| MITRE ATLAS mapping | Working starter | `config/mitre_atlas_mapping.yaml` and `core/mitre_atlas.py` validate a local ATLAS mapping catalog and populate starter findings with AML technique IDs. |
| ATLAS refresh tooling | Working starter | `config/atlas_refresh.yaml`, `config/mitre_atlas_source_fixture.yaml`, `scripts/refresh_mitre_atlas.py`, and `.github/workflows/atlas-refresh.yml` provide manual and scheduled ATLAS refresh validation using a safe local fixture path in CI. |
| RAG corpus manifest validation | Working starter | `config/rag_corpus_manifest.yaml` and `rag_testing/corpus_manifest.py` validate source metadata, approvals, hashes, and access groups. |
| RAG retrieval testing | Working starter | `config/rag_retrieval_scenarios.yaml` and `rag_testing/retrieval_harness.py` validate expected retrieval, access boundaries, approved sources, and source-trust scoring. |
| Agent runtime governance | Working starter | `config/agent_runtime.yaml` and `agent_testing/runtime_manifest.py` validate tool allowlists, high-impact approvals, memory integrity settings, and orchestration plan requirements. |
| Agent execution testing | Working starter | `config/agent_execution_scenarios.yaml` and `agent_testing/execution_harness.py` validate simulated tool calls, approval points, memory writes, integrity references, and rollback-plan coverage. |
| Package metadata validation | Working starter | `scripts/validate_package_metadata.py` verifies package name, framework display name, version consistency, CLI entry points, README maturity warnings, OWASP docs, MITRE ATLAS matrix doc, third-party notices, functional test assets, production-testing readiness assets, evaluator suite, and OWASP fixture target before release. |
| CI | Working starter | GitHub Actions installs the package across Python 3.10, 3.11, and 3.12, runs tests, validates package metadata, runs the production-testing readiness gate, performs a demo scan, and runs the functional acceptance readiness path on Python 3.12 with readiness artifacts uploaded. |

## Current safe usage

Run the Web UI:

```bash
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Use the CLI demo mode:

```bash
vulnoraiq --target demo --profile baseline
```

Run functional acceptance testing:

```bash
vulnoraiq-functional-test --output-dir reports/output/functional-test --screenshot docs/assets/vulnoraiq-dashboard-example.svg
```

Run production-testing readiness validation:

```bash
vulnoraiq-production-readiness --run-functional --output-dir reports/output/production-readiness --screenshot docs/assets/vulnoraiq-dashboard-example.svg
```

Run benchmarks and release gates:

```bash
vulnoraiq-benchmark --manifest benchmarks/benchmark_suite.yaml --fail-on-regression
vulnoraiq-validate-package
```

Build export and release packages:

```bash
vulnoraiq-html-export --input-dir reports/output
vulnoraiq-package --manifest config/release_package.yaml
```

For any configured target outside demo mode:

1. Confirm the target is owned by you or explicitly approved for assessment.
2. Replace the placeholder endpoint in `config/targets.yaml`.
3. Validate target contracts before testing.
4. Set any required token environment variable.
5. Run with the CLI authorisation flag or tick the Web UI authorisation confirmation.
6. Treat results as experimental until OWASP and ATLAS coverage checks are validated.
7. Store reports securely and review evidence before sharing.

## Implementation roadmap status

All seven phases requested for the previous pass have been completed as **working-alpha starter** or **working starter** capabilities. The current pass adds a production-testing readiness gate, a CI readiness path, and a functional acceptance path with README dashboard example so testing can move toward repeatable production-readiness evaluation.

The next phase should deepen the production-readiness suite by adding OWASP scenario manifests, adapter evidence-contract tests, report schema assertions, dashboard regression checks, and calibrated checks against intentionally vulnerable local AI app fixtures.

## Documentation rule

README claims should stay aligned to this file. If a capability is only a starter, placeholder, partial, experimental, or roadmap item, mark it as such in both places.
