# LLM VAPT Framework

An AI security assessment framework for **LLM applications, RAG pipelines, AI agents, and orchestration layers**.

> **Current maturity:** this repository is evolving from a starter framework into an enterprise platform. Start with [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) to see what is implemented, partial, or planned.

> **Responsible use only:** run this framework only against systems you own or are explicitly authorised to assess. The default demo target is safe and local. Configured non-demo targets require an explicit authorisation flag.

## Why this exists

AI application security needs more than prompt-level checks. This repository provides a practical structure for assessing model endpoints, retrieval layers, tools, memory, orchestration, governance controls, and reporting.

The current implementation provides:

- OWASP LLM 2025 starter mapping
- MITRE ATLAS mapping catalog with AML technique IDs
- Safe demo target with no external API keys
- Baseline, RAG, agent, and full profile definitions
- Module protocol, starter modules, and registry-based module lookup
- Safe YAML payload libraries mapped to module names
- Scanner, scoring, result model, policy evaluation, and scoped policy exceptions
- RAG corpus manifest validation
- RAG retrieval scenario validation and source-trust scoring
- Agent runtime governance validation
- Agent execution scenario validation for tools, memory, approvals, and rollback planning
- Markdown, JSON, and SARIF-style reports with evidence details
- Markdown and HTML dashboard generation
- JSON/Markdown report diffing between assessment runs
- Explicit non-demo authorisation gate
- Minimal HTTP JSON target adapter for approved targets
- Python CI across supported versions with demo report artifacts

The roadmap includes richer target adapters, packaged example outputs, trend tracking, benchmark datasets, signed approval evidence validation, and report-diff regression gates.

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
Target AI Systems: demo echo target | configured HTTP JSON target
        ↓
Integration Layer: DemoEchoClient | HttpJsonTargetClient
        ↓
Core Engine: Scanner | Test Runner | Results Engine | Risk Scoring | Policy Engine
        ↓
Module Layer: AssessmentModule protocol | ModuleRegistry | starter modules
        ↓
Payload Layer: safe YAML payload libraries
        ↓
Governance Layer: policy rules | exceptions | RAG manifest | RAG retrieval scenarios | agent runtime manifest | agent execution scenarios | ATLAS mapping
        ↓
Assessment Profiles: baseline | rag | agent | full
        ↓
Outputs: Markdown | JSON | SARIF-style | Markdown dashboard | HTML dashboard | report diff
```

## Repository structure

```text
llm-vapt-framework/
├── .github/workflows/       # Python CI
├── config/                  # Targets, profiles, policies, manifests, mappings, scenarios
├── core/                    # Scanner, runner, scoring, policy, exceptions, mapping, results model
├── integrations/            # Demo and HTTP JSON adapters
├── modules/                 # Module protocol, registry, and starter modules
├── rag_testing/             # RAG corpus and retrieval validation
├── agent_testing/           # Agent runtime and execution validation
├── payloads/                # Safe payload schema and libraries
├── reports/                 # Markdown, JSON, SARIF-style, and diff generation
├── dashboards/              # Markdown and HTML dashboard generation
├── tests/                   # Unit tests
├── scripts/                 # CLI entry points
└── docs/                    # Architecture, status, mapping, governance docs
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
python scripts/run_scan.py --target demo --profile baseline
```

The demo target uses an in-memory echo client, so the framework can be explored without external API keys.

The default command writes:

- `reports/output/scan-report.md`
- `reports/output/scan-report.json`
- `reports/output/scan-report.sarif`
- `reports/output/dashboard.md`
- `reports/output/dashboard.html`

## Run tests

```bash
pytest -q
```

## Example demo command

```bash
python scripts/run_scan.py \
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
python scripts/run_scan.py \
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
python -m reports.report_diff \
  --baseline reports/output/baseline.json \
  --current reports/output/current.json \
  --json-output reports/output/report-diff.json \
  --markdown-output reports/output/report-diff.md
```

Use `--fail-on-regression` in CI when added or changed findings or policy status changes should fail the job.

## Dashboard command

Generate a Markdown dashboard from an existing JSON report:

```bash
python dashboards/generate_dashboard.py \
  --report reports/output/scan-report.json \
  --output reports/output/dashboard.md
```

The standard scan command also writes an HTML dashboard.

## Module and payload authoring

Read [`docs/module-authoring.md`](docs/module-authoring.md) before adding modules or payload libraries.

## Configuration

- `config/default.yaml`: engine defaults, payload libraries, report outputs, approval gates, RAG corpus metadata, RAG retrieval scenarios, agent runtime metadata, agent execution scenarios, and ATLAS mapping path
- `config/targets.yaml`: target definitions
- `config/attack_profiles.yaml`: selective module execution
- `config/policies.yaml`: governance thresholds and blocking conditions
- `config/policy_exceptions.yaml`: scoped exception register
- `config/owasp_llm_2025_mapping.yaml`: audit-friendly OWASP mapping
- `config/mitre_atlas_mapping.yaml`: MITRE ATLAS mapping catalog
- `config/rag_corpus_manifest.yaml`: RAG corpus metadata manifest
- `config/rag_retrieval_scenarios.yaml`: RAG retrieval scenario manifest
- `config/agent_runtime.yaml`: agent tool, memory, and orchestration governance manifest
- `config/agent_execution_scenarios.yaml`: agent execution scenario manifest
- `payloads/schema.yaml`: payload library schema and safety rules

## Design principles

1. Audit-friendly by default.
2. Safe local demo first.
3. Explicit authorisation for configured targets.
4. System-level coverage roadmap across LLM, RAG, tool, memory, and orchestration layers.
5. CI/CD-ready direction for prompt, corpus, agent, and release-gate checks.

## License

MIT. See `LICENSE`.
