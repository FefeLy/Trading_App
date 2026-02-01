import pandas as pd

def clean_market_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna()

    numeric_cols = ["open", "high", "low", "close", "volume"]
    df[numeric_cols] = df[numeric_cols].astype(float)

    df = df[df["volume"] > 0]

    return df
