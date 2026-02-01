# app/scanner/filters.py

import pandas as pd

REQUIRED_COLUMNS = {
    "close",
    "volume",
}

OPTIONAL_COLUMNS = {
    "atr",
    "ema_20",
    "ema_50",
    "ema_slow",
    "rsi",
}


def market_filter(df: pd.DataFrame) -> bool:
    """
    Filtro técnico base.
    Nunca rompe el scanner.
    Devuelve True solo si el activo es tradable.
    """

    # ---------- Seguridad básica ----------
    if df is None or df.empty:
        return False

    if not REQUIRED_COLUMNS.issubset(df.columns):
        return False

    if len(df) < 50:
        return False

    # ---------- Liquidez mínima ----------
    if df["volume"].iloc[-20:].mean() <= 0:
        return False

    # ---------- Filtros avanzados (solo si existen) ----------
    cols = set(df.columns)

    # Volatilidad (ATR)
    if "atr" in cols:
        if df["atr"].iloc[-1] / df["close"].iloc[-1] < 0.003:
            return False

    # Tendencia (EMA alignment)
    if {"ema_20", "ema_50", "ema_slow"}.issubset(cols):
        ema20 = df["ema_20"].iloc[-1]
        ema50 = df["ema_50"].iloc[-1]
        emaslow = df["ema_slow"].iloc[-1]

        bull_ok = (ema20 > ema50 > emaslow)
        bear_ok = (ema20 < ema50 < emaslow)

        # Permitimos tendencias bullish O bearish
        if not (bull_ok or bear_ok):
            return False


    # RSI extremo
    if "rsi" in cols:
        rsi = df["rsi"].iloc[-1]
        if rsi < 35 or rsi > 75:
            return False

    return True
