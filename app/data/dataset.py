def prepare_dataset(df):
    feature_columns = [
        "ema_20",
        "ema_50",
        "ema_fast",
        "ema_slow",
        "rsi",
        "atr",
        "volatility",
    ]

    X = df[feature_columns]
    y = (df["return"] > 0).astype(int)

    return X, y

