"""Read-only access to the sandbox SME data."""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


@lru_cache(maxsize=1)
def _load(name: str):
    return json.loads((DATA_DIR / name).read_text())


def ensure_data():
    """Generate the sandbox data if it hasn't been created yet."""
    if not (DATA_DIR / "transactions.json").exists():
        import subprocess, sys
        subprocess.run([sys.executable, str(DATA_DIR / "generate_data.py")], check=True)


def list_businesses():
    return _load("businesses.json")["businesses"]


def get_business(biz_id: str):
    for b in list_businesses():
        if b["id"] == biz_id:
            return b
    raise KeyError(f"Unknown business {biz_id}")


def get_transactions(biz_id: str):
    return _load("transactions.json").get(biz_id, [])


def get_invoices(biz_id: str):
    return _load("invoices.json").get(biz_id, [])


def get_financing_products():
    return _load("financing_products.json")["products"]
