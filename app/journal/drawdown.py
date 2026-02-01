from app.journal.equity import equity_curve

def drawdown_curve() -> dict:
    equity = equity_curve()
    if not equity:
        return {
            "max_drawdown": 0.0,
            "current_drawdown": 0.0
        }

    values = [e["equity"] for e in equity]
    peak = values[0]
    max_dd = 0.0

    for v in values:
        if v > peak:
            peak = v
        dd = (v - peak) / peak
        if dd < max_dd:
            max_dd = dd

    current_dd = (values[-1] - peak) / peak

    return {
        "max_drawdown": max_dd,
        "current_drawdown": current_dd
    }
