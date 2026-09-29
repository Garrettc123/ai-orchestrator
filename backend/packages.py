"""Load every registered repo and run it through the one process."""
from __future__ import annotations

import json
import os
from typing import Any, Dict

_HERE = os.path.dirname(os.path.abspath(__file__))
_PATH = os.path.join(_HERE, "catalog.json")


def _load() -> Dict[str, Dict[str, Any]]:
    with open(_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    out = {}
    for row in data.get("packages") or []:
        out[row["repo"]] = row
    return out


PACKAGES = _load()


def run(name: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    row = PACKAGES.get(name)
    if not row:
        return {"ok": False, "error": "unknown_package", "name": name, "count": len(PACKAGES)}
    from onesys import HOP_ORGAN, ONESYS, SPINE
    family = row["family"]
    if family == "intelligence":
        from knowledge import ask
        q = payload.get("query") or payload.get("task") or f"status {name}"
        kn = ask(str(q), intent=payload.get("intent") or "auto")
        return {"ok": bool(kn.get("ok")), "package": name, "family": family, "via": "knowledge", "result": kn}
    if family == "core":
        return {"ok": True, "package": name, "family": family, "via": "core", "result": ONESYS.snapshot()}
    hop = next((h for h, org in HOP_ORGAN.items() if org == family), None)
    if hop in SPINE:
        act = ONESYS.act(hop, payload=payload, confidence=float(payload.get("confidence", 0.8)))
        return {"ok": bool(act.get("ok")), "package": name, "family": family, "via": f"spine.{hop}", "result": act}
    return {"ok": True, "package": name, "family": family, "via": "registered", "state": row.get("state")}


def summary() -> Dict[str, Any]:
    by: Dict[str, int] = {}
    states: Dict[str, int] = {}
    for v in PACKAGES.values():
        by[v["family"]] = by.get(v["family"], 0) + 1
        states[v.get("state") or "?"] = states.get(v.get("state") or "?", 0) + 1
    return {"organism": "Garrett.ai", "count": len(PACKAGES), "by_family": by, "by_state": states, "names": sorted(PACKAGES)}
