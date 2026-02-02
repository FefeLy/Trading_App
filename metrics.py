import numpy as np
import pandas as pd

def performance_metrics(df: pd.DataFrame) -> dict:
    returns = df["returns"]

    total_return = df["equity"].iloc[-1] / df["equity"].iloc[0] - 1
    win_rate = (returns > 0).sum() / (returns != 0).sum()

    sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if returns.std() != 0 else 0

    cummax = df["equity"].cummax()
    drawdown = (df["equity"] - cummax) / cummax
    max_drawdown = drawdown.min()

    return {
        "total_return": round(total_return, 4),
        "win_rate": round(win_rate, 4),
        "sharpe": round(sharpe, 2),
        "max_drawdown": round(max_drawdown, 4)
    }
