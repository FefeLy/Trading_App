import pandas as pd

from app.data.loaders import load_binance_klines
from app.data.cleaners import clean_market_data
from app.features.technicals import add_technicals
from app.models.ml_models import LogisticSignalModel
from app.models.registry import prepare_dataset
from app.signals.signal_engine import SignalEngine, SignalType
from app.risk.risk_manager import RiskManager
from app.risk.stop_loss import atr_stop_loss
from app.backtest.engine_risk import RiskBacktestEngine
from app.backtest.metrics import performance_metrics

# 1. Data
df = load_binance_klines("BTCUSDT", "1h", 1000)
df = clean_market_data(df)
df = add_technicals(df)

# 2. Dataset
X, y = prepare_dataset(df)

# 3. Train model
model = LogisticSignalModel()
model.train(X, y)

# 4. Probabilities
probs = model.predict_proba(X)

# 5. Signal + Risk plans
engine = SignalEngine()
risk_manager = RiskManager(risk_per_trade=0.01, rr_ratio=2.0)

signals = []
trade_plans = {}
capital = 10_000

for i in range(len(probs)):
    signal = engine.generate(df.iloc[:i+1], probs.iloc[i])
    signals.append(signal.type)

    if signal.type == SignalType.BUY:
        entry = df.iloc[i]["close"]
        stop = atr_stop_loss(df.iloc[:i+1], entry)
        plan = risk_manager.build_trade(
            capital=capital,
            entry_price=entry,
            stop_price=stop
        )
        trade_plans[i] = plan

signals = pd.Series(signals, index=X.index)

# 6. Backtest con riesgo
engine_bt = RiskBacktestEngine(initial_capital=capital)
results = engine_bt.run(df.loc[X.index], signals, trade_plans)

# 7. Métricas
metrics = performance_metrics(results)
print(metrics)
