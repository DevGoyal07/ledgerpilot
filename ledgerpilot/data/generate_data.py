"""
Deterministic mock-data generator for LedgerPilot's sandbox.

Produces 6 months of transactions and open invoices for each business in
businesses.json. Seeded so every run yields identical data -> reproducible
execution evidence for the competition submission.
"""
import json
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20261020
random.seed(SEED)

HERE = Path(__file__).parent
TODAY = date(2026, 10, 20)
MONTHS = 6

# Category templates per sector keyword -> (label, share_of_expense, volatility)
EXPENSE_MIX = {
    "Food & Beverage": [
        ("Ingredients & Supplies", 0.34, 0.15),
        ("Staff Salaries", 0.30, 0.03),
        ("Rent", 0.16, 0.0),
        ("Utilities", 0.07, 0.20),
        ("Marketing", 0.05, 0.40),
        ("Equipment & Maintenance", 0.04, 0.60),
        ("Misc / Admin", 0.04, 0.30),
    ],
    "Manufacturing": [
        ("Raw Materials", 0.45, 0.18),
        ("Staff Salaries", 0.24, 0.03),
        ("Rent & Factory", 0.10, 0.0),
        ("Utilities & Power", 0.09, 0.22),
        ("Logistics", 0.06, 0.35),
        ("Equipment & Maintenance", 0.03, 0.70),
        ("Misc / Admin", 0.03, 0.30),
    ],
    "Services": [
        ("Staff Salaries", 0.52, 0.03),
        ("Software & Tools", 0.14, 0.10),
        ("Rent / Co-working", 0.12, 0.0),
        ("Contractors", 0.10, 0.50),
        ("Marketing", 0.07, 0.45),
        ("Misc / Admin", 0.05, 0.30),
    ],
}

INCOME_LABELS = {
    "Food & Beverage": ["Dine-in Sales", "Takeaway Sales", "Catering Order"],
    "Manufacturing": ["Client Invoice Payment", "Bulk Order", "Export Order"],
    "Services": ["Retainer Payment", "Project Milestone", "One-off Project"],
}


def sector_key(sector):
    for k in EXPENSE_MIX:
        if k.split()[0] in sector:
            return k
    return "Services"


def month_starts():
    starts = []
    y, m = TODAY.year, TODAY.month
    for _ in range(MONTHS):
        starts.append(date(y, m, 1))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return list(reversed(starts))


def seasonal_factor(biz, d):
    # Cafe dips in monsoon (Jun-Aug)
    if "Food & Beverage" in biz["sector"] and d.month in (6, 7, 8):
        return 0.82
    # Agency ramps toward year-end
    if "Services" in biz["sector"] and d.month in (9, 10, 11):
        return 1.12
    return 1.0


def jitter(base, vol):
    return base * (1 + random.uniform(-vol, vol))


def gen_transactions(biz):
    txns = []
    key = sector_key(biz["sector"])
    tid = 1
    for ms in month_starts():
        sf = seasonal_factor(biz, ms)
        # ---- income: several deposits across the month ----
        month_income = jitter(biz["monthly_revenue_avg"] * sf, 0.08)
        n_income = random.randint(6, 12) if key != "Manufacturing" else random.randint(3, 6)
        labels = INCOME_LABELS[key]
        # distribute month_income across n deposits via random weights that
        # sum to exactly month_income (no leakage)
        weights = [random.uniform(0.6, 1.4) for _ in range(n_income)]
        wsum = sum(weights)
        for i in range(n_income):
            share = month_income * weights[i] / wsum
            day = random.randint(1, 27)
            txns.append({
                "txn_id": f"{biz['id']}-T{tid:04d}",
                "date": str(ms + timedelta(days=day - 1)),
                "type": "credit",
                "category": random.choice(labels),
                "amount": round(share, 2),
            })
            tid += 1
        # ---- expenses ----
        month_expense = jitter(biz["monthly_expense_avg"] * (0.5 + 0.5 * sf), 0.05)
        for label, share, vol in EXPENSE_MIX[key]:
            amt = jitter(month_expense * share, vol)
            # salaries/rent land on fixed days; others scattered
            if label.startswith("Staff"):
                day = 1
            elif "Rent" in label:
                day = 3
            else:
                day = random.randint(2, 27)
            txns.append({
                "txn_id": f"{biz['id']}-T{tid:04d}",
                "date": str(ms + timedelta(days=day - 1)),
                "type": "debit",
                "category": label,
                "amount": round(amt, 2),
            })
            tid += 1
    txns.sort(key=lambda t: t["date"])
    return txns


def gen_invoices(biz):
    """Open receivables — bigger & slower for manufacturing (the cash-crunch story)."""
    invoices = []
    key = sector_key(biz["sector"])
    if key == "Manufacturing":
        specs = [(45, 90, 7), (30, 60, 5), (20, 45, 4), (12, 30, 3)]  # amount%, term days, count-ish
        clients = ["Northline Retail", "Sarathi Garments", "UrbanWeave Pvt Ltd",
                   "Deccan Exports", "Metro Fashion House"]
    elif key == "Services":
        specs = [(40, 30, 3), (35, 15, 2)]
        clients = ["Finzo App", "GreenCart", "Nimbus SaaS", "Rtold Media"]
    else:
        specs = [(100, 15, 1)]
        clients = ["Local Events Co."]
    iid = 1
    base = biz["monthly_revenue_avg"]
    for pct, term, _ in specs:
        amt = round(base * pct / 100 * random.uniform(0.7, 1.1), 2)
        issued = TODAY - timedelta(days=random.randint(5, term + 20))
        due = issued + timedelta(days=term)
        invoices.append({
            "invoice_id": f"{biz['id']}-INV{iid:03d}",
            "client": random.choice(clients),
            "issued_date": str(issued),
            "due_date": str(due),
            "amount": amt,
            "status": "overdue" if due < TODAY else "open",
            "days_to_due": (due - TODAY).days,
        })
        iid += 1
    return invoices


def main():
    businesses = json.loads((HERE / "businesses.json").read_text())["businesses"]
    all_txns, all_invoices = {}, {}
    for biz in businesses:
        all_txns[biz["id"]] = gen_transactions(biz)
        all_invoices[biz["id"]] = gen_invoices(biz)
    (HERE / "transactions.json").write_text(json.dumps(all_txns, indent=2))
    (HERE / "invoices.json").write_text(json.dumps(all_invoices, indent=2))
    tc = sum(len(v) for v in all_txns.values())
    ic = sum(len(v) for v in all_invoices.values())
    print(f"Generated {tc} transactions and {ic} invoices across {len(businesses)} businesses.")


if __name__ == "__main__":
    main()
