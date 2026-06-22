# Local Demo Targets

These examples are safe local fixtures for framework development and demonstrations.

They are not production services and should not be exposed to the internet.

## Safe echo HTTP target

Run locally:

```bash
python examples/local_demo_targets/safe_echo_http_app.py --host 127.0.0.1 --port 8765
```

Configure `config/targets.yaml` with a local HTTP JSON target such as:

```yaml
targets:
  local_safe_echo:
    type: http_json
    endpoint: http://127.0.0.1:8765/invoke
    auth: none
```

Then run the framework with explicit authorisation because this is a configured non-demo target:

```bash
python scripts/run_scan.py --target local_safe_echo --profile baseline --authorised
```

## Control-gap fixture

`control_gap_fixture.py` is an importable local fixture used by tests and demos to model expected pass/fail control behaviour without network access.
