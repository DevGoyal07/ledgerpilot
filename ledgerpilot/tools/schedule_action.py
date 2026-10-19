"""
schedule_action — a STATE-CHANGING action (T2_ACT). Schedules a payment
reminder or a cash-flow alert for the owner. Because it has a side effect, it
can never run without an explicit user confirmation, even if the agent's
ceiling allows acting. In the sandbox the "action" is writing to an actions
ledger; in production this is where a real reminder/notification would fire.

Permission: T2_ACT (confirmation always required).
"""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

from ..agent.permissions import Tier

REQUIRED_TIER = Tier.T2_ACT
NAME = "schedule_action"
ACTIONS_LEDGER = Path(__file__).parent.parent.parent / "logs" / "actions_ledger.jsonl"

SCHEMA = {
    "name": NAME,
    "description": "Schedule a payment reminder or cash-flow alert for the owner. "
                   "STATE-CHANGING: always requires explicit user confirmation "
                   "before it executes.",
    "parameters": {
        "type": "object",
        "properties": {
            "business_id": {"type": "string"},
            "action_type": {"type": "string",
                            "enum": ["payment_reminder", "cashflow_alert", "invoice_followup"]},
            "detail": {"type": "string", "description": "What the reminder/alert says."},
            "trigger_date": {"type": "string", "description": "YYYY-MM-DD"},
        },
        "required": ["business_id", "action_type", "detail"],
    },
}


def summarize(business_id, action_type, detail, trigger_date=None):
    return f"{action_type} for {business_id} on {trigger_date or 'next cycle'}: {detail}"


def run(business_id: str, action_type: str, detail: str,
        trigger_date: str | None = None, perms=None) -> dict:
    summary = summarize(business_id, action_type, detail, trigger_date)
    if perms:
        # Raises ConfirmationRequired if not yet confirmed, PermissionError if above ceiling.
        perms.check(REQUIRED_TIER, action_summary=summary)
    ACTIONS_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "business_id": business_id,
        "action_type": action_type,
        "detail": detail,
        "trigger_date": trigger_date,
        "status": "scheduled",
    }
    with ACTIONS_LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return {"status": "scheduled", "confirmation": summary, "record": record}
