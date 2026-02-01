import csv
from pathlib import Path

DATA_PATH = Path("app/data/journal.csv")

def load_trades():
    if not DATA_PATH.exists():
        return []

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
        return list(reader)


def discipline_metrics():
    trades = load_trades()
    if not trades:
        return {
            "win_rate": 0,
            "avg_rr": None,
            "max_drawdown": None,
            "trades": 0,
        }

    wins = [t for t in trades if float(t["profit_r"]) > 0]
    rr_values = [float(t["profit_r"]) for t in trades]

    equity = 0
    peak = 0
    max_dd = 0

    for r in rr_values:
        equity += r
        peak = max(peak, equity)
        dd = peak - equity
        max_dd = max(max_dd, dd)

    return {
        "win_rate": round(len(wins) / len(trades) * 100, 2),
        "avg_rr": round(sum(rr_values) / len(rr_values), 2),
        "max_drawdown": round(max_dd, 2),
        "trades": len(trades),
    }

def drawdown_curve(equity_curve: list[dict] | None = None) -> dict:
    if not equity_curve:
        return {"max_drawdown": 0.0}

    peak = equity_curve[0]["equity"]
    max_dd = 0.0

    for point in equity_curve:
        equity = point["equity"]
        if equity > peak:
            peak = equity
        dd = (equity - peak) / peak
        max_dd = min(max_dd, dd)

    return {"max_drawdown": max_dd}
