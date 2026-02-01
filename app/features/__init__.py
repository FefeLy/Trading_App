from app.features.technicals import add_technicals
from app.features.trends import add_returns, add_target
from app.features.volatility import add_volatility_features


def build_features(df):
    """
    Ensures the dataframe has all mandatory features required by the system.
    """

    df = add_technicals(df)
    df = add_returns(df)
    df = add_target(df)
    df = add_volatility_features(df)

    # HARD VALIDATION (no silent failure)
    required = ["return", "ema_20", "ema_50", "rsi"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing required features: {missing}")

    return df
