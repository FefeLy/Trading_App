import csv
from pathlib import Path
from datetime import datetime

DATA_PATH = Path("app/data/journal.csv")

def equity_curve():
    if not DATA_PATH.exists():
        return []

    equity = 0.0
    curve = []

    with open(DATA_PATH, newline="") as f:
        reader = csv.DictReader(
            f,
            fieldnames=[
                "timestamp",
                "symbol",
                "side",
                "entry",
                "stop",
                "take_profit",
                "risk_r",
                "profit_r",
                "rule_respected",
            ],
        )

        for row in reader:
            try:
                r = float(row["profit_r"])
            except (TypeError, ValueError):
                continue

            equity += r

            curve.append({
                "date": row["timestamp"],
                "equity": round(equity, 2),
            })

    return curve
