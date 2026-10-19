"""
Permission-tier system for LedgerPilot.

Every tool declares the minimum permission tier it needs. The agent runs at a
configured tier; anything above READ that would change state or move money is
gated behind an explicit human-confirmation step. This is the core of the
"Security & compliance" design and maps directly to the Security
Self-Assessment deliverable.

Tiers
-----
T0_READ      : read-only analysis. No side effects. Always allowed.
T1_RECOMMEND : may produce recommendations / drafts. No side effects.
T2_ACT       : may initiate a state-changing action (e.g. schedule a payment,
               send a reminder). ALWAYS requires explicit user confirmation,
               regardless of configured tier. The agent never self-approves.
"""
from __future__ import annotations
from enum import IntEnum
from dataclasses import dataclass


class Tier(IntEnum):
    T0_READ = 0
    T1_RECOMMEND = 1
    T2_ACT = 2


TIER_LABELS = {
    Tier.T0_READ: "Read-only analysis",
    Tier.T1_RECOMMEND: "Recommendation / drafting",
    Tier.T2_ACT: "State-changing action (confirmation required)",
}


class PermissionError_(Exception):
    """Raised when a tool is invoked above the agent's configured tier."""


class ConfirmationRequired(Exception):
    """Raised when a T2_ACT tool is called without an explicit confirmation token."""
    def __init__(self, action_summary: str):
        self.action_summary = action_summary
        super().__init__(action_summary)


@dataclass
class PermissionContext:
    """Holds the agent's configured ceiling and whether the user pre-authorised
    a specific pending action in this turn."""
    max_tier: Tier = Tier.T1_RECOMMEND
    confirmed_action: str | None = None  # set when user explicitly confirms

    def check(self, required: Tier, action_summary: str = "") -> None:
        if required > self.max_tier:
            raise PermissionError_(
                f"Tool requires {TIER_LABELS[required]} but agent ceiling is "
                f"{TIER_LABELS[self.max_tier]}."
            )
        if required == Tier.T2_ACT:
            # Act-tier ALWAYS needs an explicit matching confirmation.
            if self.confirmed_action != action_summary:
                raise ConfirmationRequired(action_summary)
