# OWASP AI Testing Guide Integration

VulnoraIQ now includes a controlled, safe implementation path for the OWASP AI Testing Guide ecosystem and related AI red-team guidance. This implementation is intended for authorised local or internal assessment only and does not claim certified VAPT-grade assurance.

## Source framework coverage

The new `ai_testing_guide_foundation` suite provides methodology-oriented checks for these source areas:

| Source area | VulnoraIQ module | Purpose |
| --- | --- | --- |
| OWASP AI Testing Guide | `owasp_ai_testing_methodology` | AI testing lifecycle, evidence, integration, runtime and reporting assumptions |
| OWASP GenAI Red Teaming Guide | `owasp_genai_red_teaming_methodology` | Risk-based GenAI red-team planning, model/runtime behaviour and system integration review |
| CSA Agentic AI Red Teaming Guide | `csa_agentic_ai_red_teaming` | Autonomous agent, tool, memory, permission and inter-agent workflow review |
| OWASP AI Exchange | `owasp_ai_exchange_controls` | Practical AI/data-centric control mapping and operational ownership |
| OWASP AI Security and Privacy Guide | `owasp_ai_security_privacy_design` | Secure design, privacy, procurement and testing questions |
| OWASP Top 10 for LLM | Existing `owasp_llm01` to `owasp_llm10` modules | LLM application risk checks already available in the Web UI |
| OWASP AI VSS | `owasp_aivss_scoring_review` | AI vulnerability scoring, triage factors and evidence quality review |
| NIST AI 100-2 E2025 | `nist_ai_100_2_adversarial_ml` | Adversarial ML taxonomy and terminology alignment |

## Web UI profiles

The following profiles are selectable from the Web UI:

- `ai_testing_guide_foundation` — runs the full AI Testing Guide foundation suite.
- `test_owasp_ai_testing_methodology`
- `test_owasp_genai_red_teaming_methodology`
- `test_csa_agentic_ai_red_teaming`
- `test_owasp_ai_exchange_controls`
- `test_owasp_ai_security_privacy_design`
- `test_owasp_aivss_scoring_review`
- `test_nist_ai_100_2_adversarial_ml`

These profiles use the `payloads/ai_testing_guide.yaml` safe payload library. The payloads ask the target for defensive methodology, evidence, control and triage responses. They do not ask the target to perform unauthorised actions.

## Testing actual local AI agents

The original `demo` target remains a safe in-memory target. To test an actual local AI agent, start the agent locally and select one of the new OWASP lab targets from the Web UI.

| Web UI target | Endpoint | Contract |
| --- | --- | --- |
| `owasp_lab_agent_http` | `http://127.0.0.1:8000/agent` | Generic HTTP JSON |
| `owasp_lab_chat_completions` | `http://127.0.0.1:8000/v1/chat/completions` | OpenAI-compatible chat completions |
| `owasp_lab_ollama_generate` | `http://127.0.0.1:11434/api/generate` | Ollama generate API |
| `owasp_lab_webhook_json` | `http://127.0.0.1:8000/assessment-webhook` | Webhook-style JSON |

### Generic HTTP JSON contract

VulnoraIQ sends:

```json
{
  "prompt": "assessment prompt",
  "input": "assessment prompt"
}
```

It accepts either a plain text response or JSON containing one of these string fields:

```text
output, response, text, message, content
```

### Chat completions contract

VulnoraIQ sends an OpenAI-compatible request body:

```json
{
  "model": "owasp-lab-agent",
  "messages": [
    {
      "role": "user",
      "content": "assessment prompt"
    }
  ],
  "temperature": 0
}
```

It reads `choices[0].message.content` from the response.

### Ollama generate contract

VulnoraIQ sends:

```json
{
  "model": "llama3",
  "prompt": "assessment prompt",
  "stream": false
}
```

It reads the `response` field.

### Webhook JSON contract

VulnoraIQ sends:

```json
{
  "input": "assessment prompt",
  "metadata": {
    "assessment_client": "owasp_lab_webhook_json"
  }
}
```

It accepts JSON containing `output`, `response`, `text`, or `content`.

## Web UI run flow

1. Start the local lab AI agent.
2. Open the VulnoraIQ Web UI.
3. Select one of the `owasp_lab_*` targets.
4. Select `OWASP AI Testing Guide foundation` or an individual AI Testing Guide profile.
5. Tick the authorisation checkbox.
6. Start the assessment.
7. Review the dashboard, findings, evidence preview and downloadable reports.

## Safety and assurance boundary

- Use these targets only for local lab systems or systems you own or are explicitly authorised to assess.
- These checks are methodology and evidence harness checks, not independent certification.
- Findings must still be reviewed by a human tester before they are used for assurance, remediation decisions or external reporting.
- If a local lab target is not running, the Web UI will show a failed scan rather than silently falling back to the demo target.
