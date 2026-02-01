from app.data.loaders import load_binance_history
from app.features.technicals import add_technicals
from app.signals.signal_engine import SignalEngine, SignalType
from app.risk.risk_manager import RiskManager
from app.backtest.engine import BacktestEngine
from app.backtest.metrics import compute_metrics

def run_backtest(symbol="BTCUSDT", timeframe="1h", capital=10_000):
    df = load_binance_history(symbol, timeframe)
    df = add_technicals(df)

    engine = BacktestEngine(capital)
    signal_engine = SignalEngine()
    risk = RiskManager()

    for i in range(50, len(df)):
        slice_df = df.iloc[:i]
        signal = signal_engine.generate(slice_df, probability=0.55)

        if signal.type == SignalType.BUY:
            trade = risk.build_trade(
                capital=engine.capital,
                entry_price=slice_df.iloc[-1]["close"],
                stop_price=slice_df.iloc[-1]["low"]
            )

            # simulación simple
            engine.execute_trade(trade, result_pct=0.01)

    metrics = compute_metrics(engine.trades, engine.equity_curve)

    return {
        "equity": engine.equity_curve,
        "metrics": metrics
    }
