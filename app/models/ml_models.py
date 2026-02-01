from app.data.dataset import prepare_dataset

class LogisticSignalModel:
    feature_columns = [
        "ema_20",
        "ema_50",
        "ema_fast",
        "ema_slow",
        "rsi",
        "atr",
        "return",
        "volatility",
    ]

    def predict_proba(self, df):
        X, _ = prepare_dataset(df)
        # aquí va tu lógica real de predicción
        return [0.6]  # placeholder
