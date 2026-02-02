import pandas as pd

def trend_filter(df: pd.DataFrame) -> bool:
    """
    True = mercado alineado para operar
    False = mercado neutro / contra tendencia
    """
    last = df.iloc[-1]
    return last["ema_20"] > last["ema_50"]

def htf_filter(signal: dict, htf_trend: str) -> dict:
    """
    htf_trend: 'bull', 'bear', 'range'
    """
    if signal["signal"] == "BUY" and htf_trend != "bull":
        signal["signal"] = "HOLD"
        signal["reason"] = "htf_misalignment"

    if signal["signal"] == "SELL" and htf_trend != "bear":
        signal["signal"] = "HOLD"
        signal["reason"] = "htf_misalignment"

    return signal
