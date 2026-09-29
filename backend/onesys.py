"""Garrett.ai — one organism. Organs are families, not repos."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json
import os
from uuid import uuid4

LIVE_SKU = "https://buy.stripe.com/3cI00j7YV0hQgDp8BR43S2v"
PLINK = "plink_1UKUvNFKGbk21LK5jhAXBaLz"
STRIPE_ACCT = "acct_1SS3dpFKGbk21LK5"
COMMIT_MIN = 0.72
CONTRA_ABORT = 2
STALL_ESCALATE = 3

SPINE = (
    "intake",
    "enrichment",
    "outreach",
    "proposal",
    "checkout",
    "crm",
    "fulfillment",
    "report",
)

HOP_ORGAN = {
    "intake": "revenue",
    "enrichment": "research",
    "outreach": "outreach",
    "proposal": "proposal",
    "checkout": "billing",
    "crm": "crm",
    "fulfillment": "fulfillment",
    "report": "governance",
}

MONEY_HOPS = frozenset({"outreach", "checkout", "crm"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _organ(family: str, state: str, provides: List[str], **extra: Any) -> Dict[str, Any]:
    labels = {
        "revenue": "Revenue",
        "crm": "CRM",
        "proposal": "Proposal",
        "outreach": "Outreach",
        "billing": "Billing",
        "fulfillment": "Fulfillment",
        "research": "Research",
        "governance": "Governance",
        "content": "Content",
        "compliance": "Compliance",
        "intelligence": "Enterprise Intelligence",
    }
    row = {
        "id": family,
        "family": labels[family],
        "state": state,
        "provides": provides,
        "packaging": [],
    }
    row.update(extra)
    return row


def _bootstrap_organs() -> Dict[str, Dict[str, Any]]:
    return {
        "revenue": _organ("revenue", "monetizing", ["revenue.intake"], sku="LLA-47"),
        "crm": _organ("crm", "provisioning", ["crm.sync"], portal="247022078"),
        "proposal": _organ("proposal", "provisioning", ["proposal.generate"]),
        "outreach": _organ("outreach", "provisioning", ["outreach.send"]),
        "billing": _organ("billing", "healthy", ["billing.checkout"], account=STRIPE_ACCT, checkout=LIVE_SKU),
        "fulfillment": _organ("fulfillment", "provisioning", ["fulfillment.trigger"]),
        "research": _organ("research", "provisioning", ["research.enrich"]),
        "governance": _organ("governance", "dormant", ["governance.identity", "governance.timechain"], sku="BF-GOV-SOV"),
        "content": _organ("content", "healthy", ["content.storefront"], url="https://garrettc123.github.io/"),
        "compliance": _organ("compliance", "healthy", ["compliance.policy"], forbidden=["live_4242"]),
        "intelligence": _organ("intelligence", "provisioning", ["ei.control_loop", "rhns.cmc"]),
    }


@dataclass
class Event:
    id: str
    type: str
    ts: str
    payload: Dict[str, Any]
    cmc: str
    hop: Optional[str] = None
    organ: Optional[str] = None


@dataclass
class OneSys:
    events: List[Event] = field(default_factory=list)
    ledger: List[Dict[str, Any]] = field(default_factory=list)
    organs: Dict[str, Dict[str, Any]] = field(default_factory=_bootstrap_organs)

    def emit(self, etype: str, payload: Dict[str, Any], cmc: str, hop: Optional[str] = None, organ: Optional[str] = None) -> Event:
        ev = Event(id=_id("evt"), type=etype, ts=_now(), payload=payload, cmc=cmc, hop=hop, organ=organ)
        self.events.append(ev)
        if cmc == "commit":
            self.ledger.append({"id": ev.id, "type": etype, "ts": ev.ts, "hop": hop, "organ": organ})
        return ev

    def cmc(self, hop: str, confidence: float, contradictions: int = 0, stalls: int = 0) -> str:
        if contradictions >= CONTRA_ABORT:
            return "abort"
        if hop in MONEY_HOPS and confidence < COMMIT_MIN:
            return "escalate" if stalls >= STALL_ESCALATE else "continue"
        if stalls >= STALL_ESCALATE:
            return "escalate"
        if hop in MONEY_HOPS and confidence >= COMMIT_MIN:
            return "commit"
        return "continue"

    def snapshot(self) -> Dict[str, Any]:
        return {
            "name": "Garrett.ai",
            "kind": "single_organism",
            "infra": "own-box",
            "rule": "organs_are_families_not_repos",
            "not": ["chatbot", "agi", "repo_per_organ", "vercel_as_brain"],
            "core": "ai-orchestrator",
            "brand": "Garrett.ai",
            "rhns": {"planner": "rgt+hrm", "gate": "cmc", "commit_min": COMMIT_MIN},
            "spine": list(SPINE),
            "organs": self.organs,
            "events": len(self.events),
            "committed": len(self.ledger),
            "cash": {
                "account": STRIPE_ACCT,
                "default_sku": "LLA-47",
                "checkout": LIVE_SKU,
                "rule": "paid=true only",
            },
            "ts": _now(),
        }

    def act(self, hop: str, payload: Optional[Dict[str, Any]] = None, confidence: float = 0.8) -> Dict[str, Any]:
        payload = payload or {}
        if hop not in SPINE:
            ev = self.emit("system.rejected", {"hop": hop}, "abort")
            return {"ok": False, "cmc": "abort", "event": ev.id, "error": "unknown_hop"}
        organ = HOP_ORGAN[hop]
        if self.organs[organ]["state"] == "blocked":
            ev = self.emit(f"spine.{hop}", payload, "abort", hop=hop, organ=organ)
            return {"ok": False, "cmc": "abort", "event": ev.id, "organ": organ, "error": "organ_blocked"}
        decision = self.cmc(hop, float(confidence))
        if hop == "checkout" and decision == "commit":
            out: Dict[str, Any] = {
                "sku": payload.get("sku", "LLA-47"),
                "url": LIVE_SKU,
                "plink": PLINK,
                "mode": "live_payment_link",
                "charge": False,
            }
        elif hop == "intake":
            out = {"stage": "intake", "offer": {"sku": "LLA-47", "checkout": LIVE_SKU}, "lead": payload}
        elif hop == "fulfillment":
            out = {"queued": True, "requires": "stripe.paid=true"}
        else:
            out = {"hop": hop, "accepted": True}
        ev = self.emit(f"spine.{hop}", {**payload, "result": out}, decision, hop=hop, organ=organ)
        return {"ok": decision != "abort", "cmc": decision, "event": ev.id, "organ": organ, "hop": hop, "result": out}


def persist(inst: OneSys) -> None:
    root = os.getenv("DATA_DIR")
    if not root:
        return
    os.makedirs(root, exist_ok=True)
    path = os.path.join(root, "ledger.jsonl")
    with open(path, "w", encoding="utf-8") as fh:
        for row in inst.ledger:
            fh.write(json.dumps(row) + "\n")


class Persisting(OneSys):
    def emit(self, etype, payload, cmc, hop=None, organ=None):
        ev = super().emit(etype, payload, cmc, hop=hop, organ=organ)
        persist(self)
        return ev


ONESYS = Persisting()
