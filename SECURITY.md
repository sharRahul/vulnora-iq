# Security Policy

This document defines VulnoraIQ's supported security boundary, responsible-use rules, production controls, accepted risks, and vulnerability reporting process.

## Security posture

VulnoraIQ is a self-hosted defensive AI security assessment application for authorised testing of LLM applications, RAG pipelines, AI agents, tool-using systems, GenAI data-security surfaces, and orchestration layers.

`0.3.0` has passed the controlled internal production-readiness gate for the current laptop, workstation, lab-machine, and internal-server deployment model. Findings are framework evidence for authorised human review. They are not certified VAPT-grade assurance, a substitute for independent testing, or permission to test systems without explicit approval.

The experimental Agent Lab adds local Docker build/run orchestration for real AI-agent projects. Treat it as a local-lab capability until its hardening backlog is complete.

## Supported deployment boundary

| Deployment model | Status | Notes |
| --- | --- | --- |
| Local laptop/workstation Docker lab | Complete | Default WebUI publish is loopback-only at `127.0.0.1:8787`. |
| Experimental Agent Lab | Experimental | Imports real agent projects, configures LLM providers, runs Docker containers, optionally uses GPU flags, and auto-registers runtime targets. Requires Docker socket access in the current Compose lab. |
| Standalone local WebUI launcher | Complete | Loopback-only convenience path with startup checks and local stop control. |
| Self-hosted internal server | Complete for current scope | Requires production mode, auth, real secrets, reverse proxy/TLS for remote access, audit retention, and backup controls. Do not expose Agent Lab on shared systems without an explicit risk decision. |
| Trusted reverse-proxy identity | Supported | Use only when the proxy authenticates users and strips spoofed identity headers. |
| Direct OIDC/JWT | Future maturity item | Planned in `docs/future-plans/OIDC_JWT_AUTH_PLAN.md`; not required for current local single-user usage. |
| Certified VAPT-grade assurance | Not claimed | External independent review is still required for stronger assurance claims. |

## Responsible use

Use VulnoraIQ only against systems you own or are explicitly authorised to assess.

Allowed use includes internal AI security validation, authorised AI red-team exercises, defensive control testing, CI regression checks for owned AI systems, and evidence collection for internal review.

All configured targets require explicit authorisation. Reports and artifacts may contain sensitive evidence and must be handled according to your organisation's data-handling rules.

Users are solely responsible for complying with [`ACCEPTABLE_USE.md`](ACCEPTABLE_USE.md), obtaining required authorisation, and using VulnoraIQ only within the defensive assessment scope. To the fullest extent permitted by law, the maintainer and contributors disclaim responsibility for prohibited, unlawful, unauthorised, or otherwise improper use by any user or third party.

## Auth and web security controls

The self-hosted production path includes:

- auth enabled by default for the hosted server and required in production;
- fail-closed protected endpoints;
- `VULNORAIQ_ENV=production` runtime validation;
- required strong `VULNORAIQ_ADMIN_TOKEN` for token-mode production deployments;
- known default token rejection;
- internal development admin token disabled in production;
- constant-time token comparison;
- `VULNORAIQ_AUTH_MODE=token`;
- `VULNORAIQ_AUTH_MODE=trusted_proxy` with trusted CIDR validation;
- viewer, analyst, and admin roles;
- CSRF protection for write actions;
- request body limits, rate limits, scan concurrency limits, and scan queue limits;
- security headers on normal and error responses;
- artifact path protection;
- role-aware `/api/config`;
- auth-protected `/metrics` by default;
- structured JSON audit logs with request correlation IDs.

For shared/internal-server deployments:

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="replace-with-a-strong-random-token-min-20-chars"
export VULNORAIQ_JOB_STORE_BACKEND=sqlite
export VULNORAIQ_JOB_STORE_PATH=/data/jobs.db
export VULNORAIQ_WEB_OUTPUT_ROOT=/data/reports

python scripts/validate_runtime_production_config.py
```

For trusted reverse-proxy identity:

```bash
export VULNORAIQ_TRUST_PROXY_HEADERS=true
export VULNORAIQ_TRUSTED_PROXY_CIDRS="127.0.0.1/32,::1/128"
export VULNORAIQ_AUTH_MODE=trusted_proxy
```

Only enable trusted-proxy identity when the proxy performs authentication and removes spoofable inbound identity headers before forwarding requests to VulnoraIQ.

## Container, CI, and supply-chain controls

The default Docker Compose lab keeps the WebUI bound to host loopback. Containers run with dropped capabilities and no privileged mode. The experimental Agent Lab uses the Docker socket so the WebUI container can build and run imported agent projects; this is intentionally documented as a higher-trust local-lab control surface rather than a hardened multi-tenant boundary.

The current CI/release posture includes Ruff, mypy, pytest, `pip check`, `pip-audit`, package metadata validation, OWASP/ATLAS validation, GenAI readiness validation, production readiness validation, hosted WebUI browser flow, functional acceptance, Docker smoke testing, release package builds, SBOM generation, Trivy filesystem/image reports, SARIF upload, GHCR publishing path, and Cosign keyless image-signing path.

## Accepted risks and future work

The following are accepted for the current self-hosted local/internal model and should be revisited as the application matures:

- direct OIDC/JWT is not implemented yet;
- trusted-proxy identity is the current enterprise identity bridge;
- local Docker and launcher modes are for loopback-only local use;
- Agent Lab requires Docker socket access for local build/run operations and remains experimental;
- CSRF and rate-limit stores are in-memory and single-instance;
- SQLite is single-node and not high availability;
- SIEM-specific rule packs are not packaged yet;
- native OS certificate-signed installers remain future work;
- external independent review is still required for stronger assurance claims;
- scanner/evaluator results are framework evidence requiring human review.

## Reporting vulnerabilities

Please report vulnerabilities privately.

Preferred channels:

1. Open a GitHub Security Advisory for the repository.
2. If advisories are not available, contact the maintainer through a private repository-owner channel.

Do **not** publicly disclose an exploitable issue before maintainers have had a reasonable opportunity to investigate and remediate it.

Include the affected version or commit, affected component, reproduction steps, expected and actual behaviour, and whether the issue affects local-only or self-hosted internal deployment assumptions.
