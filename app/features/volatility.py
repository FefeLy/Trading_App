import pandas as pd


def add_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def add_volatility(df: pd.DataFrame, period: int = 20) -> pd.Series:
    return df["close"].pct_change().rolling(period).std()


def add_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["atr"] = add_atr(df)
    df["volatility"] = add_volatility(df)

    return df
