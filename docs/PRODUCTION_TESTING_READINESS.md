# Production-Testing Readiness

VulnoraIQ can now be checked with a repeatable **production-testing readiness** gate before it is used for controlled testing workflows.

This gate does **not** claim that VulnoraIQ is ready for real-world VAPT assurance or production security assessment conclusions. It confirms that the safe local assessment path, report outputs, release metadata, mappings, fixtures, and authorisation controls are wired well enough for repeatable testing.

## Run the readiness gate

```bash
vulnoraiq-production-readiness --output-dir reports/output/production-readiness
```

This validates:

- package metadata, version alignment, CLI entries, dashboard asset, notices, OWASP docs, and evaluator assets
- configured target adapter contract shape
- OWASP starter benchmark fixture coverage
- local MITRE ATLAS mapping integrity
- OWASP LLM 2025 oracle coverage for all 10 categories
- non-demo target authorisation blocking
- README/status/CI wiring for functional testing

The gate may return `warn` while non-demo targets remain placeholders. That is acceptable for local production-testing readiness because placeholder endpoints are expected to stay blocked until an authorised endpoint is configured.

## Run the full readiness path with one functional acceptance run

```bash
vulnoraiq-production-readiness \
  --run-functional \
  --output-dir reports/output/production-readiness \
  --screenshot docs/assets/vulnoraiq-dashboard-example.svg
```

This additionally runs the safe `demo` target with the `baseline` profile and generates:

- Markdown report
- structured JSON report
- SARIF-style report
- Markdown dashboard
- HTML dashboard
- README dashboard SVG example
- readiness JSON and Markdown summaries

## Expected status interpretation

| Status | Meaning |
| --- | --- |
| `pass` | All readiness checks passed without warnings. |
| `warn` | Controlled testing can continue, but review warnings first. Current placeholder configured targets normally produce warnings until real authorised endpoints are configured. |
| `fail` | Do not proceed until the failed gate is fixed. |

## Real target testing rules

For any configured target outside `demo`:

1. Confirm written authorisation and scope.
2. Replace the placeholder endpoint in `config/targets.yaml`.
3. Set required token environment variables.
4. Validate target contracts.
5. Run with `--authorised` only inside approved scope.
6. Treat findings as starter framework evidence until deeper OWASP and MITRE ATLAS detection logic is validated.
