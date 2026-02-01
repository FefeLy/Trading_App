from app.models.logistic_signal_model import LogisticSignalModel
from app.data.loaders import load_market_data
from app.data.features import add_features

_active_model = None

def get_active_model():
    global _active_model

    if _active_model is None:
        model = LogisticSignalModel()

        # === AUTO-TRAIN ===
        df = load_market_data("BTCUSDT", "1h", 500)
        df = add_features(df)
        print(df.columns)

        X = df[model.feature_columns]
        y = (df["close"].shift(-1) > df["close"]).astype(int)

        X = X.iloc[:-1]
        y = y.iloc[:-1]

        model.train(X, y)

        _active_model = model

    return _active_model
