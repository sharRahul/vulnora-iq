# Agent Lab implementation plan

This document records the planned and implemented experimental WebUI flow:

```text
Import Agent -> Configure LLM/API keys -> Select CPU/GPU -> Build/Run -> Auto-create target -> Test with VulnoraIQ
```

## Goals

1. Allow operators to bring real AI-agent source projects into VulnoraIQ without adding demo or mock projects to the repository.
2. Support local and remote model providers through environment-driven configuration.
3. Build and run the agent inside Docker from the WebUI.
4. Support optional NVIDIA GPU runtime flags for agents that need local inference acceleration.
5. Register a runtime target automatically so the normal scanner/reporting path is reused.
6. Keep the capability experimental and explicit because it requires Docker build/run access.

## Implemented components

| Component | File(s) | Status |
| --- | --- | --- |
| Agent Lab backend module | `webui/agent_lab.py` | Implemented |
| Agent Lab HTTP routes | `webui/assistant_server.py` | Implemented |
| Static Agent Lab page | `webui/static/agent-lab/` | Implemented as a no-build runtime page |
| React console entry point | `webui/console/src/components/projects/ProjectImporter.tsx` | Embedded via iframe |
| Docker image support | `Dockerfile` | Git client and Agent Lab data roots added |
| Docker Compose runtime config | `docker-compose.yml` | Agent Lab env, host gateway, and project/data mounts configured |
| Operator documentation | `docs/AGENT_LAB.md` | Implemented |

## Audit findings addressed

| Finding from audit | Planned/implemented response |
| --- | --- |
| Docker socket documentation drift | Document the socket as an intentional experimental Agent Lab requirement instead of claiming no socket mount. |
| Agent/project deployment under-documented | Add Agent Lab operator guide and plan. |
| WebUI profile list hardcoded | Agent Lab scan profile selector loads backend profile keys from `/api/agent-lab`. |
| Runtime target persistence not obvious | Agent Lab docs describe generated runtime targets and reuse of the normal target store. |
| Provider configuration missing | Add provider presets for Ollama, LM Studio, OpenRouter, custom OpenAI-compatible, and custom env. |
| GPU runtime not represented | Add CPU/all GPU/specific GPU device runtime selections and backend Docker flags. |
| Imported projects should not be dummy data | Import only operator-provided Git/ZIP/mapped projects. No sample/demo projects are added. |

## Import design

The backend supports three import modes:

1. HTTPS Git clone from an allow-listed host.
2. ZIP archive upload through the backend API with size, file count, and path traversal controls.
3. Read-only mapped host folder under `/app/projects`.

Git credentials are deliberately not accepted in URLs. Private source support should use a future credential broker or host-side checkout.

## Provider design

Provider settings are converted into commonly used environment variables rather than writing provider-specific files into imported source code. API keys are passed to Docker runtime and redacted from deployment metadata responses.

## Runtime design

The deployment step:

1. Analyzes project metadata.
2. Uses an existing Dockerfile or generates one for common Python/Node apps in the managed project area.
3. Builds an image.
4. Replaces a previous container with the same project ID.
5. Runs the container on the VulnoraIQ lab network.
6. Applies no-new-privileges and capability drop.
7. Adds optional GPU flags.
8. Registers a runtime target.

## Generated targets

Generated target IDs use this pattern:

```text
agent-lab-<project-id>-<target-type>
```

The generated target stays in runtime target storage and can be scanned through the normal target manager or Agent Lab.

## Hardening backlog before promoting from experimental

1. Move build/run into a job queue with streamed Docker build logs.
2. Add secret-file or Docker secret injection to reduce use of process environment variables for API keys.
3. Add optional signed-source or trusted-source policy for Git imports.
4. Add configurable outbound network policy per deployment.
5. Add image/container cleanup controls.
6. Add per-project role scoping for shared internal deployments.
7. Add richer React-native UI integration and browser ZIP upload controls.
8. Add release packaging verification for Agent Lab static assets.
9. Add CI tests that exercise import analysis and target generation without creating demo projects.

## Release posture

The feature remains experimental until the hardening backlog is closed and the Docker socket risk is reviewed for shared/internal-server deployments.
