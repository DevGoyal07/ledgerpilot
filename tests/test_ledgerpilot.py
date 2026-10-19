"""
Test suite for LedgerPilot. Covers the three analytical tools, the financing
matcher's eligibility logic, and — most importantly — the permission-tier
gating that underpins the security design.

Run:  pytest -q
"""
import json
from pathlib import Path

import pytest

from ledgerpilot.agent import datastore
from ledgerpilot.agent.core import Agent, AuditLogger
from ledgerpilot.agent.permissions import (
    PermissionContext, Tier, ConfirmationRequired, PermissionError_)
from ledgerpilot.tools import analyze_cashflow, financial_analysis, match_financing, schedule_action


@pytest.fixture(scope="session", autouse=True)
def _data():
    datastore.ensure_data()


# ---------- data integrity ----------
def test_all_businesses_have_data():
    for b in datastore.list_businesses():
        assert datastore.get_transactions(b["id"]), f"no txns for {b['id']}"


# ---------- analytical tools ----------
def test_cashflow_returns_series_and_alerts():
    r = analyze_cashflow.run("SME002")
    assert len(r["monthly_series"]) == 6
    assert isinstance(r["alerts"], list)
    # ThreadCraft is the cash-crunch case -> should raise at least one alert
    assert r["alerts"], "expected cash-flow alerts for the tight business"


def test_financial_analysis_score_bounds():
    for b in ("SME001", "SME002", "SME003"):
        r = financial_analysis.run(b)
        assert 0 <= r["health_score"] <= 100
        assert r["health_band"] in {"Strong", "Stable", "Watch", "At risk"}
    # debt-free strong agency should outscore the indebted tight manufacturer
    assert financial_analysis.run("SME003")["health_score"] > \
           financial_analysis.run("SME002")["health_score"]


def test_financing_match_ranks_and_explains():
    r = match_financing.run("SME002", amount_needed=1500000, purpose="bridge a cash gap")
    assert r["recommended"], "expected at least one recommendation"
    top = r["recommended"][0]
    # invoice financing should top the list for a receivables-heavy cash gap
    assert "Invoice Financing" in top["product"]
    assert top["why_it_fits"], "every recommendation must carry reasons (explainability)"


def test_financing_reports_ineligibility_with_reasons():
    # Cafe has Good credit; overdraft needs Good -> eligible. Force an ineligible
    # case: huge amount beyond any product cap.
    r = match_financing.run("SME001", amount_needed=99000000)
    assert r["not_yet_eligible"], "expected some products to be out of range"
    assert all("reasons" in x for x in r["not_yet_eligible"])


# ---------- permission system ----------
def test_read_tool_always_allowed():
    perms = PermissionContext(max_tier=Tier.T0_READ)
    perms.check(Tier.T0_READ)  # no raise


def test_recommend_blocked_under_read_ceiling():
    perms = PermissionContext(max_tier=Tier.T0_READ)
    with pytest.raises(PermissionError_):
        perms.check(Tier.T1_RECOMMEND)


def test_action_requires_confirmation():
    perms = PermissionContext(max_tier=Tier.T2_ACT)
    with pytest.raises(ConfirmationRequired):
        perms.check(Tier.T2_ACT, action_summary="do X")


def test_action_runs_after_matching_confirmation():
    perms = PermissionContext(max_tier=Tier.T2_ACT, confirmed_action="do X")
    perms.check(Tier.T2_ACT, action_summary="do X")  # no raise


def test_action_ceiling_enforced_even_with_confirmation():
    perms = PermissionContext(max_tier=Tier.T0_READ, confirmed_action="do X")
    with pytest.raises(PermissionError_):
        perms.check(Tier.T2_ACT, action_summary="do X")


# ---------- agent integration ----------
def test_agent_gates_then_executes_action(tmp_path):
    log = AuditLogger(tmp_path / "audit.jsonl")
    agent = Agent(max_tier=Tier.T2_ACT, logger=log)
    agent.set_business("SME002")
    r1 = agent.handle("set an alert to chase overdue invoices")
    assert r1["pending_confirmation"], "action must be gated first"
    r2 = agent.handle("yes go ahead")
    assert "scheduled" in r2["reply"].lower() or "done" in r2["reply"].lower()


def test_agent_logs_every_turn(tmp_path):
    log = AuditLogger(tmp_path / "audit.jsonl")
    agent = Agent(max_tier=Tier.T2_ACT, logger=log)
    agent.set_business("SME001")
    agent.handle("how is my business doing?")
    events = [json.loads(l)["event"] for l in (tmp_path / "audit.jsonl").read_text().splitlines()]
    assert "user_message" in events and "tool_call" in events and "assistant_reply" in events
