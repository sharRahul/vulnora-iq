# VulnoraIQ manual test plan

This plan defines the manual QA pass for VulnoraIQ after changes to launch modes, WebUI auth, Agent Lab, reports, persistence, and release packaging.

The plan is written so a human tester or an LLM coding agent can execute it. Do not use it to test systems you do not own or do not have explicit authorisation to assess.

## Scope

Manual testing must cover:

- Desktop Mode: native VulnoraIQ WebUI on the host, with Docker used only for sandboxed Agent Lab runtimes.
- Advanced Docker Lab Mode: full Docker Compose lab with the WebUI inside `vulnoraiq-web`.
- WebUI auth boundaries: `VULNORAIQ_AUTH_MODE=local_admin` for local single-user/admin operation, and `VULNORAIQ_AUTH_MODE=token` for production/shared internal use.
- WebUI pages: dashboard, targets, scans, agents, projects, and Agent Lab.
- Agent Lab import paths: Local folder upload, ZIP upload, Git import, and mapped `./projects/<agent-name>/` refresh.
- Agent Lab build/deploy/remove flow with a safe local test agent.
- Managed-vs-mapped project behaviour, including Dockerfile generation only for writable managed imports.
- Scan execution against a safe local/mock target.
- Reports, evidence, audit logs, and persistence.
- Release/package smoke checks.
- UI layout, dark mode, icon contrast, and browser console errors.

## Test rules

- Start from a clean working tree.
- Record OS, browser, Python, Docker, Docker Compose, Node/npm, branch, and commit SHA.
- Do not mark a test as passed unless it was actually executed.
- Do not hide failures or convert them into documentation-only notes.
- Do not change product code until the failure is reproduced and root cause is understood.
- Capture command output, server logs, browser console errors, screenshots, and report paths.
- Do not test third-party targets.
- Use only safe local test agents and local/mock targets.

## Environment capture

Run and record:

```bash
git status --short
git branch --show-current
git rev-parse HEAD
python --version
python -m pip --version
docker version
docker compose version
docker info
node --version || true
npm --version || true
```

Also record:

- Browser name/version used for WebUI testing.
- Whether browser folder selection is available for Local folder upload.
- Docker Desktop/Engine status.
- Host OS path where the repository was checked out.

Expected result:

- Git working tree is clean before manual testing.
- Python is 3.10 or newer.
- Docker Engine or Docker Desktop is running.
- Docker Compose v2 is available.
- A modern browser is available for WebUI and Agent Lab tests.

## Safe local test agent fixture

Use this fixture for Agent Lab import/build/deploy tests. Create it outside the repo root or under a temporary ignored workspace such as `.manual-test-work/`.

```bash
mkdir -p .manual-test-work/safe-echo-agent
cat > .manual-test-work/safe-echo-agent/app.py <<'PY'
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Prompt(BaseModel):
    prompt: str = ""

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/")
def echo(body: Prompt):
    return {"response": "echo:" + body.prompt[:80]}
PY
cat > .manual-test-work/safe-echo-agent/requirements.txt <<'REQ'
fastapi
uvicorn
pydantic
REQ
```

The fixture must not call third-party APIs. It is safe for CPU-only local Docker execution.

## Test matrix

| ID | Area | Test | Expected result |
| --- | --- | --- | --- |
| MT-001 | Install | Editable install and dependency check | Install succeeds and `pip check` is clean. |
| MT-002 | Static validation | Lint, type check, tests | `ruff`, `mypy`, and `pytest` pass, or failures are documented. |
| MT-003 | Project validators | Metadata, mappings, readiness | Validators pass or expected production-env failures are documented. |
| MT-010 | Documentation | README and docs consistency | Docs agree on run modes, auth mode, output paths, Agent Lab import paths, and assurance boundary. |
| MT-020 | Desktop Mode | Start native launcher | WebUI runs on host loopback, expected folders are created, and no `vulnoraiq-web` container is created. |
| MT-021 | Desktop Mode | Health/session endpoints | `/healthz` is healthy and `/api/session` resolves `local-admin` admin. |
| MT-022 | Desktop Mode | WebUI pages | Dashboard, targets, scans, agents, projects, and Agent Lab load without unexpected auth errors. |
| MT-030 | Docker Lab | Compose startup | `vulnoraiq-web` is healthy and host port is loopback-published only. |
| MT-031 | Docker Lab | Session and CLI | Session resolves local admin; CLI commands run inside container. |
| MT-040 | Auth boundary | Direct local admin startup | `local_admin` works only on loopback by default. |
| MT-041 | Auth boundary | Reject unsafe local admin binds | `local_admin` rejects `0.0.0.0` unless explicit Docker Lab exception is set. |
| MT-042 | Auth boundary | Reject production local admin | `VULNORAIQ_ENV=production` rejects `local_admin`. |
| MT-043 | Auth boundary | Production token mode | Missing token fails; valid token authenticates admin. |
| MT-050 | WebUI | Clean state and page navigation | No fake data, raw JSON auth errors, broken icons, or major layout defects. |
| MT-060 | Scan workflow | Safe local baseline scan | Scan starts, emits events, completes/fails clearly, and produces expected artifacts. |
| MT-070 | Agent Lab | Import panel and project analysis | Agent Lab exposes Git URL, ZIP upload, Local folder upload, and Mapped folder tabs; project analysis works. |
| MT-071 | Agent Lab | Local folder upload | Browser folder picker imports a selected safe agent folder into managed Agent Lab storage. |
| MT-072 | Agent Lab | Mapped `./projects/` discovery | Desktop/Docker Lab mapped project folders appear after refresh and are marked mapped/read-only. |
| MT-073 | Agent Lab | Build/deploy/remove safe managed agent | Managed import builds/deploys, auto-creates target, and cleanup works. |
| MT-074 | Agent Lab | Mapped project without Dockerfile | Read-only mapped project without Dockerfile fails with a clear actionable message. |
| MT-080 | Reports | Evidence and assurance wording | Reports are readable, parseable, redacted where applicable, and do not overclaim assurance. |
| MT-090 | Persistence | Desktop and Docker Lab persistence | Jobs/reports/Agent Lab data persist across restart and are removed only by explicit reset. |
| MT-100 | Negative tests | CSRF, bad target, wrong token, invalid import, rate limit | Server fails closed with clear errors and no traceback. |
| MT-110 | Release | Release package smoke test | Launchers, docs, config examples, and static assets are present; secrets/local artifacts are absent. |

## Detailed procedures

### MT-001: install

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .[dev]
python -m pip check
```

Pass criteria:

- Install succeeds.
- `pip check` reports no broken dependencies.

### MT-002: static validation

```bash
ruff check .
mypy .
pytest -q
```

Pass criteria:

- All commands pass.
- Any failure includes exact command output and root-cause notes.

### MT-003: project validators

```bash
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_runtime_production_config.py
```

Pass criteria:

- Non-production validators pass.
- Production validation failures are classified as expected only when required production env variables are intentionally missing.

### MT-010: documentation consistency

Review:

- `README.md`
- `docs/README.md`
- `docs/USER_GUIDE.md`
- `docs/WEBUI_GUIDE.md`
- `docs/AGENT_LAB.md`
- `docs/RUN_MODES_DESKTOP_AND_DOCKER_LAB.md`
- `docs/WEBUI_SINGLE_USER_MODE.md`
- `docs/ASSESSMENT_ASSURANCE.md`
- `docs/MANUAL_TEST_PLAN.md`
- `docs/LLM_MANUAL_TESTING_PROMPT.md`
- `config/web_users.yaml`
- `.env.docker.example`
- `docker-compose.yml`

Pass criteria:

- Desktop Mode is documented as native-host WebUI plus Docker-sandboxed agents.
- Docker Lab Mode is documented as full Docker Compose.
- Desktop Mode folder contract includes `scan-reports/`, `agent-lab/projects/`, and optional mapped `projects/`.
- Agent Lab Local folder upload is documented as the preferred desktop flow for selecting local source folders through the browser.
- Agent Lab mapped folders are documented as read-only refresh/discovery folders.
- Direct local WebUI examples use `VULNORAIQ_AUTH_MODE=local_admin`.
- Production examples use `VULNORAIQ_ENV=production`, `VULNORAIQ_AUTH_MODE=token`, and `VULNORAIQ_ADMIN_TOKEN`.
- `VULNORAIQ_AUTH_ENABLED=false` is described only as a backward-compatible alias.
- Assessment docs say findings require human review and are not certified VAPT-grade assurance.

### MT-020: Desktop Mode startup

```bash
python scripts/desktop_launch.py
```

In another shell:

```bash
curl -i http://127.0.0.1:8787/healthz
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
```

Pass criteria:

- WebUI listens on `127.0.0.1:8787`.
- `scan-reports/`, `agent-lab/`, `agent-lab/projects/`, and `projects/` are created.
- Launcher output prints the managed Agent Lab import folder and mapped project folder.
- No `vulnoraiq-web` container is created by Desktop Mode.
- Docker containers are created only when sandboxed agents/runtimes are deployed.

### MT-021: Desktop Mode auth/session

```bash
curl -s http://127.0.0.1:8787/api/session
```

Pass criteria:

- Username is `local-admin`.
- Role is `admin`.
- Permissions include `view_scans`, `start_configured_scan`, and `manage_runtime`.
- No protected page shows raw `{"error":"authentication required"}`.

### MT-022: Desktop Mode WebUI navigation

Open `http://127.0.0.1:8787` and inspect:

- Dashboard
- Targets
- Scans
- Agents
- Projects
- Agent Lab at `/agent-lab`

Pass criteria:

- Pages load cleanly.
- Empty states are useful and not misleading.
- No repeated 401/403 errors in browser network tab.
- No repeated `/favicon.ico` auth-failure noise.

### MT-030: Docker Lab startup

```bash
docker compose build
docker compose up -d
docker compose ps
docker compose logs --tail=100 vulnoraiq-web
```

Pass criteria:

- `vulnoraiq-web` is running and healthy.
- Host port is published as `127.0.0.1:8787:8787`.
- Container startup accepts `VULNORAIQ_AUTH_MODE=local_admin` with Docker Lab bind acknowledgement.
- `./projects:/app/projects:ro` exists in the Docker Lab mapping.
- Logs have no startup traceback.

### MT-031: Docker Lab session and CLI

```bash
curl -s http://127.0.0.1:8787/api/session
docker compose exec vulnoraiq-web vulnoraiq targets list
docker compose exec vulnoraiq-web vulnoraiq reports list
docker compose exec vulnoraiq-web vulnoraiq jobs list
```

Pass criteria:

- Session resolves `local-admin` admin.
- CLI commands run without path, package, or container errors.

### MT-040: direct local admin startup

```bash
VULNORAIQ_AUTH_MODE=local_admin vulnoraiq-web --host 127.0.0.1 --port 8787
```

Pass criteria:

- Server starts.
- `/api/session` resolves `local-admin` admin.

### MT-041: unsafe local admin bind rejection

```bash
VULNORAIQ_AUTH_MODE=local_admin vulnoraiq-web --host 0.0.0.0 --port 8787
```

Pass criteria:

- Startup fails.
- Error explains that `local_admin` requires loopback unless the explicit Docker Lab exception is set.

### MT-042: production rejects local admin

```bash
VULNORAIQ_ENV=production VULNORAIQ_AUTH_MODE=local_admin vulnoraiq-web --host 127.0.0.1 --port 8787
```

Pass criteria:

- Startup fails.
- No local-admin fallback is available in production.

### MT-043: production token mode

Missing-token case:

```bash
VULNORAIQ_ENV=production VULNORAIQ_AUTH_MODE=token vulnoraiq-web --host 127.0.0.1 --port 8787
```

Expected: startup fails because `VULNORAIQ_ADMIN_TOKEN` is missing.

Valid-token case:

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_MODE=token
export VULNORAIQ_ADMIN_TOKEN="this-is-a-long-enough-admin-token-12345"
vulnoraiq-web --host 127.0.0.1 --port 8787
```

Then:

```bash
curl -i http://127.0.0.1:8787/api/session
curl -i -H "X-VulnoraIQ-Token: this-is-a-long-enough-admin-token-12345" http://127.0.0.1:8787/api/session
```

Pass criteria:

- Missing token fails closed.
- Wrong/no token cannot perform protected operations.
- Valid token authenticates as admin.

### MT-050: WebUI clean state and layout

Inspect dashboard and primary pages in light and dark mode.

Pass criteria:

- Clean workspace has no fake findings, mock assets, or dummy dashboard data.
- No overlapping text, clipped buttons, invisible icons, or critical contrast failures.
- Browser console has no repeated fatal JavaScript errors.

### MT-060: safe scan workflow

Use a safe local/mock target from the repo or Docker Lab. From the WebUI:

1. Select an authorised local target.
2. Select `baseline` or another safe profile.
3. Confirm the authorisation checklist.
4. Start the scan.
5. Watch progress/events.
6. Wait for completion or clear failure.

Verify artifacts:

Desktop Mode:

```bash
find scan-reports -maxdepth 4 -type f
```

Docker Lab:

```bash
docker compose exec vulnoraiq-web find /data -maxdepth 4 -type f
```

Pass criteria:

- Scan emits events and terminal state.
- Artifacts are written to the documented location.
- Failure, if any, is actionable and not a traceback.

### MT-070: Agent Lab import panel and project analysis

Open `/agent-lab`.

Pass criteria:

- Import panel exposes these tabs/options: Git URL, ZIP upload, Local folder upload, and Mapped folder.
- Local folder upload has a browser folder picker and clear managed-storage wording.
- Mapped folder panel explains `./projects/<agent-name>/` and read-only behaviour.
- Empty project state explains local folder upload, ZIP/Git import, and mapped folder refresh.
- Selecting an existing project populates Project Analysis without JavaScript errors.

### MT-071: Agent Lab Local folder upload

Use the safe local test agent fixture.

1. Start Desktop Mode.
2. Open `/agent-lab`.
3. Select **Local folder upload**.
4. Choose `.manual-test-work/safe-echo-agent` in the browser folder picker.
5. Set Project ID to `safe-echo-agent-local`.
6. Click **Upload Selected Folder**.
7. Confirm the project appears in the project list and is selected.
8. Inspect Project Analysis.
9. Confirm the project exists under managed storage:

```bash
find agent-lab/projects/safe-echo-agent-local -maxdepth 2 -type f
```

Docker Lab equivalent, if tested there:

```bash
docker compose exec vulnoraiq-web find /data/agent_lab/projects/safe-echo-agent-local -maxdepth 2 -type f
```

Pass criteria:

- Upload succeeds without requiring manual copy into `./projects/`.
- The backend does not request or store a raw local filesystem path; it receives selected files via browser upload/archive import.
- Project source is managed/writable, not mapped/read-only.
- Analysis detects Python/FastAPI or at least a Python project with port `8000` fallback.
- Existing duplicate Project ID fails cleanly with a clear message.

### MT-072: Agent Lab mapped `./projects/` discovery

Desktop Mode:

```bash
mkdir -p projects
rm -rf projects/safe-echo-agent-mapped
cp -R .manual-test-work/safe-echo-agent projects/safe-echo-agent-mapped
```

Then:

1. Open `/agent-lab`.
2. Select **Mapped folder**.
3. Click **Refresh Projects**.
4. Select `safe-echo-agent-mapped`.
5. Inspect Project Analysis.

Docker Lab equivalent:

```bash
mkdir -p projects
rm -rf projects/safe-echo-agent-mapped
cp -R .manual-test-work/safe-echo-agent projects/safe-echo-agent-mapped
docker compose up -d
```

Pass criteria:

- Desktop Mode launcher creates `projects/` even before this test copies anything into it.
- Mapped project appears after refresh.
- Project source is shown as mapped/mounted and not managed.
- Mapped project is treated as read-only by Agent Lab.

### MT-073: Agent Lab build/deploy/remove safe managed agent

Use the `safe-echo-agent-local` project imported by MT-071.

1. Select `safe-echo-agent-local`.
2. Configure provider as Custom environment only or a local provider that does not require third-party API access.
3. Select CPU-only runtime.
4. Keep container port `8000` unless analysis detected a different safe port.
5. Build/deploy the agent.
6. Confirm the container is running.
7. Confirm a VulnoraIQ target is auto-created.
8. Run a safe scan against that target if environment permits.
9. Remove deployment and delete project if supported by the UI/API.

Useful checks:

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | grep vulnoraiq-agent-lab || true
curl -s http://127.0.0.1:8000/healthz || true
```

Pass criteria:

- Managed import can generate or use a Dockerfile for the supported Python/FastAPI fixture.
- Build/deploy succeeds or fails with a clear actionable error.
- Target URL is correct for mode:
  - Desktop Mode: published localhost endpoint.
  - Docker Lab Mode: Docker network/container DNS endpoint.
- Cleanup removes container/deployment metadata.

### MT-074: mapped project without Dockerfile

Use the mapped `safe-echo-agent-mapped` project from MT-072. Ensure it has no Dockerfile.

1. Select `safe-echo-agent-mapped`.
2. Try to build/deploy it.
3. Record the error message.

Pass criteria:

- Agent Lab does not silently write a Dockerfile into the mapped/read-only project.
- Deployment fails with a clear message explaining that mapped projects without Dockerfiles must either add a Dockerfile to the mapped folder or be uploaded/imported into managed Agent Lab storage.
- No partial container or stale target remains after the failed deployment.

### MT-080: reports and evidence

Review produced Markdown, JSON, SARIF, dashboard, and HTML artifacts when available.

Pass criteria:

- JSON/SARIF parse successfully.
- Reports include evidence and enough context for human review.
- Sensitive values are redacted where applicable.
- Reports do not claim certified VAPT-grade assurance.
- Reports clearly state findings require human validation.

### MT-090: persistence

Desktop Mode:

1. Run a scan or create a runtime target.
2. Import `safe-echo-agent-local` through Local folder upload.
3. Stop the WebUI.
4. Restart Desktop Mode.
5. Confirm prior scan/report/target data is still visible.
6. Confirm `agent-lab/projects/safe-echo-agent-local` still exists.

Docker Lab Mode:

1. Run a scan or create a runtime target.
2. Import `safe-echo-agent-local` through Local folder upload or ZIP upload.
3. Run `docker compose down`.
4. Run `docker compose up -d`.
5. Confirm prior data is still visible.
6. Run `docker compose down -v` only for full reset.

Pass criteria:

- Data persists across normal restart.
- Managed Agent Lab imports persist across normal restart.
- Data is removed only by explicit volume/data reset.

### MT-100: negative tests

Run at least these negative checks:

- Save invalid target config.
- Send mutating request without CSRF token.
- Use wrong production token.
- Upload a ZIP with an unsafe path such as `../evil.txt` if you have a controlled way to create it.
- Upload a duplicate Local folder project ID.
- Use an invalid Project ID such as `demo-agent`, `mock-agent`, or `../../bad`.
- Send oversized request body to a suitable endpoint.
- Exceed rate limit in a controlled way.

Pass criteria:

- Server rejects unsafe/invalid actions.
- No mutation occurs after failed CSRF/auth checks.
- Invalid imports are rejected without writing unsafe files.
- No traceback is shown to the user.
- Logs contain useful diagnostics without leaking secrets.

### MT-110: release package smoke test

```bash
python scripts/build_release_package.py
# or, if installed:
vulnoraiq-package
```

Pass criteria:

- Release package builds.
- Desktop and Docker Lab launchers are present.
- README/User Guide/docs/manual test plan/LLM manual testing prompt are present.
- WebUI static assets are present.
- Secrets, `.venv`, `node_modules`, local reports, managed Agent Lab imports, mapped `projects/`, and temporary test artifacts are absent unless intentionally packaged as examples.

## Defect severity

| Severity | Meaning |
| --- | --- |
| Critical | Unsafe exposure, production auth bypass, destructive data loss, arbitrary local filesystem access, or unusable product start path. |
| High | Core Desktop/Docker Lab/WebUI/scan/Agent Lab import path broken. |
| Medium | Important workflow broken with workaround available. |
| Low | Documentation, layout, cosmetic, or minor usability issue. |

## Final report template

```markdown
# VulnoraIQ manual test report

## Environment

- OS:
- Browser:
- Python:
- Docker:
- Docker Compose:
- Node/npm:
- Branch:
- Commit SHA:
- Test date:

## Summary

| Area | Result | Notes |
| --- | --- | --- |
| Install/static validation | PASS/FAIL/SKIPPED | |
| Documentation consistency | PASS/FAIL/SKIPPED | |
| Desktop Mode | PASS/FAIL/SKIPPED | |
| Docker Lab Mode | PASS/FAIL/SKIPPED | |
| Auth/security boundaries | PASS/FAIL/SKIPPED | |
| WebUI pages | PASS/FAIL/SKIPPED | |
| Scan workflow | PASS/FAIL/SKIPPED | |
| Agent Lab import paths | PASS/FAIL/SKIPPED | |
| Agent Lab build/deploy | PASS/FAIL/SKIPPED | |
| UI/dark mode | PASS/FAIL/SKIPPED | |
| Persistence | PASS/FAIL/SKIPPED | |
| Release package | PASS/FAIL/SKIPPED | |

## Test results

| Test ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| MT-001 | PASS/FAIL/SKIPPED | | |

## Defects found

### DEFECT-001: Title

- Severity:
- Area:
- Test ID:
- Steps to reproduce:
- Expected:
- Actual:
- Evidence:
- Suspected root cause:
- Recommended fix:
- Retest status:

## Open questions

- Question 1

## Final recommendation

State whether the build is ready to release, needs fixes, or needs targeted retesting.
```
