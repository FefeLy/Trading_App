import pandas as pd


def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["return"] = df["close"].pct_change()
    return df


def add_target(df: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
    df = df.copy()
    future_return = df["close"].pct_change(horizon).shift(-horizon)
    df["target"] = (future_return > 0).astype(int)
    return df
