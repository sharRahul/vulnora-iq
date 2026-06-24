# WebUI Auth and Session Hardening

This document records the session handling direction for the VulnoraIQ WebUI.

## Current supported modes

| Mode | Intended use | Notes |
| --- | --- | --- |
| Disabled auth | Local launcher and isolated demo use | Not suitable for shared or exposed deployments. |
| Header token auth | Self-hosted internal deployment | Uses the configured VulnoraIQ token header and existing RBAC. |
| Trusted proxy identity | Reverse-proxy deployments | Uses trusted identity headers after proxy CIDR validation. |

## Frontend token storage

The default local frontend continues to use session-scoped browser storage. This keeps local demo behavior simple and avoids long-lived persistence across browser restarts.

The helper layer now exposes token storage strategies so later code can explicitly select session, memory, or local storage. Local storage must not be used for production credentials.

## Production recommendation

For production, prefer one of the following:

1. Trusted reverse proxy identity with strict trusted proxy CIDRs.
2. HTTP-only secure cookie mode once backend login/session endpoints are implemented.
3. OIDC/OAuth Authorization Code with PKCE behind the backend or reverse proxy.

## Deferred OIDC implementation

Full OIDC is intentionally deferred. It requires:

- Provider metadata configuration.
- Authorization Code with PKCE.
- Callback route.
- Token validation and refresh design.
- Secure cookie issuance.
- Logout and session revocation behavior.

Adding partial OIDC UI without backend enforcement would create a false sense of security, so this work remains a future enterprise-auth PR.

## Security rules

- Do not store production access tokens in local storage.
- Do not expose auth cookies to JavaScript.
- Keep CSRF validation on state-changing scan and runtime actions.
- Keep production mode fail-closed.
