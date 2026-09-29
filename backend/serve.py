#!/usr/bin/env python3
"""Stdlib revenue orchestrator — Garrett.ai surface."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from mars_reason import reason as mars_reason
from onesys import ONESYS, LIVE_SKU, PLINK, STRIPE_ACCT

HOST = os.getenv("APP_HOST", "0.0.0.0")
PORT = int(os.getenv("APP_PORT", "8010"))
STARTED = datetime.now(timezone.utc).isoformat()


def health():
    snap = ONESYS.snapshot()
    return {
        "status": "ok",
        "service": "garrett-ai",
        "organism": "Garrett.ai",
        "env": os.getenv("APP_ENV", "production"),
        "operator": "Garrett Carroll",
        "market": "DFW_TX",
        "started_at": STARTED,
        "port": PORT,
        "connectors": {
            "stripe": "live_account_linked",
            "openai": "missing",
            "hubspot": "oauth_connected_host",
            "gmail": "oauth_connected_host",
            "mars": "v1.1_client",
        },
        "revenue_loop": "armed",
        "cash_path": "stripe_payment_link",
        "stripe_account": STRIPE_ACCT,
        "sku": {
            "name": "Contractor Lead Leak Audit",
            "price": 47,
            "sku_code": "LLA-47",
            "plink": PLINK,
            "checkout": LIVE_SKU,
        },
        "organs": {k: v["state"] for k, v in snap["organs"].items()},
        "repo": "https://github.com/Garrettc123/ai-orchestrator",
        "mars": {"reason": "/v1/mars/reason", "contract": "1.1.0"},
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
        if path == "/v1/onesys/ledger":
            return self._json(200, {"ledger": ONESYS.ledger[-100:], "count": len(ONESYS.ledger)})
        if path == "/v1/revenue/loop":
            snap = ONESYS.snapshot()
            return self._json(200, {"spine": snap["spine"], "live_sku": LIVE_SKU, "organs": snap["organs"]})
        if path == "/":
            return self._json(200, {
                "service": "garrett-ai",
                "brand": "Garrett.ai",
                "health": "/health",
                "organism": "/v1/onesys",
                "act": "POST /v1/onesys/act",
                "loop": "/v1/revenue/loop",
                "mars": "/v1/mars/reason",
            })
        return self._json(404, {"error": "not_found", "path": path})

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()
        if path == "/v1/onesys/act":
            hop = body.get("hop") or body.get("stage") or ""
            if not hop:
                return self._json(422, {"error": "hop_required"})
            return self._json(200, ONESYS.act(hop, payload=body, confidence=float(body.get("confidence", 0.8))))
        if path == "/v1/revenue/leads":
            return self._json(200, ONESYS.act("intake", payload=body, confidence=0.9))
        if path == "/v1/revenue/checkout":
            return self._json(200, ONESYS.act("checkout", payload=body, confidence=0.9))
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
