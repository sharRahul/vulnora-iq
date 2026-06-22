# Vulnora-IQ

**Vulnora-IQ** is an early-stage AI security assessment and VAPT platform for **LLM applications, RAG pipelines, AI agents, and orchestration layers**.

> **Current maturity:** version `0.0.1.2` is an early development build. It is useful for local demos, UI workflow validation, report-pipeline development, and safe framework testing. It is **not ready for real-world VAPT testing or production assessment use** yet.

> **Important limitation:** OWASP LLM 2025 coverage is only partially mapped and currently implemented as starter checks. Treat all scan output as framework-development evidence, not as validated security assurance.

> **Responsible use only:** run this platform only against systems you own or are explicitly authorised to assess. The default demo target is safe and local. Configured non-demo targets require an explicit authorisation flag.

## Why this exists

AI application security needs more than prompt-level checks. Vulnora-IQ provides a practical structure for assessing model endpoints, retrieval layers, tools, memory, orchestration, governance controls, and reporting.

The current implementation provides:

- Modern Web UI for launching scans, realtime progress, executive dashboards, scan history, and artifact download
- OWASP LLM 2025 starter mapping
- MITRE ATLAS mapping catalog with AML technique IDs and refresh tooling
- Safe demo target with no external API keys
- Local demo HTTP target and control-gap fixture examples
- Baseline, RAG, agent, and full profile definitions
- Module protocol, starter modules, and registry-based module lookup
- Safe YAML payload libraries mapped to module names
- Scanner, scoring, result model, policy evaluation, and scoped policy exceptions
- Signed approval evidence validation for policy exceptions
- RAG corpus manifest validation
- RAG retrieval scenario validation and source-trust scoring
- Agent runtime governance validation
- Agent execution scenario validation for tools, memory, approvals, and rollback planning
- Richer configured target adapters: HTTP JSON, chat-completions-compatible, Ollama-style generate, and webhook JSON
- Markdown, JSON, and SARIF-style reports with evidence details
- Markdown and HTML dashboard generation
- JSON/Markdown report diffing between assessment runs
- Policy-result trend tracking
- Report-diff trend dashboards
- Benchmark regression suite
- Safe release-package builder for demo outputs and non-sensitive examples
- Explicit non-demo authorisation gate
- Python CI across supported versions with baseline, RAG, agent, diff, benchmark, trend, and release-package artifacts

The roadmap now focuses on completing OWASP LLM 2025 coverage, validating checks, deeper production adapters, larger benchmark corpora, richer report branding, and automated release governance.

## OWASP LLM 2025 coverage

| OWASP ID | Risk | Module status |
|---|---|---|
| LLM01:2025 | Prompt Injection | Starter check with ATLAS mapping |
| LLM02:2025 | Sensitive Information Disclosure | Starter check with ATLAS mapping |
| LLM03:2025 | Supply Chain | Starter check with ATLAS mapping |
| LLM04:2025 | Data and Model Poisoning | Starter check with ATLAS mapping |
| LLM05:2025 | Improper Output Handling | Starter check with ATLAS mapping |
| LLM06:2025 | Excessive Agency | Starter check with ATLAS mapping |
| LLM07:2025 | System Prompt Leakage | Starter check with ATLAS mapping |
| LLM08:2025 | Vector and Embedding Weaknesses | Starter check with ATLAS mapping |
| LLM09:2025 | Misinformation | Starter check with ATLAS mapping |
| LLM10:2025 | Unbounded Consumption | Starter check with ATLAS mapping |

## Architecture

```text
Operator Browser: Modern Web UI | CLI | CI
        ↓
Target AI Systems: demo echo target | local demo app | configured HTTP/Chat/Ollama/Webhook targets
        ↓
Integration Layer: DemoEchoClient | HttpJsonTargetClient | ChatCompletionsTargetClient | OllamaGenerateTargetClient | WebhookJsonTargetClient
        ↓
Core Engine: Scanner | Test Runner | Results Engine | Risk Scoring | Policy Engine
        ↓
Module Layer: AssessmentModule protocol | ModuleRegistry | starter modules
        ↓
Payload Layer: safe YAML payload libraries
        ↓
Governance Layer: policy rules | exceptions | approval evidence | RAG manifest | RAG retrieval scenarios | agent runtime manifest | agent execution scenarios | ATLAS mapping
        ↓
Assessment Profiles: baseline | rag | agent | full
        ↓
Outputs: Web dashboard | Markdown | JSON | SARIF-style | dashboards | report diff | trends | benchmarks | release package
```

## Repository structure

```text
Vulnora-IQ/
├── .github/workflows/       # Python CI
├── benchmarks/              # Regression benchmark suite and runner
├── config/                  # Targets, profiles, policies, manifests, mappings, scenarios
├── core/                    # Scanner, runner, scoring, policy, exceptions, approvals, mapping, results model
├── examples/                # Safe local demo targets and fixtures
├── integrations/            # Demo, HTTP JSON, chat, Ollama-style, and webhook adapters
├── modules/                 # Module protocol, registry, and starter modules
├── rag_testing/             # RAG corpus and retrieval validation
├── agent_testing/           # Agent runtime and execution validation
├── payloads/                # Safe payload schema and libraries
├── reports/                 # Markdown, JSON, SARIF-style, diff, and policy-trend generation
├── dashboards/              # Markdown, HTML, and diff-trend dashboard generation
├── webui/                   # Modern Web UI server and static frontend
├── tests/                   # Unit tests
├── scripts/                 # CLI entry points, release package builder, ATLAS refresh
└── docs/                    # Architecture, status, mapping, governance docs
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
vulnoraiq --target demo --profile baseline
```

The demo target uses an in-memory echo client, so the platform can be explored without external API keys.

The default command writes:

- `reports/output/scan-report.md`
- `reports/output/scan-report.json`
- `reports/output/scan-report.sarif`
- `reports/output/dashboard.md`
- `reports/output/dashboard.html`

## Web UI command

Run the modern Web UI:

```bash
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Open:

```text
http://127.0.0.1:8787
```

The Web UI supports scan launch, realtime progress via Server-Sent Events, completed dashboard views, scan history, and downloadable Markdown/JSON/SARIF/dashboard artifacts. See [`docs/web-ui.md`](docs/web-ui.md).

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
  --authorised \
  --output reports/output/authorised-target-report.md \
  --json-output reports/output/authorised-target-report.json \
  --sarif-output reports/output/authorised-target-report.sarif \
  --dashboard-output reports/output/authorised-target-dashboard.md \
  --html-dashboard-output reports/output/authorised-target-dashboard.html
```

Before running against a configured target, replace the placeholder endpoint in `config/targets.yaml` and set any required token environment variable.

## Report diff command

Compare two structured JSON reports:

```bash
vulnoraiq-diff \
  --baseline reports/output/baseline.json \
  --current reports/output/current.json \
  --json-output reports/output/report-diff.json \
  --markdown-output reports/output/report-diff.md
```

Use `--fail-on-regression` in CI when added or changed findings or policy status changes should fail the job.

## Trend commands

```bash
vulnoraiq-policy-trend --input-dir reports/output
vulnoraiq-diff-trend --input-dir reports/output
```

## Benchmark command

```bash
vulnoraiq-benchmark --manifest benchmarks/benchmark_suite.yaml --fail-on-regression
```

## ATLAS refresh command

Use local fixture mode in CI and review generated mappings before committing refreshed data:

```bash
vulnoraiq-refresh-atlas --source path/to/ATLAS.yaml --output config/mitre_atlas_mapping.yaml
```

## Release package command

Build a ZIP package with safe demo outputs and non-sensitive examples after generating demo reports:

```bash
vulnoraiq-package --manifest config/release_package.yaml
```

The package path defaults to `dist/vulnoraiq-example-package.zip`.

## Dashboard command

Generate a Markdown dashboard from an existing JSON report:

```bash
vulnoraiq-dashboard \
  --report reports/output/scan-report.json \
  --output reports/output/dashboard.md
```

The standard scan command also writes an HTML dashboard.

## Module and payload authoring

Read [`docs/module-authoring.md`](docs/module-authoring.md) before adding modules or payload libraries.

## Configuration

- `config/default.yaml`: engine defaults and paths for reports, Web UI, approvals, RAG, agent, ATLAS, benchmarks, and release packaging
- `config/targets.yaml`: target definitions and adapter examples
- `config/attack_profiles.yaml`: selective module execution
- `config/policies.yaml`: governance thresholds and blocking conditions
- `config/policy_exceptions.yaml`: scoped exception register
- `config/approval_evidence.yaml`: signed approval evidence register
- `config/owasp_llm_2025_mapping.yaml`: audit-friendly OWASP mapping
- `config/mitre_atlas_mapping.yaml`: MITRE ATLAS mapping catalog
- `config/atlas_refresh.yaml`: ATLAS refresh settings
- `config/rag_corpus_manifest.yaml`: RAG corpus metadata manifest
- `config/rag_retrieval_scenarios.yaml`: RAG retrieval scenario manifest
- `config/agent_runtime.yaml`: agent tool, memory, and orchestration governance manifest
- `config/agent_execution_scenarios.yaml`: agent execution scenario manifest
- `config/release_package.yaml`: release package manifest
- `benchmarks/benchmark_suite.yaml`: regression benchmark suite
- `payloads/schema.yaml`: payload library schema and safety rules

## Design principles

1. Audit-friendly by default.
2. Safe local demo first.
3. Explicit authorisation for configured targets.
4. System-level coverage across LLM, RAG, tool, memory, and orchestration layers.
5. CI/CD-ready direction for prompt, corpus, agent, release-gate, and regression checks.

## License

MIT. See `LICENSE`.
