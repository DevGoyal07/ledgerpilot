"""Tool registry — maps tool names to their run() + schema + required tier."""
from . import analyze_cashflow, financial_analysis, match_financing, schedule_action

REGISTRY = {
    analyze_cashflow.NAME: analyze_cashflow,
    financial_analysis.NAME: financial_analysis,
    match_financing.NAME: match_financing,
    schedule_action.NAME: schedule_action,
}

SCHEMAS = [m.SCHEMA for m in REGISTRY.values()]


def get(name):
    return REGISTRY.get(name)
