"""
LedgerPilot agent core.

Flow per user turn:
  1. plan    -> LLM (or offline router) decides which tool(s) to call
  2. gate    -> each call is checked against the permission tier; T2_ACT calls
                without confirmation surface a confirmation prompt instead of
                executing
  3. execute -> tool runs; every decision + result is logged to the audit log
  4. narrate -> results are verbalised into an owner-friendly reply

The AuditLogger writes a structured JSONL trail — this file IS the
"execution evidence" deliverable (sandbox operation logs).
"""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

from . import llm, datastore
from .permissions import PermissionContext, Tier, ConfirmationRequired, PermissionError_
from .. import tools

AUDIT_LOG = Path(__file__).parent.parent.parent / "logs" / "audit_log.jsonl"


class AuditLogger:
    def __init__(self, path=AUDIT_LOG):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event, **fields):
        rec = {"ts": datetime.now().isoformat(timespec="seconds"), "event": event, **fields}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str) + "\n")
        return rec


class Agent:
    def __init__(self, max_tier=Tier.T2_ACT, logger: AuditLogger | None = None):
        datastore.ensure_data()
        self.perms = PermissionContext(max_tier=max_tier)
        self.logger = logger or AuditLogger()
        self.context = {
            "businesses": datastore.list_businesses(),
            "current_business": "SME001",
            "pending_action": None,
        }

    # -- session helpers --
    def set_business(self, biz_id):
        datastore.get_business(biz_id)  # validates
        self.context["current_business"] = biz_id

    # -- main entry --
    def handle(self, user_msg: str) -> dict:
        self.logger.log("user_message", text=user_msg,
                        business=self.context["current_business"],
                        backend=llm.backend_name())
        calls = llm.plan(user_msg, self.context)
        self.logger.log("plan", tools=[c.name for c in calls],
                        args=[c.arguments for c in calls])

        tool_results = []
        pending = None
        for call in calls:
            mod = tools.get(call.name)
            if not mod:
                tool_results.append((call.name, {"error": "unknown tool"}))
                continue
            required = getattr(mod, "REQUIRED_TIER", Tier.T0_READ)
            # wire confirmation token if this call matches a pending action
            if (self.context.get("pending_action")
                    and call.name == self.context["pending_action"]["name"]):
                summary = _action_summary(call)
                self.perms.confirmed_action = summary
            try:
                self.logger.log("tool_call", tool=call.name,
                                required_tier=int(required), args=call.arguments)
                result = mod.run(**call.arguments, perms=self.perms)
                self.logger.log("tool_result", tool=call.name, ok=True,
                                summary=_short(result))
                tool_results.append((call.name, result))
                if call.name == "schedule_action":
                    self.context["pending_action"] = None
                    self.perms.confirmed_action = None
            except ConfirmationRequired as e:
                self.logger.log("confirmation_required", tool=call.name,
                                action=e.action_summary)
                pending = {"name": call.name, "arguments": call.arguments,
                           "summary": e.action_summary}
                self.context["pending_action"] = pending
            except PermissionError_ as e:
                self.logger.log("permission_denied", tool=call.name, reason=str(e))
                tool_results.append((call.name, {"error": f"blocked: {e}"}))
            except Exception as e:
                self.logger.log("tool_error", tool=call.name, error=str(e))
                tool_results.append((call.name, {"error": str(e)}))

        if pending:
            reply = (f"⚠️ This needs your confirmation before I act:\n\n"
                     f"**{pending['summary']}**\n\nReply 'yes' to confirm, or tell me what to change.")
        else:
            reply = llm.narrate(user_msg, tool_results, self.context)

        self.logger.log("assistant_reply", chars=len(reply),
                        pending_confirmation=bool(pending))
        return {"reply": reply, "tool_results": tool_results,
                "pending_confirmation": pending,
                "backend": llm.backend_name()}


def _action_summary(call):
    from ..tools.schedule_action import summarize
    a = call.arguments
    return summarize(a.get("business_id"), a.get("action_type"),
                     a.get("detail"), a.get("trigger_date"))


def _short(result):
    if isinstance(result, dict):
        return {k: result[k] for k in list(result)[:4]}
    return str(result)[:200]
