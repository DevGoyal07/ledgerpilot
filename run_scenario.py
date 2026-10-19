"""
End-to-end sandbox scenario runner — produces the execution-evidence logs.

It drives the agent through a realistic session across all three businesses,
exercising every tool and, critically, the full permission flow:
  - a T2_ACT action attempted WITHOUT confirmation  -> gated (ConfirmationRequired)
  - the same action then CONFIRMED by the user       -> executed + written to ledger
  - a T2_ACT action attempted with the ceiling too low -> permission denied

Outputs:
  logs/audit_log.jsonl      full structured decision/operation trail
  logs/actions_ledger.jsonl the state-changing actions that were authorised
  logs/scenario_transcript.txt  human-readable transcript
"""
from __future__ import annotations
import json
from pathlib import Path

from ledgerpilot.agent.core import Agent, AuditLogger
from ledgerpilot.agent.permissions import Tier

ROOT = Path(__file__).parent
LOGS = ROOT / "logs"
for f in ("audit_log.jsonl", "actions_ledger.jsonl", "scenario_transcript.txt"):
    (LOGS / f).unlink(missing_ok=True)

transcript = []


def say(line=""):
    print(line)
    transcript.append(line)


def turn(agent, biz, msg):
    agent.set_business(biz)
    say(f"\n[{biz}] USER: {msg}")
    r = agent.handle(msg)
    say(f"[{biz}] LEDGERPILOT ({r['backend']}):")
    say(r["reply"])
    if r["pending_confirmation"]:
        say(f"   << awaiting confirmation: {r['pending_confirmation']['summary']} >>")
    return r


def main():
    say("=" * 70)
    say("LedgerPilot — sandbox execution evidence")
    say("All data is simulated. No real accounts or funds are touched.")
    say("=" * 70)

    # Live agent: guarded autonomy — may act, but every action needs confirmation.
    agent = Agent(max_tier=Tier.T2_ACT, logger=AuditLogger())

    # 1. Health check — PixelForge (strong)
    turn(agent, "SME003", "How is PixelForge doing financially?")

    # 2. Cash-flow + alerts — ThreadCraft (the cash-crunch story)
    turn(agent, "SME002", "Will ThreadCraft run short of cash? Show me the risks.")

    # 3. Financing match with amount + purpose — ThreadCraft
    turn(agent, "SME002", "I need about 15 lakh to bridge a cash gap. What financing suits me?")

    # 4. Financing match — Cafe expansion
    turn(agent, "SME001", "I want a loan of 8 lakh for expansion. What are my options?")

    # 5. ACTION attempted without confirmation -> should be GATED
    say("\n" + "-" * 70)
    say("PERMISSION DEMO 1: action requested — must be confirmed, not auto-run")
    say("-" * 70)
    r = turn(agent, "SME002", "Set an alert to chase the overdue invoices next Monday.")
    assert r["pending_confirmation"], "expected a confirmation gate"

    # 6. User confirms -> action executes and is written to the ledger
    say("\n" + "-" * 70)
    say("PERMISSION DEMO 2: user confirms the pending action -> it executes")
    say("-" * 70)
    turn(agent, "SME002", "Yes, go ahead.")

    # 7. Ceiling too low -> permission denied even if user tries to confirm
    say("\n" + "-" * 70)
    say("PERMISSION DEMO 3: read-only agent cannot act at all")
    say("-" * 70)
    ro = Agent(max_tier=Tier.T0_READ, logger=agent.logger)
    ro.set_business("SME001")
    ro.context["pending_action"] = {
        "name": "schedule_action",
        "arguments": {"business_id": "SME001", "action_type": "payment_reminder",
                      "detail": "rent due", "trigger_date": "2026-11-03"},
    }
    r = ro.handle("yes confirm the reminder")
    say(f"[SME001] LEDGERPILOT: {r['reply']}")

    # ---- summary ----
    audit = (LOGS / "audit_log.jsonl").read_text().strip().splitlines()
    events = {}
    for ln in audit:
        e = json.loads(ln)["event"]
        events[e] = events.get(e, 0) + 1
    say("\n" + "=" * 70)
    say("EVIDENCE SUMMARY")
    say(f"Total audit events logged: {len(audit)}")
    for k in sorted(events):
        say(f"  {k:24} {events[k]}")
    ledger = LOGS / "actions_ledger.jsonl"
    n_actions = len(ledger.read_text().strip().splitlines()) if ledger.exists() else 0
    say(f"Authorised state-changing actions in ledger: {n_actions}")
    say("=" * 70)

    (LOGS / "scenario_transcript.txt").write_text("\n".join(transcript), encoding="utf-8")
    print(f"\nWrote transcript -> {LOGS / 'scenario_transcript.txt'}")


if __name__ == "__main__":
    main()
