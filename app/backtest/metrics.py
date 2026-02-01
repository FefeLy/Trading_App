import numpy as np


def compute_profit_factor(trades):
    """
    Profit Factor = suma ganancias / suma pérdidas
    """
    gains = [t["pnl"] for t in trades if t["pnl"] > 0]
    losses = [abs(t["pnl"]) for t in trades if t["pnl"] < 0]

    if not losses:
        return float("inf")

    return round(sum(gains) / sum(losses), 4)


def compute_expectancy(trades):
    """
    Expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
    """
    if not trades:
        return 0.0

    wins = [t["pnl"] for t in trades if t["pnl"] > 0]
    losses = [abs(t["pnl"]) for t in trades if t["pnl"] < 0]

    win_rate = len(wins) / len(trades)
    loss_rate = len(losses) / len(trades)

    avg_win = np.mean(wins) if wins else 0
    avg_loss = np.mean(losses) if losses else 0

    return round((win_rate * avg_win) - (loss_rate * avg_loss), 4)


def compute_metrics(trades):
    """
    Métricas resumidas para dashboard
    """
    return {
        "total_trades": len(trades),
        "profit_factor": compute_profit_factor(trades),
        "expectancy": compute_expectancy(trades),
        "net_pnl": round(sum(t["pnl"] for t in trades), 2),
    }

def compute_risk_score(trades):
    """
    Risk Score (0–100)
    Combina profit factor, expectancy y drawdown
    """

    if not trades:
        return 0

    pnls = np.array([t["pnl"] for t in trades])
    equity = pnls.cumsum()

    # Drawdown
    peak = np.maximum.accumulate(equity)
    drawdown = peak - equity
    max_dd = drawdown.max() if len(drawdown) else 0

    profit_factor = compute_profit_factor(trades)
    expectancy = compute_expectancy(trades)

    # Normalización simple (estable)
    pf_score = min(profit_factor / 3, 1) * 40        # máx 40
    exp_score = min(max(expectancy, 0) / 100, 1) * 40  # máx 40
    dd_penalty = min(max_dd / 1000, 1) * 20           # penalización máx 20

    score = pf_score + exp_score - dd_penalty

    return int(max(0, min(100, score)))
