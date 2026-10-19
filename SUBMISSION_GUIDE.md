# LedgerPilot — Submission Guide

Everything for the 2026 FinTechathon (WeBank · International Track, **Topic E**)
is in this folder. This guide maps each required deliverable to its file and
lists exactly what **you** still need to do.

> ⏰ **Deadline: 20 October 2026, 23:59 Beijing Time (UTC+8)** — that's
> **21:29 IST on 20 Oct**. Registration shares this deadline. Submit with buffer.

---

## The six required deliverables → where they are

| # | Required | File / location | Status |
|---|----------|-----------------|--------|
| 1 | **Technical documentation** (architecture, algorithms, security design) | `docs/Technical_Documentation.pdf` | ✅ Ready |
| 2 | **Presentation deck** (≤10 min) | `docs/LedgerPilot_Deck.pptx` (+ `.pdf`) | ✅ Ready — 12 slides with speaker notes |
| 3 | **Demo video** (≤5 min, optional) | Record using `docs/Demo_Video_Script.md` | ⬜ You record (script ready) |
| 4 | **Source code** (README, GitHub link, deploy, tests) | whole repo + `README.md` | ✅ Ready — needs your GitHub push |
| 5 | **Security self-assessment** (permission tiers + known-risk list) | `docs/Security_Self_Assessment.pdf` | ✅ Ready |
| 6 | **Execution evidence** (sandbox logs + demo) | `logs/sample/` | ✅ Ready — reproducible via `run_scenario.py` |

---

## What you still need to do (the human-only parts)

### 1. Register the team (if not done) — do this FIRST
Registration closes at the same moment as submission. Confirm your team meets
the rules: **2–5 full-time students**, at institutions **outside** Mainland
China / Hong Kong / Macao / Chinese Taipei, with **at least 60% non-Chinese
nationals**. (This is the one eligibility catch — check it before anything else.)

### 2. Push the code to GitHub
```bash
cd ledgerpilot
git init
git add .
git commit -m "LedgerPilot — FinTechathon 2026 Topic E submission"
git branch -M main
git remote add origin https://github.com/<your-org>/ledgerpilot.git
git push -u origin main
```
Then put the repo URL into your technical documentation / submission form.
(Make the repo **public**, or share access with the organizers.)

### 3. Verify it runs on a clean machine (2 minutes)
```bash
pip install -r requirements.txt
python ledgerpilot/data/generate_data.py
python -m ledgerpilot.ui.app          # open http://127.0.0.1:5000
python run_scenario.py                # regenerates logs/
pytest -q                             # 12 tests pass
```

### 4. Record the demo video
Follow `docs/Demo_Video_Script.md`. ~4 minutes. Optional but recommended.

### 5. Final presentation polish (optional)
Open `docs/LedgerPilot_Deck.pptx`, add your **team name + member names** on the
title slide, and rehearse once against the speaker notes (they're timed to ~10 min).

### 6. Submit
Upload all six items (or the repo link + docs) through the official portal at
`fintechathon.g-ican.com` before the deadline. Latest version received wins, so
you can submit early and update.

---

## 30-second pitch (for the form's summary box, if asked)

> LedgerPilot is an AI finance copilot for small-business owners. It proactively
> manages cash flow and raises early alerts, matches the business to the right
> financing with explainable reasons, and analyses financial health into one
> transparent score. It is an agent, not a chatbot — it plans and executes tool
> calls — but every state-changing action is gated behind explicit human
> confirmation and a full audit trail, with all figures computed by deterministic
> tools rather than the language model.

---

## Project structure

```
ledgerpilot/
├─ README.md                  ← main source-code readme (deliverable 4)
├─ SUBMISSION_GUIDE.md         ← this file
├─ requirements.txt  .env.example  LICENSE  .gitignore
├─ run_scenario.py            ← regenerates execution evidence
├─ ledgerpilot/
│  ├─ agent/   core.py  llm.py  permissions.py  datastore.py
│  ├─ tools/   analyze_cashflow.py  financial_analysis.py
│  │           match_financing.py   schedule_action.py
│  ├─ ui/      app.py  templates/index.html
│  └─ data/    businesses.json  financing_products.json  generate_data.py
├─ tests/      test_ledgerpilot.py          ← 12 tests
├─ logs/sample/   audit_log.jsonl  actions_ledger.jsonl  scenario_transcript.txt
└─ docs/
   ├─ Technical_Documentation.pdf           ← deliverable 1
   ├─ Security_Self_Assessment.pdf          ← deliverable 5
   ├─ LedgerPilot_Deck.pptx / .pdf          ← deliverable 2
   └─ Demo_Video_Script.md                  ← for deliverable 3
```

Good luck. 🚀
