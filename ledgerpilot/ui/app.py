"""
LedgerPilot web UI — a lightweight Flask chat interface over the agent.

Run:  python -m ledgerpilot.ui.app
Then open http://127.0.0.1:5000
"""
from __future__ import annotations
import os
from flask import Flask, request, jsonify, render_template, session

from ..agent.core import Agent
from ..agent.permissions import Tier
from ..agent import datastore, llm

app = Flask(__name__)
app.secret_key = os.environ.get("LEDGERPILOT_SECRET", "ledgerpilot-dev-secret")

# One agent per process is fine for the demo; business selection is per-request.
_AGENT = Agent(max_tier=Tier.T2_ACT)


@app.route("/")
def index():
    return render_template("index.html",
                           businesses=datastore.list_businesses(),
                           backend=llm.backend_name())


@app.route("/api/businesses")
def businesses():
    return jsonify(datastore.list_businesses())


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    biz = data.get("business_id", "SME001")
    msg = data.get("message", "").strip()
    # restore any pending confirmation from the session
    _AGENT.context["pending_action"] = session.get("pending_action")
    _AGENT.set_business(biz)
    if not msg:
        return jsonify({"reply": "Ask me about cash flow, financial health, or financing."})
    result = _AGENT.handle(msg)
    session["pending_action"] = _AGENT.context.get("pending_action")
    return jsonify({
        "reply": result["reply"],
        "backend": result["backend"],
        "pending_confirmation": bool(result["pending_confirmation"]),
    })


@app.route("/api/summary/<biz_id>")
def summary(biz_id):
    from ..tools import financial_analysis, analyze_cashflow
    return jsonify({
        "health": financial_analysis.run(biz_id),
        "cashflow": analyze_cashflow.run(biz_id),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=False)
