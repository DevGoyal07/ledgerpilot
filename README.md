# LedgerPilot — an AI Finance Copilot for Small-Business Owners

**2026 FinTechathon · WeBank FinTech College Students Challenge — International Track**
**Topic E: SME Finance Copilot**

LedgerPilot is an AI agent that acts as a finance copilot for small-business
owners. It does three jobs an owner would otherwise pay an accountant or
analyst for, and it does them proactively:

1. **Cash-flow management with alerts** — reconstructs monthly cash flow,
   projects the next 30 days, and raises early warnings (shortfall risk, thin
   buffer, expense spikes, overdue receivables).
2. **Financing-option matching** — matches the business to suitable financing
   products with an *explainable* fit score, estimated cost, and the specific
   reasons behind every recommendation — plus why it is *not* yet eligible for
   others.
3. **Business financial analysis** — computes core metrics (margin, expense
   ratio, leverage, revenue trend, top cost drivers) and an explainable
   0–100 financial-health score.

It is an **agent**, not a chatbot: it plans which tools to call, runs them, and
can take real actions (e.g. scheduling a reminder) — but every state-changing
action is gated behind explicit human confirmation and a permission-tier system.

---

## Why this design wins on the scoring rubric

| Criterion | Weight | How LedgerPilot addresses it |
|---|---|---|
| **Task completion** | 40% | All three required capabilities implemented with real financial logic and verified end-to-end against sandbox data. |
| **Security & compliance** | 30% | 3-tier permission model; actions always require confirmation; full audit log of every decision; explainable, non-advisory recommendations with disclaimers; documented known-risk list. |
| **Innovation & interaction** | 30% | Live "state-of-the-business" snapshot panel, proactive alerting (the agent speaks up unprompted), purpose-aware financing matcher, and a pluggable LLM backend that runs fully offline for reproducible evidence. |

---

## Quick start (offline mode — no API key needed)

```bash
# 1. clone, then from the repo root:
python -m pip install -r requirements.txt     # flask (openai/pytest optional)

# 2. generate the deterministic sandbox data
python ledgerpilot/data/generate_data.py

# 3a. run the web app
python -m ledgerpilot.ui.app
#     open http://127.0.0.1:5000

# 3b. OR produce the execution-evidence logs from the CLI
python run_scenario.py
```

Offline mode uses a deterministic intent router + templating layer, so the
whole agent loop runs with **no network and no key**. This is how the
reproducible execution evidence in `logs/sample/` is produced.

## Live LLM mode (for the demo)

Copy `.env.example` to `.env`, set a key, and the agent switches to a real
LLM backend with tool-calling automatically:

```bash
cp .env.example .env
# edit .env: set LEDGERPILOT_API_KEY (any OpenAI-compatible provider)
export $(grep -v '^#' .env | xargs)
python -m ledgerpilot.ui.app
```

The header chip shows which engine is active (`offline engine` / `api engine`).
Nothing else changes — same tools, same permission gating, same audit trail.

---

## Architecture

```
          ┌──────────────────────────────────────────────┐
  user →  │                  Agent core                   │
          │  plan → permission gate → execute → narrate    │
          └───────┬───────────────┬───────────────┬───────┘
                  │               │               │
            ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼──────┐
            │    LLM     │   │  Tools    │   │  Audit log │
            │  adapter   │   │ registry  │   │  (JSONL)   │
            │ api│offline │   └─────┬─────┘   └────────────┘
            └───────────┘         │
                         ┌────────┼─────────┬──────────────┐
                   analyze_   financial_  match_      schedule_
                   cashflow   analysis    financing   action (T2)
                     (T0)       (T0)        (T1)      confirm-gated
                                  │
                           ┌──────▼──────┐
                           │  Datastore   │  (read-only sandbox:
                           │  businesses, │   3 SMEs, 6 mo. txns,
                           │  txns, inv., │   invoices, products)
                           │  products    │
                           └─────────────┘
```

- **`ledgerpilot/agent/core.py`** — the agent loop and `AuditLogger`.
- **`ledgerpilot/agent/llm.py`** — dual backend (API / deterministic offline).
- **`ledgerpilot/agent/permissions.py`** — the 3-tier permission model.
- **`ledgerpilot/agent/datastore.py`** — read-only sandbox data access.
- **`ledgerpilot/tools/`** — the four tools, each declaring its required tier.
- **`ledgerpilot/ui/`** — Flask app + single-page chat interface.
- **`ledgerpilot/data/`** — business profiles, financing catalog, data generator.

Full detail is in `docs/Technical_Documentation.pdf` and
`docs/Security_Self_Assessment.pdf`.

---

## Permission tiers (the security backbone)

| Tier | Name | Side effects | Example tools | Rule |
|------|------|--------------|---------------|------|
| T0 | Read-only analysis | none | `analyze_cashflow`, `financial_analysis` | always allowed |
| T1 | Recommend / draft | none | `match_financing` | allowed up to ceiling |
| T2 | State-changing action | yes | `schedule_action` | **always needs explicit user confirmation**, even if the ceiling allows it |

The live agent runs at a **T2 ceiling with confirmation-always** ("guarded
autonomy"). A separate read-only configuration (T0 ceiling) demonstrates full
lock-down. See `run_scenario.py` for all three cases demonstrated live.

---

## Tests

```bash
pytest -q
# if your environment doesn't pick up the package, use:  python -m pytest -q
```

12 tests cover data integrity, the three analytical tools, the financing
matcher's ranking + ineligibility reporting, and every branch of the
permission system (read allowed, recommend blocked under read ceiling, action
needs confirmation, action runs after matching confirmation, ceiling enforced
even with confirmation, and the agent's gate-then-execute integration path).

---

## Execution evidence

`logs/sample/` contains a committed run:

- **`audit_log.jsonl`** — every event: user messages, plans, tool calls with
  their required tier, results, confirmation prompts, permission denials.
- **`actions_ledger.jsonl`** — the state-changing actions that were authorised.
- **`scenario_transcript.txt`** — the human-readable session.

Re-generate any time with `python run_scenario.py` (deterministic).

> **All data is simulated.** No real bank account, customer, or money is
> touched anywhere in this project.

---

## Deliverables map (submission checklist → this repo)

| # | Required deliverable | Where |
|---|---|---|
| 1 | Technical documentation | `docs/Technical_Documentation.pdf` |
| 2 | Presentation deck (≤10 min) | `docs/LedgerPilot_Deck.pptx` |
| 3 | Demo video (≤5 min, optional) | `docs/Demo_Video_Script.md` (record from the running app) |
| 4 | Source code + README + deploy + tests | this repo |
| 5 | Security self-assessment | `docs/Security_Self_Assessment.pdf` |
| 6 | Execution evidence | `logs/sample/` |

## License

MIT — see `LICENSE`. Third-party components (Flask, optional OpenAI SDK) retain
their own licenses.
