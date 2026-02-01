from enum import Enum
import numpy as np


class MarketRegime(str, Enum):
    TRENDING = "trending"
    RANGING = "ranging"
    CHAOTIC = "chaotic"


def detect_market_regime(df):
    """
    Detecta el régimen de mercado usando datos 1H.
    Devuelve: MarketRegime
    """

    ema_fast = df["ema_fast"]
    ema_slow = df["ema_slow"]
    atr = df["atr"]
    close = df["close"]

    # Pendiente de la EMA lenta
    slope = ema_slow.diff().tail(5).mean()

    atr_relative = (atr / close).tail(5).mean()

    # 🔹 CAÓTICO: volatilidad extrema
    if atr_relative > 0.06:
        return MarketRegime.CHAOTIC

    # 🔹 TENDENCIA: pendiente clara
    if abs(slope) > 0.0005:
        return MarketRegime.TRENDING

    # 🔹 RANGO
    return MarketRegime.RANGING
