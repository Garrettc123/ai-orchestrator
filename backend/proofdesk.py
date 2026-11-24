"""Proofdesk organ adapter for Garrett.ai spine.

Embeds the evidence-backed callback-priority CSV workflow so a paid LLA-47
can trigger same-day fulfillment from customer-owned exports only.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from onesys import ONESYS, LIVE_SKU


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass
class EvidenceRecord:
    id: str
    source_file: str
    row_index: int
    raw: Dict[str, Any]
    priority_score: float = 0.0
    review_reason: str = ""
    contact_permission: bool = False
    held: bool = True
    created_at: str = field(default_factory=_now)


class CallbackPriorityWorkflow:
    def __init__(self) -> None:
        self.records: List[EvidenceRecord] = []
        self.held: List[EvidenceRecord] = []

    def ingest_csv(self, content: str, source_file: str = "upload.csv") -> Dict[str, Any]:
        reader = csv.DictReader(io.StringIO(content))
        new_records: List[EvidenceRecord] = []
        for idx, row in enumerate(reader):
            rec = EvidenceRecord(
                id=_id("ev"),
                source_file=source_file,
                row_index=idx,
                raw={k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k},
            )
            rec.priority_score = self._score(rec.raw)
            rec.review_reason = self._reason(rec.raw, rec.priority_score)
            rec.contact_permission = self._has_permission(rec.raw)
            rec.held = not rec.contact_permission
            new_records.append(rec)
            self.records.append(rec)
            if rec.held:
                self.held.append(rec)

        prioritized = sorted(new_records, key=lambda r: r.priority_score, reverse=True)
        result = {
            "ingested": len(new_records),
            "held": sum(1 for r in new_records if r.held),
            "ready": sum(1 for r in new_records if not r.held),
            "top_priorities": [
                {
                    "id": r.id,
                    "score": round(r.priority_score, 2),
                    "reason": r.review_reason,
                    "held": r.held,
                }
                for r in prioritized[:10]
            ],
            "sku": "LLA-47",
            "checkout": LIVE_SKU,
            "ts": _now(),
        }
        # Emit into the organism spine as fulfillment evidence
        ONESYS.emit(
            "proofdesk.ingested",
            result,
            "commit" if result["ready"] else "continue",
            hop="fulfillment",
            organ="fulfillment",
        )
        return result

    def _score(self, raw: Dict[str, Any]) -> float:
        score = 0.0
        status = str(raw.get("lead_status", "") or raw.get("status", "")).lower()
        if any(s in status for s in ("new", "open", "uncontacted", "pending")):
            score += 0.4
        if raw.get("value") or raw.get("amount") or raw.get("estimate"):
            score += 0.3
        if not (raw.get("last_contact") or raw.get("last_touch")):
            score += 0.2
        if raw.get("notes") or raw.get("comments"):
            score += 0.1
        return min(score, 1.0)

    def _reason(self, raw: Dict[str, Any], score: float) -> str:
        reasons = []
        status = str(raw.get("lead_status", "") or raw.get("status", "")).lower()
        if any(s in status for s in ("new", "open", "uncontacted")):
            reasons.append("status indicates no confirmed follow-up")
        if not (raw.get("last_contact") or raw.get("last_touch")):
            reasons.append("no recorded last contact")
        if raw.get("value") or raw.get("amount"):
            reasons.append("monetary value present")
        if not reasons:
            reasons.append("default review queue")
        return "; ".join(reasons) + f" (score={score:.2f})"

    def _has_permission(self, raw: Dict[str, Any]) -> bool:
        perm = str(raw.get("contact_permission", "") or raw.get("permission", "") or "").lower()
        return perm in ("yes", "true", "confirmed", "opt-in", "1")

    def export_held_summary(self) -> str:
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["id", "source_file", "row_index", "priority_score", "review_reason", "held"])
        for r in self.held:
            writer.writerow([r.id, r.source_file, r.row_index, f"{r.priority_score:.2f}", r.review_reason, r.held])
        return out.getvalue()


WORKFLOW = CallbackPriorityWorkflow()
