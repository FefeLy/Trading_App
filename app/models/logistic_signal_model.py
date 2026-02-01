from sklearn.linear_model import LogisticRegression


class LogisticSignalModel:

    feature_columns = [
        "rsi",
        "ema_20",
        "ema_50",
        "ema_fast",
        "ema_slow",
        "atr",
        "volatility"
    ]

    def __init__(self):
        self.model = LogisticRegression(max_iter=1000)
        self.is_trained = False

    def train(self, X, y):
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X):
        if not self.is_trained:
            raise RuntimeError("Model not trained")
        return self.model.predict(X)

    def predict_proba(self, X):
        if not self.is_trained:
            raise RuntimeError("Model not trained")
        return self.model.predict_proba(X)
