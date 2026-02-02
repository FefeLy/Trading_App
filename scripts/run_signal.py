from app.data.loaders import load_binance_klines
from app.data.cleaners import clean_market_data
from app.features.technicals import add_technicals
from app.models.ml_models import LogisticSignalModel
from app.models.registry import prepare_dataset
from app.signals.signal_engine import SignalEngine

# 1. Data
df = load_binance_klines("BTCUSDT", "1h", 300)
df = clean_market_data(df)
df = add_technicals(df)

# 2. Dataset
X, y = prepare_dataset(df)

# 3. Modelo
model = LogisticSignalModel()
model.train(X, y)

# 4. Predicción actual
latest_X = X.tail(1)
probability = model.predict_proba(latest_X).iloc[0]

# 5. Señal
engine = SignalEngine()
signal = engine.generate(df, probability)

print(signal)
