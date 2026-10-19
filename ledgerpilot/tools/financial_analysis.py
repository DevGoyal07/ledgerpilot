"""
financial_analysis — computes core SME financial-health metrics and a simple
0-100 health score with plain-language explanation.

Permission: T0_READ.
"""
from __future__ import annotations
from collections import defaultdict
from statistics import mean

from ..agent import datastore
from ..agent.permissions import Tier

REQUIRED_TIER = Tier.T0_READ
NAME = "financial_analysis"
SCHEMA = {
    "name": NAME,
    "description": "Compute an SME's key financial metrics (net margin, expense "
                   "ratio, debt load, revenue trend, top cost drivers) and an "
                   "explainable 0-100 financial-health score.",
    "parameters": {
        "type": "object",
        "properties": {
            "business_id": {"type": "string", "description": "e.g. SME001"}
        },
        "required": ["business_id"],
    },
}


def _month(d):
    return d[:7]


def run(business_id: str, perms=None) -> dict:
    if perms:
        perms.check(REQUIRED_TIER)
    biz = datastore.get_business(business_id)
    txns = datastore.get_transactions(business_id)

    monthly = defaultdict(lambda: {"credit": 0.0, "debit": 0.0})
    cat_debit = defaultdict(float)
    for t in txns:
        monthly[_month(t["date"])][t["type"]] += t["amount"]
        if t["type"] == "debit":
            cat_debit[t["category"]] += t["amount"]

    months = sorted(monthly)
    inflows = [monthly[m]["credit"] for m in months]
    outflows = [monthly[m]["debit"] for m in months]
    avg_in = mean(inflows) if inflows else 0
    avg_out = mean(outflows) if outflows else 0

    net_margin = (avg_in - avg_out) / avg_in * 100 if avg_in else 0
    expense_ratio = avg_out / avg_in * 100 if avg_in else 0
    debt_to_rev = biz["outstanding_debt"] / (avg_in * 12) if avg_in else 0

    # revenue trend: first-half vs second-half average
    half = len(inflows) // 2 or 1
    trend = (mean(inflows[half:]) - mean(inflows[:half])) / (mean(inflows[:half]) or 1) * 100

    # top cost drivers
    total_debit = sum(cat_debit.values()) or 1
    top = sorted(cat_debit.items(), key=lambda kv: kv[1], reverse=True)[:3]
    top_drivers = [{"category": k, "share_pct": round(v / total_debit * 100, 1)} for k, v in top]

    # --- explainable health score (weighted components, each 0-100) ---
    comp = {}
    comp["margin"] = max(0, min(100, net_margin * 4))           # 25% margin -> 100
    comp["liquidity"] = max(0, min(100, biz["cash_on_hand"] / (avg_out or 1) * 50))  # 2 months -> 100
    comp["leverage"] = max(0, min(100, 100 - debt_to_rev * 100))  # 0 debt -> 100
    comp["growth"] = max(0, min(100, 50 + trend * 2.5))          # flat -> 50
    weights = {"margin": 0.30, "liquidity": 0.25, "leverage": 0.25, "growth": 0.20}
    score = round(sum(comp[k] * weights[k] for k in weights), 1)

    if score >= 75:
        band = "Strong"
    elif score >= 55:
        band = "Stable"
    elif score >= 40:
        band = "Watch"
    else:
        band = "At risk"

    return {
        "business": biz["name"],
        "currency": biz["currency"],
        "avg_monthly_revenue": round(avg_in, 2),
        "avg_monthly_expense": round(avg_out, 2),
        "net_margin_pct": round(net_margin, 1),
        "expense_ratio_pct": round(expense_ratio, 1),
        "debt_to_annual_revenue": round(debt_to_rev, 2),
        "revenue_trend_pct": round(trend, 1),
        "top_cost_drivers": top_drivers,
        "health_score": score,
        "health_band": band,
        "score_components": {k: round(v, 1) for k, v in comp.items()},
        "score_weights": weights,
    }
