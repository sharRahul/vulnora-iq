from __future__ import annotations

import argparse
import json
import sys

from webui.agent_runtime import AgentRuntimeManager


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether Docker is available for VulnoraIQ agent runtimes.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output")
    args = parser.parse_args()

    status = AgentRuntimeManager().docker_status()
    payload = {
        "available": bool(status.get("available")),
        "path": status.get("path"),
        "message": status.get("message"),
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        state = "available" if payload["available"] else "not available"
        print(f"Docker runtime is {state}.")
        print(payload["message"] or "No Docker detail returned.")
        if payload.get("path"):
            print(f"Docker CLI: {payload['path']}")
    return 0 if payload["available"] else 1


if __name__ == "__main__":
    sys.exit(main())
