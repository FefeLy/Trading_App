def build_report(trades, metrics):
    equity = []
    balance = 0

    for t in trades:
        balance += t.pnl
        equity.append(balance)

    return {
        "equity": equity,
        "metrics": metrics
    }
