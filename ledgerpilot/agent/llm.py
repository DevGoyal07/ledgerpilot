"""
LLM adapter with two interchangeable backends:

1. API backend  — any OpenAI-compatible chat-completions endpoint with tool
   calling. Enabled when LEDGERPILOT_API_KEY is set. Used for the live demo.

2. Offline backend — a deterministic intent router + natural-language
   templating layer that needs no network or key. It performs genuine intent
   detection to decide which tool(s) to call, then verbalises the structured
   tool results. This lets the full agent loop run end-to-end in any sandbox
   and produce real execution logs for the submission.

Both backends speak the same tiny interface:
    plan(user_msg, context) -> list[ToolCall]         # which tools to call
    narrate(user_msg, tool_results, context) -> str   # final NL answer
"""
from __future__ import annotations
import os
import re
import json
from dataclasses import dataclass


@dataclass
class ToolCall:
    name: str
    arguments: dict


def _api_enabled() -> bool:
    return bool(os.environ.get("LEDGERPILOT_API_KEY"))


# ----------------------------------------------------------------------------
# Offline intent router
# ----------------------------------------------------------------------------
_INTENTS = [
    ("analyze_cashflow", r"cash\s*flow|runway|shortfall|burn|liquidity|will i run out|short of cash|cash position"),
    ("financial_analysis", r"how (am|is).*doing|health|margin|profit|financial (health|analysis)|metrics|overview|how are we"),
    ("match_financing", r"loan|financ|funding|borrow|capital|credit line|overdraft|raise money|need money|fund"),
    ("schedule_action", r"remind|set (an )?alert|schedule|follow[- ]?up|notify me"),
]


def _detect_business(text, context):
    # explicit id
    m = re.search(r"\bSME\d{3}\b", text, re.I)
    if m:
        return m.group(0).upper()
    # by name
    for b in context.get("businesses", []):
        if b["name"].lower() in text.lower():
            return b["id"]
    return context.get("current_business")


def _offline_plan(user_msg, context):
    text = user_msg.lower()
    biz = _detect_business(user_msg, context)
    calls = []
    matched = [name for name, pat in _INTENTS if re.search(pat, text)]

    # confirmation of a pending action
    if context.get("pending_action") and re.search(r"\b(yes|confirm|go ahead|do it|approve|ok|okay)\b", text):
        pa = context["pending_action"]
        calls.append(ToolCall("schedule_action", pa["arguments"]))
        return calls

    if not matched:
        # default: a general check-in -> health + cashflow
        matched = ["financial_analysis", "analyze_cashflow"]

    for name in matched:
        args = {"business_id": biz}
        if name == "match_financing":
            m = re.search(r"(?:₹|rs\.?|inr)?\s*([\d,]+)\s*(k|lakh|lakhs|l|cr|crore|million|m)?", text)
            if m:
                num = float(m.group(1).replace(",", ""))
                unit = (m.group(2) or "").lower()
                mult = {"k": 1e3, "lakh": 1e5, "lakhs": 1e5, "l": 1e5,
                        "cr": 1e7, "crore": 1e7, "million": 1e6, "m": 1e6}.get(unit, 1)
                if num * mult >= 10000:
                    args["amount_needed"] = num * mult
            for kw in ("expansion", "expand", "bridge", "gap", "hire", "hiring"):
                if kw in text:
                    args["purpose"] = text
                    break
        if name == "schedule_action":
            atype = "invoice_followup" if ("invoice" in text or "overdue" in text or "chase" in text) \
                else "payment_reminder" if "remind" in text else "cashflow_alert"
            args.update({"action_type": atype,
                         "detail": user_msg.strip(), "trigger_date": None})
        calls.append(ToolCall(name, args))
    return calls


# ----------------------------------------------------------------------------
# Offline narrator — turns structured results into plain language
# ----------------------------------------------------------------------------
def _fmt(n, cur="INR"):
    sym = "₹" if cur == "INR" else ""
    return f"{sym}{n:,.0f}"


def _narrate_cashflow(r):
    cur = r["currency"]
    lines = [f"**Cash flow — {r['business']}**",
             f"Average monthly net: {_fmt(r['avg_monthly_net'], cur)}; "
             f"cash on hand {_fmt(r['cash_on_hand'], cur)}; "
             f"~{_fmt(r['projected_cash_30d'], cur)} projected in 30 days."]
    if r["runway_months_if_negative"]:
        lines.append(f"At the current burn, that's roughly "
                     f"{r['runway_months_if_negative']} months of runway.")
    if r["alerts"]:
        lines.append("\n_Alerts:_")
        for a in r["alerts"]:
            lines.append(f"- **[{a['severity'].upper()}]** {a['message']}")
    else:
        lines.append("No cash-flow alerts — position looks comfortable.")
    return "\n".join(lines)


def _narrate_financial(r):
    cur = r["currency"]
    drivers = ", ".join(f"{d['category']} ({d['share_pct']}%)" for d in r["top_cost_drivers"])
    return "\n".join([
        f"**Financial health — {r['business']}: {r['health_score']}/100 ({r['health_band']})**",
        f"Net margin {r['net_margin_pct']}%, expense ratio {r['expense_ratio_pct']}%, "
        f"debt-to-annual-revenue {r['debt_to_annual_revenue']}.",
        f"Revenue trend over the window: {r['revenue_trend_pct']:+.1f}%.",
        f"Top cost drivers: {drivers}.",
        f"_Score components_ — margin {r['score_components']['margin']}, "
        f"liquidity {r['score_components']['liquidity']}, "
        f"leverage {r['score_components']['leverage']}, "
        f"growth {r['score_components']['growth']} (weighted).",
    ])


def _narrate_financing(r):
    cur = r["currency"]
    out = [f"**Financing options — {r['business']}**"]
    if r["purpose"]:
        out.append(f"_Purpose considered: matching your stated need._")
    for i, p in enumerate(r["recommended"], 1):
        out.append(f"\n{i}. **{p['product']}** — fit {p['fit_score']}/100, "
                   f"APR {p['apr_range_pct'][0]}–{p['apr_range_pct'][1]}%, "
                   f"est. annual interest ~{_fmt(p['est_annual_interest_cost'], cur)}")
        out.append(f"   Why: {'; '.join(p['why_it_fits'])}.")
        out.append(f"   Needs: {p['key_requirement']}.")
    if r["not_yet_eligible"]:
        ne = r["not_yet_eligible"][0]
        out.append(f"\n_Not yet eligible, e.g._ {ne['product']}: {ne['reasons'][0]}.")
    out.append("\n_These are explainable suggestions, not a credit offer. "
               "Final terms depend on the lender's assessment._")
    return "\n".join(out)


def _narrate_action(r):
    if r.get("status") == "scheduled":
        return f"✅ Done — scheduled: {r['confirmation']}"
    return json.dumps(r)


_NARRATORS = {
    "analyze_cashflow": _narrate_cashflow,
    "financial_analysis": _narrate_financial,
    "match_financing": _narrate_financing,
    "schedule_action": _narrate_action,
}


def _offline_narrate(user_msg, tool_results, context):
    parts = []
    for name, result in tool_results:
        fn = _NARRATORS.get(name)
        if fn and isinstance(result, dict) and "error" not in result:
            parts.append(fn(result))
        elif isinstance(result, dict) and result.get("error"):
            parts.append(f"_{name}: {result['error']}_")
    return "\n\n".join(parts) if parts else "I couldn't complete that — could you rephrase?"


# ----------------------------------------------------------------------------
# API backend (used when a key is present)
# ----------------------------------------------------------------------------
def _api_plan(user_msg, context):
    from openai import OpenAI
    from ..tools import SCHEMAS
    client = OpenAI(api_key=os.environ["LEDGERPILOT_API_KEY"],
                    base_url=os.environ.get("LEDGERPILOT_API_BASE",
                                            "https://api.openai.com/v1"))
    model = os.environ.get("LEDGERPILOT_MODEL", "gpt-4o-mini")
    tools = [{"type": "function", "function": s} for s in SCHEMAS]
    sys = ("You are LedgerPilot, a finance copilot for small-business owners. "
           "Use tools to analyse cash flow, financial health and financing "
           "options. Current business context: "
           + json.dumps({k: context.get(k) for k in ("current_business",)}))
    resp = client.chat.completions.create(
        model=model, tools=tools,
        messages=[{"role": "system", "content": sys},
                  {"role": "user", "content": user_msg}])
    msg = resp.choices[0].message
    calls = []
    for tc in (msg.tool_calls or []):
        calls.append(ToolCall(tc.function.name, json.loads(tc.function.arguments)))
    return calls or _offline_plan(user_msg, context)


def _api_narrate(user_msg, tool_results, context):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["LEDGERPILOT_API_KEY"],
                    base_url=os.environ.get("LEDGERPILOT_API_BASE",
                                            "https://api.openai.com/v1"))
    model = os.environ.get("LEDGERPILOT_MODEL", "gpt-4o-mini")
    payload = [{"tool": n, "result": r} for n, r in tool_results]
    sys = ("You are LedgerPilot. Given tool results as JSON, write a concise, "
           "owner-friendly answer. Always note recommendations are not a credit "
           "offer. Never invent numbers beyond the tool results.")
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": sys},
                  {"role": "user", "content": f"Question: {user_msg}\n"
                   f"Tool results: {json.dumps(payload, default=str)}"}])
    return resp.choices[0].message.content


# ----------------------------------------------------------------------------
# Public interface
# ----------------------------------------------------------------------------
def backend_name():
    return "api" if _api_enabled() else "offline"


def plan(user_msg, context):
    return _api_plan(user_msg, context) if _api_enabled() else _offline_plan(user_msg, context)


def narrate(user_msg, tool_results, context):
    return _api_narrate(user_msg, tool_results, context) if _api_enabled() \
        else _offline_narrate(user_msg, tool_results, context)
