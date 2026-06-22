from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class SafeEchoHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802 - stdlib API
        if self.path != "/invoke":
            self.send_error(404)
            return
        length = int(self.headers.get("content-length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        payload = json.loads(raw_body or "{}")
        prompt = str(payload.get("prompt") or payload.get("input") or "")
        body = json.dumps({"output": self._safe_response(prompt)}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @staticmethod
    def _safe_response(prompt: str) -> str:
        lowered = prompt.lower()
        if "system prompt" in lowered or "protected instruction" in lowered:
            return "I cannot disclose protected instructions."
        if "credential" in lowered or "token" in lowered or "secret" in lowered:
            return "I cannot disclose sensitive values."
        return f"Safe local echo target received: {prompt[:160]}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a safe local HTTP JSON demo target.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), SafeEchoHandler)
    print(f"Safe local demo target listening on http://{args.host}:{args.port}/invoke")
    server.serve_forever()


if __name__ == "__main__":
    main()
