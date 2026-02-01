from app.core.signal_types import SignalType


def atr_stop_loss(df):
    """
    Función legacy (NO TOCAR main.py).
    Se mantiene por compatibilidad.
    """
    close = float(df["close"].iloc[-1])
    atr = df["atr"].iloc[-1] if "atr" in df.columns else close * 0.005
    return round(close - atr, 4)


def compute_stop_loss(df, signal: SignalType) -> float:
    """
    Stop loss institucional:
    - BUY: ATR debajo del precio
    - SELL: ATR encima del precio
    - HOLD: escenario defensivo
    """

    close = float(df["close"].iloc[-1])
    atr = df["atr"].iloc[-1] if "atr" in df.columns else close * 0.005

    if signal == SignalType.BUY:
        return round(close - atr, 4)

    if signal == SignalType.SELL:
        return round(close + atr, 4)

    # HOLD institucional
    return round(close - atr, 4)

