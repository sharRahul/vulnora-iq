# Experimental Agent Lab

The Agent Lab is an experimental VulnoraIQ WebUI workflow for importing a real AI-agent project, configuring its model provider, running it in Docker, auto-registering a VulnoraIQ target, and launching an authorised scan.

It is available at:

```text
http://localhost:8787/agent-lab
```

The React project workspace also embeds this page through the Project Importer area.

## What it does

| Step | Capability |
| --- | --- |
| Import Agent | Import a real project from an approved Git host, upload a ZIP archive through the backend API, or use a mapped `./projects/<name>` directory. |
| Configure LLM/API keys | Select Ollama, LM Studio, OpenRouter, a custom OpenAI-compatible endpoint, or custom environment variables. |
| Select CPU/GPU | Run CPU-only, all NVIDIA GPUs, or a specific GPU device list. |
| Build/Run | Use the project's Dockerfile or generate one for common Python/Node agent projects in the managed Agent Lab project area. |
| Auto-create target | Register a runtime target using `http_json` or `chat_completions` target contracts. |
| Test with VulnoraIQ | Launch an authorised scan against the generated runtime target from the same WebUI flow. |

No demo, mock, fake, or fixture projects are created by this workflow. Project IDs containing those terms are rejected in normal Agent Lab runtime.

## Import modes

### Git import

Use the Git URL form with an HTTPS repository URL. By default the allowed Git hosts are:

```text
github.com,gitlab.com,bitbucket.org
```

Configure this allow-list with:

```text
VULNORAIQ_AGENT_LAB_ALLOWED_GIT_HOSTS=github.com,gitlab.com,bitbucket.org
```

Git URLs must not embed credentials. Private repository import should use a controlled host-side checkout or a future credential broker rather than placing credentials in the URL.

### ZIP archive import

The backend supports ZIP archive import at `POST /api/agent-lab/import/archive`. The archive is size-limited, file-count-limited, and extracted with path traversal checks into the managed Agent Lab project area.

### Mapped folder

The Docker lab mounts:

```text
./projects:/app/projects:ro
```

Folders placed there appear as read-only mounted projects. If a mounted project has no Dockerfile, copy/import it into the managed Agent Lab area or add a Dockerfile in the host project folder.

## Provider configuration

The Agent Lab exposes provider presets for:

| Provider | Typical endpoint |
| --- | --- |
| Ollama | `http://host.docker.internal:11434/v1` |
| LM Studio | `http://host.docker.internal:1234/v1` |
| OpenRouter | `https://openrouter.ai/api/v1` |
| Custom OpenAI-compatible | Operator-provided base URL |
| Custom environment only | Operator-provided environment variables |

The backend maps provider settings into common environment variables used by many agent frameworks:

```text
OPENAI_BASE_URL
OPENAI_API_BASE
OPENAI_API_KEY
OPENROUTER_API_KEY
OLLAMA_HOST
MODEL
OPENAI_MODEL
VULNORAIQ_LLM_PROVIDER
VULNORAIQ_LLM_MODEL
```

API keys are not written to the repository or runtime target YAML. They are passed to the launched Docker container as runtime environment variables. Operators should still treat Docker inspect output, process metadata, and container logs as sensitive.

## CPU and GPU runtime

| UI option | Docker runtime behaviour |
| --- | --- |
| CPU only | No GPU flags are added. |
| All NVIDIA GPUs | Adds `--gpus all`. |
| Specific GPU device IDs | Adds `--gpus device=<ids>`. |

GPU mode requires the host Docker runtime to be configured for NVIDIA GPU containers. The Agent Lab does not install host GPU drivers.

## Docker build/run behaviour

The Agent Lab builds a project image tagged as:

```text
vulnoraiq-agent-lab-<project-id>
```

It runs a container named:

```text
vulnoraiq-agent-lab-<project-id>
```

The container is attached to the VulnoraIQ lab network and is labelled with `vulnoraiq.agent=agent-lab` and `vulnoraiq.agent.id=<project-id>`.

The run command applies:

```text
--security-opt no-new-privileges:true
--cap-drop ALL
```

Optional runtime limits include memory and CPU settings.

## Auto-created runtime targets

The deployment step registers a runtime target in the same runtime target store used by the WebUI target manager.

Generated target defaults:

```yaml
authorisation_required: true
environment: agent_lab
safety_profile: local_lab_safe
```

Supported generated target types:

| Target type | Use case |
| --- | --- |
| `http_json` | Agent endpoint accepts JSON such as `{ "prompt": "..." }`. |
| `chat_completions` | Agent exposes an OpenAI-compatible `/v1/chat/completions` endpoint. |

## Testing flow

1. Start the Docker lab.
2. Open `/agent-lab`.
3. Import or select a real agent project.
4. Configure the provider, model, and key/environment values.
5. Choose CPU/GPU mode and runtime limits.
6. Choose the target contract and endpoint path.
7. Build/run the agent.
8. Select the auto-created target.
9. Launch an authorised VulnoraIQ scan.
10. Review findings, evidence, and reports in the main WebUI.

## Security boundary

The Agent Lab requires Docker build/run access from the WebUI container. In Docker Compose this is provided through the existing Docker socket mount. This is powerful and should be treated as an experimental local-lab capability.

Do not expose the default Docker WebUI beyond loopback unless production auth, reverse proxy, TLS, audit retention, and backup controls are configured.

## Configuration reference

| Variable | Purpose | Default |
| --- | --- | --- |
| `VULNORAIQ_AGENT_LAB_ROOT` | Agent Lab data root. | `/data/agent_lab` |
| `VULNORAIQ_AGENT_LAB_PROJECTS_ROOT` | Managed imported project root. | `/data/agent_lab/projects` |
| `VULNORAIQ_AGENT_LAB_DEPLOYMENTS` | Deployment metadata YAML. | `/data/agent_lab/deployments.yaml` |
| `VULNORAIQ_PROJECTS_ROOT` | Mounted read-only project root. | `/app/projects` |
| `VULNORAIQ_AGENT_LAB_ALLOWED_GIT_HOSTS` | Allowed Git import hosts. | `github.com,gitlab.com,bitbucket.org` |
| `VULNORAIQ_AGENT_LAB_MAX_IMPORT_BYTES` | Max import size. | `52428800` |
| `VULNORAIQ_AGENT_LAB_MAX_IMPORT_FILES` | Max import file count. | `2000` |
| `VULNORAIQ_AGENT_NETWORK` | Docker network for launched agents. | `vulnoraiq_vulnoraiq-lab` |
