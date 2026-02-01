import pandas as pd

from app.data.loaders import load_binance_history
from app.features import build_features
from app.models.registry import prepare_dataset
from app.signals.signal_engine import generate_signal
from app.backtest.metrics import compute_expectancy


def walk_forward_validation(
    symbol: str = "BTCUSDT",
    timeframe: str = "1h",
    train_size: int = 1000,
    test_size: int = 200
):
    df = load_binance_history(symbol, timeframe)
    df = build_features(df)

    results = []
    start = 0

    while start + train_size + test_size < len(df):
        train_df = df.iloc[start : start + train_size]
        test_df = df.iloc[start + train_size : start + train_size + test_size]

        # Dataset entrenamiento
        X_train, y_train = prepare_dataset(train_df)

        # ⚠️ Entrenamiento conceptual (placeholder)
        # Aquí NO entrenamos de nuevo todavía.
        # Usamos el modelo congelado (v1.0)

        trades = []

        for i in range(len(test_df)):
            slice_df = df.iloc[: start + train_size + i + 1]
            signal = generate_signal(slice_df, symbol)

            if signal["signal"] in ("BUY", "SELL"):
                trades.append({
                    "pnl": 1 if signal["signal"] == "BUY" else -1
                })

        expectancy = compute_expectancy(trades)

        results.append({
            "start": start,
            "expectancy": expectancy,
            "trades": len(trades)
        })

        start += test_size

    return results
