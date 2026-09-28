#!/usr/bin/env python3
"""Stdlib revenue orchestrator — no pip required."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = 8000
STARTED = datetime.now(timezone.utc).isoformat()
LIVE_SKU = "https://buy.stripe.com/3cI00j7YV0hQgDp8BR43S2v"
PLINK = "plink_1UKUvNFKGbk21LK5jhAXBaLz"
STRIPE_ACCT = "acct_1SS3dpFKGbk21LK5"


def health():
    return {
        "status": "ok",
        "service": "garcar-ai-orchestrator",
        "env": "production",
        "operator": "Garrett Carroll",
        "market": "DFW_TX",
        "started_at": STARTED,
        "connectors": {
            "stripe": "live_account_linked",
            "openai": "missing",
            "hubspot": "oauth_connected_host",
            "gmail": "oauth_connected_host",
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
        "repo": "https://github.com/Garrettc123/ai-orchestrator",
    }


def loop():
    return {
        "spine": [
            "lead_intake",
            "enrichment",
            "outreach",
            "proposal",
            "checkout",
            "crm_sync",
            "fulfillment",
            "executive_report",
        ],
        "live_sku": LIVE_SKU,
        "storefront": "https://garrettc123.github.io/",
        "stripe_account": STRIPE_ACCT,
        "hubspot_deals_open": ["Comfort Experts LLA-47", "Service Champs LLA-47"],
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
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            return self._json(200, health())
        if path == "/v1/revenue/loop":
            return self._json(200, loop())
        if path == "/":
            return self._json(200, {"service": "garcar-ai-orchestrator", "health": "/health", "loop": "/v1/revenue/loop"})
        return self._json(404, {"error": "not_found", "path": path})

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()
        if path == "/v1/revenue/leads":
            return self._json(200, {"accepted": True, "stage": "intake", "lead": body, "offer": {"sku": "LLA-47", "checkout": LIVE_SKU}})
        if path == "/v1/revenue/checkout":
            return self._json(200, {"mode": "live_payment_link", "url": LIVE_SKU, "plink": PLINK, "sku": body.get("sku", "LLA-47"), "email": body.get("email"), "company": body.get("company")})
        return self._json(404, {"error": "not_found", "path": path})


def main():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"garcar-ai-orchestrator listening on {HOST}:{PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
