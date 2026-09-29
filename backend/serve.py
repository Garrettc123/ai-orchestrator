#!/usr/bin/env python3
"""Garrett.ai — one process. Every repo runs through here."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote

from knowledge import ask as knowledge_ask, inventory as knowledge_inventory
from mars_reason import reason as mars_reason
from onesys import ONESYS, STRIPE_ACCT
from packages import run as run_package, summary as package_summary

HOST = os.getenv("APP_HOST", "0.0.0.0")
PORT = int(os.getenv("APP_PORT", "8010"))
STARTED = datetime.now(timezone.utc).isoformat()


def health():
    snap = ONESYS.snapshot()
    packs = package_summary()
    return {
        "status": "ok",
        "service": "garrett-ai",
        "organism": "Garrett.ai",
        "packages": packs["count"],
        "by_family": packs["by_family"],
        "operator": "Garrett Carroll",
        "started_at": STARTED,
        "port": PORT,
        "connectors": {"knowledge": knowledge_inventory()["providers"], "stripe": "live_account_linked"},
        "organs": {k: v["state"] for k, v in snap["organs"].items()},
        "stripe_account": STRIPE_ACCT,
        "storefront": "https://garrettc123.github.io/garrett.html",
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args), flush=True)

    def _json(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type,X-Api-Key")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            return self._json(200, health())
        if path in ("/v1/onesys", "/v1/organism"):
            return self._json(200, ONESYS.snapshot())
        if path in ("/v1/packages", "/v1/catalog"):
            return self._json(200, package_summary())
        if path.startswith("/v1/run/"):
            name = unquote(path.split("/v1/run/", 1)[1])
            return self._json(200, run_package(name, {}))
        if path in ("/v1/knowledge", "/v1/knowledge/status"):
            return self._json(200, knowledge_inventory())
        if path == "/":
            return self._json(200, {"service": "garrett-ai", "packages": "GET /v1/packages", "run": "POST /v1/run", "knowledge": "POST /v1/knowledge/ask"})
        return self._json(404, {"error": "not_found", "path": path})

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()
        if path == "/v1/run":
            name = body.get("repo") or body.get("package") or body.get("name") or ""
            if not name:
                return self._json(422, {"error": "repo_required", "hint": "pass repo: TITAN-Autonomous-Business-Empire"})
            return self._json(200, run_package(name, body))
        if path.startswith("/v1/run/"):
            name = unquote(path.split("/v1/run/", 1)[1])
            return self._json(200, run_package(name, body))
        if path in ("/v1/knowledge/ask", "/v1/knowledge"):
            query = body.get("query") or body.get("q") or body.get("task") or ""
            if not query:
                return self._json(422, {"error": "query_required"})
            return self._json(200, knowledge_ask(query, intent=body.get("intent") or "auto"))
        if path == "/v1/onesys/act":
            hop = body.get("hop") or body.get("stage") or ""
            if not hop:
                return self._json(422, {"error": "hop_required"})
            return self._json(200, ONESYS.act(hop, payload=body, confidence=float(body.get("confidence", 0.8))))
        if path == "/v1/mars/reason":
            query = body.get("query") or body.get("task") or ""
            if not query:
                return self._json(422, {"error": "query_required"})
            return self._json(200, mars_reason(query, route=body.get("route"), max_tokens=body.get("max_tokens")))
        return self._json(404, {"error": "not_found", "path": path})


def main():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"garrett-ai listening on {HOST}:{PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
