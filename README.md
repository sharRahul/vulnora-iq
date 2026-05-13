# LLM VAPT Framework

An AI-native Vulnerability Assessment and Penetration Testing framework for **LLM applications, RAG pipelines, AI agents, and orchestration layers**.

The project extends VAPT beyond prompt-level testing into full AI system assessment: model endpoints, retrieval layers, tools, memory, orchestrators, governance controls, and reporting.

> **Responsible use only:** run this framework only against systems you own or are explicitly authorised to test. Payloads and modules are safe starter assessment scaffolding and should be customised only inside an approved red-team engagement process.

## Why this exists

Existing AI security tools are strong in specific areas: probe libraries, prompt regression, attack-chain automation, and model robustness testing. This framework combines those strengths and adds an enterprise VAPT structure for:

- OWASP Top 10 for LLM Applications 2025 mapping
- Agent and tool abuse testing
- RAG poisoning and retrieval manipulation simulation
- Orchestrator attack-chain modelling
- Policy-as-code guardrails
- Audit-ready evidence and reporting
- MITRE ATLAS mapping for threat-informed AI security testing

## OWASP LLM 2025 coverage

| OWASP ID | Risk | Module path |
|---|---|---|
| LLM01:2025 | Prompt Injection | `modules/owasp_llm01_prompt_injection/` |
| LLM02:2025 | Sensitive Information Disclosure | `modules/owasp_llm02_sensitive_information_disclosure/` |
| LLM03:2025 | Supply Chain | `modules/owasp_llm03_supply_chain/` |
| LLM04:2025 | Data and Model Poisoning | `modules/owasp_llm04_data_and_model_poisoning/` |
| LLM05:2025 | Improper Output Handling | `modules/owasp_llm05_improper_output_handling/` |
| LLM06:2025 | Excessive Agency | `modules/owasp_llm06_excessive_agency/` |
| LLM07:2025 | System Prompt Leakage | `modules/owasp_llm07_system_prompt_leakage/` |
| LLM08:2025 | Vector and Embedding Weaknesses | `modules/owasp_llm08_vector_embedding_weaknesses/` |
| LLM09:2025 | Misinformation | `modules/owasp_llm09_misinformation/` |
| LLM10:2025 | Unbounded Consumption | `modules/owasp_llm10_unbounded_consumption/` |

## Architecture

```text
Target AI Systems: LLM APIs | RAG pipelines | Agents | Orchestrators
        ↓
Integration Layer: OpenAI | Azure OpenAI | LangChain | Semantic Kernel | Custom Agent
        ↓
Core Engine: Scanner | Test Runner | Orchestrator | Results Engine | Risk Scoring
        ↓
Testing Modules: OWASP LLM 2025 | RAG Testing | Agent Testing | Payload Libraries
        ↓
Governance + Reporting: Policy-as-Code | Evidence | Executive | Technical | Risk Matrix
```

## Repository structure

```text
llm-vapt-framework/
├── config/                 # Targets, attack profiles, policies, mappings
├── core/                   # Scanner, orchestrator, runner, scoring, results model
├── integrations/           # Provider and agent adapters
├── modules/                # OWASP LLM Top 10 2025 modules
├── rag_testing/            # RAG poisoning, retrieval, embedding, corpus checks
├── agent_testing/          # Agent chain, tool execution, memory, multi-agent tests
├── payloads/               # Safe starter payload libraries
├── reports/                # Markdown report generation and templates
├── dashboards/             # Visualisation helpers
├── tests/                  # Unit tests
├── scripts/                # CLI and CI entry points
└── docs/                   # Architecture, roadmap, mapping, governance docs
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
python scripts/run_scan.py --target demo --profile baseline
```

The demo target uses an in-memory echo client, so the framework can be explored without external API keys.

## Run tests

```bash
pytest -q
```

## Example scan command

```bash
python scripts/run_scan.py \
  --target demo \
  --profile baseline \
  --output reports/output/demo-report.md
```

## Configuration

- `config/default.yaml`: engine defaults
- `config/targets.yaml`: target definitions
- `config/attack_profiles.yaml`: selective module execution
- `config/policies.yaml`: governance thresholds and blocking conditions
- `config/owasp_llm_2025_mapping.yaml`: audit-friendly OWASP mapping

## Design principles

1. Audit-friendly by default.
2. Payload-driven testing.
3. System-level coverage across LLM, RAG, tool, memory, and orchestration layers.
4. Safe extensibility for authorised testing.
5. CI/CD ready for prompt, corpus, agent, and release-gate checks.

## License

MIT. See `LICENSE`.
