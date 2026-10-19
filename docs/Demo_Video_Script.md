# LedgerPilot — Demo Video Script (≤5 minutes)

The demo video is **optional** per the rules, but it is cheap insurance: if the
live tool stutters during the judges' review, the video still shows it working.
Target **3.5–4.5 minutes**. Record a screen capture of the running web app
(OBS, Loom, or QuickTime). Narration below is a guide — speak naturally.

**Before recording**
1. Start the app: `python -m ledgerpilot.ui.app` → open `http://127.0.0.1:5000`
2. (Optional, for the "api engine" badge) set `LEDGERPILOT_API_KEY` in `.env` first.
3. Have the three businesses ready in the dropdown: PixelForge (strong),
   ThreadCraft (cash-crunch), Brew & Bloom (cafe).

---

### Shot 1 — Hook & product (0:00–0:35)
**On screen:** the app's home view, ThreadCraft selected, snapshot panel visible.
**Say:** "This is LedgerPilot — an AI finance copilot for small businesses. On
the left, a live snapshot of the business: a health score, cash position, and
proactive alerts. On the right, you just talk to it. Notice the header — it runs
in guarded-autonomy mode: it can act, but only with your confirmation."

### Shot 2 — Financial analysis (0:35–1:15)
**Do:** Switch the dropdown to **PixelForge Studios**. Click the chip
**"How is my business doing?"**
**Say:** "Let's ask how the business is doing. LedgerPilot runs its analysis
tool and comes back with an explainable health score — 89, Strong — broken into
margin, liquidity, leverage, and growth. Every number is backed by the data, not
guessed by a language model."

### Shot 3 — Cash-flow alerts (1:15–2:10)
**Do:** Switch to **ThreadCraft Apparel**. Click **"Will I run short of cash?"**
**Say:** "Now a business that's profitable on paper but cash-starved by long
client payment terms. Watch what the copilot does unprompted — it flags a thin
cash buffer and overdue invoices, and tells the owner that collecting those
receivables is the fastest cash win. This is the agent being proactive, not just
answering."

### Shot 4 — Financing match (2:10–3:05)
**Do:** Type: *"I need 15 lakh to bridge a cash gap. What financing suits me?"*
**Say:** "Let's ask for financing. It ranks what actually fits — invoice
financing first, because of those receivables — each with a fit score, an APR
range, estimated cost, and the reasons it fits. And it ends every time with
'explainable suggestions, not a credit offer.' Transparency is built in."

### Shot 5 — The security moment (3:05–4:00)  ← the one judges remember
**Do:** Type: *"Set an alert to chase the overdue invoices next Monday."*
**Say:** "Here's the part we're proudest of. I asked it to take an action.
Instead of just doing it, it stops and asks for confirmation — because this
changes state. The agent never self-approves."
**Do:** Type: *"Yes, go ahead."*
**Say:** "Now, with my explicit yes, it executes and logs the action. Every
decision — the plan, the tool calls, the confirmation, the result — is written
to an audit trail. That's the security design that earns the compliance score."

### Shot 6 — Close (4:00–4:30)
**On screen:** back to the snapshot, or the terminal showing `pytest` passing /
`logs/audit_log.jsonl`.
**Say:** "Everything you saw runs today — with a deterministic offline engine
that needs no API key, twelve passing tests, and a full execution-evidence log.
LedgerPilot: the finance teammate every small business deserves. Thank you."

---

**Recording tips**
- 1080p, 30fps is plenty. Keep the cursor movements slow and deliberate.
- If an answer is long, let it finish rendering before narrating the next line.
- Keep it under 5:00 — the rules cap it there. Trim Shot 2 or 6 if tight.
