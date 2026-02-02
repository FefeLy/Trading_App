import pandas as pd

from app.data.loaders import load_binance_klines
from app.data.cleaners import clean_market_data
from app.features.technicals import add_technicals
from app.models.registry import prepare_dataset
from app.models.ml_models import LogisticSignalModel
from app.signals.signal_engine import SignalEngine
from app.backtest.engine import BacktestEngine
from app.backtest.metrics import performance_metrics


def main():
    print("📥 Loading data...")
    df = load_binance_klines("BTCUSDT", "1h", 1500)
    df = clean_market_data(df)
    df = add_technicals(df)

    print("🧠 Preparing dataset...")
    X, y = prepare_dataset(df)

    print("🤖 Training model...")
    model = LogisticSignalModel()
    model.train(X, y)

    print("📊 Generating probabilities...")
    probs = model.predict_proba(X)

    print("📈 Generating signals...")
    engine = SignalEngine()
    signals = []

    for i in range(len(probs)):
        sig = engine.generate(df.iloc[: i + 1], probs.iloc[i])
        signals.append(sig.type)

    signals = pd.Series(signals, index=X.index)

    print("🔁 Running backtest...")
    bt = BacktestEngine()
    results = bt.run(df.loc[X.index], signals)

    print("📊 Metrics:")
    metrics = performance_metrics(results)
    for k, v in metrics.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
