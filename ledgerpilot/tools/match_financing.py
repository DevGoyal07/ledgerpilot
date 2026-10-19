"""
match_financing — matches an SME to suitable financing products with an
explainable, rule-based eligibility + fit score. Every recommendation carries
the reasons behind it (explainability = compliance requirement).

Permission: T1_RECOMMEND.
"""
from __future__ import annotations
from collections import defaultdict
from statistics import mean

from ..agent import datastore
from ..agent.permissions import Tier

REQUIRED_TIER = Tier.T1_RECOMMEND
NAME = "match_financing"

BAND_RANK = {
    "Poor (below 650)": 0,
    "Fair (650-699)": 1,
    "Good (720-759)": 2,
    "Excellent (760+)": 3,
}

SCHEMA = {
    "name": NAME,
    "description": "Match an SME to suitable financing products. Returns ranked, "
                   "eligible options each with an explainable fit score, the "
                   "reasons it fits, and estimated cost. Also lists products the "
                   "business does NOT yet qualify for and why.",
    "parameters": {
        "type": "object",
        "properties": {
            "business_id": {"type": "string", "description": "e.g. SME001"},
            "amount_needed": {"type": "number",
                              "description": "Optional funding amount sought."},
            "purpose": {"type": "string",
                        "description": "Optional purpose, e.g. 'expansion', "
                                       "'bridge a cash gap', 'hire ahead of demand'."},
        },
        "required": ["business_id"],
    },
}


def _band_ok(biz_band, min_band):
    return BAND_RANK.get(biz_band, 0) >= BAND_RANK.get(min_band, 0)


def run(business_id: str, amount_needed: float | None = None,
        purpose: str | None = None, perms=None) -> dict:
    if perms:
        perms.check(REQUIRED_TIER)
    biz = datastore.get_business(business_id)
    txns = datastore.get_transactions(business_id)
    invoices = datastore.get_invoices(business_id)
    products = datastore.get_financing_products()

    # derived signals
    monthly = defaultdict(lambda: {"credit": 0.0, "debit": 0.0})
    for t in txns:
        monthly[t["date"][:7]][t["type"]] += t["amount"]
    nets = [v["credit"] - v["debit"] for v in monthly.values()]
    avg_net = mean(nets) if nets else 0
    age = biz["bank_account_age_months"]
    open_recv = sum(i["amount"] for i in invoices if i["status"] in ("open", "overdue"))
    margin = (biz["monthly_revenue_avg"] - biz["monthly_expense_avg"]) / \
             (biz["monthly_revenue_avg"] or 1)
    purpose_l = (purpose or "").lower()

    eligible, ineligible = [], []
    for p in products:
        reasons, fails = [], []
        # hard eligibility
        if not _band_ok(biz["credit_score_band"], p["min_credit_band"]):
            fails.append(f"credit band {biz['credit_score_band']} below required "
                         f"{p['min_credit_band']}")
        if age < p["min_business_age_months"]:
            fails.append(f"business age {age}m below required "
                         f"{p['min_business_age_months']}m")
        if amount_needed and amount_needed > p["max_amount"]:
            fails.append(f"amount {amount_needed:,.0f} exceeds product cap "
                         f"{p['max_amount']:,.0f}")

        if fails:
            ineligible.append({"product": p["name"], "reasons": fails})
            continue

        # --- fit score (0-100) with explicit reasons ---
        fit = 50
        t = p["type"]
        if t == "invoice_financing":
            if open_recv > biz["monthly_revenue_avg"] * 0.4:
                fit += 30; reasons.append(f"large open receivables ({open_recv:,.0f}) "
                                          f"suit invoice financing")
            else:
                fit -= 10
        if t == "credit_line" and avg_net < biz["monthly_expense_avg"] * 0.1:
            fit += 20; reasons.append("recurring tight months fit a revolving line")
        if t == "revenue_based":
            if margin > 0.25:
                fit += 25; reasons.append(f"healthy margin ({margin*100:.0f}%) suits "
                                          f"revenue-share repayment")
            else:
                fit -= 15; reasons.append("thin margin makes revenue-share costly")
        if t == "scheme_loan" and biz["gst_registered"]:
            fit += 20; reasons.append("GST-registered MSME — eligible for low-cost "
                                      "govt-backed credit")
        if t == "term_loan" and avg_net > 0:
            fit += 15; reasons.append("positive average net cash flow supports fixed EMIs")
        if t == "mca":
            fit -= 20; reasons.append("high effective cost — treat as last resort")

        # purpose nudges
        if "expan" in purpose_l and t in ("term_loan", "scheme_loan"):
            fit += 8; reasons.append("good structural fit for expansion")
        if ("gap" in purpose_l or "bridge" in purpose_l) and t in ("invoice_financing", "credit_line"):
            fit += 10; reasons.append("designed for short-term cash-gap bridging")
        if "hire" in purpose_l and t in ("revenue_based", "credit_line"):
            fit += 6; reasons.append("flexible capital suits hiring ahead of demand")

        fit = max(0, min(100, fit))
        lo, hi = p["typical_apr_pct"]
        est_amt = amount_needed or min(p["max_amount"], biz["monthly_revenue_avg"])
        est_annual_cost = (lo + hi) / 2 / 100 * est_amt
        eligible.append({
            "product": p["name"],
            "type": p["type"],
            "fit_score": fit,
            "apr_range_pct": p["typical_apr_pct"],
            "est_amount_considered": round(est_amt, 2),
            "est_annual_interest_cost": round(est_annual_cost, 2),
            "why_it_fits": reasons or ["meets basic eligibility"],
            "key_requirement": p["key_requirement"],
        })

    eligible.sort(key=lambda x: x["fit_score"], reverse=True)
    return {
        "business": biz["name"],
        "currency": biz["currency"],
        "amount_needed": amount_needed,
        "purpose": purpose,
        "recommended": eligible[:3],
        "other_eligible": eligible[3:],
        "not_yet_eligible": ineligible,
    }
