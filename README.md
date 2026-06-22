# VulnoraIQ

**VulnoraIQ** is an early-stage AI security assessment platform for **LLM applications, RAG pipelines, AI agents, and orchestration layers**.

> **Current maturity:** version `0.2.0` is ready for **controlled internal enterprise deployment**. It is **not recommended for unsupervised public internet exposure or multi-tenant SaaS hosting** without additional controls (OIDC/SSO, horizontal scaling, penetration testing, tenant isolation). See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for the production checklist, [`docs/PRODUCTION_READINESS_SCORECARD.md`](docs/PRODUCTION_READINESS_SCORECARD.md) for scored readiness, [`docs/PRODUCTION_HARDENING_BACKLOG.md`](docs/PRODUCTION_HARDENING_BACKLOG.md) for remaining gaps, and [`docs/ASSESSMENT_ASSURANCE.md`](docs/ASSESSMENT_ASSURANCE.md) for scanner/evaluator assurance limitations.

> **Important limitation:** OWASP LLM 2025 coverage now has safe starter oracle coverage, implementation specs, evaluator primitives, and local good/bad fixtures for all 10 categories. MITRE ATLAS AI technique coverage has a source-driven documentation matrix, but not every listed technique is implemented as an active check yet. Unmapped tactics and techniques must still be listed as `Unmapped / map later`. Treat all scan output as framework-development evidence, not validated security assurance.

> **Responsible use only:** run this platform only against systems you own or are explicitly authorised to assess. The default demo target is safe and local. Configured non-demo targets require an explicit authorisation flag. Auth is enabled by default and fail-closed; configure real tokens before exposing the web UI beyond localhost.

## Dashboard example

The image below is generated from the safe local functional test path and shows the intended dashboard style for demo/report workflow testing.

![VulnoraIQ dashboard example](docs/assets/vulnoraiq-dashboard-example.svg)

## Why this exists

AI application security needs more than prompt-level checks. VulnoraIQ provides a practical structure for assessing model endpoints, retrieval layers, tools, memory, orchestration, governance controls, and reporting.

The current implementation provides:

- Modern hosted Web UI with realtime progress (SSE), role-aware auth (env tokens / trusted proxy headers), production SQLite job persistence with WAL mode, CSRF protection, rate limiting, security headers, audit logging, executive dashboards, scan history, artifact download, and Prometheus metrics
- Functional acceptance runner that generates demo reports, validates required output fields, and refreshes the README dashboard example image
- OWASP LLM 2025 implementation specs in `docs/owasp/` for all 10 categories
- MITRE ATLAS Matrix for AI planning register in `docs/MITRE_ATLAS_AI_MATRIX.md`
- Source-driven ATLAS matrix generator with explicit `Unmapped / map later` backlog preservation
- Third-party notices for MITRE ATLAS-derived documentation and planning data
- OWASP LLM 2025 safe starter oracle coverage for all 10 categories
- Deterministic local evaluator primitives and local good/bad OWASP fixture targets
- Structured evidence records and oracle results for module interactions
- MITRE ATLAS mapping catalog with AML technique IDs, local source fixture, and scheduled refresh validation workflow
- Safe demo target with no external API keys
- Local demo HTTP target and control-gap fixture examples
- Baseline, RAG, agent, and full profile definitions
- Module protocol, starter modules, and registry-based module lookup
- Safe YAML payload libraries mapped to module names
- Scanner, scoring, result model, policy evaluation, scoped policy exceptions, and approval evidence validation
- RAG corpus manifest validation and RAG retrieval scenario validation with source-trust scoring
- Agent runtime governance and simulated execution validation for tools, memory, approvals, and rollback planning
- Configured target adapter contracts for HTTP JSON, chat-completions-compatible, Ollama-style generate, and webhook JSON endpoint shapes
- Markdown, JSON, SARIF-style, Markdown dashboard, HTML dashboard, trend, diff, and branded HTML export outputs
- Benchmark regression suite and OWASP starter fixture corpus
- Safe release-package builder for demo outputs and non-sensitive examples
- Package metadata release gate that checks OWASP docs, MITRE ATLAS matrix docs, third-party notices, functional test assets, evaluators, fixtures, version alignment, and CLI entries
- Explicit non-demo authorisation gate
- Python CI across supported versions with tests, metadata gates, target contract validation, benchmark fixture validation, functional acceptance testing, scan smoke tests, trends, exports, and release artifacts

The next phase should go through `docs/owasp/` and `docs/MITRE_ATLAS_AI_MATRIX.md` category by category and decide the deeper check logic, evaluator thresholds, fixture realism, and report language needed before any real-world VAPT readiness claim.

## OWASP LLM 2025 coverage

| OWASP ID | Risk | Module status |
|---|---|---|
| LLM01:2025 | Prompt Injection | Working-alpha spec + safe oracle + local fixture |
| LLM02:2025 | Sensitive Information Disclosure | Working-alpha spec + safe oracle + local fixture |
| LLM03:2025 | Supply Chain | Working-alpha spec + safe oracle + local fixture |
| LLM04:2025 | Data and Model Poisoning | Working-alpha spec + safe oracle + local fixture |
| LLM05:2025 | Improper Output Handling | Working-alpha spec + safe oracle + local fixture |
| LLM06:2025 | Excessive Agency | Working-alpha spec + safe oracle + local fixture |
| LLM07:2025 | System Prompt Leakage | Working-alpha spec + safe oracle + local fixture |
| LLM08:2025 | Vector and Embedding Weaknesses | Working-alpha spec + safe oracle + local fixture |
| LLM09:2025 | Misinformation | Working-alpha spec + safe oracle + local fixture |
| LLM10:2025 | Unbounded Consumption | Working-alpha spec + safe oracle + local fixture |

## MITRE ATLAS coverage planning

Use [`docs/MITRE_ATLAS_AI_MATRIX.md`](docs/MITRE_ATLAS_AI_MATRIX.md) as the planning register for adding ATLAS tactics, techniques, and sub-techniques into VulnoraIQ. The source-driven generator adds OWASP and VulnoraIQ candidate mapping columns. If a tactic or technique cannot be confidently mapped, it is still listed as `Unmapped / map later` so it can be reviewed later.

Regenerate the matrix from the official MITRE ATLAS data source:

```bash
vulnoraiq-generate-atlas-matrix \
  --source https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.05.yaml \
  --output docs/MITRE_ATLAS_AI_MATRIX.md
```

## Architecture

```text
Operator Browser: Hosted Web UI | CLI | CI
        ↓
Auth / Role Layer: local token config | viewer | analyst | admin
        ↓
Target AI Systems: demo echo target | local demo app | configured HTTP/Chat/Ollama/Webhook targets
        ↓
Integration Layer: DemoEchoClient | HttpJsonTargetClient | ChatCompletionsTargetClient | OllamaGenerateTargetClient | WebhookJsonTargetClient | TargetContractValidator
        ↓
Core Engine: Scanner | Test Runner | Results Engine | Risk Scoring | Policy Engine | OWASP Oracle Registry | Local Evaluator Suite | MITRE ATLAS Mapping
        ↓
Module Layer: AssessmentModule protocol | ModuleRegistry | starter modules | structured evidence model
        ↓
Payload Layer: safe YAML payload libraries
        ↓
Governance Layer: policy rules | exceptions | approval evidence | RAG manifest | RAG retrieval scenarios | agent runtime manifest | agent execution scenarios | ATLAS mapping
        ↓
Assessment Profiles: baseline | rag | agent | full
        ↓
Outputs: Web dashboard | Markdown | JSON | SARIF-style | dashboards | report diff | trends | benchmarks | HTML export | release package
```

## Repository structure

```text
vulnoraiq/
├── .github/workflows/       # Python CI and ATLAS refresh validation
├── benchmarks/              # Regression benchmark suite, fixtures, and runner
├── config/                  # Targets, profiles, policies, manifests, mappings, scenarios, auth, branding
├── core/                    # Scanner, runner, scoring, policy, exceptions, approvals, mapping, evidence, evaluators, results model
├── docs/MITRE_ATLAS_AI_MATRIX.md # MITRE ATLAS AI planning matrix
├── docs/assets/             # README dashboard example image
├── docs/owasp/              # OWASP LLM 2025 implementation specs
├── examples/                # Safe local demo targets and OWASP fixtures
├── integrations/            # Demo, HTTP JSON, chat, Ollama-style, webhook adapters, and contract validation
├── modules/                 # Module protocol, registry, and starter modules
├── rag_testing/             # RAG corpus and retrieval validation
├── agent_testing/           # Agent runtime and execution validation
├── payloads/                # Safe payload schema and libraries
├── reports/                 # Markdown, JSON, SARIF-style, diff, policy-trend, and HTML export generation
├── dashboards/              # Markdown, HTML, and diff-trend dashboard generation
├── webui/                   # Hosted Web UI server, auth, persistent jobs, and static frontend
├── tests/                   # Unit tests
├── THIRD_PARTY_NOTICES.md   # Third-party attribution and license notices
└── scripts/                 # CLI entry points, package validation, release package builder, ATLAS refresh, functional test runner
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
vulnoraiq --target demo --profile baseline
```

The demo target uses an in-memory echo client, so the platform can be explored without external API keys.

## Web UI command

```bash
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Set `VULNORAIQ_ENV=production` with a valid `VULNORAIQ_ADMIN_TOKEN` (20+ characters) for production mode:

```bash
VULNORAIQ_ENV=production VULNORAIQ_ADMIN_TOKEN="your-strong-token-here-min-20-chars" vulnoraiq-web
```

Open:

```text
http://127.0.0.1:8787
```

## Functional acceptance test

Run the safe local functional test and refresh the dashboard example asset:

```bash
vulnoraiq-functional-test \
  --output-dir reports/output/functional-test \
  --screenshot docs/assets/vulnoraiq-dashboard-example.svg
```

This runs the demo/baseline workflow, writes Markdown/JSON/SARIF/dashboard outputs, validates required fields and safety metadata, writes a functional test summary, and refreshes the README dashboard SVG.

## Run tests

```bash
pytest -q
```

## Example demo command

```bash
vulnoraiq \
  --target demo \
  --profile baseline \
  --output reports/output/demo-report.md \
  --json-output reports/output/demo-report.json \
  --sarif-output reports/output/demo-report.sarif \
  --dashboard-output reports/output/demo-dashboard.md \
  --html-dashboard-output reports/output/demo-dashboard.html
```

## Configured target command

Only use this for systems you own or are explicitly authorised to assess:

```bash
vulnoraiq \
  --target custom_http_agent \
  --profile baseline \
  --authorised
```

Before running against a configured target, replace the placeholder endpoint in `config/targets.yaml`, validate the target contract, and set any required token environment variable.

## Report, trend, benchmark, and export commands

```bash
vulnoraiq-diff --baseline reports/output/baseline.json --current reports/output/current.json
vulnoraiq-policy-trend --input-dir reports/output
vulnoraiq-diff-trend --input-dir reports/output
vulnoraiq-benchmark --manifest benchmarks/benchmark_suite.yaml --fail-on-regression
vulnoraiq-html-export --input-dir reports/output
vulnoraiq-validate-package
```

## ATLAS refresh command

```bash
vulnoraiq-refresh-atlas --source config/mitre_atlas_source_fixture.yaml --output reports/output/mitre_atlas_mapping.refresh-check.yaml
```

## Release package command

```bash
vulnoraiq-package --manifest config/release_package.yaml
```

The package path defaults to `dist/vulnoraiq-example-package.zip`.

## Configuration highlights

- `docs/MITRE_ATLAS_AI_MATRIX.md`: MITRE ATLAS AI planning matrix and technique implementation register
- `scripts/generate_mitre_atlas_matrix.py`: source-driven matrix generator with unmapped backlog preservation
- `scripts/run_functional_test.py`: functional acceptance runner and dashboard example generator
- `docs/assets/vulnoraiq-dashboard-example.svg`: README dashboard example image
- `THIRD_PARTY_NOTICES.md`: third-party attribution and license notices, including MITRE ATLAS
- `docs/owasp/`: OWASP LLM 2025 implementation specs
- `config/owasp_oracles.yaml`: safe OWASP starter oracle definitions
- `config/mitre_atlas_mapping.yaml`: local MITRE ATLAS technique catalog and module mapping
- `core/evaluators.py`: deterministic local evaluator primitives
- `examples/local_demo_targets/owasp_fixture_targets.py`: local good/bad OWASP fixture target behaviours
- `config/target_contracts.yaml`: target adapter contract definitions
- `config/web_users.yaml`: Web UI auth configuration (use env tokens in production; see `config/web_users.example.yaml`)
- `config/web_users.example.yaml`: template for local auth configuration
- `config/report_branding.yaml`: report/export branding
- `benchmarks/fixtures/owasp_starter_fixture.yaml`: OWASP starter fixture corpus

## Design principles

1. Audit-friendly by default.
2. Safe local demo first.
3. Explicit authorisation for configured targets.
4. System-level starter coverage across LLM, RAG, tool, memory, and orchestration layers.
5. CI/CD-ready direction for prompt, corpus, agent, release-gate, and regression checks.

## License and third-party notices

VulnoraIQ-specific source code and documentation are licensed under this repository's license. See `LICENSE`.

Some documentation and planning data is derived from MITRE ATLAS. MITRE ATLAS data is copyright 2021-2026 MITRE and licensed under the Apache License, Version 2.0. See `THIRD_PARTY_NOTICES.md`.
