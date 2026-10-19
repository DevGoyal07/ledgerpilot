"""
analyze_cashflow — reconstructs monthly cash flow, projects the next 30 days,
and raises proactive alerts (shortfall risk, expense spikes, overdue invoices).

Permission: T0_READ (pure analysis, no side effects).
"""
from __future__ import annotations
from collections import defaultdict
from datetime import date, datetime, timedelta
from statistics import mean, pstdev

from ..agent import datastore
from ..agent.permissions import Tier

REQUIRED_TIER = Tier.T0_READ
TODAY = date(2026, 10, 20)

NAME = "analyze_cashflow"
SCHEMA = {
    "name": NAME,
    "description": "Analyse an SME's cash flow: monthly net position, 30-day "
                   "runway projection, and proactive alerts (shortfall risk, "
                   "unusual expense spikes, overdue receivables).",
    "parameters": {
        "type": "object",
        "properties": {
            "business_id": {"type": "string", "description": "e.g. SME001"}
        },
        "required": ["business_id"],
    },
}


def _month(d: str) -> str:
    return d[:7]


def run(business_id: str, perms=None) -> dict:
    if perms:
        perms.check(REQUIRED_TIER)
    biz = datastore.get_business(business_id)
    txns = datastore.get_transactions(business_id)
    invoices = datastore.get_invoices(business_id)

    monthly = defaultdict(lambda: {"credit": 0.0, "debit": 0.0})
    cat_debit = defaultdict(list)
    for t in txns:
        monthly[_month(t["date"])][t["type"]] += t["amount"]
        if t["type"] == "debit":
            cat_debit[t["category"]].append(t["amount"])

    months = sorted(monthly)
    series = []
    for m in months:
        c, d = monthly[m]["credit"], monthly[m]["debit"]
        series.append({"month": m, "inflow": round(c, 2),
                       "outflow": round(d, 2), "net": round(c - d, 2)})

    nets = [s["net"] for s in series]
    avg_net = mean(nets) if nets else 0
    avg_outflow = mean(s["outflow"] for s in series) if series else 0
    cash = biz["cash_on_hand"]

    # Runway: months of cash left if net stays negative
    runway_months = None
    if avg_net < 0:
        runway_months = round(cash / abs(avg_net), 1)

    # 30-day projection
    due_in_30 = sum(i["amount"] for i in invoices
                    if i["status"] in ("open", "overdue") and i["days_to_due"] <= 30)
    projected_close = cash + avg_net + due_in_30 * 0.5  # assume half of near receivables land

    alerts = []
    # 1) Shortfall risk
    if avg_net < 0 and runway_months is not None and runway_months < 6:
        alerts.append({
            "severity": "high" if runway_months < 3 else "medium",
            "type": "shortfall_risk",
            "message": f"Average monthly net cash flow is negative "
                       f"({avg_net:,.0f} {biz['currency']}). At this burn, cash on "
                       f"hand covers ~{runway_months} months.",
        })
    if cash < avg_outflow * 0.5:
        alerts.append({
            "severity": "high",
            "type": "thin_buffer",
            "message": f"Cash on hand ({cash:,.0f}) is under half of average "
                       f"monthly outflow ({avg_outflow:,.0f}). Low buffer against a bad month.",
        })
    # 2) Expense spikes (category last month vs its own history)
    last_m = months[-1] if months else None
    if last_m:
        last_cat = defaultdict(float)
        for t in txns:
            if _month(t["date"]) == last_m and t["type"] == "debit":
                last_cat[t["category"]] += t["amount"]
        for cat, amts in cat_debit.items():
            if len(amts) >= 3:
                base = mean(amts)
                sd = pstdev(amts) or 1
                cur = last_cat.get(cat, 0)
                if cur > base + 2 * sd and cur > base * 1.3:
                    alerts.append({
                        "severity": "medium",
                        "type": "expense_spike",
                        "message": f"'{cat}' last month ({cur:,.0f}) ran well above "
                                   f"its usual (~{base:,.0f}). Worth a look.",
                    })
    # 3) Overdue receivables
    overdue = [i for i in invoices if i["status"] == "overdue"]
    if overdue:
        tot = sum(i["amount"] for i in overdue)
        alerts.append({
            "severity": "medium",
            "type": "overdue_receivable",
            "message": f"{len(overdue)} overdue invoice(s) worth {tot:,.0f} "
                       f"{biz['currency']}. Collecting these is the fastest cash win.",
        })

    return {
        "business": biz["name"],
        "currency": biz["currency"],
        "monthly_series": series,
        "avg_monthly_net": round(avg_net, 2),
        "cash_on_hand": cash,
        "runway_months_if_negative": runway_months,
        "receivables_due_30d": round(due_in_30, 2),
        "projected_cash_30d": round(projected_close, 2),
        "alerts": alerts,
    }
