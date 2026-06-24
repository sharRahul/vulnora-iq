# AI agent testing

The current default AI-agent test path is the Docker Compose lab. It provides a deterministic `local-mock-agent` target that never calls external LLM providers, does not execute shell commands, does not read host files, and returns safe simulated responses for authorised testing.

## Start the agent lab

```bash
docker compose build
docker compose up -d
```

Open <http://localhost:8787> or use the CLI inside the web container.

## Current mock-agent contracts

| Target | Contract |
| --- | --- |
| `local_mock_agent` | Chat-completions-compatible endpoint. |
| `local_rag_app` | RAG query endpoint with answer/context extraction. |
| `local_mock_ollama` | Ollama-style generate endpoint. |
| `local_webhook_agent` | Webhook-style JSON endpoint. |
| `local_agent_tool_loop` | Dry-run agent tool-loop endpoint. |

All Docker targets use `http://local-mock-agent:9090` inside the private Docker network and are defined in `config/targets.docker.yaml`.

## Run the foundation profile

```bash
docker compose exec vulnoraiq-web vulnoraiq scan \
  --target local_mock_agent \
  --profile ai_agent_foundation \
  --authorised
```

The foundation path exercises prompt-injection resistance, system prompt leakage boundaries, tool misuse resistance, RAG context handling, policy bypass attempts, output handling, sensitive-data disclosure checks, agency limits, and audit/report generation.

## WebUI flow

1. Start Docker Compose.
2. Open the WebUI.
3. Select a Docker lab target.
4. Validate connectivity.
5. Review the authorisation/readiness checklist.
6. Select `ai_agent_foundation` or another assessment profile.
7. Launch the scan and review findings/reports.

## Scope and assurance boundary

The mock agent is a deterministic lab target. It is useful for validating scanner wiring, target adapters, policy/report output, WebUI target management, and CI smoke paths. It does not prove certified detection against real AI agents. Real targets must be owned by you or explicitly authorised for assessment.
