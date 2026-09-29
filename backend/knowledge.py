"""Garrett.ai knowledge plane. Ground first. Generate second. Never invent keys."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from mars_reason import reason as mars_reason


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _present(name: str) -> bool:
    return bool((os.getenv(name) or "").strip())


def inventory() -> Dict[str, Any]:
    return {
        "organism": "Garrett.ai",
        "plane": "knowledge",
        "claim": "operator_system_not_agi",
        "providers": {
            "perplexity": _present("PERPLEXITY_API_KEY"),
            "anthropic": _present("ANTHROPIC_API_KEY"),
            "openai": _present("OPENAI_API_KEY"),
            "openrouter": _present("OPENROUTER_API_KEY"),
            "mars": _present("MARS_REASON_URL") or _present("MARS_PRODUCTION_URL"),
        },
        "ts": _now(),
    }


def _post(url: str, payload: Dict[str, Any], headers: Dict[str, str], timeout: int = 60) -> Dict[str, Any]:
    body = json.dumps(payload).encode()
    req = Request(url, data=body, headers=headers, method="POST")
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _perplexity(query: str, model: str = "sonar-pro") -> Dict[str, Any]:
    key = os.getenv("PERPLEXITY_API_KEY") or ""
    if not key:
        return {"ok": False, "reason": "perplexity_key_unset"}
    data = _post(
        "https://api.perplexity.ai/chat/completions",
        {
            "model": model,
            "messages": [
                {"role": "system", "content": "Ground answers in current sources. Cite. Do not invent cash."},
                {"role": "user", "content": query},
            ],
            "temperature": 0.2,
        },
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    choice = (data.get("choices") or [{}])[0]
    return {
        "ok": True,
        "provider": "perplexity",
        "model": data.get("model", model),
        "content": ((choice.get("message") or {}).get("content") or ""),
        "citations": data.get("citations") or [],
    }


def _openai_compat(url: str, key: str, model: str, query: str, provider: str) -> Dict[str, Any]:
    if not key:
        return {"ok": False, "reason": f"{provider}_key_unset"}
    data = _post(
        url,
        {
            "model": model,
            "messages": [
                {"role": "system", "content": "Reasoning layer for Garrett.ai. No simulated payments."},
                {"role": "user", "content": query},
            ],
            "temperature": 0.3,
        },
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    choice = (data.get("choices") or [{}])[0]
    return {
        "ok": True,
        "provider": provider,
        "model": data.get("model", model),
        "content": ((choice.get("message") or {}).get("content") or ""),
        "citations": [],
    }


def _anthropic(query: str) -> Dict[str, Any]:
    key = os.getenv("ANTHROPIC_API_KEY") or ""
    if not key:
        return {"ok": False, "reason": "anthropic_key_unset"}
    data = _post(
        "https://api.anthropic.com/v1/messages",
        {
            "model": os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-4-5",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": query}],
        },
        {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
    )
    blocks = data.get("content") or []
    text = "".join(b.get("text", "") for b in blocks if isinstance(b, dict))
    return {"ok": True, "provider": "anthropic", "model": data.get("model"), "content": text, "citations": []}


def ask(query: str, intent: str = "auto") -> Dict[str, Any]:
    intent = (intent or "auto").lower()
    tried: List[str] = []
    errors: List[str] = []
    if intent in {"search", "research", "fact", "ground"}:
        order = ["perplexity", "mars", "anthropic", "openai", "openrouter"]
    elif intent in {"reason", "mars"}:
        order = ["mars", "perplexity", "anthropic", "openai"]
    elif intent in {"write", "chat", "claude", "gpt"}:
        order = ["anthropic", "openai", "openrouter", "perplexity"]
    else:
        order = ["perplexity", "mars", "anthropic", "openai", "openrouter"]

    for name in order:
        tried.append(name)
        try:
            if name == "perplexity":
                out = _perplexity(query)
            elif name == "mars":
                raw = mars_reason(query)
                if raw.get("queued") or not raw.get("success"):
                    out = {"ok": False, "reason": (raw.get("route") or {}).get("reason") or raw.get("error") or "mars_dark"}
                else:
                    out = {
                        "ok": True,
                        "provider": "mars",
                        "model": raw.get("model"),
                        "content": raw.get("reasoning") or raw.get("content") or "",
                        "citations": [],
                        "route": raw.get("route"),
                    }
            elif name == "anthropic":
                out = _anthropic(query)
            elif name == "openai":
                out = _openai_compat(
                    "https://api.openai.com/v1/chat/completions",
                    os.getenv("OPENAI_API_KEY") or "",
                    os.getenv("OPENAI_MODEL") or "gpt-4.1-mini",
                    query,
                    "openai",
                )
            else:
                out = _openai_compat(
                    "https://openrouter.ai/api/v1/chat/completions",
                    os.getenv("OPENROUTER_API_KEY") or "",
                    os.getenv("OPENROUTER_MODEL") or "anthropic/claude-sonnet-4.5",
                    query,
                    "openrouter",
                )
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append(f"{name}:{exc.__class__.__name__}")
            continue
        if out.get("ok"):
            return {"ok": True, "intent": intent, "tried": tried, "result": out, "inventory": inventory(), "ts": _now()}
        errors.append(f"{name}:{out.get('reason')}")

    return {
        "ok": False,
        "queued": True,
        "intent": intent,
        "tried": tried,
        "errors": errors,
        "inventory": inventory(),
        "hint": "Set PERPLEXITY_API_KEY and one generation key on the host. Do not paste keys in chat.",
        "ts": _now(),
    }
